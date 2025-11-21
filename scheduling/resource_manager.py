"""
Resource Manager - Manages computational resources and API limits
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from Arena.config.arena_config import ArenaConfig
from Arena.trace_logging import get_logger


class ResourceAllocation:
    """Resource allocation for an agent"""
    
    def __init__(self, agent_id: str, memory_mb: int, cpu_cores: float):
        self.agent_id = agent_id
        self.memory_mb = memory_mb
        self.cpu_cores = cpu_cores
        self.allocated_at = datetime.now()


class ResourceUsageReport:
    """Resource usage report"""
    
    def __init__(self):
        self.total_memory_mb = 0
        self.total_cpu_cores = 0.0
        self.agent_count = 0
        self.timestamp = datetime.now()


class ResourceManager:
    """Resource manager - manages compute resources and API limits"""
    
    def __init__(self, config: ArenaConfig):
        self.config = config
        self.logger = get_logger("resource_manager", "scheduling")
        
        # Resource allocations
        self.allocations: Dict[str, ResourceAllocation] = {}
        
        # Available resources
        self.available_memory = 8192  # MB
        self.available_cpu = 4.0  # cores
        
        # API rate limiting
        self.api_counters: Dict[str, int] = defaultdict(int)
        self.api_reset_times: Dict[str, datetime] = {}
        
        self.logger.info("ResourceManager initialized", extra={
            "available_memory_mb": self.available_memory,
            "available_cpu_cores": self.available_cpu
        })
    
    def allocate_resources(self, agent_id: str, task_type: str) -> Optional[ResourceAllocation]:
        """
        Allocate resources to agent
        
        Args:
            agent_id: Agent ID
            task_type: Type of task
            
        Returns:
            ResourceAllocation if successful, None otherwise
        """
        # Check if already allocated
        if agent_id in self.allocations:
            return self.allocations[agent_id]
        
        # Determine resource requirements
        memory_needed = self.config.max_memory_per_agent
        cpu_needed = self.config.max_cpu_per_agent
        
        # Check availability
        if (self.available_memory < memory_needed or 
            self.available_cpu < cpu_needed):
            self.logger.warning(f"Insufficient resources for agent", extra={
                "agent_id": agent_id,
                "memory_needed": memory_needed,
                "cpu_needed": cpu_needed,
                "available_memory": self.available_memory,
                "available_cpu": self.available_cpu
            })
            return None
        
        # Allocate
        allocation = ResourceAllocation(agent_id, memory_needed, cpu_needed)
        self.allocations[agent_id] = allocation
        
        self.available_memory -= memory_needed
        self.available_cpu -= cpu_needed
        
        self.logger.info(f"Resources allocated", extra={
            "agent_id": agent_id,
            "memory_mb": memory_needed,
            "cpu_cores": cpu_needed
        })
        
        return allocation
    
    def release_resources(self, agent_id: str) -> None:
        """
        Release resources from agent
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self.allocations:
            return
        
        allocation = self.allocations[agent_id]
        
        self.available_memory += allocation.memory_mb
        self.available_cpu += allocation.cpu_cores
        
        del self.allocations[agent_id]
        
        self.logger.info(f"Resources released", extra={
            "agent_id": agent_id,
            "memory_mb": allocation.memory_mb,
            "cpu_cores": allocation.cpu_cores
        })
    
    def monitor_resource_usage(self) -> ResourceUsageReport:
        """
        Monitor current resource usage
        
        Returns:
            ResourceUsageReport
        """
        report = ResourceUsageReport()
        
        for allocation in self.allocations.values():
            report.total_memory_mb += allocation.memory_mb
            report.total_cpu_cores += allocation.cpu_cores
            report.agent_count += 1
        
        self.logger.debug(f"Resource usage monitored", extra={
            "total_memory_mb": report.total_memory_mb,
            "total_cpu_cores": report.total_cpu_cores,
            "agent_count": report.agent_count
        })
        
        return report
    
    async def enforce_api_limits(self, platform: str, endpoint: str = "default") -> bool:
        """
        Enforce platform API limits
        
        Args:
            platform: Platform name (e.g., "twitter", "feed_system")
            endpoint: Specific endpoint
            
        Returns:
            True if within limits, False if rate limited
        """
        key = f"{platform}:{endpoint}"
        
        # Check if rate limit window has reset
        if key in self.api_reset_times:
            if datetime.now() >= self.api_reset_times[key]:
                # Reset counter
                self.api_counters[key] = 0
                del self.api_reset_times[key]
        
        # Get limit for platform
        limit = self.config.api_rate_limits.get(platform, 100)
        
        # Check if within limit
        if self.api_counters[key] >= limit:
            self.logger.warning(f"API rate limit reached", extra={
                "platform": platform,
                "endpoint": endpoint,
                "limit": limit
            })
            return False
        
        # Increment counter
        self.api_counters[key] += 1
        
        # Set reset time if first request
        if key not in self.api_reset_times:
            self.api_reset_times[key] = datetime.now() + timedelta(minutes=1)
        
        return True
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """Get resource statistics"""
        usage_report = self.monitor_resource_usage()
        
        return {
            "allocated_memory_mb": usage_report.total_memory_mb,
            "allocated_cpu_cores": usage_report.total_cpu_cores,
            "available_memory_mb": self.available_memory,
            "available_cpu_cores": self.available_cpu,
            "agent_count": usage_report.agent_count,
            "memory_utilization": usage_report.total_memory_mb / (usage_report.total_memory_mb + self.available_memory) if (usage_report.total_memory_mb + self.available_memory) > 0 else 0,
            "cpu_utilization": usage_report.total_cpu_cores / (usage_report.total_cpu_cores + self.available_cpu) if (usage_report.total_cpu_cores + self.available_cpu) > 0 else 0
        }

