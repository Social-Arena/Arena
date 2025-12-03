# Arena - Social Arena Orchestrator

**Arena** is the integration layer that orchestrates the three core Social Arena packages into a complete, configurable social media simulation system.

## Overview

Arena connects:
- **[Agent](https://github.com/Social-Arena/Agent)** - AI agents with 9 fundamental social actions (post, reply, retweet, quote, like, unlike, follow, unfollow, decide)
- **[Feed](https://github.com/Social-Arena/Feed)** - Twitter-style Pydantic data models for posts, entities, and metrics
- **[Recommendation](https://github.com/Social-Arena/Recommendation)** - Centralized recommendation system with multiple ranking strategies (Twitter-style algorithm)

Arena provides a **CLI-driven simulation** that:
- Creates N agents with diverse profiles
- Runs multi-day simulations where agents post, react, and interact
- Uses LLM (OpenAI/Anthropic) to drive agent decision-making
- Tracks recommendation mappings (which feeds were shown to which agents)
- Saves structured output in separate folders for agents, feeds, and recommendations

Built from `external/Agent/examples/simple_simulation.py` but upgraded to:
- Use real `CentralizedRecommendationSystem` + `BalancedStrategy` from the recommendation package
- Use `feed.Feed` Pydantic models throughout
- Provide structured, analyzable output
- Support configurable simulation parameters via CLI

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

**Option A: Using environment variables directly**

```bash
source venv/bin/activate

# Set your API key directly
export OPENAI_API_KEY="your_actual_openai_key_here"
python -m agent --provider openai --port 8000

# Or for Anthropic/Claude:
# export ANTHROPIC_API_KEY="your_actual_anthropic_key_here"
# python -m agent --provider anthropic --port 8000
```

**Option B: Using .env file with dotenv**

```bash
source venv/bin/activate

# Load .env and start (requires python-dotenv)
python -c "from dotenv import load_dotenv; load_dotenv(); import os; os.system('python -m agent --provider openai --port 8000')"
```

**Option C: Source .env manually**

```bash
source venv/bin/activate

# Load .env (remove quotes from values first)
set -a
source .env
set +a

python -m agent --provider openai --port 8000
```

**Note:** The agent host needs `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` environment variable set before starting.

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

## Key Features

- ✅ **No try/except blocks** - Clean error propagation using Pydantic validation
- ✅ **Structured output** - Separate folders for agents, feeds, and recommendations
- ✅ **Daily snapshots** - Agent states saved after each simulation day
- ✅ **Recommendation tracking** - Records which feeds were recommended to which agents each day
- ✅ **Configurable** - All simulation parameters controllable via CLI arguments
- ✅ **LLM-driven** - Agents make realistic decisions using OpenAI or Anthropic models
- ✅ **Scalable** - Tested with 10+ agents over multiple days
- ✅ **Analyzable** - All data saved as JSON for post-simulation analysis

---

## Simulation Flow

### Daily Cycle

Each simulation day follows this pattern:

1. **Morning (Content Creation)**
   - Each agent creates `post_per_day` posts
   - Posts are ingested into the recommendation system's global feed pool
   - Example: 10 agents × 5 posts = 50 new posts per day

2. **Afternoon (Content Discovery)**
   - Each agent fetches `fetch_per_day` posts from the recommendation system
   - Recommendation system uses `BalancedStrategy` (exploration + exploitation)
   - Mappings saved: which feeds were shown to which agent

3. **Decision Making**
   - LLM analyzes the recommended feeds for each agent
   - Agent decides: like, reply, follow, or idle
   - Decision based on agent's personality (bio) and feed content

4. **Action Execution**
   - Agent executes the chosen action
   - New content (replies) fed back into the system
   - Social graph updated (follows)
   - Engagement signals recorded

5. **Evening (State Persistence)**
   - Each agent's state saved to `agents/agent_XXX_dayYYY.json`
   - Includes: following, followers, liked tweets, stats

### After All Days

- All feeds saved to `feeds/all_feeds.json`
- Recommendation mappings show the complete history of what was shown to whom
- Final recommendation system state saved with social graph and statistics

---

## Architecture

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


