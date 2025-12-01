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

#### Option 1: Install from GitHub (recommended for users)

```bash
pip install "arena @ git+https://github.com/Social-Arena/Arena.git@dev"
```

This will also install the `dev` branches of:

- `agent @ git+https://github.com/Social-Arena/Agent.git@dev`
- `feed @ git+https://github.com/Social-Arena/Feed.git@dev`
- `recommendation @ git+https://github.com/Social-Arena/Recommendation.git@dev`

#### Option 2: Local development with submodules

If you are working from this repository with submodules checked out:

```bash
# Clone the repository
git clone https://github.com/Social-Arena/Arena.git
cd Arena

# Initialize and update submodules
git submodule update --init --recursive

# Checkout dev branch for each submodule
cd external/Feed && git checkout dev && cd ../..
cd external/Recommendation && git checkout dev && cd ../..
cd external/Agent && git checkout dev && cd ../..

# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies from local submodules (dev branches)
pip install -e external/Feed
pip install -e external/Recommendation
pip install -e external/Agent

# Install Arena itself
pip install -e .
```

---

### Quick Start

#### 1. Set up your API keys

Create a `.env` file in the Arena root directory:

```bash
# Copy the template from Agent submodule
cp external/Agent/env.template .env

# Edit .env and add your API key
# OPENAI_API_KEY=your_actual_openai_key_here
# or
# ANTHROPIC_API_KEY=your_actual_anthropic_key_here
```

#### 2. Start an LLM host

In one terminal, start the agent LLM host:

```bash
source venv/bin/activate

# Load .env and start OpenAI host
export $(cat .env | grep -v '^#' | xargs)
python -m agent --provider openai --port 8000

# Or for Anthropic/Claude:
# python -m agent --provider anthropic --port 8000
```

#### 3. Run an Arena simulation

```bash
source venv/bin/activate
python arena.py -n_of_agents 10 -post_per_day 5 -days_of_simulations 5
```

**CLI Arguments:**
- `-n_of_agents`: Number of agents to create (default: 10)
- `-post_per_day`: Posts each agent creates per day (default: 5)
- `-days_of_simulations`: Number of days to simulate (default: 5)
- `-fetch_per_day`: Posts each agent fetches from recommendation system per day (default: 10)
- `-explore_ratio`: Exploration ratio for recommendations (default: 0.2)
- `-output`: Output directory (default: `cache/arena_output_TIMESTAMP`)

**Output Structure:**
```
cache/arena_output_20241201_123456/
├── agents/           # Individual agent cache files per day
│   ├── agent_000_day000.json  # Initial state
│   ├── agent_000_day001.json  # After day 1
│   ├── agent_000_day002.json  # After day 2
│   └── ...
├── feeds/            # All feeds created during simulation
│   └── all_feeds.json
└── recommendation/   # Recommendation mappings and state
    ├── agent_000_day001_mapping.json  # What feeds were recommended to each agent
    ├── agent_001_day001_mapping.json
    └── recommendation_state.json       # Final recommendation system state
```

**What happens during simulation:**

Each day:
1. **Morning**: Each agent creates `post_per_day` posts → ingested into recommendation system
2. **Afternoon**: Each agent fetches `fetch_per_day` posts from recommendation system
3. **Decision**: LLM decides what action to take (like, reply, follow, idle)
4. **Action**: Agent executes the action and updates state
5. **Evening**: Agent states saved to `agents/` folder

After all days:
- All feeds saved to `feeds/all_feeds.json`
- Recommendation mappings show which feeds were sent to which agents
- Final recommendation system state saved

**Example:**
With 10 agents, 5 posts/day, 5 days:
- **Agents folder**: 10 agents × 6 states (initial + 5 days) = 60 JSON files
- **Feeds folder**: 10 agents × 5 posts/day × 5 days = 250+ feeds (plus replies)
- **Recommendation folder**: Daily mappings + final state

---

### Architecture

```text
┌───────────────────────────────────────────┐
│           ArenaSimulationCLI              │
│   (Orchestrates Agent + Feed + RecSys)   │
└───────────────┬──────────────────────────┘
                │
      ┌─────────▼─────────┐
      │ CentralizedRecommendationSystem │  recommendation
      │     + BalancedStrategy           │
      └─────────┬─────────┘
                │
      ┌─────────▼─────────┐
      │    N Agents        │  agent.Agent (Pydantic)
      └─────────┬─────────┘
                │
      ┌─────────▼─────────┐
      │  Feeds (Pydantic)  │  feed.Feed
      └────────────────────┘
```

For the underlying recommendation algorithm details, see the
Recommendation repository README: `https://github.com/Social-Arena/Recommendation`.

---


