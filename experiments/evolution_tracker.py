"""
Evolution Tracker - Tracks strategy evolution across agents
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

from Arena.trace_logging import get_logger


@dataclass
class EvolutionEvent:
    """Evolution event record"""
    agent_id: str
    event_type: str  # "mutation", "crossover", "selection"
    old_strategy: Dict[str, Any]
    new_strategy: Dict[str, Any]
    fitness_before: float
    fitness_after: float
    timestamp: datetime


@dataclass
class SuccessfulMutation:
    """Record of successful strategy mutation"""
    mutation_id: str
    agent_id: str
    strategy_change: Dict[str, Any]
    fitness_improvement: float
    timestamp: datetime


@dataclass
class EvolutionHistory:
    """Evolution history for an agent"""
    agent_id: str
    events: List[EvolutionEvent]
    successful_mutations: List[SuccessfulMutation]
    current_fitness: float


@dataclass
class EvolutionDirection:
    """Recommended evolution direction"""
    direction_type: str
    parameters: Dict[str, Any]
    expected_improvement: float
    confidence: float


class EvolutionTracker:
    """Evolution tracker - tracks strategy evolution"""
    
    def __init__(self):
        self.logger = get_logger("evolution_tracker", "experiments")
        
        # Evolution tracking
        self.evolution_histories: Dict[str, EvolutionHistory] = {}
        self.successful_mutations: List[SuccessfulMutation] = []
        
        # Population statistics
        self.fitness_history: Dict[str, List[float]] = defaultdict(list)
        self.generation_count = 0
        
        self.logger.info("EvolutionTracker initialized")
    
    def track_strategy_evolution(self, agent_id: str) -> EvolutionHistory:
        """
        Track strategy evolution for agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Evolution history
        """
        if agent_id not in self.evolution_histories:
            self.evolution_histories[agent_id] = EvolutionHistory(
                agent_id=agent_id,
                events=[],
                successful_mutations=[],
                current_fitness=0.0
            )
        
        return self.evolution_histories[agent_id]
    
    def record_evolution_event(
        self,
        agent_id: str,
        event_type: str,
        old_strategy: Dict[str, Any],
        new_strategy: Dict[str, Any],
        fitness_before: float,
        fitness_after: float
    ) -> None:
        """
        Record an evolution event
        
        Args:
            agent_id: Agent ID
            event_type: Type of evolution event
            old_strategy: Strategy before evolution
            new_strategy: Strategy after evolution
            fitness_before: Fitness before evolution
            fitness_after: Fitness after evolution
        """
        event = EvolutionEvent(
            agent_id=agent_id,
            event_type=event_type,
            old_strategy=old_strategy,
            new_strategy=new_strategy,
            fitness_before=fitness_before,
            fitness_after=fitness_after,
            timestamp=datetime.now()
        )
        
        history = self.track_strategy_evolution(agent_id)
        history.events.append(event)
        history.current_fitness = fitness_after
        
        # Track fitness history
        self.fitness_history[agent_id].append(fitness_after)
        
        # Check if mutation was successful
        if fitness_after > fitness_before:
            mutation = SuccessfulMutation(
                mutation_id=f"mut_{agent_id}_{len(history.successful_mutations)}",
                agent_id=agent_id,
                strategy_change=self._calculate_strategy_diff(old_strategy, new_strategy),
                fitness_improvement=fitness_after - fitness_before,
                timestamp=datetime.now()
            )
            
            history.successful_mutations.append(mutation)
            self.successful_mutations.append(mutation)
            
            self.logger.info(f"Successful mutation recorded", extra={
                "agent_id": agent_id,
                "fitness_improvement": mutation.fitness_improvement
            })
    
    def identify_successful_mutations(self, min_improvement: float = 0.1) -> List[SuccessfulMutation]:
        """
        Identify successful mutations
        
        Args:
            min_improvement: Minimum fitness improvement threshold
            
        Returns:
            List of successful mutations
        """
        significant_mutations = [
            m for m in self.successful_mutations
            if m.fitness_improvement >= min_improvement
        ]
        
        # Sort by improvement
        significant_mutations.sort(key=lambda x: x.fitness_improvement, reverse=True)
        
        return significant_mutations
    
    def recommend_evolution_directions(self, agent_id: str) -> List[EvolutionDirection]:
        """
        Recommend evolution directions for agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of recommended directions
        """
        history = self.track_strategy_evolution(agent_id)
        
        recommendations = []
        
        # Analyze successful mutations
        if history.successful_mutations:
            # Recommend similar mutations
            recent_success = history.successful_mutations[-1]
            
            recommendations.append(EvolutionDirection(
                direction_type="similar_mutation",
                parameters=recent_success.strategy_change,
                expected_improvement=recent_success.fitness_improvement * 0.8,
                confidence=0.7
            ))
        
        # Recommend based on population best practices
        population_best = self._find_population_best_practices()
        if population_best:
            recommendations.append(EvolutionDirection(
                direction_type="population_best",
                parameters=population_best,
                expected_improvement=0.15,
                confidence=0.6
            ))
        
        return recommendations
    
    def _calculate_strategy_diff(
        self,
        old_strategy: Dict[str, Any],
        new_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate difference between strategies"""
        diff = {}
        
        # Find changed parameters
        for key in set(list(old_strategy.keys()) + list(new_strategy.keys())):
            old_val = old_strategy.get(key)
            new_val = new_strategy.get(key)
            
            if old_val != new_val:
                diff[key] = {
                    "old": old_val,
                    "new": new_val
                }
        
        return diff
    
    def _find_population_best_practices(self) -> Dict[str, Any]:
        """Find best practices from population"""
        # Analyze top performing agents
        if not self.fitness_history:
            return {}
        
        # Get agents with highest average fitness
        avg_fitness = {
            agent_id: sum(fitnesses) / len(fitnesses)
            for agent_id, fitnesses in self.fitness_history.items()
        }
        
        if not avg_fitness:
            return {}
        
        best_agent = max(avg_fitness, key=avg_fitness.get)
        
        return {
            "best_agent": best_agent,
            "fitness": avg_fitness[best_agent],
            "strategy_hints": "explore_more"  # Simplified
        }
    
    def get_population_statistics(self) -> Dict[str, Any]:
        """Get population evolution statistics"""
        if not self.fitness_history:
            return {}
        
        # Calculate population metrics
        current_fitnesses = [
            fitnesses[-1] for fitnesses in self.fitness_history.values()
            if fitnesses
        ]
        
        return {
            "population_size": len(self.fitness_history),
            "average_fitness": sum(current_fitnesses) / max(len(current_fitnesses), 1),
            "max_fitness": max(current_fitnesses) if current_fitnesses else 0,
            "min_fitness": min(current_fitnesses) if current_fitnesses else 0,
            "successful_mutations": len(self.successful_mutations),
            "generation": self.generation_count
        }
    
    def advance_generation(self) -> None:
        """Advance to next generation"""
        self.generation_count += 1
        
        self.logger.info(f"Advanced to generation {self.generation_count}")
    
    def _generate_experiment_id(self) -> str:
        """Generate unique experiment ID"""
        self.experiment_counter += 1
        return f"exp_{self.experiment_counter:06d}"

