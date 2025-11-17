"""
Log Analysis Utilities

Tools for analyzing and debugging trace logs.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class LogEntry:
    """Parsed log entry"""
    timestamp: datetime
    level: str
    component: str
    event: str
    message: str
    data: Dict[str, Any]
    context: Dict[str, Any]
    exception: Optional[Dict[str, Any]] = None
    raw: str = ""

    @classmethod
    def from_json(cls, json_str: str) -> 'LogEntry':
        """Parse log entry from JSON string"""
        try:
            data = json.loads(json_str)
            return cls(
                timestamp=datetime.fromisoformat(data['timestamp'].rstrip('Z')),
                level=data.get('level', 'INFO'),
                component=data.get('component', ''),
                event=data.get('event', ''),
                message=data.get('message', ''),
                data=data.get('data', {}),
                context=data.get('context', {}),
                exception=data.get('exception'),
                raw=json_str
            )
        except Exception as e:
            # Return a minimal entry for malformed logs
            return cls(
                timestamp=datetime.utcnow(),
                level='ERROR',
                component='parser',
                event='parse_error',
                message=f"Failed to parse log: {e}",
                data={'raw': json_str},
                context={},
                raw=json_str
            )


class LogReader:
    """Read and parse log files"""

    def __init__(self, trace_dir: Path = Path("trace")):
        self.trace_dir = trace_dir

    def read_logs(
        self,
        category: Optional[str] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[str] = None,
        trace_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Iterator[LogEntry]:
        """
        Read logs with filters.

        Args:
            category: Filter by category (e.g., "agents", "simulation")
            component: Filter by component name
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            level: Filter by log level
            trace_id: Filter by trace ID
            limit: Maximum number of logs to return

        Yields:
            LogEntry objects matching filters
        """
        count = 0

        # Determine which files to read
        if category and component:
            files = [self.trace_dir / category / f"{component}.jsonl"]
        elif category:
            files = list((self.trace_dir / category).glob("*.jsonl"))
        else:
            files = list(self.trace_dir.glob("**/*.jsonl"))

        for log_file in files:
            if not log_file.exists():
                continue

            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if limit and count >= limit:
                            return

                        entry = LogEntry.from_json(line.strip())

                        # Apply filters
                        if start_time and entry.timestamp < start_time:
                            continue
                        if end_time and entry.timestamp > end_time:
                            continue
                        if level and entry.level != level:
                            continue
                        if trace_id and entry.context.get('trace_id') != trace_id:
                            continue

                        yield entry
                        count += 1

            except Exception as e:
                print(f"Error reading {log_file}: {e}")
                continue

    def get_trace_chain(self, trace_id: str) -> List[LogEntry]:
        """Get all logs for a specific trace ID"""
        return list(self.read_logs(trace_id=trace_id))

    def get_recent_errors(
        self,
        hours: int = 1,
        limit: int = 100
    ) -> List[LogEntry]:
        """Get recent error logs"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return list(self.read_logs(
            level='ERROR',
            start_time=start_time,
            limit=limit
        ))

    def get_component_logs(
        self,
        category: str,
        component: str,
        limit: int = 100
    ) -> List[LogEntry]:
        """Get logs for a specific component"""
        return list(self.read_logs(
            category=category,
            component=component,
            limit=limit
        ))


class LogAnalyzer:
    """Analyze logs for patterns and insights"""

    def __init__(self, trace_dir: Path = Path("trace")):
        self.reader = LogReader(trace_dir)

    def analyze_errors(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze error patterns.

        Returns:
            Dictionary with error analysis
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        errors = list(self.reader.read_logs(
            level='ERROR',
            start_time=start_time
        ))

        # Count by component
        by_component = Counter(e.component for e in errors)

        # Count by event type
        by_event = Counter(e.event for e in errors)

        # Count by error type (from exception)
        error_types = Counter()
        for e in errors:
            if e.exception:
                error_types[e.exception.get('type', 'Unknown')] += 1

        # Identify most recent errors
        recent_errors = sorted(errors, key=lambda e: e.timestamp, reverse=True)[:10]

        return {
            'total_errors': len(errors),
            'by_component': dict(by_component.most_common(10)),
            'by_event': dict(by_event.most_common(10)),
            'by_error_type': dict(error_types.most_common(10)),
            'recent_errors': [
                {
                    'timestamp': e.timestamp.isoformat(),
                    'component': e.component,
                    'event': e.event,
                    'message': e.message,
                }
                for e in recent_errors
            ]
        }

    def analyze_performance(
        self,
        operation: str,
        hours: int = 1
    ) -> Dict[str, Any]:
        """
        Analyze performance metrics for an operation.

        Args:
            operation: Operation name to analyze
            hours: Hours of history to analyze

        Returns:
            Performance statistics
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        logs = list(self.reader.read_logs(start_time=start_time))

        # Find operation start/complete pairs
        durations = []
        for log in logs:
            if log.event == f"{operation}.complete":
                duration = log.data.get('duration_seconds')
                if duration:
                    durations.append(duration)

        if not durations:
            return {'error': 'No performance data found'}

        durations.sort()
        count = len(durations)

        return {
            'operation': operation,
            'count': count,
            'min_seconds': min(durations),
            'max_seconds': max(durations),
            'avg_seconds': sum(durations) / count,
            'median_seconds': durations[count // 2],
            'p95_seconds': durations[int(count * 0.95)] if count > 20 else None,
            'p99_seconds': durations[int(count * 0.99)] if count > 100 else None,
        }

    def trace_request(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Trace a request through the system.

        Args:
            trace_id: Trace ID to follow

        Returns:
            List of log entries in chronological order
        """
        logs = self.reader.get_trace_chain(trace_id)
        logs.sort(key=lambda e: e.timestamp)

        return [
            {
                'timestamp': e.timestamp.isoformat(),
                'component': e.component,
                'event': e.event,
                'message': e.message,
                'data': e.data,
            }
            for e in logs
        ]

    def find_slow_operations(
        self,
        threshold_seconds: float = 1.0,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Find operations that exceeded duration threshold.

        Args:
            threshold_seconds: Duration threshold
            hours: Hours of history to search

        Returns:
            List of slow operations
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        logs = list(self.reader.read_logs(start_time=start_time))

        slow_ops = []
        for log in logs:
            if '.complete' in log.event:
                duration = log.data.get('duration_seconds', 0)
                if duration >= threshold_seconds:
                    slow_ops.append({
                        'timestamp': log.timestamp.isoformat(),
                        'component': log.component,
                        'operation': log.event.replace('.complete', ''),
                        'duration_seconds': duration,
                        'trace_id': log.context.get('trace_id'),
                    })

        return sorted(slow_ops, key=lambda x: x['duration_seconds'], reverse=True)

    def analyze_agent_behavior(
        self,
        agent_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze behavior of a specific agent.

        Args:
            agent_id: Agent ID to analyze
            hours: Hours of history

        Returns:
            Agent behavior analysis
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        logs = list(self.reader.read_logs(
            category='agents',
            start_time=start_time
        ))

        # Filter for this agent
        agent_logs = [
            log for log in logs
            if log.context.get('agent_id') == agent_id
        ]

        # Count actions
        actions = Counter(
            log.data.get('action_type')
            for log in agent_logs
            if log.event == 'agent_action'
        )

        # Find strategy changes
        strategy_changes = [
            {
                'timestamp': log.timestamp.isoformat(),
                'old_strategy': log.data.get('old_state'),
                'new_strategy': log.data.get('new_state'),
                'reason': log.data.get('reason'),
            }
            for log in agent_logs
            if log.event == 'state_change' and log.data.get('entity_type') == 'agent_strategy'
        ]

        # Find learning events
        learning_events = [
            {
                'timestamp': log.timestamp.isoformat(),
                'event': log.data.get('learning_event'),
                'improvement': log.data.get('improvement', {}),
            }
            for log in agent_logs
            if log.event == 'agent_learning'
        ]

        return {
            'agent_id': agent_id,
            'total_logs': len(agent_logs),
            'actions': dict(actions.most_common()),
            'strategy_changes': strategy_changes,
            'learning_events': learning_events,
        }

    def generate_summary_report(self, hours: int = 24) -> str:
        """
        Generate a summary report of system activity.

        Args:
            hours: Hours of history to include

        Returns:
            Formatted report string
        """
        error_analysis = self.analyze_errors(hours)

        report_lines = [
            f"=== Arena System Report (Last {hours} hours) ===",
            "",
            "Error Summary:",
            f"  Total Errors: {error_analysis['total_errors']}",
            "",
            "Errors by Component:",
        ]

        for component, count in list(error_analysis['by_component'].items())[:5]:
            report_lines.append(f"  {component}: {count}")

        report_lines.extend([
            "",
            "Recent Errors:",
        ])

        for err in error_analysis['recent_errors'][:5]:
            report_lines.append(
                f"  [{err['timestamp']}] {err['component']}: {err['message']}"
            )

        return "\n".join(report_lines)
