"""
Agent Orchestrator - Manages agent lifecycle and task allocation
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from Arena.config.arena_config import ArenaConfig
from Arena.trace_logging import get_logger


class AgentOrchestrator:
    """
    Agent Orchestrator - Manages agent lifecycle and coordinates agent actions
    """
    
    def __init__(self, config: ArenaConfig):
        self.config = config
        self.logger = get_logger("agent_orchestrator", "system")
        
        # Agent storage
        self.agents: Dict[str, Any] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        
        # Action tracking
        self.action_queue: List[Dict[str, Any]] = []
        self.completed_actions: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.agent_metrics: Dict[str, Dict[str, float]] = {}
        
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize the orchestrator"""
        if self.is_initialized:
            return
        
        self.logger.info("Initializing AgentOrchestrator")
        
        # Initialize agent factory (will import Agent module)
        self._setup_agent_factory()
        
        self.is_initialized = True
        self.logger.info("AgentOrchestrator initialized")
    
    def _setup_agent_factory(self) -> None:
        """Setup agent factory for creating agents"""
        # Import Agent module components
        try:
            from Agent import (
                CreatorAgent, CreatorConfig,
                AudienceAgent, AudienceConfig,
                BrandAgent, BrandConfig,
                ModeratorAgent, ModeratorConfig,
                LearningStage
            )
            
            self.agent_classes = {
                "creator": (CreatorAgent, CreatorConfig),
                "audience": (AudienceAgent, AudienceConfig),
                "brand": (BrandAgent, BrandConfig),
                "moderator": (ModeratorAgent, ModeratorConfig)
            }
            
            self.LearningStage = LearningStage
            
            self.logger.info("Agent factory setup complete")
            
        except ImportError as e:
            self.logger.error(f"Failed to import Agent module: {e}")
            raise
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> str:
        """
        Create and initialize a new agent
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            Agent ID
        """
        agent_id = agent_config["agent_id"]
        role = agent_config["role"]
        
        if agent_id in self.agents:
            self.logger.warning(f"Agent {agent_id} already exists")
            return agent_id
        
        # Get agent class and config class
        if role not in self.agent_classes:
            raise ValueError(f"Unknown agent role: {role}")
        
        AgentClass, ConfigClass = self.agent_classes[role]
        
        # Convert learning stage string to enum
        learning_stage_str = agent_config.get("learning_stage", "cold_start")
        learning_stage = self.LearningStage[learning_stage_str.upper()]
        agent_config["learning_stage"] = learning_stage
        
        # Create config instance
        config = ConfigClass(**agent_config)
        
        # Create agent
        agent = AgentClass(agent_id, config)
        await agent.initialize()
        
        # Store agent
        self.agents[agent_id] = agent
        self.agent_states[agent_id] = {
            "role": role,
            "status": "active",
            "created_at": datetime.now(),
            "action_count": 0
        }
        
        self.logger.info(f"Agent created", extra={
            "agent_id": agent_id,
            "role": role
        })
        
        return agent_id
    
    async def orchestrate_agent_actions(
        self,
        time_step: int,
        environment_state: Any
    ) -> List[Dict[str, Any]]:
        """
        Orchestrate agent actions for current time step
        
        Args:
            time_step: Current time step
            environment_state: Current environment state
            
        Returns:
            List of agent actions
        """
        actions = []
        
        # Get active agents
        active_agents = [
            (agent_id, agent) 
            for agent_id, agent in self.agents.items()
            if self.agent_states[agent_id]["status"] == "active"
        ]
        
        self.logger.debug(f"Orchestrating actions for {len(active_agents)} agents")
        
        # Execute agent actions concurrently
        tasks = []
        for agent_id, agent in active_agents:
            task = self._execute_agent_action(agent_id, agent, environment_state)
            tasks.append(task)
        
        # Gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for (agent_id, agent), result in zip(active_agents, results):
            if isinstance(result, Exception):
                self.logger.error(f"Agent action failed", extra={
                    "agent_id": agent_id,
                    "error": str(result)
                })
                continue
            
            if result:
                actions.append({
                    "agent_id": agent_id,
                    "action": result,
                    "time_step": time_step,
                    "timestamp": datetime.now()
                })
                
                # Update state
                self.agent_states[agent_id]["action_count"] += 1
        
        self.completed_actions.extend(actions)
        
        self.logger.info(f"Orchestrated {len(actions)} agent actions")
        
        return actions
    
    async def _execute_agent_action(
        self,
        agent_id: str,
        agent: Any,
        environment_state: Any
    ) -> Optional[Any]:
        """Execute single agent action"""
        # Call agent's act method
        action = await agent.act(environment_state)
        
        # Simulate action feedback (in real system, this would come from actual execution)
        feedback = self._generate_mock_feedback(action)
        await agent.update_from_feedback(feedback)
        
        return action
    
    def _generate_mock_feedback(self, action: Any) -> Any:
        """Generate mock feedback for action"""
        import random
        from Agent import ActionFeedback
        
        # Generate random metrics based on action type
        success = random.random() > 0.2  # 80% success rate
        
        feedback = ActionFeedback(
            action_id=f"action_{action.agent_id}_{action.timestamp.timestamp()}",
            action_type=action.action_type,
            success=success,
            metrics={
                "engagement_rate": random.uniform(0.01, 0.1),
                "virality_score": random.uniform(0.0, 1.0)
            },
            timestamp=datetime.now()
        )
        
        # Add content-specific feedback
        if action.action_type == "create_content":
            feedback.content_id = f"content_{action.agent_id}_{int(action.timestamp.timestamp())}"
            feedback.engagement_metrics = {
                "likes": random.randint(10, 1000),
                "shares": random.randint(5, 200),
                "comments": random.randint(2, 100),
                "views": random.randint(100, 10000)
            }
            feedback.audience_reaction = {
                "sentiment": random.uniform(0.5, 1.0),
                "topics": ["general"]
            }
        
        return feedback
    
    async def handle_agent_evolution(self, agent_id: str) -> None:
        """Handle agent evolution"""
        if agent_id not in self.agents:
            return
        
        agent = self.agents[agent_id]
        
        # Check if agent should evolve
        performance = agent.get_current_state().performance_metrics
        
        if performance.learning_progress > 0.7:
            # Agent is performing well, consider stage transition
            current_stage = agent.learning_stage
            
            from Agent import LearningStage
            stage_order = [
                LearningStage.COLD_START,
                LearningStage.BANDIT,
                LearningStage.REINFORCEMENT,
                LearningStage.EVOLUTION
            ]
            
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                new_stage = stage_order[current_index + 1]
                agent.transition_learning_stage(new_stage)
                
                self.logger.info(f"Agent evolved", extra={
                    "agent_id": agent_id,
                    "old_stage": current_stage.value,
                    "new_stage": new_stage.value
                })
    
    async def evaluate_all_agents(self) -> Dict[str, Any]:
        """Evaluate performance of all agents"""
        evaluations = {}
        
        for agent_id, agent in self.agents.items():
            state = agent.get_current_state()
            evaluations[agent_id] = {
                "role": state.role.value,
                "learning_stage": state.learning_stage.value,
                "total_actions": state.performance_metrics.total_actions,
                "success_rate": state.performance_metrics.successful_actions / max(state.performance_metrics.total_actions, 1),
                "average_reward": state.performance_metrics.average_reward,
                "cumulative_reward": state.performance_metrics.cumulative_reward,
                "learning_progress": state.performance_metrics.learning_progress
            }
        
        self.logger.info(f"Evaluated {len(evaluations)} agents")
        
        return evaluations
    
    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Get overall agent statistics"""
        stats = {
            "total_agents": len(self.agents),
            "active_agents": len([s for s in self.agent_states.values() if s["status"] == "active"]),
            "total_actions": sum(s["action_count"] for s in self.agent_states.values()),
            "by_role": {}
        }
        
        # Group by role
        for agent_id, state in self.agent_states.items():
            role = state["role"]
            if role not in stats["by_role"]:
                stats["by_role"][role] = {
                    "count": 0,
                    "total_actions": 0
                }
            
            stats["by_role"][role]["count"] += 1
            stats["by_role"][role]["total_actions"] += state["action_count"]
        
        return stats
    
    async def shutdown(self) -> None:
        """Shutdown orchestrator"""
        self.logger.info("Shutting down AgentOrchestrator")
        
        # Clear agents
        self.agents.clear()
        self.agent_states.clear()
        
        self.is_initialized = False

