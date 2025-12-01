"""
Arena CLI - Command-line interface for running Social Arena simulations.

Usage:
    python -m arena.cli -n_of_agents 10 -post_per_day 5 -days_of_simulations 5
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from agent import Agent
import feed
from recommendation import CentralizedRecommendationSystem, BalancedStrategy

from .config import ArenaLLMConfig

from openai import AsyncOpenAI


# Helper functions
def _format_feeds(feeds: List[feed.Feed]) -> str:
    """Format feeds for the LLM prompt."""
    lines: List[str] = []
    for index, item in enumerate(feeds, 1):
        lines.append(f"{index}. [{item.id[:8]}] @{item.author_id}: {item.text}")
    return "\n".join(lines)


class ParsedDecision(BaseModel):
    """Parsed LLM decision."""
    action: str
    target_id: Optional[str] = None


def _parse_decision(llm_response: str) -> ParsedDecision:
    """
    Parse LLM decision into an action + optional target id.
    """
    response_lower = llm_response.lower().strip()
    parts = response_lower.split()
    target_id = parts[1] if len(parts) > 1 else None

    if "like" in response_lower:
        return ParsedDecision(action="like", target_id=target_id)
    if "reply" in response_lower:
        return ParsedDecision(action="reply", target_id=target_id)
    if "follow" in response_lower:
        return ParsedDecision(action="follow", target_id=target_id)
    if "post" in response_lower:
        return ParsedDecision(action="post")
    return ParsedDecision(action="idle")


def _find_feed_by_id(feeds: List[feed.Feed], feed_id: str) -> Optional[feed.Feed]:
    """Find feed by ID (supports partial match)."""
    for item in feeds:
        if item.id.startswith(feed_id) or item.id == feed_id:
            return item
    return feeds[0] if feeds else None


class CLISimulationResult(BaseModel):
    """Result of a CLI simulation run."""
    
    agents_folder: Path
    feeds_folder: Path
    recommendation_folder: Path
    total_agents: int
    total_feeds: int
    total_days: int


class ArenaSimulationCLI:
    """
    CLI-driven Arena simulation with structured output folders.
    
    Output structure:
    - agents/ -> Individual agent cache files
    - feeds/ -> All feeds created during simulation
    - recommendation/ -> Recommendation system state and mappings
    """
    
    def __init__(
        self,
        n_of_agents: int,
        post_per_day: int,
        days_of_simulations: int,
        fetch_per_day: int = 10,
        explore_ratio: float = 0.2,
        llm_config: ArenaLLMConfig | None = None,
        output_root: Path | None = None,
    ):
        self.n_of_agents = n_of_agents
        self.post_per_day = post_per_day
        self.days_of_simulations = days_of_simulations
        self.fetch_per_day = fetch_per_day
        self.explore_ratio = explore_ratio
        
        self.llm_config = llm_config or ArenaLLMConfig()
        self.llm_client = AsyncOpenAI(
            base_url=self.llm_config.base_url,
            api_key=self.llm_config.api_key,
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_root = output_root or Path(f"cache/arena_output_{timestamp}")
        
        self.agents_folder = self.output_root / "agents"
        self.feeds_folder = self.output_root / "feeds"
        self.recommendation_folder = self.output_root / "recommendation"
        
        self.agents_folder.mkdir(parents=True, exist_ok=True)
        self.feeds_folder.mkdir(parents=True, exist_ok=True)
        self.recommendation_folder.mkdir(parents=True, exist_ok=True)
        
        strategy = BalancedStrategy(explore_ratio=self.explore_ratio)
        self.rec_system = CentralizedRecommendationSystem(strategy=strategy)
        
        self.agents: List[Agent] = []
        self._initialize_agents()
    
    def _initialize_agents(self) -> None:
        """Create N agents with generated profiles."""
        agent_templates = [
            ("Tech enthusiast", "tech"),
            ("Crypto investor", "crypto"),
            ("AI researcher", "ai"),
            ("Sports fan", "sports"),
            ("Food blogger", "food"),
            ("Travel enthusiast", "travel"),
            ("Music lover", "music"),
            ("Fitness coach", "fitness"),
            ("Artist", "art"),
            ("Writer", "writing"),
        ]
        
        for i in range(self.n_of_agents):
            template_idx = i % len(agent_templates)
            bio_template, username_prefix = agent_templates[template_idx]
            
            agent_id = f"agent_{i:03d}"
            username = f"{username_prefix}_{i:03d}"
            bio = f"{bio_template} #{i}"
            
            arena_agent = Agent(
                agent_id=agent_id,
                username=username,
                bio=bio,
            )
            
            self.agents.append(arena_agent)
            self.rec_system.add_agent(
                arena_agent.agent_id,
                {"bio": arena_agent.bio, "username": arena_agent.username},
            )
            
            # Save initial agent state
            self._save_agent_cache(arena_agent, day=0)
    
    async def run(self) -> CLISimulationResult:
        """
        Run the full simulation with structured output.
        
        For each day:
        1. Each agent creates `post_per_day` posts
        2. Each agent fetches `fetch_per_day` posts from recommendation system
        3. Each agent decides and acts on the recommended content
        4. Update agent states and recommendation mappings
        """
        print(f"Starting Arena simulation:")
        print(f"  Agents: {self.n_of_agents}")
        print(f"  Posts per day: {self.post_per_day}")
        print(f"  Days: {self.days_of_simulations}")
        print(f"  Fetch per day: {self.fetch_per_day}")
        print(f"  Output: {self.output_root}")
        print()
        
        for day in range(1, self.days_of_simulations + 1):
            print(f"Day {day}/{self.days_of_simulations}")
            
            # Morning: Each agent creates posts
            print(f"  Morning: Agents creating {self.post_per_day} posts each...")
            for agent in self.agents:
                for post_idx in range(self.post_per_day):
                    post_text = (
                        f"Day {day} Post {post_idx + 1}: "
                        f"{agent.bio} - {agent.username}"
                    )
                    post_dict = agent.create_post(post_text)
                    post_model = feed.Feed.from_dict(post_dict)
                    self.rec_system.ingest_feed(post_model)
            
            total_feeds = len(self.rec_system.feed_pool)
            print(f"    ✓ Total feeds in system: {total_feeds}")
            
            # Afternoon: Each agent fetches and reacts
            print(f"  Afternoon: Agents fetching {self.fetch_per_day} posts and reacting...")
            for agent in self.agents:
                recommended = self.rec_system.fetch(
                    agent.agent_id,
                    {
                        "interests": agent.bio,
                        "max_feeds": self.fetch_per_day,
                    },
                )
                
                feeds_for_agent: List[feed.Feed] = [
                    item for item in recommended["feeds"] if isinstance(item, feed.Feed)
                ]
                
                # Store recommendation mapping
                self._save_recommendation_mapping(
                    agent.agent_id,
                    feeds_for_agent,
                    day,
                )
                
                if not feeds_for_agent:
                    continue
                
                # Agent decides what to do
                decision_prompt = (
                    f"You are {agent.username} ({agent.bio}).\n\n"
                    f"You see these recent posts:\n"
                    f"{_format_feeds(feeds_for_agent[:self.fetch_per_day])}\n\n"
                    "What do you want to do? Choose ONE simple action:\n"
                    "- like [feed_id] - Like a post\n"
                    "- reply [feed_id] - Reply to a post\n"
                    "- follow [username] - Follow someone\n"
                    "- idle - Do nothing\n\n"
                    f'Respond with just the action and ID, like: "like {feeds_for_agent[0].id[:8]}"'
                )
                
                response = await self.llm_client.chat.completions.create(
                    model=self.llm_config.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a social media user. Be concise.",
                        },
                        {"role": "user", "content": decision_prompt},
                    ],
                    max_tokens=self.llm_config.max_tokens,
                    temperature=self.llm_config.temperature,
                )
                
                content = response.choices[0].message.content or ""
                decision = _parse_decision(content)
                
                # Execute action
                if decision.action == "like":
                    target = _find_feed_by_id(feeds_for_agent, decision.target_id or "")
                    if target:
                        liked = agent.like(target.id)
                        if liked:
                            self.rec_system.record_action(
                                agent.agent_id,
                                "like",
                                target.id,
                            )
                
                elif decision.action == "reply":
                    target = _find_feed_by_id(feeds_for_agent, decision.target_id or "")
                    if target:
                        reply_text = f"Interesting perspective on {target.text[:20]}..."
                        reply_dict = agent.reply(target.id, reply_text, target.author_id)
                        reply_model = feed.Feed.from_dict(reply_dict)
                        self.rec_system.ingest_feed(reply_model)
                        self.rec_system.record_action(
                            agent.agent_id,
                            "reply",
                            target.id,
                        )
                
                elif decision.action == "follow":
                    suggested_users = recommended.get("users", [])
                    if suggested_users:
                        target_user = suggested_users[0]
                        followed = agent.follow(target_user)
                        if followed:
                            self.rec_system.update_social_graph(
                                agent.agent_id,
                                target_user,
                                action="follow",
                            )
                            self.rec_system.record_action(
                                agent.agent_id,
                                "follow",
                                target_user,
                            )
            
            # End of day: Save agent states
            print(f"  Evening: Saving agent states...")
            for agent in self.agents:
                self._save_agent_cache(agent, day)
            
            print()
        
        # Final: Save all feeds and recommendation system state
        print("Simulation complete. Saving final state...")
        self._save_all_feeds()
        self._save_recommendation_state()
        
        result = CLISimulationResult(
            agents_folder=self.agents_folder,
            feeds_folder=self.feeds_folder,
            recommendation_folder=self.recommendation_folder,
            total_agents=self.n_of_agents,
            total_feeds=len(self.rec_system.feed_pool),
            total_days=self.days_of_simulations,
        )
        
        print(f"\n✓ Simulation saved to: {self.output_root}")
        print(f"  - Agents: {result.agents_folder} ({result.total_agents} agents)")
        print(f"  - Feeds: {result.feeds_folder} ({result.total_feeds} feeds)")
        print(f"  - Recommendations: {result.recommendation_folder}")
        
        return result
    
    def _save_agent_cache(self, agent: Agent, day: int) -> None:
        """Save individual agent state to agents folder."""
        agent_file = self.agents_folder / f"{agent.agent_id}_day{day:03d}.json"
        
        agent_data = {
            "agent_id": agent.agent_id,
            "username": agent.username,
            "bio": agent.bio,
            "day": day,
            "following": agent.following,
            "followers": agent.followers,
            "liked_tweets": agent.liked_tweets,
            "stats": agent.get_stats(),
        }
        
        agent_file.write_text(json.dumps(agent_data, indent=2), encoding="utf-8")
    
    def _save_all_feeds(self) -> None:
        """Save all feeds to feeds folder."""
        feeds_file = self.feeds_folder / "all_feeds.json"
        
        feeds_data: List[Dict[str, Any]] = []
        for item in self.rec_system.feed_pool:
            if isinstance(item, feed.Feed):
                feeds_data.append(item.to_dict())
            elif hasattr(item, "model_dump"):
                feeds_data.append(item.model_dump())
            else:
                feeds_data.append(item)
        
        feeds_file.write_text(json.dumps(feeds_data, indent=2), encoding="utf-8")
    
    def _save_recommendation_mapping(
        self,
        agent_id: str,
        feeds: List[feed.Feed],
        day: int,
    ) -> None:
        """
        Save recommendation mapping: which feeds were recommended to which agent.
        
        This stores the relation: agent_id -> [feed_ids] for each day.
        """
        mapping_file = self.recommendation_folder / f"{agent_id}_day{day:03d}_mapping.json"
        
        mapping_data = {
            "agent_id": agent_id,
            "day": day,
            "recommended_feed_ids": [f.id for f in feeds],
            "recommended_feed_count": len(feeds),
        }
        
        mapping_file.write_text(json.dumps(mapping_data, indent=2), encoding="utf-8")
    
    def _save_recommendation_state(self) -> None:
        """Save final recommendation system state."""
        state_file = self.recommendation_folder / "recommendation_state.json"
        
        state_data = {
            "stats": self.rec_system.get_stats(),
            "social_graph": {
                agent_id: list(following)
                for agent_id, following in self.rec_system.social_graph.items()
            },
            "total_actions": len([
                action
                for actions in self.rec_system.agent_actions.values()
                for action in actions
            ]),
        }
        
        state_file.write_text(json.dumps(state_data, indent=2), encoding="utf-8")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Arena - Social Arena Simulation CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        "-n_of_agents",
        type=int,
        default=10,
        help="Number of agents to create",
    )
    
    parser.add_argument(
        "-post_per_day",
        type=int,
        default=5,
        help="Number of posts each agent creates per day",
    )
    
    parser.add_argument(
        "-days_of_simulations",
        type=int,
        default=5,
        help="Number of days to simulate",
    )
    
    parser.add_argument(
        "-fetch_per_day",
        type=int,
        default=10,
        help="Number of posts each agent fetches from recommendation system per day",
    )
    
    parser.add_argument(
        "-explore_ratio",
        type=float,
        default=0.2,
        help="Exploration ratio for recommendation system (0.0-1.0)",
    )
    
    parser.add_argument(
        "-output",
        type=str,
        default=None,
        help="Output root directory (default: arena_output_TIMESTAMP)",
    )
    
    args = parser.parse_args()
    
    output_root = Path(args.output) if args.output else None
    
    sim = ArenaSimulationCLI(
        n_of_agents=args.n_of_agents,
        post_per_day=args.post_per_day,
        days_of_simulations=args.days_of_simulations,
        fetch_per_day=args.fetch_per_day,
        explore_ratio=args.explore_ratio,
        output_root=output_root,
    )
    
    asyncio.run(sim.run())


if __name__ == "__main__":
    main()

