"""
Arena - Social Arena Orchestrator Package

This package integrates:
- `agent`: AI agents with 9 fundamental social actions
- `feed`: Twitter-style Pydantic data models
- `recommendation`: Centralized recommendation system

Arena provides a CLI-driven simulation built from the
`external/Agent/examples/simple_simulation.py` example.
"""

from .config import (
    ArenaAgentConfig,
    ArenaLLMConfig,
    ArenaSimulationConfig,
    ArenaConfig,
)
from .cli import ArenaSimulationCLI, CLISimulationResult

__all__ = [
    "ArenaAgentConfig",
    "ArenaLLMConfig",
    "ArenaSimulationConfig",
    "ArenaConfig",
    "ArenaSimulationCLI",
    "CLISimulationResult",
]


