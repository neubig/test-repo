#!/usr/bin/env python3
"""
Migration Comparison Tool

Compare migration progress between different branches, projects, or scan paths.
Useful for evaluating different migration approaches or tracking team progress.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple


class MigrationComparison:
    """Compare migration progress across different contexts."""
    
    def __init__(self):
        """Initialize the comparison tool."""
        pass
    
    def compare_paths(self, path_a: str, path_b: str, 
                     label_a: str = "Path A", label_b: str = "Path B") -> Dict:
        """Compare two different file system paths.
        
        Args:
            path_a: First path to analyze
            path_b: Second path to analyze
            label_a: Label for first path
            label_b: Label for second path
            
        Returns:
            dict: Comparison results
        """
        from stats_tracker import MigrationStatsTracker
        
        # Collect stats for both paths
        tracker_a = MigrationStatsTracker(path_a)
        tracker_b = MigrationStatsTracker(path_b)
        
        stats_a = tracker_a.collect_stats(path_a)
        stats_b = tracker_b.collect_stats(path_b)
        
        # Build comparison
        comparison = self._build_comparison(
            stats_a, stats_b, label_a, label_b,
            context_a=f"Path: {path_a}",
            context_b=f"Path: {path_b}"
        )
        
        return comparison
    
    def compare_branches(self, branch_a: str, branch_b: str, 
                        scan_path: str = ".") -> Dict:
        """Compare migration progress between two git branches.
        
        Args:
            branch_a: First branch name
            branch_b: Second branch name
            scan_path: Path within branches to scan
            
        Returns:
            dict: Comparison results
        """
        # Verify we're in a git repository
        if not self._is_git_repo():
            raise RuntimeError("Not in a git repository")
        
        # Get current branch to restore later
        current_branch = self._get_current_branch()
        
        try:
            # Collect stats from first branch
            self._checkout_branch(branch_a)
            stats_a = self._collect_stats_for_current_state(scan_path)
            
            # Collect stats from second branch
            self._checkout_branch(branch_b)
            stats_b = self._collect_stats_for_current_state(scan_path)
            
        finally:
            # Restore original branch
            if current_branch:
                self._checkout_branch(current_branch)
        
        # Build comparison
        comparison = self._build_comparison(
            stats_a, stats_b, branch_a, branch_b,
            context_a=f"Branch: {branch_a}",
            context_b=f"Branch: {branch_b}"
        )
        
        return comparison
    
    def compare_commits(self, commit_a: str, commit_b: str, 
                       scan_path: str = ".") -> Dict:
        """Compare migration progress between two git commits.
        
        Args:
            commit_a: First commit hash/reference
            commit_b: Second commit hash/reference
            scan_path: Path within commits to scan
            
        Returns:
            dict: Comparison results
        """
        if not self._is_git_repo():
            raise RuntimeError("Not in a git repository")
        
        # Get current HEAD to restore later
        current_head = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            universal_newlines=True
        ).strip()
        
        try:
            # Collect stats from first commit
            subprocess.run(['git', 'checkout', commit_a], 
                         check=True, capture_output=True)
            stats_a = self._collect_stats_for_current_state(scan_path)
            
            # Collect stats from second commit
            subprocess.run(['git', 'checkout', commit_b], 
                         check=True, capture_output=True)
            stats_b = self._collect_stats_for_current_state(scan_path)
            
        finally:
            # Restore original HEAD
            subprocess.run(['git', 'checkout', current_head], 
                         check=True, capture_output=True)
        
        # Build comparison
        comparison = self._build_comparison(
            stats_a, stats_b, 
            f"Commit {commit_a[:7]}", f"Commit {commit_b[:7]}",
            context_a=f"Commit: {commit_a}",
            context_b=f"Commit: {commit_b}"
        )
        
        return comparison
    
    def _collect_stats_for_current_state(self, scan_path: str) -> Dict:
        """Collect statistics for the current working directory state.
        
        Args:
            scan_path: Path to scan
            
        Returns:
            dict: Statistics dictionary
        """
        from stats_tracker import MigrationStatsTracker
        
        tracker = MigrationStatsTracker()
        return tracker.collect_stats(scan_path)
    
    def _build_comparison(self, stats_a: Dict, stats_b: Dict,
                         label_a: str, label_b: str,
                         context_a: str = "", context_b: str = "") -> Dict:
        """Build a comprehensive comparison between two stats snapshots.
        
        Args:
            stats_a: First statistics dictionary
            stats_b: Second statistics dictionary
            label_a: Label for first dataset
            label_b: Label for second dataset
            context_a: Context information for first dataset
            context_b: Context information for second dataset
            
        Returns:
            dict: Comparison results
        """
        sum_a = stats_a['summary']
        sum_b = stats_b['summary']
        
        # Calculate differences
        comparison = {
            'comparison_metadata': {
                'label_a': label_a,
                'label_b': label_b,
                'context_a': context_a,
                'context_b': context_b,
                'timestamp_a': stats_a.get('timestamp', 'N/A'),
                'timestamp_b': stats_b.get('timestamp', 'N/A')
            },
            'summary_comparison': {
                'total_files': {
                    label_a: sum_a['total_files'],
                    label_b: sum_b['total_files'],
                    'difference': sum_b['total_files'] - sum_a['total_files'],
                    'percent_change': self._percent_change(
                        sum_a['total_files'], sum_b['total_files']
                    )
                },
                'clean_files': {
                    label_a: sum_a['clean_files'],
                    label_b: sum_b['clean_files'],
                    'difference': sum_b['clean_files'] - sum_a['clean_files'],
                    'percent_change': self._percent_change(
                        sum_a['clean_files'], sum_b['clean_files']
                    )
                },
                'files_with_issues': {
                    label_a: sum_a['files_with_issues'],
                    label_b: sum_b['files_with_issues'],
                    'difference': sum_b['files_with_issues'] - sum_a['files_with_issues'],
                    'percent_change': self._percent_change(
                        sum_a['files_with_issues'], sum_b['files_with_issues']
                    )
                },
                'total_issues': {
                    label_a: sum_a['total_issues'],
                    label_b: sum_b['total_issues'],
                    'difference': sum_b['total_issues'] - sum_a['total_issues'],
                    'percent_change': self._percent_change(
                        sum_a['total_issues'], sum_b['total_issues']
                    )
                },
                'progress_percentage': {
                    label_a: sum_a['progress_percentage'],
                    label_b: sum_b['progress_percentage'],
                    'difference': round(sum_b['progress_percentage'] - sum_a['progress_percentage'], 2)
                }
            },
            'issue_type_comparison': self._compare_issue_types(
                stats_a.get('issues_by_type', {}),
                stats_b.get('issues_by_type', {}),
                label_a, label_b
            ),
            'severity_comparison': self._compare_severities(
                stats_a.get('issues_by_severity', {}),
                stats_b.get('issues_by_severity', {}),
                label_a, label_b
            ),
            'winner': self._determine_winner(sum_a, sum_b, label_a, label_b)
        }
        
        return comparison
    
    def _compare_issue_types(self, types_a: Dict, types_b: Dict,
                           label_a: str, label_b: str) -> Dict:
        """Compare issue types between two datasets.
        
        Args:
            types_a: Issue types from first dataset
            types_b: Issue types from second dataset
            label_a: Label for first dataset
            label_b: Label for second dataset
            
        Returns:
            dict: Issue type comparison
        """
        all_types = set(types_a.keys()) | set(types_b.keys())
        
        comparison = {}
        for issue_type in all_types:
            count_a = types_a.get(issue_type, 0)
            count_b = types_b.get(issue_type, 0)
            
            comparison[issue_type] = {
                label_a: count_a,
                label_b: count_b,
                'difference': count_b - count_a,
                'percent_change': self._percent_change(count_a, count_b)
            }
        
        return comparison
    
    def _compare_severities(self, sev_a: Dict, sev_b: Dict,
                          label_a: str, label_b: str) -> Dict:
        """Compare severity distributions between two datasets.
        
        Args:
            sev_a: Severities from first dataset
            sev_b: Severities from second dataset
            label_a: Label for first dataset
            label_b: Label for second dataset
            
        Returns:
            dict: Severity comparison
        """
        all_severities = set(sev_a.keys()) | set(sev_b.keys())
        
        comparison = {}
        for severity in all_severities:
            count_a = sev_a.get(severity, 0)
            count_b = sev_b.get(severity, 0)
            
            comparison[severity] = {
                label_a: count_a,
                label_b: count_b,
                'difference': count_b - count_a,
                'percent_change': self._percent_change(count_a, count_b)
            }
        
        return comparison
    
    def _determine_winner(self, sum_a: Dict, sum_b: Dict,
                         label_a: str, label_b: str) -> Dict:
        """Determine which dataset has better migration progress.
        
        Args:
            sum_a: Summary from first dataset
            sum_b: Summary from second dataset
            label_a: Label for first dataset
            label_b: Label for second dataset
            
        Returns:
            dict: Winner determination
        """
        # Compare by progress percentage (primary metric)
        progress_a = sum_a['progress_percentage']
        progress_b = sum_b['progress_percentage']
        
        if progress_a > progress_b:
            winner = label_a
            margin = round(progress_a - progress_b, 2)
        elif progress_b > progress_a:
            winner = label_b
            margin = round(progress_b - progress_a, 2)
        else:
            # If progress is equal, compare by total issues
            if sum_a['total_issues'] < sum_b['total_issues']:
                winner = label_a
                margin = 0
            elif sum_b['total_issues'] < sum_a['total_issues']:
                winner = label_b
                margin = 0
            else:
                winner = "tie"
                margin = 0
        
        return {
            'winner': winner,
            'margin': margin,
            'metric': 'progress_percentage'
        }
    
    def _percent_change(self, old_value: float, new_value: float) -> float:
        """Calculate percent change between two values.
        
        Args:
            old_value: Original value
            new_value: New value
            
        Returns:
            float: Percent change (rounded to 2 decimals)
        """
        if old_value == 0:
            if new_value == 0:
                return 0.0
            return float('inf') if new_value > 0 else float('-inf')
        
        return round(((new_value - old_value) / old_value) * 100, 2)
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository.
        
        Returns:
            bool: True if in a git repository
        """
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                check=True, capture_output=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_current_branch(self) -> Optional[str]:
        """Get the current git branch name.
        
        Returns:
            str or None: Current branch name, or None if detached HEAD
        """
        try:
            result = subprocess.check_output(
                ['git', 'symbolic-ref', '--short', 'HEAD'],
                universal_newlines=True,
                stderr=subprocess.DEVNULL
            )
            return result.strip()
        except subprocess.CalledProcessError:
            # Detached HEAD state
            return None
    
    def _checkout_branch(self, branch: str):
        """Checkout a git branch.
        
        Args:
            branch: Branch name to checkout
        """
        subprocess.run(
            ['git', 'checkout', branch],
            check=True,
            capture_output=True
        )
    
    def format_comparison(self, comparison: Dict, format: str = 'text') -> str:
        """Format comparison results for display.
        
        Args:
            comparison: Comparison results dictionary
            format: Output format ('text' or 'json')
            
        Returns:
            str: Formatted comparison
        """
        if format == 'json':
            return json.dumps(comparison, indent=2)
        
        # Text format
        lines = []
        metadata = comparison['comparison_metadata']
        summary = comparison['summary_comparison']
        winner = comparison['winner']
        
        # Header
        lines.append('=' * 70)
        lines.append('MIGRATION COMPARISON REPORT')
        lines.append('=' * 70)
        lines.append('')
        
        # Comparison context
        lines.append(f"Comparing: {metadata['label_a']} vs {metadata['label_b']}")
        if metadata.get('context_a'):
            lines.append(f"  {metadata['label_a']}: {metadata['context_a']}")
        if metadata.get('context_b'):
            lines.append(f"  {metadata['label_b']}: {metadata['context_b']}")
        lines.append('')
        
        # Winner announcement
        if winner['winner'] != 'tie':
            lines.append(f"🏆 Winner: {winner['winner']}")
            if winner['margin'] > 0:
                lines.append(f"   Margin: {winner['margin']}% better progress")
        else:
            lines.append("🤝 Result: Tie")
        lines.append('')
        lines.append('-' * 70)
        lines.append('')
        
        # Summary comparison
        lines.append('SUMMARY COMPARISON:')
        lines.append('')
        
        for metric, data in summary.items():
            metric_name = metric.replace('_', ' ').title()
            lines.append(f"{metric_name}:")
            
            label_a = metadata['label_a']
            label_b = metadata['label_b']
            
            value_a = data[label_a]
            value_b = data[label_b]
            
            lines.append(f"  {label_a:20s}: {value_a}")
            lines.append(f"  {label_b:20s}: {value_b}")
            
            if 'difference' in data:
                diff = data['difference']
                diff_str = f"+{diff}" if diff > 0 else str(diff)
                lines.append(f"  {'Difference':20s}: {diff_str}")
            
            if 'percent_change' in data:
                pct = data['percent_change']
                if pct != float('inf') and pct != float('-inf'):
                    pct_str = f"+{pct}%" if pct > 0 else f"{pct}%"
                    lines.append(f"  {'Percent Change':20s}: {pct_str}")
            
            lines.append('')
        
        # Issue type comparison (top 10)
        if comparison.get('issue_type_comparison'):
            lines.append('-' * 70)
            lines.append('')
            lines.append('TOP ISSUE TYPES COMPARISON:')
            lines.append('')
            
            issue_types = comparison['issue_type_comparison']
            # Sort by total count (sum of both)
            sorted_types = sorted(
                issue_types.items(),
                key=lambda x: x[1][label_a] + x[1][label_b],
                reverse=True
            )[:10]
            
            for issue_type, data in sorted_types:
                lines.append(f"{issue_type}:")
                lines.append(f"  {label_a:20s}: {data[label_a]}")
                lines.append(f"  {label_b:20s}: {data[label_b]}")
                diff = data['difference']
                diff_str = f"+{diff}" if diff > 0 else str(diff)
                lines.append(f"  {'Difference':20s}: {diff_str}")
                lines.append('')
        
        # Severity comparison
        if comparison.get('severity_comparison'):
            lines.append('-' * 70)
            lines.append('')
            lines.append('SEVERITY COMPARISON:')
            lines.append('')
            
            for severity, data in comparison['severity_comparison'].items():
                lines.append(f"{severity.upper()}:")
                lines.append(f"  {label_a:20s}: {data[label_a]}")
                lines.append(f"  {label_b:20s}: {data[label_b]}")
                diff = data['difference']
                diff_str = f"+{diff}" if diff > 0 else str(diff)
                lines.append(f"  {'Difference':20s}: {diff_str}")
                lines.append('')
        
        lines.append('=' * 70)
        
        return '\n'.join(lines)


def main():
    """Command-line interface for comparison tool."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Compare migration progress across branches, commits, or paths'
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Comparison mode')
    
    # Path comparison
    parser_paths = subparsers.add_parser('paths', help='Compare two file system paths')
    parser_paths.add_argument('path_a', help='First path to compare')
    parser_paths.add_argument('path_b', help='Second path to compare')
    parser_paths.add_argument('--label-a', default='Path A', help='Label for first path')
    parser_paths.add_argument('--label-b', default='Path B', help='Label for second path')
    
    # Branch comparison
    parser_branches = subparsers.add_parser('branches', help='Compare two git branches')
    parser_branches.add_argument('branch_a', help='First branch to compare')
    parser_branches.add_argument('branch_b', help='Second branch to compare')
    parser_branches.add_argument('--scan-path', default='.', help='Path to scan in branches')
    
    # Commit comparison
    parser_commits = subparsers.add_parser('commits', help='Compare two git commits')
    parser_commits.add_argument('commit_a', help='First commit to compare')
    parser_commits.add_argument('commit_b', help='Second commit to compare')
    parser_commits.add_argument('--scan-path', default='.', help='Path to scan in commits')
    
    # Common arguments
    for p in [parser_paths, parser_branches, parser_commits]:
        p.add_argument('-o', '--output', help='Output file path')
        p.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                      help='Output format')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return 1
    
    # Run comparison
    comparator = MigrationComparison()
    
    try:
        if args.mode == 'paths':
            result = comparator.compare_paths(
                args.path_a, args.path_b,
                args.label_a, args.label_b
            )
        elif args.mode == 'branches':
            result = comparator.compare_branches(
                args.branch_a, args.branch_b,
                args.scan_path
            )
        elif args.mode == 'commits':
            result = comparator.compare_commits(
                args.commit_a, args.commit_b,
                args.scan_path
            )
        
        # Format and output
        output = comparator.format_comparison(result, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Comparison saved to: {args.output}")
        else:
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
