#!/usr/bin/env python3
"""
Import Optimizer for Python 2 to 3 Migration

This module analyzes and optimizes Python imports after migration:
- Removes unused imports
- Sorts imports according to PEP 8 (stdlib, third-party, local)
- Removes duplicate imports
- Groups imports logically
- Detects and optionally removes wildcard imports
- Generates detailed reports of optimizations
"""

import ast
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ImportOptimizer:
    """Analyzes and optimizes Python imports in migrated code."""
    
    # Python standard library modules (Python 3)
    STDLIB_MODULES = {
        'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
        'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins',
        'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
        'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
        'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv',
        'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
        'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
        'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions', 'ftplib',
        'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp',
        'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'idlelib', 'imaplib',
        'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json',
        'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox',
        'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib',
        'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'numbers', 'operator',
        'optparse', 'os', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle',
        'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix',
        'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile',
        'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib',
        'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors',
        'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr',
        'socket', 'socketserver', 'spwd', 'sqlite3', 'ssl', 'stat', 'statistics',
        'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol', 'symtable',
        'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile',
        'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter',
        'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle',
        'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu',
        'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg',
        'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile',
        'zipimport', 'zlib', '_thread'
    }
    
    def __init__(self):
        self.issues: List[Dict] = []
        self.stats = {
            'files_analyzed': 0,
            'unused_imports': 0,
            'duplicate_imports': 0,
            'wildcard_imports': 0,
            'unsorted_imports': 0,
            'total_optimizations': 0
        }
    
    def analyze_file(self, filepath: str) -> Dict:
        """Analyze imports in a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=filepath)
            
            result = {
                'filepath': filepath,
                'imports': self._extract_imports(tree),
                'used_names': self._extract_used_names(tree),
                'issues': []
            }
            
            # Analyze for issues
            result['issues'].extend(self._check_unused_imports(result))
            result['issues'].extend(self._check_duplicate_imports(result))
            result['issues'].extend(self._check_wildcard_imports(result))
            result['issues'].extend(self._check_import_order(result))
            
            self.stats['files_analyzed'] += 1
            for issue in result['issues']:
                issue_type = issue['type']
                if issue_type == 'unused_import':
                    self.stats['unused_imports'] += 1
                elif issue_type == 'duplicate_import':
                    self.stats['duplicate_imports'] += 1
                elif issue_type == 'wildcard_import':
                    self.stats['wildcard_imports'] += 1
                elif issue_type == 'unsorted_imports':
                    self.stats['unsorted_imports'] += 1
            
            self.stats['total_optimizations'] += len(result['issues'])
            
            return result
            
        except SyntaxError as e:
            return {
                'filepath': filepath,
                'error': f"Syntax error: {e}",
                'issues': []
            }
        except Exception as e:
            return {
                'filepath': filepath,
                'error': f"Error analyzing file: {e}",
                'issues': []
            }
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict]:
        """Extract all import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'name': alias.asname or alias.name,
                        'lineno': node.lineno,
                        'is_wildcard': False
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from',
                        'module': module,
                        'name': alias.name,
                        'asname': alias.asname,
                        'lineno': node.lineno,
                        'level': node.level,
                        'is_wildcard': alias.name == '*'
                    })
        
        return imports
    
    def _extract_used_names(self, tree: ast.AST) -> Set[str]:
        """Extract all names used in the code (excluding imports)."""
        used_names = set()
        
        class NameCollector(ast.NodeVisitor):
            def __init__(self):
                self.in_import = False
                
            def visit_Import(self, node):
                pass  # Skip import statements
                
            def visit_ImportFrom(self, node):
                pass  # Skip import statements
                
            def visit_Name(self, node):
                if not self.in_import:
                    used_names.add(node.id)
                    
            def visit_Attribute(self, node):
                # Get the root name (e.g., 'os' from 'os.path.join')
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
                self.generic_visit(node)
        
        collector = NameCollector()
        collector.visit(tree)
        
        return used_names
    
    def _check_unused_imports(self, result: Dict) -> List[Dict]:
        """Check for unused imports."""
        issues = []
        used_names = result['used_names']
        
        for imp in result['imports']:
            if imp['is_wildcard']:
                continue  # Can't determine if wildcard imports are used
                
            # Check if the imported name is used
            name_to_check = imp.get('asname') or imp['name']
            
            if name_to_check not in used_names:
                issues.append({
                    'type': 'unused_import',
                    'severity': 'low',
                    'line': imp['lineno'],
                    'message': f"Unused import: {name_to_check}",
                    'suggestion': f"Remove unused import '{name_to_check}'"
                })
        
        return issues
    
    def _check_duplicate_imports(self, result: Dict) -> List[Dict]:
        """Check for duplicate imports."""
        issues = []
        seen = {}
        
        for imp in result['imports']:
            key = (imp['type'], imp['module'], imp['name'])
            
            if key in seen:
                issues.append({
                    'type': 'duplicate_import',
                    'severity': 'medium',
                    'line': imp['lineno'],
                    'message': f"Duplicate import on line {seen[key]}: {imp['name']}",
                    'suggestion': f"Remove duplicate import of '{imp['name']}'"
                })
            else:
                seen[key] = imp['lineno']
        
        return issues
    
    def _check_wildcard_imports(self, result: Dict) -> List[Dict]:
        """Check for wildcard imports."""
        issues = []
        
        for imp in result['imports']:
            if imp['is_wildcard']:
                issues.append({
                    'type': 'wildcard_import',
                    'severity': 'medium',
                    'line': imp['lineno'],
                    'message': f"Wildcard import from {imp['module']}",
                    'suggestion': f"Replace wildcard import with explicit imports"
                })
        
        return issues
    
    def _check_import_order(self, result: Dict) -> List[Dict]:
        """Check if imports follow PEP 8 ordering."""
        issues = []
        imports = result['imports']
        
        if not imports:
            return issues
        
        # Categorize imports
        stdlib = []
        third_party = []
        local = []
        
        for imp in imports:
            module = imp['module'].split('.')[0] if imp['module'] else imp['name'].split('.')[0]
            
            if imp['type'] == 'from' and imp.get('level', 0) > 0:
                local.append(imp)
            elif module in self.STDLIB_MODULES:
                stdlib.append(imp)
            elif module.startswith('_'):
                local.append(imp)
            else:
                # Heuristic: if it's a common third-party package or not in stdlib
                third_party.append(imp)
        
        # Check if they're in the right order
        expected_order = stdlib + third_party + local
        
        if len(expected_order) > 1:
            for i in range(len(expected_order) - 1):
                if expected_order[i]['lineno'] > expected_order[i + 1]['lineno']:
                    issues.append({
                        'type': 'unsorted_imports',
                        'severity': 'low',
                        'line': imports[0]['lineno'],
                        'message': 'Imports are not sorted according to PEP 8',
                        'suggestion': 'Sort imports: stdlib → third-party → local'
                    })
                    break
        
        return issues
    
    def analyze_directory(self, dirpath: str, recursive: bool = True) -> List[Dict]:
        """Analyze all Python files in a directory."""
        results = []
        
        path = Path(dirpath)
        pattern = '**/*.py' if recursive else '*.py'
        
        for filepath in path.glob(pattern):
            if filepath.is_file():
                result = self.analyze_file(str(filepath))
                if result.get('issues'):
                    results.append(result)
        
        return results
    
    def optimize_file(self, filepath: str, backup: bool = True) -> bool:
        """Optimize imports in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup if requested
            if backup:
                backup_path = f"{filepath}.bak"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            tree = ast.parse(content, filename=filepath)
            
            # Get analysis
            result = self.analyze_file(filepath)
            
            if not result.get('issues'):
                return False  # No optimization needed
            
            # Perform optimizations
            optimized_content = self._optimize_imports(content, result)
            
            # Write optimized content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            return True
            
        except Exception as e:
            print(f"Error optimizing {filepath}: {e}", file=sys.stderr)
            return False
    
    def _optimize_imports(self, content: str, result: Dict) -> str:
        """Optimize imports in file content."""
        lines = content.split('\n')
        
        # Find import section (usually at the top after docstrings)
        import_start = None
        import_end = None
        
        tree = ast.parse(content)
        import_nodes = [node for node in ast.walk(tree) 
                       if isinstance(node, (ast.Import, ast.ImportFrom))]
        
        if not import_nodes:
            return content
        
        # Get the range of import lines
        import_lines = sorted([node.lineno - 1 for node in import_nodes])
        import_start = import_lines[0]
        import_end = import_lines[-1]
        
        # Categorize and deduplicate imports
        stdlib_imports = []
        third_party_imports = []
        local_imports = []
        seen = set()
        
        for imp in result['imports']:
            # Skip if this import has issues we want to remove
            should_skip = False
            for issue in result['issues']:
                if (issue['type'] == 'unused_import' and 
                    imp['lineno'] == issue['line']):
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Create import string
            if imp['type'] == 'import':
                import_str = f"import {imp['module']}"
                if imp['name'] != imp['module']:
                    import_str += f" as {imp['name']}"
            else:
                if imp['is_wildcard']:
                    import_str = f"from {imp['module']} import *"
                else:
                    import_str = f"from {imp['module']} import {imp['name']}"
                    if imp.get('asname'):
                        import_str += f" as {imp['asname']}"
            
            # Deduplicate
            if import_str in seen:
                continue
            seen.add(import_str)
            
            # Categorize
            module = imp['module'].split('.')[0] if imp['module'] else imp['name'].split('.')[0]
            
            if imp['type'] == 'from' and imp.get('level', 0) > 0:
                local_imports.append(import_str)
            elif module in self.STDLIB_MODULES:
                stdlib_imports.append(import_str)
            else:
                third_party_imports.append(import_str)
        
        # Sort each category
        stdlib_imports.sort()
        third_party_imports.sort()
        local_imports.sort()
        
        # Build optimized import section
        optimized_imports = []
        
        if stdlib_imports:
            optimized_imports.extend(stdlib_imports)
        
        if third_party_imports:
            if stdlib_imports:
                optimized_imports.append('')  # Blank line separator
            optimized_imports.extend(third_party_imports)
        
        if local_imports:
            if stdlib_imports or third_party_imports:
                optimized_imports.append('')  # Blank line separator
            optimized_imports.extend(local_imports)
        
        # Reconstruct file
        new_lines = lines[:import_start] + optimized_imports + lines[import_end + 1:]
        
        return '\n'.join(new_lines)
    
    def generate_report(self, results: List[Dict], output_file: str = None):
        """Generate a detailed optimization report."""
        report_lines = []
        
        report_lines.append("=" * 70)
        report_lines.append("IMPORT OPTIMIZATION REPORT")
        report_lines.append("=" * 70)
        report_lines.append("")
        
        report_lines.append("Summary Statistics:")
        report_lines.append(f"  Files analyzed: {self.stats['files_analyzed']}")
        report_lines.append(f"  Unused imports: {self.stats['unused_imports']}")
        report_lines.append(f"  Duplicate imports: {self.stats['duplicate_imports']}")
        report_lines.append(f"  Wildcard imports: {self.stats['wildcard_imports']}")
        report_lines.append(f"  Unsorted imports: {self.stats['unsorted_imports']}")
        report_lines.append(f"  Total optimizations: {self.stats['total_optimizations']}")
        report_lines.append("")
        
        if results:
            report_lines.append("=" * 70)
            report_lines.append("DETAILED ISSUES")
            report_lines.append("=" * 70)
            report_lines.append("")
            
            for result in results:
                if 'error' in result:
                    report_lines.append(f"File: {result['filepath']}")
                    report_lines.append(f"  ERROR: {result['error']}")
                    report_lines.append("")
                    continue
                
                if not result['issues']:
                    continue
                
                report_lines.append(f"File: {result['filepath']}")
                
                # Group by type
                by_type = defaultdict(list)
                for issue in result['issues']:
                    by_type[issue['type']].append(issue)
                
                for issue_type, issues in sorted(by_type.items()):
                    report_lines.append(f"  {issue_type.replace('_', ' ').title()}:")
                    for issue in issues:
                        report_lines.append(f"    Line {issue['line']}: {issue['message']}")
                        report_lines.append(f"      → {issue['suggestion']}")
                
                report_lines.append("")
        else:
            report_lines.append("No issues found! Imports are well-organized.")
        
        report = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to: {output_file}")
        else:
            print(report)
        
        return report


def main():
    """Command-line interface for import optimizer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Optimize Python imports after Python 2 to 3 migration'
    )
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument(
        '--fix', 
        action='store_true',
        help='Apply optimizations to files'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files when fixing'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        default=True,
        help='Recursively process directories'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output report to file'
    )
    
    args = parser.parse_args()
    
    optimizer = ImportOptimizer()
    
    if os.path.isfile(args.path):
        if args.fix:
            success = optimizer.optimize_file(args.path, backup=not args.no_backup)
            if success:
                print(f"✓ Optimized: {args.path}")
            else:
                print(f"ℹ No optimization needed: {args.path}")
        else:
            results = [optimizer.analyze_file(args.path)]
            optimizer.generate_report(results, args.output)
    
    elif os.path.isdir(args.path):
        results = optimizer.analyze_directory(args.path, args.recursive)
        
        if args.fix:
            for result in results:
                if 'error' not in result:
                    success = optimizer.optimize_file(
                        result['filepath'], 
                        backup=not args.no_backup
                    )
                    if success:
                        print(f"✓ Optimized: {result['filepath']}")
        else:
            optimizer.generate_report(results, args.output)
    
    else:
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
