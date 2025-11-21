# Arena - Global Orchestration Center 🏟️

**The Operating System of Social-Arena**

Arena is the **core control center** of the entire social media viral propagation agent simulation system. It orchestrates all subsystems, manages agent lifecycles, controls experiments, and maintains the real-time simulation environment.

---

## 📋 Table of Contents

- [Core Responsibilities](#core-responsibilities)
- [System Architecture](#system-architecture)
- [Directory Structure](#directory-structure)
- [Core Modules](#core-modules)
- [Simulation Flow](#simulation-flow)
- [Integration Interfaces](#integration-interfaces)
- [Configuration Management](#configuration-management)
- [Trace Logging System](#trace-logging-system)
- [Development Guide](#development-guide)
- [Performance Requirements](#performance-requirements)

---

## 🎯 Core Responsibilities

Arena serves as the "operating system" for the entire simulation, responsible for:

### 1. **Unified Scheduling**
- Manage lifecycles of 100-1000 agents
- Allocate tasks and resources
- Coordinate cross-module operations
- Handle concurrent requests

### 2. **Simulation Environment Maintenance**
- Create realistic social media environments
- Simulate ranking algorithm pressure
- Inject trend shocks
- Manage user sessions

### 3. **Experiment Control**
- A/B testing framework
- Hot-swappable strategies
- Evolution tracking
- Results analysis

### 4. **Performance Monitoring**
- Viral propagation tracking
- System metrics collection
- Real-time dashboards
- Anomaly detection

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Arena Manager                          │
│         (Global Coordination Manager - The Brain)        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Agent        │  │ Simulation   │  │ Resource     │  │
│  │ Orchestrator │  │ Engine       │  │ Manager      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Task         │  │ Metrics      │  │ Experiment   │  │
│  │ Scheduler    │  │ Tracker      │  │ Framework    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
  ┌────────────┐   ┌────────────┐   ┌────────────┐
  │ Feed       │   │Recommend   │   │ Scrapper   │
  │ System     │   │ System     │   │ System     │
  └────────────┘   └────────────┘   └────────────┘
           │                │                │
           └────────────────┴────────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │ Agent Pool   │
                  │ (100-1000)   │
                  └──────────────┘
```

---

## 📁 Directory Structure

```
arena/
│
├── core/                          # Core management modules
│   ├── __init__.py
│   ├── arena_manager.py           # Main Arena coordinator
│   ├── agent_orchestrator.py     # Agent lifecycle management
│   └── simulation_engine.py      # Simulation environment engine
│
├── scheduling/                    # Task scheduling system
│   ├── __init__.py
│   ├── task_scheduler.py         # Intelligent task allocation
│   └── resource_manager.py       # Compute resource management
│
├── metrics/                       # Monitoring and metrics
│   ├── __init__.py
│   ├── virality_tracker.py       # Viral propagation tracking
│   └── performance_monitor.py    # System performance monitoring
│
├── experiments/                   # Experiment framework
│   ├── __init__.py
│   ├── ab_testing.py             # A/B testing framework
│   └── evolution_tracker.py      # Strategy evolution tracking
│
├── config/                        # Configuration management
│   ├── __init__.py
│   └── arena_config.py           # Arena configuration
│
├── tests/                         # Test suite
│   ├── test_core.py
│   ├── test_scheduler.py
│   ├── test_metrics.py
│   └── test_experiments.py
│
├── examples/                      # Usage examples
│   ├── simple_simulation.py
│   ├── full_simulation_example.py
│   └── experiment_example.py
│
└── README.md                      # This file
```

---

## 🧩 Core Modules

### 1. Arena Manager (`core/arena_manager.py`)

The brain of Arena, coordinating all components.

```python
class ArenaManager:
    """Global coordination manager - Arena's brain"""
    
    def __init__(self, config: ArenaConfig):
        self.agents: Dict[str, Agent] = {}          # Agent pool
        self.feed_manager: FeedManager = None       # Feed manager
        self.recommender: Recommender = None        # Recommendation system
        self.scraper: Scraper = None               # Data collector
        self.metrics_tracker: MetricsTracker = None # Metrics tracker
    
    async def initialize_arena(self) -> None:
        """Initialize the arena environment"""
        
    async def deploy_agent(self, agent_config: AgentConfig) -> str:
        """Deploy a new agent to the arena"""
        
    async def run_simulation_step(self) -> SimulationResult:
        """Execute one simulation step"""
        
    async def evaluate_agents(self) -> Dict[str, AgentMetrics]:
        """Evaluate all agent performances"""
```

**Key Features:**
- Manages all system components
- Coordinates agent deployment and lifecycle
- Executes simulation steps
- Collects and aggregates metrics

---

### 2. Agent Orchestrator (`core/agent_orchestrator.py`)

Manages agent lifecycles and task allocation.

```python
class AgentOrchestrator:
    """Agent orchestrator - manages agent lifecycle and task allocation"""
    
    async def orchestrate_agent_actions(self, time_step: int) -> None:
        """Orchestrate agent actions
        
        1. Analyze current state
        2. Assign tasks to agents
        3. Handle inter-agent interactions
        4. Collect feedback and update
        """
    
    async def handle_agent_evolution(self, agent_id: str) -> None:
        """Handle agent evolution"""
    
    async def balance_agent_load(self) -> LoadBalanceReport:
        """Balance computational load across agents"""
```

**Key Features:**
- Dynamic task allocation
- Agent interaction coordination
- Evolution management
- Load balancing

---

### 3. Simulation Engine (`core/simulation_engine.py`)

Creates realistic social media environments.

```python
class SimulationEngine:
    """Simulation engine - creates realistic social media environment"""
    
    async def simulate_ranking_pressure(self) -> None:
        """Simulate ranking algorithm pressure"""
    
    async def inject_trend_shock(self, trend_data: TrendData) -> None:
        """Inject trend shock"""
    
    async def simulate_user_sessions(self) -> SessionData:
        """Simulate user sessions"""
    
    async def update_environment_state(self) -> EnvironmentState:
        """Update global environment state"""
```

**Key Features:**
- Ranking pressure simulation
- Trend shock injection
- User session modeling
- Environment state management

---

### 4. Task Scheduler (`scheduling/task_scheduler.py`)

Intelligent task allocation across agents.

```python
class TaskScheduler:
    """Task scheduler - intelligent agent task allocation"""
    
    async def schedule_content_creation(self) -> List[ContentTask]:
        """Schedule content creation tasks"""
    
    async def schedule_interactions(self) -> List[InteractionTask]:
        """Schedule interaction tasks"""
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Task priority sorting"""
```

**Key Features:**
- Priority-based scheduling
- Load-aware allocation
- Deadline management
- Task dependency resolution

---

### 5. Resource Manager (`scheduling/resource_manager.py`)

Manages computational resources and API limits.

```python
class ResourceManager:
    """Resource manager - manages compute resources and API limits"""
    
    def allocate_resources(self, agent_id: str, task_type: TaskType) -> ResourceAllocation:
        """Allocate resources to agent"""
    
    def monitor_resource_usage(self) -> ResourceUsageReport:
        """Monitor resource usage"""
    
    async def enforce_api_limits(self, platform: str) -> None:
        """Enforce platform API limits"""
```

**Key Features:**
- Dynamic resource allocation
- API quota management
- Memory optimization
- Resource usage monitoring

---

### 6. Virality Tracker (`metrics/virality_tracker.py`)

Tracks viral content propagation.

```python
class ViralityTracker:
    """Virality tracker - tracks viral content propagation"""
    
    def track_content_spread(self, content_id: str) -> ViralityMetrics:
        """Track content spread"""
    
    def analyze_viral_patterns(self) -> ViralPatternAnalysis:
        """Analyze viral propagation patterns"""
    
    def predict_virality_potential(self, content: Content) -> float:
        """Predict viral potential"""
```

**Key Features:**
- Real-time viral tracking
- Propagation pattern analysis
- Virality prediction
- Cascade visualization

---

### 7. Performance Monitor (`metrics/performance_monitor.py`)

Monitors system and agent performance.

```python
class PerformanceMonitor:
    """Performance monitor - monitors system performance"""
    
    def monitor_agent_performance(self) -> Dict[str, AgentPerformance]:
        """Monitor agent performance"""
    
    def track_system_metrics(self) -> SystemMetrics:
        """Track system metrics"""
    
    def generate_performance_report(self) -> PerformanceReport:
        """Generate performance report"""
```

**Key Features:**
- Agent performance tracking
- System health monitoring
- Response time analysis
- Throughput measurement

---

### 8. A/B Testing Framework (`experiments/ab_testing.py`)

Hot-swappable strategy testing.

```python
class ABTestFramework:
    """A/B testing framework - hot-swappable strategy testing"""
    
    def create_experiment(self, config: ExperimentConfig) -> Experiment:
        """Create new experiment"""
    
    def assign_agents_to_groups(self, experiment_id: str) -> Dict[str, str]:
        """Assign agents to experiment groups"""
    
    def analyze_experiment_results(self, experiment_id: str) -> ExperimentResults:
        """Analyze experiment results"""
```

**Key Features:**
- Experiment design
- Agent group allocation
- Statistical analysis
- Result visualization

---

### 9. Evolution Tracker (`experiments/evolution_tracker.py`)

Tracks strategy evolution across agents.

```python
class EvolutionTracker:
    """Evolution tracker - tracks strategy evolution"""
    
    def track_strategy_evolution(self, agent_id: str) -> EvolutionHistory:
        """Track strategy evolution"""
    
    def identify_successful_mutations(self) -> List[SuccessfulMutation]:
        """Identify successful mutations"""
    
    def recommend_evolution_directions(self, agent_id: str) -> List[EvolutionDirection]:
        """Recommend evolution directions"""
```

**Key Features:**
- Strategy mutation tracking
- Success pattern identification
- Evolution recommendations
- Fitness calculation

---

## 🔄 Simulation Flow

### Main Simulation Loop

```python
async def main_simulation_loop():
    """Core simulation loop - executed every time step"""
    
    # 1. Arena initiates new simulation round
    arena.check_global_state()
    arena.allocate_tasks_to_agents()
    arena.set_environment_parameters()
    
    # 2. Scrapper updates real-time data
    new_content = await scrapper.collect_latest_data()
    detected_trends = await scrapper.detect_emerging_trends()
    await feed_manager.update_database(new_content)
    
    # 3. Feed processes and analyzes data
    viral_potential = await feed.calculate_viral_potential(new_content)
    trend_state = await feed.update_trend_decay()
    recommendation_data = await feed.prepare_recommendation_data()
    
    # 4. Recommendation generates personalized feeds
    for agent in arena.get_active_agents():
        recommendations = await recommender.generate_recommendations(
            agent_id=agent.id,
            context=arena.get_agent_context(agent.id)
        )
        agent.receive_recommendations(recommendations)
    
    # 5. Agents execute behavioral decisions
    agent_actions = await arena.orchestrate_agent_actions()
    # - Creators: create content / engagement strategy
    # - Audience: consume content / generate feedback
    # - Brands: placement decisions / effect evaluation
    # - Moderators: rule enforcement / parameter tuning
    
    # 6. Arena collects feedback and updates
    await arena.analyze_agent_performance()
    await arena.update_environment_state()
    await arena.update_ranking_pressure()
    await arena.trigger_next_round()
    
    # 7. Dashboard real-time display
    metrics = arena.collect_current_metrics()
    await dashboard.update_visualizations(metrics)
    await dashboard.display_viral_propagation(viral_metrics)
```

### Step-by-Step Breakdown

1. **Environment Initialization** (Once per simulation)
   - Load configurations
   - Initialize all subsystems
   - Deploy initial agents
   - Set up monitoring

2. **Time Step Execution** (Repeated)
   - Update external data
   - Process content
   - Generate recommendations
   - Execute agent actions
   - Collect metrics

3. **Periodic Evaluation** (Every N steps)
   - Evaluate agent performance
   - Trigger evolution
   - Run A/B test analysis
   - Generate reports

4. **Simulation Termination**
   - Aggregate final results
   - Generate comprehensive report
   - Archive logs
   - Cleanup resources

---

## 🔌 Integration Interfaces

### With Feed System

```python
# Get feed data from Feed system
async def get_feed_data(self, filters: FeedFilters) -> List[Feed]:
    return await self.feed_manager.get_feeds(filters)

# Publish agent-generated content to Feed system
async def publish_agent_content(self, agent_id: str, content: Content) -> str:
    return await self.feed_manager.create_feed(content)

# Get viral metrics
async def get_viral_metrics(self, content_ids: List[str]) -> Dict[str, ViralityMetrics]:
    return await self.feed_manager.get_virality_metrics(content_ids)
```

### With Recommendation System

```python
# Get recommendations for agent
async def get_recommendations(self, user_id: str, context: Context) -> List[Recommendation]:
    return await self.recommender.recommend(user_id, context)

# Provide interaction feedback
async def provide_interaction_feedback(self, interaction_data: InteractionData) -> None:
    await self.recommender.update_from_interaction(interaction_data)
```

### With Agent System

```python
# Create new agent
async def create_agent(self, agent_config: AgentConfig) -> Agent:
    return await self.agent_factory.create_agent(agent_config)

# Update agent strategy
async def update_agent_strategy(self, agent_id: str, new_strategy: Strategy) -> None:
    await self.agents[agent_id].update_strategy(new_strategy)

# Get agent state
async def get_agent_state(self, agent_id: str) -> AgentState:
    return self.agents[agent_id].get_current_state()
```

### With Scrapper System

```python
# Request data collection
async def request_scraping(self, platform: str, criteria: ScrapingCriteria) -> ScrapingTask:
    return await self.scraper.schedule_scraping_task(platform, criteria)

# Get trend data
async def get_trend_data(self) -> TrendData:
    return await self.scraper.get_current_trends()
```

---

## ⚙️ Configuration Management

### Arena Configuration

```python
from arena.config import ArenaConfig

config = ArenaConfig(
    # Agent configuration
    num_agents=100,
    agent_distribution={
        "creator": 30,
        "audience": 50,
        "brand": 15,
        "moderator": 5
    },
    
    # Simulation parameters
    simulation_duration=72,  # hours
    time_step_duration=60,   # seconds
    
    # Resource limits
    max_memory_per_agent=512,  # MB
    max_cpu_per_agent=0.5,     # cores
    api_rate_limits={
        "twitter": 100,  # requests per minute
        "feed_system": 1000
    },
    
    # Experiment settings
    enable_ab_testing=True,
    experiment_duration=24,  # hours
    
    # Monitoring
    metrics_collection_interval=10,  # seconds
    dashboard_update_interval=5,
    
    # Trace logging
    trace_log_level="INFO",
    trace_storage_days=30
)
```

---

## 📝 Trace Logging System

**CRITICAL**: Arena uses file-based trace logging. **NO console logs**.

### Log Structure

```
trace/
├── arena/
│   ├── manager/              # Arena manager logs
│   ├── orchestrator/         # Agent orchestration logs
│   ├── simulation/           # Simulation engine logs
│   └── scheduler/            # Task scheduling logs
├── agents/
│   ├── creators/             # Creator agent logs
│   ├── audience/             # Audience agent logs
│   ├── brands/               # Brand agent logs
│   └── moderators/           # Moderator agent logs
├── experiments/
│   ├── ab_tests/             # A/B test logs
│   └── evolution/            # Evolution tracking logs
├── metrics/
│   ├── virality/             # Viral tracking logs
│   └── performance/          # Performance logs
├── errors/                   # All errors
└── archived/                 # Rotated logs
```

### Usage Example

```python
from arena.trace_logging import get_logger

logger = get_logger(__name__, component="arena_manager")

# Log simulation start
logger.info("Starting simulation", extra={
    "num_agents": 100,
    "duration": 72,
    "config": config.to_dict()
})

# Log agent action
logger.debug("Agent action executed", extra={
    "agent_id": "creator_001",
    "action_type": "content_creation",
    "result": "success"
})

# Log error with context
logger.error("Agent deployment failed", extra={
    "agent_id": "creator_002",
    "error_type": "ResourceAllocationError",
    "available_memory": 256
})
```

### Debugging Workflow

1. **Identify Component** - Which module had the issue?
2. **Check Error Logs** - `trace/errors/errors_YYYYMMDD.log`
3. **Trace Request Flow** - `python utils/trace_request.py <request_id>`
4. **Analyze Metrics** - `python utils/log_analyzer.py --component arena`
5. **Fix and Verify** - Check new trace logs

---

## 🛠️ Development Guide

### Development Priority

#### Phase 1: Core Infrastructure 🚧
1. Implement `ArenaManager` base framework
2. Complete `TaskScheduler` and `ResourceManager`
3. Establish basic agent lifecycle management

#### Phase 2: Simulation Engine
1. Implement `SimulationEngine` core functionality
2. Complete metrics tracking system
3. Establish A/B testing framework

#### Phase 3: Integration & Optimization
1. Implement evolution mechanisms
2. Complete real-time dashboard
3. System integration testing

### Quick Start Example

```python
import asyncio
from arena import ArenaManager
from arena.config import ArenaConfig

async def simple_simulation():
    # 1. Create configuration
    config = ArenaConfig(
        num_agents=10,
        simulation_duration=1  # 1 hour for testing
    )
    
    # 2. Initialize Arena
    arena = ArenaManager(config)
    await arena.initialize_arena()
    
    # 3. Deploy agents
    for i in range(config.num_agents):
        agent_config = arena.create_default_agent_config(agent_id=f"agent_{i}")
        await arena.deploy_agent(agent_config)
    
    # 4. Run simulation
    for time_step in range(60):  # 60 steps = 1 hour
        result = await arena.run_simulation_step()
        print(f"Step {time_step}: {result.summary}")
    
    # 5. Get results
    final_report = await arena.generate_simulation_report()
    return final_report

# Run
results = asyncio.run(simple_simulation())
```

### Testing

```bash
# Run unit tests
pytest tests/test_core.py

# Run integration tests
pytest tests/test_integration.py

# Run performance tests
pytest tests/test_performance.py

# Test with specific configuration
pytest tests/ --config configs/test_config.yaml
```

---

## 📊 Performance Requirements

### System Requirements

- **Scalability**: Support 1000 concurrent agents
- **Response Time**: API response < 100ms
- **Availability**: System uptime > 99.9%
- **Memory**: < 8GB total system memory
- **Throughput**: 10,000+ operations/second

### Agent Management

- **Deployment Time**: < 1 second per agent
- **Action Latency**: < 50ms per agent action
- **State Sync**: < 10ms for state updates
- **Resource Efficiency**: < 512MB per agent

### Monitoring

- **Metrics Collection**: Every 10 seconds
- **Dashboard Update**: Every 5 seconds
- **Log Rotation**: Daily
- **Anomaly Detection**: < 5 second delay

---

## 🧪 Experiment Examples

### A/B Test Example

```python
from arena.experiments import ABTestFramework, ExperimentConfig

# Create experiment
experiment_config = ExperimentConfig(
    name="content_strategy_test",
    hypothesis="Emotional triggers increase engagement",
    duration=timedelta(days=3),
    control_strategy="baseline",
    treatment_strategy="emotional_triggers"
)

experiment = ABTestFramework.create_experiment(experiment_config)

# Assign agents to groups
await experiment.assign_agents(
    control_group=["creator_001", "creator_002"],
    treatment_group=["creator_003", "creator_004"]
)

# Run experiment
results = await experiment.run()

# Analyze results
analysis = experiment.analyze_results(results)
print(f"Statistical significance: {analysis.p_value}")
print(f"Effect size: {analysis.effect_size}")
```

---

## 📚 API Reference

### ArenaManager API

```python
# Initialization
async def initialize_arena() -> None
async def shutdown_arena() -> None

# Agent Management
async def deploy_agent(config: AgentConfig) -> str
async def remove_agent(agent_id: str) -> None
async def get_agent_state(agent_id: str) -> AgentState

# Simulation Control
async def run_simulation_step() -> SimulationResult
async def pause_simulation() -> None
async def resume_simulation() -> None

# Metrics & Monitoring
async def get_current_metrics() -> SystemMetrics
async def get_viral_content() -> List[ViralContent]
async def generate_simulation_report() -> SimulationReport

# Experiment Control
async def create_experiment(config: ExperimentConfig) -> Experiment
async def get_experiment_results(experiment_id: str) -> ExperimentResults
```

---

## 🤝 Contributing

When contributing to Arena:

1. **Use Trace Logging** - Never use `print()` or console logs
2. **Write Tests** - Maintain > 90% code coverage
3. **Document APIs** - Clear docstrings for all public methods
4. **Performance Aware** - Profile critical paths
5. **Integration Focus** - Ensure compatibility with all modules

---

## 📖 Related Documentation

- [Feed Module](../Feed/README.md)
- [Agent Module](../Agent/README.md)
- [Recommendation Module](../Recommendation/README.md)
- [Scrapper Module](../Scrapper/README.md)
- [Project Status Report](../PROJECT_STATUS_REPORT.md)

---

**Arena - The Heart of Social-Arena** ❤️🏟️

*Orchestrating 1000+ agents in realistic social media simulation*
