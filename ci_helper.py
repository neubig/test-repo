#!/usr/bin/env python3
"""
CI/CD Helper Script for Python 2 to 3 Migration Toolkit

This script provides a unified interface for running py2to3 checks in CI/CD environments.
It works with any CI/CD system (GitHub Actions, GitLab CI, Jenkins, CircleCI, etc.)
and provides structured output suitable for automated processing.

Usage:
    python ci_helper.py [command] [options]

Commands:
    full-check    - Run complete migration check (preflight + compatibility + stats + report)
    quick-check   - Run quick compatibility check only
    preflight     - Run preflight safety checks only
    report        - Generate HTML report only
    stats         - Collect and display migration statistics

Examples:
    # Run full check with report generation
    python ci_helper.py full-check --scan-path src/ --output reports/

    # Quick compatibility check with JSON output
    python ci_helper.py quick-check --scan-path src/ --format json

    # CI/CD mode with strict exit codes
    python ci_helper.py full-check --scan-path src/ --ci-mode --fail-on-issues
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def disable():
        """Disable color output."""
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''


class CIHelper:
    """Helper class for running py2to3 checks in CI/CD environments."""

    def __init__(self, no_color=False, ci_mode=False):
        """Initialize CI helper.
        
        Args:
            no_color: Disable colored output
            ci_mode: Enable CI/CD mode (structured output, appropriate exit codes)
        """
        self.no_color = no_color
        self.ci_mode = ci_mode
        self.results = {}
        
        if no_color or ci_mode:
            Colors.disable()
        
        # Find py2to3 executable
        self.py2to3_cmd = self._find_py2to3()
    
    def _find_py2to3(self):
        """Find the py2to3 executable."""
        # Try ./py2to3 first (local)
        if os.path.exists('./py2to3'):
            return './py2to3'
        
        # Try in same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_py2to3 = os.path.join(script_dir, 'py2to3')
        if os.path.exists(local_py2to3):
            return local_py2to3
        
        # Try in PATH
        try:
            subprocess.run(['which', 'py2to3'], check=True, capture_output=True)
            return 'py2to3'
        except subprocess.CalledProcessError:
            pass
        
        self.print_error("Could not find py2to3 executable")
        sys.exit(1)
    
    def print_header(self, text):
        """Print formatted header."""
        if not self.ci_mode:
            print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.HEADER}{text:^70}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
    
    def print_success(self, text):
        """Print success message."""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")
    
    def print_error(self, text):
        """Print error message."""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}", file=sys.stderr)
    
    def print_warning(self, text):
        """Print warning message."""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")
    
    def print_info(self, text):
        """Print info message."""
        if not self.ci_mode:
            print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")
    
    def run_command(self, cmd, capture_output=True):
        """Run a command and return the result.
        
        Args:
            cmd: Command as list of strings
            capture_output: Whether to capture output
            
        Returns:
            CompletedProcess object
        """
        self.print_info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self.print_error("Command timed out after 5 minutes")
            return None
        except Exception as e:
            self.print_error(f"Error running command: {e}")
            return None
    
    def run_preflight(self, scan_path):
        """Run preflight safety checks.
        
        Args:
            scan_path: Path to scan
            
        Returns:
            dict: Preflight results
        """
        self.print_header("Pre-Migration Safety Check")
        
        cmd = [self.py2to3_cmd, 'preflight', scan_path, '--json']
        result = self.run_command(cmd)
        
        if result and result.returncode == 0:
            try:
                preflight_data = json.loads(result.stdout)
                self.results['preflight'] = preflight_data
                
                status = preflight_data.get('status', 'UNKNOWN')
                critical = preflight_data.get('critical_issues', 0)
                
                if status == 'READY':
                    self.print_success(f"Preflight check passed: {status}")
                elif critical > 0:
                    self.print_error(f"Preflight check failed: {critical} critical issues")
                else:
                    self.print_warning(f"Preflight check warning: {status}")
                
                return preflight_data
            except json.JSONDecodeError:
                self.print_warning("Could not parse preflight results")
                return {}
        else:
            self.print_warning("Preflight check encountered issues")
            return {}
    
    def run_compatibility_check(self, scan_path):
        """Run Python 3 compatibility check.
        
        Args:
            scan_path: Path to scan
            
        Returns:
            dict: Compatibility check results
        """
        self.print_header("Python 3 Compatibility Check")
        
        # Run check with text report
        report_file = f"compatibility-report-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        cmd = [self.py2to3_cmd, 'check', scan_path, '--report', report_file]
        
        result = self.run_command(cmd, capture_output=True)
        
        # Parse results
        issue_count = 0
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                content = f.read()
                issue_count = content.count('Issue:')
        
        check_results = {
            'issue_count': issue_count,
            'report_file': report_file,
            'scan_path': scan_path
        }
        
        self.results['compatibility_check'] = check_results
        
        if issue_count == 0:
            self.print_success("No compatibility issues found")
        else:
            self.print_warning(f"Found {issue_count} compatibility issues")
        
        return check_results
    
    def run_stats_collection(self, scan_path):
        """Collect migration statistics.
        
        Args:
            scan_path: Path to scan
            
        Returns:
            dict: Statistics results
        """
        self.print_header("Migration Statistics")
        
        cmd = [self.py2to3_cmd, 'stats', 'collect', scan_path, '--save']
        result = self.run_command(cmd, capture_output=True)
        
        stats_data = {
            'collected': result is not None and result.returncode == 0,
            'output': result.stdout if result else None
        }
        
        self.results['statistics'] = stats_data
        
        if stats_data['collected']:
            self.print_success("Statistics collected successfully")
            if not self.ci_mode and result.stdout:
                print(result.stdout)
        else:
            self.print_warning("Could not collect statistics")
        
        return stats_data
    
    def generate_report(self, scan_path, output_dir):
        """Generate HTML report.
        
        Args:
            scan_path: Path that was scanned
            output_dir: Directory for output files
            
        Returns:
            dict: Report generation results
        """
        self.print_header("Report Generation")
        
        os.makedirs(output_dir, exist_ok=True)
        
        report_file = os.path.join(output_dir, 'py3-compatibility-report.html')
        cmd = [self.py2to3_cmd, 'report', '--scan-path', scan_path, '--output', report_file]
        
        result = self.run_command(cmd, capture_output=True)
        
        report_data = {
            'generated': os.path.exists(report_file),
            'report_file': report_file if os.path.exists(report_file) else None
        }
        
        self.results['report'] = report_data
        
        if report_data['generated']:
            self.print_success(f"Report generated: {report_file}")
        else:
            self.print_warning("Could not generate report")
        
        return report_data
    
    def run_full_check(self, scan_path, output_dir='ci-reports'):
        """Run complete migration check.
        
        Args:
            scan_path: Path to scan
            output_dir: Directory for output files
            
        Returns:
            dict: Complete results
        """
        self.print_info(f"Starting full migration check for: {scan_path}")
        self.print_info(f"Output directory: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Run all checks
        preflight = self.run_preflight(scan_path)
        compat = self.run_compatibility_check(scan_path)
        stats = self.run_stats_collection(scan_path)
        report = self.generate_report(scan_path, output_dir)
        
        # Compile overall results
        overall = {
            'timestamp': datetime.datetime.now().isoformat(),
            'scan_path': scan_path,
            'preflight': preflight,
            'compatibility_check': compat,
            'statistics': stats,
            'report': report
        }
        
        self.results = overall
        
        # Save results as JSON
        results_file = os.path.join(output_dir, 'ci-results.json')
        with open(results_file, 'w') as f:
            json.dump(overall, f, indent=2)
        
        self.print_success(f"Results saved to: {results_file}")
        
        return overall
    
    def run_quick_check(self, scan_path):
        """Run quick compatibility check only.
        
        Args:
            scan_path: Path to scan
            
        Returns:
            dict: Quick check results
        """
        self.print_info(f"Starting quick compatibility check for: {scan_path}")
        
        compat = self.run_compatibility_check(scan_path)
        self.results = {'compatibility_check': compat}
        
        return compat
    
    def print_summary(self):
        """Print summary of all results."""
        if self.ci_mode:
            # In CI mode, print JSON
            print(json.dumps(self.results, indent=2))
        else:
            # In normal mode, print formatted summary
            print(f"\n{Colors.BOLD}=== Migration Check Summary ==={Colors.ENDC}\n")
            
            if 'preflight' in self.results:
                status = self.results['preflight'].get('status', 'N/A')
                print(f"Preflight Check: {status}")
            
            if 'compatibility_check' in self.results:
                issues = self.results['compatibility_check'].get('issue_count', 0)
                print(f"Compatibility Issues: {issues}")
            
            if 'statistics' in self.results:
                collected = self.results['statistics'].get('collected', False)
                print(f"Statistics: {'Collected' if collected else 'Not collected'}")
            
            if 'report' in self.results:
                generated = self.results['report'].get('generated', False)
                if generated:
                    print(f"Report: {self.results['report']['report_file']}")
                else:
                    print("Report: Not generated")
    
    def get_exit_code(self, fail_on_issues=False):
        """Get appropriate exit code based on results.
        
        Args:
            fail_on_issues: Whether to fail (exit 1) if issues are found
            
        Returns:
            int: Exit code (0 = success, 1 = failure)
        """
        if not self.results:
            return 0
        
        # Check for critical preflight issues
        if 'preflight' in self.results:
            critical = self.results['preflight'].get('critical_issues', 0)
            if critical > 0:
                return 1
        
        # Check for compatibility issues if fail_on_issues is enabled
        if fail_on_issues and 'compatibility_check' in self.results:
            issues = self.results['compatibility_check'].get('issue_count', 0)
            if issues > 0:
                return 1
        
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CI/CD Helper for Python 2 to 3 Migration Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'command',
        choices=['full-check', 'quick-check', 'preflight', 'report', 'stats'],
        help='Command to run'
    )
    
    parser.add_argument(
        '--scan-path',
        default='src/',
        help='Path to scan (default: src/)'
    )
    
    parser.add_argument(
        '--output',
        default='ci-reports',
        help='Output directory for reports (default: ci-reports)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--ci-mode',
        action='store_true',
        help='Enable CI/CD mode (structured JSON output, appropriate exit codes)'
    )
    
    parser.add_argument(
        '--fail-on-issues',
        action='store_true',
        help='Exit with code 1 if compatibility issues are found'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Enable CI mode if JSON format is requested
    ci_mode = args.ci_mode or args.format == 'json'
    
    # Create helper instance
    helper = CIHelper(no_color=args.no_color, ci_mode=ci_mode)
    
    # Run requested command
    try:
        if args.command == 'full-check':
            helper.run_full_check(args.scan_path, args.output)
        elif args.command == 'quick-check':
            helper.run_quick_check(args.scan_path)
        elif args.command == 'preflight':
            helper.run_preflight(args.scan_path)
        elif args.command == 'report':
            helper.generate_report(args.scan_path, args.output)
        elif args.command == 'stats':
            helper.run_stats_collection(args.scan_path)
        
        # Print summary
        helper.print_summary()
        
        # Exit with appropriate code
        exit_code = helper.get_exit_code(fail_on_issues=args.fail_on_issues)
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        helper.print_error("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        helper.print_error(f"Unexpected error: {e}")
        if not ci_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
