"""
Logging Configuration for Arena System
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogConfig:
    """Configuration for logging system"""

    # Base directory for all logs
    trace_dir: Path = Path("trace")

    # Log level
    log_level: LogLevel = LogLevel.INFO

    # Rotation settings
    max_bytes: int = 100 * 1024 * 1024  # 100MB
    backup_count: int = 30  # Keep 30 days

    # Format settings
    use_json: bool = True
    include_timestamp: bool = True
    include_trace_id: bool = True
    include_context: bool = True

    # Performance settings
    async_logging: bool = True
    buffer_size: int = 1000

    # Component-specific settings
    components: dict = None

    def __post_init__(self):
        """Initialize configuration"""
        if self.components is None:
            self.components = {
                'agents': LogLevel.INFO,
                'simulation': LogLevel.INFO,
                'performance': LogLevel.DEBUG,
                'errors': LogLevel.ERROR,
                'experiments': LogLevel.INFO,
                'integration': LogLevel.INFO,
                'system': LogLevel.INFO,
            }

        # Ensure trace directory exists
        self.trace_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        for component in self.components.keys():
            (self.trace_dir / component).mkdir(exist_ok=True)


# Global configuration instance
_global_config: Optional[LogConfig] = None


def configure_logging(config: Optional[LogConfig] = None) -> LogConfig:
    """Configure global logging settings"""
    global _global_config

    if config is None:
        config = LogConfig()

    _global_config = config
    return config


def get_config() -> LogConfig:
    """Get current logging configuration"""
    global _global_config

    if _global_config is None:
        _global_config = configure_logging()

    return _global_config
