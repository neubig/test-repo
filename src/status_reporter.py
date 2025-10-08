#!/usr/bin/env python3
"""
Quick Status Reporter for Python 2 to 3 Migration

Provides a comprehensive, at-a-glance view of migration state in the terminal.
Shows progress, issues, recent activity, git status, and recommendations.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class MigrationStatusReporter:
    """Generate quick status reports for migration progress."""
    
    def __init__(self, project_path='.', stats_dir='.migration_stats'):
        self.project_path = Path(project_path).resolve()
        self.stats_dir = Path(stats_dir)
        self.git_available = self._check_git_available()
        
    def _check_git_available(self):
        """Check if git is available and this is a git repository."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.project_path,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _get_latest_stats(self):
        """Get the most recent stats snapshot."""
        if not self.stats_dir.exists():
            return None
            
        snapshots = sorted(self.stats_dir.glob('snapshot_*.json'))
        if not snapshots:
            return None
            
        try:
            with open(snapshots[-1], 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _get_previous_stats(self):
        """Get the second-most recent stats snapshot for comparison."""
        if not self.stats_dir.exists():
            return None
            
        snapshots = sorted(self.stats_dir.glob('snapshot_*.json'))
        if len(snapshots) < 2:
            return None
            
        try:
            with open(snapshots[-2], 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _count_python_files(self):
        """Count Python files in the project."""
        count = 0
        for root, dirs, files in os.walk(self.project_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            count += sum(1 for f in files if f.endswith('.py'))
        return count
    
    def _get_git_status(self):
        """Get git status information."""
        if not self.git_available:
            return None
            
        try:
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown'
            
            # Get modified files count
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            modified_files = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            
            # Get last commit info
            log_result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%h - %s (%cr)'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            last_commit = log_result.stdout.strip() if log_result.returncode == 0 else 'No commits'
            
            return {
                'branch': branch,
                'modified_files': modified_files,
                'last_commit': last_commit
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def _get_backup_info(self):
        """Get backup directory information."""
        backup_dirs = ['.migration_backups', 'backups', '.backups']
        
        for backup_dir in backup_dirs:
            backup_path = self.project_path / backup_dir
            if backup_path.exists() and backup_path.is_dir():
                backup_count = len(list(backup_path.glob('*.bak')))
                if backup_count > 0:
                    return {
                        'directory': backup_dir,
                        'count': backup_count
                    }
        return None
    
    def _calculate_progress(self, stats):
        """Calculate migration progress percentage."""
        if not stats:
            return 0
        
        total_issues = stats.get('total_issues', 0)
        if total_issues == 0:
            return 100
        
        # Consider severity - critical and high are more important
        critical = stats.get('critical_issues', 0)
        high = stats.get('high_issues', 0)
        medium = stats.get('medium_issues', 0)
        low = stats.get('low_issues', 0)
        
        # Weighted calculation
        weighted_total = (critical * 4) + (high * 3) + (medium * 2) + (low * 1)
        weighted_max = total_issues * 4  # Assume all could be critical
        
        if weighted_max == 0:
            return 100
        
        progress = ((weighted_max - weighted_total) / weighted_max) * 100
        return max(0, min(100, progress))
    
    def _get_recommendations(self, stats, git_status):
        """Generate actionable recommendations based on current state."""
        recommendations = []
        
        if not stats:
            recommendations.append("Run './py2to3 check .' to analyze your code")
            recommendations.append("Run './py2to3 preflight' to verify environment readiness")
            return recommendations
        
        total_issues = stats.get('total_issues', 0)
        critical = stats.get('critical_issues', 0)
        high = stats.get('high_issues', 0)
        
        if total_issues == 0:
            recommendations.append("Migration appears complete! Run tests to verify")
            recommendations.append("Generate final report: './py2to3 report -o final_report.html'")
        elif critical > 0:
            recommendations.append(f"Address {critical} critical issue(s) first - these will break Python 3")
            recommendations.append("Run './py2to3 fix .' to apply automatic fixes")
        elif high > 0:
            recommendations.append(f"Focus on {high} high-severity issue(s)")
            recommendations.append("Use './py2to3 interactive' for guided fixing")
        else:
            recommendations.append("Review remaining low/medium issues")
            recommendations.append("Run './py2to3 test-gen' to generate migration tests")
        
        if git_status and git_status['modified_files'] > 5:
            recommendations.append(f"Commit your changes - {git_status['modified_files']} files modified")
        
        if not self._get_backup_info():
            recommendations.append("Create a backup before continuing: './py2to3 backup create'")
        
        return recommendations
    
    def generate_status_report(self):
        """Generate comprehensive status report."""
        stats = self._get_latest_stats()
        prev_stats = self._get_previous_stats()
        git_status = self._get_git_status()
        backup_info = self._get_backup_info()
        python_files = self._count_python_files()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'python_files': python_files,
            'progress': self._calculate_progress(stats),
            'stats': stats,
            'previous_stats': prev_stats,
            'git_status': git_status,
            'backup_info': backup_info,
            'recommendations': self._get_recommendations(stats, git_status)
        }
        
        return report
    
    def print_status(self, report=None, color=True):
        """Print status report to console with colors."""
        if report is None:
            report = self.generate_status_report()
        
        # Color codes
        if color:
            RESET = '\033[0m'
            BOLD = '\033[1m'
            GREEN = '\033[92m'
            YELLOW = '\033[93m'
            RED = '\033[91m'
            CYAN = '\033[96m'
            MAGENTA = '\033[95m'
            BLUE = '\033[94m'
        else:
            RESET = BOLD = GREEN = YELLOW = RED = CYAN = MAGENTA = BLUE = ''
        
        # Header
        print(f"\n{BOLD}{MAGENTA}{'=' * 70}{RESET}")
        print(f"{BOLD}{MAGENTA}{'MIGRATION STATUS REPORT':^70}{RESET}")
        print(f"{BOLD}{MAGENTA}{'=' * 70}{RESET}\n")
        
        # Project Info
        print(f"{BOLD}📁 Project Information{RESET}")
        print(f"   Path: {CYAN}{report['project_path']}{RESET}")
        print(f"   Python Files: {CYAN}{report['python_files']}{RESET}")
        print(f"   Timestamp: {CYAN}{datetime.fromisoformat(report['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
        print()
        
        # Progress
        progress = report['progress']
        progress_bar = self._create_progress_bar(progress, width=40, color=color)
        
        if progress >= 90:
            status_icon = f"{GREEN}✓{RESET}"
            status_text = f"{GREEN}Excellent{RESET}"
        elif progress >= 70:
            status_icon = f"{YELLOW}◐{RESET}"
            status_text = f"{YELLOW}Good Progress{RESET}"
        elif progress >= 40:
            status_icon = f"{YELLOW}◑{RESET}"
            status_text = f"{YELLOW}In Progress{RESET}"
        else:
            status_icon = f"{RED}◯{RESET}"
            status_text = f"{RED}Just Started{RESET}"
        
        print(f"{BOLD}📊 Migration Progress{RESET}")
        print(f"   {status_icon} Status: {status_text}")
        print(f"   {progress_bar} {BOLD}{progress:.1f}%{RESET}")
        print()
        
        # Issues Summary
        stats = report['stats']
        if stats:
            print(f"{BOLD}🔍 Issues Summary{RESET}")
            total = stats.get('total_issues', 0)
            critical = stats.get('critical_issues', 0)
            high = stats.get('high_issues', 0)
            medium = stats.get('medium_issues', 0)
            low = stats.get('low_issues', 0)
            
            print(f"   Total Issues: {BOLD}{total}{RESET}")
            if critical > 0:
                print(f"   {RED}● Critical:{RESET} {critical:>4}")
            if high > 0:
                print(f"   {YELLOW}● High:{RESET}     {high:>4}")
            if medium > 0:
                print(f"   {BLUE}● Medium:{RESET}   {medium:>4}")
            if low > 0:
                print(f"   {CYAN}● Low:{RESET}      {low:>4}")
            
            # Show change from previous snapshot
            prev_stats = report['previous_stats']
            if prev_stats:
                prev_total = prev_stats.get('total_issues', 0)
                change = prev_total - total
                if change > 0:
                    print(f"   {GREEN}↓ {change} fewer issues since last check{RESET}")
                elif change < 0:
                    print(f"   {RED}↑ {abs(change)} more issues since last check{RESET}")
                else:
                    print(f"   {CYAN}→ No change since last check{RESET}")
            print()
        else:
            print(f"{BOLD}🔍 Issues Summary{RESET}")
            print(f"   {YELLOW}No stats available - run './py2to3 check .' first{RESET}")
            print()
        
        # Git Status
        git_status = report['git_status']
        if git_status:
            print(f"{BOLD}🔀 Git Status{RESET}")
            print(f"   Branch: {CYAN}{git_status['branch']}{RESET}")
            
            modified = git_status['modified_files']
            if modified > 0:
                print(f"   Modified Files: {YELLOW}{modified}{RESET}")
            else:
                print(f"   Modified Files: {GREEN}0 (clean){RESET}")
            
            print(f"   Last Commit: {CYAN}{git_status['last_commit']}{RESET}")
            print()
        
        # Backup Info
        backup_info = report['backup_info']
        if backup_info:
            print(f"{BOLD}💾 Backup Status{RESET}")
            print(f"   {GREEN}✓{RESET} {backup_info['count']} backup(s) in {CYAN}{backup_info['directory']}{RESET}")
            print()
        else:
            print(f"{BOLD}💾 Backup Status{RESET}")
            print(f"   {YELLOW}⚠{RESET} No backups found - consider creating one")
            print()
        
        # Recommendations
        recommendations = report['recommendations']
        if recommendations:
            print(f"{BOLD}💡 Recommendations{RESET}")
            for i, rec in enumerate(recommendations[:5], 1):  # Show max 5
                print(f"   {i}. {rec}")
            print()
        
        # Footer
        print(f"{BOLD}{MAGENTA}{'=' * 70}{RESET}\n")
    
    def _create_progress_bar(self, percentage, width=40, color=True):
        """Create a visual progress bar."""
        if color:
            GREEN = '\033[92m'
            YELLOW = '\033[93m'
            RED = '\033[91m'
            RESET = '\033[0m'
            GRAY = '\033[90m'
        else:
            GREEN = YELLOW = RED = RESET = GRAY = ''
        
        filled = int(width * percentage / 100)
        empty = width - filled
        
        # Choose color based on progress
        if percentage >= 70:
            bar_color = GREEN
        elif percentage >= 40:
            bar_color = YELLOW
        else:
            bar_color = RED
        
        bar = f"[{bar_color}{'█' * filled}{GRAY}{'░' * empty}{RESET}]"
        return bar
    
    def export_json(self, output_path=None):
        """Export status report as JSON."""
        report = self.generate_status_report()
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            return output_path
        else:
            return json.dumps(report, indent=2)


def main():
    """CLI entry point for standalone usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Quick status reporter for Python 2 to 3 migration'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path to analyze (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Export report to JSON file'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    parser.add_argument(
        '--stats-dir',
        default='.migration_stats',
        help='Stats directory (default: .migration_stats)'
    )
    
    args = parser.parse_args()
    
    reporter = MigrationStatusReporter(args.path, args.stats_dir)
    
    if args.output:
        reporter.export_json(args.output)
        print(f"Status report exported to: {args.output}")
    else:
        reporter.print_status(color=not args.no_color)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
