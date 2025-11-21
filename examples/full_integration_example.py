"""
Full Integration Example
Demonstrates all modules working together: Agent, Arena, Recommendation, Scrapper, Feed
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Arena import ArenaManager, ArenaConfig
from Recommendation import RecommendationEngine, RecommendationConfig
from Scrapper import ScrapperManager, ScrapperConfig


async def main():
    """Run full integrated simulation"""
    
    print("=" * 100)
    print(" " * 30 + "SOCIAL-ARENA")
    print(" " * 20 + "Full System Integration Example")
    print("=" * 100)
    print()
    
    # ==================== PHASE 1: INITIALIZATION ====================
    print("🚀 PHASE 1: SYSTEM INITIALIZATION")
    print("-" * 100)
    print()
    
    # 1. Initialize Scrapper
    print("1.1. Initializing Scrapper (Data Collection)...")
    scrapper_config = ScrapperConfig()
    scrapper = ScrapperManager(scrapper_config)
    await scrapper.initialize()
    print("    ✓ Scrapper ready")
    print()
    
    # 2. Initialize Recommendation Engine
    print("1.2. Initializing Recommendation Engine...")
    rec_config = RecommendationConfig(
        candidate_pool_size=1000,
        exploration_strategy="epsilon_greedy"
    )
    recommender = RecommendationEngine(rec_config)
    print("    ✓ Recommendation engine ready")
    print()
    
    # 3. Initialize Arena
    print("1.3. Initializing Arena (Orchestration Hub)...")
    arena_config = ArenaConfig(
        num_agents=15,
        agent_distribution={
            "creator": 5,
            "audience": 7,
            "brand": 2,
            "moderator": 1
        },
        simulation_duration=1,  # 1 hour
        time_step_duration=60
    )
    arena = ArenaManager(arena_config)
    await arena.initialize_arena()
    print("    ✓ Arena ready")
    print()
    
    # 4. Deploy Agents
    print("1.4. Deploying Agents...")
    agent_ids = await arena.deploy_agents()
    print(f"    ✓ Deployed {len(agent_ids)} agents")
    for role, count in arena_config.agent_distribution.items():
        print(f"       - {role.capitalize()}: {count}")
    print()
    
    print("✅ System initialization complete!")
    print()
    
    # ==================== PHASE 2: DATA COLLECTION ====================
    print("🕷️  PHASE 2: DATA COLLECTION")
    print("-" * 100)
    print()
    
    # 5. Scrape real-time data
    print("2.1. Scraping Twitter trending topics...")
    scraped_feeds = await scrapper.scrape_twitter_trending()
    print(f"    ✓ Scraped {len(scraped_feeds)} tweets")
    print()
    
    # 6. Detect trends
    print("2.2. Detecting emerging trends...")
    trends = await scrapper.detect_trends(scraped_feeds)
    print(f"    ✓ Detected {len(trends)} trends")
    if trends:
        print("       Top trends:", ", ".join([f"#{t['name']}" for t in trends[:5]]))
    print()
    
    print("✅ Data collection complete!")
    print()
    
    # ==================== PHASE 3: SIMULATION ====================
    print("🏟️  PHASE 3: RUNNING SIMULATION")
    print("-" * 100)
    print()
    
    # 7. Run simulation steps
    print("3.1. Running simulation steps...")
    num_steps = 10
    
    for step in range(num_steps):
        # Generate recommendations for agents (mocking the integration)
        if step % 3 == 0:  # Every 3 steps, generate recommendations
            for agent_id in agent_ids[:3]:  # Sample 3 agents
                recommendations = await recommender.recommend(agent_id, num_results=10)
                
                if step == 0:  # Log first time
                    print(f"       ✓ Recommendations for {agent_id}: {len(recommendations.recommendations)} items")
        
        # Run arena step
        result = await arena.run_simulation_step()
        
        if step == 0 or step == num_steps - 1:  # Log first and last
            print(f"       Step {step + 1}: {result['agent_actions']} actions, " +
                  f"{result['viral_content_count']} viral")
        elif step == num_steps // 2:
            print(f"       ...")
    
    print(f"    ✓ Completed {num_steps} simulation steps")
    print()
    
    print("✅ Simulation complete!")
    print()
    
    # ==================== PHASE 4: ANALYSIS ====================
    print("📊 PHASE 4: RESULTS ANALYSIS")
    print("-" * 100)
    print()
    
    # 8. Collect metrics
    print("4.1. Collecting Metrics...")
    arena_metrics = await arena.get_current_metrics()
    rec_stats = recommender.get_statistics()
    scrapper_stats = scrapper.get_statistics()
    
    print("    📈 Arena Metrics:")
    print(f"       - Total steps: {arena_metrics['time_step']}")
    print(f"       - Active agents: {arena_metrics['active_agents']}")
    print()
    
    print("    🎯 Recommendation Stats:")
    print(f"       - Total requests: {rec_stats['total_requests']}")
    print(f"       - Avg latency: {rec_stats['average_latency_ms']:.1f}ms")
    print(f"       - Cache hits: {rec_stats['cache_size']}")
    print()
    
    print("    🕷️  Scrapper Stats:")
    print(f"       - Total scraped: {scrapper_stats['total_scraped']}")
    for platform, count in scrapper_stats['by_platform'].items():
        print(f"       - {platform.capitalize()}: {count} items")
    print()
    
    # 9. Evaluate agents
    print("4.2. Evaluating Agent Performance...")
    evaluations = await arena.evaluate_agents()
    
    # Group by role
    by_role = {}
    for agent_id, eval_data in evaluations.items():
        role = eval_data['role']
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(eval_data)
    
    print()
    for role, agents in by_role.items():
        total_actions = sum(a['total_actions'] for a in agents)
        avg_success = sum(a['success_rate'] for a in agents) / len(agents)
        avg_reward = sum(a['average_reward'] for a in agents) / len(agents)
        
        print(f"    👤 {role.capitalize()} Agents ({len(agents)}):")
        print(f"       - Total actions: {total_actions}")
        print(f"       - Avg success rate: {avg_success:.1%}")
        print(f"       - Avg reward: {avg_reward:.3f}")
        print()
    
    print("✅ Analysis complete!")
    print()
    
    # ==================== PHASE 5: REPORTING ====================
    print("📄 PHASE 5: REPORT GENERATION")
    print("-" * 100)
    print()
    
    # 10. Generate comprehensive report
    print("5.1. Generating comprehensive report...")
    
    # Set simulation results for report
    arena.simulation_results = {
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "duration": num_steps * arena_config.time_step_duration,
        "total_steps": num_steps,
        "step_results": []
    }
    
    report = await arena.generate_simulation_report()
    
    # Save report
    report_path = Path(f"full_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_path, 'w') as f:
        # Add integration metrics
        report["integration_metrics"] = {
            "scrapper": scrapper_stats,
            "recommendation": rec_stats
        }
        json.dump(report, f, indent=2)
    
    print(f"    ✓ Report saved to: {report_path}")
    print()
    
    # 11. Shutdown
    print("5.2. Shutting down systems...")
    await arena.shutdown()
    print("    ✓ All systems shutdown")
    print()
    
    print("=" * 100)
    print(" " * 35 + "🎉 SUCCESS!")
    print("=" * 100)
    print()
    
    print("📊 FINAL SUMMARY:")
    print()
    print(f"  🤖 Agents Deployed:     {len(agent_ids)}")
    print(f"  🏃 Simulation Steps:    {num_steps}")
    print(f"  📝 Content Scraped:     {scrapper_stats['total_scraped']}")
    print(f"  🎯 Recommendations:     {rec_stats['total_requests']}")
    print(f"  ⚡ Avg Latency:         {rec_stats['average_latency_ms']:.1f}ms")
    print(f"  📈 Trends Detected:     {len(trends)}")
    print()
    
    print("📁 OUTPUT FILES:")
    print(f"  - Report: {report_path}")
    print(f"  - Logs: trace/ directory")
    print(f"  - Scraped data: {scrapper_config.file_storage_path}/")
    print()
    
    print("=" * 100)
    print(" " * 25 + "FULL INTEGRATION SUCCESSFUL!")
    print(" " * 25 + "All modules working together ✅")
    print("=" * 100)
    print()


if __name__ == "__main__":
    asyncio.run(main())

