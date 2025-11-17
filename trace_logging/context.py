"""
Trace Context Management

Provides context tracking across async operations for distributed tracing.
"""

import uuid
import contextvars
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


# Context variable for trace context
_trace_context_var: contextvars.ContextVar = contextvars.ContextVar(
    'trace_context',
    default=None
)


@dataclass
class TraceContext:
    """
    Context for tracking operations across the system.
    Automatically propagated across async operations.
    """

    # Unique trace ID for this operation chain
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Parent trace ID if this is a child operation
    parent_trace_id: Optional[str] = None

    # Session ID for grouping related operations
    session_id: Optional[str] = None

    # Agent ID if operation is agent-specific
    agent_id: Optional[str] = None

    # Experiment ID if part of an experiment
    experiment_id: Optional[str] = None

    # User ID if applicable
    user_id: Optional[str] = None

    # Simulation step if applicable
    simulation_step: Optional[int] = None

    # Additional context data
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Timestamp when context was created
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            'trace_id': self.trace_id,
            'parent_trace_id': self.parent_trace_id,
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'experiment_id': self.experiment_id,
            'user_id': self.user_id,
            'simulation_step': self.simulation_step,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
        }

    def create_child(self, **kwargs) -> 'TraceContext':
        """Create a child context inheriting from this context"""
        child_data = {
            'parent_trace_id': self.trace_id,
            'session_id': self.session_id or kwargs.get('session_id'),
            'agent_id': self.agent_id or kwargs.get('agent_id'),
            'experiment_id': self.experiment_id or kwargs.get('experiment_id'),
            'user_id': self.user_id or kwargs.get('user_id'),
            'simulation_step': self.simulation_step or kwargs.get('simulation_step'),
            'metadata': {**self.metadata, **kwargs.get('metadata', {})},
        }

        # Override with any explicitly provided kwargs
        for key in ['session_id', 'agent_id', 'experiment_id', 'user_id', 'simulation_step']:
            if key in kwargs:
                child_data[key] = kwargs[key]

        return TraceContext(**child_data)


def get_trace_context() -> TraceContext:
    """
    Get current trace context or create a new one.

    Returns:
        Current TraceContext from context variable
    """
    context = _trace_context_var.get()
    if context is None:
        context = TraceContext()
        _trace_context_var.set(context)
    return context


def set_trace_context(context: TraceContext) -> None:
    """Set the current trace context"""
    _trace_context_var.set(context)


def clear_trace_context() -> None:
    """Clear the current trace context"""
    _trace_context_var.set(None)


class trace_context:
    """
    Context manager for setting trace context.

    Usage:
        with trace_context(agent_id="agent_123"):
            # Operations here will have agent_id in context
            logger.info("action", data={})
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.previous_context = None
        self.new_context = None

    def __enter__(self):
        self.previous_context = _trace_context_var.get()

        if self.previous_context:
            self.new_context = self.previous_context.create_child(**self.kwargs)
        else:
            self.new_context = TraceContext(**self.kwargs)

        _trace_context_var.set(self.new_context)
        return self.new_context

    def __exit__(self, exc_type, exc_val, exc_tb):
        _trace_context_var.set(self.previous_context)
