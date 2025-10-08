#!/usr/bin/env python3
"""
Freeze Guard - Prevent Python 2 code from being introduced during migration.

This module provides functionality to "freeze" files/directories that have been
migrated to Python 3, preventing Python 2 patterns from being re-introduced.
Useful for maintaining migration progress in active development environments.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime

# Try to import verifier for Python 2 pattern detection
try:
    from verifier import check_file, PY2_PATTERNS
except ImportError:
    PY2_PATTERNS = []
    check_file = None


class FreezeConfig:
    """Manage freeze guard configuration."""
    
    def __init__(self, config_path: str = ".freeze-guard.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "frozen_paths": [],
            "excluded_patterns": [],
            "strict_mode": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def save(self):
        """Save configuration to file."""
        self.config["updated_at"] = datetime.now().isoformat()
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_frozen_path(self, path: str):
        """Add a path to frozen list."""
        if path not in self.config["frozen_paths"]:
            self.config["frozen_paths"].append(path)
            self.save()
    
    def remove_frozen_path(self, path: str):
        """Remove a path from frozen list."""
        if path in self.config["frozen_paths"]:
            self.config["frozen_paths"].remove(path)
            self.save()
    
    def is_frozen(self, path: str) -> bool:
        """Check if a path is frozen."""
        path = Path(path).resolve()
        for frozen in self.config["frozen_paths"]:
            frozen_path = Path(frozen).resolve()
            if path == frozen_path or frozen_path in path.parents:
                return True
        return False
    
    def get_frozen_paths(self) -> List[str]:
        """Get all frozen paths."""
        return self.config["frozen_paths"]


class FreezeViolation:
    """Represents a violation of freeze guard rules."""
    
    def __init__(self, file_path: str, pattern: str, line_num: int, line: str, severity: str = "error"):
        self.file_path = file_path
        self.pattern = pattern
        self.line_num = line_num
        self.line = line.strip()
        self.severity = severity
    
    def __str__(self):
        return f"{self.file_path}:{self.line_num}: {self.pattern} - {self.line}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "file": self.file_path,
            "pattern": self.pattern,
            "line": self.line_num,
            "code": self.line,
            "severity": self.severity
        }


class FreezeGuard:
    """Main freeze guard implementation."""
    
    def __init__(self, config_path: str = ".freeze-guard.json"):
        self.config = FreezeConfig(config_path)
        self.violations: List[FreezeViolation] = []
    
    def check_file_for_py2_patterns(self, file_path: str) -> List[FreezeViolation]:
        """Check a single file for Python 2 patterns."""
        violations = []
        
        if not os.path.exists(file_path):
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
            return violations
        
        # Define Python 2 patterns to check
        patterns = {
            'print statement': [
                (lambda l: 'print ' in l and not l.strip().startswith('#') and 'print(' not in l, 
                 'Print statement without parentheses'),
            ],
            'old imports': [
                (lambda l: 'import urllib2' in l or 'from urllib2' in l, 
                 'Python 2 urllib2 import'),
                (lambda l: 'import ConfigParser' in l or 'from ConfigParser' in l,
                 'Python 2 ConfigParser import'),
                (lambda l: 'import Queue' in l or 'from Queue' in l,
                 'Python 2 Queue import'),
            ],
            'string types': [
                (lambda l: 'basestring' in l and not l.strip().startswith('#'),
                 'Python 2 basestring usage'),
                (lambda l: 'unicode(' in l and not l.strip().startswith('#'),
                 'Python 2 unicode() function'),
            ],
            'dict methods': [
                (lambda l: '.iteritems()' in l and not l.strip().startswith('#'),
                 'Python 2 iteritems() method'),
                (lambda l: '.iterkeys()' in l and not l.strip().startswith('#'),
                 'Python 2 iterkeys() method'),
                (lambda l: '.itervalues()' in l and not l.strip().startswith('#'),
                 'Python 2 itervalues() method'),
            ],
            'range': [
                (lambda l: 'xrange(' in l and not l.strip().startswith('#'),
                 'Python 2 xrange() function'),
            ],
            'exceptions': [
                (lambda l: 'except ' in l and ', e' in l and ' as ' not in l,
                 'Python 2 exception syntax'),
            ],
        }
        
        for line_num, line in enumerate(lines, 1):
            for category, checks in patterns.items():
                for check_func, description in checks:
                    try:
                        if check_func(line):
                            violations.append(FreezeViolation(
                                file_path,
                                description,
                                line_num,
                                line,
                                "error"
                            ))
                    except Exception:
                        # Skip lines that cause errors in checking
                        pass
        
        return violations
    
    def check_files(self, file_paths: List[str], only_frozen: bool = False) -> List[FreezeViolation]:
        """Check multiple files for violations."""
        all_violations = []
        
        for file_path in file_paths:
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
            
            # If only_frozen is True, skip non-frozen files
            if only_frozen and not self.config.is_frozen(file_path):
                continue
            
            violations = self.check_file_for_py2_patterns(file_path)
            all_violations.extend(violations)
        
        self.violations = all_violations
        return all_violations
    
    def check_git_staged(self) -> Tuple[List[FreezeViolation], List[str]]:
        """Check git staged files for violations."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                capture_output=True,
                text=True,
                check=True
            )
            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            return [], []
        except FileNotFoundError:
            print("Warning: git not found", file=sys.stderr)
            return [], []
        
        violations = self.check_files(staged_files, only_frozen=True)
        return violations, staged_files
    
    def check_directory(self, directory: str, recursive: bool = True) -> List[FreezeViolation]:
        """Check all Python files in a directory."""
        files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return []
        
        if recursive:
            files = list(dir_path.rglob('*.py'))
        else:
            files = list(dir_path.glob('*.py'))
        
        return self.check_files([str(f) for f in files])
    
    def install_pre_commit_hook(self) -> bool:
        """Install pre-commit hook for freeze guard."""
        git_dir = Path('.git')
        if not git_dir.exists():
            print("Error: Not a git repository", file=sys.stderr)
            return False
        
        hooks_dir = git_dir / 'hooks'
        hooks_dir.mkdir(exist_ok=True)
        
        hook_path = hooks_dir / 'pre-commit'
        
        hook_content = '''#!/bin/bash
# Freeze Guard pre-commit hook
# Prevents Python 2 code from being committed to frozen files

# Run freeze guard check
python3 -c "
import sys
sys.path.insert(0, 'src')
from freeze_guard import FreezeGuard

guard = FreezeGuard()
violations, files = guard.check_git_staged()

if violations:
    print('\\n❌ Freeze Guard: Python 2 patterns detected in frozen files!')
    print('=' * 70)
    for v in violations:
        print(f'  {v.file_path}:{v.line_num}')
        print(f'    ⚠️  {v.pattern}')
        print(f'    📝 {v.line}')
        print()
    print('=' * 70)
    print(f'Found {len(violations)} violation(s) in {len(set(v.file_path for v in violations))} file(s)')
    print('\\nPlease fix these issues before committing.')
    print('Or unfreeze the files with: ./py2to3 freeze unmark <path>')
    sys.exit(1)
else:
    checked_frozen = [f for f in files if guard.config.is_frozen(f)]
    if checked_frozen:
        print(f'✅ Freeze Guard: Checked {len(checked_frozen)} frozen file(s) - all clear!')
    sys.exit(0)
"

exit $?
'''
        
        with open(hook_path, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        os.chmod(hook_path, 0o755)
        
        print(f"✅ Freeze Guard pre-commit hook installed at {hook_path}")
        return True
    
    def generate_report(self, format: str = 'text') -> str:
        """Generate a report of violations."""
        if format == 'json':
            return json.dumps({
                "violations": [v.to_dict() for v in self.violations],
                "total": len(self.violations),
                "files_affected": len(set(v.file_path for v in self.violations))
            }, indent=2)
        
        # Text format
        if not self.violations:
            return "✅ No Python 2 patterns detected!"
        
        report = []
        report.append(f"❌ Found {len(self.violations)} Python 2 pattern(s) in {len(set(v.file_path for v in self.violations))} file(s)")
        report.append("=" * 70)
        
        # Group by file
        by_file = {}
        for v in self.violations:
            if v.file_path not in by_file:
                by_file[v.file_path] = []
            by_file[v.file_path].append(v)
        
        for file_path, violations in sorted(by_file.items()):
            report.append(f"\n📄 {file_path}")
            for v in violations:
                report.append(f"  Line {v.line_num}: {v.pattern}")
                report.append(f"    {v.line}")
        
        report.append("\n" + "=" * 70)
        return "\n".join(report)


def main():
    """Command-line interface for freeze guard."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Freeze Guard - Prevent Python 2 code from being re-introduced'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # check command
    check_parser = subparsers.add_parser('check', help='Check files for Python 2 patterns')
    check_parser.add_argument('paths', nargs='*', help='Files or directories to check')
    check_parser.add_argument('--staged', action='store_true', help='Check git staged files only')
    check_parser.add_argument('--frozen-only', action='store_true', help='Check frozen files only')
    check_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    # mark command
    mark_parser = subparsers.add_parser('mark', help='Mark paths as frozen (Python 3 only)')
    mark_parser.add_argument('paths', nargs='+', help='Paths to mark as frozen')
    
    # unmark command
    unmark_parser = subparsers.add_parser('unmark', help='Unmark frozen paths')
    unmark_parser.add_argument('paths', nargs='+', help='Paths to unmark')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show frozen paths status')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # install-hook command
    hook_parser = subparsers.add_parser('install-hook', help='Install git pre-commit hook')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    guard = FreezeGuard()
    
    if args.command == 'check':
        if args.staged:
            violations, files = guard.check_git_staged()
            if not violations:
                checked_frozen = [f for f in files if guard.config.is_frozen(f)]
                if checked_frozen:
                    print(f"✅ Checked {len(checked_frozen)} frozen file(s) - all clear!")
                else:
                    print("✅ No frozen files in staged changes")
        else:
            paths = args.paths if args.paths else ['.']
            for path in paths:
                if os.path.isfile(path):
                    violations = guard.check_files([path], only_frozen=args.frozen_only)
                else:
                    violations = guard.check_directory(path)
        
        print(guard.generate_report(format=args.format))
        return 1 if violations else 0
    
    elif args.command == 'mark':
        for path in args.paths:
            if not os.path.exists(path):
                print(f"Warning: {path} does not exist", file=sys.stderr)
                continue
            guard.config.add_frozen_path(path)
            print(f"✅ Marked as frozen: {path}")
        return 0
    
    elif args.command == 'unmark':
        for path in args.paths:
            guard.config.remove_frozen_path(path)
            print(f"✅ Unmarked: {path}")
        return 0
    
    elif args.command == 'status':
        frozen_paths = guard.config.get_frozen_paths()
        
        if args.json:
            print(json.dumps({
                "frozen_paths": frozen_paths,
                "total": len(frozen_paths)
            }, indent=2))
        else:
            if not frozen_paths:
                print("No frozen paths configured")
            else:
                print(f"🔒 Frozen Paths ({len(frozen_paths)}):")
                for path in frozen_paths:
                    exists = "✓" if os.path.exists(path) else "✗"
                    print(f"  [{exists}] {path}")
        return 0
    
    elif args.command == 'install-hook':
        success = guard.install_pre_commit_hook()
        return 0 if success else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
