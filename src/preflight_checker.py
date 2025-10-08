#!/usr/bin/env python3
"""
Pre-Migration Safety Checker

Validates the environment and project state before running Python 2 to 3 migration.
Identifies potential issues early to prevent migration failures and data loss.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


class PreflightCheck:
    """Represents a single preflight check with its result."""
    
    PASS = 'PASS'
    WARN = 'WARN'
    FAIL = 'FAIL'
    INFO = 'INFO'
    
    def __init__(self, name, status, message, details=None, fix_suggestion=None):
        """Initialize a preflight check result.
        
        Args:
            name: Name of the check
            status: Status (PASS, WARN, FAIL, INFO)
            message: Short message describing the result
            details: Optional detailed information
            fix_suggestion: Optional suggestion for fixing issues
        """
        self.name = name
        self.status = status
        self.message = message
        self.details = details or []
        self.fix_suggestion = fix_suggestion
    
    def __repr__(self):
        return f"PreflightCheck({self.name}, {self.status})"


class PreflightChecker:
    """Performs comprehensive pre-migration safety checks."""
    
    def __init__(self, project_path='.'):
        """Initialize the preflight checker.
        
        Args:
            project_path: Path to the project to check
        """
        self.project_path = Path(project_path).resolve()
        self.checks = []
    
    def run_all_checks(self, backup_dir='backup'):
        """Run all preflight checks.
        
        Args:
            backup_dir: Path to backup directory (for disk space checks)
            
        Returns:
            list: List of PreflightCheck objects
        """
        self.checks = []
        
        # Run all checks
        self.checks.append(self._check_path_exists())
        self.checks.append(self._check_python_version())
        self.checks.append(self._check_git_repository())
        self.checks.append(self._check_git_status())
        self.checks.append(self._check_git_branch())
        self.checks.append(self._check_disk_space(backup_dir))
        self.checks.append(self._check_backup_directory(backup_dir))
        self.checks.append(self._check_file_permissions())
        self.checks.append(self._check_virtual_environment())
        self.checks.append(self._check_python_files())
        self.checks.append(self._check_2to3_tool())
        self.checks.append(self._check_requirements_file())
        
        return self.checks
    
    def _check_path_exists(self):
        """Check if the project path exists and is accessible."""
        if not self.project_path.exists():
            return PreflightCheck(
                'Project Path',
                PreflightCheck.FAIL,
                f'Path does not exist: {self.project_path}',
                fix_suggestion='Verify the path and try again'
            )
        
        if not os.access(self.project_path, os.R_OK):
            return PreflightCheck(
                'Project Path',
                PreflightCheck.FAIL,
                'Path is not readable',
                fix_suggestion='Check file permissions'
            )
        
        return PreflightCheck(
            'Project Path',
            PreflightCheck.PASS,
            f'Project path is valid and accessible'
        )
    
    def _check_python_version(self):
        """Check Python version compatibility."""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3:
            return PreflightCheck(
                'Python Version',
                PreflightCheck.FAIL,
                f'Python {version_str} detected - Python 3.6+ required',
                fix_suggestion='Use Python 3.6 or higher to run migration tools'
            )
        
        if version.major == 3 and version.minor < 6:
            return PreflightCheck(
                'Python Version',
                PreflightCheck.WARN,
                f'Python {version_str} detected - Python 3.6+ recommended',
                fix_suggestion='Consider upgrading to Python 3.6 or higher'
            )
        
        return PreflightCheck(
            'Python Version',
            PreflightCheck.PASS,
            f'Python {version_str} is compatible'
        )
    
    def _check_git_repository(self):
        """Check if the project is a git repository."""
        git_dir = self.project_path / '.git'
        
        if not git_dir.exists():
            return PreflightCheck(
                'Git Repository',
                PreflightCheck.WARN,
                'Not a git repository - changes will not be version controlled',
                fix_suggestion='Initialize git: git init'
            )
        
        # Check if git command is available
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                check=True
            )
            return PreflightCheck(
                'Git Repository',
                PreflightCheck.PASS,
                'Git repository initialized'
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return PreflightCheck(
                'Git Repository',
                PreflightCheck.WARN,
                'Git repository exists but git command not found',
                fix_suggestion='Install git to track changes'
            )
    
    def _check_git_status(self):
        """Check git status for uncommitted changes."""
        git_dir = self.project_path / '.git'
        if not git_dir.exists():
            return PreflightCheck(
                'Git Status',
                PreflightCheck.INFO,
                'Skipped (not a git repository)'
            )
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                uncommitted = len(result.stdout.strip().split('\n'))
                return PreflightCheck(
                    'Git Status',
                    PreflightCheck.WARN,
                    f'{uncommitted} uncommitted change(s) detected',
                    details=result.stdout.strip().split('\n')[:10],  # Show first 10
                    fix_suggestion='Commit or stash changes before migration: git add -A && git commit -m "Pre-migration checkpoint"'
                )
            
            return PreflightCheck(
                'Git Status',
                PreflightCheck.PASS,
                'Working directory is clean'
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return PreflightCheck(
                'Git Status',
                PreflightCheck.INFO,
                'Could not check git status'
            )
    
    def _check_git_branch(self):
        """Check current git branch."""
        git_dir = self.project_path / '.git'
        if not git_dir.exists():
            return PreflightCheck(
                'Git Branch',
                PreflightCheck.INFO,
                'Skipped (not a git repository)'
            )
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branch = result.stdout.strip()
            
            if branch in ['main', 'master']:
                return PreflightCheck(
                    'Git Branch',
                    PreflightCheck.WARN,
                    f'On branch "{branch}" - consider using a feature branch',
                    fix_suggestion=f'Create a migration branch: git checkout -b python3-migration'
                )
            
            return PreflightCheck(
                'Git Branch',
                PreflightCheck.PASS,
                f'On branch "{branch}"'
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return PreflightCheck(
                'Git Branch',
                PreflightCheck.INFO,
                'Could not determine git branch'
            )
    
    def _check_disk_space(self, backup_dir):
        """Check available disk space for backups."""
        try:
            stat = shutil.disk_usage(self.project_path)
            available_gb = stat.free / (1024**3)
            
            # Estimate project size
            project_size = 0
            for root, dirs, files in os.walk(self.project_path):
                # Skip hidden dirs and common large directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', 'node_modules', '__pycache__']]
                for file in files:
                    if file.endswith('.py'):
                        try:
                            project_size += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            pass
            
            project_size_mb = project_size / (1024**2)
            
            # Check if we have at least 10x the project size available
            required_space = project_size_mb * 10
            
            details = [
                f'Available space: {available_gb:.2f} GB',
                f'Python files size: {project_size_mb:.2f} MB',
                f'Recommended free space: {required_space:.2f} MB'
            ]
            
            if available_gb < 0.1:  # Less than 100 MB
                return PreflightCheck(
                    'Disk Space',
                    PreflightCheck.FAIL,
                    'Critically low disk space',
                    details=details,
                    fix_suggestion='Free up disk space before running migration'
                )
            elif available_gb < 1.0:  # Less than 1 GB
                return PreflightCheck(
                    'Disk Space',
                    PreflightCheck.WARN,
                    'Low disk space - backups may fail',
                    details=details,
                    fix_suggestion='Consider freeing up disk space'
                )
            
            return PreflightCheck(
                'Disk Space',
                PreflightCheck.PASS,
                f'{available_gb:.2f} GB available',
                details=details
            )
        except Exception as e:
            return PreflightCheck(
                'Disk Space',
                PreflightCheck.INFO,
                f'Could not check disk space: {e}'
            )
    
    def _check_backup_directory(self, backup_dir):
        """Check if backup directory is writable."""
        backup_path = Path(backup_dir)
        
        # Check if parent directory is writable
        if backup_path.exists():
            test_path = backup_path
        else:
            test_path = backup_path.parent or Path('.')
        
        if not os.access(test_path, os.W_OK):
            return PreflightCheck(
                'Backup Directory',
                PreflightCheck.FAIL,
                f'Backup location is not writable: {backup_dir}',
                fix_suggestion='Choose a writable backup directory or fix permissions'
            )
        
        if backup_path.exists():
            # Count existing backups
            backup_count = len(list(backup_path.glob('**/*.py')))
            size_mb = sum(f.stat().st_size for f in backup_path.glob('**/*') if f.is_file()) / (1024**2)
            
            return PreflightCheck(
                'Backup Directory',
                PreflightCheck.PASS,
                f'Backup directory ready: {backup_dir}',
                details=[
                    f'Existing backups: {backup_count} files',
                    f'Backup size: {size_mb:.2f} MB'
                ]
            )
        
        return PreflightCheck(
            'Backup Directory',
            PreflightCheck.PASS,
            f'Backup directory will be created: {backup_dir}'
        )
    
    def _check_file_permissions(self):
        """Check if Python files are writable."""
        python_files = []
        unwritable = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
                    
                    if not os.access(file_path, os.W_OK):
                        unwritable.append(file_path)
        
        if unwritable:
            return PreflightCheck(
                'File Permissions',
                PreflightCheck.FAIL,
                f'{len(unwritable)} file(s) are not writable',
                details=unwritable[:10],  # Show first 10
                fix_suggestion='Fix file permissions: chmod +w <file>'
            )
        
        return PreflightCheck(
            'File Permissions',
            PreflightCheck.PASS,
            f'All {len(python_files)} Python file(s) are writable'
        )
    
    def _check_virtual_environment(self):
        """Check if running in a virtual environment."""
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if not in_venv:
            return PreflightCheck(
                'Virtual Environment',
                PreflightCheck.WARN,
                'Not running in a virtual environment',
                fix_suggestion='Consider using a virtual environment for isolation'
            )
        
        return PreflightCheck(
            'Virtual Environment',
            PreflightCheck.PASS,
            'Running in a virtual environment'
        )
    
    def _check_python_files(self):
        """Check for Python files and estimate migration scope."""
        python_files = []
        py2_indicators = 0
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
                    
                    # Quick scan for Python 2 indicators
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(10000)  # Read first 10KB
                            if any(indicator in content for indicator in ['print ', 'import urllib2', 'from __future__ import', 'basestring', '.iteritems()']):
                                py2_indicators += 1
                    except Exception:
                        pass
        
        if not python_files:
            return PreflightCheck(
                'Python Files',
                PreflightCheck.WARN,
                'No Python files found',
                fix_suggestion='Verify the project path'
            )
        
        details = [
            f'Total Python files: {len(python_files)}',
            f'Files with potential Python 2 code: {py2_indicators}'
        ]
        
        if py2_indicators > 0:
            complexity = 'Small' if py2_indicators < 5 else 'Medium' if py2_indicators < 20 else 'Large'
            details.append(f'Estimated complexity: {complexity}')
        
        return PreflightCheck(
            'Python Files',
            PreflightCheck.PASS,
            f'Found {len(python_files)} Python file(s)',
            details=details
        )
    
    def _check_2to3_tool(self):
        """Check if 2to3 tool is available."""
        try:
            result = subprocess.run(
                ['2to3', '--help'],
                capture_output=True,
                check=True
            )
            return PreflightCheck(
                '2to3 Tool',
                PreflightCheck.PASS,
                '2to3 tool is available'
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return PreflightCheck(
                '2to3 Tool',
                PreflightCheck.WARN,
                '2to3 tool not found - some features may be limited',
                fix_suggestion='Install 2to3 (usually included with Python)'
            )
    
    def _check_requirements_file(self):
        """Check for requirements file and Python 2 dependencies."""
        req_files = ['requirements.txt', 'requirements-py2.txt', 'Pipfile', 'setup.py', 'pyproject.toml']
        found_files = []
        
        for req_file in req_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                found_files.append(req_file)
        
        if not found_files:
            return PreflightCheck(
                'Dependencies',
                PreflightCheck.INFO,
                'No dependency files found'
            )
        
        # Check for Python 2 specific dependencies
        py2_deps = []
        for req_file in found_files:
            req_path = self.project_path / req_file
            try:
                with open(req_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if any(dep in content.lower() for dep in ['python_requires="2', 'python>=2', 'futures', 'typing', 'enum34']):
                        py2_deps.append(req_file)
            except Exception:
                pass
        
        details = [f'Found: {", ".join(found_files)}']
        
        if py2_deps:
            return PreflightCheck(
                'Dependencies',
                PreflightCheck.WARN,
                'Python 2 dependencies detected',
                details=details + [f'Review: {", ".join(py2_deps)}'],
                fix_suggestion='Update dependencies to Python 3 compatible versions after migration'
            )
        
        return PreflightCheck(
            'Dependencies',
            PreflightCheck.PASS,
            f'Found {len(found_files)} dependency file(s)',
            details=details
        )
    
    def get_summary(self):
        """Get summary of all checks.
        
        Returns:
            dict: Summary with counts and overall status
        """
        if not self.checks:
            return None
        
        counts = {
            PreflightCheck.PASS: 0,
            PreflightCheck.WARN: 0,
            PreflightCheck.FAIL: 0,
            PreflightCheck.INFO: 0
        }
        
        for check in self.checks:
            counts[check.status] += 1
        
        # Determine overall status
        if counts[PreflightCheck.FAIL] > 0:
            overall = 'FAILED'
            message = 'Critical issues found - migration not recommended'
        elif counts[PreflightCheck.WARN] > 0:
            overall = 'WARNING'
            message = 'Some issues detected - proceed with caution'
        else:
            overall = 'READY'
            message = 'All checks passed - ready for migration'
        
        return {
            'overall_status': overall,
            'message': message,
            'total_checks': len(self.checks),
            'passed': counts[PreflightCheck.PASS],
            'warnings': counts[PreflightCheck.WARN],
            'failures': counts[PreflightCheck.FAIL],
            'info': counts[PreflightCheck.INFO]
        }
    
    def format_report(self, verbose=False):
        """Format checks as a readable report.
        
        Args:
            verbose: Include detailed information
            
        Returns:
            str: Formatted report
        """
        lines = []
        
        # Header
        lines.append('=' * 70)
        lines.append('Pre-Migration Safety Check Report')
        lines.append('=' * 70)
        lines.append(f'Project: {self.project_path}')
        lines.append(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append('=' * 70)
        lines.append('')
        
        # Group checks by status
        status_order = [PreflightCheck.FAIL, PreflightCheck.WARN, PreflightCheck.PASS, PreflightCheck.INFO]
        status_symbols = {
            PreflightCheck.PASS: '✓',
            PreflightCheck.WARN: '⚠',
            PreflightCheck.FAIL: '✗',
            PreflightCheck.INFO: 'ℹ'
        }
        
        for status in status_order:
            status_checks = [c for c in self.checks if c.status == status]
            if not status_checks:
                continue
            
            lines.append(f'\n{status}:')
            lines.append('-' * 70)
            
            for check in status_checks:
                symbol = status_symbols.get(status, '•')
                lines.append(f'{symbol} {check.name}: {check.message}')
                
                if verbose and check.details:
                    for detail in check.details[:5]:  # Limit details
                        lines.append(f'  → {detail}')
                
                if check.fix_suggestion:
                    lines.append(f'  💡 {check.fix_suggestion}')
                
                lines.append('')
        
        # Summary
        summary = self.get_summary()
        if summary:
            lines.append('=' * 70)
            lines.append('SUMMARY')
            lines.append('=' * 70)
            lines.append(f"Status: {summary['overall_status']}")
            lines.append(f"Message: {summary['message']}")
            lines.append('')
            lines.append(f"Total Checks: {summary['total_checks']}")
            lines.append(f"  ✓ Passed: {summary['passed']}")
            lines.append(f"  ⚠ Warnings: {summary['warnings']}")
            lines.append(f"  ✗ Failed: {summary['failures']}")
            lines.append(f"  ℹ Info: {summary['info']}")
            lines.append('=' * 70)
        
        return '\n'.join(lines)


def main():
    """Command-line interface for preflight checker."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Pre-Migration Safety Checker for Python 2 to 3 migration'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path to check (default: current directory)'
    )
    parser.add_argument(
        '-b', '--backup-dir',
        default='backup',
        help='Backup directory to check (default: backup)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    checker = PreflightChecker(args.path)
    checker.run_all_checks(args.backup_dir)
    
    if args.json:
        import json
        summary = checker.get_summary()
        checks_data = [
            {
                'name': c.name,
                'status': c.status,
                'message': c.message,
                'details': c.details,
                'fix_suggestion': c.fix_suggestion
            }
            for c in checker.checks
        ]
        result = {
            'summary': summary,
            'checks': checks_data
        }
        print(json.dumps(result, indent=2))
    else:
        print(checker.format_report(verbose=args.verbose))
    
    # Exit with appropriate code
    summary = checker.get_summary()
    if summary['overall_status'] == 'FAILED':
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
