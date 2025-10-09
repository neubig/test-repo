#!/usr/bin/env python3
"""
Migration Story Generator

Creates a narrative-style HTML report documenting the entire Python 2 to 3
migration journey. Perfect for team communication, stakeholder presentations,
and knowledge sharing.

Unlike technical reports that focus on metrics, this generates a story about
the migration - the challenges faced, victories achieved, lessons learned, and
the journey from start to finish.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import subprocess


class MigrationStoryGenerator:
    """Generates narrative-style migration story reports."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.data = {
            'timeline': [],
            'stats': {},
            'challenges': [],
            'victories': [],
            'team': {},
            'code_examples': [],
            'lessons': []
        }
        
    def collect_data(self) -> None:
        """Collect data from various sources."""
        print("📚 Collecting migration story data...")
        
        self._collect_git_history()
        self._collect_journal_entries()
        self._collect_stats()
        self._collect_backup_info()
        self._analyze_code_changes()
        
    def _collect_git_history(self) -> None:
        """Extract migration milestones from git history."""
        try:
            # Get git log with commits related to migration
            result = subprocess.run(
                ['git', 'log', '--all', '--pretty=format:%H|%an|%ae|%at|%s', '--grep=py2to3\\|python.*3\\|migration\\|fix.*python', '-i'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 4)
                        if len(parts) == 5:
                            commit_hash, author, email, timestamp, message = parts
                            self.data['timeline'].append({
                                'type': 'commit',
                                'timestamp': int(timestamp),
                                'author': author,
                                'message': message,
                                'hash': commit_hash[:8]
                            })
                            
                            # Track team contributions
                            if author not in self.data['team']:
                                self.data['team'][author] = {
                                    'commits': 0,
                                    'email': email
                                }
                            self.data['team'][author]['commits'] += 1
                            
        except Exception as e:
            print(f"   Note: Could not collect git history: {e}")
    
    def _collect_journal_entries(self) -> None:
        """Collect entries from migration journal."""
        journal_path = self.project_root / '.migration_journal'
        if journal_path.exists():
            try:
                with open(journal_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                self.data['timeline'].append({
                                    'type': 'journal',
                                    'timestamp': entry.get('timestamp', 0),
                                    'action': entry.get('action', 'unknown'),
                                    'details': entry.get('details', {})
                                })
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                print(f"   Note: Could not read journal: {e}")
    
    def _collect_stats(self) -> None:
        """Collect migration statistics."""
        stats_dir = self.project_root / '.migration_stats'
        if stats_dir.exists():
            snapshot_files = sorted(stats_dir.glob('snapshot_*.json'))
            if snapshot_files:
                try:
                    # Get first and last snapshots
                    with open(snapshot_files[0], 'r') as f:
                        self.data['stats']['initial'] = json.load(f)
                    with open(snapshot_files[-1], 'r') as f:
                        self.data['stats']['final'] = json.load(f)
                    
                    # Calculate improvements
                    if 'initial' in self.data['stats'] and 'final' in self.data['stats']:
                        initial_issues = self.data['stats']['initial'].get('total_issues', 0)
                        final_issues = self.data['stats']['final'].get('total_issues', 0)
                        self.data['stats']['improvement'] = {
                            'issues_fixed': initial_issues - final_issues,
                            'percentage': ((initial_issues - final_issues) / initial_issues * 100) if initial_issues > 0 else 0
                        }
                except Exception as e:
                    print(f"   Note: Could not process stats: {e}")
    
    def _collect_backup_info(self) -> None:
        """Analyze backup history."""
        backup_dir = self.project_root / 'backups'
        if backup_dir.exists():
            backups = list(backup_dir.glob('backup_*'))
            self.data['stats']['backups_created'] = len(backups)
    
    def _analyze_code_changes(self) -> None:
        """Extract interesting before/after code examples."""
        # Look for common migration patterns in git history
        patterns = [
            ('print statement', r'print\s+["\']', 'Modernized print statements'),
            ('except syntax', r'except\s+\w+\s*,\s*\w+:', 'Updated exception handling'),
            ('imports', r'import\s+(urllib2|ConfigParser|Queue)', 'Updated imports'),
            ('iterators', r'\.(iteritems|iterkeys|itervalues)\(', 'Modernized iterators'),
        ]
        
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--unified=3'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse diff for interesting changes
                # (Simplified - in production would parse properly)
                pass
        except:
            pass
    
    def generate_story(self, output_path: str = 'migration_story.html') -> None:
        """Generate the migration story HTML report."""
        print(f"✍️  Writing migration story to {output_path}...")
        
        # Sort timeline
        self.data['timeline'].sort(key=lambda x: x.get('timestamp', 0))
        
        html = self._generate_html()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Migration story generated: {output_path}")
        print(f"   Open it in your browser to view the journey!")
    
    def _generate_html(self) -> str:
        """Generate the HTML content."""
        project_name = os.path.basename(os.path.abspath(self.project_root))
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Story - {project_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}
        
        .hero h1 {{
            font-size: 3em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .hero .subtitle {{
            font-size: 1.3em;
            opacity: 0.95;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            font-size: 2em;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 40px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(to bottom, #667eea, #764ba2);
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -36px;
            top: 25px;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: #667eea;
            border: 3px solid white;
            box-shadow: 0 0 0 3px #667eea;
        }}
        
        .timeline-item .date {{
            color: #764ba2;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .timeline-item .author {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .team-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .team-member {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #667eea;
        }}
        
        .team-member .name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .team-member .contributions {{
            color: #667eea;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 5px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .highlight-box h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-right: 10px;
        }}
        
        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-fill {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>🚀 {project_name}</h1>
            <div class="subtitle">Our Python 2 → 3 Migration Journey</div>
            <p style="margin-top: 20px; opacity: 0.9;">
                A story of transformation, challenges overcome, and lessons learned
            </p>
        </div>
        
        <div class="content">
            {self._generate_overview_section()}
            {self._generate_stats_section()}
            {self._generate_journey_section()}
            {self._generate_team_section()}
            {self._generate_lessons_section()}
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p style="margin-top: 10px;">
                <em>Created with ❤️ by the py2to3 Migration Toolkit</em>
            </p>
        </div>
    </div>
</body>
</html>'''
    
    def _generate_overview_section(self) -> str:
        """Generate the overview section."""
        return '''
        <div class="section">
            <h2>📖 The Story</h2>
            <p style="font-size: 1.1em; line-height: 1.8;">
                This document tells the story of our migration from Python 2 to Python 3.
                It's not just about the code changes—it's about the journey, the team effort,
                the challenges we faced, and the victories we celebrated along the way.
            </p>
            
            <div class="highlight-box">
                <h3>Why We Migrated</h3>
                <p>
                    Python 2 reached end-of-life on January 1, 2020. This migration ensures our
                    codebase remains secure, maintainable, and compatible with modern tools and
                    libraries. It's an investment in our future.
                </p>
            </div>
        </div>'''
    
    def _generate_stats_section(self) -> str:
        """Generate statistics section."""
        stats = self.data.get('stats', {})
        improvement = stats.get('improvement', {})
        
        issues_fixed = improvement.get('issues_fixed', 0)
        percentage = improvement.get('percentage', 0)
        timeline_events = len(self.data.get('timeline', []))
        team_size = len(self.data.get('team', {}))
        backups = stats.get('backups_created', 0)
        
        html = '''
        <div class="section">
            <h2>📊 By The Numbers</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{}</div>
                    <div class="label">Issues Fixed</div>
                </div>
                <div class="stat-card">
                    <div class="number">{}%</div>
                    <div class="label">Completion</div>
                </div>
                <div class="stat-card">
                    <div class="number">{}</div>
                    <div class="label">Team Members</div>
                </div>
                <div class="stat-card">
                    <div class="number">{}</div>
                    <div class="label">Milestones</div>
                </div>
            </div>
            '''.format(issues_fixed, round(percentage, 1), team_size, timeline_events)
        
        if percentage > 0:
            html += f'''
            <div class="highlight-box">
                <h3>🎯 Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {percentage}%">
                        {round(percentage, 1)}% Complete
                    </div>
                </div>
            </div>'''
        
        html += '</div>'
        return html
    
    def _generate_journey_section(self) -> str:
        """Generate the journey timeline section."""
        timeline = self.data.get('timeline', [])
        
        if not timeline:
            return '''
            <div class="section">
                <h2>🗺️ The Journey</h2>
                <p>The migration journey is just beginning! Check back after some migration work has been done.</p>
            </div>'''
        
        html = '''
        <div class="section">
            <h2>🗺️ The Journey</h2>
            <p style="margin-bottom: 30px;">
                Every great journey is made up of many small steps. Here's ours:
            </p>
            <div class="timeline">'''
        
        # Show up to 10 most recent events
        for event in timeline[-10:]:
            timestamp = event.get('timestamp', 0)
            date_str = datetime.fromtimestamp(timestamp).strftime('%B %d, %Y') if timestamp else 'Unknown date'
            
            if event.get('type') == 'commit':
                html += f'''
                <div class="timeline-item">
                    <div class="date">{date_str}</div>
                    <div class="author">👤 {event.get('author', 'Unknown')}</div>
                    <div><span class="badge">Commit</span> {event.get('message', '')}</div>
                    <small style="color: #999;">#{event.get('hash', '')}</small>
                </div>'''
            elif event.get('type') == 'journal':
                action = event.get('action', 'unknown')
                html += f'''
                <div class="timeline-item">
                    <div class="date">{date_str}</div>
                    <div><span class="badge">{action.title()}</span></div>
                </div>'''
        
        html += '''
            </div>
        </div>'''
        
        return html
    
    def _generate_team_section(self) -> str:
        """Generate team contributions section."""
        team = self.data.get('team', {})
        
        if not team:
            return '''
            <div class="section">
                <h2>👥 The Team</h2>
                <p>Migration team information will appear here once work begins.</p>
            </div>'''
        
        html = '''
        <div class="section">
            <h2>👥 The Team</h2>
            <p style="margin-bottom: 30px;">
                Behind every successful migration is a dedicated team. Here are the heroes who made it happen:
            </p>
            <div class="team-grid">'''
        
        for name, info in team.items():
            commits = info.get('commits', 0)
            html += f'''
            <div class="team-member">
                <div class="name">{name}</div>
                <div class="contributions">{commits}</div>
                <div style="color: #666; font-size: 0.9em;">commits</div>
            </div>'''
        
        html += '''
            </div>
            <div class="highlight-box" style="margin-top: 30px;">
                <h3>🙏 Thank You</h3>
                <p>
                    This migration was a team effort. Every commit, every code review, every bug fix
                    brought us closer to our goal. Thank you to everyone who contributed!
                </p>
            </div>
        </div>'''
        
        return html
    
    def _generate_lessons_section(self) -> str:
        """Generate lessons learned section."""
        return '''
        <div class="section">
            <h2>💡 Lessons Learned</h2>
            <p style="margin-bottom: 20px;">
                Every migration teaches us something new. Here are some key takeaways:
            </p>
            
            <div class="highlight-box">
                <h3>✅ What Worked Well</h3>
                <ul style="margin-left: 20px; line-height: 2;">
                    <li>Automated tooling significantly reduced manual effort</li>
                    <li>Comprehensive backups provided safety and confidence</li>
                    <li>Incremental migration allowed for steady progress</li>
                    <li>Regular testing caught issues early</li>
                </ul>
            </div>
            
            <div class="highlight-box">
                <h3>🎯 Best Practices</h3>
                <ul style="margin-left: 20px; line-height: 2;">
                    <li>Start with files that have fewer dependencies</li>
                    <li>Maintain comprehensive test coverage</li>
                    <li>Review automated changes before committing</li>
                    <li>Document migration patterns for team reference</li>
                    <li>Celebrate small wins to maintain momentum</li>
                </ul>
            </div>
            
            <div class="highlight-box">
                <h3>🚀 Looking Forward</h3>
                <p>
                    With Python 3, we gain access to modern language features, better performance,
                    improved standard library modules, and continued community support. This migration
                    positions our codebase for long-term success and maintainability.
                </p>
            </div>
        </div>'''


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate a narrative-style migration story report'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='migration_story.html',
        help='Output file path (default: migration_story.html)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("📚 Migration Story Generator")
    print("="*70 + "\n")
    
    generator = MigrationStoryGenerator(args.path)
    generator.collect_data()
    generator.generate_story(args.output)
    
    print(f"\n{'='*70}")
    print(f"Story generated successfully!")
    print(f"Open {args.output} in your browser to read your migration journey!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
