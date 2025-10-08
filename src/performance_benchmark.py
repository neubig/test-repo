#!/usr/bin/env python3
"""
Performance Benchmark Tool for Python 2 to 3 Migration

Compares execution time and memory usage between Python 2 and Python 3 code
to quantify performance improvements and identify regressions.
"""

import ast
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PerformanceBenchmark:
    """Benchmarks Python code performance across Python 2 and 3."""
    
    def __init__(self, python2_cmd='python2', python3_cmd='python3'):
        """
        Initialize the performance benchmark.
        
        Args:
            python2_cmd: Command to run Python 2 (default: python2)
            python3_cmd: Command to run Python 3 (default: python3)
        """
        self.python2_cmd = python2_cmd
        self.python3_cmd = python3_cmd
        self.results = []
        
    def check_environment(self) -> Dict[str, any]:
        """
        Check if both Python 2 and 3 are available.
        
        Returns:
            Dictionary with environment information and availability status
        """
        env_info = {
            'python2_available': False,
            'python3_available': False,
            'python2_version': None,
            'python3_version': None,
            'platform': platform.platform(),
            'processor': platform.processor() or 'unknown',
        }
        
        # Check Python 2
        try:
            result = subprocess.run(
                [self.python2_cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_output = result.stdout + result.stderr
            env_info['python2_available'] = result.returncode == 0
            env_info['python2_version'] = version_output.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
            
        # Check Python 3
        try:
            result = subprocess.run(
                [self.python3_cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            env_info['python3_available'] = result.returncode == 0
            env_info['python3_version'] = result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
            
        return env_info
    
    def _create_benchmark_script(self, code_file: str, iterations: int = 100) -> str:
        """
        Create a benchmark wrapper script.
        
        Args:
            code_file: Path to the code file to benchmark
            iterations: Number of iterations to run
            
        Returns:
            Path to the temporary benchmark script
        """
        benchmark_template = '''
import gc
import sys
import time
import traceback

def benchmark_code():
    """Run the benchmark."""
    # Import the module
    sys.path.insert(0, "{module_dir}")
    
    try:
        # Try to import and run
        import {module_name}
        
        # Collect all callable functions
        functions = []
        for name in dir({module_name}):
            if not name.startswith('_'):
                obj = getattr({module_name}, name)
                if callable(obj):
                    functions.append((name, obj))
        
        # Benchmark each function
        results = {{}}
        for name, func in functions:
            try:
                # Warm up
                func()
                
                # Benchmark
                gc.collect()
                start = time.time()
                for _ in range({iterations}):
                    func()
                end = time.time()
                
                results[name] = {{
                    'time': end - start,
                    'iterations': {iterations},
                    'avg_time': (end - start) / {iterations}
                }}
            except Exception as e:
                results[name] = {{'error': str(e)}}
        
        return results
    except Exception as e:
        return {{'import_error': str(e), 'traceback': traceback.format_exc()}}

if __name__ == '__main__':
    gc.disable()
    results = benchmark_code()
    gc.enable()
    
    # Print results as JSON
    import json
    print(json.dumps(results))
'''
        
        # Extract module info
        code_path = Path(code_file)
        module_dir = str(code_path.parent.absolute())
        module_name = code_path.stem
        
        script_content = benchmark_template.format(
            module_dir=module_dir,
            module_name=module_name,
            iterations=iterations
        )
        
        # Create temporary script
        fd, script_path = tempfile.mkstemp(suffix='.py', text=True)
        os.write(fd, script_content.encode('utf-8'))
        os.close(fd)
        
        return script_path
    
    def benchmark_file(self, file_path: str, iterations: int = 100, 
                       timeout: int = 30) -> Dict[str, any]:
        """
        Benchmark a single Python file.
        
        Args:
            file_path: Path to the Python file to benchmark
            iterations: Number of iterations to run (default: 100)
            timeout: Maximum execution time in seconds (default: 30)
            
        Returns:
            Dictionary with benchmark results
        """
        result = {
            'file': file_path,
            'iterations': iterations,
            'python2': None,
            'python3': None,
            'comparison': None,
            'status': 'pending'
        }
        
        # Validate file exists
        if not os.path.exists(file_path):
            result['status'] = 'error'
            result['error'] = f"File not found: {file_path}"
            return result
        
        # Check if file is valid Python
        try:
            with open(file_path, 'r') as f:
                ast.parse(f.read())
        except SyntaxError as e:
            result['status'] = 'error'
            result['error'] = f"Syntax error: {e}"
            return result
        
        benchmark_script = None
        try:
            # Create benchmark script
            benchmark_script = self._create_benchmark_script(file_path, iterations)
            
            # Run with Python 2
            result['python2'] = self._run_benchmark(
                self.python2_cmd, benchmark_script, timeout
            )
            
            # Run with Python 3
            result['python3'] = self._run_benchmark(
                self.python3_cmd, benchmark_script, timeout
            )
            
            # Compare results
            result['comparison'] = self._compare_results(
                result['python2'], result['python3']
            )
            
            result['status'] = 'completed'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        finally:
            # Clean up temporary script
            if benchmark_script and os.path.exists(benchmark_script):
                os.unlink(benchmark_script)
        
        return result
    
    def _run_benchmark(self, python_cmd: str, script_path: str, 
                       timeout: int) -> Dict[str, any]:
        """
        Run benchmark with specified Python command.
        
        Args:
            python_cmd: Python command to use
            script_path: Path to benchmark script
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary with benchmark results
        """
        try:
            start_time = time.time()
            result = subprocess.run(
                [python_cmd, script_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            end_time = time.time()
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return {
                        'success': True,
                        'data': data,
                        'total_time': end_time - start_time,
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': 'Failed to parse benchmark output',
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
            else:
                return {
                    'success': False,
                    'error': f"Benchmark failed with exit code {result.returncode}",
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Benchmark timed out after {timeout} seconds"
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f"Python interpreter not found: {python_cmd}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _compare_results(self, py2_result: Dict, py3_result: Dict) -> Dict[str, any]:
        """
        Compare Python 2 and Python 3 benchmark results.
        
        Args:
            py2_result: Python 2 benchmark results
            py3_result: Python 3 benchmark results
            
        Returns:
            Dictionary with comparison statistics
        """
        comparison = {
            'speedup': None,
            'slower': None,
            'performance_change': None,
            'improvements': [],
            'regressions': [],
            'status': 'incomplete'
        }
        
        if not py2_result or not py2_result.get('success'):
            comparison['status'] = 'python2_failed'
            return comparison
            
        if not py3_result or not py3_result.get('success'):
            comparison['status'] = 'python3_failed'
            return comparison
        
        py2_time = py2_result.get('total_time', 0)
        py3_time = py3_result.get('total_time', 0)
        
        if py2_time > 0 and py3_time > 0:
            speedup = py2_time / py3_time
            comparison['speedup'] = speedup
            comparison['slower'] = py3_time / py2_time if speedup < 1 else None
            comparison['performance_change'] = ((py2_time - py3_time) / py2_time) * 100
            
            if speedup > 1.05:  # More than 5% faster
                comparison['improvements'].append(f"Python 3 is {speedup:.2f}x faster")
            elif speedup < 0.95:  # More than 5% slower
                comparison['regressions'].append(f"Python 3 is {1/speedup:.2f}x slower")
            
            comparison['status'] = 'completed'
        
        return comparison
    
    def benchmark_directory(self, directory: str, iterations: int = 100,
                           timeout: int = 30, pattern: str = '*.py') -> List[Dict]:
        """
        Benchmark all Python files in a directory.
        
        Args:
            directory: Directory to scan
            iterations: Number of iterations per file
            timeout: Maximum execution time per file
            pattern: File pattern to match (default: *.py)
            
        Returns:
            List of benchmark results
        """
        results = []
        
        # Find all Python files
        path = Path(directory)
        python_files = list(path.rglob(pattern))
        
        for file_path in python_files:
            # Skip test files and __init__.py
            if 'test' in str(file_path).lower() or file_path.name == '__init__.py':
                continue
            
            result = self.benchmark_file(str(file_path), iterations, timeout)
            results.append(result)
        
        self.results.extend(results)
        return results
    
    def generate_report(self, results: Optional[List[Dict]] = None,
                       format: str = 'text') -> str:
        """
        Generate a performance report.
        
        Args:
            results: List of benchmark results (default: use stored results)
            format: Output format ('text' or 'json')
            
        Returns:
            Formatted report string
        """
        results = results or self.results
        
        if format == 'json':
            return json.dumps({
                'summary': self._generate_summary(results),
                'results': results
            }, indent=2)
        else:
            return self._generate_text_report(results)
    
    def _generate_summary(self, results: List[Dict]) -> Dict[str, any]:
        """Generate summary statistics."""
        summary = {
            'total_files': len(results),
            'completed': 0,
            'errors': 0,
            'python2_failures': 0,
            'python3_failures': 0,
            'improvements': 0,
            'regressions': 0,
            'avg_speedup': 0.0,
            'total_speedup': 0.0
        }
        
        speedups = []
        for result in results:
            if result['status'] == 'completed':
                summary['completed'] += 1
                comparison = result.get('comparison', {})
                
                if comparison.get('status') == 'completed':
                    speedup = comparison.get('speedup', 1.0)
                    speedups.append(speedup)
                    
                    if speedup > 1.05:
                        summary['improvements'] += 1
                    elif speedup < 0.95:
                        summary['regressions'] += 1
                elif comparison.get('status') == 'python2_failed':
                    summary['python2_failures'] += 1
                elif comparison.get('status') == 'python3_failed':
                    summary['python3_failures'] += 1
            else:
                summary['errors'] += 1
        
        if speedups:
            summary['avg_speedup'] = sum(speedups) / len(speedups)
            summary['total_speedup'] = sum(speedups)
        
        return summary
    
    def _generate_text_report(self, results: List[Dict]) -> str:
        """Generate text format report."""
        lines = []
        lines.append("=" * 80)
        lines.append("Performance Benchmark Report".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        summary = self._generate_summary(results)
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total files benchmarked: {summary['total_files']}")
        lines.append(f"Successfully completed: {summary['completed']}")
        lines.append(f"Errors: {summary['errors']}")
        lines.append(f"Python 2 failures: {summary['python2_failures']}")
        lines.append(f"Python 3 failures: {summary['python3_failures']}")
        lines.append("")
        
        if summary['avg_speedup'] > 0:
            lines.append(f"Average speedup: {summary['avg_speedup']:.2f}x")
            lines.append(f"Performance improvements: {summary['improvements']}")
            lines.append(f"Performance regressions: {summary['regressions']}")
            
            if summary['avg_speedup'] > 1.0:
                improvement = (summary['avg_speedup'] - 1.0) * 100
                lines.append(f"✓ Overall: Python 3 is {improvement:.1f}% faster on average")
            elif summary['avg_speedup'] < 1.0:
                regression = (1.0 - summary['avg_speedup']) * 100
                lines.append(f"✗ Overall: Python 3 is {regression:.1f}% slower on average")
            else:
                lines.append("○ Overall: No significant performance difference")
        
        lines.append("")
        lines.append("")
        
        # Detailed results
        lines.append("DETAILED RESULTS")
        lines.append("-" * 80)
        
        for result in results:
            lines.append(f"\nFile: {result['file']}")
            lines.append(f"Status: {result['status']}")
            
            if result['status'] == 'error':
                lines.append(f"Error: {result.get('error', 'Unknown error')}")
                continue
            
            if result['status'] != 'completed':
                continue
            
            py2 = result.get('python2', {})
            py3 = result.get('python3', {})
            comparison = result.get('comparison', {})
            
            if py2.get('success'):
                lines.append(f"  Python 2 time: {py2.get('total_time', 0):.4f}s")
            else:
                lines.append(f"  Python 2: Failed - {py2.get('error', 'Unknown error')}")
            
            if py3.get('success'):
                lines.append(f"  Python 3 time: {py3.get('total_time', 0):.4f}s")
            else:
                lines.append(f"  Python 3: Failed - {py3.get('error', 'Unknown error')}")
            
            if comparison.get('status') == 'completed':
                speedup = comparison.get('speedup', 0)
                change = comparison.get('performance_change', 0)
                
                if speedup > 1.05:
                    lines.append(f"  ✓ Speedup: {speedup:.2f}x faster ({change:.1f}% improvement)")
                elif speedup < 0.95:
                    lines.append(f"  ✗ Regression: {1/speedup:.2f}x slower ({abs(change):.1f}% slower)")
                else:
                    lines.append(f"  ○ Similar performance (±5%)")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Benchmark Python code performance across Python 2 and 3'
    )
    parser.add_argument('path', help='File or directory to benchmark')
    parser.add_argument('-i', '--iterations', type=int, default=100,
                       help='Number of iterations per benchmark (default: 100)')
    parser.add_argument('-t', '--timeout', type=int, default=30,
                       help='Timeout per file in seconds (default: 30)')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--python2', default='python2',
                       help='Python 2 command (default: python2)')
    parser.add_argument('--python3', default='python3',
                       help='Python 3 command (default: python3)')
    
    args = parser.parse_args()
    
    # Create benchmark
    benchmark = PerformanceBenchmark(
        python2_cmd=args.python2,
        python3_cmd=args.python3
    )
    
    # Check environment
    env_info = benchmark.check_environment()
    
    if not env_info['python2_available'] and not env_info['python3_available']:
        print("Error: Neither Python 2 nor Python 3 found", file=sys.stderr)
        sys.exit(1)
    
    if not env_info['python2_available']:
        print("Warning: Python 2 not found - will only test Python 3", file=sys.stderr)
    
    if not env_info['python3_available']:
        print("Warning: Python 3 not found - will only test Python 2", file=sys.stderr)
    
    # Run benchmark
    if os.path.isfile(args.path):
        results = [benchmark.benchmark_file(args.path, args.iterations, args.timeout)]
    elif os.path.isdir(args.path):
        results = benchmark.benchmark_directory(args.path, args.iterations, args.timeout)
    else:
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # Generate report
    report = benchmark.generate_report(results, args.format)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
