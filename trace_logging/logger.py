"""
Structured Logger Implementation

Provides JSON-based structured logging with file rotation and async support.
"""

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler
import logging
import traceback
from queue import Queue
from threading import Thread

from .config import get_config, LogLevel
from .context import get_trace_context


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""

        # Get trace context
        try:
            trace_ctx = get_trace_context()
            context_data = trace_ctx.to_dict() if trace_ctx else {}
        except Exception:
            context_data = {}

        # Build structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'component': record.name,
            'event': getattr(record, 'event', 'log'),
            'message': record.getMessage(),
            'data': getattr(record, 'data', {}),
            'context': context_data,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info),
            }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                          'event', 'data']:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


class AsyncLogHandler:
    """Async log handler for non-blocking logging"""

    def __init__(self, handler: logging.Handler, buffer_size: int = 1000):
        self.handler = handler
        self.queue: Queue = Queue(maxsize=buffer_size)
        self.thread: Optional[Thread] = None
        self.running = False

    def start(self):
        """Start async logging thread"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._process_logs, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop async logging thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def emit(self, record: logging.LogRecord):
        """Emit log record to queue"""
        try:
            self.queue.put_nowait(record)
        except Exception:
            # If queue is full, drop the log (or handle differently)
            pass

    def _process_logs(self):
        """Process logs from queue"""
        while self.running:
            try:
                record = self.queue.get(timeout=0.1)
                self.handler.emit(record)
            except Exception:
                continue


class TraceLogger:
    """
    Structured logger for Arena system.

    Provides JSON-based logging with automatic trace context inclusion.
    """

    def __init__(self, component: str, category: str = "system"):
        """
        Initialize logger.

        Args:
            component: Component name (e.g., "arena_manager", "agent_orchestrator")
            category: Log category (e.g., "agents", "simulation", "performance")
        """
        self.component = component
        self.category = category
        self.config = get_config()

        # Create logger
        self.logger = logging.getLogger(f"{category}.{component}")
        self.logger.setLevel(self._get_log_level())
        self.logger.propagate = False

        # Setup file handler with rotation
        self._setup_file_handler()

        # Setup async handler if enabled
        if self.config.async_logging:
            self._setup_async_handler()

    def _get_log_level(self) -> int:
        """Get log level for this component"""
        level = self.config.components.get(
            self.category,
            self.config.log_level
        )

        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }

        return level_map.get(level, logging.INFO)

    def _setup_file_handler(self):
        """Setup rotating file handler"""
        log_dir = self.config.trace_dir / self.category
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{self.component}.jsonl"

        handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.max_bytes,
            backupCount=self.config.backup_count,
        )

        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
        self.file_handler = handler

    def _setup_async_handler(self):
        """Setup async logging handler"""
        self.async_handler = AsyncLogHandler(
            self.file_handler,
            buffer_size=self.config.buffer_size
        )
        self.async_handler.start()

    def _log(
        self,
        level: int,
        event: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Internal log method"""
        extra = {
            'event': event,
            'data': data or {},
            **kwargs
        }

        if not message:
            message = event

        self.logger.log(level, message, extra=extra)

    def debug(
        self,
        event: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log debug message"""
        self._log(logging.DEBUG, event, message, data, **kwargs)

    def info(
        self,
        event: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log info message"""
        self._log(logging.INFO, event, message, data, **kwargs)

    def warning(
        self,
        event: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log warning message"""
        self._log(logging.WARNING, event, message, data, **kwargs)

    def error(
        self,
        event: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
        **kwargs
    ):
        """Log error message"""
        extra = {
            'event': event,
            'data': data or {},
            **kwargs
        }

        if not message:
            message = event

        self.logger.error(message, extra=extra, exc_info=exc_info)

    def critical(
        self,
        event: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
        **kwargs
    ):
        """Log critical message"""
        extra = {
            'event': event,
            'data': data or {},
            **kwargs
        }

        if not message:
            message = event

        self.logger.critical(message, extra=extra, exc_info=exc_info)

    def exception(
        self,
        event: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log exception with traceback"""
        self.error(event, message, data, exc_info=True, **kwargs)


# Logger cache
_loggers: Dict[str, TraceLogger] = {}


def get_logger(component: str, category: str = "system") -> TraceLogger:
    """
    Get or create a logger for a component.

    Args:
        component: Component name
        category: Log category (agents, simulation, performance, etc.)

    Returns:
        TraceLogger instance
    """
    key = f"{category}.{component}"

    if key not in _loggers:
        _loggers[key] = TraceLogger(component, category)

    return _loggers[key]
