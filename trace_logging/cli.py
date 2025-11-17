"""
CLI Tool for Log Analysis

Interactive command-line interface for exploring Arena traces.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

from .analysis import LogReader, LogAnalyzer


def cmd_errors(args):
    """Show recent errors"""
    analyzer = LogAnalyzer(Path(args.trace_dir))
    analysis = analyzer.analyze_errors(hours=args.hours)

    print(f"\n=== Error Analysis (Last {args.hours} hours) ===\n")
    print(f"Total Errors: {analysis['total_errors']}\n")

    if analysis['by_component']:
        print("Errors by Component:")
        for component, count in list(analysis['by_component'].items())[:10]:
            print(f"  {component}: {count}")
        print()

    if analysis['by_error_type']:
        print("Errors by Type:")
        for error_type, count in list(analysis['by_error_type'].items())[:10]:
            print(f"  {error_type}: {count}")
        print()

    if analysis['recent_errors']:
        print("Most Recent Errors:")
        for err in analysis['recent_errors'][:10]:
            print(f"  [{err['timestamp']}] {err['component']}")
            print(f"    Event: {err['event']}")
            print(f"    Message: {err['message']}")
            print()


def cmd_trace(args):
    """Trace a specific request"""
    analyzer = LogAnalyzer(Path(args.trace_dir))
    logs = analyzer.trace_request(args.trace_id)

    print(f"\n=== Trace: {args.trace_id} ===\n")

    if not logs:
        print("No logs found for this trace ID")
        return

    for log in logs:
        print(f"[{log['timestamp']}] {log['component']}")
        print(f"  Event: {log['event']}")
        print(f"  Message: {log['message']}")
        if log['data']:
            print(f"  Data: {log['data']}")
        print()


def cmd_performance(args):
    """Analyze performance of an operation"""
    analyzer = LogAnalyzer(Path(args.trace_dir))
    stats = analyzer.analyze_performance(args.operation, hours=args.hours)

    print(f"\n=== Performance Analysis: {args.operation} ===\n")

    if 'error' in stats:
        print(f"Error: {stats['error']}")
        return

    print(f"Total Executions: {stats['count']}")
    print(f"Min Duration: {stats['min_seconds']:.3f}s")
    print(f"Max Duration: {stats['max_seconds']:.3f}s")
    print(f"Avg Duration: {stats['avg_seconds']:.3f}s")
    print(f"Median Duration: {stats['median_seconds']:.3f}s")

    if stats['p95_seconds']:
        print(f"P95 Duration: {stats['p95_seconds']:.3f}s")
    if stats['p99_seconds']:
        print(f"P99 Duration: {stats['p99_seconds']:.3f}s")


def cmd_slow(args):
    """Find slow operations"""
    analyzer = LogAnalyzer(Path(args.trace_dir))
    slow_ops = analyzer.find_slow_operations(
        threshold_seconds=args.threshold,
        hours=args.hours
    )

    print(f"\n=== Slow Operations (>{args.threshold}s, Last {args.hours} hours) ===\n")

    if not slow_ops:
        print("No slow operations found")
        return

    for op in slow_ops[:20]:
        print(f"[{op['timestamp']}] {op['component']}")
        print(f"  Operation: {op['operation']}")
        print(f"  Duration: {op['duration_seconds']:.3f}s")
        print(f"  Trace ID: {op['trace_id']}")
        print()


def cmd_agent(args):
    """Analyze agent behavior"""
    analyzer = LogAnalyzer(Path(args.trace_dir))
    analysis = analyzer.analyze_agent_behavior(args.agent_id, hours=args.hours)

    print(f"\n=== Agent Analysis: {args.agent_id} ===\n")

    print(f"Total Log Entries: {analysis['total_logs']}\n")

    if analysis['actions']:
        print("Actions Taken:")
        for action, count in list(analysis['actions'].items())[:10]:
            print(f"  {action}: {count}")
        print()

    if analysis['strategy_changes']:
        print("Strategy Changes:")
        for change in analysis['strategy_changes']:
            print(f"  [{change['timestamp']}]")
            print(f"    {change['old_strategy']} -> {change['new_strategy']}")
            print(f"    Reason: {change['reason']}")
            print()

    if analysis['learning_events']:
        print("Learning Events:")
        for event in analysis['learning_events'][:5]:
            print(f"  [{event['timestamp']}] {event['event']}")
            if event['improvement']:
                print(f"    Improvements: {event['improvement']}")
            print()


def cmd_summary(args):
    """Show summary report"""
    analyzer = LogAnalyzer(Path(args.trace_dir))
    report = analyzer.generate_summary_report(hours=args.hours)
    print(report)


def cmd_tail(args):
    """Tail logs in real-time"""
    reader = LogReader(Path(args.trace_dir))

    print(f"\n=== Tailing logs (Ctrl+C to stop) ===\n")

    try:
        # Show last N logs first
        logs = list(reader.read_logs(
            category=args.category,
            component=args.component,
            limit=args.lines
        ))

        for log in logs[-args.lines:]:
            print(f"[{log.timestamp}] {log.level} {log.component}")
            print(f"  {log.event}: {log.message}")
            if args.verbose and log.data:
                print(f"  Data: {log.data}")
            print()

        # In a real implementation, would watch for new logs
        print("(Live tailing not implemented in this version)")

    except KeyboardInterrupt:
        print("\nStopped tailing")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Arena Trace Log Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--trace-dir',
        default='trace',
        help='Trace directory path (default: trace)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Errors command
    errors_parser = subparsers.add_parser('errors', help='Show recent errors')
    errors_parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours of history to analyze (default: 24)'
    )

    # Trace command
    trace_parser = subparsers.add_parser('trace', help='Trace a specific request')
    trace_parser.add_argument('trace_id', help='Trace ID to follow')

    # Performance command
    perf_parser = subparsers.add_parser('performance', help='Analyze operation performance')
    perf_parser.add_argument('operation', help='Operation name')
    perf_parser.add_argument(
        '--hours',
        type=int,
        default=1,
        help='Hours of history (default: 1)'
    )

    # Slow operations command
    slow_parser = subparsers.add_parser('slow', help='Find slow operations')
    slow_parser.add_argument(
        '--threshold',
        type=float,
        default=1.0,
        help='Duration threshold in seconds (default: 1.0)'
    )
    slow_parser.add_argument(
        '--hours',
        type=int,
        default=1,
        help='Hours of history (default: 1)'
    )

    # Agent command
    agent_parser = subparsers.add_parser('agent', help='Analyze agent behavior')
    agent_parser.add_argument('agent_id', help='Agent ID')
    agent_parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours of history (default: 24)'
    )

    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show summary report')
    summary_parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours of history (default: 24)'
    )

    # Tail command
    tail_parser = subparsers.add_parser('tail', help='Tail logs')
    tail_parser.add_argument(
        '--category',
        help='Filter by category'
    )
    tail_parser.add_argument(
        '--component',
        help='Filter by component'
    )
    tail_parser.add_argument(
        '--lines',
        type=int,
        default=10,
        help='Number of lines to show (default: 10)'
    )
    tail_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed data'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Dispatch to command handler
    commands = {
        'errors': cmd_errors,
        'trace': cmd_trace,
        'performance': cmd_performance,
        'slow': cmd_slow,
        'agent': cmd_agent,
        'summary': cmd_summary,
        'tail': cmd_tail,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
