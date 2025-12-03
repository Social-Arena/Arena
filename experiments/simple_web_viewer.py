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

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Social Arena - Data Analysis Dashboard</title>
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
        .feed-item {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .feed-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .feed-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .feed-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 10px;
        }
        .feed-author {
            flex: 1;
        }
        .feed-username {
            font-weight: bold;
            color: #2E86AB;
        }
        .feed-time {
            font-size: 0.85em;
            color: #666;
        }
        .feed-text {
            margin: 10px 0;
            line-height: 1.5;
            color: #333;
        }
        .feed-type-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            margin-left: 10px;
        }
        .badge-post { background: #e3f2fd; color: #1976d2; }
        .badge-reply { background: #f3e5f5; color: #7b1fa2; }
        .badge-retweet { background: #e8f5e9; color: #388e3c; }
        .feed-metrics {
            display: flex;
            gap: 20px;
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
        }
        .metric-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 Social Arena Data Analysis Dashboard</h1>
        <p>Data Load Time: {{ timestamp }}</p>
    </div>

    <div class="tab-container">
        <button class="tab active" onclick="showTab('overview')">📊 Overview</button>
        <button class="tab" onclick="showTab('feeds')">💬 Feed Stream</button>
        <button class="tab" onclick="showTab('network')">🌐 Network</button>
        <button class="tab" onclick="showTab('timeline')">📈 Timeline</button>
        <button class="tab" onclick="showTab('content')">📝 Content Analysis</button>
    </div>

    <div id="overview" class="content active">
        <h2>📊 Data Overview</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_agents }}</div>
                <div class="stat-label">Total Agents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_feeds }}</div>
                <div class="stat-label">Total Posts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.simulation_days }}</div>
                <div class="stat-label">Simulation Days</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_interactions }}</div>
                <div class="stat-label">Total Interactions</div>
            </div>
        </div>
        
        <h3>📈 Basic Statistics Charts</h3>
        <div id="overview-chart" class="chart-container"></div>
    </div>

    <div id="feeds" class="content">
        <h2>💬 Social Feed Stream</h2>
        <p>📍 Real-time view of all posts in chronological order</p>
        <div style="margin-bottom: 20px;">
            <label for="agentFilter">Filter by Agent: </label>
            <select id="agentFilter" onchange="filterFeeds()" style="padding: 5px; border-radius: 5px;">
                <option value="all">All Agents</option>
            </select>
            <span style="margin-left: 20px;">
                <label for="feedTypeFilter">Filter by Type: </label>
                <select id="feedTypeFilter" onchange="filterFeeds()" style="padding: 5px; border-radius: 5px;">
                    <option value="all">All Types</option>
                    <option value="post">Posts</option>
                    <option value="reply">Replies</option>
                    <option value="retweet">Retweets</option>
                </select>
            </span>
        </div>
        <div id="feeds-container" style="max-height: 600px; overflow-y: auto; background: #f9f9f9; padding: 15px; border-radius: 10px;"></div>
    </div>

    <div id="network" class="content">
        <h2>🌐 Social Network Graph</h2>
        <p>📍 Displays relationships and social network structure between agents</p>
        <div id="network-chart" class="chart-container"></div>
    </div>

    <div id="timeline" class="content">
        <h2>📈 Activity Timeline</h2>
        <p>📍 Tracks agent activity metrics over time</p>
        <div id="timeline-chart" class="chart-container"></div>
    </div>

    <div id="content" class="content">
        <h2>📝 Content Analysis</h2>
        <p>📍 Analyzes post content characteristics and topic distribution</p>
        <div id="content-chart" class="chart-container"></div>
    </div>

    <script>
        // Switch tabs
        function showTab(tabName) {
            // Hide all content
            var contents = document.getElementsByClassName('content');
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            
            // Remove active class from all tabs
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // Show selected content
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Load corresponding chart
            loadChart(tabName);
        }
        
        // Load chart data
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
        
        // Display overview chart after page load
        document.addEventListener('DOMContentLoaded', function() {
            loadChart('overview');
            loadAgentList();
        });
        
        // Load agent list for filter
        let allFeeds = [];
        function loadAgentList() {
            fetch('/api/agents')
                .then(response => response.json())
                .then(agents => {
                    const select = document.getElementById('agentFilter');
                    agents.forEach(agent => {
                        const option = document.createElement('option');
                        option.value = agent.id;
                        option.textContent = agent.username + ' (' + agent.id + ')';
                        select.appendChild(option);
                    });
                });
            
            // Load all feeds
            fetch('/api/feeds')
                .then(response => response.json())
                .then(feeds => {
                    allFeeds = feeds;
                    displayFeeds(feeds);
                });
        }
        
        // Display feeds
        function displayFeeds(feeds) {
            const container = document.getElementById('feeds-container');
            if (!feeds || feeds.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">No feeds available</p>';
                return;
            }
            
            let html = '';
            feeds.forEach(feed => {
                const date = new Date(feed.created_at);
                const timeStr = date.toLocaleString();
                const badgeClass = 'badge-' + feed.feed_type;
                const avatar = feed.username ? feed.username.substring(0, 2).toUpperCase() : feed.author_id.substring(6, 8);
                
                html += `
                    <div class="feed-item" data-agent="${feed.author_id}" data-type="${feed.feed_type}">
                        <div class="feed-header">
                            <div class="feed-avatar">${avatar}</div>
                            <div class="feed-author">
                                <div>
                                    <span class="feed-username">${feed.username || feed.author_id}</span>
                                    <span class="feed-type-badge ${badgeClass}">${feed.feed_type}</span>
                                </div>
                                <div class="feed-time">${timeStr}</div>
                            </div>
                        </div>
                        <div class="feed-text">${feed.text}</div>
                        <div class="feed-metrics">
                            <div class="metric-item">❤️ ${feed.public_metrics.like_count}</div>
                            <div class="metric-item">🔁 ${feed.public_metrics.retweet_count}</div>
                            <div class="metric-item">💬 ${feed.public_metrics.reply_count}</div>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
        
        // Filter feeds
        function filterFeeds() {
            const agentFilter = document.getElementById('agentFilter').value;
            const typeFilter = document.getElementById('feedTypeFilter').value;
            
            let filtered = allFeeds;
            
            if (agentFilter !== 'all') {
                filtered = filtered.filter(feed => feed.author_id === agentFilter);
            }
            
            if (typeFilter !== 'all') {
                filtered = filtered.filter(feed => feed.feed_type === typeFilter);
            }
            
            displayFeeds(filtered);
        }
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
        """Load data"""
        # Load feed data
        feeds_file = os.path.join(self.results_path, "feeds", "all_feeds.json")
        if os.path.exists(feeds_file):
            with open(feeds_file, 'r', encoding='utf-8') as f:
                self.feeds_data = json.load(f)
        
        # Load agent data
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
        """Get basic statistics"""
        total_agents = len(self.agents_data)
        total_feeds = len(self.feeds_data)
        
        # Calculate simulation days
        max_days = 0
        total_interactions = 0
        
        for agent_data in self.agents_data.values():
            max_days = max(max_days, max(agent_data.keys()) if agent_data else 0)
            # Calculate interactions on the final day
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
        """Create overview chart"""
        # Count posts by each agent
        author_counts = Counter(feed['author_id'] for feed in self.feeds_data)
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(author_counts.keys()),
                y=list(author_counts.values()),
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title='Post Count by Agent',
            xaxis_title='Agent ID',
            yaxis_title='Post Count',
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
                
                # Add following relationships
                following_list = agent_data.get('following', [])
                for followed in following_list:
                    if followed in self.agents_data:
                        G.add_edge(agent_id, followed)
        
        # Generate layout
        if len(G.nodes()) > 0:
            pos = nx.spring_layout(G, k=1, iterations=50)
        else:
            pos = {}
        
        # Create edge traces
        edge_x, edge_y = [], []
        for edge in G.edges():
            if edge[0] in pos and edge[1] in pos:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        # Create node traces
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
        """Create timeline chart"""
        timeline_data = []
        
        for agent_id, days_data in self.agents_data.items():
            for day, data in days_data.items():
                if day > 0:  # Skip initial state
                    stats = data.get('stats', {})
                    timeline_data.append({
                        'agent': agent_id,
                        'day': day,
                        'followers': stats.get('followers_count', 0),
                        'following': stats.get('following_count', 0),
                        'likes': stats.get('liked_tweets_count', 0)
                    })
        
        if not timeline_data:
            # Return empty chart
            fig = go.Figure()
            fig.add_annotation(text="No timeline data available", x=0.5, y=0.5)
            return fig
        
        df = pd.DataFrame(timeline_data)
        
        fig = go.Figure()
        
        # Add trace for each agent
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
            title='Agent Follower Count Over Time',
            xaxis_title='Simulation Days',
            yaxis_title='Follower Count',
            hovermode='x'
        )
        
        return fig
    
    def create_content_chart(self):
        """Create content analysis chart"""
        if not self.feeds_data:
            fig = go.Figure()
            fig.add_annotation(text="No content data available", x=0.5, y=0.5)
            return fig
        
        # Analyze post length distribution
        lengths = [len(feed['text']) for feed in self.feeds_data]
        
        fig = go.Figure(data=[
            go.Histogram(x=lengths, nbinsx=20, marker_color='lightcoral')
        ])
        
        fig.update_layout(
            title='Post Length Distribution',
            xaxis_title='Post Character Count',
            yaxis_title='Frequency',
            showlegend=False
        )
        
        return fig

# Initialize analyzer
analyzer = SimpleAnalyzer("cache/arena_output_20251201_191327")

@app.route('/')
def index():
    """Home page"""
    stats = analyzer.get_basic_stats()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template_string(HTML_TEMPLATE, stats=stats, timestamp=timestamp)

@app.route('/api/chart/<chart_type>')
def get_chart(chart_type):
    """Get chart data"""
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

@app.route('/api/agents')
def get_agents():
    """Get all agents info"""
    agents = []
    for agent_id, days_data in analyzer.agents_data.items():
        if days_data:
            first_day_data = days_data.get(0, {})
            agents.append({
                'id': agent_id,
                'username': first_day_data.get('username', agent_id),
                'bio': first_day_data.get('bio', '')
            })
    return jsonify(agents)

@app.route('/api/feeds')
def get_feeds():
    """Get all feeds with username"""
    feeds = []
    # Create agent username mapping
    username_map = {}
    for agent_id, days_data in analyzer.agents_data.items():
        if days_data:
            first_day_data = days_data.get(0, {})
            username_map[agent_id] = first_day_data.get('username', agent_id)
    
    # Add username to feeds and sort by time
    for feed in analyzer.feeds_data:
        feed_copy = feed.copy()
        feed_copy['username'] = username_map.get(feed['author_id'], feed['author_id'])
        feeds.append(feed_copy)
    
    # Sort by creation time (newest first)
    feeds.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(feeds)

if __name__ == '__main__':
    print("🚀 Starting Social Arena Web Visualization Dashboard...")
    print("📱 Please visit in browser: http://127.0.0.1:5001")
    print("🛑 Press Ctrl+C to stop server")
    
    app.run(debug=True, host='127.0.0.1', port=5001)