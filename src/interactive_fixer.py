#!/usr/bin/env python
"""
Interactive Fixer - Review and approve Python 2 to 3 fixes interactively

This module provides an interactive mode for the Python 2 to 3 migration,
allowing users to review each proposed fix and decide whether to apply it.
This gives users more control and confidence during the migration process.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""


@dataclass
class ProposedFix:
    """Represents a single proposed fix"""
    file_path: str
    line_number: int
    original_line: str
    fixed_line: str
    fix_type: str
    description: str
    context_before: List[str]
    context_after: List[str]


class InteractiveFixer:
    """Interactive fixer that shows each change and asks for user approval"""
    
    def __init__(self, directory: str, context_lines: int = 3, auto_backup: bool = True):
        self.directory = Path(directory).resolve()
        self.context_lines = context_lines
        self.auto_backup = auto_backup
        self.fixes = []
        self.stats = {
            'total_fixes': 0,
            'accepted': 0,
            'rejected': 0,
            'files_modified': set(),
            'fixes_by_type': {}
        }
        
    def _colorize(self, text: str, color: str, bright: bool = False) -> str:
        """Add color to text if colors are available"""
        if not COLORS_AVAILABLE:
            return text
        prefix = Style.BRIGHT if bright else ""
        return f"{prefix}{color}{text}{Style.RESET_ALL}"
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the directory"""
        python_files = []
        for root, dirs, files in os.walk(self.directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'env', '.tox', 'node_modules']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        return python_files
    
    def _analyze_file(self, file_path: Path) -> List[ProposedFix]:
        """Analyze a file and generate proposed fixes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(self._colorize(f"Error reading {file_path}: {e}", Fore.RED))
            return []
        
        proposed_fixes = []
        
        for i, line in enumerate(lines):
            fixes = self._detect_fixes_for_line(line, i + 1)
            for fix_type, description, fixed_line in fixes:
                # Get context
                context_before = lines[max(0, i - self.context_lines):i]
                context_after = lines[i + 1:min(len(lines), i + 1 + self.context_lines)]
                
                proposed_fixes.append(ProposedFix(
                    file_path=str(file_path),
                    line_number=i + 1,
                    original_line=line.rstrip('\n'),
                    fixed_line=fixed_line.rstrip('\n'),
                    fix_type=fix_type,
                    description=description,
                    context_before=[l.rstrip('\n') for l in context_before],
                    context_after=[l.rstrip('\n') for l in context_after]
                ))
        
        return proposed_fixes
    
    def _detect_fixes_for_line(self, line: str, line_num: int) -> List[Tuple[str, str, str]]:
        """Detect what fixes are needed for a line"""
        fixes = []
        
        # Print statement detection
        if re.match(r'^\s*print\s+[^(]', line) and not line.strip().startswith('#'):
            # Convert print statement to function
            match = re.match(r'^(\s*)print\s+(.+)', line)
            if match:
                indent, content = match.groups()
                # Remove trailing comma if present
                content = re.sub(r',\s*$', '', content)
                fixed = f"{indent}print({content})\n"
                fixes.append(('print_statement', 'Convert print statement to function', fixed))
        
        # Check for old-style exception handling
        if 'except' in line and ',' in line and ' as ' not in line:
            match = re.match(r'^(\s*except\s+\w+),\s*(\w+):\s*$', line)
            if match:
                indent_and_except, var_name = match.groups()
                fixed = f"{indent_and_except} as {var_name}:\n"
                fixes.append(('exception_syntax', 'Update exception syntax to use "as"', fixed))
        
        # Check for iteritems, iterkeys, itervalues
        if '.iteritems()' in line:
            fixed = line.replace('.iteritems()', '.items()')
            fixes.append(('iterator_method', 'Replace iteritems() with items()', fixed))
        elif '.iterkeys()' in line:
            fixed = line.replace('.iterkeys()', '.keys()')
            fixes.append(('iterator_method', 'Replace iterkeys() with keys()', fixed))
        elif '.itervalues()' in line:
            fixed = line.replace('.itervalues()', '.values()')
            fixes.append(('iterator_method', 'Replace itervalues() with values()', fixed))
        
        # Check for xrange
        if 'xrange(' in line:
            fixed = line.replace('xrange(', 'range(')
            fixes.append(('builtin_function', 'Replace xrange with range', fixed))
        
        # Check for raw_input
        if 'raw_input(' in line:
            fixed = line.replace('raw_input(', 'input(')
            fixes.append(('builtin_function', 'Replace raw_input with input', fixed))
        
        # Check for unicode type
        if re.search(r'\bunicode\(', line):
            fixed = re.sub(r'\bunicode\(', 'str(', line)
            fixes.append(('type_change', 'Replace unicode() with str()', fixed))
        
        # Check for basestring
        if re.search(r'\bbasestring\b', line):
            fixed = re.sub(r'\bbasestring\b', 'str', line)
            fixes.append(('type_change', 'Replace basestring with str', fixed))
        
        # Check for old imports
        import_fixes = [
            ('import urllib2', 'import urllib.request', 'Update urllib2 import'),
            ('from urllib2 import', 'from urllib.request import', 'Update urllib2 import'),
            ('import ConfigParser', 'import configparser', 'Update ConfigParser import'),
            ('from ConfigParser import', 'from configparser import', 'Update ConfigParser import'),
            ('import Queue', 'import queue', 'Update Queue import'),
            ('from Queue import', 'from queue import', 'Update Queue import'),
        ]
        
        for old, new, desc in import_fixes:
            if old in line:
                fixed = line.replace(old, new)
                fixes.append(('import_update', desc, fixed))
                break
        
        return fixes
    
    def _display_fix(self, fix: ProposedFix, fix_num: int, total: int) -> None:
        """Display a proposed fix with context"""
        print("\n" + "=" * 80)
        print(self._colorize(f"Fix {fix_num}/{total}: {fix.fix_type}", Fore.CYAN, bright=True))
        print(self._colorize(f"File: {fix.file_path}:{fix.line_number}", Fore.WHITE))
        print(self._colorize(f"Description: {fix.description}", Fore.YELLOW))
        print("-" * 80)
        
        # Show context before
        for i, context_line in enumerate(fix.context_before):
            line_no = fix.line_number - len(fix.context_before) + i
            print(self._colorize(f"  {line_no:4d} | {context_line}", Fore.WHITE, bright=False))
        
        # Show original line
        print(self._colorize(f"- {fix.line_number:4d} | {fix.original_line}", Fore.RED, bright=True))
        
        # Show fixed line
        print(self._colorize(f"+ {fix.line_number:4d} | {fix.fixed_line}", Fore.GREEN, bright=True))
        
        # Show context after
        for i, context_line in enumerate(fix.context_after):
            line_no = fix.line_number + i + 1
            print(self._colorize(f"  {line_no:4d} | {context_line}", Fore.WHITE, bright=False))
        
        print("-" * 80)
    
    def _prompt_user(self) -> str:
        """Prompt user for decision on a fix"""
        while True:
            response = input(self._colorize(
                "Apply this fix? [y]es/[n]o/[a]ll/[q]uit/[s]kip file: ",
                Fore.YELLOW,
                bright=True
            )).lower().strip()
            
            if response in ['y', 'n', 'a', 'q', 's', '']:
                return response if response else 'y'  # Default to yes
            
            print(self._colorize("Invalid input. Please enter y, n, a, q, or s.", Fore.RED))
    
    def _apply_fixes(self, file_path: str, accepted_fixes: List[ProposedFix]) -> bool:
        """Apply accepted fixes to a file"""
        if not accepted_fixes:
            return True
        
        try:
            # Create backup if enabled
            if self.auto_backup:
                backup_dir = Path('backups_interactive') / datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / Path(file_path).name
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(self._colorize(f"Backup created: {backup_path}", Fore.CYAN))
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply fixes (sorted by line number in reverse to avoid index issues)
            for fix in sorted(accepted_fixes, key=lambda x: x.line_number, reverse=True):
                if fix.line_number <= len(lines):
                    lines[fix.line_number - 1] = fix.fixed_line + '\n'
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(self._colorize(f"Error applying fixes to {file_path}: {e}", Fore.RED))
            return False
    
    def run(self) -> Dict:
        """Run interactive fixer"""
        print(self._colorize("\n🔧 Interactive Python 2 to 3 Fixer", Fore.CYAN, bright=True))
        print(self._colorize(f"Scanning directory: {self.directory}\n", Fore.WHITE))
        
        # Find Python files
        python_files = self._find_python_files()
        print(self._colorize(f"Found {len(python_files)} Python files", Fore.GREEN))
        
        # Analyze files and collect fixes
        print(self._colorize("\nAnalyzing files for potential fixes...", Fore.YELLOW))
        all_fixes = []
        for file_path in python_files:
            fixes = self._analyze_file(file_path)
            if fixes:
                all_fixes.extend(fixes)
                print(self._colorize(f"  {file_path.name}: {len(fixes)} fixes found", Fore.WHITE))
        
        if not all_fixes:
            print(self._colorize("\n✓ No fixes needed! Your code looks Python 3 compatible.", Fore.GREEN, bright=True))
            return self.stats
        
        print(self._colorize(f"\nTotal fixes found: {len(all_fixes)}", Fore.CYAN, bright=True))
        print(self._colorize("\nStarting interactive review...\n", Fore.YELLOW))
        
        # Process fixes interactively
        apply_all = False
        current_file = None
        accepted_fixes = []
        skip_current_file = False
        
        for i, fix in enumerate(all_fixes, 1):
            # Check if we've moved to a new file
            if fix.file_path != current_file:
                # Apply fixes from previous file
                if current_file and accepted_fixes:
                    if self._apply_fixes(current_file, accepted_fixes):
                        self.stats['files_modified'].add(current_file)
                    accepted_fixes = []
                
                current_file = fix.file_path
                skip_current_file = False
                print(self._colorize(f"\n{'='*80}", Fore.CYAN))
                print(self._colorize(f"Now reviewing: {current_file}", Fore.CYAN, bright=True))
                print(self._colorize(f"{'='*80}", Fore.CYAN))
            
            if skip_current_file:
                self.stats['rejected'] += 1
                continue
            
            self.stats['total_fixes'] += 1
            self.stats['fixes_by_type'][fix.fix_type] = self.stats['fixes_by_type'].get(fix.fix_type, 0) + 1
            
            # Show the fix
            self._display_fix(fix, i, len(all_fixes))
            
            # Get user decision
            if apply_all:
                decision = 'y'
                print(self._colorize("Auto-applying (all mode enabled)", Fore.GREEN))
            else:
                decision = self._prompt_user()
            
            if decision == 'q':
                print(self._colorize("\n\nQuitting interactive mode...", Fore.YELLOW))
                break
            elif decision == 'a':
                apply_all = True
                decision = 'y'
                print(self._colorize("Will auto-apply all remaining fixes", Fore.GREEN))
            elif decision == 's':
                skip_current_file = True
                print(self._colorize(f"Skipping remaining fixes in {current_file}", Fore.YELLOW))
                continue
            
            if decision == 'y':
                accepted_fixes.append(fix)
                self.stats['accepted'] += 1
                print(self._colorize("✓ Fix accepted", Fore.GREEN))
            else:
                self.stats['rejected'] += 1
                print(self._colorize("✗ Fix rejected", Fore.RED))
        
        # Apply fixes from last file
        if current_file and accepted_fixes:
            if self._apply_fixes(current_file, accepted_fixes):
                self.stats['files_modified'].add(current_file)
        
        # Display summary
        self._print_summary()
        
        return self.stats
    
    def _print_summary(self) -> None:
        """Print summary of interactive session"""
        print("\n" + "=" * 80)
        print(self._colorize("📊 Interactive Fix Summary", Fore.CYAN, bright=True))
        print("=" * 80)
        print(f"Total fixes reviewed:  {self.stats['total_fixes']}")
        print(self._colorize(f"Fixes accepted:        {self.stats['accepted']}", Fore.GREEN))
        print(self._colorize(f"Fixes rejected:        {self.stats['rejected']}", Fore.RED))
        print(f"Files modified:        {len(self.stats['files_modified'])}")
        
        if self.stats['fixes_by_type']:
            print(self._colorize("\nFixes by type:", Fore.CYAN))
            for fix_type, count in sorted(self.stats['fixes_by_type'].items()):
                print(f"  {fix_type:20s}: {count}")
        
        if self.stats['files_modified']:
            print(self._colorize("\nModified files:", Fore.CYAN))
            for file_path in sorted(self.stats['files_modified']):
                print(f"  {file_path}")
        
        print("=" * 80)


def main():
    """Main entry point for interactive fixer"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Interactive Python 2 to 3 fixer - Review each fix before applying'
    )
    parser.add_argument(
        'directory',
        help='Directory to analyze and fix'
    )
    parser.add_argument(
        '--context',
        type=int,
        default=3,
        help='Number of context lines to show (default: 3)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Disable automatic backups'
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    fixer = InteractiveFixer(
        directory=args.directory,
        context_lines=args.context,
        auto_backup=not args.no_backup
    )
    
    try:
        stats = fixer.run()
        
        # Exit with appropriate code
        if stats['total_fixes'] == 0:
            sys.exit(0)
        elif stats['accepted'] > 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(self._colorize("\n\nInterrupted by user", Fore.YELLOW))
        sys.exit(130)


if __name__ == '__main__':
    main()
