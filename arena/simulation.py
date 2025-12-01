"""
Arena simulation built from `external/Agent/examples/simple_simulation.py`.

Key differences from the raw example:
- Uses the real `CentralizedRecommendationSystem` + `BalancedStrategy`
  from the `recommendation` package.
- Uses `feed.Feed` Pydantic models for the global feed pool.
- Configuration is expressed via Pydantic models in `arena.config`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from agent import Agent
import feed
from recommendation import CentralizedRecommendationSystem, BalancedStrategy

from .config import ArenaConfig


def _format_feeds(feeds: List[feed.Feed]) -> str:
    """Format feeds for the LLM prompt."""
    lines: List[str] = []
    for index, item in enumerate(feeds, 1):
        lines.append(f"{index}. [{item.id[:8]}] @{item.author_id}: {item.text}")
    return "\n".join(lines)


class ParsedDecision(BaseModel):
    action: str
    target_id: Optional[str] = None


def _parse_decision(llm_response: str) -> ParsedDecision:
    """
    Parse LLM decision into an action + optional target id.

    Mirrors the behavior of `parse_decision` in the Agent example,
    but returns a Pydantic model.
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


class ArenaRunResult(BaseModel):
    """Structured result returned after a simulation run."""

    cache_dir: Path
    recommendation_stats: Dict[str, Any]
    agent_stats: Dict[str, Dict[str, Any]]


@dataclass
class ArenaSimulation:
    """
    Orchestrates a multi-day Social Arena simulation.

    This is a higher-level, configurable version of `simple_simulation.py`
    that plugs the three core libraries together:
    - `agent.Agent`
    - `feed.Feed`
    - `recommendation.CentralizedRecommendationSystem`
    """

    config: ArenaConfig

    def __post_init__(self) -> None:
        strategy = BalancedStrategy(explore_ratio=self.config.simulation.explore_ratio)
        self.rec_system = CentralizedRecommendationSystem(strategy=strategy)
        self.agents: List[Agent] = []

        for agent_cfg in self.config.agents:
            arena_agent = Agent(
                agent_id=agent_cfg.agent_id,
                username=agent_cfg.username,
                bio=agent_cfg.bio,
            )
            self.agents.append(arena_agent)
            self.rec_system.add_agent(
                arena_agent.agent_id,
                {"bio": arena_agent.bio, "username": arena_agent.username},
            )

        llm_cfg = self.config.llm
        self.llm_client = AsyncOpenAI(
            base_url=llm_cfg.base_url,
            api_key=llm_cfg.api_key,
        )

    async def run(self) -> ArenaRunResult:
        """
        Run the full simulation and persist results to a cache directory.

        The structure of the saved cache matches the Agent example:
        - feeds.json
        - agents.json
        - social_graph.json
        - actions.json
        - stats.json
        """
        num_days = self.config.simulation.num_days
        posts_per_agent_per_day = self.config.simulation.posts_per_agent_per_day

        for day in range(1, num_days + 1):
            # Morning: each agent creates posts
            for agent in self.agents:
                for post_index in range(posts_per_agent_per_day):
                    post_text = (
                        f"Day {day} Post {post_index + 1}: "
                        f"{(agent.bio or agent.username).split()[0]} thoughts!"
                    )
                    post_dict = agent.create_post(post_text)
                    post_model = feed.Feed.from_dict(post_dict)
                    self.rec_system.ingest_feed(post_model)

            # Afternoon: each agent reacts to content
            for agent in self.agents:
                recommended = self.rec_system.fetch(
                    agent.agent_id,
                    {
                        "interests": agent.bio,
                        "max_feeds": self.config.simulation.max_feeds_per_agent,
                    },
                )
                feeds_for_agent: List[feed.Feed] = [
                    item for item in recommended["feeds"] if isinstance(item, feed.Feed)
                ]

                if not feeds_for_agent:
                    continue

                decision_prompt = (
                    f"You are {agent.username} ({agent.bio}).\n\n"
                    f"You see these recent posts:\n"
                    f"{_format_feeds(feeds_for_agent[: self.config.simulation.max_feeds_per_agent])}\n\n"
                    "What do you want to do? Choose ONE simple action:\n"
                    "- like [feed_id] - Like a post\n"
                    "- reply [feed_id] - Reply to a post\n"
                    "- follow [username] - Follow someone\n"
                    "- idle - Do nothing\n\n"
                    f'Respond with just the action and ID, like: "like {feeds_for_agent[0].id[:8]}"'
                )

                response = await self.llm_client.chat.completions.create(
                    model=self.config.llm.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a social media user. Be concise.",
                        },
                        {"role": "user", "content": decision_prompt},
                    ],
                    max_tokens=self.config.llm.max_tokens,
                    temperature=self.config.llm.temperature,
                )

                content = response.choices[0].message.content or ""
                decision = _parse_decision(content)

                if decision.action == "like":
                    target = _find_feed_by_id(
                        feeds_for_agent, decision.target_id or ""
                    )
                    if target:
                        liked = agent.like(target.id)
                        if liked:
                            self.rec_system.record_action(
                                agent.agent_id,
                                "like",
                                target.id,
                            )
                elif decision.action == "reply":
                    target = _find_feed_by_id(
                        feeds_for_agent, decision.target_id or ""
                    )
                    if target:
                        reply_text = (
                            f"Interesting perspective on {target.text[:20]}..."
                        )
                        reply_dict = agent.reply(
                            target.id,
                            reply_text,
                            target.author_id,
                        )
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

        cache_dir = self._save_to_cache()
        recommendation_stats = self.rec_system.get_stats()
        agent_stats: Dict[str, Dict[str, Any]] = {}

        for agent in self.agents:
            agent_stats[agent.agent_id] = agent.get_stats()

        return ArenaRunResult(
            cache_dir=cache_dir,
            recommendation_stats=recommendation_stats,
            agent_stats=agent_stats,
        )

    def _save_to_cache(self) -> Path:
        """Persist simulation artifacts to disk (JSON)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_root = Path(self.config.simulation.cache_root)
        cache_dir = cache_root / f"sim_{timestamp}"
        cache_dir.mkdir(parents=True, exist_ok=True)

        feeds_data: List[Dict[str, Any]] = []
        for item in self.rec_system.feed_pool:
            if isinstance(item, feed.Feed):
                feeds_data.append(item.to_dict())
            elif hasattr(item, "model_dump"):
                feeds_data.append(item.model_dump())
            else:
                feeds_data.append(item)  # Fallback

        (cache_dir / "feeds.json").write_text(
            text=_to_json(feeds_data),
            encoding="utf-8",
        )

        agents_payload: Dict[str, Any] = {}
        for agent in self.agents:
            agents_payload[agent.agent_id] = {
                "username": agent.username,
                "bio": agent.bio,
                "following": agent.following,
                "followers": agent.followers,
                "liked_tweets": agent.liked_tweets,
                "stats": agent.get_stats(),
            }

        (cache_dir / "agents.json").write_text(
            text=_to_json(agents_payload),
            encoding="utf-8",
        )

        (cache_dir / "social_graph.json").write_text(
            text=_to_json(self.rec_system.social_graph),
            encoding="utf-8",
        )

        (cache_dir / "actions.json").write_text(
            text=_to_json(self.rec_system.agent_actions),
            encoding="utf-8",
        )

        (cache_dir / "stats.json").write_text(
            text=_to_json(self.rec_system.get_stats()),
            encoding="utf-8",
        )

        return cache_dir


def _to_json(data: Any) -> str:
    """
    Lightweight JSON serialization helper using Pydantic for consistency.
    """

    class Wrapper(BaseModel):
        payload: Any

    wrapper = Wrapper(payload=data)
    return wrapper.model_dump_json(indent=2)


