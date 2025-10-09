#!/usr/bin/env python3
"""
Code Complexity Analyzer for Python 2 to 3 Migration

Analyzes code complexity before and after migration to identify files
that may have become more complex and need manual refactoring.

Metrics tracked:
- Cyclomatic Complexity (McCabe)
- Lines of Code (LOC)
- Maintainability Index
- Halstead Complexity
- Comment Ratio
"""

import ast
import os
import sys
import json
import math
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate code complexity metrics."""
    
    def __init__(self):
        self.complexity = 1  # Base complexity
        self.nodes = 0
        self.operators = set()
        self.operands = set()
        self.operator_count = 0
        self.operand_count = 0
        self.functions = 0
        self.classes = 0
        self.branches = 0
        
    def visit_If(self, node):
        self.complexity += 1
        self.branches += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self.branches += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self.branches += 1
        self.generic_visit(node)
        
    def visit_Try(self, node):
        self.complexity += len(node.handlers)
        self.branches += len(node.handlers)
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        self.functions += 1
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        self.functions += 1
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self.classes += 1
        self.generic_visit(node)
        
    def visit_BinOp(self, node):
        self.operators.add(node.op.__class__.__name__)
        self.operator_count += 1
        self.generic_visit(node)
        
    def visit_UnaryOp(self, node):
        self.operators.add(node.op.__class__.__name__)
        self.operator_count += 1
        self.generic_visit(node)
        
    def visit_Compare(self, node):
        self.operator_count += len(node.ops)
        for op in node.ops:
            self.operators.add(op.__class__.__name__)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        self.operands.add(node.id)
        self.operand_count += 1
        self.generic_visit(node)
        
    def visit_Constant(self, node):
        self.operands.add(str(node.value))
        self.operand_count += 1
        self.generic_visit(node)
        
    def generic_visit(self, node):
        self.nodes += 1
        super().generic_visit(node)


class ComplexityAnalyzer:
    """Analyze code complexity for Python files."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        self.backup_dir = backup_dir
        self.results = {}
        
    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a single Python file and return complexity metrics."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate basic metrics
            lines = content.split('\n')
            loc = len([line for line in lines if line.strip()])
            sloc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comments = len([line for line in lines if line.strip().startswith('#')])
            comment_ratio = comments / max(loc, 1)
            
            # Parse AST and calculate complexity
            try:
                tree = ast.parse(content)
                visitor = ComplexityVisitor()
                visitor.visit(tree)
                
                # Cyclomatic complexity
                cyclomatic = visitor.complexity
                
                # Halstead metrics
                n1 = len(visitor.operators)  # Unique operators
                n2 = len(visitor.operands)   # Unique operands
                N1 = visitor.operator_count   # Total operators
                N2 = visitor.operand_count    # Total operands
                
                vocabulary = n1 + n2
                length = N1 + N2
                
                if vocabulary > 0 and n2 > 0:
                    volume = length * math.log2(vocabulary) if vocabulary > 1 else 0
                    difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
                    effort = difficulty * volume
                else:
                    volume = difficulty = effort = 0
                
                # Maintainability Index (Microsoft formula)
                # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
                if volume > 0 and sloc > 0:
                    mi = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic - 16.2 * math.log(sloc)
                    mi = max(0, min(100, mi * 100 / 171))  # Normalize to 0-100
                else:
                    mi = 100
                
                return {
                    'loc': loc,
                    'sloc': sloc,
                    'comments': comments,
                    'comment_ratio': round(comment_ratio, 3),
                    'cyclomatic': cyclomatic,
                    'maintainability': round(mi, 2),
                    'halstead_volume': round(volume, 2),
                    'halstead_difficulty': round(difficulty, 2),
                    'halstead_effort': round(effort, 2),
                    'functions': visitor.functions,
                    'classes': visitor.classes,
                    'branches': visitor.branches,
                    'nodes': visitor.nodes,
                    'status': 'success'
                }
                
            except SyntaxError as e:
                return {
                    'loc': loc,
                    'sloc': sloc,
                    'status': 'syntax_error',
                    'error': str(e)
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def compare_with_backup(self, filepath: str, backup_filepath: str) -> Dict:
        """Compare complexity between current and backup version."""
        current = self.analyze_file(filepath)
        backup = self.analyze_file(backup_filepath)
        
        if current['status'] != 'success' or backup['status'] != 'success':
            return {
                'filepath': filepath,
                'current': current,
                'backup': backup,
                'comparison': 'unavailable'
            }
        
        # Calculate changes
        changes = {}
        metrics = ['loc', 'sloc', 'cyclomatic', 'maintainability', 'halstead_difficulty']
        
        for metric in metrics:
            if metric in current and metric in backup:
                old_val = backup[metric]
                new_val = current[metric]
                delta = new_val - old_val
                
                if old_val != 0:
                    percent = (delta / old_val) * 100
                else:
                    percent = 100 if delta > 0 else 0
                
                changes[metric] = {
                    'old': old_val,
                    'new': new_val,
                    'delta': round(delta, 2),
                    'percent': round(percent, 2)
                }
        
        # Determine overall trend
        complexity_increased = (
            changes.get('cyclomatic', {}).get('delta', 0) > 0 or
            changes.get('halstead_difficulty', {}).get('delta', 0) > 0
        )
        
        maintainability_decreased = changes.get('maintainability', {}).get('delta', 0) < -5
        
        if complexity_increased and maintainability_decreased:
            trend = 'significantly_worse'
        elif complexity_increased or maintainability_decreased:
            trend = 'worse'
        elif changes.get('maintainability', {}).get('delta', 0) > 5:
            trend = 'better'
        else:
            trend = 'neutral'
        
        return {
            'filepath': filepath,
            'current': current,
            'backup': backup,
            'changes': changes,
            'trend': trend,
            'comparison': 'success'
        }
    
    def analyze_directory(self, directory: str, compare_backups: bool = False) -> Dict:
        """Analyze all Python files in a directory."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'directory': directory,
            'files': {},
            'summary': {
                'total_files': 0,
                'analyzed': 0,
                'errors': 0,
                'syntax_errors': 0
            }
        }
        
        # Find all Python files
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, directory)
                    
                    results['summary']['total_files'] += 1
                    
                    if compare_backups and self.backup_dir:
                        # Try to find backup file
                        backup_path = os.path.join(self.backup_dir, rel_path)
                        if os.path.exists(backup_path):
                            result = self.compare_with_backup(filepath, backup_path)
                        else:
                            result = {
                                'filepath': filepath,
                                'current': self.analyze_file(filepath),
                                'comparison': 'no_backup'
                            }
                    else:
                        result = {
                            'filepath': filepath,
                            'current': self.analyze_file(filepath),
                            'comparison': 'no_comparison'
                        }
                    
                    results['files'][rel_path] = result
                    
                    # Update summary
                    current = result.get('current', {})
                    if current.get('status') == 'success':
                        results['summary']['analyzed'] += 1
                    elif current.get('status') == 'syntax_error':
                        results['summary']['syntax_errors'] += 1
                    else:
                        results['summary']['errors'] += 1
        
        # Calculate aggregate metrics
        if compare_backups:
            self._calculate_comparison_summary(results)
        else:
            self._calculate_basic_summary(results)
        
        return results
    
    def _calculate_basic_summary(self, results: Dict):
        """Calculate summary statistics for basic analysis."""
        metrics = defaultdict(list)
        
        for file_result in results['files'].values():
            current = file_result.get('current', {})
            if current.get('status') == 'success':
                for key in ['loc', 'sloc', 'cyclomatic', 'maintainability', 'halstead_difficulty']:
                    if key in current:
                        metrics[key].append(current[key])
        
        summary = results['summary']
        for key, values in metrics.items():
            if values:
                summary[f'avg_{key}'] = round(sum(values) / len(values), 2)
                summary[f'max_{key}'] = max(values)
                summary[f'min_{key}'] = min(values)
    
    def _calculate_comparison_summary(self, results: Dict):
        """Calculate summary statistics for comparison analysis."""
        self._calculate_basic_summary(results)
        
        trends = defaultdict(int)
        files_worse = []
        files_better = []
        
        for rel_path, file_result in results['files'].items():
            if file_result.get('comparison') == 'success':
                trend = file_result.get('trend')
                trends[trend] += 1
                
                if trend in ['worse', 'significantly_worse']:
                    files_worse.append({
                        'file': rel_path,
                        'trend': trend,
                        'changes': file_result.get('changes', {})
                    })
                elif trend == 'better':
                    files_better.append({
                        'file': rel_path,
                        'trend': trend,
                        'changes': file_result.get('changes', {})
                    })
        
        # Sort by complexity increase
        files_worse.sort(
            key=lambda x: x['changes'].get('cyclomatic', {}).get('delta', 0),
            reverse=True
        )
        
        results['summary']['trends'] = dict(trends)
        results['summary']['files_needing_review'] = files_worse[:10]  # Top 10
        results['summary']['files_improved'] = files_better[:5]  # Top 5
    
    def generate_report(self, results: Dict, output_file: Optional[str] = None,
                       format: str = 'text') -> str:
        """Generate a human-readable report."""
        
        if format == 'json':
            report = json.dumps(results, indent=2)
        else:
            report = self._generate_text_report(results)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            return f"Report saved to {output_file}"
        
        return report
    
    def _generate_text_report(self, results: Dict) -> str:
        """Generate text format report."""
        lines = []
        lines.append("=" * 80)
        lines.append("CODE COMPLEXITY ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {results['timestamp']}")
        lines.append(f"Directory: {results['directory']}")
        lines.append("")
        
        summary = results['summary']
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Python files: {summary['total_files']}")
        lines.append(f"Successfully analyzed: {summary['analyzed']}")
        lines.append(f"Syntax errors: {summary['syntax_errors']}")
        lines.append(f"Other errors: {summary['errors']}")
        lines.append("")
        
        # Average metrics
        if 'avg_loc' in summary:
            lines.append("Average Metrics:")
            lines.append(f"  Lines of Code (LOC): {summary.get('avg_loc', 0):.0f}")
            lines.append(f"  Cyclomatic Complexity: {summary.get('avg_cyclomatic', 0):.1f}")
            lines.append(f"  Maintainability Index: {summary.get('avg_maintainability', 0):.1f}/100")
            lines.append(f"  Halstead Difficulty: {summary.get('avg_halstead_difficulty', 0):.1f}")
            lines.append("")
        
        # Comparison results
        if 'trends' in summary:
            lines.append("MIGRATION IMPACT ANALYSIS")
            lines.append("-" * 80)
            trends = summary['trends']
            lines.append("Complexity Trends:")
            lines.append(f"  Significantly Worse: {trends.get('significantly_worse', 0)} files")
            lines.append(f"  Worse: {trends.get('worse', 0)} files")
            lines.append(f"  Neutral: {trends.get('neutral', 0)} files")
            lines.append(f"  Better: {trends.get('better', 0)} files")
            lines.append("")
            
            # Files needing review
            if summary.get('files_needing_review'):
                lines.append("FILES NEEDING REVIEW (Top 10):")
                lines.append("-" * 80)
                for item in summary['files_needing_review']:
                    lines.append(f"\n{item['file']} [{item['trend'].upper()}]")
                    changes = item['changes']
                    if 'cyclomatic' in changes:
                        c = changes['cyclomatic']
                        lines.append(f"  Cyclomatic: {c['old']} → {c['new']} ({c['delta']:+.0f}, {c['percent']:+.1f}%)")
                    if 'maintainability' in changes:
                        m = changes['maintainability']
                        lines.append(f"  Maintainability: {m['old']:.1f} → {m['new']:.1f} ({m['delta']:+.1f}, {m['percent']:+.1f}%)")
                lines.append("")
            
            # Improved files
            if summary.get('files_improved'):
                lines.append("FILES IMPROVED (Top 5):")
                lines.append("-" * 80)
                for item in summary['files_improved']:
                    lines.append(f"\n{item['file']}")
                    changes = item['changes']
                    if 'maintainability' in changes:
                        m = changes['maintainability']
                        lines.append(f"  Maintainability: {m['old']:.1f} → {m['new']:.1f} ({m['delta']:+.1f})")
                lines.append("")
        
        lines.append("=" * 80)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        
        if 'trends' in summary:
            worse_count = trends.get('significantly_worse', 0) + trends.get('worse', 0)
            if worse_count > 0:
                lines.append(f"⚠️  {worse_count} files have increased in complexity after migration.")
                lines.append("   Consider manual refactoring for files listed above.")
                lines.append("")
        
        if summary.get('avg_cyclomatic', 0) > 10:
            lines.append("⚠️  Average cyclomatic complexity is high (>10).")
            lines.append("   Consider breaking down complex functions into smaller ones.")
            lines.append("")
        
        if summary.get('avg_maintainability', 100) < 65:
            lines.append("⚠️  Average maintainability index is low (<65).")
            lines.append("   Focus on improving code structure and documentation.")
            lines.append("")
        
        lines.append("✓ Analysis complete!")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze code complexity before and after migration'
    )
    parser.add_argument(
        'directory',
        help='Directory to analyze'
    )
    parser.add_argument(
        '--backup-dir',
        help='Backup directory for comparison'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare with backup versions'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for report'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    analyzer = ComplexityAnalyzer(backup_dir=args.backup_dir)
    
    print(f"Analyzing {args.directory}...")
    results = analyzer.analyze_directory(args.directory, compare_backups=args.compare)
    
    report = analyzer.generate_report(results, output_file=args.output, format=args.format)
    
    if not args.output:
        print(report)


if __name__ == '__main__':
    main()
