#!/usr/bin/env python3
"""
Documentation Modernizer for Python 2 to 3 Migration

Automatically updates docstrings, comments, and inline documentation to reflect
Python 3 syntax and conventions. Helps ensure documentation stays in sync with
code changes during migration.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class DocumentationModernizer:
    """Modernize documentation in Python files for Python 3."""
    
    # Patterns to detect and update in documentation
    PYTHON2_PATTERNS = [
        # Print statements
        (r'print\s+"([^"]*)"', r'print("\1")'),
        (r"print\s+'([^']*)'", r"print('\1')"),
        
        # String types
        (r'\bbasestring\b', r'str'),
        (r'\bunicode\b', r'str'),
        (r'\.decode\(\s*["\']utf-?8["\']\s*\)', r'  # Not needed in Python 3'),
        
        # Dictionary methods
        (r'\.iteritems\(\)', r'.items()'),
        (r'\.iterkeys\(\)', r'.keys()'),
        (r'\.itervalues\(\)', r'.values()'),
        (r'\.has_key\(', r' in '),
        
        # Range
        (r'\bxrange\b', r'range'),
        
        # Imports
        (r'\bConfigParser\b', r'configparser'),
        (r'\burllib2\b', r'urllib.request'),
        (r'\bHTTPServer\b', r'http.server'),
        (r'\bQueue\b', r'queue'),
        (r'\bSocketServer\b', r'socketserver'),
        
        # Exception syntax
        (r'except\s+(\w+)\s*,\s*(\w+):', r'except \1 as \2:'),
        
        # Raw input
        (r'\braw_input\b', r'input'),
        
        # File operations
        (r"file\(", r"open("),
        
        # Long type
        (r'\blong\b', r'int'),
        
        # Division
        (r'from __future__ import division', '# Python 3 uses true division by default'),
        (r'from __future__ import print_function', '# Python 3 uses print() by default'),
        (r'from __future__ import unicode_literals', '# Python 3 uses Unicode strings by default'),
    ]
    
    # Common Python 2 phrases to flag
    PYTHON2_REFERENCES = [
        r'python\s*2\.\d+',
        r'python\s*2(?!\d)',
        r'py2',
        r'python2',
        r'backward[s]?\s+compat(?:ible|ibility)?.*python\s*2',
        r'compatible\s+with\s+python\s*2',
        r'works?\s+(?:in|with|on)\s+python\s*2',
        r'requires?\s+python\s*2',
    ]
    
    def __init__(self, project_path: str = ".", backup: bool = True):
        self.project_path = Path(project_path)
        self.backup = backup
        self.changes = []
        self.files_modified = 0
        self.total_updates = 0
        
    def modernize_file(self, filepath: str) -> Dict:
        """Modernize documentation in a single Python file."""
        filepath = Path(filepath)
        
        if not filepath.suffix == '.py':
            return {'error': 'Not a Python file'}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            return {'error': f'Failed to read file: {e}'}
        
        # Create backup if requested
        if self.backup:
            backup_path = filepath.with_suffix('.py.docbackup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        
        # Process the file
        updated_content, changes = self._process_content(original_content, str(filepath))
        
        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.files_modified += 1
            self.total_updates += len(changes)
            
            change_record = {
                'file': str(filepath),
                'changes': changes,
                'backup': str(backup_path) if self.backup else None
            }
            self.changes.append(change_record)
            
            return change_record
        
        return {'file': str(filepath), 'changes': [], 'message': 'No changes needed'}
    
    def modernize_directory(self, directory: str = None) -> Dict:
        """Modernize documentation in all Python files in a directory."""
        if directory is None:
            directory = self.project_path
        else:
            directory = Path(directory)
        
        self.changes = []
        self.files_modified = 0
        self.total_updates = 0
        
        python_files = list(directory.rglob('*.py'))
        
        for filepath in python_files:
            # Skip test files and virtual environments
            if any(part in str(filepath) for part in ['venv', '__pycache__', '.git', 'site-packages']):
                continue
            
            self.modernize_file(filepath)
        
        return {
            'files_scanned': len(python_files),
            'files_modified': self.files_modified,
            'total_updates': self.total_updates,
            'changes': self.changes
        }
    
    def _process_content(self, content: str, filepath: str) -> Tuple[str, List[Dict]]:
        """Process file content and update documentation."""
        changes = []
        lines = content.split('\n')
        updated_lines = []
        
        in_docstring = False
        docstring_quote = None
        
        for line_num, line in enumerate(lines, 1):
            updated_line = line
            line_changes = []
            
            # Detect docstring boundaries
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_quote = '"""' if '"""' in line else "'''"
                elif docstring_quote in line:
                    in_docstring = False
                    docstring_quote = None
            
            # Process documentation lines (docstrings and comments)
            if in_docstring or line.strip().startswith('#'):
                # Apply all Python 2 patterns
                for pattern, replacement in self.PYTHON2_PATTERNS:
                    if re.search(pattern, updated_line, re.IGNORECASE):
                        new_line = re.sub(pattern, replacement, updated_line, flags=re.IGNORECASE)
                        if new_line != updated_line:
                            line_changes.append({
                                'pattern': pattern,
                                'old': updated_line.strip(),
                                'new': new_line.strip()
                            })
                            updated_line = new_line
                
                # Flag Python 2 references
                for ref_pattern in self.PYTHON2_REFERENCES:
                    if re.search(ref_pattern, updated_line, re.IGNORECASE):
                        line_changes.append({
                            'type': 'python2_reference',
                            'line': updated_line.strip(),
                            'message': 'Contains Python 2 reference - consider updating'
                        })
            
            if line_changes:
                changes.append({
                    'line_number': line_num,
                    'changes': line_changes
                })
            
            updated_lines.append(updated_line)
        
        return '\n'.join(updated_lines), changes
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate a report of all documentation changes."""
        report_lines = [
            "=" * 80,
            "Documentation Modernization Report",
            "=" * 80,
            "",
            f"Files scanned: {len(self.changes)}",
            f"Files modified: {self.files_modified}",
            f"Total updates: {self.total_updates}",
            "",
            "=" * 80,
            "Detailed Changes",
            "=" * 80,
            ""
        ]
        
        for change_record in self.changes:
            if not change_record.get('changes'):
                continue
            
            report_lines.append(f"\nFile: {change_record['file']}")
            report_lines.append("-" * 80)
            
            for change in change_record['changes']:
                line_num = change['line_number']
                report_lines.append(f"\n  Line {line_num}:")
                
                for detail in change['changes']:
                    if 'old' in detail and 'new' in detail:
                        report_lines.append(f"    - Old: {detail['old']}")
                        report_lines.append(f"    + New: {detail['new']}")
                    elif 'message' in detail:
                        report_lines.append(f"    ⚠ {detail['message']}")
                        report_lines.append(f"      {detail['line']}")
        
        report = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    def restore_backups(self, directory: str = None) -> int:
        """Restore all backup files and remove backups."""
        if directory is None:
            directory = self.project_path
        else:
            directory = Path(directory)
        
        restored = 0
        for backup_file in directory.rglob('*.py.docbackup'):
            original_file = backup_file.with_suffix('')
            
            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with open(original_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                backup_file.unlink()
                restored += 1
        
        return restored


def main():
    """Command-line interface for documentation modernizer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Modernize documentation in Python files for Python 3'
    )
    parser.add_argument(
        'path',
        help='Path to file or directory to modernize'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    parser.add_argument(
        '--report',
        '-r',
        help='Output report file path'
    )
    parser.add_argument(
        '--restore',
        action='store_true',
        help='Restore all backup files'
    )
    
    args = parser.parse_args()
    
    modernizer = DocumentationModernizer(backup=not args.no_backup)
    
    if args.restore:
        restored = modernizer.restore_backups(args.path)
        print(f"✓ Restored {restored} files from backups")
        return
    
    if os.path.isfile(args.path):
        result = modernizer.modernize_file(args.path)
        print(f"✓ Processed {args.path}")
        print(f"  Changes: {len(result.get('changes', []))}")
    else:
        result = modernizer.modernize_directory(args.path)
        print(f"✓ Processed {result['files_scanned']} files")
        print(f"  Modified: {result['files_modified']} files")
        print(f"  Total updates: {result['total_updates']}")
    
    # Generate report
    report = modernizer.generate_report(args.report)
    
    if not args.report:
        print("\n" + report)


if __name__ == '__main__':
    main()
