#!/usr/bin/env python3
"""
Simple Web Visualization for Social Arena Results
Interactive dashboard for analyzing social media simulation data
"""

import json
import os
from flask import Flask, render_template_string, jsonify
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import pandas as pd
import networkx as nx
from collections import Counter
from datetime import datetime

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Social Arena - 数据分析仪表板</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5; 
        }
        .header { 
            text-align: center; 
            color: #2E86AB; 
            margin-bottom: 30px; 
        }
        .tab-container {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            margin: 0 5px;
            background-color: #ddd;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        .tab.active {
            background-color: #2E86AB;
            color: white;
        }
        .content {
            display: none;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .content.active {
            display: block;
        }
        .chart-container {
            width: 100%;
            height: 500px;
            margin: 20px 0;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 Social Arena 数据分析仪表板</h1>
        <p>数据加载时间: {{ timestamp }}</p>
    </div>

    <div class="tab-container">
        <button class="tab active" onclick="showTab('overview')">📊 总览</button>
        <button class="tab" onclick="showTab('network')">🌐 网络图</button>
        <button class="tab" onclick="showTab('timeline')">📈 时间线</button>
        <button class="tab" onclick="showTab('content')">📝 内容分析</button>
    </div>

    <div id="overview" class="content active">
        <h2>📊 数据总览</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_agents }}</div>
                <div class="stat-label">智能体数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_feeds }}</div>
                <div class="stat-label">总推文数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.simulation_days }}</div>
                <div class="stat-label">模拟天数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_interactions }}</div>
                <div class="stat-label">总互动次数</div>
            </div>
        </div>
        
        <h3>📈 基础统计图表</h3>
        <div id="overview-chart" class="chart-container"></div>
    </div>

    <div id="network" class="content">
        <h2>🌐 社交网络图</h2>
        <p>📍 显示智能体之间的关注关系和社交网络结构</p>
        <div id="network-chart" class="chart-container"></div>
    </div>

    <div id="timeline" class="content">
        <h2>📈 活动时间线</h2>
        <p>📍 追踪智能体活动指标随时间的变化</p>
        <div id="timeline-chart" class="chart-container"></div>
    </div>

    <div id="content" class="content">
        <h2>📝 内容分析</h2>
        <p>📍 分析推文内容特征和话题分布</p>
        <div id="content-chart" class="chart-container"></div>
    </div>

    <script>
        // 切换选项卡
        function showTab(tabName) {
            // 隐藏所有内容
            var contents = document.getElementsByClassName('content');
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            
            // 移除所有选项卡的active类
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // 显示选中的内容
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // 加载对应的图表
            loadChart(tabName);
        }
        
        // 加载图表数据
        function loadChart(chartType) {
            fetch('/api/chart/' + chartType)
                .then(response => response.json())
                .then(data => {
                    var targetDiv = chartType + '-chart';
                    if (chartType === 'overview') {
                        targetDiv = 'overview-chart';
                    }
                    Plotly.newPlot(targetDiv, data.data, data.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error loading chart:', error);
                });
        }
        
        // 页面加载完成后显示总览图表
        document.addEventListener('DOMContentLoaded', function() {
            loadChart('overview');
        });
    </script>
</body>
</html>
"""

class SimpleAnalyzer:
    def __init__(self, results_path):
        self.results_path = results_path
        self.agents_data = {}
        self.feeds_data = []
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        # 加载推文数据
        feeds_file = os.path.join(self.results_path, "feeds", "all_feeds.json")
        if os.path.exists(feeds_file):
            with open(feeds_file, 'r', encoding='utf-8') as f:
                self.feeds_data = json.load(f)
        
        # 加载智能体数据
        agents_dir = os.path.join(self.results_path, "agents")
        if os.path.exists(agents_dir):
            for filename in os.listdir(agents_dir):
                if filename.endswith('.json'):
                    parts = filename.replace('.json', '').split('_day')
                    agent_id = parts[0]
                    day = int(parts[1])
                    
                    with open(os.path.join(agents_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if agent_id not in self.agents_data:
                            self.agents_data[agent_id] = {}
                        self.agents_data[agent_id][day] = data
    
    def get_basic_stats(self):
        """获取基础统计信息"""
        total_agents = len(self.agents_data)
        total_feeds = len(self.feeds_data)
        
        # 计算模拟天数
        max_days = 0
        total_interactions = 0
        
        for agent_data in self.agents_data.values():
            max_days = max(max_days, max(agent_data.keys()) if agent_data else 0)
            # 计算最后一天的互动数
            if agent_data:
                final_day_data = agent_data.get(max(agent_data.keys()), {})
                stats = final_day_data.get('stats', {})
                total_interactions += stats.get('followers_count', 0)
                total_interactions += stats.get('following_count', 0)
                total_interactions += stats.get('liked_tweets_count', 0)
        
        return {
            'total_agents': total_agents,
            'total_feeds': total_feeds,
            'simulation_days': max_days,
            'total_interactions': total_interactions
        }
    
    def create_overview_chart(self):
        """创建总览图表"""
        # 统计每个智能体的发帖数量
        author_counts = Counter(feed['author_id'] for feed in self.feeds_data)
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(author_counts.keys()),
                y=list(author_counts.values()),
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title='各智能体发帖数量统计',
            xaxis_title='智能体ID',
            yaxis_title='发帖数量',
            showlegend=False
        )
        
        return fig
    
    def create_network_chart(self):
        """Create network chart"""
        G = nx.Graph()
        
        # Add nodes and edges
        for agent_id, days_data in self.agents_data.items():
            if days_data:
                final_day = max(days_data.keys())
                agent_data = days_data[final_day]
                
                G.add_node(agent_id, 
                          followers=agent_data.get('stats', {}).get('followers_count', 0),
                          username=agent_data.get('username', agent_id))
                
                # 添加关注关系
                following_list = agent_data.get('following', [])
                for followed in following_list:
                    if followed in self.agents_data:
                        G.add_edge(agent_id, followed)
        
        # 生成布局
        if len(G.nodes()) > 0:
            pos = nx.spring_layout(G, k=1, iterations=50)
        else:
            pos = {}
        
        # 创建边的轨迹
        edge_x, edge_y = [], []
        for edge in G.edges():
            if edge[0] in pos and edge[1] in pos:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        # 创建节点的轨迹
        node_x, node_y, node_text = [], [], []
        for node in G.nodes():
            if node in pos:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_info = G.nodes[node]
                node_text.append(f"{node}<br>Followers: {node_info.get('followers', 0)}")
        
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y,
                                line=dict(width=1, color='lightgray'),
                                hoverinfo='none',
                                mode='lines',
                                showlegend=False))
        
        # Add nodes
        fig.add_trace(go.Scatter(x=node_x, y=node_y,
                                mode='markers+text',
                                marker=dict(size=15, color='lightblue'),
                                text=[node.split('_')[-1] for node in G.nodes() if node in pos],
                                textposition='middle center',
                                hovertext=node_text,
                                showlegend=False))
        
        fig.update_layout(
            title='Social Network Graph',
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return fig
    
    def create_timeline_chart(self):
        """创建时间线图表"""
        timeline_data = []
        
        for agent_id, days_data in self.agents_data.items():
            for day, data in days_data.items():
                if day > 0:  # 跳过初始状态
                    stats = data.get('stats', {})
                    timeline_data.append({
                        'agent': agent_id,
                        'day': day,
                        'followers': stats.get('followers_count', 0),
                        'following': stats.get('following_count', 0),
                        'likes': stats.get('liked_tweets_count', 0)
                    })
        
        if not timeline_data:
            # 返回空图表
            fig = go.Figure()
            fig.add_annotation(text="暂无时间线数据", x=0.5, y=0.5)
            return fig
        
        df = pd.DataFrame(timeline_data)
        
        fig = go.Figure()
        
        # 为每个智能体添加轨迹
        for agent in df['agent'].unique():
            agent_df = df[df['agent'] == agent]
            fig.add_trace(go.Scatter(
                x=agent_df['day'],
                y=agent_df['followers'],
                mode='lines+markers',
                name=agent,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title='智能体粉丝数量时间变化',
            xaxis_title='模拟天数',
            yaxis_title='粉丝数量',
            hovermode='x'
        )
        
        return fig
    
    def create_content_chart(self):
        """创建内容分析图表"""
        if not self.feeds_data:
            fig = go.Figure()
            fig.add_annotation(text="暂无内容数据", x=0.5, y=0.5)
            return fig
        
        # 分析推文长度分布
        lengths = [len(feed['text']) for feed in self.feeds_data]
        
        fig = go.Figure(data=[
            go.Histogram(x=lengths, nbinsx=20, marker_color='lightcoral')
        ])
        
        fig.update_layout(
            title='推文长度分布',
            xaxis_title='推文字符数',
            yaxis_title='频次',
            showlegend=False
        )
        
        return fig

# 初始化分析器
analyzer = SimpleAnalyzer("simulation_results_20251202")

@app.route('/')
def index():
    """主页"""
    stats = analyzer.get_basic_stats()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template_string(HTML_TEMPLATE, stats=stats, timestamp=timestamp)

@app.route('/api/chart/<chart_type>')
def get_chart(chart_type):
    """获取图表数据"""
    if chart_type == 'overview':
        fig = analyzer.create_overview_chart()
    elif chart_type == 'network':
        fig = analyzer.create_network_chart()
    elif chart_type == 'timeline':
        fig = analyzer.create_timeline_chart()
    elif chart_type == 'content':
        fig = analyzer.create_content_chart()
    else:
        return jsonify({'error': 'Unknown chart type'})
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)

if __name__ == '__main__':
    print("🚀 启动 Social Arena Web 可视化仪表板...")
    print("📱 请在浏览器中访问: http://localhost:5000")
    print("🛑 按 Ctrl+C 停止服务器")
    
    app.run(debug=True, host='localhost', port=5000)