"""
Arena Manager - The brain of the entire simulation system
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

from Arena.config.arena_config import ArenaConfig
from Arena.core.agent_orchestrator import AgentOrchestrator
from Arena.core.simulation_engine import SimulationEngine
from Arena.scheduling.task_scheduler import TaskScheduler
from Arena.scheduling.resource_manager import ResourceManager
from Arena.metrics.virality_tracker import ViralityTracker
from Arena.metrics.performance_monitor import PerformanceMonitor
from Arena.trace_logging import get_logger


class ArenaManager:
    """
    Arena Manager - Global coordination manager
    
    The brain of Arena, coordinating all components and managing the simulation lifecycle.
    """
    
    def __init__(self, config: ArenaConfig):
        self.config = config
        self.logger = get_logger("arena_manager", "system")
        
        # Core components
        self.agent_orchestrator: Optional[AgentOrchestrator] = None
        self.simulation_engine: Optional[SimulationEngine] = None
        self.task_scheduler: Optional[TaskScheduler] = None
        self.resource_manager: Optional[ResourceManager] = None
        
        # Metrics tracking
        self.virality_tracker: Optional[ViralityTracker] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        
        # State
        self.agents: Dict[str, Any] = {}
        self.is_initialized: bool = False
        self.is_running: bool = False
        self.current_time_step: int = 0
        self.start_time: Optional[datetime] = None
        
        # Simulation results
        self.simulation_results: Dict[str, Any] = {}
        
        self.logger.info("ArenaManager created", extra={
            "num_agents": config.num_agents,
            "simulation_duration": config.simulation_duration
        })
    
    async def initialize_arena(self) -> None:
        """
        Initialize the arena environment
        
        Sets up all components and prepares for simulation.
        """
        if self.is_initialized:
            self.logger.warning("Arena already initialized")
            return
        
        self.logger.info("Initializing Arena...")
        
        # Create directories
        self.config.trace_dir.mkdir(parents=True, exist_ok=True)
        self.config.feed_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize core components
        self.agent_orchestrator = AgentOrchestrator(self.config)
        await self.agent_orchestrator.initialize()
        
        self.simulation_engine = SimulationEngine(self.config)
        await self.simulation_engine.initialize()
        
        self.task_scheduler = TaskScheduler(self.config)
        self.resource_manager = ResourceManager(self.config)
        
        # Initialize metrics
        self.virality_tracker = ViralityTracker()
        self.performance_monitor = PerformanceMonitor(self.config)
        
        self.is_initialized = True
        
        self.logger.info("Arena initialized successfully")
    
    async def deploy_agent(self, agent_config: Dict[str, Any]) -> str:
        """
        Deploy a new agent to the arena
        
        Args:
            agent_config: Agent configuration dictionary
            
        Returns:
            Agent ID
        """
        if not self.is_initialized:
            raise RuntimeError("Arena not initialized. Call initialize_arena() first.")
        
        agent_id = await self.agent_orchestrator.create_agent(agent_config)
        self.agents[agent_id] = {
            "config": agent_config,
            "deployed_at": datetime.now(),
            "status": "active"
        }
        
        self.logger.info(f"Agent deployed", extra={
            "agent_id": agent_id,
            "role": agent_config.get("role"),
            "total_agents": len(self.agents)
        })
        
        return agent_id
    
    async def deploy_agents(self, agent_configs: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Deploy multiple agents based on configuration
        
        Args:
            agent_configs: Optional list of agent configurations.
                          If None, creates agents based on config.agent_distribution
        
        Returns:
            List of agent IDs
        """
        if agent_configs is None:
            # Create agents based on distribution
            agent_configs = self._generate_agent_configs()
        
        agent_ids = []
        for agent_config in agent_configs:
            agent_id = await self.deploy_agent(agent_config)
            agent_ids.append(agent_id)
        
        self.logger.info(f"Deployed {len(agent_ids)} agents")
        return agent_ids
    
    def _generate_agent_configs(self) -> List[Dict[str, Any]]:
        """Generate agent configurations based on distribution"""
        configs = []
        
        for role, count in self.config.agent_distribution.items():
            for i in range(count):
                agent_id = f"{role}_{i:03d}"
                config = {
                    "agent_id": agent_id,
                    "role": role,
                    "learning_stage": "cold_start"
                }
                
                # Add role-specific config
                if role == "creator":
                    config["niche_specialty"] = self._assign_niche(i)
                elif role == "audience":
                    config["interests"] = self._assign_interests(i)
                elif role == "brand":
                    config["brand_name"] = f"Brand_{i:03d}"
                    config["marketing_budget"] = 10000.0
                
                configs.append(config)
        
        return configs
    
    def _assign_niche(self, index: int) -> str:
        """Assign niche specialty to creator"""
        niches = ["technology", "lifestyle", "entertainment", "education", "news"]
        return niches[index % len(niches)]
    
    def _assign_interests(self, index: int) -> List[str]:
        """Assign interests to audience"""
        interest_groups = [
            ["technology", "AI", "programming"],
            ["lifestyle", "fashion", "travel"],
            ["entertainment", "music", "movies"],
            ["education", "science", "learning"],
            ["news", "politics", "business"]
        ]
        return interest_groups[index % len(interest_groups)]
    
    async def run_simulation_step(self) -> Dict[str, Any]:
        """
        Execute one simulation step
        
        Returns:
            Dictionary with step results
        """
        if not self.is_initialized:
            raise RuntimeError("Arena not initialized")
        
        step_start = datetime.now()
        
        # Update environment state
        environment_state = await self.simulation_engine.update_environment_state()
        
        # Orchestrate agent actions
        agent_actions = await self.agent_orchestrator.orchestrate_agent_actions(
            self.current_time_step,
            environment_state
        )
        
        # Track virality
        viral_metrics = await self.virality_tracker.track_step(agent_actions)
        
        # Collect performance metrics
        performance_metrics = await self.performance_monitor.collect_metrics()
        
        # Update time step
        self.current_time_step += 1
        
        step_duration = (datetime.now() - step_start).total_seconds()
        
        result = {
            "time_step": self.current_time_step,
            "timestamp": datetime.now().isoformat(),
            "agent_actions": len(agent_actions),
            "viral_content_count": viral_metrics.get("viral_count", 0),
            "step_duration": step_duration,
            "performance": performance_metrics
        }
        
        self.logger.debug(f"Simulation step completed", extra=result)
        
        return result
    
    async def run_simulation(self) -> Dict[str, Any]:
        """
        Run complete simulation
        
        Returns:
            Final simulation results
        """
        if not self.is_initialized:
            raise RuntimeError("Arena not initialized")
        
        self.logger.info("Starting simulation", extra={
            "duration_hours": self.config.simulation_duration,
            "num_agents": len(self.agents)
        })
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Calculate total steps
        total_steps = (self.config.simulation_duration * 3600) // self.config.time_step_duration
        
        step_results = []
        
        for step in range(total_steps):
            if not self.is_running:
                self.logger.warning("Simulation stopped early")
                break
            
            try:
                result = await self.run_simulation_step()
                step_results.append(result)
                
                # Log progress every 100 steps
                if step % 100 == 0:
                    progress = (step / total_steps) * 100
                    self.logger.info(f"Simulation progress: {progress:.1f}%", extra={
                        "step": step,
                        "total_steps": total_steps
                    })
                
                # Check for emergency stop
                if self.performance_monitor.should_emergency_stop():
                    self.logger.critical("Emergency stop triggered")
                    break
                
            except Exception as e:
                self.logger.error(f"Error in simulation step {step}", extra={
                    "error": str(e)
                })
                # Continue simulation despite errors
        
        self.is_running = False
        end_time = datetime.now()
        
        # Generate final results
        self.simulation_results = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": (end_time - self.start_time).total_seconds(),
            "total_steps": len(step_results),
            "total_agents": len(self.agents),
            "step_results": step_results,
            "final_metrics": await self.collect_final_metrics()
        }
        
        self.logger.info("Simulation completed", extra={
            "duration": self.simulation_results["duration"],
            "total_steps": self.simulation_results["total_steps"]
        })
        
        return self.simulation_results
    
    async def pause_simulation(self) -> None:
        """Pause the simulation"""
        self.is_running = False
        self.logger.info("Simulation paused")
    
    async def resume_simulation(self) -> None:
        """Resume the simulation"""
        self.is_running = True
        self.logger.info("Simulation resumed")
    
    async def stop_simulation(self) -> None:
        """Stop the simulation"""
        self.is_running = False
        self.logger.info("Simulation stopped")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current simulation metrics"""
        return {
            "time_step": self.current_time_step,
            "active_agents": len([a for a in self.agents.values() if a["status"] == "active"]),
            "viral_metrics": await self.virality_tracker.get_current_metrics(),
            "performance_metrics": await self.performance_monitor.get_current_metrics()
        }
    
    async def collect_final_metrics(self) -> Dict[str, Any]:
        """Collect final metrics after simulation"""
        return {
            "virality": await self.virality_tracker.generate_report(),
            "performance": await self.performance_monitor.generate_report(),
            "agents": await self.agent_orchestrator.get_agent_statistics()
        }
    
    async def evaluate_agents(self) -> Dict[str, Any]:
        """Evaluate all agent performances"""
        return await self.agent_orchestrator.evaluate_all_agents()
    
    async def generate_simulation_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive simulation report
        
        Returns:
            Complete simulation report
        """
        if not self.simulation_results:
            self.logger.warning("No simulation results available")
            return {}
        
        report = {
            "simulation_info": {
                "config": self.config.to_dict(),
                "start_time": self.simulation_results["start_time"],
                "end_time": self.simulation_results["end_time"],
                "duration_seconds": self.simulation_results["duration"],
                "total_steps": self.simulation_results["total_steps"]
            },
            "agent_statistics": await self.agent_orchestrator.get_agent_statistics(),
            "viral_propagation": await self.virality_tracker.generate_report(),
            "performance_analysis": await self.performance_monitor.generate_report(),
            "summary": self._generate_summary()
        }
        
        self.logger.info("Simulation report generated")
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not self.simulation_results:
            return {}
        
        step_results = self.simulation_results.get("step_results", [])
        
        total_actions = sum(r.get("agent_actions", 0) for r in step_results)
        total_viral = sum(r.get("viral_content_count", 0) for r in step_results)
        avg_step_duration = sum(r.get("step_duration", 0) for r in step_results) / max(len(step_results), 1)
        
        return {
            "total_agent_actions": total_actions,
            "total_viral_content": total_viral,
            "average_step_duration_seconds": avg_step_duration,
            "actions_per_second": total_actions / max(self.simulation_results["duration"], 1)
        }
    
    async def shutdown(self) -> None:
        """Shutdown arena and cleanup resources"""
        self.logger.info("Shutting down Arena...")
        
        # Stop simulation if running
        if self.is_running:
            await self.stop_simulation()
        
        # Cleanup components
        if self.agent_orchestrator:
            await self.agent_orchestrator.shutdown()
        
        if self.simulation_engine:
            await self.simulation_engine.shutdown()
        
        self.is_initialized = False
        
        self.logger.info("Arena shutdown complete")

