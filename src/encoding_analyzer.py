#!/usr/bin/env python3
"""
Encoding Analyzer for Python 2 to 3 Migration

Detects and manages file encodings in Python codebases during migration.
Identifies encoding issues, missing declarations, and can automatically
fix common encoding problems.
"""

import os
import re
import sys
import chardet
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class EncodingAnalyzer:
    """Analyze and fix encoding issues in Python files."""
    
    # Common encoding declarations in Python files
    ENCODING_PATTERN = re.compile(
        rb'coding[=:]\s*([-\w.]+)', re.IGNORECASE
    )
    
    # PEP 263 compliant encoding declaration formats
    ENCODING_FORMATS = [
        '# -*- coding: {encoding} -*-',
        '# coding: {encoding}',
        '#!/usr/bin/env python3\n# -*- coding: {encoding} -*-'
    ]
    
    def __init__(self, target_encoding: str = 'utf-8'):
        """
        Initialize the encoding analyzer.
        
        Args:
            target_encoding: The target encoding for migration (default: utf-8)
        """
        self.target_encoding = target_encoding
        self.results = []
        
    def detect_encoding(self, file_path: str) -> Dict:
        """
        Detect the actual encoding of a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary with encoding detection results
        """
        result = {
            'file': file_path,
            'detected_encoding': None,
            'confidence': 0.0,
            'declared_encoding': None,
            'has_declaration': False,
            'declaration_line': None,
            'issues': [],
            'status': 'ok'
        }
        
        try:
            # Read file in binary mode to detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Detect encoding using chardet
            detection = chardet.detect(raw_data)
            result['detected_encoding'] = detection.get('encoding', 'unknown')
            result['confidence'] = detection.get('confidence', 0.0)
            
            # Check for encoding declaration in first two lines
            lines = raw_data.split(b'\n', 2)
            for i, line in enumerate(lines[:2]):
                match = self.ENCODING_PATTERN.search(line)
                if match:
                    result['has_declaration'] = True
                    result['declared_encoding'] = match.group(1).decode('ascii', errors='ignore')
                    result['declaration_line'] = i + 1
                    break
            
            # Analyze for issues
            self._analyze_issues(result, raw_data)
            
        except Exception as e:
            result['issues'].append(f"Error reading file: {str(e)}")
            result['status'] = 'error'
        
        return result
    
    def _analyze_issues(self, result: Dict, raw_data: bytes):
        """Analyze encoding-related issues in the file."""
        detected = result['detected_encoding']
        declared = result['declared_encoding']
        
        # Check for non-ASCII characters without encoding declaration
        has_non_ascii = any(b > 127 for b in raw_data)
        
        if has_non_ascii and not result['has_declaration']:
            result['issues'].append(
                "File contains non-ASCII characters but has no encoding declaration"
            )
            result['status'] = 'warning'
        
        # Check if declared encoding matches detected encoding
        if declared and detected:
            # Normalize encoding names for comparison
            declared_norm = declared.lower().replace('-', '').replace('_', '')
            detected_norm = detected.lower().replace('-', '').replace('_', '')
            
            if declared_norm != detected_norm and result['confidence'] > 0.7:
                result['issues'].append(
                    f"Declared encoding '{declared}' doesn't match detected encoding '{detected}'"
                )
                result['status'] = 'warning'
        
        # Check if encoding is not UTF-8 (Python 3 standard)
        if detected and detected.lower() not in ['utf-8', 'utf8', 'ascii']:
            result['issues'].append(
                f"File uses '{detected}' encoding instead of UTF-8"
            )
            if result['status'] == 'ok':
                result['status'] = 'info'
        
        # Check for common encoding issues
        try:
            raw_data.decode('utf-8')
        except UnicodeDecodeError:
            result['issues'].append(
                "File cannot be decoded as UTF-8"
            )
            result['status'] = 'warning'
    
    def analyze_directory(self, directory: str, recursive: bool = True) -> List[Dict]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory: Directory path to analyze
            recursive: Whether to analyze subdirectories
            
        Returns:
            List of analysis results for each file
        """
        self.results = []
        
        if recursive:
            pattern = '**/*.py'
        else:
            pattern = '*.py'
        
        path = Path(directory)
        for py_file in path.glob(pattern):
            if py_file.is_file():
                result = self.detect_encoding(str(py_file))
                self.results.append(result)
        
        return self.results
    
    def add_encoding_declaration(
        self,
        file_path: str,
        encoding: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Add or update encoding declaration in a Python file.
        
        Args:
            file_path: Path to the file
            encoding: Encoding to declare (uses detected encoding if None)
            dry_run: If True, don't modify the file
            
        Returns:
            Dictionary with operation results
        """
        result = {
            'file': file_path,
            'action': 'none',
            'encoding_added': None,
            'success': False,
            'message': ''
        }
        
        try:
            # Read file
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Detect current encoding if not specified
            if encoding is None:
                detection = chardet.detect(raw_data)
                encoding = detection.get('encoding', 'utf-8')
            
            # Check if declaration already exists
            lines = raw_data.split(b'\n')
            has_declaration = False
            declaration_line = -1
            
            for i, line in enumerate(lines[:2]):
                if self.ENCODING_PATTERN.search(line):
                    has_declaration = True
                    declaration_line = i
                    break
            
            if has_declaration:
                result['action'] = 'skipped'
                result['message'] = 'File already has encoding declaration'
                result['success'] = True
                return result
            
            # Determine where to insert the declaration
            encoding_line = f'# -*- coding: {encoding} -*-\n'.encode('ascii')
            
            # Check if first line is shebang
            if lines and lines[0].startswith(b'#!'):
                # Insert after shebang
                new_lines = [lines[0], encoding_line] + lines[1:]
                result['action'] = 'added_after_shebang'
            else:
                # Insert at beginning
                new_lines = [encoding_line] + lines
                result['action'] = 'added_at_start'
            
            if not dry_run:
                # Write back to file
                with open(file_path, 'wb') as f:
                    f.write(b'\n'.join(new_lines))
            
            result['encoding_added'] = encoding
            result['success'] = True
            result['message'] = f'Added encoding declaration: {encoding}'
            
        except Exception as e:
            result['success'] = False
            result['message'] = f'Error: {str(e)}'
        
        return result
    
    def convert_to_utf8(
        self,
        file_path: str,
        backup: bool = True,
        dry_run: bool = False
    ) -> Dict:
        """
        Convert a file to UTF-8 encoding.
        
        Args:
            file_path: Path to the file
            backup: Whether to create a backup before conversion
            dry_run: If True, don't modify the file
            
        Returns:
            Dictionary with conversion results
        """
        result = {
            'file': file_path,
            'original_encoding': None,
            'converted': False,
            'backup_created': False,
            'success': False,
            'message': ''
        }
        
        try:
            # Read file and detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            detection = chardet.detect(raw_data)
            original_encoding = detection.get('encoding', 'unknown')
            result['original_encoding'] = original_encoding
            
            # Check if already UTF-8
            if original_encoding.lower() in ['utf-8', 'utf8', 'ascii']:
                result['success'] = True
                result['message'] = f'File is already {original_encoding}'
                return result
            
            # Decode with detected encoding and re-encode as UTF-8
            try:
                text = raw_data.decode(original_encoding)
            except (UnicodeDecodeError, LookupError) as e:
                result['message'] = f'Cannot decode file with {original_encoding}: {e}'
                return result
            
            # Update encoding declaration if present
            lines = text.split('\n')
            for i, line in enumerate(lines[:2]):
                if 'coding' in line and original_encoding in line:
                    lines[i] = line.replace(original_encoding, 'utf-8')
                    break
            
            new_content = '\n'.join(lines)
            
            if not dry_run:
                # Create backup if requested
                if backup:
                    backup_path = f"{file_path}.bak"
                    with open(backup_path, 'wb') as f:
                        f.write(raw_data)
                    result['backup_created'] = True
                
                # Write UTF-8 encoded content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            result['converted'] = True
            result['success'] = True
            result['message'] = f'Converted from {original_encoding} to UTF-8'
            
        except Exception as e:
            result['success'] = False
            result['message'] = f'Error: {str(e)}'
        
        return result
    
    def generate_report(self, output_format: str = 'text') -> str:
        """
        Generate a report of encoding analysis results.
        
        Args:
            output_format: Format of the report ('text', 'json', 'markdown')
            
        Returns:
            Formatted report as string
        """
        if output_format == 'json':
            import json
            return json.dumps(self.results, indent=2)
        
        elif output_format == 'markdown':
            return self._generate_markdown_report()
        
        else:  # text
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate a text format report."""
        lines = []
        lines.append("=" * 70)
        lines.append("ENCODING ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary statistics
        total = len(self.results)
        with_issues = sum(1 for r in self.results if r['status'] in ['warning', 'error'])
        no_declaration = sum(1 for r in self.results if not r['has_declaration'])
        non_utf8 = sum(1 for r in self.results 
                      if r['detected_encoding'] 
                      and r['detected_encoding'].lower() not in ['utf-8', 'utf8', 'ascii'])
        
        lines.append(f"Total files analyzed:           {total}")
        lines.append(f"Files with issues:              {with_issues}")
        lines.append(f"Files without declarations:     {no_declaration}")
        lines.append(f"Files with non-UTF-8 encoding:  {non_utf8}")
        lines.append("")
        lines.append("=" * 70)
        lines.append("")
        
        # Detailed results
        for result in self.results:
            status_symbol = {
                'ok': '✓',
                'info': 'ℹ',
                'warning': '⚠',
                'error': '✗'
            }.get(result['status'], '?')
            
            lines.append(f"{status_symbol} {result['file']}")
            lines.append(f"  Detected: {result['detected_encoding']} "
                        f"(confidence: {result['confidence']:.2f})")
            
            if result['has_declaration']:
                lines.append(f"  Declared: {result['declared_encoding']} "
                           f"(line {result['declaration_line']})")
            else:
                lines.append("  Declared: None")
            
            if result['issues']:
                lines.append("  Issues:")
                for issue in result['issues']:
                    lines.append(f"    - {issue}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_markdown_report(self) -> str:
        """Generate a Markdown format report."""
        lines = []
        lines.append("# Encoding Analysis Report")
        lines.append("")
        
        # Summary
        total = len(self.results)
        with_issues = sum(1 for r in self.results if r['status'] in ['warning', 'error'])
        no_declaration = sum(1 for r in self.results if not r['has_declaration'])
        non_utf8 = sum(1 for r in self.results 
                      if r['detected_encoding'] 
                      and r['detected_encoding'].lower() not in ['utf-8', 'utf8', 'ascii'])
        
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total files analyzed:** {total}")
        lines.append(f"- **Files with issues:** {with_issues}")
        lines.append(f"- **Files without declarations:** {no_declaration}")
        lines.append(f"- **Files with non-UTF-8 encoding:** {non_utf8}")
        lines.append("")
        
        # Detailed results
        lines.append("## Detailed Results")
        lines.append("")
        
        for result in self.results:
            status_emoji = {
                'ok': '✅',
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌'
            }.get(result['status'], '❓')
            
            lines.append(f"### {status_emoji} `{result['file']}`")
            lines.append("")
            lines.append(f"- **Detected encoding:** {result['detected_encoding']} "
                        f"({result['confidence']:.0%} confidence)")
            
            if result['has_declaration']:
                lines.append(f"- **Declared encoding:** {result['declared_encoding']} "
                           f"(line {result['declaration_line']})")
            else:
                lines.append("- **Declared encoding:** None")
            
            if result['issues']:
                lines.append("- **Issues:**")
                for issue in result['issues']:
                    lines.append(f"  - {issue}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_statistics(self) -> Dict:
        """Get summary statistics from analysis results."""
        stats = {
            'total_files': len(self.results),
            'files_with_issues': 0,
            'files_without_declaration': 0,
            'files_non_utf8': 0,
            'encoding_distribution': {},
            'status_distribution': {
                'ok': 0,
                'info': 0,
                'warning': 0,
                'error': 0
            }
        }
        
        for result in self.results:
            # Count by status
            stats['status_distribution'][result['status']] += 1
            
            if result['status'] in ['warning', 'error']:
                stats['files_with_issues'] += 1
            
            if not result['has_declaration']:
                stats['files_without_declaration'] += 1
            
            detected = result['detected_encoding']
            if detected:
                if detected.lower() not in ['utf-8', 'utf8', 'ascii']:
                    stats['files_non_utf8'] += 1
                
                # Count encoding distribution
                stats['encoding_distribution'][detected] = \
                    stats['encoding_distribution'].get(detected, 0) + 1
        
        return stats


def main():
    """CLI interface for encoding analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze and fix encoding issues in Python files'
    )
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Recursively analyze subdirectories')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'markdown'],
                       default='text', help='Report format')
    parser.add_argument('--add-declarations', action='store_true',
                       help='Add encoding declarations to files without them')
    parser.add_argument('--convert-to-utf8', action='store_true',
                       help='Convert files to UTF-8 encoding')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backups when converting files')
    
    args = parser.parse_args()
    
    analyzer = EncodingAnalyzer()
    
    # Analyze files
    if os.path.isdir(args.path):
        analyzer.analyze_directory(args.path, recursive=args.recursive)
    else:
        result = analyzer.detect_encoding(args.path)
        analyzer.results = [result]
    
    # Apply fixes if requested
    if args.add_declarations:
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Adding encoding declarations...")
        for result in analyzer.results:
            if not result['has_declaration'] and result['status'] != 'error':
                fix_result = analyzer.add_encoding_declaration(
                    result['file'],
                    dry_run=args.dry_run
                )
                if fix_result['success']:
                    print(f"  ✓ {fix_result['file']}: {fix_result['message']}")
    
    if args.convert_to_utf8:
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Converting files to UTF-8...")
        for result in analyzer.results:
            if result['detected_encoding'] and \
               result['detected_encoding'].lower() not in ['utf-8', 'utf8', 'ascii']:
                convert_result = analyzer.convert_to_utf8(
                    result['file'],
                    backup=not args.no_backup,
                    dry_run=args.dry_run
                )
                if convert_result['success']:
                    print(f"  ✓ {convert_result['file']}: {convert_result['message']}")
    
    # Generate report
    report = analyzer.generate_report(output_format=args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")
    else:
        print(report)
    
    # Exit with error code if issues found
    stats = analyzer.get_statistics()
    return 1 if stats['files_with_issues'] > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
