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
        
        # 实验配置
        self.experiments = {
            "A1_scale_effects": {
                "description": "智能体数量对社交网络影响的研究",
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
                "description": "发帖频率对用户参与度和内容质量的影响",
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
                "description": "社交网络长期演化和稳定性分析",
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
        """运行单次模拟"""
        print(f"🚀 开始模拟: {params}")
        print(f"📁 输出目录: {output_dir}")
        
        # 构建命令
        cmd = [
            "python", "arena.py",
            "-n_of_agents", str(params["n_agents"]),
            "-post_per_day", str(params["posts_per_day"]),
            "-days_of_simulations", str(params["days"]),
            "-fetch_per_day", str(params["fetch_per_day"]),
            "-output", str(output_dir)
        ]
        
        # 执行命令
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.arena_path,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ 模拟成功完成，耗时: {duration:.2f}秒")
                return {
                    "success": True,
                    "duration": duration,
                    "output": result.stdout,
                    "error": result.stderr
                }
            else:
                print(f"❌ 模拟失败: {result.stderr}")
                return {
                    "success": False,
                    "duration": duration,
                    "output": result.stdout,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ 模拟超时")
            return {
                "success": False,
                "duration": 3600,
                "error": "Simulation timeout"
            }
        except Exception as e:
            print(f"🔥 执行异常: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_experiment_group(self, experiment_name):
        """运行实验组"""
        if experiment_name not in self.experiments:
            print(f"❌ 实验 {experiment_name} 不存在")
            return
        
        experiment = self.experiments[experiment_name]
        print(f"\n🧪 开始实验组: {experiment_name}")
        print(f"📄 描述: {experiment['description']}")
        print(f"🔢 参数组合数: {len(experiment['params'])}")
        print(f"🔄 重复次数: {experiment['repeat']}")
        
        # 创建实验目录
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_dir = self.results_base_path / f"{experiment_name}_{timestamp}"
        experiment_dir.mkdir(exist_ok=True)
        
        # 保存实验配置
        with open(experiment_dir / "experiment_config.json", "w") as f:
            json.dump(experiment, f, indent=2)
        
        results = []
        total_runs = len(experiment['params']) * experiment['repeat']
        current_run = 0
        
        for param_idx, params in enumerate(experiment['params']):
            for repeat_idx in range(experiment['repeat']):
                current_run += 1
                print(f"\n📊 进度: {current_run}/{total_runs}")
                print(f"🎯 参数组 {param_idx+1}, 重复 {repeat_idx+1}")
                
                # 创建本次运行的输出目录
                run_name = f"param{param_idx+1}_run{repeat_idx+1}"
                run_output_dir = experiment_dir / run_name
                
                # 运行模拟
                result = self.run_single_simulation(params, run_output_dir)
                
                # 记录结果
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
                
                # 保存中间结果
                with open(experiment_dir / "results.json", "w") as f:
                    json.dump(results, f, indent=2)
                
                # 如果失败，询问是否继续
                if not result["success"]:
                    print("⚠️  本次运行失败，是否继续？(y/n): ", end="")
                    # response = input().lower()
                    # if response != 'y':
                    #     print("🛑 实验中止")
                    #     return results
                    print("y (自动继续)")
                
                # 短暂休息，避免系统过载
                time.sleep(5)
        
        print(f"\n🎉 实验组 {experiment_name} 完成！")
        print(f"📁 结果保存在: {experiment_dir}")
        
        # 生成实验报告
        self.generate_experiment_report(experiment_dir, results)
        
        return results
    
    def generate_experiment_report(self, experiment_dir, results):
        """生成实验报告"""
        report_content = f"""# 实验报告
        
## 实验信息
- 实验时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 总运行次数: {len(results)}
- 成功次数: {sum(1 for r in results if r['result']['success'])}
- 失败次数: {sum(1 for r in results if not r['result']['success'])}

## 成功率统计
"""
        
        # 按参数组统计成功率
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
            report_content += f"\n### 参数组 {param_idx + 1}\n"
            report_content += f"- 参数: {stats['params']}\n"
            report_content += f"- 成功率: {success_rate:.1f}% ({stats['success']}/{stats['total']})\n"
        
        # 执行时间统计
        successful_runs = [r for r in results if r['result']['success']]
        if successful_runs:
            durations = [r['result']['duration'] for r in successful_runs]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            report_content += f"\n## 执行时间统计\n"
            report_content += f"- 平均执行时间: {avg_duration:.2f}秒\n"
            report_content += f"- 最短执行时间: {min_duration:.2f}秒\n"
            report_content += f"- 最长执行时间: {max_duration:.2f}秒\n"
        
        # 保存报告
        with open(experiment_dir / "report.md", "w", encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 实验报告已生成: {experiment_dir}/report.md")
    
    def run_all_experiments(self):
        """运行所有实验"""
        print("🚀 开始运行所有实验组...")
        
        for experiment_name in self.experiments.keys():
            print(f"\n{'='*60}")
            self.run_experiment_group(experiment_name)
            print("⏱️  等待10秒后开始下一个实验组...")
            time.sleep(10)
        
        print("\n🎊 所有实验完成！")
    
    def list_experiments(self):
        """列出所有可用实验"""
        print("📋 可用实验列表:")
        for name, config in self.experiments.items():
            print(f"\n🧪 {name}")
            print(f"   📄 {config['description']}")
            print(f"   🔢 参数组合: {len(config['params'])}")
            print(f"   🔄 重复次数: {config['repeat']}")
            print(f"   ⏱️  预计时间: {len(config['params']) * config['repeat'] * 2}分钟")

def main():
    """主程序"""
    print("🎯 Social Arena 实验运行器")
    print("="*50)
    
    runner = ExperimentRunner()
    
    # 检查Arena目录
    if not runner.arena_path.exists():
        print(f"❌ Arena目录不存在: {runner.arena_path}")
        return
    
    print("📋 请选择要执行的操作:")
    print("1. 查看所有实验")
    print("2. 运行单个实验组")
    print("3. 运行所有实验")
    print("4. 退出")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == "1":
        runner.list_experiments()
    
    elif choice == "2":
        runner.list_experiments()
        experiment_name = input("\n请输入实验名称: ").strip()
        runner.run_experiment_group(experiment_name)
    
    elif choice == "3":
        print("⚠️  这将运行所有实验，可能需要数小时时间")
        confirm = input("确认继续？(y/n): ").strip().lower()
        if confirm == 'y':
            runner.run_all_experiments()
    
    elif choice == "4":
        print("👋 再见！")
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()