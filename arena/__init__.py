"""
Arena - Social Arena Orchestrator Package

This package integrates:
- `agent`: AI agents with 9 fundamental social actions
- `feed`: Twitter-style Pydantic data models
- `recommendation`: Centralized recommendation system

Arena provides a high-level simulation facade built from the
`external/Agent/examples/simple_simulation.py` example.
"""

from .config import (
    ArenaAgentConfig,
    ArenaLLMConfig,
    ArenaSimulationConfig,
    ArenaConfig,
)
from .simulation import ArenaSimulation, ArenaRunResult

__all__ = [
    "ArenaAgentConfig",
    "ArenaLLMConfig",
    "ArenaSimulationConfig",
    "ArenaConfig",
    "ArenaSimulation",
    "ArenaRunResult",
]


