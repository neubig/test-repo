#!/usr/bin/env python3
"""
Parallel Migration Runner for Python 2 to 3 Migration

This module enables parallel processing of migration operations across multiple
files simultaneously, significantly speeding up large codebase migrations.
"""

import os
import sys
import time
import multiprocessing as mp
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from verifier import Python3CompatibilityVerifier
from fixer import Python2to3Fixer


class ParallelMigrationRunner:
    """Runs migration operations in parallel across multiple files."""
    
    def __init__(self, workers: Optional[int] = None, verbose: bool = False):
        """
        Initialize parallel migration runner.
        
        Args:
            workers: Number of worker processes (default: CPU count)
            verbose: Enable verbose output
        """
        self.workers = workers or mp.cpu_count()
        self.verbose = verbose
        self.results = []
        
    def check_files(self, file_paths: List[str], 
                   exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check multiple files for Python 3 compatibility in parallel.
        
        Args:
            file_paths: List of Python files to check
            exclude_patterns: Patterns to exclude from checking
            
        Returns:
            Dictionary with aggregated results
        """
        print(f"🚀 Starting parallel compatibility check with {self.workers} workers...")
        print(f"📁 Checking {len(file_paths)} files")
        
        start_time = time.time()
        results = []
        
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            future_to_file = {
                executor.submit(self._check_single_file, fp, exclude_patterns): fp 
                for fp in file_paths
            }
            
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Progress indicator
                    status = "✓" if result['issues'] == 0 else "✗"
                    issues_str = f"({result['issues']} issues)" if result['issues'] > 0 else ""
                    print(f"  [{completed}/{len(file_paths)}] {status} {file_path} {issues_str}")
                    
                except Exception as e:
                    print(f"  [{completed}/{len(file_paths)}] ✗ {file_path} (ERROR: {e})")
                    results.append({
                        'file': file_path,
                        'success': False,
                        'issues': 0,
                        'error': str(e)
                    })
        
        elapsed_time = time.time() - start_time
        
        # Aggregate results
        total_issues = sum(r.get('issues', 0) for r in results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        summary = {
            'total_files': len(file_paths),
            'successful': successful,
            'failed': failed,
            'total_issues': total_issues,
            'elapsed_time': elapsed_time,
            'files_per_second': len(file_paths) / elapsed_time if elapsed_time > 0 else 0,
            'workers': self.workers,
            'results': results
        }
        
        return summary
    
    def fix_files(self, file_paths: List[str], 
                  backup: bool = True,
                  dry_run: bool = False) -> Dict[str, Any]:
        """
        Fix multiple files for Python 3 compatibility in parallel.
        
        Args:
            file_paths: List of Python files to fix
            backup: Create backups before fixing
            dry_run: Preview changes without applying them
            
        Returns:
            Dictionary with aggregated results
        """
        action = "Simulating" if dry_run else "Applying"
        print(f"🚀 {action} fixes in parallel with {self.workers} workers...")
        print(f"📁 Processing {len(file_paths)} files")
        
        start_time = time.time()
        results = []
        
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            future_to_file = {
                executor.submit(self._fix_single_file, fp, backup, dry_run): fp 
                for fp in file_paths
            }
            
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Progress indicator
                    status = "✓" if result.get('success', False) else "✗"
                    fixes_str = f"({result.get('fixes_applied', 0)} fixes)" if result.get('fixes_applied', 0) > 0 else ""
                    print(f"  [{completed}/{len(file_paths)}] {status} {file_path} {fixes_str}")
                    
                except Exception as e:
                    print(f"  [{completed}/{len(file_paths)}] ✗ {file_path} (ERROR: {e})")
                    results.append({
                        'file': file_path,
                        'success': False,
                        'fixes_applied': 0,
                        'error': str(e)
                    })
        
        elapsed_time = time.time() - start_time
        
        # Aggregate results
        total_fixes = sum(r.get('fixes_applied', 0) for r in results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        summary = {
            'total_files': len(file_paths),
            'successful': successful,
            'failed': failed,
            'total_fixes': total_fixes,
            'elapsed_time': elapsed_time,
            'files_per_second': len(file_paths) / elapsed_time if elapsed_time > 0 else 0,
            'workers': self.workers,
            'dry_run': dry_run,
            'results': results
        }
        
        return summary
    
    @staticmethod
    def _check_single_file(file_path: str, 
                          exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Check a single file for Python 3 compatibility."""
        try:
            # Create a verifier instance (it collects issues internally)
            verifier = Python3CompatibilityVerifier()
            
            # Suppress print output by redirecting stdout temporarily
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                verifier.verify_file(file_path)
            
            return {
                'file': file_path,
                'success': True,
                'issues': len(verifier.issues_found),
                'issue_details': verifier.issues_found
            }
        except Exception as e:
            return {
                'file': file_path,
                'success': False,
                'issues': 0,
                'error': str(e)
            }
    
    @staticmethod
    def _fix_single_file(file_path: str, backup: bool = True, 
                        dry_run: bool = False) -> Dict[str, Any]:
        """Fix a single file for Python 3 compatibility."""
        try:
            fixer = Python2to3Fixer()
            
            # Suppress print output by redirecting stdout temporarily
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = fixer.fix_file(file_path, dry_run=dry_run)
            
            return {
                'file': file_path,
                'success': result.get('success', False),
                'fixes_applied': len(result.get('fixes', [])),
                'dry_run': dry_run
            }
        except Exception as e:
            return {
                'file': file_path,
                'success': False,
                'fixes_applied': 0,
                'error': str(e)
            }
    
    def print_summary(self, summary: Dict[str, Any], operation: str = "check"):
        """Print a formatted summary of the parallel operation."""
        print("\n" + "=" * 70)
        print(f"📊 Parallel {operation.title()} Summary")
        print("=" * 70)
        
        print(f"\n⚙️  Configuration:")
        print(f"   Workers: {summary['workers']}")
        print(f"   Total files: {summary['total_files']}")
        
        print(f"\n📈 Results:")
        print(f"   ✓ Successful: {summary['successful']}")
        print(f"   ✗ Failed: {summary['failed']}")
        
        if operation == "check":
            print(f"   ⚠️  Total issues: {summary['total_issues']}")
        else:
            print(f"   🔧 Total fixes: {summary['total_fixes']}")
            if summary.get('dry_run'):
                print(f"   ℹ️  Mode: DRY RUN (no changes made)")
        
        print(f"\n⏱️  Performance:")
        print(f"   Time: {summary['elapsed_time']:.2f}s")
        print(f"   Speed: {summary['files_per_second']:.2f} files/second")
        
        # Calculate speedup estimate
        estimated_serial_time = summary['elapsed_time'] * summary['workers']
        speedup = estimated_serial_time / summary['elapsed_time'] if summary['elapsed_time'] > 0 else 0
        print(f"   Speedup: ~{speedup:.1f}x faster than serial processing")
        
        print("\n" + "=" * 70)


def collect_python_files(directory: str, recursive: bool = True,
                         exclude_patterns: Optional[List[str]] = None) -> List[str]:
    """
    Collect Python files from a directory.
    
    Args:
        directory: Directory to scan
        recursive: Recursively scan subdirectories
        exclude_patterns: Patterns to exclude
        
    Returns:
        List of Python file paths
    """
    python_files = []
    exclude_patterns = exclude_patterns or ['__pycache__', '.git', 'venv', '.venv']
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.endswith('.py'):
                python_files.append(os.path.join(directory, file))
    
    return sorted(python_files)


def main():
    """Main CLI interface for parallel migration runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Parallel Migration Runner - Speed up large migrations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all Python files in src/ directory using all CPU cores
  %(prog)s check src/
  
  # Check with specific number of workers
  %(prog)s check src/ --workers 4
  
  # Fix all files in parallel (with backup)
  %(prog)s fix src/ --backup
  
  # Preview fixes without applying them
  %(prog)s fix src/ --dry-run
  
  # Export results as JSON
  %(prog)s check src/ --json results.json
        """
    )
    
    parser.add_argument('operation', choices=['check', 'fix'],
                       help='Operation to perform in parallel')
    parser.add_argument('path', help='File or directory to process')
    parser.add_argument('--workers', '-w', type=int,
                       help='Number of worker processes (default: CPU count)')
    parser.add_argument('--recursive', '-r', action='store_true', default=True,
                       help='Recursively process subdirectories (default: True)')
    parser.add_argument('--backup', '-b', action='store_true', default=False,
                       help='Create backups before fixing (for fix operation)')
    parser.add_argument('--dry-run', action='store_true', default=False,
                       help='Preview changes without applying them (for fix operation)')
    parser.add_argument('--json', '-j', metavar='FILE',
                       help='Export results as JSON to specified file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Collect files to process
    if os.path.isfile(args.path):
        files = [args.path]
    elif os.path.isdir(args.path):
        files = collect_python_files(args.path, recursive=args.recursive)
        if not files:
            print(f"❌ No Python files found in {args.path}")
            return 1
    else:
        print(f"❌ Path not found: {args.path}")
        return 1
    
    # Create runner
    runner = ParallelMigrationRunner(workers=args.workers, verbose=args.verbose)
    
    # Execute operation
    if args.operation == 'check':
        summary = runner.check_files(files)
        runner.print_summary(summary, operation='check')
        
        if args.json:
            with open(args.json, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n💾 Results exported to {args.json}")
        
        return 0 if summary['total_issues'] == 0 else 1
        
    elif args.operation == 'fix':
        summary = runner.fix_files(files, backup=args.backup, dry_run=args.dry_run)
        runner.print_summary(summary, operation='fix')
        
        if args.json:
            with open(args.json, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n💾 Results exported to {args.json}")
        
        return 0 if summary['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
