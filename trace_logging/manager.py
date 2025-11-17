"""
Trace Manager

High-level interface for component-specific tracing.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from contextlib import contextmanager

from .logger import get_logger, TraceLogger
from .context import get_trace_context, set_trace_context, TraceContext


class TraceManager:
    """
    High-level trace manager for specific components.

    Provides convenient methods for tracing common operations.
    """

    def __init__(self, component: str, category: str):
        """
        Initialize trace manager.

        Args:
            component: Component name
            category: Log category
        """
        self.component = component
        self.category = category
        self.logger = get_logger(component, category)

    @contextmanager
    def trace_operation(
        self,
        operation: str,
        **context_kwargs
    ):
        """
        Context manager for tracing an operation.

        Usage:
            with trace_manager.trace_operation("create_agent", agent_id="agent_123"):
                # Do work
                pass

        Args:
            operation: Operation name
            **context_kwargs: Additional context fields
        """
        # Create child context for this operation
        parent_ctx = get_trace_context()
        operation_ctx = parent_ctx.create_child(**context_kwargs)
        set_trace_context(operation_ctx)

        start_time = datetime.utcnow()

        self.logger.info(
            f"{operation}.start",
            data={'operation': operation, **context_kwargs}
        )

        try:
            yield operation_ctx
            duration = (datetime.utcnow() - start_time).total_seconds()

            self.logger.info(
                f"{operation}.complete",
                data={
                    'operation': operation,
                    'duration_seconds': duration,
                    **context_kwargs
                }
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()

            self.logger.exception(
                f"{operation}.error",
                data={
                    'operation': operation,
                    'duration_seconds': duration,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    **context_kwargs
                }
            )
            raise

        finally:
            # Restore parent context
            set_trace_context(parent_ctx)

    def trace_event(
        self,
        event: str,
        data: Optional[Dict[str, Any]] = None,
        level: str = "info"
    ):
        """
        Trace a discrete event.

        Args:
            event: Event name
            data: Event data
            level: Log level (debug, info, warning, error, critical)
        """
        log_method = getattr(self.logger, level.lower())
        log_method(event, data=data or {})

    def trace_state_change(
        self,
        entity_type: str,
        entity_id: str,
        old_state: Any,
        new_state: Any,
        reason: Optional[str] = None
    ):
        """
        Trace a state change.

        Args:
            entity_type: Type of entity (e.g., "agent", "simulation")
            entity_id: Entity identifier
            old_state: Previous state
            new_state: New state
            reason: Reason for state change
        """
        self.logger.info(
            "state_change",
            data={
                'entity_type': entity_type,
                'entity_id': entity_id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason,
            }
        )

    def trace_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Trace a metric value.

        Args:
            metric_name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags for metric
        """
        self.logger.debug(
            "metric",
            data={
                'metric_name': metric_name,
                'value': value,
                'unit': unit,
                'tags': tags or {},
            }
        )

    def trace_interaction(
        self,
        source_id: str,
        target_id: str,
        interaction_type: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Trace an interaction between entities.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            interaction_type: Type of interaction
            data: Additional interaction data
        """
        self.logger.info(
            "interaction",
            data={
                'source_id': source_id,
                'target_id': target_id,
                'interaction_type': interaction_type,
                **(data or {})
            }
        )

    def trace_decision(
        self,
        decision_point: str,
        options: List[str],
        chosen_option: str,
        reasoning: Optional[str] = None,
        confidence: Optional[float] = None
    ):
        """
        Trace a decision made by the system.

        Args:
            decision_point: Where the decision was made
            options: Available options
            chosen_option: Selected option
            reasoning: Why this option was chosen
            confidence: Confidence score (0-1)
        """
        self.logger.info(
            "decision",
            data={
                'decision_point': decision_point,
                'options': options,
                'chosen_option': chosen_option,
                'reasoning': reasoning,
                'confidence': confidence,
            }
        )

    def trace_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ):
        """
        Trace an error.

        Args:
            error_type: Type of error
            error_message: Error message
            context: Error context
            recoverable: Whether error is recoverable
        """
        self.logger.error(
            "error",
            data={
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {},
                'recoverable': recoverable,
            },
            exc_info=True
        )


class AgentTraceManager(TraceManager):
    """Specialized trace manager for agents"""

    def __init__(self, agent_id: str):
        super().__init__(f"agent_{agent_id}", "agents")
        self.agent_id = agent_id

    def trace_action(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None
    ):
        """Trace an agent action"""
        self.logger.info(
            "agent_action",
            data={
                'agent_id': self.agent_id,
                'action_type': action_type,
                'action_data': action_data,
                'result': result,
            }
        )

    def trace_learning(
        self,
        learning_event: str,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float]
    ):
        """Trace agent learning"""
        self.logger.info(
            "agent_learning",
            data={
                'agent_id': self.agent_id,
                'learning_event': learning_event,
                'before_metrics': before_metrics,
                'after_metrics': after_metrics,
                'improvement': {
                    k: after_metrics.get(k, 0) - before_metrics.get(k, 0)
                    for k in set(before_metrics.keys()) | set(after_metrics.keys())
                }
            }
        )

    def trace_strategy_update(
        self,
        old_strategy: str,
        new_strategy: str,
        reason: str
    ):
        """Trace strategy change"""
        self.trace_state_change(
            entity_type="agent_strategy",
            entity_id=self.agent_id,
            old_state=old_strategy,
            new_state=new_strategy,
            reason=reason
        )


class SimulationTraceManager(TraceManager):
    """Specialized trace manager for simulation"""

    def __init__(self):
        super().__init__("simulation_engine", "simulation")

    def trace_step(
        self,
        step_number: int,
        step_data: Dict[str, Any]
    ):
        """Trace simulation step"""
        self.logger.info(
            "simulation_step",
            data={
                'step_number': step_number,
                **step_data
            }
        )

    def trace_trend_injection(
        self,
        trend_id: str,
        trend_type: str,
        impact_score: float
    ):
        """Trace trend injection"""
        self.logger.info(
            "trend_injection",
            data={
                'trend_id': trend_id,
                'trend_type': trend_type,
                'impact_score': impact_score,
            }
        )


class PerformanceTraceManager(TraceManager):
    """Specialized trace manager for performance monitoring"""

    def __init__(self):
        super().__init__("performance_monitor", "performance")

    def trace_latency(
        self,
        operation: str,
        latency_ms: float,
        tags: Optional[Dict[str, str]] = None
    ):
        """Trace operation latency"""
        self.trace_metric(
            metric_name=f"{operation}_latency",
            value=latency_ms,
            unit="ms",
            tags=tags
        )

    def trace_throughput(
        self,
        operation: str,
        count: int,
        duration_seconds: float
    ):
        """Trace operation throughput"""
        throughput = count / duration_seconds if duration_seconds > 0 else 0
        self.trace_metric(
            metric_name=f"{operation}_throughput",
            value=throughput,
            unit="ops/sec"
        )

    def trace_resource_usage(
        self,
        resource_type: str,
        usage_value: float,
        capacity: float
    ):
        """Trace resource usage"""
        utilization = (usage_value / capacity * 100) if capacity > 0 else 0
        self.logger.debug(
            "resource_usage",
            data={
                'resource_type': resource_type,
                'usage_value': usage_value,
                'capacity': capacity,
                'utilization_percent': utilization,
            }
        )


class ExperimentTraceManager(TraceManager):
    """Specialized trace manager for experiments"""

    def __init__(self, experiment_id: str):
        super().__init__(f"experiment_{experiment_id}", "experiments")
        self.experiment_id = experiment_id

    def trace_experiment_start(
        self,
        experiment_config: Dict[str, Any]
    ):
        """Trace experiment start"""
        self.logger.info(
            "experiment_start",
            data={
                'experiment_id': self.experiment_id,
                'config': experiment_config,
            }
        )

    def trace_experiment_result(
        self,
        variant: str,
        metrics: Dict[str, float]
    ):
        """Trace experiment results"""
        self.logger.info(
            "experiment_result",
            data={
                'experiment_id': self.experiment_id,
                'variant': variant,
                'metrics': metrics,
            }
        )
