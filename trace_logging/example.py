"""
Example Usage of Arena Trace Logging System

This script demonstrates how to use the trace logging system.
"""

import asyncio
import random
import time
from datetime import datetime

from trace_logging import (
    get_logger,
    configure_logging,
    LogConfig,
    trace_context,
    AgentTraceManager,
    SimulationTraceManager,
    PerformanceTraceManager,
    ExperimentTraceManager,
)


def example_basic_logging():
    """Example 1: Basic logging"""
    print("\n=== Example 1: Basic Logging ===\n")

    logger = get_logger("example_basic", category="system")

    logger.info("system_startup", data={"version": "1.0.0"})
    logger.debug("config_loaded", data={"config_file": "config.yaml"})
    logger.warning("deprecated_feature", data={"feature": "old_api"})

    try:
        # Simulate an error
        result = 1 / 0
    except ZeroDivisionError:
        logger.exception("calculation_error", data={"operation": "division"})

    print("Logs written to: trace/system/example_basic.jsonl")


def example_trace_context():
    """Example 2: Using trace context"""
    print("\n=== Example 2: Trace Context ===\n")

    logger = get_logger("example_context", category="agents")

    # Simulate agent workflow
    agent_id = "agent_001"
    session_id = "session_123"

    with trace_context(agent_id=agent_id, session_id=session_id):
        logger.info("agent_session_start", data={"agent_type": "content_creator"})

        # Nested operation with additional context
        with trace_context(task_id="task_456"):
            logger.info("task_start", data={"task_type": "create_post"})

            time.sleep(0.1)  # Simulate work

            logger.info("task_complete", data={
                "task_type": "create_post",
                "result": "success"
            })

        logger.info("agent_session_end", data={"duration": 0.1})

    print("Logs written to: trace/agents/example_context.jsonl")


def example_agent_tracing():
    """Example 3: Agent-specific tracing"""
    print("\n=== Example 3: Agent Tracing ===\n")

    agent_id = "agent_002"
    agent_trace = AgentTraceManager(agent_id=agent_id)

    # Log agent creation
    with agent_trace.trace_operation("agent_initialization", agent_id=agent_id):
        time.sleep(0.05)  # Simulate initialization

    # Log agent action
    agent_trace.trace_action(
        action_type="create_content",
        action_data={
            "content_type": "post",
            "topic": "AI in 2025",
            "platform": "twitter"
        },
        result={
            "content_id": "post_789",
            "engagement_predicted": 0.75
        }
    )

    # Log learning event
    agent_trace.trace_learning(
        learning_event="engagement_feedback",
        before_metrics={"engagement_rate": 0.05, "virality_score": 0.3},
        after_metrics={"engagement_rate": 0.08, "virality_score": 0.45}
    )

    # Log strategy update
    agent_trace.trace_strategy_update(
        old_strategy="conservative",
        new_strategy="aggressive",
        reason="improved_performance_metrics"
    )

    print(f"Logs written to: trace/agents/agent_{agent_id}.jsonl")


def example_simulation_tracing():
    """Example 4: Simulation tracing"""
    print("\n=== Example 4: Simulation Tracing ===\n")

    sim_trace = SimulationTraceManager()

    # Simulate 3 simulation steps
    for step in range(1, 4):
        with sim_trace.trace_operation("simulation_step", step_number=step):
            # Log step data
            sim_trace.trace_step(
                step_number=step,
                step_data={
                    "active_agents": random.randint(80, 120),
                    "content_created": random.randint(50, 150),
                    "interactions": random.randint(200, 500)
                }
            )

            # Simulate work
            time.sleep(0.05)

            # Occasionally inject trend
            if step == 2:
                sim_trace.trace_trend_injection(
                    trend_id="trend_001",
                    trend_type="viral_topic",
                    impact_score=0.85
                )

    print("Logs written to: trace/simulation/simulation_engine.jsonl")


def example_performance_tracing():
    """Example 5: Performance tracing"""
    print("\n=== Example 5: Performance Tracing ===\n")

    perf_trace = PerformanceTraceManager()

    # Track various operations
    operations = ["create_agent", "process_feed", "calculate_ranking"]

    for op in operations:
        # Simulate operation
        start_time = time.time()
        time.sleep(random.uniform(0.01, 0.1))
        latency_ms = (time.time() - start_time) * 1000

        # Log latency
        perf_trace.trace_latency(
            operation=op,
            latency_ms=latency_ms,
            tags={"environment": "development"}
        )

    # Log throughput
    perf_trace.trace_throughput(
        operation="process_content",
        count=1000,
        duration_seconds=5.0
    )

    # Log resource usage
    perf_trace.trace_resource_usage(
        resource_type="memory",
        usage_value=4096,  # MB
        capacity=8192      # MB
    )

    print("Logs written to: trace/performance/performance_monitor.jsonl")


def example_experiment_tracing():
    """Example 6: Experiment tracing"""
    print("\n=== Example 6: Experiment Tracing ===\n")

    experiment_id = "exp_001"
    exp_trace = ExperimentTraceManager(experiment_id=experiment_id)

    # Start experiment
    exp_trace.trace_experiment_start(
        experiment_config={
            "name": "Content Strategy A/B Test",
            "variants": ["conservative", "aggressive"],
            "duration_days": 7,
            "metric": "engagement_rate"
        }
    )

    # Log results for variant A
    exp_trace.trace_experiment_result(
        variant="conservative",
        metrics={
            "engagement_rate": 0.05,
            "virality_score": 0.3,
            "retention_rate": 0.8
        }
    )

    # Log results for variant B
    exp_trace.trace_experiment_result(
        variant="aggressive",
        metrics={
            "engagement_rate": 0.08,
            "virality_score": 0.45,
            "retention_rate": 0.7
        }
    )

    print(f"Logs written to: trace/experiments/experiment_{experiment_id}.jsonl")


def example_error_tracking():
    """Example 7: Error tracking and debugging"""
    print("\n=== Example 7: Error Tracking ===\n")

    logger = get_logger("example_errors", category="errors")

    # Simulate various error scenarios
    errors = [
        ("api_timeout", {"endpoint": "/api/agents", "timeout_ms": 5000}),
        ("database_connection", {"host": "db.example.com", "port": 5432}),
        ("validation_error", {"field": "agent_id", "value": "invalid"}),
    ]

    for error_type, context in errors:
        try:
            # Simulate error
            raise Exception(f"Simulated {error_type}")
        except Exception:
            logger.exception(error_type, data=context)

    print("Logs written to: trace/errors/example_errors.jsonl")


async def example_async_operations():
    """Example 8: Async operations with tracing"""
    print("\n=== Example 8: Async Operations ===\n")

    logger = get_logger("example_async", category="system")

    async def async_task(task_id: str):
        """Simulate async task"""
        with trace_context(task_id=task_id):
            logger.info("async_task_start", data={"task_id": task_id})

            # Simulate async work
            await asyncio.sleep(random.uniform(0.01, 0.05))

            logger.info("async_task_complete", data={"task_id": task_id})

    # Run multiple async tasks
    tasks = [async_task(f"task_{i}") for i in range(5)]
    await asyncio.gather(*tasks)

    print("Logs written to: trace/system/example_async.jsonl")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Arena Trace Logging System - Examples")
    print("="*60)

    # Configure logging
    configure_logging(LogConfig())

    # Run synchronous examples
    example_basic_logging()
    example_trace_context()
    example_agent_tracing()
    example_simulation_tracing()
    example_performance_tracing()
    example_experiment_tracing()
    example_error_tracking()

    # Run async example
    asyncio.run(example_async_operations())

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
    print("\nTo analyze logs, try:")
    print("  python -m trace_logging.cli summary")
    print("  python -m trace_logging.cli errors --hours 1")
    print("  python -m trace_logging.cli tail --category agents --lines 10")
    print()


if __name__ == "__main__":
    main()
