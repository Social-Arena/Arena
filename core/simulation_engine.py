"""
Simulation Engine - Creates realistic social media environment
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from Arena.config.arena_config import ArenaConfig
from Arena.trace_logging import get_logger


class SimulationEngine:
    """
    Simulation Engine - Creates and maintains realistic social media environment
    """
    
    def __init__(self, config: ArenaConfig):
        self.config = config
        self.logger = get_logger("simulation_engine", "simulation")
        
        # Environment state
        self.current_state: Dict[str, Any] = {}
        self.trend_momentum: Dict[str, float] = {}
        self.platform_health: float = 0.8
        
        # Trend management
        self.active_trends: List[str] = []
        self.trend_lifecycle: Dict[str, Dict[str, Any]] = {}
        
        # User session simulation
        self.active_sessions: int = 0
        
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize simulation engine"""
        if self.is_initialized:
            return
        
        self.logger.info("Initializing SimulationEngine")
        
        # Initialize with default trends
        self.active_trends = self._generate_initial_trends()
        
        # Initialize trend momentum
        for trend in self.active_trends:
            self.trend_momentum[trend] = random.uniform(0.5, 1.0)
            self.trend_lifecycle[trend] = {
                "phase": "growth",
                "start_time": datetime.now(),
                "peak_momentum": self.trend_momentum[trend]
            }
        
        # Initialize environment state
        self.current_state = await self.update_environment_state()
        
        self.is_initialized = True
        self.logger.info("SimulationEngine initialized")
    
    def _generate_initial_trends(self) -> List[str]:
        """Generate initial trending topics"""
        trend_pool = [
            "AI", "MachineLearning", "TechNews", "Innovation",
            "Startup", "Coding", "DataScience", "CloudComputing",
            "Cybersecurity", "Blockchain", "IoT", "5G",
            "SocialMedia", "DigitalMarketing", "ContentCreation"
        ]
        return random.sample(trend_pool, min(10, len(trend_pool)))
    
    async def update_environment_state(self) -> Any:
        """
        Update and return current environment state
        
        Returns:
            EnvironmentState object
        """
        # Import EnvironmentState from Agent module
        from Agent import EnvironmentState
        
        # Update trends
        self._update_trends()
        
        # Simulate audience activity
        audience_activity = self._simulate_audience_activity()
        
        # Calculate platform metrics
        platform_metrics = self._calculate_platform_metrics()
        
        # Get recommended content (mock)
        recommended_content = self._generate_recommended_content()
        
        # Get social signals
        social_signals = self._generate_social_signals()
        
        # Create environment state
        state = EnvironmentState(
            timestamp=datetime.now(),
            trending_topics=self.active_trends.copy(),
            audience_activity=audience_activity,
            platform_metrics=platform_metrics,
            recommended_content=recommended_content,
            social_signals=social_signals
        )
        
        self.current_state = state
        
        return state
    
    def _update_trends(self) -> None:
        """Update trending topics"""
        # Decay existing trends
        for trend in list(self.trend_momentum.keys()):
            # Apply decay
            self.trend_momentum[trend] *= 0.95
            
            # Update lifecycle phase
            lifecycle = self.trend_lifecycle[trend]
            age = (datetime.now() - lifecycle["start_time"]).total_seconds() / 3600  # hours
            
            if age < 2:
                lifecycle["phase"] = "emergence"
            elif age < 6:
                lifecycle["phase"] = "growth"
            elif age < 12:
                lifecycle["phase"] = "peak"
            elif age < 24:
                lifecycle["phase"] = "decline"
            else:
                lifecycle["phase"] = "tail"
            
            # Remove dead trends
            if self.trend_momentum[trend] < 0.1 or lifecycle["phase"] == "tail":
                self.active_trends.remove(trend)
                del self.trend_momentum[trend]
                del self.trend_lifecycle[trend]
                
                self.logger.debug(f"Trend died", extra={"trend": trend})
        
        # Introduce new trends occasionally
        if random.random() < 0.1 and len(self.active_trends) < 15:
            new_trend = self._generate_new_trend()
            if new_trend and new_trend not in self.active_trends:
                self.active_trends.append(new_trend)
                self.trend_momentum[new_trend] = random.uniform(0.3, 0.7)
                self.trend_lifecycle[new_trend] = {
                    "phase": "emergence",
                    "start_time": datetime.now(),
                    "peak_momentum": self.trend_momentum[new_trend]
                }
                
                self.logger.info(f"New trend emerged", extra={"trend": new_trend})
    
    def _generate_new_trend(self) -> Optional[str]:
        """Generate a new trending topic"""
        emerging_topics = [
            "BreakingNews", "TechUpdate", "Innovation2024", "NewTech",
            "TrendAlert", "ViralMoment", "MustSee", "GameChanger"
        ]
        return random.choice(emerging_topics) if emerging_topics else None
    
    async def inject_trend_shock(self, trend_data: Dict[str, Any]) -> None:
        """
        Inject a trend shock into the system
        
        Args:
            trend_data: Trend shock data with 'trend', 'intensity', 'duration'
        """
        trend = trend_data.get("trend", "ShockTrend")
        intensity = trend_data.get("intensity", 0.8)
        
        # Add trend with high momentum
        if trend not in self.active_trends:
            self.active_trends.append(trend)
        
        self.trend_momentum[trend] = intensity
        self.trend_lifecycle[trend] = {
            "phase": "shock",
            "start_time": datetime.now(),
            "peak_momentum": intensity,
            "is_shock": True
        }
        
        self.logger.warning(f"Trend shock injected", extra={
            "trend": trend,
            "intensity": intensity
        })
    
    def _simulate_audience_activity(self) -> Dict[str, Any]:
        """Simulate audience activity levels"""
        # Time-of-day based activity
        hour = datetime.now().hour
        
        # Activity peaks in evening (18-22)
        if 18 <= hour <= 22:
            base_activity = 0.8
        elif 12 <= hour <= 17:
            base_activity = 0.6
        elif 8 <= hour <= 11:
            base_activity = 0.5
        else:
            base_activity = 0.3
        
        # Add randomness
        activity = base_activity * random.uniform(0.8, 1.2)
        activity = max(0.0, min(1.0, activity))
        
        return {
            "engagement_level": activity,
            "active_users": int(1000 * activity),
            "peak_hours": 18 <= hour <= 22
        }
    
    def _calculate_platform_metrics(self) -> Dict[str, float]:
        """Calculate platform health metrics"""
        # Simulate platform metrics
        metrics = {
            "health_score": self.platform_health,
            "negative_sentiment": random.uniform(0.1, 0.3),
            "engagement": random.uniform(0.4, 0.8),
            "content_velocity": random.uniform(100, 1000)  # posts per minute
        }
        
        # Update platform health based on trends
        if self.platform_health < 0.5:
            self.platform_health += 0.01  # Slow recovery
        elif self.platform_health > 0.9:
            self.platform_health -= 0.005  # Slight decay from peak
        
        return metrics
    
    def _generate_recommended_content(self) -> List[Dict[str, Any]]:
        """Generate mock recommended content"""
        content_list = []
        
        for i in range(10):
            content_list.append({
                "id": f"content_{datetime.now().timestamp()}_{i}",
                "text": f"Sample content about {random.choice(self.active_trends) if self.active_trends else 'general topic'}",
                "topics": random.sample(self.active_trends, min(2, len(self.active_trends))) if self.active_trends else [],
                "quality_score": random.uniform(0.5, 1.0),
                "engagement_count": random.randint(10, 1000),
                "length": random.randint(50, 280)
            })
        
        return content_list
    
    def _generate_social_signals(self) -> Dict[str, Any]:
        """Generate social proof signals"""
        return {
            "friend_likes": [f"user_{i}" for i in range(random.randint(0, 5))],
            "friend_shares": [f"user_{i}" for i in range(random.randint(0, 3))],
            "friend_preferences": {
                "technology": random.uniform(0.5, 1.0),
                "lifestyle": random.uniform(0.3, 0.8)
            }
        }
    
    async def simulate_ranking_pressure(self) -> None:
        """Simulate ranking algorithm pressure"""
        # Simulate competitive pressure from ranking algorithm
        pressure_factor = random.uniform(0.7, 1.0)
        
        self.logger.debug(f"Ranking pressure applied", extra={
            "pressure_factor": pressure_factor
        })
    
    async def simulate_user_sessions(self) -> Dict[str, Any]:
        """
        Simulate user sessions
        
        Returns:
            Session data
        """
        # Simulate concurrent user sessions
        self.active_sessions = random.randint(50, 500)
        
        session_data = {
            "active_sessions": self.active_sessions,
            "average_duration": random.uniform(5, 30),  # minutes
            "engagement_rate": random.uniform(0.1, 0.4)
        }
        
        return session_data
    
    async def shutdown(self) -> None:
        """Shutdown simulation engine"""
        self.logger.info("Shutting down SimulationEngine")
        self.is_initialized = False

