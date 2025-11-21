"""
A/B Testing Framework - Hot-swappable strategy testing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib

from Arena.trace_logging import get_logger


class ExperimentStatus(Enum):
    """Experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ExperimentConfig:
    """Configuration for A/B experiment"""
    name: str
    hypothesis: str
    control_strategy: str
    treatment_strategy: str
    split_ratio: float = 0.5  # 50/50 split
    duration: timedelta = timedelta(days=7)
    min_sample_size: int = 100
    significance_level: float = 0.05


@dataclass
class ExperimentMetrics:
    """Metrics for experiment analysis"""
    control: Dict[str, float]
    treatment: Dict[str, float]
    p_value: float
    effect_size: float
    confidence_interval: tuple
    is_significant: bool


class Experiment:
    """A/B Test Experiment"""
    
    def __init__(self, experiment_id: str, config: ExperimentConfig):
        self.id = experiment_id
        self.config = config
        self.status = ExperimentStatus.DRAFT
        
        # Group assignments
        self.control_group: List[str] = []
        self.treatment_group: List[str] = []
        
        # Results
        self.control_metrics: Dict[str, List[float]] = {}
        self.treatment_metrics: Dict[str, List[float]] = {}
        
        # Timing
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def assign_to_group(self, agent_id: str) -> str:
        """Assign agent to control or treatment group"""
        # Consistent hashing for stable assignment
        hash_value = hashlib.md5(f"{agent_id}{self.id}".encode()).hexdigest()
        hash_int = int(hash_value, 16)
        
        if (hash_int % 100) < (self.config.split_ratio * 100):
            group = "treatment"
            self.treatment_group.append(agent_id)
        else:
            group = "control"
            self.control_group.append(agent_id)
        
        return group
    
    def record_metric(self, agent_id: str, metric_name: str, value: float) -> None:
        """Record metric for agent"""
        if agent_id in self.treatment_group:
            if metric_name not in self.treatment_metrics:
                self.treatment_metrics[metric_name] = []
            self.treatment_metrics[metric_name].append(value)
        elif agent_id in self.control_group:
            if metric_name not in self.control_metrics:
                self.control_metrics[metric_name] = []
            self.control_metrics[metric_name].append(value)


class ABTestFramework:
    """A/B testing framework - hot-swappable strategy testing"""
    
    def __init__(self):
        self.logger = get_logger("ab_testing", "experiments")
        
        # Experiments
        self.experiments: Dict[str, Experiment] = {}
        self.experiment_counter = 0
        
        self.logger.info("ABTestFramework initialized")
    
    def create_experiment(self, config: ExperimentConfig) -> Experiment:
        """
        Create new A/B test experiment
        
        Args:
            config: Experiment configuration
            
        Returns:
            Created experiment
        """
        experiment_id = self._generate_experiment_id()
        
        experiment = Experiment(experiment_id, config)
        self.experiments[experiment_id] = experiment
        
        self.logger.info(f"Experiment created", extra={
            "experiment_id": experiment_id,
            "name": config.name,
            "hypothesis": config.hypothesis
        })
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> None:
        """Start experiment"""
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_time = datetime.now()
        
        self.logger.info(f"Experiment started", extra={
            "experiment_id": experiment_id,
            "name": experiment.config.name
        })
    
    def stop_experiment(self, experiment_id: str) -> None:
        """Stop experiment"""
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_time = datetime.now()
        
        self.logger.info(f"Experiment stopped", extra={
            "experiment_id": experiment_id,
            "duration": (experiment.end_time - experiment.start_time).total_seconds()
        })
    
    def assign_agents_to_groups(self, experiment_id: str, agent_ids: List[str]) -> Dict[str, str]:
        """
        Assign agents to experiment groups
        
        Args:
            experiment_id: Experiment ID
            agent_ids: List of agent IDs
            
        Returns:
            Dictionary mapping agent_id to group
        """
        if experiment_id not in self.experiments:
            return {}
        
        experiment = self.experiments[experiment_id]
        assignments = {}
        
        for agent_id in agent_ids:
            group = experiment.assign_to_group(agent_id)
            assignments[agent_id] = group
        
        self.logger.info(f"Agents assigned to experiment", extra={
            "experiment_id": experiment_id,
            "total_agents": len(agent_ids),
            "control": len(experiment.control_group),
            "treatment": len(experiment.treatment_group)
        })
        
        return assignments
    
    def record_agent_metric(
        self,
        experiment_id: str,
        agent_id: str,
        metric_name: str,
        value: float
    ) -> None:
        """Record metric for agent in experiment"""
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        experiment.record_metric(agent_id, metric_name, value)
    
    def analyze_experiment_results(self, experiment_id: str) -> Optional[ExperimentMetrics]:
        """
        Analyze experiment results
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            ExperimentMetrics or None
        """
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        
        # Calculate average metrics for each group
        control_avg = {}
        for metric_name, values in experiment.control_metrics.items():
            control_avg[metric_name] = sum(values) / max(len(values), 1)
        
        treatment_avg = {}
        for metric_name, values in experiment.treatment_metrics.items():
            treatment_avg[metric_name] = sum(values) / max(len(values), 1)
        
        # Calculate p-value and effect size (simplified)
        p_value = self._calculate_p_value(experiment)
        effect_size = self._calculate_effect_size(experiment)
        
        # Determine significance
        is_significant = p_value < experiment.config.significance_level
        
        metrics = ExperimentMetrics(
            control=control_avg,
            treatment=treatment_avg,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(0.0, 1.0),  # Simplified
            is_significant=is_significant
        )
        
        self.logger.info(f"Experiment analyzed", extra={
            "experiment_id": experiment_id,
            "is_significant": is_significant,
            "p_value": p_value,
            "effect_size": effect_size
        })
        
        return metrics
    
    def _calculate_p_value(self, experiment: Experiment) -> float:
        """Calculate p-value (simplified)"""
        # Mock p-value calculation
        # In production, use proper statistical test (t-test, etc.)
        import random
        return random.uniform(0.01, 0.1)
    
    def _calculate_effect_size(self, experiment: Experiment) -> float:
        """Calculate effect size (Cohen's d)"""
        # Simplified effect size
        # In production, calculate proper Cohen's d
        import random
        return random.uniform(0.2, 0.8)
    
    def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment status"""
        if experiment_id not in self.experiments:
            return {}
        
        experiment = self.experiments[experiment_id]
        
        return {
            "experiment_id": experiment_id,
            "name": experiment.config.name,
            "status": experiment.status.value,
            "control_size": len(experiment.control_group),
            "treatment_size": len(experiment.treatment_group),
            "start_time": experiment.start_time.isoformat() if experiment.start_time else None,
            "end_time": experiment.end_time.isoformat() if experiment.end_time else None
        }
    
    def _generate_experiment_id(self) -> str:
        """Generate unique experiment ID"""
        self.experiment_counter += 1
        return f"exp_{self.experiment_counter:04d}"

