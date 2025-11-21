"""
Arena Configuration Management
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ArenaConfig:
    """Configuration for Arena orchestration system"""
    
    # Agent configuration
    num_agents: int = 100
    agent_distribution: Dict[str, int] = field(default_factory=lambda: {
        "creator": 30,
        "audience": 50,
        "brand": 15,
        "moderator": 5
    })
    
    # Simulation parameters
    simulation_duration: int = 72  # hours
    time_step_duration: int = 60  # seconds per step
    
    # Resource limits
    max_memory_per_agent: int = 512  # MB
    max_cpu_per_agent: float = 0.5  # cores
    api_rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "twitter": 100,  # requests per minute
        "feed_system": 1000
    })
    
    # Experiment settings
    enable_ab_testing: bool = True
    experiment_duration: int = 24  # hours
    
    # Monitoring
    metrics_collection_interval: int = 10  # seconds
    dashboard_update_interval: int = 5  # seconds
    
    # Trace logging
    trace_log_level: str = "INFO"
    trace_storage_days: int = 30
    trace_dir: Path = field(default_factory=lambda: Path("trace"))
    
    # Feed system integration
    feed_storage_dir: Path = field(default_factory=lambda: Path("feeds"))
    
    # Simulation modes
    real_time_mode: bool = False  # False = accelerated simulation
    acceleration_factor: int = 10  # How much faster than real-time
    
    # Evolution parameters
    enable_evolution: bool = True
    evolution_check_interval: int = 100  # time steps
    
    # Safety and limits
    max_concurrent_agents: int = 1000
    max_actions_per_step: int = 10000
    emergency_stop_threshold: float = 0.9  # System load threshold
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Check agent distribution sums correctly
        if sum(self.agent_distribution.values()) != self.num_agents:
            return False
        
        # Check positive values
        if self.simulation_duration <= 0 or self.time_step_duration <= 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "num_agents": self.num_agents,
            "agent_distribution": self.agent_distribution,
            "simulation_duration": self.simulation_duration,
            "time_step_duration": self.time_step_duration,
            "max_memory_per_agent": self.max_memory_per_agent,
            "max_cpu_per_agent": self.max_cpu_per_agent,
            "api_rate_limits": self.api_rate_limits,
            "enable_ab_testing": self.enable_ab_testing,
            "experiment_duration": self.experiment_duration,
            "metrics_collection_interval": self.metrics_collection_interval,
            "dashboard_update_interval": self.dashboard_update_interval,
            "trace_log_level": self.trace_log_level,
            "trace_storage_days": self.trace_storage_days,
            "trace_dir": str(self.trace_dir),
            "feed_storage_dir": str(self.feed_storage_dir),
            "real_time_mode": self.real_time_mode,
            "acceleration_factor": self.acceleration_factor,
            "enable_evolution": self.enable_evolution,
            "evolution_check_interval": self.evolution_check_interval,
            "max_concurrent_agents": self.max_concurrent_agents,
            "max_actions_per_step": self.max_actions_per_step,
            "emergency_stop_threshold": self.emergency_stop_threshold
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ArenaConfig':
        """Create config from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})


def get_default_config() -> ArenaConfig:
    """Get default arena configuration"""
    return ArenaConfig()


def load_config(config_path: Path) -> ArenaConfig:
    """Load configuration from file"""
    import json
    
    if not config_path.exists():
        return get_default_config()
    
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    return ArenaConfig.from_dict(config_dict)


def save_config(config: ArenaConfig, config_path: Path) -> None:
    """Save configuration to file"""
    import json
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)

