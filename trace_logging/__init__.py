"""
Arena Trace Logging System

Centralized logging infrastructure for comprehensive system debugging.
"""

from .logger import get_logger, TraceLogger
from .config import LogConfig, configure_logging, LogLevel
from .context import TraceContext, get_trace_context, trace_context
from .manager import (
    TraceManager,
    AgentTraceManager,
    SimulationTraceManager,
    PerformanceTraceManager,
    ExperimentTraceManager,
)

__all__ = [
    'get_logger',
    'TraceLogger',
    'LogConfig',
    'LogLevel',
    'configure_logging',
    'TraceContext',
    'get_trace_context',
    'trace_context',
    'TraceManager',
    'AgentTraceManager',
    'SimulationTraceManager',
    'PerformanceTraceManager',
    'ExperimentTraceManager',
]
