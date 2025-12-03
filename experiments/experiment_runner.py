#!/usr/bin/env python3
"""
Social Arena 实验自动化运行器
Automated Experiment Runner for Social Arena
"""

import os
import json
import time
import subprocess
import datetime
from pathlib import Path
import shutil

class ExperimentRunner:
    def __init__(self, arena_path="Arena"):
        self.arena_path = Path(arena_path)
        self.results_base_path = Path("experiment_results")
        self.results_base_path.mkdir(exist_ok=True)
        
        # Experiment configuration
        self.experiments = {
            "A1_scale_effects": {
                "description": "Study of agent count impact on social networks",
                "params": [
                    {"n_agents": 5, "posts_per_day": 5, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 10, "posts_per_day": 5, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 15, "posts_per_day": 5, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 20, "posts_per_day": 5, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 25, "posts_per_day": 5, "days": 7, "fetch_per_day": 10},
                ],
                "repeat": 3
            },
            "B1_posting_frequency": {
                "description": "Impact of posting frequency on user engagement and content quality",
                "params": [
                    {"n_agents": 10, "posts_per_day": 1, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 10, "posts_per_day": 3, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 10, "posts_per_day": 5, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 10, "posts_per_day": 8, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 10, "posts_per_day": 12, "days": 7, "fetch_per_day": 10},
                ],
                "repeat": 3
            },
            "C1_temporal_evolution": {
                "description": "Long-term evolution and stability analysis of social networks",
                "params": [
                    {"n_agents": 15, "posts_per_day": 5, "days": 3, "fetch_per_day": 10},
                    {"n_agents": 15, "posts_per_day": 5, "days": 7, "fetch_per_day": 10},
                    {"n_agents": 15, "posts_per_day": 5, "days": 14, "fetch_per_day": 10},
                    {"n_agents": 15, "posts_per_day": 5, "days": 21, "fetch_per_day": 10},
                ],
                "repeat": 2
            }
        }
    
    def run_single_simulation(self, params, output_dir):
        """Run single simulation"""
        print(f"🚀 Starting simulation: {params}")
        print(f"📁 Output directory: {output_dir}")
        
        # Build command
        cmd = [
            "python", "arena.py",
            "-n_of_agents", str(params["n_agents"]),
            "-post_per_day", str(params["posts_per_day"]),
            "-days_of_simulations", str(params["days"]),
            "-fetch_per_day", str(params["fetch_per_day"]),
            "-output", str(output_dir)
        ]
        
        # Execute command
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.arena_path,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ Simulation completed successfully, duration: {duration:.2f}s")
                return {
                    "success": True,
                    "duration": duration,
                    "output": result.stdout,
                    "error": result.stderr
                }
            else:
                print(f"❌ Simulation failed: {result.stderr}")
                return {
                    "success": False,
                    "duration": duration,
                    "output": result.stdout,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ Simulation timeout")
            return {
                "success": False,
                "duration": 3600,
                "error": "Simulation timeout"
            }
        except Exception as e:
            print(f"🔥 Execution exception: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_experiment_group(self, experiment_name):
        """Run experiment group"""
        if experiment_name not in self.experiments:
            print(f"❌ Experiment {experiment_name} does not exist")
            return
        
        experiment = self.experiments[experiment_name]
        print(f"\n🧪 Starting experiment group: {experiment_name}")
        print(f"📄 Description: {experiment['description']}")
        print(f"🔢 Parameter combinations: {len(experiment['params'])}")
        print(f"🔄 Repetitions: {experiment['repeat']}")
        
        # Create experiment directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_dir = self.results_base_path / f"{experiment_name}_{timestamp}"
        experiment_dir.mkdir(exist_ok=True)
        
        # Save experiment configuration
        with open(experiment_dir / "experiment_config.json", "w") as f:
            json.dump(experiment, f, indent=2)
        
        results = []
        total_runs = len(experiment['params']) * experiment['repeat']
        current_run = 0
        
        for param_idx, params in enumerate(experiment['params']):
            for repeat_idx in range(experiment['repeat']):
                current_run += 1
                print(f"\n📊 Progress: {current_run}/{total_runs}")
                print(f"🎯 Parameter set {param_idx+1}, repetition {repeat_idx+1}")
                
                # Create output directory for this run
                run_name = f"param{param_idx+1}_run{repeat_idx+1}"
                run_output_dir = experiment_dir / run_name
                
                # Run simulation
                result = self.run_single_simulation(params, run_output_dir)
                
                # Record result
                run_result = {
                    "experiment_name": experiment_name,
                    "param_index": param_idx,
                    "repeat_index": repeat_idx,
                    "run_name": run_name,
                    "params": params,
                    "result": result,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                results.append(run_result)
                
                # Save intermediate results
                with open(experiment_dir / "results.json", "w") as f:
                    json.dump(results, f, indent=2)
                
                # If failed, ask whether to continue
                if not result["success"]:
                    print("⚠️  This run failed, continue anyway? (y/n): ", end="")
                    # response = input().lower()
                    # if response != 'y':
                    #     print("🛑 Experiment aborted")
                    #     return results
                    print("y (auto-continue)")
                
                # Brief pause to avoid system overload
                time.sleep(5)
        
        print(f"\n🎉 Experiment group {experiment_name} completed!")
        print(f"📁 Results saved in: {experiment_dir}")
        
        # Generate experiment report
        self.generate_experiment_report(experiment_dir, results)
        
        return results
    
    def generate_experiment_report(self, experiment_dir, results):
        """Generate experiment report"""
        report_content = f"""# Experiment Report
        
## Experiment Information
- Experiment time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Total runs: {len(results)}
- Successful runs: {sum(1 for r in results if r['result']['success'])}
- Failed runs: {sum(1 for r in results if not r['result']['success'])}

## Success Rate Statistics
"""
        
        # Calculate success rate by parameter group
        param_groups = {}
        for result in results:
            param_idx = result['param_index']
            if param_idx not in param_groups:
                param_groups[param_idx] = {'total': 0, 'success': 0, 'params': result['params']}
            
            param_groups[param_idx]['total'] += 1
            if result['result']['success']:
                param_groups[param_idx]['success'] += 1
        
        for param_idx, stats in param_groups.items():
            success_rate = stats['success'] / stats['total'] * 100
            report_content += f"\n### Parameter Set {param_idx + 1}\n"
            report_content += f"- Parameters: {stats['params']}\n"
            report_content += f"- Success rate: {success_rate:.1f}% ({stats['success']}/{stats['total']})\n"
        
        # Execution time statistics
        successful_runs = [r for r in results if r['result']['success']]
        if successful_runs:
            durations = [r['result']['duration'] for r in successful_runs]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            report_content += f"\n## Execution Time Statistics\n"
            report_content += f"- Average execution time: {avg_duration:.2f}s\n"
            report_content += f"- Minimum execution time: {min_duration:.2f}s\n"
            report_content += f"- Maximum execution time: {max_duration:.2f}s\n"
        
        # Save report
        with open(experiment_dir / "report.md", "w", encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 Experiment report generated: {experiment_dir}/report.md")
    
    def run_all_experiments(self):
        """Run all experiments"""
        print("🚀 Starting all experiment groups...")
        
        for experiment_name in self.experiments.keys():
            print(f"\n{'='*60}")
            self.run_experiment_group(experiment_name)
            print("⏱️  Waiting 10 seconds before starting next experiment group...")
            time.sleep(10)
        
        print("\n🎊 All experiments completed!")
    
    def list_experiments(self):
        """List all available experiments"""
        print("📋 Available experiments:")
        for name, config in self.experiments.items():
            print(f"\n🧪 {name}")
            print(f"   📄 {config['description']}")
            print(f"   🔢 Parameter combinations: {len(config['params'])}")
            print(f"   🔄 Repetitions: {config['repeat']}")
            print(f"   ⏱️  Estimated time: {len(config['params']) * config['repeat'] * 2} minutes")

def main():
    """Main program"""
    print("🎯 Social Arena Experiment Runner")
    print("="*50)
    
    runner = ExperimentRunner()
    
    # Check Arena directory
    if not runner.arena_path.exists():
        print(f"❌ Arena directory does not exist: {runner.arena_path}")
        return
    
    print("📋 Please select an operation:")
    print("1. View all experiments")
    print("2. Run single experiment group")
    print("3. Run all experiments")
    print("4. Exit")
    
    choice = input("\nPlease enter choice (1-4): ").strip()
    
    if choice == "1":
        runner.list_experiments()
    
    elif choice == "2":
        runner.list_experiments()
        experiment_name = input("\nPlease enter experiment name: ").strip()
        runner.run_experiment_group(experiment_name)
    
    elif choice == "3":
        print("⚠️  This will run all experiments, which may take several hours")
        confirm = input("Confirm to continue? (y/n): ").strip().lower()
        if confirm == 'y':
            runner.run_all_experiments()
    
    elif choice == "4":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
