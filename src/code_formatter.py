#!/usr/bin/env python3
"""
Code Formatter for Python 2 to 3 Migration
Automatically format migrated code using modern Python formatters (black, isort).
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class CodeFormatter:
    """Format Python code using modern formatters like black and isort."""
    
    def __init__(self, line_length: int = 88, check_only: bool = False):
        """
        Initialize the code formatter.
        
        Args:
            line_length: Maximum line length for formatting (default: 88, black's default)
            check_only: If True, only check formatting without making changes
        """
        self.line_length = line_length
        self.check_only = check_only
        self.stats = {
            'files_processed': 0,
            'files_formatted': 0,
            'files_unchanged': 0,
            'files_failed': 0,
            'imports_sorted': 0
        }
        
    def check_formatter_available(self, formatter: str) -> bool:
        """Check if a formatter is installed."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', formatter, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def install_formatter(self, formatter: str) -> bool:
        """Attempt to install a formatter using pip."""
        print(f"📦 Installing {formatter}...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', formatter],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def format_with_black(self, file_path: str) -> Tuple[bool, str]:
        """
        Format a file using black.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.check_formatter_available('black'):
            if not self.install_formatter('black'):
                return False, "black is not installed and auto-install failed"
        
        cmd = [
            sys.executable, '-m', 'black',
            '--line-length', str(self.line_length),
            '--quiet'
        ]
        
        if self.check_only:
            cmd.append('--check')
        
        cmd.append(file_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if self.check_only:
                    return True, "already formatted"
                return True, "formatted successfully"
            elif result.returncode == 1 and self.check_only:
                return True, "would be reformatted"
            else:
                return False, result.stderr or "formatting failed"
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as e:
            return False, str(e)
    
    def sort_imports_with_isort(self, file_path: str) -> Tuple[bool, str]:
        """
        Sort imports using isort.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.check_formatter_available('isort'):
            if not self.install_formatter('isort'):
                return False, "isort is not installed and auto-install failed"
        
        cmd = [
            sys.executable, '-m', 'isort',
            '--profile', 'black',  # Compatible with black
            '--line-length', str(self.line_length)
        ]
        
        if self.check_only:
            cmd.append('--check-only')
        
        cmd.append(file_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if self.check_only:
                    return True, "imports already sorted"
                return True, "imports sorted"
            elif self.check_only and "would be reformatted" in result.stdout.lower():
                return True, "imports would be sorted"
            else:
                # isort returns non-zero when it makes changes (in non-check mode)
                if not self.check_only and "Fixing" in result.stdout:
                    return True, "imports sorted"
                return False, result.stderr or "sorting failed"
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as e:
            return False, str(e)
    
    def format_file(self, file_path: str, use_isort: bool = True) -> Dict[str, any]:
        """
        Format a single Python file.
        
        Args:
            file_path: Path to the Python file
            use_isort: Whether to sort imports with isort
            
        Returns:
            Dictionary with formatting results
        """
        if not os.path.exists(file_path):
            return {
                'success': False,
                'file': file_path,
                'error': 'File not found'
            }
        
        if not file_path.endswith('.py'):
            return {
                'success': False,
                'file': file_path,
                'error': 'Not a Python file'
            }
        
        self.stats['files_processed'] += 1
        
        result = {
            'success': True,
            'file': file_path,
            'black_status': None,
            'isort_status': None,
            'changed': False
        }
        
        # Format with black
        black_success, black_msg = self.format_with_black(file_path)
        result['black_status'] = black_msg
        
        if not black_success:
            result['success'] = False
            self.stats['files_failed'] += 1
            return result
        
        if 'reformatted' in black_msg or 'formatted successfully' in black_msg:
            result['changed'] = True
        
        # Sort imports with isort
        if use_isort:
            isort_success, isort_msg = self.sort_imports_with_isort(file_path)
            result['isort_status'] = isort_msg
            
            if not isort_success and 'not installed' in isort_msg:
                # Non-critical error, continue
                pass
            elif isort_success and ('sorted' in isort_msg or 'would be sorted' in isort_msg):
                result['changed'] = True
                if 'sorted' in isort_msg and not self.check_only:
                    self.stats['imports_sorted'] += 1
        
        if result['changed']:
            self.stats['files_formatted'] += 1
        else:
            self.stats['files_unchanged'] += 1
        
        return result
    
    def format_directory(self, directory: str, recursive: bool = True, 
                        use_isort: bool = True, exclude_patterns: Optional[List[str]] = None) -> List[Dict]:
        """
        Format all Python files in a directory.
        
        Args:
            directory: Path to the directory
            recursive: Whether to process subdirectories
            use_isort: Whether to sort imports with isort
            exclude_patterns: List of patterns to exclude (e.g., ['test_*', '*_backup.py'])
            
        Returns:
            List of results for each file
        """
        if not os.path.exists(directory):
            return [{
                'success': False,
                'file': directory,
                'error': 'Directory not found'
            }]
        
        if not os.path.isdir(directory):
            return [{
                'success': False,
                'file': directory,
                'error': 'Not a directory'
            }]
        
        results = []
        exclude_patterns = exclude_patterns or []
        
        # Find all Python files
        if recursive:
            python_files = list(Path(directory).rglob('*.py'))
        else:
            python_files = list(Path(directory).glob('*.py'))
        
        # Filter out excluded files
        filtered_files = []
        for file_path in python_files:
            file_str = str(file_path)
            
            # Check exclude patterns
            excluded = False
            for pattern in exclude_patterns:
                if pattern in file_str:
                    excluded = True
                    break
            
            # Skip common directories that should be excluded
            skip_dirs = ['venv', 'env', '.env', '__pycache__', '.git', 'node_modules', 'build', 'dist', '.tox']
            if any(skip_dir in file_str.split(os.sep) for skip_dir in skip_dirs):
                excluded = True
            
            if not excluded:
                filtered_files.append(file_path)
        
        print(f"Found {len(filtered_files)} Python file(s) to format")
        
        # Format each file
        for file_path in filtered_files:
            result = self.format_file(str(file_path), use_isort=use_isort)
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict[str, int]:
        """Get formatting statistics."""
        return self.stats.copy()
    
    def print_summary(self):
        """Print a summary of formatting operations."""
        print("\n" + "=" * 70)
        print("FORMATTING SUMMARY")
        print("=" * 70)
        print(f"Files processed:   {self.stats['files_processed']}")
        print(f"Files formatted:   {self.stats['files_formatted']}")
        print(f"Files unchanged:   {self.stats['files_unchanged']}")
        print(f"Imports sorted:    {self.stats['imports_sorted']}")
        if self.stats['files_failed'] > 0:
            print(f"Files failed:      {self.stats['files_failed']}")
        print("=" * 70)


def main():
    """Command-line interface for the formatter."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Format Python code with black and isort'
    )
    parser.add_argument(
        'path',
        help='Path to file or directory to format'
    )
    parser.add_argument(
        '-l', '--line-length',
        type=int,
        default=88,
        help='Maximum line length (default: 88)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check formatting without making changes'
    )
    parser.add_argument(
        '--no-isort',
        action='store_true',
        help='Skip import sorting with isort'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not process subdirectories'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='Patterns to exclude'
    )
    
    args = parser.parse_args()
    
    formatter = CodeFormatter(
        line_length=args.line_length,
        check_only=args.check
    )
    
    path = args.path
    
    if os.path.isfile(path):
        print(f"Formatting file: {path}")
        result = formatter.format_file(path, use_isort=not args.no_isort)
        
        if result['success']:
            print(f"✓ {result['file']}")
            if result['black_status']:
                print(f"  Black: {result['black_status']}")
            if result['isort_status']:
                print(f"  isort: {result['isort_status']}")
        else:
            print(f"✗ {result['file']}: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    elif os.path.isdir(path):
        print(f"Formatting directory: {path}")
        results = formatter.format_directory(
            path,
            recursive=not args.no_recursive,
            use_isort=not args.no_isort,
            exclude_patterns=args.exclude
        )
        
        # Print results
        for result in results:
            if result['success']:
                status = "would change" if args.check and result['changed'] else "changed" if result['changed'] else "unchanged"
                print(f"✓ {result['file']} - {status}")
            else:
                print(f"✗ {result['file']}: {result.get('error', 'Unknown error')}")
    
    else:
        print(f"Error: Path not found: {path}")
        sys.exit(1)
    
    formatter.print_summary()


if __name__ == '__main__':
    main()
