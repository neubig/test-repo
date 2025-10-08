#!/usr/bin/env python3
"""
Linting Integration Module

Integrates popular Python linters (pylint, flake8, mypy, black) to ensure
migrated code meets modern Python standards and best practices.
"""

import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class LintingIntegration:
    """Integrate multiple Python linters for comprehensive code quality checking."""
    
    # Linter configurations
    LINTERS = {
        'pylint': {
            'cmd': ['pylint', '--output-format=json'],
            'description': 'Comprehensive Python code analyzer',
            'install': 'pip install pylint'
        },
        'flake8': {
            'cmd': ['flake8', '--format=json'],
            'description': 'Style guide enforcement tool',
            'install': 'pip install flake8 flake8-json'
        },
        'mypy': {
            'cmd': ['mypy', '--show-column-numbers', '--show-error-codes'],
            'description': 'Static type checker',
            'install': 'pip install mypy'
        },
        'black': {
            'cmd': ['black', '--check', '--diff'],
            'description': 'Code formatter checker',
            'install': 'pip install black'
        }
    }
    
    def __init__(self, project_path: str = ".", config: Optional[Dict] = None):
        self.project_path = Path(project_path).resolve()
        self.config = config or {}
        self.results = {}
        
    def run_all_linters(
        self,
        target: Optional[str] = None,
        enabled_linters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run all enabled linters on the target path.
        
        Args:
            target: Path to lint (file or directory). Defaults to project root.
            enabled_linters: List of linters to run. Defaults to all available.
            
        Returns:
            Dictionary with results from all linters
        """
        if target is None:
            target = str(self.project_path)
        else:
            target = str(Path(target).resolve())
            
        if enabled_linters is None:
            enabled_linters = list(self.LINTERS.keys())
        
        # Check which linters are available
        available = self._check_available_linters(enabled_linters)
        
        results = {
            'target': target,
            'linters': {},
            'summary': {
                'total_issues': 0,
                'by_severity': defaultdict(int),
                'by_linter': {},
                'available_linters': available['available'],
                'unavailable_linters': available['unavailable']
            }
        }
        
        # Run each available linter
        for linter in available['available']:
            print(f"Running {linter}...")
            linter_results = self._run_linter(linter, target)
            results['linters'][linter] = linter_results
            
            # Update summary
            issue_count = linter_results.get('issue_count', 0)
            results['summary']['by_linter'][linter] = issue_count
            results['summary']['total_issues'] += issue_count
            
            # Update severity counts
            for severity, count in linter_results.get('by_severity', {}).items():
                results['summary']['by_severity'][severity] += count
        
        self.results = results
        return results
    
    def _check_available_linters(self, linters: List[str]) -> Dict[str, List[str]]:
        """Check which linters are installed and available."""
        available = []
        unavailable = []
        
        for linter in linters:
            if linter not in self.LINTERS:
                continue
                
            # Try to run the linter with --version
            cmd = self.LINTERS[linter]['cmd'][0]
            try:
                subprocess.run(
                    [cmd, '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                available.append(linter)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                unavailable.append(linter)
        
        return {'available': available, 'unavailable': unavailable}
    
    def _run_linter(self, linter: str, target: str) -> Dict[str, Any]:
        """Run a specific linter and parse its output."""
        method_name = f"_run_{linter}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(target)
        else:
            return {'error': f'No handler for linter: {linter}'}
    
    def _run_pylint(self, target: str) -> Dict[str, Any]:
        """Run pylint and parse results."""
        cmd = self.LINTERS['pylint']['cmd'] + [target]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
                cwd=str(self.project_path)
            )
            
            # Pylint returns non-zero on issues, which is expected
            output = result.stdout.decode('utf-8')
            
            try:
                issues = json.loads(output) if output.strip() else []
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'status': 'error',
                    'message': 'Failed to parse pylint output',
                    'raw_output': output[:500]
                }
            
            # Categorize issues by severity
            by_severity = defaultdict(int)
            by_type = defaultdict(int)
            
            for issue in issues:
                issue_type = issue.get('type', 'unknown')
                by_type[issue_type] += 1
                
                # Map pylint types to severity levels
                if issue_type in ['error', 'fatal']:
                    by_severity['error'] += 1
                elif issue_type == 'warning':
                    by_severity['warning'] += 1
                elif issue_type in ['convention', 'refactor']:
                    by_severity['info'] += 1
            
            return {
                'status': 'success',
                'issue_count': len(issues),
                'issues': issues[:100],  # Limit to first 100 for brevity
                'by_severity': dict(by_severity),
                'by_type': dict(by_type),
                'total_issues': len(issues)
            }
            
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Pylint execution timed out'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _run_flake8(self, target: str) -> Dict[str, Any]:
        """Run flake8 and parse results."""
        # First try with JSON format
        cmd = ['flake8', '--format=json', target]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                cwd=str(self.project_path)
            )
            
            output = result.stdout.decode('utf-8')
            stderr = result.stderr.decode('utf-8')
            
            # Check if flake8-json is installed
            if 'format' in stderr or 'json' in stderr.lower():
                # Fallback to default format
                cmd = ['flake8', target]
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60,
                    cwd=str(self.project_path)
                )
                output = result.stdout.decode('utf-8')
                return self._parse_flake8_default(output)
            
            # Try to parse JSON output
            try:
                issues_dict = json.loads(output) if output.strip() else {}
            except json.JSONDecodeError:
                # Parse default format
                return self._parse_flake8_default(output)
            
            # Flatten the dictionary structure
            issues = []
            for filename, file_issues in issues_dict.items():
                for issue in file_issues:
                    issues.append({
                        'file': filename,
                        'line': issue.get('line_number'),
                        'column': issue.get('column_number'),
                        'code': issue.get('code'),
                        'message': issue.get('text')
                    })
            
            by_severity = self._categorize_flake8_issues(issues)
            
            return {
                'status': 'success',
                'issue_count': len(issues),
                'issues': issues[:100],
                'by_severity': by_severity,
                'total_issues': len(issues)
            }
            
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Flake8 execution timed out'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _parse_flake8_default(self, output: str) -> Dict[str, Any]:
        """Parse flake8 default output format."""
        issues = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Format: filename:line:column: code message
            parts = line.split(':', 3)
            if len(parts) >= 4:
                issues.append({
                    'file': parts[0],
                    'line': parts[1],
                    'column': parts[2],
                    'message': parts[3].strip()
                })
        
        by_severity = self._categorize_flake8_issues(issues)
        
        return {
            'status': 'success',
            'issue_count': len(issues),
            'issues': issues[:100],
            'by_severity': by_severity,
            'total_issues': len(issues)
        }
    
    def _categorize_flake8_issues(self, issues: List[Dict]) -> Dict[str, int]:
        """Categorize flake8 issues by severity based on error codes."""
        by_severity = defaultdict(int)
        
        for issue in issues:
            code = issue.get('code', issue.get('message', ''))[:1]
            
            # E: Error, W: Warning, F: Fatal, C: Complexity, N: Naming
            if code in ['E', 'F']:
                by_severity['error'] += 1
            elif code in ['W', 'C']:
                by_severity['warning'] += 1
            else:
                by_severity['info'] += 1
        
        return dict(by_severity)
    
    def _run_mypy(self, target: str) -> Dict[str, Any]:
        """Run mypy and parse results."""
        cmd = self.LINTERS['mypy']['cmd'] + [target]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
                cwd=str(self.project_path)
            )
            
            output = result.stdout.decode('utf-8')
            
            # Parse mypy output
            issues = []
            lines = output.strip().split('\n')
            
            for line in lines:
                if not line.strip() or ':' not in line:
                    continue
                
                # Format: filename:line:column: severity: message
                parts = line.split(':', 4)
                if len(parts) >= 4:
                    issues.append({
                        'file': parts[0],
                        'line': parts[1],
                        'column': parts[2] if len(parts) > 3 else '0',
                        'severity': parts[3].strip() if len(parts) > 4 else 'error',
                        'message': parts[4].strip() if len(parts) > 4 else parts[3].strip()
                    })
            
            by_severity = defaultdict(int)
            for issue in issues:
                severity = issue.get('severity', 'error')
                if 'error' in severity:
                    by_severity['error'] += 1
                elif 'warning' in severity:
                    by_severity['warning'] += 1
                else:
                    by_severity['info'] += 1
            
            return {
                'status': 'success',
                'issue_count': len(issues),
                'issues': issues[:100],
                'by_severity': dict(by_severity),
                'total_issues': len(issues)
            }
            
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Mypy execution timed out'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _run_black(self, target: str) -> Dict[str, Any]:
        """Run black in check mode and parse results."""
        cmd = self.LINTERS['black']['cmd'] + [target]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                cwd=str(self.project_path)
            )
            
            output = result.stdout.decode('utf-8')
            
            # Black returns 0 if no changes needed, 1 if changes needed
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'issue_count': 0,
                    'issues': [],
                    'by_severity': {},
                    'message': 'Code is already formatted correctly'
                }
            
            # Parse the output to count files that need formatting
            lines = output.strip().split('\n')
            files_to_format = []
            
            for line in lines:
                if line.startswith('would reformat'):
                    files_to_format.append(line)
            
            return {
                'status': 'success',
                'issue_count': len(files_to_format),
                'issues': [{'message': line} for line in files_to_format[:100]],
                'by_severity': {'info': len(files_to_format)},
                'total_issues': len(files_to_format)
            }
            
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Black execution timed out'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def generate_report(self, format: str = 'text') -> str:
        """
        Generate a report of linting results.
        
        Args:
            format: Output format ('text' or 'json')
            
        Returns:
            Formatted report string
        """
        if format == 'json':
            return json.dumps(self.results, indent=2)
        
        return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate a human-readable text report."""
        if not self.results:
            return "No linting results available. Run linters first."
        
        lines = []
        lines.append("=" * 80)
        lines.append("LINTING REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTarget: {self.results['target']}")
        lines.append("")
        
        summary = self.results['summary']
        
        # Available linters
        lines.append("Available Linters:")
        for linter in summary['available_linters']:
            count = summary['by_linter'].get(linter, 0)
            lines.append(f"  ✓ {linter}: {count} issues")
        
        if summary['unavailable_linters']:
            lines.append("\nUnavailable Linters:")
            for linter in summary['unavailable_linters']:
                install_cmd = self.LINTERS[linter]['install']
                lines.append(f"  ✗ {linter} (install: {install_cmd})")
        
        lines.append("")
        lines.append("-" * 80)
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Issues: {summary['total_issues']}")
        
        if summary['by_severity']:
            lines.append("\nBy Severity:")
            for severity, count in sorted(summary['by_severity'].items()):
                lines.append(f"  {severity.upper()}: {count}")
        
        # Detailed results per linter
        for linter, linter_results in self.results['linters'].items():
            lines.append("")
            lines.append("-" * 80)
            lines.append(f"{linter.upper()} RESULTS")
            lines.append("-" * 80)
            
            if linter_results.get('status') == 'success':
                issue_count = linter_results.get('issue_count', 0)
                lines.append(f"Status: ✓ Success")
                lines.append(f"Issues Found: {issue_count}")
                
                if issue_count > 0 and linter_results.get('issues'):
                    lines.append("\nTop Issues (showing first 10):")
                    for i, issue in enumerate(linter_results['issues'][:10], 1):
                        if 'file' in issue:
                            lines.append(
                                f"  {i}. {issue.get('file')}:"
                                f"{issue.get('line', '?')} - "
                                f"{issue.get('message', 'No message')}"
                            )
                        else:
                            lines.append(f"  {i}. {issue.get('message', 'No message')}")
            else:
                status = linter_results.get('status', 'unknown')
                message = linter_results.get('message', 'No details')
                lines.append(f"Status: ✗ {status.upper()}")
                lines.append(f"Message: {message}")
        
        # Recommendations
        lines.append("")
        lines.append("-" * 80)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            lines.append(f"  • {rec}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on results."""
        recommendations = []
        
        if not self.results:
            return recommendations
        
        summary = self.results['summary']
        
        # Check for unavailable linters
        if summary['unavailable_linters']:
            recommendations.append(
                f"Install missing linters to get more comprehensive analysis: "
                f"{', '.join(summary['unavailable_linters'])}"
            )
        
        # High issue counts
        total = summary['total_issues']
        if total > 100:
            recommendations.append(
                f"High issue count ({total}). Consider addressing critical errors first."
            )
        elif total > 0:
            recommendations.append(
                f"Found {total} issues. Review and address them to improve code quality."
            )
        else:
            recommendations.append("Great! No issues found by available linters.")
        
        # Severity-based recommendations
        by_severity = summary.get('by_severity', {})
        if by_severity.get('error', 0) > 0:
            recommendations.append(
                f"Priority: Fix {by_severity['error']} error(s) that may cause runtime issues."
            )
        
        if by_severity.get('warning', 0) > 10:
            recommendations.append(
                f"Consider addressing {by_severity['warning']} warnings to improve code quality."
            )
        
        # Black formatting
        if 'black' in self.results['linters']:
            black_results = self.results['linters']['black']
            if black_results.get('issue_count', 0) > 0:
                recommendations.append(
                    "Run 'black <target>' to auto-format code according to PEP 8 standards."
                )
        
        # MyPy type checking
        if 'mypy' in self.results['linters']:
            mypy_results = self.results['linters']['mypy']
            if mypy_results.get('issue_count', 0) > 0:
                recommendations.append(
                    "Add type hints to improve code maintainability and catch type errors."
                )
        
        return recommendations
    
    def save_report(self, output_file: str, format: str = 'text') -> None:
        """Save the linting report to a file."""
        report = self.generate_report(format=format)
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"\nReport saved to: {output_file}")


def main():
    """CLI entry point for linting integration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Python linters on migrated code"
    )
    parser.add_argument(
        'target',
        nargs='?',
        default='.',
        help='Path to lint (file or directory)'
    )
    parser.add_argument(
        '--linters',
        nargs='+',
        choices=['pylint', 'flake8', 'mypy', 'black'],
        help='Specific linters to run (default: all available)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save report to file'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Create linter and run
    linter = LintingIntegration()
    results = linter.run_all_linters(
        target=args.target,
        enabled_linters=args.linters
    )
    
    # Generate and display report
    report = linter.generate_report(format=args.format)
    print(report)
    
    # Save to file if requested
    if args.output:
        linter.save_report(args.output, format=args.format)
    
    # Exit with error code if issues found
    total_issues = results['summary']['total_issues']
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == '__main__':
    main()
