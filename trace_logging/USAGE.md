# Arena Trace Logging - Usage Guide

## Overview

The Arena trace logging system provides comprehensive runtime logging for debugging and monitoring. All logs are stored in structured JSON format for easy analysis.

## Quick Start

### 1. Basic Usage

```python
from trace_logging import get_logger

# Get a logger for your component
logger = get_logger("my_component", category="system")

# Log events
logger.info("user_action", data={"user_id": "123", "action": "click"})
logger.error("api_error", data={"endpoint": "/api/agents", "status": 500})
```

### 2. Using Trace Context

```python
from trace_logging import get_logger, trace_context

logger = get_logger("agent_manager", category="agents")

# Create a context for tracking operations
with trace_context(agent_id="agent_123", session_id="session_456"):
    logger.info("agent_created", data={"type": "content_creator"})

    # Child operations inherit the context
    with trace_context(task_id="task_789"):
        logger.info("task_assigned", data={"task_type": "create_post"})
```

### 3. Using Trace Managers

```python
from trace_logging import TraceManager, AgentTraceManager

# Generic trace manager
trace_mgr = TraceManager("simulation_engine", category="simulation")

# Track an operation
with trace_mgr.trace_operation("simulate_step", step_number=42):
    # Do simulation work
    result = run_simulation()

    # Log metrics
    trace_mgr.trace_metric("active_agents", value=100, unit="count")

# Agent-specific trace manager
agent_trace = AgentTraceManager(agent_id="agent_123")

# Log agent actions
agent_trace.trace_action(
    action_type="create_content",
    action_data={"content_type": "post", "topic": "AI"},
    result={"content_id": "post_456", "success": True}
)

# Log learning events
agent_trace.trace_learning(
    learning_event="strategy_update",
    before_metrics={"engagement_rate": 0.05},
    after_metrics={"engagement_rate": 0.08}
)
```

## Log Categories

Logs are organized into categories:

- **agents**: Agent-specific logs (actions, learning, strategy changes)
- **simulation**: Simulation engine logs (steps, trends, state changes)
- **performance**: Performance metrics and monitoring
- **errors**: Error traces and exceptions
- **experiments**: A/B testing and experiment logs
- **integration**: Integration with external systems
- **system**: System-level logs (startup, shutdown, config)

## Analyzing Logs

### Command Line Tool

```bash
# Show recent errors
python -m trace_logging.cli errors --hours 24

# Trace a specific request
python -m trace_logging.cli trace <trace-id>

# Analyze operation performance
python -m trace_logging.cli performance create_agent --hours 1

# Find slow operations
python -m trace_logging.cli slow --threshold 1.0 --hours 1

# Analyze agent behavior
python -m trace_logging.cli agent agent_123 --hours 24

# Show summary report
python -m trace_logging.cli summary --hours 24

# Tail logs
python -m trace_logging.cli tail --category agents --lines 20
```

### Programmatic Analysis

```python
from trace_logging.analysis import LogAnalyzer

analyzer = LogAnalyzer()

# Analyze errors
error_analysis = analyzer.analyze_errors(hours=24)
print(f"Total errors: {error_analysis['total_errors']}")

# Analyze performance
perf_stats = analyzer.analyze_performance("create_agent", hours=1)
print(f"Average duration: {perf_stats['avg_seconds']}s")

# Trace a request
logs = analyzer.trace_request(trace_id="abc-123")
for log in logs:
    print(f"{log['timestamp']}: {log['event']}")

# Find slow operations
slow_ops = analyzer.find_slow_operations(threshold_seconds=1.0, hours=1)
for op in slow_ops:
    print(f"{op['operation']}: {op['duration_seconds']}s")

# Analyze agent behavior
agent_analysis = analyzer.analyze_agent_behavior("agent_123", hours=24)
print(f"Actions: {agent_analysis['actions']}")
```

## Best Practices

### 1. Use Meaningful Event Names

```python
# Good
logger.info("agent_created", data={"agent_id": "123", "type": "creator"})
logger.info("content_published", data={"content_id": "456", "platform": "twitter"})

# Bad
logger.info("event", data={"msg": "agent created"})
logger.info("log", data={"info": "something happened"})
```

### 2. Include Relevant Context

```python
# Always include entity IDs in context
with trace_context(agent_id=agent_id, experiment_id=experiment_id):
    logger.info("experiment_started", data={"variant": "A"})
```

### 3. Log State Changes

```python
trace_mgr.trace_state_change(
    entity_type="agent",
    entity_id=agent_id,
    old_state="idle",
    new_state="active",
    reason="new_task_assigned"
)
```

### 4. Track Operation Duration

```python
# Automatically tracks start, completion, and duration
with trace_mgr.trace_operation("process_feed", feed_id=feed_id):
    process_feed(feed_id)
```

### 5. Log Errors with Context

```python
try:
    result = risky_operation()
except Exception as e:
    logger.exception(
        "operation_failed",
        data={
            "operation": "risky_operation",
            "input": input_data,
            "error_type": type(e).__name__
        }
    )
    raise
```

### 6. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic info (verbose, frequent)
- **INFO**: Normal operation events (agent actions, state changes)
- **WARNING**: Potential issues (retries, degraded performance)
- **ERROR**: Errors that need attention (failed operations)
- **CRITICAL**: Critical failures (system crashes, data corruption)

## Examples

### Example 1: Arena Manager Initialization

```python
from trace_logging import get_logger, trace_context

logger = get_logger("arena_manager", category="system")

with trace_context(session_id=session_id):
    logger.info("arena_init_start", data={"config": config})

    try:
        # Initialize components
        logger.info("loading_agents", data={"count": len(agents)})

        for agent in agents:
            with trace_context(agent_id=agent.id):
                logger.info("agent_loaded", data={"type": agent.type})

        logger.info("arena_init_complete", data={"total_agents": len(agents)})

    except Exception as e:
        logger.exception("arena_init_failed", data={"error": str(e)})
        raise
```

### Example 2: Simulation Step with Metrics

```python
from trace_logging import SimulationTraceManager

sim_trace = SimulationTraceManager()

with sim_trace.trace_operation("simulation_step", step_number=42):
    # Log step start
    sim_trace.trace_step(
        step_number=42,
        step_data={
            "active_agents": 100,
            "pending_tasks": 50,
            "completed_tasks": 200
        }
    )

    # Execute simulation
    result = execute_simulation_step()

    # Log metrics
    sim_trace.trace_metric("throughput", value=result.throughput, unit="tasks/sec")
    sim_trace.trace_metric("active_agents", value=result.active_agents, unit="count")

    # Log trend injection
    if result.trend_injected:
        sim_trace.trace_trend_injection(
            trend_id=result.trend_id,
            trend_type=result.trend_type,
            impact_score=result.impact_score
        )
```

### Example 3: Debugging with Trace ID

When you encounter an issue:

1. Get the trace_id from the error log
2. Use the CLI to trace the full request:

```bash
python -m trace_logging.cli trace abc-123-def-456
```

This will show all log entries for that trace_id across all components, allowing you to see the full flow of the request.

## Configuration

### Custom Log Configuration

```python
from trace_logging import configure_logging, LogConfig, LogLevel
from pathlib import Path

config = LogConfig(
    trace_dir=Path("custom_trace"),
    log_level=LogLevel.DEBUG,
    max_bytes=200 * 1024 * 1024,  # 200MB
    backup_count=60,  # 60 days
    async_logging=True,
    buffer_size=2000
)

configure_logging(config)
```

### Component-Specific Log Levels

```python
config = LogConfig(
    components={
        'agents': LogLevel.INFO,
        'simulation': LogLevel.DEBUG,
        'performance': LogLevel.DEBUG,
        'errors': LogLevel.ERROR,
    }
)

configure_logging(config)
```

## Integration with Existing Code

### Before: Using print statements

```python
def create_agent(agent_id, agent_type):
    print(f"Creating agent {agent_id} of type {agent_type}")
    agent = Agent(agent_id, agent_type)
    print(f"Agent {agent_id} created successfully")
    return agent
```

### After: Using trace logging

```python
from trace_logging import get_logger, trace_context

logger = get_logger("agent_factory", category="agents")

def create_agent(agent_id, agent_type):
    with trace_context(agent_id=agent_id):
        logger.info("agent_creation_start", data={"agent_type": agent_type})

        try:
            agent = Agent(agent_id, agent_type)
            logger.info("agent_creation_complete", data={"agent_type": agent_type})
            return agent

        except Exception as e:
            logger.exception("agent_creation_failed", data={
                "agent_type": agent_type,
                "error": str(e)
            })
            raise
```

## Troubleshooting

### No logs being written

1. Check that trace directory exists and is writable
2. Verify log level is appropriate (DEBUG logs won't show with INFO level)
3. Check disk space

### Logs growing too large

1. Adjust `max_bytes` in LogConfig
2. Reduce `backup_count` to keep fewer days
3. Lower log level to reduce verbosity

### Can't find specific logs

1. Use trace_id to follow request flow
2. Check correct category folder
3. Use CLI tool for filtering: `python -m trace_logging.cli tail --category agents`

## Performance Considerations

- **Async logging** is enabled by default to minimize impact on main thread
- Logs are buffered (default 1000 entries) before writing
- Use DEBUG level sparingly in production
- JSON serialization is fast but adds some overhead
- Log rotation happens automatically, no cleanup needed
