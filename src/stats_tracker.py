#!/usr/bin/env python3
"""
Migration Statistics Tracker

Tracks Python 2 to 3 migration progress over time with detailed analytics.
Provides insights into migration status, trends, and bottlenecks.
"""

import datetime
import json
import os
from collections import defaultdict
from pathlib import Path


class MigrationStatsTracker:
    """Track and analyze migration statistics over time."""
    
    STATS_DIR = '.py2to3-stats'
    
    def __init__(self, project_path='.'):
        """Initialize the stats tracker.
        
        Args:
            project_path: Path to the project being tracked
        """
        self.project_path = Path(project_path).resolve()
        self.stats_dir = self.project_path / self.STATS_DIR
        
    def collect_stats(self, scan_path=None):
        """Collect current migration statistics.
        
        Args:
            scan_path: Path to scan (defaults to project_path)
            
        Returns:
            dict: Statistics dictionary
        """
        from verifier import Python3CompatibilityVerifier
        
        scan_path = scan_path or self.project_path
        verifier = Python3CompatibilityVerifier()
        
        # Collect issues
        if os.path.isdir(scan_path):
            verifier.verify_directory(scan_path)
        else:
            verifier.verify_file(scan_path)
        
        issues = verifier.issues_found
        
        # Collect file statistics
        python_files = []
        for root, dirs, files in os.walk(scan_path):
            # Skip hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Analyze issues
        files_with_issues = set()
        issue_types = defaultdict(int)
        severity_counts = defaultdict(int)
        file_issue_counts = defaultdict(int)
        
        for issue in issues:
            file_path = issue.get('file', '')
            files_with_issues.add(file_path)
            
            issue_type = issue.get('type', 'unknown')
            issue_types[issue_type] += 1
            
            severity = issue.get('severity', 'unknown')
            severity_counts[severity] += 1
            
            file_issue_counts[file_path] += 1
        
        # Calculate statistics
        total_files = len(python_files)
        files_with_issues_count = len(files_with_issues)
        clean_files = total_files - files_with_issues_count
        
        progress_pct = (clean_files / total_files * 100) if total_files > 0 else 0
        
        # Find most problematic files
        top_problematic = sorted(
            file_issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        stats = {
            'timestamp': datetime.datetime.now().isoformat(),
            'scan_path': str(scan_path),
            'summary': {
                'total_files': total_files,
                'clean_files': clean_files,
                'files_with_issues': files_with_issues_count,
                'total_issues': len(issues),
                'progress_percentage': round(progress_pct, 2)
            },
            'issues_by_type': dict(issue_types),
            'issues_by_severity': dict(severity_counts),
            'top_problematic_files': [
                {'file': f, 'issues': c} for f, c in top_problematic
            ]
        }
        
        return stats
    
    def save_snapshot(self, stats):
        """Save a statistics snapshot.
        
        Args:
            stats: Statistics dictionary to save
            
        Returns:
            str: Path to saved snapshot
        """
        self.stats_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_file = self.stats_dir / f'snapshot_{timestamp}.json'
        
        with open(snapshot_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Also save as latest
        latest_file = self.stats_dir / 'latest.json'
        with open(latest_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return str(snapshot_file)
    
    def get_snapshots(self):
        """Get all saved snapshots sorted by timestamp.
        
        Returns:
            list: List of snapshot file paths
        """
        if not self.stats_dir.exists():
            return []
        
        snapshots = sorted(
            [f for f in self.stats_dir.glob('snapshot_*.json')],
            key=lambda x: x.name
        )
        return snapshots
    
    def load_snapshot(self, snapshot_path):
        """Load a snapshot file.
        
        Args:
            snapshot_path: Path to snapshot file
            
        Returns:
            dict: Statistics dictionary
        """
        with open(snapshot_path, 'r') as f:
            return json.load(f)
    
    def get_latest_snapshot(self):
        """Get the most recent snapshot.
        
        Returns:
            dict or None: Latest statistics or None if no snapshots exist
        """
        latest_file = self.stats_dir / 'latest.json'
        if latest_file.exists():
            return self.load_snapshot(latest_file)
        return None
    
    def compare_snapshots(self, old_stats, new_stats):
        """Compare two statistics snapshots.
        
        Args:
            old_stats: Older statistics dictionary
            new_stats: Newer statistics dictionary
            
        Returns:
            dict: Comparison results
        """
        old_summary = old_stats['summary']
        new_summary = new_stats['summary']
        
        comparison = {
            'total_files': {
                'old': old_summary['total_files'],
                'new': new_summary['total_files'],
                'change': new_summary['total_files'] - old_summary['total_files']
            },
            'clean_files': {
                'old': old_summary['clean_files'],
                'new': new_summary['clean_files'],
                'change': new_summary['clean_files'] - old_summary['clean_files']
            },
            'files_with_issues': {
                'old': old_summary['files_with_issues'],
                'new': new_summary['files_with_issues'],
                'change': new_summary['files_with_issues'] - old_summary['files_with_issues']
            },
            'total_issues': {
                'old': old_summary['total_issues'],
                'new': new_summary['total_issues'],
                'change': new_summary['total_issues'] - old_summary['total_issues']
            },
            'progress_percentage': {
                'old': old_summary['progress_percentage'],
                'new': new_summary['progress_percentage'],
                'change': round(new_summary['progress_percentage'] - old_summary['progress_percentage'], 2)
            },
            'old_timestamp': old_stats['timestamp'],
            'new_timestamp': new_stats['timestamp']
        }
        
        return comparison
    
    def format_stats(self, stats, comparison=None):
        """Format statistics for display.
        
        Args:
            stats: Statistics dictionary
            comparison: Optional comparison results
            
        Returns:
            str: Formatted statistics string
        """
        lines = []
        summary = stats['summary']
        
        # Summary section
        lines.append('Migration Progress Summary')
        lines.append('=' * 50)
        lines.append(f"Scan Path: {stats['scan_path']}")
        lines.append(f"Timestamp: {stats['timestamp']}")
        lines.append('')
        
        # Overall progress
        lines.append('Overall Progress:')
        lines.append(f"  Total Python Files: {summary['total_files']}")
        lines.append(f"  Clean Files: {summary['clean_files']}")
        lines.append(f"  Files with Issues: {summary['files_with_issues']}")
        lines.append(f"  Total Issues: {summary['total_issues']}")
        lines.append(f"  Progress: {summary['progress_percentage']:.2f}%")
        lines.append('')
        
        # Show comparison if available
        if comparison:
            lines.append('Changes Since Last Scan:')
            lines.append(f"  Total Files: {self._format_change(comparison['total_files']['change'])}")
            lines.append(f"  Clean Files: {self._format_change(comparison['clean_files']['change'])}")
            lines.append(f"  Files with Issues: {self._format_change(comparison['files_with_issues']['change'])}")
            lines.append(f"  Total Issues: {self._format_change(comparison['total_issues']['change'])}")
            lines.append(f"  Progress: {self._format_change(comparison['progress_percentage']['change'])}%")
            lines.append('')
        
        # Issues by severity
        if stats.get('issues_by_severity'):
            lines.append('Issues by Severity:')
            for severity, count in sorted(stats['issues_by_severity'].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {severity}: {count}")
            lines.append('')
        
        # Issues by type
        if stats.get('issues_by_type'):
            lines.append('Top Issue Types:')
            sorted_types = sorted(stats['issues_by_type'].items(), key=lambda x: x[1], reverse=True)[:10]
            for issue_type, count in sorted_types:
                lines.append(f"  {issue_type}: {count}")
            lines.append('')
        
        # Most problematic files
        if stats.get('top_problematic_files'):
            lines.append('Most Problematic Files:')
            for item in stats['top_problematic_files'][:5]:
                file_path = item['file']
                # Shorten path if too long
                if len(file_path) > 60:
                    file_path = '...' + file_path[-57:]
                lines.append(f"  {file_path}: {item['issues']} issues")
            lines.append('')
        
        return '\n'.join(lines)
    
    def _format_change(self, value):
        """Format a change value with +/- sign.
        
        Args:
            value: Numeric change value
            
        Returns:
            str: Formatted change string
        """
        if value > 0:
            return f"+{value}"
        elif value < 0:
            return str(value)
        else:
            return "0"
    
    def generate_trend_report(self):
        """Generate a trend report from all snapshots.
        
        Returns:
            dict: Trend analysis
        """
        snapshots = self.get_snapshots()
        
        if len(snapshots) < 2:
            return None
        
        # Load all snapshots
        snapshot_data = [self.load_snapshot(s) for s in snapshots]
        
        # Extract key metrics over time
        timeline = []
        for data in snapshot_data:
            summary = data['summary']
            timeline.append({
                'timestamp': data['timestamp'],
                'total_files': summary['total_files'],
                'clean_files': summary['clean_files'],
                'total_issues': summary['total_issues'],
                'progress_percentage': summary['progress_percentage']
            })
        
        # Calculate overall trend
        first = timeline[0]
        last = timeline[-1]
        
        trend = {
            'snapshots_count': len(timeline),
            'first_scan': first['timestamp'],
            'latest_scan': last['timestamp'],
            'total_progress': round(last['progress_percentage'] - first['progress_percentage'], 2),
            'issues_resolved': first['total_issues'] - last['total_issues'],
            'timeline': timeline
        }
        
        return trend
