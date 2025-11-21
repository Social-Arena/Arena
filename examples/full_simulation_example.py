"""
Full Arena Simulation Example
Demonstrates complete simulation with all features
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Arena import ArenaManager
from Arena.config import ArenaConfig


async def run_full_simulation():
    """Run complete simulation"""
    
    print("=" * 80)
    print("Arena - Full Simulation Example")
    print("=" * 80)
    print()
    
    # Configuration
    config = ArenaConfig(
        num_agents=20,
        agent_distribution={
            "creator": 6,
            "audience": 10,
            "brand": 3,
            "moderator": 1
        },
        simulation_duration=2,  # 2 hours
        time_step_duration=60,  # 1 minute steps
        enable_ab_testing=True,
        enable_evolution=True
    )
    
    print(f"Configuration:")
    print(f"  - Total agents: {config.num_agents}")
    print(f"  - Duration: {config.simulation_duration} hours")
    print(f"  - Time step: {config.time_step_duration}s")
    print()
    
    # Initialize Arena
    print("Initializing Arena...")
    arena = ArenaManager(config)
    await arena.initialize_arena()
    print("✓ Arena initialized\n")
    
    # Deploy agents
    print("Deploying agents...")
    agent_ids = await arena.deploy_agents()
    print(f"✓ Deployed {len(agent_ids)} agents\n")
    
    # Run simulation
    print(f"Running simulation for {config.simulation_duration} hours...")
    print("(This may take a moment...)\n")
    
    results = await arena.run_simulation()
    
    # Display results
    print("\n" + "=" * 80)
    print("Simulation Results")
    print("=" * 80)
    print()
    
    print(f"Duration: {results['duration']:.1f} seconds")
    print(f"Total steps: {results['total_steps']}")
    print(f"Total agents: {results['total_agents']}")
    print()
    
    # Final metrics
    final_metrics = results.get('final_metrics', {})
    
    if 'virality' in final_metrics:
        viral = final_metrics['virality']
        print(f"Viral Propagation:")
        print(f"  - Total content: {viral.get('total_content_tracked', 0)}")
        print(f"  - Viral content: {viral.get('viral_content_count', 0)}")
        print(f"  - Viral rate: {viral.get('viral_rate', 0):.2%}")
        print()
    
    if 'performance' in final_metrics:
        perf = final_metrics['performance']
        summary = perf.get('summary', {})
        print(f"Performance:")
        print(f"  - Actions processed: {summary.get('total_actions_processed', 0)}")
        print(f"  - Error rate: {summary.get('error_rate', 0):.2%}")
        
        if 'latency' in perf:
            print(f"  - Avg latency: {perf['latency'].get('average_ms', 0):.1f}ms")
        print()
    
    if 'agents' in final_metrics:
        agents = final_metrics['agents']
        print(f"Agent Statistics:")
        print(f"  - Active agents: {agents.get('active_agents', 0)}")
        print(f"  - Total actions: {agents.get('total_actions', 0)}")
        print()
    
    # Save detailed report
    report_path = Path(f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Detailed report saved to: {report_path}")
    print()
    
    # Shutdown
    await arena.shutdown()
    
    print("=" * 80)
    print("Simulation Complete!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(run_full_simulation())

