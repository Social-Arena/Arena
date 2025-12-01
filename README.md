## Social Arena - Arena Orchestrator

Arena is the **integration layer** that connects the three core Social Arena
packages into a single, configurable simulation:

- **Agent**: AI agents with 9 fundamental social actions (`agent` package)
- **Feed**: Twitter-style Pydantic data models (`feed` package)
- **Recommendation**: Centralized recommendation system (`recommendation` package, Twitter-style algorithm)  
  (see the Recommendation README for details: `https://github.com/Social-Arena/Recommendation`).

Arena is built directly from the example in `external/Agent/examples/simple_simulation.py`,
but upgraded to:

- Use the real `CentralizedRecommendationSystem` + `BalancedStrategy`
- Use `feed.Feed` Pydantic models throughout the feed pool
- Provide a configurable, reusable Python API

---

### Installation

Install Arena and its three dependencies via pip:

```bash
pip install "arena @ git+https://github.com/Social-Arena/Arena.git"
```

This will also install:

- `agent @ git+https://github.com/Social-Arena/Agent.git`
- `feed @ git+https://github.com/Social-Arena/Feed.git`
- `recommendation @ git+https://github.com/Social-Arena/Recommendation.git`

If you are working from this repository with submodules checked out:

```bash
cd /Users/access/Social-Arena/Arena
python -m venv venv
source venv/bin/activate
pip install -e external/Feed
pip install -e external/Recommendation
pip install -e external/Agent
pip install -e .
```

---

### Quick Start

1. **Start an LLM host** (from the `agent` package) in one terminal:

```bash
source venv/bin/activate
agent-host --provider openai --port 8000
```

2. **Run an Arena simulation** in another terminal:

```python
import asyncio

from arena import (
    ArenaAgentConfig,
    ArenaConfig,
    ArenaSimulation,
)


async def main() -> None:
    config = ArenaConfig(
        agents=[
            ArenaAgentConfig(agent_id="agent_a", username="alice", bio="Tech enthusiast"),
            ArenaAgentConfig(agent_id="agent_b", username="bob", bio="Crypto investor"),
            ArenaAgentConfig(agent_id="agent_c", username="carol", bio="AI researcher"),
        ],
    )

    sim = ArenaSimulation(config=config)
    result = await sim.run()
    print("Simulation cache:", result.cache_dir)
    print("Recommendation stats:", result.recommendation_stats)


if __name__ == "__main__":
    asyncio.run(main())
```

This will:

- Create three agents
- Run a multi-day simulation (defaults: 30 days, 3 posts/agent/day)
- Use `CentralizedRecommendationSystem` + `BalancedStrategy`
- Save results under `examples/cache/sim_TIMESTAMP/` (feeds, agents, social graph, actions, stats)

---

### Configuration

Arena uses Pydantic models for all configuration (`arena.config`):

- `ArenaAgentConfig`: agent_id, username, bio
- `ArenaLLMConfig`: base_url, api_key, model, temperature, max_tokens
- `ArenaSimulationConfig`: num_days, posts_per_agent_per_day, max_feeds_per_agent, explore_ratio, cache_root
- `ArenaConfig`: ties agents + llm + simulation together

You can construct these directly in Python or load them however you like
before passing into `ArenaSimulation`.

---

### Internal Architecture

```text
┌───────────────────────────────────────────┐
│                ArenaSimulation            │
│   (Orchestrates Agent + Feed + RecSys)   │
└───────────────┬──────────────────────────┘
                │
      ┌─────────▼─────────┐
      │ CentralizedRecommendationSystem │  recommendation
      └─────────┬─────────┘
                │
      ┌─────────▼─────────┐
      │       Agents       │  agent.Agent (Pydantic)
      └─────────┬─────────┘
                │
      ┌─────────▼─────────┐
      │    Feeds (Pydantic)│  feed.Feed
      └────────────────────┘
```

For the underlying recommendation algorithm details, see the
Recommendation repository README: `https://github.com/Social-Arena/Recommendation`.


