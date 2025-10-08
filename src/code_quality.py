#!/usr/bin/env python3
"""
Code Quality and Complexity Analyzer

Analyzes Python code quality, complexity, and maintainability metrics.
Helps identify areas that need attention and track quality improvements during migration.
"""

import ast
import os
import re
from collections import defaultdict
from pathlib import Path


class CodeQualityAnalyzer:
    """Analyze code quality and complexity metrics for Python files."""
    
    def __init__(self):
        """Initialize the code quality analyzer."""
        self.metrics = {}
        self.summary = {}
        
    def analyze_file(self, file_path):
        """Analyze a single Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            dict: File metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                return {
                    'error': f'Syntax error: {e}',
                    'loc': 0,
                    'functions': 0,
                    'classes': 0
                }
            
            # Calculate metrics
            metrics = {
                'file': file_path,
                'loc': self._count_loc(content),
                'sloc': self._count_sloc(content),
                'comments': self._count_comments(content),
                'blank_lines': self._count_blank_lines(content),
                'functions': 0,
                'classes': 0,
                'imports': 0,
                'complexity': 0,
                'max_complexity': 0,
                'avg_function_length': 0,
                'long_functions': [],
                'complex_functions': [],
                'maintainability_index': 0
            }
            
            # Analyze AST
            self._analyze_ast(tree, metrics, content)
            
            # Calculate maintainability index
            metrics['maintainability_index'] = self._calculate_maintainability_index(metrics)
            
            # Determine quality grade
            metrics['grade'] = self._calculate_grade(metrics)
            
            return metrics
            
        except Exception as e:
            return {
                'error': f'Error analyzing file: {e}',
                'file': file_path
            }
    
    def analyze_directory(self, directory_path):
        """Analyze all Python files in a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            dict: Directory metrics
        """
        directory_path = Path(directory_path)
        python_files = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Analyze each file
        file_metrics = []
        for file_path in python_files:
            metrics = self.analyze_file(file_path)
            if 'error' not in metrics:
                file_metrics.append(metrics)
        
        # Calculate summary statistics
        self.metrics = file_metrics
        self.summary = self._calculate_summary(file_metrics)
        
        return {
            'files': file_metrics,
            'summary': self.summary
        }
    
    def _count_loc(self, content):
        """Count total lines of code."""
        return len(content.splitlines())
    
    def _count_sloc(self, content):
        """Count source lines of code (excluding blanks and comments)."""
        lines = content.splitlines()
        sloc = 0
        in_multiline_string = False
        
        for line in lines:
            stripped = line.strip()
            
            # Toggle multiline string state
            if '"""' in stripped or "'''" in stripped:
                in_multiline_string = not in_multiline_string
                continue
            
            # Skip blank lines and comments
            if not stripped or stripped.startswith('#') or in_multiline_string:
                continue
            
            sloc += 1
        
        return sloc
    
    def _count_comments(self, content):
        """Count comment lines."""
        lines = content.splitlines()
        comments = 0
        in_docstring = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect docstrings
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                comments += 1
                continue
            
            if in_docstring:
                comments += 1
            elif stripped.startswith('#'):
                comments += 1
        
        return comments
    
    def _count_blank_lines(self, content):
        """Count blank lines."""
        lines = content.splitlines()
        return sum(1 for line in lines if not line.strip())
    
    def _analyze_ast(self, tree, metrics, content):
        """Analyze AST for code structure metrics."""
        function_lengths = []
        function_complexities = []
        
        for node in ast.walk(tree):
            # Count imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics['imports'] += 1
            
            # Count classes
            elif isinstance(node, ast.ClassDef):
                metrics['classes'] += 1
            
            # Count and analyze functions
            elif isinstance(node, ast.FunctionDef):
                metrics['functions'] += 1
                
                # Calculate function complexity
                complexity = self._calculate_complexity(node)
                function_complexities.append(complexity)
                
                # Calculate function length
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    length = node.end_lineno - node.lineno + 1
                    function_lengths.append(length)
                    
                    # Track long functions (>50 lines)
                    if length > 50:
                        metrics['long_functions'].append({
                            'name': node.name,
                            'length': length,
                            'line': node.lineno
                        })
                    
                    # Track complex functions (complexity > 10)
                    if complexity > 10:
                        metrics['complex_functions'].append({
                            'name': node.name,
                            'complexity': complexity,
                            'line': node.lineno
                        })
        
        # Calculate aggregate metrics
        if function_complexities:
            metrics['complexity'] = sum(function_complexities)
            metrics['max_complexity'] = max(function_complexities)
            metrics['avg_complexity'] = round(sum(function_complexities) / len(function_complexities), 2)
        
        if function_lengths:
            metrics['avg_function_length'] = round(sum(function_lengths) / len(function_lengths), 2)
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity of a function.
        
        Simplified McCabe complexity calculation.
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_maintainability_index(self, metrics):
        """Calculate maintainability index.
        
        Simplified version based on:
        - Volume (LOC)
        - Complexity
        - Comment ratio
        
        Returns value between 0-100 (higher is better).
        """
        loc = max(metrics['sloc'], 1)
        complexity = max(metrics['complexity'], 1)
        comment_ratio = metrics['comments'] / max(metrics['loc'], 1)
        
        # Simplified formula
        # Good: low complexity, reasonable LOC, good comments
        volume_penalty = min(loc / 500, 1.0)  # Penalty for large files
        complexity_penalty = min(complexity / 50, 1.0)  # Penalty for high complexity
        comment_bonus = min(comment_ratio * 2, 0.3)  # Bonus for comments (up to 30%)
        
        index = 100 * (1 - (volume_penalty * 0.3 + complexity_penalty * 0.5 - comment_bonus))
        return max(0, min(100, round(index, 2)))
    
    def _calculate_grade(self, metrics):
        """Calculate quality grade based on maintainability index."""
        mi = metrics['maintainability_index']
        
        if mi >= 80:
            return 'A'
        elif mi >= 60:
            return 'B'
        elif mi >= 40:
            return 'C'
        elif mi >= 20:
            return 'D'
        else:
            return 'F'
    
    def _calculate_summary(self, file_metrics):
        """Calculate summary statistics across all files."""
        if not file_metrics:
            return {}
        
        total_loc = sum(m['loc'] for m in file_metrics)
        total_sloc = sum(m['sloc'] for m in file_metrics)
        total_comments = sum(m['comments'] for m in file_metrics)
        total_functions = sum(m['functions'] for m in file_metrics)
        total_classes = sum(m['classes'] for m in file_metrics)
        total_complexity = sum(m['complexity'] for m in file_metrics)
        
        # Calculate averages
        avg_mi = sum(m['maintainability_index'] for m in file_metrics) / len(file_metrics)
        
        # Grade distribution
        grade_counts = defaultdict(int)
        for m in file_metrics:
            grade_counts[m['grade']] += 1
        
        # Find most complex files
        most_complex = sorted(file_metrics, key=lambda x: x['complexity'], reverse=True)[:5]
        
        # Find lowest quality files
        lowest_quality = sorted(file_metrics, key=lambda x: x['maintainability_index'])[:5]
        
        return {
            'total_files': len(file_metrics),
            'total_loc': total_loc,
            'total_sloc': total_sloc,
            'total_comments': total_comments,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_complexity': total_complexity,
            'avg_maintainability_index': round(avg_mi, 2),
            'avg_loc_per_file': round(total_loc / len(file_metrics), 2),
            'avg_complexity_per_file': round(total_complexity / len(file_metrics), 2),
            'comment_ratio': round(total_comments / total_loc * 100, 2) if total_loc > 0 else 0,
            'grade_distribution': dict(grade_counts),
            'most_complex_files': [
                {'file': m['file'], 'complexity': m['complexity']} 
                for m in most_complex
            ],
            'lowest_quality_files': [
                {'file': m['file'], 'maintainability_index': m['maintainability_index'], 'grade': m['grade']}
                for m in lowest_quality
            ]
        }
    
    def format_report(self, include_files=False):
        """Format quality analysis report.
        
        Args:
            include_files: Include individual file metrics
            
        Returns:
            str: Formatted report
        """
        if not self.summary:
            return "No analysis data available."
        
        lines = []
        s = self.summary
        
        # Header
        lines.append('=' * 70)
        lines.append('CODE QUALITY AND COMPLEXITY ANALYSIS')
        lines.append('=' * 70)
        lines.append('')
        
        # Overall Statistics
        lines.append('Overall Statistics:')
        lines.append(f"  Total Files: {s['total_files']}")
        lines.append(f"  Total Lines: {s['total_loc']:,}")
        lines.append(f"  Source Lines (SLOC): {s['total_sloc']:,}")
        lines.append(f"  Comment Lines: {s['total_comments']:,}")
        lines.append(f"  Comment Ratio: {s['comment_ratio']:.2f}%")
        lines.append(f"  Total Functions: {s['total_functions']}")
        lines.append(f"  Total Classes: {s['total_classes']}")
        lines.append(f"  Total Complexity: {s['total_complexity']}")
        lines.append('')
        
        # Average Metrics
        lines.append('Average Metrics:')
        lines.append(f"  LOC per File: {s['avg_loc_per_file']:.2f}")
        lines.append(f"  Complexity per File: {s['avg_complexity_per_file']:.2f}")
        lines.append(f"  Maintainability Index: {s['avg_maintainability_index']:.2f}/100")
        lines.append('')
        
        # Grade Distribution
        lines.append('Quality Grade Distribution:')
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = s['grade_distribution'].get(grade, 0)
            percentage = (count / s['total_files'] * 100) if s['total_files'] > 0 else 0
            bar = '█' * int(percentage / 5)
            lines.append(f"  {grade}: {count:3d} files ({percentage:5.1f}%) {bar}")
        lines.append('')
        
        # Most Complex Files
        if s['most_complex_files']:
            lines.append('Most Complex Files:')
            for item in s['most_complex_files']:
                file_path = item['file']
                if len(file_path) > 55:
                    file_path = '...' + file_path[-52:]
                lines.append(f"  {file_path}")
                lines.append(f"    Complexity: {item['complexity']}")
            lines.append('')
        
        # Lowest Quality Files
        if s['lowest_quality_files']:
            lines.append('Files Needing Attention (Lowest Quality):')
            for item in s['lowest_quality_files']:
                file_path = item['file']
                if len(file_path) > 55:
                    file_path = '...' + file_path[-52:]
                lines.append(f"  {file_path}")
                lines.append(f"    Maintainability: {item['maintainability_index']:.2f} (Grade {item['grade']})")
            lines.append('')
        
        # Recommendations
        lines.append('Recommendations:')
        if s['avg_maintainability_index'] >= 70:
            lines.append('  ✓ Overall code quality is good!')
        elif s['avg_maintainability_index'] >= 50:
            lines.append('  ⚠ Code quality is moderate. Consider refactoring complex areas.')
        else:
            lines.append('  ✗ Code quality needs improvement. Focus on reducing complexity.')
        
        if s['comment_ratio'] < 10:
            lines.append('  ⚠ Low comment ratio. Consider adding more documentation.')
        elif s['comment_ratio'] > 30:
            lines.append('  ⚠ High comment ratio. Ensure comments are meaningful.')
        
        if s['avg_complexity_per_file'] > 50:
            lines.append('  ✗ High average complexity. Break down complex functions.')
        
        lines.append('')
        
        # Individual file metrics
        if include_files and self.metrics:
            lines.append('=' * 70)
            lines.append('INDIVIDUAL FILE METRICS')
            lines.append('=' * 70)
            lines.append('')
            
            for m in sorted(self.metrics, key=lambda x: x['maintainability_index']):
                lines.append(f"File: {m['file']}")
                lines.append(f"  LOC: {m['loc']}, SLOC: {m['sloc']}, Comments: {m['comments']}")
                lines.append(f"  Functions: {m['functions']}, Classes: {m['classes']}")
                lines.append(f"  Complexity: {m['complexity']} (max: {m['max_complexity']})")
                lines.append(f"  Maintainability: {m['maintainability_index']:.2f} (Grade {m['grade']})")
                
                if m['long_functions']:
                    lines.append(f"  Long Functions: {', '.join(f['name'] for f in m['long_functions'][:3])}")
                if m['complex_functions']:
                    lines.append(f"  Complex Functions: {', '.join(f['name'] for f in m['complex_functions'][:3])}")
                
                lines.append('')
        
        return '\n'.join(lines)
    
    def export_json(self):
        """Export analysis results as JSON-compatible dict.
        
        Returns:
            dict: Analysis results
        """
        return {
            'files': self.metrics,
            'summary': self.summary
        }


def main():
    """Main entry point for command-line usage."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description='Analyze code quality and complexity metrics'
    )
    parser.add_argument(
        'path',
        help='File or directory to analyze'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for report'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--include-files',
        action='store_true',
        help='Include individual file metrics in report'
    )
    
    args = parser.parse_args()
    
    # Analyze code
    analyzer = CodeQualityAnalyzer()
    
    if os.path.isfile(args.path):
        result = analyzer.analyze_file(args.path)
        analyzer.metrics = [result]
        analyzer.summary = analyzer._calculate_summary([result])
    else:
        analyzer.analyze_directory(args.path)
    
    # Generate output
    if args.format == 'json':
        output = json.dumps(analyzer.export_json(), indent=2)
    else:
        output = analyzer.format_report(include_files=args.include_files)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
