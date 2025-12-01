from typing import List, Optional

from pydantic import BaseModel, Field


class ArenaAgentConfig(BaseModel):
    """Configuration for a single simulated agent."""

    agent_id: str
    username: str
    bio: Optional[str] = None


class ArenaLLMConfig(BaseModel):
    """
    Configuration for the LLM host used to drive agent decisions.

    By default this assumes an `agent-host` (from the `agent` package)
    is running locally at http://localhost:8000, as described in the
    Agent examples.
    """

    base_url: str = "http://localhost:8000/v1"
    api_key: str = "not-needed"
    model: str = "default"
    temperature: float = 0.7
    max_tokens: int = 50


class ArenaSimulationConfig(BaseModel):
    """High-level knobs for the Arena simulation."""

    num_days: int = Field(default=30, ge=1)
    posts_per_agent_per_day: int = Field(default=3, ge=1)
    max_feeds_per_agent: int = Field(default=5, ge=1)
    explore_ratio: float = Field(default=0.2, ge=0.0, le=1.0)
    cache_root: str = "examples/cache"


class ArenaConfig(BaseModel):
    """
    Top-level Arena configuration tying together agents, LLM, and simulation.
    """

    agents: List[ArenaAgentConfig]
    llm: ArenaLLMConfig = Field(default_factory=ArenaLLMConfig)
    simulation: ArenaSimulationConfig = Field(default_factory=ArenaSimulationConfig)


