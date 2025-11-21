"""
Task Scheduler - Intelligent task allocation across agents
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from Arena.config.arena_config import ArenaConfig
from Arena.trace_logging import get_logger


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Task representation"""
    task_id: str
    task_type: str
    priority: TaskPriority
    assigned_agent: Optional[str]
    created_at: datetime
    deadline: Optional[datetime] = None
    parameters: Dict[str, Any] = None
    status: str = "pending"  # pending, assigned, completed, failed


class TaskScheduler:
    """Task scheduler - intelligent agent task allocation"""
    
    def __init__(self, config: ArenaConfig):
        self.config = config
        self.logger = get_logger("task_scheduler", "scheduling")
        
        # Task queues
        self.pending_tasks: List[Task] = []
        self.assigned_tasks: Dict[str, List[Task]] = {}  # agent_id -> tasks
        self.completed_tasks: List[Task] = []
        
        # Scheduling state
        self.task_counter = 0
        
        self.logger.info("TaskScheduler initialized")
    
    async def schedule_content_creation(self, num_tasks: int = 10) -> List[Task]:
        """
        Schedule content creation tasks
        
        Args:
            num_tasks: Number of tasks to create
            
        Returns:
            List of created tasks
        """
        tasks = []
        
        for i in range(num_tasks):
            task = Task(
                task_id=self._generate_task_id(),
                task_type="content_creation",
                priority=TaskPriority.MEDIUM,
                assigned_agent=None,
                created_at=datetime.now(),
                parameters={"min_quality": 0.7}
            )
            tasks.append(task)
            self.pending_tasks.append(task)
        
        self.logger.info(f"Scheduled {num_tasks} content creation tasks")
        
        return tasks
    
    async def schedule_interactions(self, num_tasks: int = 20) -> List[Task]:
        """
        Schedule interaction tasks
        
        Args:
            num_tasks: Number of tasks to create
            
        Returns:
            List of created tasks
        """
        tasks = []
        
        for i in range(num_tasks):
            task = Task(
                task_id=self._generate_task_id(),
                task_type="interaction",
                priority=TaskPriority.LOW,
                assigned_agent=None,
                created_at=datetime.now(),
                parameters={"interaction_type": "engage"}
            )
            tasks.append(task)
            self.pending_tasks.append(task)
        
        self.logger.info(f"Scheduled {num_tasks} interaction tasks")
        
        return tasks
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by priority and deadline
        
        Args:
            tasks: List of tasks to prioritize
            
        Returns:
            Sorted list of tasks
        """
        def task_sort_key(task: Task) -> tuple:
            # Sort by priority (desc), then by deadline (asc), then by created_at (asc)
            priority_value = task.priority.value
            deadline_value = task.deadline.timestamp() if task.deadline else float('inf')
            created_value = task.created_at.timestamp()
            
            return (-priority_value, deadline_value, created_value)
        
        sorted_tasks = sorted(tasks, key=task_sort_key)
        
        return sorted_tasks
    
    def assign_task(self, task: Task, agent_id: str) -> None:
        """
        Assign task to agent
        
        Args:
            task: Task to assign
            agent_id: ID of agent to assign to
        """
        task.assigned_agent = agent_id
        task.status = "assigned"
        
        if agent_id not in self.assigned_tasks:
            self.assigned_tasks[agent_id] = []
        
        self.assigned_tasks[agent_id].append(task)
        
        if task in self.pending_tasks:
            self.pending_tasks.remove(task)
        
        self.logger.debug(f"Task assigned", extra={
            "task_id": task.task_id,
            "agent_id": agent_id,
            "task_type": task.task_type
        })
    
    def complete_task(self, task_id: str, success: bool = True) -> None:
        """
        Mark task as completed
        
        Args:
            task_id: ID of task
            success: Whether task completed successfully
        """
        # Find task in assigned tasks
        task = None
        for agent_tasks in self.assigned_tasks.values():
            for t in agent_tasks:
                if t.task_id == task_id:
                    task = t
                    break
            if task:
                break
        
        if not task:
            return
        
        task.status = "completed" if success else "failed"
        self.completed_tasks.append(task)
        
        # Remove from assigned tasks
        if task.assigned_agent and task.assigned_agent in self.assigned_tasks:
            self.assigned_tasks[task.assigned_agent].remove(task)
        
        self.logger.debug(f"Task completed", extra={
            "task_id": task_id,
            "success": success
        })
    
    def get_pending_tasks(self, limit: Optional[int] = None) -> List[Task]:
        """Get pending tasks"""
        tasks = self.prioritize_tasks(self.pending_tasks)
        return tasks[:limit] if limit else tasks
    
    def get_agent_tasks(self, agent_id: str) -> List[Task]:
        """Get tasks assigned to agent"""
        return self.assigned_tasks.get(agent_id, [])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        return {
            "pending": len(self.pending_tasks),
            "assigned": sum(len(tasks) for tasks in self.assigned_tasks.values()),
            "completed": len(self.completed_tasks),
            "failed": len([t for t in self.completed_tasks if t.status == "failed"]),
            "total_created": self.task_counter
        }
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        self.task_counter += 1
        return f"task_{self.task_counter:06d}"

