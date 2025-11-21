"""
Basic Arena Tests
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Arena import ArenaManager
from Arena.config import ArenaConfig


async def test_arena_initialization():
    """Test arena initialization"""
    print("Testing Arena initialization...")
    
    config = ArenaConfig(num_agents=5, simulation_duration=1)
    arena = ArenaManager(config)
    
    await arena.initialize_arena()
    
    assert arena.is_initialized, "Arena should be initialized"
    assert arena.agent_orchestrator is not None, "AgentOrchestrator should exist"
    assert arena.simulation_engine is not None, "SimulationEngine should exist"
    
    await arena.shutdown()
    
    print("✓ Arena initialization test passed")


async def test_agent_deployment():
    """Test agent deployment"""
    print("Testing agent deployment...")
    
    config = ArenaConfig(
        num_agents=3,
        agent_distribution={"creator": 1, "audience": 1, "moderator": 1}
    )
    arena = ArenaManager(config)
    await arena.initialize_arena()
    
    # Deploy agents
    agent_ids = await arena.deploy_agents()
    
    assert len(agent_ids) == 3, f"Should deploy 3 agents, got {len(agent_ids)}"
    assert len(arena.agents) == 3, "Arena should track 3 agents"
    
    await arena.shutdown()
    
    print("✓ Agent deployment test passed")


async def test_simulation_step():
    """Test single simulation step"""
    print("Testing simulation step...")
    
    config = ArenaConfig(num_agents=3)
    arena = ArenaManager(config)
    await arena.initialize_arena()
    await arena.deploy_agents()
    
    # Run one step
    result = await arena.run_simulation_step()
    
    assert result is not None, "Should return result"
    assert "time_step" in result, "Should have time_step"
    assert result["time_step"] == 1, "First step should be 1"
    
    await arena.shutdown()
    
    print("✓ Simulation step test passed")


async def test_metrics_collection():
    """Test metrics collection"""
    print("Testing metrics collection...")
    
    config = ArenaConfig(num_agents=3)
    arena = ArenaManager(config)
    await arena.initialize_arena()
    await arena.deploy_agents()
    
    # Run a step
    await arena.run_simulation_step()
    
    # Get metrics
    metrics = await arena.get_current_metrics()
    
    assert metrics is not None, "Should return metrics"
    assert "time_step" in metrics, "Should have time_step"
    assert "active_agents" in metrics, "Should have active_agents"
    
    await arena.shutdown()
    
    print("✓ Metrics collection test passed")


async def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("Arena Module - Basic Tests")
    print("=" * 80)
    print()
    
    await test_arena_initialization()
    await test_agent_deployment()
    await test_simulation_step()
    await test_metrics_collection()
    
    print()
    print("=" * 80)
    print("All tests passed!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(run_all_tests())

