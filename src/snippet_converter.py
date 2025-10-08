#!/usr/bin/env python3
"""
Code Snippet Converter - Interactive Python 2 to 3 code converter

This module provides a lightweight, fast tool for converting Python 2 code snippets
to Python 3. Perfect for learning, quick reference, or testing specific patterns.
"""

import re
import sys
import difflib
from typing import Dict, List, Tuple, Optional


class SnippetConverter:
    """Converts Python 2 code snippets to Python 3 with explanations."""
    
    def __init__(self):
        self.changes_made = []
        self.explanations = {
            'print_statement': 'Print is now a function in Python 3, requiring parentheses',
            'except_syntax': 'Exception handling now uses "as" instead of comma',
            'raise_syntax': 'Raise statement requires parentheses in Python 3',
            'unicode_string': 'String literals are Unicode by default in Python 3',
            'basestring': 'basestring replaced with str in Python 3',
            'long_type': 'long type unified with int in Python 3',
            'xrange': 'xrange() renamed to range() in Python 3',
            'iteritems': 'dict.iteritems() replaced with dict.items() in Python 3',
            'iterkeys': 'dict.iterkeys() replaced with dict.keys() in Python 3',
            'itervalues': 'dict.itervalues() replaced with dict.values() in Python 3',
            'has_key': 'dict.has_key() replaced with "in" operator in Python 3',
            'urllib2': 'urllib2 module split into urllib.request, urllib.error, etc.',
            'urllib': 'urllib.urlopen moved to urllib.request.urlopen',
            'ConfigParser': 'ConfigParser module renamed to configparser (lowercase)',
            'raw_input': 'raw_input() renamed to input() in Python 3',
            'input_eval': 'input() now behaves like raw_input() (no automatic eval)',
            'exec_statement': 'exec is now a function in Python 3',
            'execfile': 'execfile() removed, use exec(open(file).read())',
            'dict_keys': 'dict.keys() now returns a view object, not a list',
            'division': 'Division (/) now returns float, use // for integer division',
            'cmp_function': 'cmp() function removed, use key functions instead',
            'reduce_import': 'reduce() moved from builtins to functools module',
            'octal_literal': 'Octal literals now use 0o prefix instead of just 0',
            'metaclass': '__metaclass__ replaced with metaclass= in class definition',
            'next_method': '.next() method renamed to __next__()',
            'string_module': 'Many string module functions replaced with str methods',
        }
    
    def convert(self, code: str) -> Tuple[str, List[Dict]]:
        """
        Convert Python 2 code to Python 3.
        
        Returns:
            Tuple of (converted_code, list_of_changes)
        """
        self.changes_made = []
        original_code = code
        
        # Apply all conversion rules
        code = self._fix_print_statements(code)
        code = self._fix_except_syntax(code)
        code = self._fix_raise_syntax(code)
        code = self._fix_unicode_strings(code)
        code = self._fix_basestring(code)
        code = self._fix_long_type(code)
        code = self._fix_xrange(code)
        code = self._fix_dict_methods(code)
        code = self._fix_has_key(code)
        code = self._fix_imports(code)
        code = self._fix_raw_input(code)
        code = self._fix_exec(code)
        code = self._fix_execfile(code)
        code = self._fix_reduce(code)
        code = self._fix_octal_literals(code)
        code = self._fix_next_method(code)
        
        return code, self.changes_made
    
    def _add_change(self, change_type: str, line_num: int, old: str, new: str):
        """Record a change that was made."""
        self.changes_made.append({
            'type': change_type,
            'line': line_num,
            'old': old,
            'new': new,
            'explanation': self.explanations.get(change_type, 'Code updated for Python 3 compatibility')
        })
    
    def _fix_print_statements(self, code: str) -> str:
        """Convert print statements to print functions."""
        lines = code.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Skip if already a function call or in a string
            if re.search(r'print\s*\(', line) or re.search(r'["\'].*print\s+.*["\']', line):
                new_lines.append(line)
                continue
            
            # Match print statements
            match = re.search(r'^(\s*)print\s+(.+?)(\s*#.*)?$', line)
            if match:
                indent, content, comment = match.groups()
                comment = comment or ''
                
                # Handle special cases
                if '>>' in content:
                    # print >> file, content -> print(content, file=file)
                    file_match = re.match(r'>>\s*(\S+)\s*,\s*(.+)', content)
                    if file_match:
                        file_obj, print_content = file_match.groups()
                        new_line = f'{indent}print({print_content}, file={file_obj}){comment}'
                        self._add_change('print_statement', i + 1, line, new_line)
                        new_lines.append(new_line)
                        continue
                
                # Regular print statement
                new_line = f'{indent}print({content}){comment}'
                self._add_change('print_statement', i + 1, line, new_line)
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _fix_except_syntax(self, code: str) -> str:
        """Fix except clause syntax."""
        lines = code.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Match: except Exception, e:
            match = re.search(r'^(\s*)except\s+(\w+(\.\w+)*)\s*,\s*(\w+)\s*:', line)
            if match:
                indent, exception, _, var = match.groups()
                new_line = f'{indent}except {exception} as {var}:'
                self._add_change('except_syntax', i + 1, line, new_line)
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _fix_raise_syntax(self, code: str) -> str:
        """Fix raise statement syntax."""
        lines = code.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Match: raise Exception, args
            match = re.search(r'^(\s*)raise\s+(\w+(\.\w+)*)\s*,\s*(.+?)(\s*#.*)?$', line)
            if match:
                indent, exception, _, args, comment = match.groups()
                comment = comment or ''
                new_line = f'{indent}raise {exception}({args}){comment}'
                self._add_change('raise_syntax', i + 1, line, new_line)
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _fix_unicode_strings(self, code: str) -> str:
        """Handle Unicode string literals."""
        # Remove u'' prefix (all strings are unicode in Python 3)
        pattern = r'\bu(["\'])'
        if re.search(pattern, code):
            new_code = re.sub(pattern, r'\1', code)
            self._add_change('unicode_string', 0, 'u"..." or u\'...\'', '"..." or \'...\'')
            return new_code
        return code
    
    def _fix_basestring(self, code: str) -> str:
        """Replace basestring with str."""
        if 'basestring' in code:
            new_code = re.sub(r'\bbasestring\b', 'str', code)
            self._add_change('basestring', 0, 'basestring', 'str')
            return new_code
        return code
    
    def _fix_long_type(self, code: str) -> str:
        """Replace long type with int."""
        if re.search(r'\blong\b', code):
            new_code = re.sub(r'\blong\b', 'int', code)
            self._add_change('long_type', 0, 'long', 'int')
            return new_code
        return code
    
    def _fix_xrange(self, code: str) -> str:
        """Replace xrange with range."""
        if 'xrange' in code:
            new_code = re.sub(r'\bxrange\b', 'range', code)
            self._add_change('xrange', 0, 'xrange()', 'range()')
            return new_code
        return code
    
    def _fix_dict_methods(self, code: str) -> str:
        """Fix dictionary iteration methods."""
        changes = [
            (r'\.iteritems\(\)', '.items()', 'iteritems'),
            (r'\.iterkeys\(\)', '.keys()', 'iterkeys'),
            (r'\.itervalues\(\)', '.values()', 'itervalues'),
        ]
        
        for pattern, replacement, change_type in changes:
            if re.search(pattern, code):
                new_code = re.sub(pattern, replacement, code)
                self._add_change(change_type, 0, pattern[1:], replacement)
                code = new_code
        
        return code
    
    def _fix_has_key(self, code: str) -> str:
        """Replace dict.has_key() with in operator."""
        pattern = r'(\w+)\.has_key\(([^)]+)\)'
        if re.search(pattern, code):
            new_code = re.sub(pattern, r'\2 in \1', code)
            self._add_change('has_key', 0, 'dict.has_key(key)', 'key in dict')
            return new_code
        return code
    
    def _fix_imports(self, code: str) -> str:
        """Fix common import changes."""
        lines = code.split('\n')
        new_lines = []
        
        import_fixes = [
            (r'import urllib2', 'import urllib.request', 'urllib2'),
            (r'from urllib2 import', 'from urllib.request import', 'urllib2'),
            (r'import ConfigParser', 'import configparser', 'ConfigParser'),
            (r'from ConfigParser import', 'from configparser import', 'ConfigParser'),
            (r'import Queue', 'import queue', 'Queue'),
            (r'from Queue import', 'from queue import', 'Queue'),
            (r'import SocketServer', 'import socketserver', 'SocketServer'),
            (r'import htmlentitydefs', 'import html.entities', 'htmlentitydefs'),
            (r'import HTMLParser', 'import html.parser', 'HTMLParser'),
            (r'import Cookie', 'import http.cookies', 'Cookie'),
            (r'import cookielib', 'import http.cookiejar', 'cookielib'),
        ]
        
        for i, line in enumerate(lines):
            modified = False
            for pattern, replacement, module in import_fixes:
                if re.search(pattern, line):
                    new_line = re.sub(pattern, replacement, line)
                    self._add_change(module, i + 1, line.strip(), new_line.strip())
                    new_lines.append(new_line)
                    modified = True
                    break
            
            if not modified:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _fix_raw_input(self, code: str) -> str:
        """Replace raw_input() with input()."""
        if 'raw_input' in code:
            new_code = re.sub(r'\braw_input\b', 'input', code)
            self._add_change('raw_input', 0, 'raw_input()', 'input()')
            return new_code
        return code
    
    def _fix_exec(self, code: str) -> str:
        """Convert exec statement to exec function."""
        pattern = r'^(\s*)exec\s+([^(].*?)(\s*#.*)?$'
        lines = code.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match and 'exec(' not in line:
                indent, content, comment = match.groups()
                comment = comment or ''
                new_line = f'{indent}exec({content}){comment}'
                self._add_change('exec_statement', i + 1, line, new_line)
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _fix_execfile(self, code: str) -> str:
        """Replace execfile() with exec(open().read())."""
        pattern = r'\bexecfile\(([^)]+)\)'
        if re.search(pattern, code):
            new_code = re.sub(pattern, r'exec(open(\1).read())', code)
            self._add_change('execfile', 0, 'execfile(file)', 'exec(open(file).read())')
            return new_code
        return code
    
    def _fix_reduce(self, code: str) -> str:
        """Add functools import if reduce is used."""
        lines = code.split('\n')
        
        # Check if reduce is used but functools not imported
        has_reduce = any('reduce(' in line for line in lines)
        has_functools_import = any('from functools import' in line or 'import functools' in line for line in lines)
        
        if has_reduce and not has_functools_import:
            # Find first import or add at top
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_pos = i + 1
            
            lines.insert(insert_pos, 'from functools import reduce')
            self._add_change('reduce_import', insert_pos + 1, '', 'from functools import reduce')
        
        return '\n'.join(lines)
    
    def _fix_octal_literals(self, code: str) -> str:
        """Fix octal literal syntax."""
        pattern = r'\b0([0-7]+)\b'
        if re.search(pattern, code):
            new_code = re.sub(pattern, r'0o\1', code)
            self._add_change('octal_literal', 0, '0777', '0o777')
            return new_code
        return code
    
    def _fix_next_method(self, code: str) -> str:
        """Fix .next() method calls."""
        pattern = r'\.next\(\)'
        if re.search(pattern, code):
            new_code = re.sub(pattern, '.__next__()', code)
            self._add_change('next_method', 0, '.next()', '.__next__()')
            return new_code
        return code


def format_diff(original: str, converted: str, context_lines: int = 3) -> str:
    """Generate a colored unified diff."""
    original_lines = original.splitlines(keepends=True)
    converted_lines = converted.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        converted_lines,
        fromfile='Python 2',
        tofile='Python 3',
        lineterm='',
        n=context_lines
    )
    
    return ''.join(diff)


def format_side_by_side(original: str, converted: str, width: int = 80) -> str:
    """Generate a side-by-side comparison."""
    original_lines = original.split('\n')
    converted_lines = converted.split('\n')
    
    max_lines = max(len(original_lines), len(converted_lines))
    col_width = width // 2 - 2
    
    output = []
    output.append('=' * width)
    output.append(f"{'Python 2':<{col_width}} | {'Python 3':<{col_width}}")
    output.append('=' * width)
    
    for i in range(max_lines):
        left = original_lines[i] if i < len(original_lines) else ''
        right = converted_lines[i] if i < len(converted_lines) else ''
        
        # Truncate if too long
        if len(left) > col_width - 1:
            left = left[:col_width - 4] + '...'
        if len(right) > col_width - 1:
            right = right[:col_width - 4] + '...'
        
        marker = '│' if left == right else '│'
        output.append(f"{left:<{col_width}} {marker} {right}")
    
    output.append('=' * width)
    return '\n'.join(output)


def main():
    """Main entry point for snippet converter."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert Python 2 code snippets to Python 3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert code from a file
  python snippet_converter.py snippet.py
  
  # Convert inline code
  python snippet_converter.py -c "print 'Hello, World!'"
  
  # Read from stdin
  echo "print 'test'" | python snippet_converter.py -
  
  # Show side-by-side comparison
  python snippet_converter.py snippet.py --side-by-side
  
  # Save converted code to file
  python snippet_converter.py snippet.py -o converted.py
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input file (use - for stdin)')
    parser.add_argument('-c', '--code', help='Code string to convert')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--side-by-side', action='store_true', help='Show side-by-side comparison')
    parser.add_argument('--diff', action='store_true', help='Show unified diff')
    parser.add_argument('--no-explanation', action='store_true', help='Skip change explanations')
    parser.add_argument('--quiet', action='store_true', help='Only output converted code')
    
    args = parser.parse_args()
    
    # Get input code
    if args.code:
        code = args.code
    elif args.input == '-' or not args.input:
        code = sys.stdin.read()
    else:
        with open(args.input, 'r') as f:
            code = f.read()
    
    # Convert
    converter = SnippetConverter()
    converted, changes = converter.convert(code)
    
    # Output
    if args.quiet:
        output = converted
    else:
        output_parts = []
        
        if args.side_by_side:
            output_parts.append(format_side_by_side(code, converted))
        elif args.diff:
            output_parts.append(format_diff(code, converted))
        else:
            output_parts.append("=== Python 2 (Original) ===")
            output_parts.append(code)
            output_parts.append("\n=== Python 3 (Converted) ===")
            output_parts.append(converted)
        
        if changes and not args.no_explanation:
            output_parts.append("\n=== Changes Made ===")
            for i, change in enumerate(changes, 1):
                output_parts.append(f"\n{i}. {change['type']}")
                if change['line'] > 0:
                    output_parts.append(f"   Line {change['line']}")
                output_parts.append(f"   - Before: {change['old']}")
                output_parts.append(f"   + After:  {change['new']}")
                output_parts.append(f"   ℹ {change['explanation']}")
        
        if not changes:
            output_parts.append("\n✓ No changes needed - code is already Python 3 compatible!")
        
        output = '\n'.join(output_parts)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(converted if args.quiet else output)
        if not args.quiet:
            print(f"✓ Converted code saved to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
