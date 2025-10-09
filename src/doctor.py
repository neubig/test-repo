#!/usr/bin/env python3
"""
Migration Doctor - Health Check and Diagnostics Tool

Comprehensive health checks for the py2to3 migration toolkit and projects.
Similar to 'brew doctor' or 'flutter doctor', this tool diagnoses common
issues and provides actionable recommendations.
"""

import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class HealthCheck:
    """Represents a single health check with status and recommendations."""
    
    STATUS_OK = "OK"
    STATUS_WARNING = "WARNING"
    STATUS_ERROR = "ERROR"
    STATUS_INFO = "INFO"
    
    def __init__(self, name: str, status: str, message: str, 
                 recommendation: str = None, details: List[str] = None):
        self.name = name
        self.status = status
        self.message = message
        self.recommendation = recommendation
        self.details = details or []


class MigrationDoctor:
    """Performs comprehensive health checks on migration environment and project."""
    
    def __init__(self, project_path: str = ".", quiet: bool = False):
        self.project_path = Path(project_path).resolve()
        self.checks: List[HealthCheck] = []
        self.quiet = quiet
        
    def run_all_checks(self) -> List[HealthCheck]:
        """Run all health checks and return results."""
        if not self.quiet:
            print("🏥 Running Migration Doctor...\n", file=sys.stderr)
        
        # Environment checks
        self._check_python_version()
        self._check_python3_available()
        self._check_python2_available()
        self._check_git_available()
        self._check_required_packages()
        
        # Project checks
        self._check_project_structure()
        self._check_config_files()
        self._check_backup_directory()
        self._check_migration_state()
        
        # Code quality checks
        self._check_syntax_errors()
        self._check_common_issues()
        self._check_import_errors()
        
        # Integration checks
        self._check_git_status()
        self._check_dependencies()
        
        return self.checks
    
    def _add_check(self, check: HealthCheck):
        """Add a health check result."""
        self.checks.append(check)
    
    def _check_python_version(self):
        """Check current Python version."""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major >= 3 and version.minor >= 6:
            self._add_check(HealthCheck(
                "Python Version",
                HealthCheck.STATUS_OK,
                f"Python {version_str} is installed and compatible",
            ))
        elif version.major >= 3:
            self._add_check(HealthCheck(
                "Python Version",
                HealthCheck.STATUS_WARNING,
                f"Python {version_str} is old, consider upgrading",
                "Upgrade to Python 3.6 or newer for best compatibility",
                ["Some features may not work on older Python versions"]
            ))
        else:
            self._add_check(HealthCheck(
                "Python Version",
                HealthCheck.STATUS_ERROR,
                f"Python {version_str} is not Python 3",
                "Install Python 3.6 or newer",
                ["The migration toolkit requires Python 3"]
            ))
    
    def _check_python3_available(self):
        """Check if python3 command is available."""
        if shutil.which("python3"):
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip()
            self._add_check(HealthCheck(
                "Python 3 Command",
                HealthCheck.STATUS_OK,
                f"python3 command available: {version}"
            ))
        else:
            self._add_check(HealthCheck(
                "Python 3 Command",
                HealthCheck.STATUS_WARNING,
                "python3 command not found in PATH",
                "Ensure Python 3 is installed and in your PATH",
                ["Some tools may expect 'python3' to be available"]
            ))
    
    def _check_python2_available(self):
        """Check if python2 is available (useful for benchmarking)."""
        if shutil.which("python2"):
            result = subprocess.run(
                ["python2", "--version"],
                capture_output=True,
                text=True
            )
            version = result.stderr.strip() or result.stdout.strip()
            self._add_check(HealthCheck(
                "Python 2 Command",
                HealthCheck.STATUS_INFO,
                f"python2 command available: {version}",
                details=["Useful for performance benchmarking"]
            ))
        else:
            self._add_check(HealthCheck(
                "Python 2 Command",
                HealthCheck.STATUS_INFO,
                "python2 command not found (optional)",
                details=["Python 2 is optional, only needed for benchmarking features"]
            ))
    
    def _check_git_available(self):
        """Check if git is available."""
        if shutil.which("git"):
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip()
            self._add_check(HealthCheck(
                "Git",
                HealthCheck.STATUS_OK,
                f"Git is available: {version}"
            ))
        else:
            self._add_check(HealthCheck(
                "Git",
                HealthCheck.STATUS_WARNING,
                "Git not found in PATH",
                "Install Git for version control integration",
                ["Git integration features will not work without Git"]
            ))
    
    def _check_required_packages(self):
        """Check if required Python packages are installed."""
        required = ["ast"]  # Built-in
        optional = ["pytest", "coverage", "black", "isort", "mypy", "pylint"]
        
        missing_optional = []
        for pkg in optional:
            spec = importlib.util.find_spec(pkg)
            if spec is None:
                missing_optional.append(pkg)
        
        if not missing_optional:
            self._add_check(HealthCheck(
                "Optional Packages",
                HealthCheck.STATUS_OK,
                "All optional packages are installed"
            ))
        else:
            self._add_check(HealthCheck(
                "Optional Packages",
                HealthCheck.STATUS_INFO,
                f"Some optional packages are missing: {', '.join(missing_optional)}",
                f"Install with: pip install {' '.join(missing_optional)}",
                ["These packages enable additional features like testing, formatting, and linting"]
            ))
    
    def _check_project_structure(self):
        """Check project directory structure."""
        if not self.project_path.exists():
            self._add_check(HealthCheck(
                "Project Path",
                HealthCheck.STATUS_ERROR,
                f"Project path does not exist: {self.project_path}",
                "Provide a valid project path"
            ))
            return
        
        # Check for Python files
        py_files = list(self.project_path.rglob("*.py"))
        if not py_files:
            self._add_check(HealthCheck(
                "Project Structure",
                HealthCheck.STATUS_WARNING,
                "No Python files found in project",
                "Ensure you're in the correct directory",
                ["Expected to find .py files for migration"]
            ))
        else:
            self._add_check(HealthCheck(
                "Project Structure",
                HealthCheck.STATUS_OK,
                f"Found {len(py_files)} Python files"
            ))
    
    def _check_config_files(self):
        """Check for configuration files."""
        config_files = [
            ".py2to3.json",
            "py2to3.json",
            ".py2to3",
            "setup.py",
            "setup.cfg",
            "pyproject.toml"
        ]
        
        found_configs = []
        for config in config_files:
            config_path = self.project_path / config
            if config_path.exists():
                found_configs.append(config)
        
        if found_configs:
            self._add_check(HealthCheck(
                "Configuration Files",
                HealthCheck.STATUS_OK,
                f"Found config files: {', '.join(found_configs)}"
            ))
        else:
            self._add_check(HealthCheck(
                "Configuration Files",
                HealthCheck.STATUS_INFO,
                "No configuration files found",
                "Run 'py2to3 config init' to create a config file",
                ["Configuration files are optional but recommended"]
            ))
    
    def _check_backup_directory(self):
        """Check backup directory status."""
        backup_dirs = [
            self.project_path / "backup",
            self.project_path / ".migration_backups",
            self.project_path / "backups"
        ]
        
        found_backup = None
        for backup_dir in backup_dirs:
            if backup_dir.exists() and backup_dir.is_dir():
                found_backup = backup_dir
                break
        
        if found_backup:
            backup_files = list(found_backup.rglob("*.py"))
            self._add_check(HealthCheck(
                "Backup Directory",
                HealthCheck.STATUS_OK,
                f"Backup directory exists: {found_backup.name} ({len(backup_files)} files)"
            ))
        else:
            self._add_check(HealthCheck(
                "Backup Directory",
                HealthCheck.STATUS_INFO,
                "No backup directory found yet",
                details=["Backups will be created automatically when you run fixes"]
            ))
    
    def _check_migration_state(self):
        """Check migration state directory."""
        state_dir = self.project_path / ".migration_state"
        
        if state_dir.exists():
            state_files = list(state_dir.glob("*.json"))
            self._add_check(HealthCheck(
                "Migration State",
                HealthCheck.STATUS_OK,
                f"Migration state tracked: {len(state_files)} files"
            ))
        else:
            self._add_check(HealthCheck(
                "Migration State",
                HealthCheck.STATUS_INFO,
                "No migration state found",
                details=["State tracking begins when you start migration"]
            ))
    
    def _check_syntax_errors(self):
        """Check for Python syntax errors in the project."""
        py_files = list(self.project_path.rglob("*.py"))
        syntax_errors = []
        
        for py_file in py_files[:50]:  # Limit to first 50 files for performance
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                syntax_errors.append(f"{py_file.name}: {e}")
            except Exception:
                pass  # Skip files that can't be read
        
        if syntax_errors:
            self._add_check(HealthCheck(
                "Syntax Errors",
                HealthCheck.STATUS_ERROR,
                f"Found {len(syntax_errors)} files with syntax errors",
                "Fix syntax errors before migration",
                syntax_errors[:5]  # Show first 5
            ))
        else:
            self._add_check(HealthCheck(
                "Syntax Errors",
                HealthCheck.STATUS_OK,
                "No syntax errors detected"
            ))
    
    def _check_common_issues(self):
        """Check for common Python 2 patterns."""
        py_files = list(self.project_path.rglob("*.py"))
        py2_patterns = {
            "print statements": r'print\s+"',
            "print statements (2)": r"print\s+'",
            "except with comma": r'except\s+\w+\s*,\s*\w+:',
            "old-style string format": r'%[sd]',
            "xrange": r'\bxrange\(',
            "iteritems": r'\.iteritems\(',
        }
        
        found_issues = {}
        for py_file in py_files[:50]:  # Limit for performance
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern_name, pattern in py2_patterns.items():
                        if re.search(pattern, content):
                            if pattern_name not in found_issues:
                                found_issues[pattern_name] = 0
                            found_issues[pattern_name] += 1
            except Exception:
                pass
        
        if found_issues:
            issues_str = ", ".join([f"{v}x {k}" for k, v in found_issues.items()])
            self._add_check(HealthCheck(
                "Python 2 Patterns",
                HealthCheck.STATUS_WARNING,
                f"Found Python 2 patterns: {issues_str}",
                "Run 'py2to3 fix' to automatically convert these patterns",
                list(found_issues.keys())
            ))
        else:
            self._add_check(HealthCheck(
                "Python 2 Patterns",
                HealthCheck.STATUS_OK,
                "No obvious Python 2 patterns detected"
            ))
    
    def _check_import_errors(self):
        """Check for common import errors."""
        py2_imports = [
            "urllib2",
            "ConfigParser",
            "Queue",
            "SocketServer",
            "__builtin__",
        ]
        
        py_files = list(self.project_path.rglob("*.py"))
        found_imports = {}
        
        for py_file in py_files[:50]:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for imp in py2_imports:
                        if re.search(rf'\bimport\s+{imp}\b', content) or \
                           re.search(rf'\bfrom\s+{imp}\b', content):
                            if imp not in found_imports:
                                found_imports[imp] = 0
                            found_imports[imp] += 1
            except Exception:
                pass
        
        if found_imports:
            imports_str = ", ".join([f"{k} ({v}x)" for k, v in found_imports.items()])
            self._add_check(HealthCheck(
                "Python 2 Imports",
                HealthCheck.STATUS_ERROR,
                f"Found Python 2 imports: {imports_str}",
                "Run 'py2to3 fix' to update imports automatically",
                list(found_imports.keys())
            ))
        else:
            self._add_check(HealthCheck(
                "Python 2 Imports",
                HealthCheck.STATUS_OK,
                "No Python 2 imports detected"
            ))
    
    def _check_git_status(self):
        """Check git repository status."""
        git_dir = self.project_path / ".git"
        if not git_dir.exists():
            self._add_check(HealthCheck(
                "Git Repository",
                HealthCheck.STATUS_INFO,
                "Not a git repository",
                "Run 'git init' to enable version control",
                ["Git is recommended for tracking migration progress"]
            ))
            return
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                if changes:
                    self._add_check(HealthCheck(
                        "Git Status",
                        HealthCheck.STATUS_WARNING,
                        f"You have {len(changes)} uncommitted changes",
                        "Commit your changes before running migration",
                        ["Uncommitted changes make it harder to track migration progress"]
                    ))
                else:
                    self._add_check(HealthCheck(
                        "Git Status",
                        HealthCheck.STATUS_OK,
                        "Working directory is clean"
                    ))
        except Exception:
            pass
    
    def _check_dependencies(self):
        """Check project dependencies."""
        req_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "Pipfile",
            "poetry.lock",
            "pyproject.toml"
        ]
        
        found_deps = []
        for req_file in req_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                found_deps.append(req_file)
        
        if found_deps:
            self._add_check(HealthCheck(
                "Dependency Files",
                HealthCheck.STATUS_OK,
                f"Found dependency files: {', '.join(found_deps)}"
            ))
        else:
            self._add_check(HealthCheck(
                "Dependency Files",
                HealthCheck.STATUS_INFO,
                "No dependency files found",
                details=["Consider creating a requirements.txt for your project"]
            ))
    
    def print_results(self):
        """Print health check results in a formatted way."""
        # Count by status
        counts = {
            HealthCheck.STATUS_OK: 0,
            HealthCheck.STATUS_WARNING: 0,
            HealthCheck.STATUS_ERROR: 0,
            HealthCheck.STATUS_INFO: 0
        }
        
        for check in self.checks:
            counts[check.status] += 1
        
        # Print summary
        print("=" * 70)
        print("MIGRATION DOCTOR REPORT".center(70))
        print("=" * 70)
        print()
        
        # Print each check
        status_icons = {
            HealthCheck.STATUS_OK: "✓",
            HealthCheck.STATUS_WARNING: "⚠",
            HealthCheck.STATUS_ERROR: "✗",
            HealthCheck.STATUS_INFO: "ℹ"
        }
        
        status_colors = {
            HealthCheck.STATUS_OK: "\033[92m",      # Green
            HealthCheck.STATUS_WARNING: "\033[93m",  # Yellow
            HealthCheck.STATUS_ERROR: "\033[91m",    # Red
            HealthCheck.STATUS_INFO: "\033[94m"      # Blue
        }
        
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        
        for check in self.checks:
            icon = status_icons[check.status]
            color = status_colors[check.status]
            
            print(f"{color}{icon} {BOLD}{check.name}{ENDC}")
            print(f"  {check.message}")
            
            if check.recommendation:
                print(f"  💡 Recommendation: {check.recommendation}")
            
            if check.details:
                for detail in check.details[:3]:  # Show first 3 details
                    print(f"     • {detail}")
                if len(check.details) > 3:
                    print(f"     • ... and {len(check.details) - 3} more")
            
            print()
        
        # Print summary
        print("=" * 70)
        print("SUMMARY".center(70))
        print("=" * 70)
        print()
        print(f"  ✓ {counts[HealthCheck.STATUS_OK]} checks passed")
        print(f"  ⚠ {counts[HealthCheck.STATUS_WARNING]} warnings")
        print(f"  ✗ {counts[HealthCheck.STATUS_ERROR]} errors")
        print(f"  ℹ {counts[HealthCheck.STATUS_INFO]} informational")
        print()
        
        # Overall status
        if counts[HealthCheck.STATUS_ERROR] > 0:
            print(f"\033[91m❌ Action required: Fix {counts[HealthCheck.STATUS_ERROR]} error(s) before migration{ENDC}")
        elif counts[HealthCheck.STATUS_WARNING] > 0:
            print(f"\033[93m⚠️  Ready with warnings: Address {counts[HealthCheck.STATUS_WARNING]} warning(s) if possible{ENDC}")
        else:
            print(f"\033[92m✅ All systems go! Your environment is ready for migration{ENDC}")
        
        print()


def main():
    """Run migration doctor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migration Doctor - Diagnose migration environment and project health"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project path to check (default: current directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    doctor = MigrationDoctor(args.path, quiet=args.json)
    doctor.run_all_checks()
    
    if args.json:
        # Output as JSON
        results = {
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "message": check.message,
                    "recommendation": check.recommendation,
                    "details": check.details
                }
                for check in doctor.checks
            ]
        }
        print(json.dumps(results, indent=2))
    else:
        doctor.print_results()


if __name__ == "__main__":
    main()
