#!/usr/bin/env python3
"""
Effort Estimator for Python 2 to 3 Migration

Analyzes codebase complexity and provides detailed estimates for migration effort,
including time requirements, team size recommendations, and project timeline.
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timedelta


class EffortEstimator:
    """Estimates effort required for Python 2 to 3 migration."""
    
    # Time estimates per issue type (in hours)
    ISSUE_TIME_ESTIMATES = {
        'print_statement': 0.1,
        'import_change': 0.2,
        'exception_syntax': 0.15,
        'iterator_method': 0.2,
        'string_type': 0.3,
        'division_operator': 0.25,
        'dict_method': 0.2,
        'xrange': 0.1,
        'unicode': 0.4,
        'basestring': 0.3,
        'long_type': 0.2,
        'raw_input': 0.15,
        'has_key': 0.1,
        'execfile': 0.3,
        'cmp_function': 0.5,
        '__cmp__': 0.6,
        'apply_function': 0.3,
        'buffer_type': 0.4,
        'file_type': 0.3,
        'reduce_import': 0.2,
        'metaclass': 0.8,
        'oldstyle_class': 0.5,
        'unknown': 0.3,
    }
    
    # Complexity multipliers based on severity
    SEVERITY_MULTIPLIERS = {
        'critical': 2.0,
        'high': 1.5,
        'medium': 1.0,
        'low': 0.7,
    }
    
    # Base overhead hours for project setup and wrap-up
    BASE_OVERHEAD = {
        'small': 4,      # < 10 files
        'medium': 8,     # 10-50 files
        'large': 16,     # 50-200 files
        'xlarge': 32,    # > 200 files
    }
    
    def __init__(self):
        self.issues = []
        self.file_count = 0
        self.total_lines = 0
        self.python_files = []
        
    def analyze_codebase(self, path):
        """Analyze codebase to gather metrics."""
        if os.path.isfile(path):
            self._analyze_file(path)
        else:
            self._analyze_directory(path)
            
    def _analyze_directory(self, directory):
        """Recursively analyze all Python files in directory."""
        for root, dirs, files in os.walk(directory):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {
                '__pycache__', '.git', '.tox', 'venv', 'env', 
                '.venv', 'node_modules', 'build', 'dist', '.eggs'
            }]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self._analyze_file(filepath)
                    
    def _analyze_file(self, filepath):
        """Analyze a single Python file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                self.total_lines += len(lines)
                self.file_count += 1
                self.python_files.append(filepath)
                
                # Run verifier to detect issues
                self._detect_issues(filepath, lines)
        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}", file=sys.stderr)
            
    def _detect_issues(self, filepath, lines):
        """Detect Python 2 to 3 compatibility issues."""
        # Try to use verifier if available
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            verifier.verify_file(filepath)
            
            for issue in verifier.issues_found:
                self.issues.append({
                    'file': filepath,
                    'type': issue.get('pattern', 'unknown'),
                    'severity': issue.get('severity', 'medium'),
                    'line': issue.get('line', 0),
                })
        except ImportError:
            # Fallback: simple pattern detection
            self._simple_pattern_detection(filepath, lines)
            
    def _simple_pattern_detection(self, filepath, lines):
        """Simple fallback pattern detection without verifier."""
        patterns = [
            ('print ', 'print_statement', 'medium'),
            ('import urllib2', 'import_change', 'medium'),
            ('import ConfigParser', 'import_change', 'medium'),
            ('except ', 'exception_syntax', 'medium'),
            ('.iteritems()', 'iterator_method', 'medium'),
            ('.iterkeys()', 'iterator_method', 'medium'),
            ('.itervalues()', 'iterator_method', 'medium'),
            ('xrange(', 'xrange', 'low'),
            ('unicode(', 'unicode', 'high'),
            ('basestring', 'basestring', 'high'),
            ('.has_key(', 'has_key', 'low'),
            ('long(', 'long_type', 'medium'),
            ('raw_input(', 'raw_input', 'low'),
            ('__cmp__', '__cmp__', 'high'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, issue_type, severity in patterns:
                if pattern in line:
                    self.issues.append({
                        'file': filepath,
                        'type': issue_type,
                        'severity': severity,
                        'line': i,
                    })
                    
    def estimate_effort(self):
        """Calculate effort estimates."""
        # Group issues by type and severity
        issue_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for issue in self.issues:
            issue_counts[issue['type']] += 1
            severity_counts[issue['severity']] += 1
            
        # Calculate direct fix time
        fix_hours = 0
        for issue_type, count in issue_counts.items():
            base_time = self.ISSUE_TIME_ESTIMATES.get(issue_type, 0.3)
            fix_hours += base_time * count
            
        # Apply complexity adjustments
        avg_issues_per_file = len(self.issues) / max(self.file_count, 1)
        if avg_issues_per_file > 10:
            fix_hours *= 1.3  # High density of issues
        elif avg_issues_per_file > 5:
            fix_hours *= 1.15  # Medium density
            
        # Add testing overhead (20% of fix time)
        testing_hours = fix_hours * 0.20
        
        # Add code review overhead (15% of fix time)
        review_hours = fix_hours * 0.15
        
        # Add documentation overhead (10% of fix time)
        docs_hours = fix_hours * 0.10
        
        # Add base project overhead
        project_size = self._get_project_size()
        overhead_hours = self.BASE_OVERHEAD[project_size]
        
        # Calculate total
        total_hours = fix_hours + testing_hours + review_hours + docs_hours + overhead_hours
        
        # Calculate risk factor
        risk_factor = self._calculate_risk_factor(severity_counts)
        
        # Add contingency based on risk (10-30%)
        contingency = total_hours * (0.10 + risk_factor * 0.20)
        total_with_contingency = total_hours + contingency
        
        return {
            'breakdown': {
                'fix_hours': round(fix_hours, 1),
                'testing_hours': round(testing_hours, 1),
                'review_hours': round(review_hours, 1),
                'documentation_hours': round(docs_hours, 1),
                'overhead_hours': round(overhead_hours, 1),
                'contingency_hours': round(contingency, 1),
            },
            'total_hours': round(total_hours, 1),
            'total_with_contingency': round(total_with_contingency, 1),
            'total_days': round(total_with_contingency / 8, 1),
            'total_weeks': round(total_with_contingency / 40, 1),
            'issue_counts': dict(issue_counts),
            'severity_counts': dict(severity_counts),
            'file_count': self.file_count,
            'total_lines': self.total_lines,
            'risk_factor': round(risk_factor, 2),
            'project_size': project_size,
        }
        
    def _get_project_size(self):
        """Determine project size category."""
        if self.file_count < 10:
            return 'small'
        elif self.file_count < 50:
            return 'medium'
        elif self.file_count < 200:
            return 'large'
        else:
            return 'xlarge'
            
    def _calculate_risk_factor(self, severity_counts):
        """Calculate risk factor (0.0 to 1.0)."""
        if not self.issues:
            return 0.0
            
        total = len(self.issues)
        critical = severity_counts.get('critical', 0)
        high = severity_counts.get('high', 0)
        
        risk = (critical * 1.0 + high * 0.5) / total
        return min(risk, 1.0)
        
    def recommend_team_size(self, estimate):
        """Recommend team size based on project scope."""
        total_weeks = estimate['total_weeks']
        
        if total_weeks < 1:
            return {
                'developers': 1,
                'qa': 0,
                'timeline_weeks': round(total_weeks, 1),
                'recommendation': 'Single developer can handle this migration',
            }
        elif total_weeks < 4:
            return {
                'developers': 1,
                'qa': 1,
                'timeline_weeks': round(total_weeks, 1),
                'recommendation': 'One developer with QA support',
            }
        elif total_weeks < 12:
            devs = 2
            timeline = total_weeks / 1.5  # 50% efficiency with 2 devs
            return {
                'developers': devs,
                'qa': 1,
                'timeline_weeks': round(timeline, 1),
                'recommendation': 'Small team with dedicated QA',
            }
        else:
            devs = 3
            timeline = total_weeks / 2.0  # 50% efficiency with 3 devs
            return {
                'developers': devs,
                'qa': 2,
                'timeline_weeks': round(timeline, 1),
                'recommendation': 'Full team with multiple developers and QA',
            }
            
    def generate_timeline(self, estimate, team_recommendation):
        """Generate project timeline with milestones."""
        timeline_weeks = team_recommendation['timeline_weeks']
        start_date = datetime.now()
        
        milestones = []
        
        # Phase 1: Setup and Planning (10%)
        phase1_weeks = timeline_weeks * 0.10
        phase1_end = start_date + timedelta(weeks=phase1_weeks)
        milestones.append({
            'phase': 'Setup & Planning',
            'duration_weeks': round(phase1_weeks, 1),
            'end_date': phase1_end.strftime('%Y-%m-%d'),
            'tasks': [
                'Setup development environment',
                'Run initial assessment',
                'Create migration plan',
                'Setup version control',
            ]
        })
        
        # Phase 2: Core Migration (50%)
        phase2_weeks = timeline_weeks * 0.50
        phase2_end = phase1_end + timedelta(weeks=phase2_weeks)
        milestones.append({
            'phase': 'Core Migration',
            'duration_weeks': round(phase2_weeks, 1),
            'end_date': phase2_end.strftime('%Y-%m-%d'),
            'tasks': [
                'Apply automated fixes',
                'Manual code updates',
                'Fix critical issues',
                'Update dependencies',
            ]
        })
        
        # Phase 3: Testing (25%)
        phase3_weeks = timeline_weeks * 0.25
        phase3_end = phase2_end + timedelta(weeks=phase3_weeks)
        milestones.append({
            'phase': 'Testing & QA',
            'duration_weeks': round(phase3_weeks, 1),
            'end_date': phase3_end.strftime('%Y-%m-%d'),
            'tasks': [
                'Unit testing',
                'Integration testing',
                'Performance testing',
                'Bug fixes',
            ]
        })
        
        # Phase 4: Documentation & Deployment (15%)
        phase4_weeks = timeline_weeks * 0.15
        phase4_end = phase3_end + timedelta(weeks=phase4_weeks)
        milestones.append({
            'phase': 'Documentation & Deployment',
            'duration_weeks': round(phase4_weeks, 1),
            'end_date': phase4_end.strftime('%Y-%m-%d'),
            'tasks': [
                'Update documentation',
                'Final code review',
                'Deployment preparation',
                'Production deployment',
            ]
        })
        
        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': phase4_end.strftime('%Y-%m-%d'),
            'total_weeks': round(timeline_weeks, 1),
            'milestones': milestones,
        }
        
    def format_report(self, estimate, team_recommendation, timeline, format='text'):
        """Format the estimate report."""
        if format == 'json':
            return json.dumps({
                'estimate': estimate,
                'team_recommendation': team_recommendation,
                'timeline': timeline,
                'generated_at': datetime.now().isoformat(),
            }, indent=2)
        elif format == 'csv':
            return self._format_csv(estimate, team_recommendation)
        else:
            return self._format_text(estimate, team_recommendation, timeline)
            
    def _format_text(self, estimate, team_recommendation, timeline):
        """Format as human-readable text."""
        lines = []
        lines.append("=" * 70)
        lines.append("PYTHON 2 TO 3 MIGRATION EFFORT ESTIMATE")
        lines.append("=" * 70)
        lines.append("")
        
        # Project Overview
        lines.append("PROJECT OVERVIEW")
        lines.append("-" * 70)
        lines.append(f"Files to migrate:        {estimate['file_count']}")
        lines.append(f"Total lines of code:     {estimate['total_lines']:,}")
        lines.append(f"Issues detected:         {len(self.issues)}")
        lines.append(f"Project size:            {estimate['project_size'].upper()}")
        lines.append(f"Risk factor:             {estimate['risk_factor']:.2f} (0.0 = low, 1.0 = high)")
        lines.append("")
        
        # Issue Breakdown
        lines.append("ISSUES BY SEVERITY")
        lines.append("-" * 70)
        for severity in ['critical', 'high', 'medium', 'low']:
            count = estimate['severity_counts'].get(severity, 0)
            if count > 0:
                lines.append(f"  {severity.capitalize():12} {count:6} issues")
        lines.append("")
        
        # Time Estimate
        lines.append("TIME ESTIMATE")
        lines.append("-" * 70)
        breakdown = estimate['breakdown']
        lines.append(f"Code fixes:              {breakdown['fix_hours']:8.1f} hours")
        lines.append(f"Testing:                 {breakdown['testing_hours']:8.1f} hours")
        lines.append(f"Code review:             {breakdown['review_hours']:8.1f} hours")
        lines.append(f"Documentation:           {breakdown['documentation_hours']:8.1f} hours")
        lines.append(f"Project overhead:        {breakdown['overhead_hours']:8.1f} hours")
        lines.append(f"Contingency buffer:      {breakdown['contingency_hours']:8.1f} hours")
        lines.append("-" * 70)
        lines.append(f"TOTAL ESTIMATE:          {estimate['total_with_contingency']:8.1f} hours")
        lines.append(f"                         {estimate['total_days']:8.1f} days")
        lines.append(f"                         {estimate['total_weeks']:8.1f} weeks")
        lines.append("")
        
        # Team Recommendation
        lines.append("TEAM RECOMMENDATION")
        lines.append("-" * 70)
        lines.append(f"Developers:              {team_recommendation['developers']}")
        lines.append(f"QA Engineers:            {team_recommendation['qa']}")
        lines.append(f"Timeline:                {team_recommendation['timeline_weeks']:.1f} weeks")
        lines.append(f"Recommendation:          {team_recommendation['recommendation']}")
        lines.append("")
        
        # Timeline
        lines.append("PROJECT TIMELINE")
        lines.append("-" * 70)
        lines.append(f"Start date:              {timeline['start_date']}")
        lines.append(f"Target completion:       {timeline['end_date']}")
        lines.append("")
        
        for milestone in timeline['milestones']:
            lines.append(f"Phase: {milestone['phase']}")
            lines.append(f"  Duration:   {milestone['duration_weeks']:.1f} weeks")
            lines.append(f"  End date:   {milestone['end_date']}")
            lines.append(f"  Tasks:")
            for task in milestone['tasks']:
                lines.append(f"    • {task}")
            lines.append("")
            
        lines.append("=" * 70)
        lines.append("Note: Estimates include contingency buffer based on risk assessment.")
        lines.append("Actual time may vary based on team experience and code complexity.")
        lines.append("=" * 70)
        
        return "\n".join(lines)
        
    def _format_csv(self, estimate, team_recommendation):
        """Format as CSV."""
        lines = []
        lines.append("metric,value")
        lines.append(f"file_count,{estimate['file_count']}")
        lines.append(f"total_lines,{estimate['total_lines']}")
        lines.append(f"total_issues,{len(self.issues)}")
        lines.append(f"fix_hours,{estimate['breakdown']['fix_hours']}")
        lines.append(f"testing_hours,{estimate['breakdown']['testing_hours']}")
        lines.append(f"review_hours,{estimate['breakdown']['review_hours']}")
        lines.append(f"total_hours,{estimate['total_with_contingency']}")
        lines.append(f"total_days,{estimate['total_days']}")
        lines.append(f"total_weeks,{estimate['total_weeks']}")
        lines.append(f"developers,{team_recommendation['developers']}")
        lines.append(f"qa,{team_recommendation['qa']}")
        lines.append(f"timeline_weeks,{team_recommendation['timeline_weeks']}")
        lines.append(f"risk_factor,{estimate['risk_factor']}")
        return "\n".join(lines)


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Estimate effort required for Python 2 to 3 migration'
    )
    parser.add_argument('path', help='Path to Python file or directory to analyze')
    parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output file (default: print to console)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)
        
    # Run estimation
    estimator = EffortEstimator()
    print(f"Analyzing codebase at: {args.path}")
    estimator.analyze_codebase(args.path)
    
    print(f"Found {estimator.file_count} Python files with {len(estimator.issues)} issues")
    print("Calculating estimates...\n")
    
    estimate = estimator.estimate_effort()
    team_recommendation = estimator.recommend_team_size(estimate)
    timeline = estimator.generate_timeline(estimate, team_recommendation)
    
    # Generate report
    report = estimator.format_report(estimate, team_recommendation, timeline, args.format)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)
        
    sys.exit(0)


if __name__ == '__main__':
    main()
