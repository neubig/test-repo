#!/usr/bin/env python3
"""
Progress Dashboard Generator

Generates an interactive HTML dashboard for visualizing Python 2 to 3 migration
progress over time with charts, trends, velocity analysis, and ETA predictions.
"""

import datetime
import json
import os
from pathlib import Path
from html import escape


class ProgressDashboard:
    """Generate interactive progress dashboard with charts and analytics."""
    
    def __init__(self, project_path='.'):
        """Initialize dashboard generator.
        
        Args:
            project_path: Path to the project
        """
        self.project_path = Path(project_path).resolve()
        
    def generate_dashboard(self, output_path='migration_dashboard.html'):
        """Generate the progress dashboard.
        
        Args:
            output_path: Path for the output HTML file
            
        Returns:
            str: Path to generated dashboard
        """
        from stats_tracker import MigrationStatsTracker
        
        tracker = MigrationStatsTracker(self.project_path)
        
        # Get all snapshots
        snapshots = tracker.get_snapshots()
        
        if not snapshots:
            # No historical data, collect current stats
            current_stats = tracker.collect_stats()
            snapshot_data = [current_stats]
        else:
            snapshot_data = [tracker.load_snapshot(s) for s in snapshots]
        
        # Calculate analytics
        analytics = self._calculate_analytics(snapshot_data)
        
        # Generate HTML
        html = self._generate_html(snapshot_data, analytics)
        
        # Write to file
        output_path = Path(output_path)
        with open(output_path, 'w') as f:
            f.write(html)
        
        return str(output_path.resolve())
    
    def _calculate_analytics(self, snapshot_data):
        """Calculate analytics from snapshot data.
        
        Args:
            snapshot_data: List of snapshot dictionaries
            
        Returns:
            dict: Analytics data
        """
        if not snapshot_data:
            return {}
        
        analytics = {
            'total_snapshots': len(snapshot_data),
            'first_snapshot': snapshot_data[0]['timestamp'],
            'latest_snapshot': snapshot_data[-1]['timestamp'],
            'velocity': None,
            'eta': None,
            'trend': 'improving'
        }
        
        if len(snapshot_data) >= 2:
            # Calculate velocity (progress per day)
            first = snapshot_data[0]
            last = snapshot_data[-1]
            
            first_time = datetime.datetime.fromisoformat(first['timestamp'])
            last_time = datetime.datetime.fromisoformat(last['timestamp'])
            time_delta = (last_time - first_time).total_seconds() / 86400  # days
            
            if time_delta > 0:
                progress_change = (
                    last['summary']['progress_percentage'] - 
                    first['summary']['progress_percentage']
                )
                analytics['velocity'] = progress_change / time_delta  # % per day
                
                # Calculate ETA
                remaining_progress = 100 - last['summary']['progress_percentage']
                if analytics['velocity'] > 0 and remaining_progress > 0:
                    days_remaining = remaining_progress / analytics['velocity']
                    eta_date = last_time + datetime.timedelta(days=days_remaining)
                    analytics['eta'] = eta_date.isoformat()
                    analytics['days_remaining'] = round(days_remaining, 1)
                
                # Determine trend
                if len(snapshot_data) >= 3:
                    recent_progress = (
                        snapshot_data[-1]['summary']['progress_percentage'] -
                        snapshot_data[-2]['summary']['progress_percentage']
                    )
                    if recent_progress > 0:
                        analytics['trend'] = 'improving'
                    elif recent_progress < 0:
                        analytics['trend'] = 'declining'
                    else:
                        analytics['trend'] = 'stable'
        
        return analytics
    
    def _generate_html(self, snapshot_data, analytics):
        """Generate HTML dashboard.
        
        Args:
            snapshot_data: List of snapshot dictionaries
            analytics: Analytics data
            
        Returns:
            str: HTML content
        """
        # Prepare chart data
        chart_data = self._prepare_chart_data(snapshot_data)
        
        # Get latest snapshot
        latest = snapshot_data[-1] if snapshot_data else {}
        summary = latest.get('summary', {})
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Progress Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .dashboard-header {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stat-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .stat-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .stat-card.info {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .stat-label {{
            font-size: 0.875rem;
            opacity: 0.9;
            margin-bottom: 0.5rem;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        
        .stat-subtitle {{
            font-size: 0.75rem;
            opacity: 0.8;
            margin-top: 0.5rem;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .chart-card h2 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        .analytics-section {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .analytics-section h2 {{
            color: #333;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }}
        
        .analytics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }}
        
        .analytics-item {{
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .analytics-item h3 {{
            color: #667eea;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .analytics-item p {{
            color: #666;
            font-size: 0.875rem;
        }}
        
        .analytics-item .value {{
            color: #333;
            font-size: 1.25rem;
            font-weight: bold;
            margin-top: 0.5rem;
        }}
        
        .trend-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-top: 0.5rem;
        }}
        
        .trend-improving {{
            background: #d4edda;
            color: #155724;
        }}
        
        .trend-stable {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .trend-declining {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 2rem;
            opacity: 0.8;
            font-size: 0.875rem;
        }}
        
        .refresh-note {{
            text-align: center;
            color: white;
            margin-top: 1rem;
            font-size: 0.875rem;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Python 2→3 Migration Dashboard</h1>
        
        <div class="dashboard-header">
            <div class="stats-grid">
                <div class="stat-card success">
                    <div class="stat-label">Migration Progress</div>
                    <div class="stat-value">{summary.get('progress_percentage', 0):.1f}%</div>
                    <div class="stat-subtitle">Overall completion</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Total Python Files</div>
                    <div class="stat-value">{summary.get('total_files', 0)}</div>
                    <div class="stat-subtitle">{summary.get('clean_files', 0)} clean, {summary.get('files_with_issues', 0)} with issues</div>
                </div>
                
                <div class="stat-card warning">
                    <div class="stat-label">Remaining Issues</div>
                    <div class="stat-value">{summary.get('total_issues', 0)}</div>
                    <div class="stat-subtitle">To be resolved</div>
                </div>
                
                <div class="stat-card info">
                    <div class="stat-label">Tracked Snapshots</div>
                    <div class="stat-value">{analytics.get('total_snapshots', 0)}</div>
                    <div class="stat-subtitle">Historical data points</div>
                </div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h2>📉 Issue Burndown Chart</h2>
                <div class="chart-container">
                    <canvas id="burndownChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h2>📈 Progress Over Time</h2>
                <div class="chart-container">
                    <canvas id="progressChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h2>📊 Issues by Type</h2>
                <div class="chart-container">
                    <canvas id="issueTypesChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h2>⚠️ Issues by Severity</h2>
                <div class="chart-container">
                    <canvas id="severityChart"></canvas>
                </div>
            </div>
        </div>
        
        {self._generate_analytics_html(analytics)}
        
        <div class="refresh-note">
            💡 Run <code>py2to3 stats collect --save</code> to update data, then <code>py2to3 dashboard</code> to refresh this dashboard
        </div>
        
        <div class="footer">
            Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Python 2 to 3 Migration Toolkit
        </div>
    </div>
    
    <script>
        // Chart.js configuration
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
        
        const chartData = {json.dumps(chart_data, indent=8)};
        
        // Burndown Chart
        new Chart(document.getElementById('burndownChart'), {{
            type: 'line',
            data: {{
                labels: chartData.labels,
                datasets: [{{
                    label: 'Remaining Issues',
                    data: chartData.issues,
                    borderColor: '#f5576c',
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Number of Issues'
                        }}
                    }}
                }}
            }}
        }});
        
        // Progress Chart
        new Chart(document.getElementById('progressChart'), {{
            type: 'line',
            data: {{
                labels: chartData.labels,
                datasets: [{{
                    label: 'Progress %',
                    data: chartData.progress,
                    borderColor: '#38ef7d',
                    backgroundColor: 'rgba(56, 239, 125, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Progress (%)'
                        }}
                    }}
                }}
            }}
        }});
        
        // Issues by Type Chart
        new Chart(document.getElementById('issueTypesChart'), {{
            type: 'doughnut',
            data: {{
                labels: chartData.issueTypes.labels,
                datasets: [{{
                    data: chartData.issueTypes.data,
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#4facfe',
                        '#38ef7d', '#f5576c', '#ffa726', '#42a5f5'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Severity Chart
        new Chart(document.getElementById('severityChart'), {{
            type: 'bar',
            data: {{
                labels: chartData.severity.labels,
                datasets: [{{
                    label: 'Count',
                    data: chartData.severity.data,
                    backgroundColor: [
                        '#f5576c', '#ffa726', '#42a5f5', '#66bb6a'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Number of Issues'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def _prepare_chart_data(self, snapshot_data):
        """Prepare data for charts.
        
        Args:
            snapshot_data: List of snapshot dictionaries
            
        Returns:
            dict: Chart data
        """
        labels = []
        issues = []
        progress = []
        
        for snapshot in snapshot_data:
            timestamp = datetime.datetime.fromisoformat(snapshot['timestamp'])
            labels.append(timestamp.strftime('%Y-%m-%d %H:%M'))
            issues.append(snapshot['summary']['total_issues'])
            progress.append(round(snapshot['summary']['progress_percentage'], 2))
        
        # Get issue types and severity from latest snapshot
        latest = snapshot_data[-1] if snapshot_data else {}
        
        issue_types_data = latest.get('issues_by_type', {})
        issue_types = {
            'labels': list(issue_types_data.keys()),
            'data': list(issue_types_data.values())
        }
        
        severity_data = latest.get('issues_by_severity', {})
        severity = {
            'labels': list(severity_data.keys()),
            'data': list(severity_data.values())
        }
        
        return {
            'labels': labels,
            'issues': issues,
            'progress': progress,
            'issueTypes': issue_types,
            'severity': severity
        }
    
    def _generate_analytics_html(self, analytics):
        """Generate analytics section HTML.
        
        Args:
            analytics: Analytics data
            
        Returns:
            str: HTML content
        """
        if not analytics or analytics.get('total_snapshots', 0) < 2:
            return '''
        <div class="analytics-section">
            <h2>📊 Migration Analytics</h2>
            <p style="color: #666;">Not enough data for trend analysis yet. Collect more snapshots over time to see velocity and ETA predictions.</p>
            <p style="color: #666; margin-top: 1rem;">Run <code>py2to3 stats collect --save</code> multiple times during your migration to build up historical data.</p>
        </div>
            '''
        
        trend_class = f"trend-{analytics.get('trend', 'stable')}"
        trend_text = analytics.get('trend', 'stable').capitalize()
        
        velocity_html = ''
        if analytics.get('velocity') is not None:
            velocity_html = f'''
            <div class="analytics-item">
                <h3>Velocity</h3>
                <p>Average progress rate</p>
                <div class="value">{analytics['velocity']:.2f}% / day</div>
            </div>
            '''
        
        eta_html = ''
        if analytics.get('eta'):
            eta_date = datetime.datetime.fromisoformat(analytics['eta'])
            days_remaining = analytics.get('days_remaining', 0)
            eta_html = f'''
            <div class="analytics-item">
                <h3>Estimated Completion</h3>
                <p>Based on current velocity</p>
                <div class="value">{eta_date.strftime('%Y-%m-%d')}</div>
                <p style="margin-top: 0.5rem; color: #666;">~{days_remaining} days remaining</p>
            </div>
            '''
        
        return f'''
        <div class="analytics-section">
            <h2>📊 Migration Analytics</h2>
            <div class="analytics-grid">
                <div class="analytics-item">
                    <h3>First Snapshot</h3>
                    <p>Migration tracking started</p>
                    <div class="value">{datetime.datetime.fromisoformat(analytics['first_snapshot']).strftime('%Y-%m-%d')}</div>
                </div>
                
                <div class="analytics-item">
                    <h3>Latest Update</h3>
                    <p>Most recent snapshot</p>
                    <div class="value">{datetime.datetime.fromisoformat(analytics['latest_snapshot']).strftime('%Y-%m-%d')}</div>
                </div>
                
                {velocity_html}
                
                {eta_html}
                
                <div class="analytics-item">
                    <h3>Trend</h3>
                    <p>Current migration trend</p>
                    <div class="trend-badge {trend_class}">{trend_text}</div>
                </div>
            </div>
        </div>
        '''


def main():
    """CLI entry point for dashboard generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate interactive progress dashboard for Python 2 to 3 migration'
    )
    parser.add_argument(
        '-o', '--output',
        default='migration_dashboard.html',
        help='Output HTML file path (default: migration_dashboard.html)'
    )
    parser.add_argument(
        '--project-path',
        default='.',
        help='Project path (default: current directory)'
    )
    
    args = parser.parse_args()
    
    dashboard = ProgressDashboard(args.project_path)
    output_file = dashboard.generate_dashboard(args.output)
    
    print(f"✓ Dashboard generated: {output_file}")
    print(f"  Open in browser: file://{output_file}")


if __name__ == '__main__':
    main()
