"""
Simple Arena Simulation Example
Demonstrates basic Arena orchestration with agents
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Arena import ArenaManager
from Arena.config import ArenaConfig


async def main():
    """Run simple simulation"""
    
    print("=" * 80)
    print("Arena Simulation - Simple Example")
    print("=" * 80)
    print()
    
    # 1. Create configuration
    print("1. Creating Arena Configuration...")
    config = ArenaConfig(
        num_agents=10,
        agent_distribution={
            "creator": 3,
            "audience": 5,
            "brand": 1,
            "moderator": 1
        },
        simulation_duration=1,  # 1 hour for demo
        time_step_duration=60,  # 1 minute per step
        metrics_collection_interval=10
    )
    print(f"✓ Configuration created")
    print(f"  - Total agents: {config.num_agents}")
    print(f"  - Duration: {config.simulation_duration} hours")
    print()
    
    # 2. Initialize Arena
    print("2. Initializing Arena...")
    arena = ArenaManager(config)
    await arena.initialize_arena()
    print("✓ Arena initialized")
    print()
    
    # 3. Deploy agents
    print("3. Deploying Agents...")
    agent_ids = await arena.deploy_agents()
    print(f"✓ Deployed {len(agent_ids)} agents")
    for role, count in config.agent_distribution.items():
        print(f"  - {role.capitalize()}: {count} agents")
    print()
    
    # 4. Run simulation for a few steps
    print("4. Running Simulation Steps...")
    num_steps = 5
    
    for step in range(num_steps):
        print(f"\n  Step {step + 1}/{num_steps}")
        result = await arena.run_simulation_step()
        
        print(f"    ✓ Completed in {result['step_duration']:.2f}s")
        print(f"    - Agent actions: {result['agent_actions']}")
        print(f"    - Viral content: {result['viral_content_count']}")
    
    print()
    print("✓ Simulation steps completed")
    print()
    
    # 5. Get current metrics
    print("5. Collecting Metrics...")
    metrics = await arena.get_current_metrics()
    print(f"✓ Current metrics:")
    print(f"  - Time step: {metrics['time_step']}")
    print(f"  - Active agents: {metrics['active_agents']}")
    print(f"  - Viral content: {metrics['viral_metrics']['viral_content']}")
    print()
    
    # 6. Evaluate agents
    print("6. Evaluating Agent Performance...")
    evaluations = await arena.evaluate_agents()
    
    print(f"✓ Agent evaluations:")
    for agent_id, eval_data in list(evaluations.items())[:3]:  # Show first 3
        print(f"  - {agent_id}:")
        print(f"      Role: {eval_data['role']}")
        print(f"      Actions: {eval_data['total_actions']}")
        print(f"      Success rate: {eval_data['success_rate']:.2%}")
        print(f"      Avg reward: {eval_data['average_reward']:.3f}")
    print(f"  ... and {len(evaluations) - 3} more agents")
    print()
    
    # 7. Generate report
    print("7. Generating Simulation Report...")
    # Set simulation results manually for demo
    arena.simulation_results = {
        "start_time": arena.start_time.isoformat() if arena.start_time else None,
        "end_time": None,
        "duration": 0,
        "total_steps": arena.current_time_step,
        "step_results": []
    }
    
    report = await arena.generate_simulation_report()
    print(f"✓ Report generated:")
    print(f"  - Total steps: {report['simulation_info']['total_steps']}")
    
    agent_stats = report.get('agent_statistics', {})
    print(f"  - Total agents: {agent_stats.get('total_agents', 0)}")
    print(f"  - Total actions: {agent_stats.get('total_actions', 0)}")
    
    viral_report = report.get('viral_propagation', {})
    print(f"  - Viral content: {viral_report.get('viral_content_count', 0)}")
    print()
    
    # 8. Save report
    print("8. Saving Report...")
    report_path = Path("arena_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ Report saved to: {report_path}")
    print()
    
    # 9. Shutdown
    print("9. Shutting Down Arena...")
    await arena.shutdown()
    print("✓ Arena shutdown complete")
    print()
    
    print("=" * 80)
    print("Simulation Complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  - Check trace/ directory for detailed logs")
    print("  - Review arena_report.json for full results")
    print("  - Run longer simulations with more agents")
    print()


if __name__ == "__main__":
    asyncio.run(main())

