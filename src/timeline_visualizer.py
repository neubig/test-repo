#!/usr/bin/env python3
"""
Migration Timeline Visualizer

Creates an interactive, chronological timeline visualization of the entire
migration journey, showing key events, milestones, fixes, and progress over time.

Features:
- Interactive timeline with zoom and pan
- Event categorization (fixes, issues, milestones, rollbacks)
- Search and filter capabilities
- Export to various formats
- Integration with journal and stats data
- Team activity tracking
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys


class TimelineEvent:
    """Represents a single event in the migration timeline."""
    
    CATEGORIES = {
        'milestone': {'icon': '🎯', 'color': '#4CAF50', 'label': 'Milestone'},
        'fix': {'icon': '🔧', 'color': '#2196F3', 'label': 'Fix Applied'},
        'issue': {'icon': '⚠️', 'color': '#FF9800', 'label': 'Issue Found'},
        'rollback': {'icon': '⏪', 'color': '#F44336', 'label': 'Rollback'},
        'checkpoint': {'icon': '📍', 'color': '#9C27B0', 'label': 'Checkpoint'},
        'commit': {'icon': '📝', 'color': '#00BCD4', 'label': 'Commit'},
        'stats': {'icon': '📊', 'color': '#607D8B', 'label': 'Stats Update'},
        'export': {'icon': '📦', 'color': '#795548', 'label': 'Export'},
        'config': {'icon': '⚙️', 'color': '#3F51B5', 'label': 'Configuration'},
        'other': {'icon': '📌', 'color': '#9E9E9E', 'label': 'Other'}
    }
    
    def __init__(self, timestamp: datetime, category: str, title: str, 
                 description: str = "", metadata: Dict[str, Any] = None):
        self.timestamp = timestamp
        self.category = category if category in self.CATEGORIES else 'other'
        self.title = title
        self.description = description
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'metadata': self.metadata,
            'icon': self.CATEGORIES[self.category]['icon'],
            'color': self.CATEGORIES[self.category]['color'],
            'label': self.CATEGORIES[self.category]['label']
        }


class MigrationTimelineVisualizer:
    """Generates interactive timeline visualizations of the migration journey."""
    
    def __init__(self, project_dir: str = '.'):
        self.project_dir = Path(project_dir).resolve()
        self.migration_dir = self.project_dir / '.migration'
        self.events: List[TimelineEvent] = []
        
    def collect_events(self):
        """Collect all events from various sources."""
        print("📚 Collecting timeline events...")
        
        # Collect from journal
        self._collect_from_journal()
        
        # Collect from stats snapshots
        self._collect_from_stats()
        
        # Collect from git history
        self._collect_from_git()
        
        # Sort events by timestamp
        self.events.sort(key=lambda e: e.timestamp)
        
        print(f"✓ Collected {len(self.events)} events")
        
    def _collect_from_journal(self):
        """Collect events from migration journal."""
        journal_file = self.migration_dir / 'journal.json'
        if not journal_file.exists():
            return
            
        try:
            with open(journal_file, 'r') as f:
                journal = json.load(f)
                
            for entry in journal.get('entries', []):
                timestamp = datetime.fromisoformat(entry['timestamp'])
                operation = entry.get('operation', 'unknown')
                
                # Categorize operation
                if operation in ['fix', 'apply_fixes']:
                    category = 'fix'
                    title = f"Applied fixes to {entry.get('files_affected', 0)} file(s)"
                elif operation == 'rollback':
                    category = 'rollback'
                    title = "Rolled back changes"
                elif operation in ['checkpoint', 'backup']:
                    category = 'checkpoint'
                    title = entry.get('message', 'Created checkpoint')
                elif operation == 'export':
                    category = 'export'
                    title = "Exported migration data"
                elif operation.startswith('config'):
                    category = 'config'
                    title = entry.get('message', 'Configuration updated')
                else:
                    category = 'other'
                    title = entry.get('message', operation)
                
                event = TimelineEvent(
                    timestamp=timestamp,
                    category=category,
                    title=title,
                    description=entry.get('details', ''),
                    metadata=entry
                )
                self.events.append(event)
                
        except Exception as e:
            print(f"Warning: Could not read journal: {e}")
            
    def _collect_from_stats(self):
        """Collect milestone events from stats snapshots."""
        stats_dir = self.migration_dir / 'stats_snapshots'
        if not stats_dir.exists():
            return
            
        try:
            snapshots = sorted(stats_dir.glob('*.json'))
            
            prev_issues = None
            for snapshot_file in snapshots:
                with open(snapshot_file, 'r') as f:
                    stats = json.load(f)
                    
                timestamp = datetime.fromisoformat(stats['timestamp'])
                total_issues = stats.get('total_issues', 0)
                
                # Check for significant milestones
                if prev_issues is not None:
                    reduction = prev_issues - total_issues
                    
                    if total_issues == 0 and prev_issues > 0:
                        # Migration complete!
                        event = TimelineEvent(
                            timestamp=timestamp,
                            category='milestone',
                            title='🎉 Migration Complete!',
                            description='All Python 3 compatibility issues resolved',
                            metadata={'issues_resolved': prev_issues}
                        )
                        self.events.append(event)
                    elif reduction >= 50:
                        # Significant progress
                        event = TimelineEvent(
                            timestamp=timestamp,
                            category='milestone',
                            title=f'Major Progress: {reduction} issues resolved',
                            description=f'Issues reduced from {prev_issues} to {total_issues}',
                            metadata={'reduction': reduction}
                        )
                        self.events.append(event)
                    elif total_issues == prev_issues:
                        # Stats update with no change
                        event = TimelineEvent(
                            timestamp=timestamp,
                            category='stats',
                            title=f'Stats collected: {total_issues} issues remaining',
                            description='',
                            metadata={'total_issues': total_issues}
                        )
                        self.events.append(event)
                        
                prev_issues = total_issues
                
        except Exception as e:
            print(f"Warning: Could not read stats: {e}")
            
    def _collect_from_git(self):
        """Collect events from git history."""
        git_dir = self.project_dir / '.git'
        if not git_dir.exists():
            return
            
        try:
            import subprocess
            
            # Get commits with py2to3 in message
            result = subprocess.run(
                ['git', 'log', '--all', '--pretty=format:%H|%ai|%s|%an', '--grep=py2to3', '--grep=python.*3', '--regexp-ignore-case'],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split('|')
                    if len(parts) >= 3:
                        commit_hash = parts[0][:7]
                        timestamp = datetime.fromisoformat(parts[1].replace(' ', 'T', 1).rsplit(' ', 1)[0])
                        message = parts[2]
                        author = parts[3] if len(parts) > 3 else 'Unknown'
                        
                        event = TimelineEvent(
                            timestamp=timestamp,
                            category='commit',
                            title=f'Commit: {message}',
                            description=f'By {author}',
                            metadata={'commit': commit_hash, 'author': author}
                        )
                        self.events.append(event)
                        
        except Exception as e:
            print(f"Warning: Could not read git history: {e}")
            
    def generate_html(self, output_file: str = 'migration_timeline.html'):
        """Generate interactive HTML timeline visualization."""
        print(f"🎨 Generating timeline visualization...")
        
        if not self.events:
            print("⚠️  No events found. Timeline will be empty.")
            
        # Prepare data for template
        events_json = json.dumps([e.to_dict() for e in self.events], indent=2)
        
        # Get timeline statistics
        stats = self._calculate_stats()
        
        html_content = self._get_html_template(events_json, stats)
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        print(f"✓ Timeline saved to: {output_path.absolute()}")
        return output_path
        
    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate timeline statistics."""
        if not self.events:
            return {
                'total_events': 0,
                'date_range': 'N/A',
                'duration_days': 0,
                'categories': {}
            }
            
        # Count events by category
        categories = {}
        for event in self.events:
            categories[event.category] = categories.get(event.category, 0) + 1
            
        first_event = self.events[0].timestamp
        last_event = self.events[-1].timestamp
        duration = (last_event - first_event).days
        
        return {
            'total_events': len(self.events),
            'date_range': f"{first_event.strftime('%Y-%m-%d')} to {last_event.strftime('%Y-%m-%d')}",
            'duration_days': duration,
            'categories': categories,
            'first_event': first_event.isoformat(),
            'last_event': last_event.isoformat()
        }
        
    def _get_html_template(self, events_json: str, stats: Dict[str, Any]) -> str:
        """Generate HTML template with embedded data."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Timeline - Python 2 to 3</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .stat-card {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .controls {{
            padding: 20px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 250px;
            padding: 10px 15px;
            border: 2px solid #dee2e6;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.3s;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: 2px solid #dee2e6;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .filter-btn:hover {{
            background: #f8f9fa;
        }}
        
        .filter-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .timeline {{
            padding: 40px;
            position: relative;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 60px;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }}
        
        .timeline-event {{
            position: relative;
            margin-bottom: 30px;
            padding-left: 100px;
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .timeline-event.hidden {{
            display: none;
        }}
        
        .event-marker {{
            position: absolute;
            left: 48px;
            top: 5px;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: white;
            border: 3px solid;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            z-index: 1;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}
        
        .event-content {{
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }}
        
        .event-content:hover {{
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            transform: translateX(5px);
        }}
        
        .event-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}
        
        .event-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
            flex: 1;
        }}
        
        .event-category {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            color: white;
            margin-left: 10px;
        }}
        
        .event-time {{
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}
        
        .event-description {{
            color: #495057;
            line-height: 1.6;
        }}
        
        .event-metadata {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #dee2e6;
            font-size: 0.85em;
            color: #6c757d;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }}
        
        .empty-state-icon {{
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.5;
        }}
        
        .export-btn {{
            padding: 10px 20px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: background 0.3s;
        }}
        
        .export-btn:hover {{
            background: #218838;
        }}
        
        .footer {{
            padding: 20px 40px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .timeline::before {{
                left: 40px;
            }}
            
            .timeline-event {{
                padding-left: 80px;
            }}
            
            .event-marker {{
                left: 28px;
            }}
            
            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .filter-buttons {{
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Migration Timeline</h1>
            <p>Your Python 2 to Python 3 Migration Journey</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="value" id="total-events">{stats['total_events']}</div>
                <div class="label">Total Events</div>
            </div>
            <div class="stat-card">
                <div class="value" id="duration">{stats['duration_days']}</div>
                <div class="label">Days</div>
            </div>
            <div class="stat-card">
                <div class="value" id="date-range">{stats['date_range']}</div>
                <div class="label">Date Range</div>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" class="search-box" id="search" placeholder="🔍 Search events...">
            <div class="filter-buttons" id="filter-buttons"></div>
            <button class="export-btn" onclick="exportTimeline()">📥 Export JSON</button>
        </div>
        
        <div class="timeline" id="timeline"></div>
        
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Python 2 to 3 Migration Toolkit
        </div>
    </div>
    
    <script>
        const events = {events_json};
        const stats = {json.dumps(stats)};
        
        // Initialize timeline
        function initTimeline() {{
            const timeline = document.getElementById('timeline');
            const filterButtons = document.getElementById('filter-buttons');
            
            // Create filter buttons
            const categories = new Set(events.map(e => e.category));
            categories.forEach(category => {{
                const btn = document.createElement('button');
                btn.className = 'filter-btn active';
                btn.dataset.category = category;
                
                const sample = events.find(e => e.category === category);
                btn.innerHTML = `${{sample.icon}} ${{sample.label}}`;
                btn.onclick = () => toggleFilter(btn);
                
                filterButtons.appendChild(btn);
            }});
            
            // Render events
            renderEvents(events);
        }}
        
        function renderEvents(eventsToRender) {{
            const timeline = document.getElementById('timeline');
            timeline.innerHTML = '';
            
            if (eventsToRender.length === 0) {{
                timeline.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <h2>No events found</h2>
                        <p>Try adjusting your filters or search terms</p>
                    </div>
                `;
                return;
            }}
            
            eventsToRender.forEach(event => {{
                const eventDiv = document.createElement('div');
                eventDiv.className = 'timeline-event';
                eventDiv.dataset.category = event.category;
                
                const date = new Date(event.timestamp);
                const timeStr = date.toLocaleString();
                
                let metadataHtml = '';
                if (Object.keys(event.metadata).length > 0) {{
                    const metaItems = [];
                    for (const [key, value] of Object.entries(event.metadata)) {{
                        if (key !== 'timestamp' && key !== 'operation') {{
                            metaItems.push(`<strong>${{key}}:</strong> ${{value}}`);
                        }}
                    }}
                    if (metaItems.length > 0) {{
                        metadataHtml = `<div class="event-metadata">${{metaItems.join(' • ')}}</div>`;
                    }}
                }}
                
                eventDiv.innerHTML = `
                    <div class="event-marker" style="border-color: ${{event.color}}">
                        ${{event.icon}}
                    </div>
                    <div class="event-content">
                        <div class="event-header">
                            <div class="event-title">${{event.title}}</div>
                            <span class="event-category" style="background: ${{event.color}}">
                                ${{event.label}}
                            </span>
                        </div>
                        <div class="event-time">📅 ${{timeStr}}</div>
                        ${{event.description ? `<div class="event-description">${{event.description}}</div>` : ''}}
                        ${{metadataHtml}}
                    </div>
                `;
                
                timeline.appendChild(eventDiv);
            }});
        }}
        
        function toggleFilter(btn) {{
            btn.classList.toggle('active');
            filterEvents();
        }}
        
        function filterEvents() {{
            const activeFilters = Array.from(document.querySelectorAll('.filter-btn.active'))
                .map(btn => btn.dataset.category);
            const searchTerm = document.getElementById('search').value.toLowerCase();
            
            const filtered = events.filter(event => {{
                const matchesFilter = activeFilters.includes(event.category);
                const matchesSearch = searchTerm === '' ||
                    event.title.toLowerCase().includes(searchTerm) ||
                    event.description.toLowerCase().includes(searchTerm);
                return matchesFilter && matchesSearch;
            }});
            
            renderEvents(filtered);
        }}
        
        function exportTimeline() {{
            const data = {{
                events: events,
                stats: stats,
                exported_at: new Date().toISOString()
            }};
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'migration_timeline_export.json';
            a.click();
            URL.revokeObjectURL(url);
        }}
        
        // Event listeners
        document.getElementById('search').addEventListener('input', filterEvents);
        
        // Initialize on load
        initTimeline();
    </script>
</body>
</html>"""
        
    def export_json(self, output_file: str = 'timeline_data.json'):
        """Export timeline data as JSON."""
        data = {
            'events': [e.to_dict() for e in self.events],
            'stats': self._calculate_stats(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"✓ Timeline data exported to: {output_file}")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate an interactive timeline visualization of your migration journey'
    )
    parser.add_argument(
        'project_dir',
        nargs='?',
        default='.',
        help='Project directory (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='migration_timeline.html',
        help='Output HTML file (default: migration_timeline.html)'
    )
    parser.add_argument(
        '--json',
        help='Also export data as JSON to specified file'
    )
    
    args = parser.parse_args()
    
    print("🕐 Migration Timeline Visualizer")
    print("=" * 50)
    
    visualizer = MigrationTimelineVisualizer(args.project_dir)
    visualizer.collect_events()
    output_path = visualizer.generate_html(args.output)
    
    if args.json:
        visualizer.export_json(args.json)
    
    print("\n" + "=" * 50)
    print(f"✓ Timeline visualization complete!")
    print(f"  Open {output_path} in your browser to view")
    

if __name__ == '__main__':
    main()
