#!/usr/bin/env python3
"""
Pattern Search Tool for Python 2 to 3 Migration

Search for specific Python 2 patterns in your codebase with context and highlighting.
This tool helps identify patterns before migration and track specific issues.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class PatternSearcher:
    """Search for Python 2 patterns in codebase."""
    
    # Define common Python 2 patterns
    PATTERNS = {
        'print_statement': {
            'regex': r'\bprint\s+(?![(\[])',
            'description': 'Print statements (not function calls)',
            'example': 'print "hello"'
        },
        'except_comma': {
            'regex': r'except\s+\w+\s*,\s*\w+\s*:',
            'description': 'Old-style exception syntax',
            'example': 'except Exception, e:'
        },
        'iteritems': {
            'regex': r'\.iteritems\s*\(',
            'description': 'dict.iteritems() method',
            'example': 'dict.iteritems()'
        },
        'iterkeys': {
            'regex': r'\.iterkeys\s*\(',
            'description': 'dict.iterkeys() method',
            'example': 'dict.iterkeys()'
        },
        'itervalues': {
            'regex': r'\.itervalues\s*\(',
            'description': 'dict.itervalues() method',
            'example': 'dict.itervalues()'
        },
        'xrange': {
            'regex': r'\bxrange\s*\(',
            'description': 'xrange() function',
            'example': 'xrange(10)'
        },
        'basestring': {
            'regex': r'\bbasestring\b',
            'description': 'basestring type',
            'example': 'isinstance(x, basestring)'
        },
        'unicode': {
            'regex': r'\bunicode\s*\(',
            'description': 'unicode() function',
            'example': 'unicode(text)'
        },
        'long_type': {
            'regex': r'\blong\s*\(',
            'description': 'long() type',
            'example': 'long(123)'
        },
        'urllib2': {
            'regex': r'\burllib2\b',
            'description': 'urllib2 module (renamed)',
            'example': 'import urllib2'
        },
        'configparser': {
            'regex': r'\bConfigParser\b',
            'description': 'ConfigParser module (renamed to lowercase)',
            'example': 'import ConfigParser'
        },
        'raw_input': {
            'regex': r'\braw_input\s*\(',
            'description': 'raw_input() function',
            'example': 'raw_input("Enter: ")'
        },
        'execfile': {
            'regex': r'\bexecfile\s*\(',
            'description': 'execfile() function',
            'example': 'execfile("script.py")'
        },
        'has_key': {
            'regex': r'\.has_key\s*\(',
            'description': 'dict.has_key() method',
            'example': 'dict.has_key(key)'
        },
        'oldstyle_class': {
            'regex': r'^class\s+\w+\s*:',
            'description': 'Old-style class definition',
            'example': 'class MyClass:'
        },
        'cmp_function': {
            'regex': r'\bcmp\s*\(',
            'description': 'cmp() function',
            'example': 'cmp(a, b)'
        },
        'apply': {
            'regex': r'\bapply\s*\(',
            'description': 'apply() function',
            'example': 'apply(func, args)'
        },
        'reduce': {
            'regex': r'\breduce\s*\(',
            'description': 'reduce() function (moved to functools)',
            'example': 'reduce(lambda x,y: x+y, list)'
        },
        'file_builtin': {
            'regex': r'\bfile\s*\(',
            'description': 'file() builtin',
            'example': 'file("path.txt")'
        }
    }
    
    def __init__(self, root_path: str = '.', context_lines: int = 2):
        """Initialize pattern searcher.
        
        Args:
            root_path: Root directory to search
            context_lines: Number of context lines to show around matches
        """
        self.root_path = Path(root_path).resolve()
        self.context_lines = context_lines
        self.results = defaultdict(list)
        self.stats = defaultdict(int)
        
    def search(self, patterns: List[str] = None, include_all: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Search for patterns in Python files.
        
        Args:
            patterns: List of pattern names to search for (None = all)
            include_all: Include all patterns regardless of patterns parameter
            
        Returns:
            Dictionary mapping pattern names to lists of matches
        """
        # Determine which patterns to search for
        if include_all or patterns is None:
            search_patterns = self.PATTERNS.keys()
        else:
            search_patterns = [p for p in patterns if p in self.PATTERNS]
            if not search_patterns:
                raise ValueError(f"No valid patterns specified. Available: {', '.join(self.PATTERNS.keys())}")
        
        # Find all Python files
        python_files = self._find_python_files()
        
        # Search each file
        for file_path in python_files:
            self._search_file(file_path, search_patterns)
        
        return dict(self.results)
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the directory tree."""
        python_files = []
        
        if self.root_path.is_file():
            if self.root_path.suffix == '.py':
                return [self.root_path]
            return []
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.tox', 'venv', 'env', 'node_modules', '.eggs'}]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _search_file(self, file_path: Path, patterns: List[str]):
        """Search a single file for patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for pattern_name in patterns:
                pattern_info = self.PATTERNS[pattern_name]
                regex = re.compile(pattern_info['regex'], re.MULTILINE)
                
                for line_num, line in enumerate(lines, start=1):
                    matches = regex.finditer(line)
                    for match in matches:
                        # Get context lines
                        start_line = max(0, line_num - self.context_lines - 1)
                        end_line = min(len(lines), line_num + self.context_lines)
                        context = lines[start_line:end_line]
                        
                        # Calculate relative line number for highlighting
                        highlight_line = line_num - start_line - 1
                        
                        match_info = {
                            'file': str(file_path.relative_to(self.root_path.parent)),
                            'line': line_num,
                            'column': match.start() + 1,
                            'matched_text': match.group(0),
                            'full_line': line.rstrip(),
                            'context': [l.rstrip() for l in context],
                            'context_start_line': start_line + 1,
                            'highlight_line': highlight_line
                        }
                        
                        self.results[pattern_name].append(match_info)
                        self.stats[pattern_name] += 1
                        self.stats['total'] += 1
                        
        except Exception as e:
            # Skip files that can't be read
            pass
    
    def get_statistics(self) -> Dict[str, int]:
        """Get search statistics."""
        return dict(self.stats)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of search results."""
        return {
            'total_matches': self.stats['total'],
            'patterns_found': len([p for p in self.results if self.results[p]]),
            'files_affected': len(set(m['file'] for matches in self.results.values() for m in matches)),
            'pattern_counts': {p: len(matches) for p, matches in self.results.items() if matches}
        }
    
    def format_results_text(self, colorize: bool = True) -> str:
        """Format results as colored text."""
        if colorize:
            BOLD = '\033[1m'
            CYAN = '\033[96m'
            YELLOW = '\033[93m'
            GREEN = '\033[92m'
            RED = '\033[91m'
            GRAY = '\033[90m'
            RESET = '\033[0m'
        else:
            BOLD = CYAN = YELLOW = GREEN = RED = GRAY = RESET = ''
        
        output = []
        
        # Header
        summary = self.get_summary()
        output.append(f"\n{BOLD}{'=' * 80}{RESET}")
        output.append(f"{BOLD}{CYAN}Python 2 Pattern Search Results{RESET}")
        output.append(f"{BOLD}{'=' * 80}{RESET}\n")
        
        # Summary
        output.append(f"{BOLD}Summary:{RESET}")
        output.append(f"  Total matches: {YELLOW}{summary['total_matches']}{RESET}")
        output.append(f"  Patterns found: {YELLOW}{summary['patterns_found']}{RESET}")
        output.append(f"  Files affected: {YELLOW}{summary['files_affected']}{RESET}\n")
        
        if not self.results or summary['total_matches'] == 0:
            output.append(f"{GREEN}✓ No Python 2 patterns found!{RESET}\n")
            return '\n'.join(output)
        
        # Pattern counts
        output.append(f"{BOLD}Pattern Counts:{RESET}")
        for pattern_name, count in sorted(summary['pattern_counts'].items(), key=lambda x: x[1], reverse=True):
            pattern_desc = self.PATTERNS[pattern_name]['description']
            output.append(f"  {YELLOW}{pattern_name:20}{RESET} {count:4} matches - {GRAY}{pattern_desc}{RESET}")
        output.append("")
        
        # Detailed results
        output.append(f"{BOLD}Detailed Results:{RESET}\n")
        
        for pattern_name in sorted(self.results.keys()):
            matches = self.results[pattern_name]
            if not matches:
                continue
            
            pattern_info = self.PATTERNS[pattern_name]
            output.append(f"{BOLD}{CYAN}[{pattern_name}]{RESET} {GRAY}{pattern_info['description']}{RESET}")
            output.append(f"{GRAY}Example: {pattern_info['example']}{RESET}")
            output.append(f"{YELLOW}Found {len(matches)} occurrence(s):{RESET}\n")
            
            # Group by file
            by_file = defaultdict(list)
            for match in matches:
                by_file[match['file']].append(match)
            
            for file_path, file_matches in sorted(by_file.items()):
                output.append(f"  {BOLD}{file_path}{RESET}")
                
                for match in sorted(file_matches, key=lambda x: x['line']):
                    output.append(f"    {GRAY}Line {match['line']}, Column {match['column']}:{RESET}")
                    
                    # Show context
                    for i, context_line in enumerate(match['context']):
                        line_num = match['context_start_line'] + i
                        if i == match['highlight_line']:
                            output.append(f"      {RED}→{RESET} {GRAY}{line_num:4}{RESET} {context_line}")
                        else:
                            output.append(f"        {GRAY}{line_num:4}  {context_line}{RESET}")
                    output.append("")
                
            output.append("")
        
        return '\n'.join(output)
    
    def export_json(self, output_path: str = None) -> str:
        """Export results as JSON.
        
        Args:
            output_path: Optional file path to save JSON
            
        Returns:
            JSON string
        """
        data = {
            'summary': self.get_summary(),
            'statistics': self.get_statistics(),
            'patterns': {
                name: {
                    'description': self.PATTERNS[name]['description'],
                    'matches': matches
                }
                for name, matches in self.results.items()
                if matches
            }
        }
        
        json_str = json.dumps(data, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    @classmethod
    def list_patterns(cls) -> List[Tuple[str, str, str]]:
        """List all available patterns.
        
        Returns:
            List of (name, description, example) tuples
        """
        return [
            (name, info['description'], info['example'])
            for name, info in sorted(cls.PATTERNS.items())
        ]


def main():
    """Command-line interface for pattern search."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Search for Python 2 patterns in codebase',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('path', nargs='?', default='.', help='Path to search (default: current directory)')
    parser.add_argument('-p', '--patterns', nargs='+', help='Specific patterns to search for')
    parser.add_argument('-l', '--list-patterns', action='store_true', help='List all available patterns')
    parser.add_argument('-c', '--context', type=int, default=2, help='Number of context lines (default: 2)')
    parser.add_argument('-o', '--output', help='Output file for JSON export')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    args = parser.parse_args()
    
    # List patterns if requested
    if args.list_patterns:
        print("\nAvailable Python 2 Patterns:\n")
        for name, description, example in PatternSearcher.list_patterns():
            print(f"  {name:20} - {description}")
            print(f"  {' ' * 20}   Example: {example}\n")
        return 0
    
    # Create searcher and run search
    searcher = PatternSearcher(args.path, context_lines=args.context)
    
    try:
        results = searcher.search(patterns=args.patterns)
        
        if args.json or args.output:
            json_output = searcher.export_json(args.output)
            if not args.output:
                print(json_output)
        else:
            print(searcher.format_results_text(colorize=not args.no_color))
        
        # Exit with non-zero if patterns found (useful for CI/CD)
        return 1 if searcher.stats['total'] > 0 else 0
        
    except Exception as e:
        print(f"Error: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    exit(main())
