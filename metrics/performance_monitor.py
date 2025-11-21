"""
Performance Monitor - Monitors system and agent performance
"""

from typing import Dict, List, Any
from datetime import datetime
from collections import deque

from Arena.config.arena_config import ArenaConfig
from Arena.trace_logging import get_logger


class PerformanceMonitor:
    """Performance monitor - monitors system performance"""
    
    def __init__(self, config: ArenaConfig):
        self.config = config
        self.logger = get_logger("performance_monitor", "metrics")
        
        # Performance history
        self.system_load_history = deque(maxlen=100)
        self.latency_history = deque(maxlen=100)
        self.throughput_history = deque(maxlen=100)
        
        # Current metrics
        self.current_system_load = 0.0
        self.current_latency = 0.0
        self.current_throughput = 0.0
        
        # Counters
        self.total_actions_processed = 0
        self.total_errors = 0
        
        self.logger.info("PerformanceMonitor initialized")
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect current performance metrics
        
        Returns:
            Performance metrics
        """
        # Update system load (mock)
        import random
        self.current_system_load = random.uniform(0.3, 0.8)
        self.system_load_history.append(self.current_system_load)
        
        # Update latency (mock)
        self.current_latency = random.uniform(10, 100)  # ms
        self.latency_history.append(self.current_latency)
        
        # Update throughput (mock)
        self.current_throughput = random.uniform(100, 1000)  # actions/sec
        self.throughput_history.append(self.current_throughput)
        
        metrics = {
            "system_load": self.current_system_load,
            "latency_ms": self.current_latency,
            "throughput": self.current_throughput,
            "total_actions": self.total_actions_processed,
            "total_errors": self.total_errors,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.debug(f"Metrics collected", extra=metrics)
        
        return metrics
    
    def monitor_agent_performance(self) -> Dict[str, Any]:
        """
        Monitor agent performance
        
        Returns:
            Agent performance metrics
        """
        # In real system, would track per-agent metrics
        return {
            "active_agents": 0,
            "average_response_time": 0.0,
            "error_rate": 0.0
        }
    
    def track_system_metrics(self) -> Dict[str, Any]:
        """
        Track system-level metrics
        
        Returns:
            System metrics
        """
        return {
            "system_load": self.current_system_load,
            "memory_usage": 0.0,  # Mock
            "cpu_usage": 0.0,  # Mock
            "network_io": 0.0  # Mock
        }
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "system_load": self.current_system_load,
            "latency_ms": self.current_latency,
            "throughput": self.current_throughput
        }
    
    async def generate_report(self) -> Dict[str, Any]:
        """
        Generate performance report
        
        Returns:
            Performance report
        """
        # Calculate averages
        avg_load = sum(self.system_load_history) / max(len(self.system_load_history), 1)
        avg_latency = sum(self.latency_history) / max(len(self.latency_history), 1)
        avg_throughput = sum(self.throughput_history) / max(len(self.throughput_history), 1)
        
        # Calculate peaks
        peak_load = max(self.system_load_history) if self.system_load_history else 0
        peak_latency = max(self.latency_history) if self.latency_history else 0
        peak_throughput = max(self.throughput_history) if self.throughput_history else 0
        
        report = {
            "summary": {
                "total_actions_processed": self.total_actions_processed,
                "total_errors": self.total_errors,
                "error_rate": self.total_errors / max(self.total_actions_processed, 1)
            },
            "system_load": {
                "average": avg_load,
                "peak": peak_load,
                "current": self.current_system_load
            },
            "latency": {
                "average_ms": avg_latency,
                "peak_ms": peak_latency,
                "current_ms": self.current_latency
            },
            "throughput": {
                "average_per_sec": avg_throughput,
                "peak_per_sec": peak_throughput,
                "current_per_sec": self.current_throughput
            }
        }
        
        self.logger.info("Performance report generated", extra={
            "avg_load": avg_load,
            "avg_latency": avg_latency,
            "avg_throughput": avg_throughput
        })
        
        return report
    
    def should_emergency_stop(self) -> bool:
        """
        Check if system should emergency stop
        
        Returns:
            True if emergency stop needed
        """
        if self.current_system_load > self.config.emergency_stop_threshold:
            self.logger.critical(f"Emergency stop condition met", extra={
                "system_load": self.current_system_load,
                "threshold": self.config.emergency_stop_threshold
            })
            return True
        
        return False
    
    def record_action(self, success: bool = True) -> None:
        """Record an action execution"""
        self.total_actions_processed += 1
        if not success:
            self.total_errors += 1

