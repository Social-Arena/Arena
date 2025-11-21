"""
Virality Tracker - Tracks viral content propagation
"""

from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

from Arena.trace_logging import get_logger


class ViralityTracker:
    """Virality tracker - tracks viral content propagation"""
    
    def __init__(self):
        self.logger = get_logger("virality_tracker", "metrics")
        
        # Tracking state
        self.content_metrics: Dict[str, Dict[str, Any]] = {}
        self.viral_content: List[str] = []
        self.propagation_chains: Dict[str, List[str]] = defaultdict(list)
        
        # Thresholds
        self.virality_threshold = 0.7
        
        self.logger.info("ViralityTracker initialized")
    
    async def track_step(self, agent_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Track virality for current step
        
        Args:
            agent_actions: List of agent actions
            
        Returns:
            Metrics for this step
        """
        viral_count = 0
        new_content_count = 0
        
        for action_data in agent_actions:
            action = action_data.get("action")
            
            if not action:
                continue
            
            # Track content creation
            if action.action_type == "create_content":
                new_content_count += 1
                
                # Extract content ID if available
                content_id = getattr(action, 'content_id', None)
                if not content_id and hasattr(action, 'content'):
                    # Generate ID from content
                    content_id = f"content_{action.agent_id}_{int(action.timestamp.timestamp())}"
                
                if content_id:
                    await self._track_content(content_id, action)
        
        # Check for viral content
        for content_id, metrics in self.content_metrics.items():
            virality_score = metrics.get("virality_score", 0)
            if virality_score > self.virality_threshold and content_id not in self.viral_content:
                self.viral_content.append(content_id)
                viral_count += 1
                
                self.logger.info(f"Viral content detected", extra={
                    "content_id": content_id,
                    "virality_score": virality_score
                })
        
        return {
            "viral_count": viral_count,
            "new_content": new_content_count,
            "total_viral": len(self.viral_content)
        }
    
    async def _track_content(self, content_id: str, action: Any) -> None:
        """Track individual content"""
        if content_id not in self.content_metrics:
            self.content_metrics[content_id] = {
                "content_id": content_id,
                "author_id": action.agent_id,
                "created_at": action.timestamp,
                "views": 0,
                "shares": 0,
                "engagement_score": 0.0,
                "virality_score": 0.0
            }
        
        # Update metrics (in real system, this would come from actual engagement)
        import random
        self.content_metrics[content_id]["views"] += random.randint(10, 100)
        self.content_metrics[content_id]["shares"] += random.randint(0, 10)
        self.content_metrics[content_id]["engagement_score"] = random.uniform(0.1, 0.9)
        self.content_metrics[content_id]["virality_score"] = random.uniform(0.0, 1.0)
    
    def track_content_spread(self, content_id: str) -> Dict[str, Any]:
        """
        Track content spread
        
        Args:
            content_id: Content ID
            
        Returns:
            Virality metrics
        """
        if content_id not in self.content_metrics:
            return {}
        
        metrics = self.content_metrics[content_id]
        
        # Calculate additional metrics
        virality_metrics = {
            **metrics,
            "propagation_chain_length": len(self.propagation_chains.get(content_id, [])),
            "reach": metrics.get("views", 0),
            "viral_coefficient": metrics.get("shares", 0) / max(metrics.get("views", 1), 1)
        }
        
        return virality_metrics
    
    def analyze_viral_patterns(self) -> Dict[str, Any]:
        """
        Analyze viral propagation patterns
        
        Returns:
            Pattern analysis
        """
        if not self.viral_content:
            return {
                "total_viral": 0,
                "patterns": []
            }
        
        patterns = []
        
        for content_id in self.viral_content:
            metrics = self.content_metrics.get(content_id, {})
            patterns.append({
                "content_id": content_id,
                "virality_score": metrics.get("virality_score", 0),
                "reach": metrics.get("views", 0),
                "engagement": metrics.get("engagement_score", 0)
            })
        
        return {
            "total_viral": len(self.viral_content),
            "patterns": patterns,
            "average_virality": sum(p["virality_score"] for p in patterns) / max(len(patterns), 1)
        }
    
    def predict_virality_potential(self, content: Any) -> float:
        """
        Predict viral potential of content
        
        Args:
            content: Content to analyze
            
        Returns:
            Virality potential score (0-1)
        """
        # Mock prediction - in production would use ML model
        import random
        return random.uniform(0.3, 0.9)
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current virality metrics"""
        return {
            "total_content": len(self.content_metrics),
            "viral_content": len(self.viral_content),
            "viral_rate": len(self.viral_content) / max(len(self.content_metrics), 1)
        }
    
    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive virality report"""
        patterns = self.analyze_viral_patterns()
        
        # Calculate statistics
        all_virality_scores = [m.get("virality_score", 0) for m in self.content_metrics.values()]
        avg_virality = sum(all_virality_scores) / max(len(all_virality_scores), 1)
        
        return {
            "total_content_tracked": len(self.content_metrics),
            "viral_content_count": len(self.viral_content),
            "viral_rate": len(self.viral_content) / max(len(self.content_metrics), 1),
            "average_virality_score": avg_virality,
            "patterns": patterns,
            "top_viral_content": self._get_top_viral_content(5)
        }
    
    def _get_top_viral_content(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top viral content"""
        sorted_content = sorted(
            [m for m in self.content_metrics.values()],
            key=lambda x: x.get("virality_score", 0),
            reverse=True
        )
        
        return sorted_content[:limit]

