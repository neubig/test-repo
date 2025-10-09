#!/usr/bin/env python3
"""
Code Smell Detector

Identifies code smells and anti-patterns in Python code, providing
actionable suggestions for improvement. Perfect for cleaning up code
during Python 2 to 3 migration.
"""

import ast
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class CodeSmell:
    """Represents a detected code smell."""
    category: str
    severity: str  # 'low', 'medium', 'high'
    file: str
    line: int
    column: int
    message: str
    suggestion: str
    code_snippet: Optional[str] = None


class CodeSmellDetector:
    """Detects various code smells in Python code."""
    
    def __init__(self, max_function_length=50, max_parameters=5, max_nesting=4):
        self.max_function_length = max_function_length
        self.max_parameters = max_parameters
        self.max_nesting = max_nesting
        self.smells: List[CodeSmell] = []
        
    def analyze_file(self, filepath: str) -> List[CodeSmell]:
        """Analyze a single Python file for code smells."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Parse the AST
            try:
                tree = ast.parse(content, filename=filepath)
            except SyntaxError as e:
                return [CodeSmell(
                    category='syntax',
                    severity='high',
                    file=filepath,
                    line=e.lineno or 0,
                    column=e.offset or 0,
                    message=f'Syntax error: {e.msg}',
                    suggestion='Fix the syntax error before analyzing for smells'
                )]
            
            file_smells = []
            
            # Run various smell detectors
            file_smells.extend(self._detect_long_functions(tree, filepath, lines))
            file_smells.extend(self._detect_too_many_parameters(tree, filepath, lines))
            file_smells.extend(self._detect_deep_nesting(tree, filepath, lines))
            file_smells.extend(self._detect_magic_numbers(tree, filepath, lines))
            file_smells.extend(self._detect_mutable_defaults(tree, filepath, lines))
            file_smells.extend(self._detect_missing_docstrings(tree, filepath, lines))
            file_smells.extend(self._detect_duplicate_code(lines, filepath))
            file_smells.extend(self._detect_global_usage(tree, filepath, lines))
            file_smells.extend(self._detect_bare_except(tree, filepath, lines))
            file_smells.extend(self._detect_long_lines(lines, filepath))
            
            return file_smells
            
        except Exception as e:
            return [CodeSmell(
                category='error',
                severity='high',
                file=filepath,
                line=0,
                column=0,
                message=f'Error analyzing file: {e}',
                suggestion='Check if the file is valid Python code'
            )]
    
    def analyze_directory(self, directory: str, recursive: bool = True) -> List[CodeSmell]:
        """Analyze all Python files in a directory."""
        all_smells = []
        
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and common exclusions
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    all_smells.extend(self.analyze_file(filepath))
            
            if not recursive:
                break
        
        self.smells = all_smells
        return all_smells
    
    def _detect_long_functions(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect functions that are too long."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate function length
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    
                    if func_length > self.max_function_length:
                        severity = 'high' if func_length > self.max_function_length * 2 else 'medium'
                        smells.append(CodeSmell(
                            category='complexity',
                            severity=severity,
                            file=filepath,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f'Function "{node.name}" is too long ({func_length} lines)',
                            suggestion=f'Consider breaking this function into smaller, focused functions (max recommended: {self.max_function_length} lines)',
                            code_snippet=self._get_code_snippet(lines, node.lineno, min(node.lineno + 3, len(lines)))
                        ))
        
        return smells
    
    def _detect_too_many_parameters(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect functions with too many parameters."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                param_count = len(node.args.args) + len(node.args.kwonlyargs)
                
                if param_count > self.max_parameters:
                    severity = 'high' if param_count > self.max_parameters * 2 else 'medium'
                    smells.append(CodeSmell(
                        category='complexity',
                        severity=severity,
                        file=filepath,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f'Function "{node.name}" has too many parameters ({param_count})',
                        suggestion=f'Consider using a parameter object or **kwargs (max recommended: {self.max_parameters} parameters)',
                        code_snippet=self._get_code_snippet(lines, node.lineno, node.lineno + 1)
                    ))
        
        return smells
    
    def _detect_deep_nesting(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect deeply nested code blocks."""
        smells = []
        
        def check_nesting(node, depth=0, parent_line=0):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                depth += 1
                parent_line = node.lineno
                
                if depth > self.max_nesting:
                    smells.append(CodeSmell(
                        category='complexity',
                        severity='medium',
                        file=filepath,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f'Code is nested too deeply (level {depth})',
                        suggestion='Consider extracting nested logic into separate functions or using early returns',
                        code_snippet=self._get_code_snippet(lines, node.lineno, node.lineno + 1)
                    ))
            
            for child in ast.iter_child_nodes(node):
                check_nesting(child, depth, parent_line)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                check_nesting(node, 0, node.lineno)
        
        return smells
    
    def _detect_magic_numbers(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect magic numbers in code."""
        smells = []
        acceptable_numbers = {0, 1, -1, 2, 10, 100, 1000}  # Common acceptable values
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Num):
                # Skip if in a constant assignment or docstring
                if isinstance(node.n, (int, float)) and node.n not in acceptable_numbers:
                    smells.append(CodeSmell(
                        category='maintainability',
                        severity='low',
                        file=filepath,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f'Magic number found: {node.n}',
                        suggestion='Consider extracting this number into a named constant',
                        code_snippet=self._get_code_snippet(lines, node.lineno, node.lineno + 1)
                    ))
        
        return smells
    
    def _detect_mutable_defaults(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect mutable default arguments."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        smells.append(CodeSmell(
                            category='bugs',
                            severity='high',
                            file=filepath,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f'Function "{node.name}" has mutable default argument',
                            suggestion='Use None as default and create the mutable object inside the function',
                            code_snippet=self._get_code_snippet(lines, node.lineno, node.lineno + 1)
                        ))
        
        return smells
    
    def _detect_missing_docstrings(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect functions and classes missing docstrings."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Skip private methods and very short functions
                if node.name.startswith('_'):
                    continue
                
                # Check if it has a docstring
                has_docstring = (
                    ast.get_docstring(node) is not None
                )
                
                if not has_docstring:
                    item_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    smells.append(CodeSmell(
                        category='documentation',
                        severity='low',
                        file=filepath,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f'{item_type.capitalize()} "{node.name}" is missing a docstring',
                        suggestion=f'Add a docstring explaining what this {item_type} does',
                        code_snippet=self._get_code_snippet(lines, node.lineno, node.lineno + 1)
                    ))
        
        return smells
    
    def _detect_duplicate_code(self, lines: List[str], filepath: str) -> List[CodeSmell]:
        """Detect duplicate code blocks."""
        smells = []
        min_duplicate_lines = 5  # Minimum lines to consider as duplicate
        
        # Simple duplicate detection: look for identical sequences of lines
        line_sequences = {}
        
        for i in range(len(lines) - min_duplicate_lines):
            # Skip empty or comment-only blocks
            sequence = tuple(lines[i:i + min_duplicate_lines])
            normalized = tuple(line.strip() for line in sequence if line.strip() and not line.strip().startswith('#'))
            
            if len(normalized) >= min_duplicate_lines:
                if normalized in line_sequences:
                    line_sequences[normalized].append(i + 1)
                else:
                    line_sequences[normalized] = [i + 1]
        
        # Report duplicates
        for sequence, locations in line_sequences.items():
            if len(locations) > 1:
                smells.append(CodeSmell(
                    category='duplication',
                    severity='medium',
                    file=filepath,
                    line=locations[0],
                    column=0,
                    message=f'Duplicate code block found at lines: {", ".join(map(str, locations))}',
                    suggestion='Consider extracting this code into a reusable function',
                    code_snippet='\n'.join(sequence[:3]) + '...'
                ))
        
        return smells
    
    def _detect_global_usage(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect usage of global variables."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                smells.append(CodeSmell(
                    category='maintainability',
                    severity='medium',
                    file=filepath,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f'Global variable(s) used: {", ".join(node.names)}',
                    suggestion='Consider passing variables as parameters or using class attributes',
                    code_snippet=self._get_code_snippet(lines, node.lineno, node.lineno + 1)
                ))
        
        return smells
    
    def _detect_bare_except(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[CodeSmell]:
        """Detect bare except clauses."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:  # Bare except
                    smells.append(CodeSmell(
                        category='bugs',
                        severity='high',
                        file=filepath,
                        line=node.lineno,
                        column=node.col_offset,
                        message='Bare except clause found',
                        suggestion='Catch specific exceptions instead of using bare except',
                        code_snippet=self._get_code_snippet(lines, node.lineno, node.lineno + 1)
                    ))
        
        return smells
    
    def _detect_long_lines(self, lines: List[str], filepath: str, max_length: int = 120) -> List[CodeSmell]:
        """Detect lines that are too long."""
        smells = []
        
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                smells.append(CodeSmell(
                    category='style',
                    severity='low',
                    file=filepath,
                    line=i,
                    column=max_length,
                    message=f'Line is too long ({len(line)} characters)',
                    suggestion=f'Break this line into multiple lines (max recommended: {max_length} characters)',
                    code_snippet=line[:80] + '...' if len(line) > 80 else line
                ))
        
        return smells
    
    def _get_code_snippet(self, lines: List[str], start: int, end: int) -> str:
        """Extract a code snippet from the lines."""
        try:
            snippet_lines = lines[start - 1:end]
            return '\n'.join(snippet_lines)
        except:
            return ''
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate a report of all detected smells."""
        if output_format == 'json':
            import json
            return json.dumps([{
                'category': s.category,
                'severity': s.severity,
                'file': s.file,
                'line': s.line,
                'column': s.column,
                'message': s.message,
                'suggestion': s.suggestion,
                'code_snippet': s.code_snippet
            } for s in self.smells], indent=2)
        
        elif output_format == 'html':
            return self._generate_html_report()
        
        else:  # text format
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate a text report."""
        if not self.smells:
            return "✅ No code smells detected! Your code looks great!"
        
        # Group by category and severity
        by_category = defaultdict(list)
        by_severity = defaultdict(list)
        
        for smell in self.smells:
            by_category[smell.category].append(smell)
            by_severity[smell.severity].append(smell)
        
        report = []
        report.append("=" * 80)
        report.append("CODE SMELL DETECTION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total smells found: {len(self.smells)}")
        report.append(f"  • High severity:   {len(by_severity['high'])}")
        report.append(f"  • Medium severity: {len(by_severity['medium'])}")
        report.append(f"  • Low severity:    {len(by_severity['low'])}")
        report.append("")
        
        # By category
        report.append("BY CATEGORY")
        report.append("-" * 80)
        for category, smells in sorted(by_category.items()):
            report.append(f"  • {category.capitalize()}: {len(smells)}")
        report.append("")
        
        # Detailed findings
        report.append("DETAILED FINDINGS")
        report.append("=" * 80)
        
        for severity in ['high', 'medium', 'low']:
            if severity in by_severity:
                report.append("")
                report.append(f"{severity.upper()} SEVERITY ({len(by_severity[severity])} issues)")
                report.append("-" * 80)
                
                for smell in by_severity[severity]:
                    report.append(f"\n📍 {smell.file}:{smell.line}:{smell.column}")
                    report.append(f"   Category: {smell.category}")
                    report.append(f"   Issue: {smell.message}")
                    report.append(f"   💡 Suggestion: {smell.suggestion}")
                    if smell.code_snippet:
                        report.append(f"   Code:")
                        for line in smell.code_snippet.split('\n'):
                            report.append(f"      {line}")
        
        report.append("")
        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        report.append("1. Address high severity issues first (bugs, security)")
        report.append("2. Refactor medium severity issues (complexity, maintainability)")
        report.append("3. Fix low severity issues as time permits (style, documentation)")
        report.append("")
        
        return '\n'.join(report)
    
    def _generate_html_report(self) -> str:
        """Generate an HTML report."""
        # Group by severity
        by_severity = defaultdict(list)
        for smell in self.smells:
            by_severity[smell.severity].append(smell)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Smell Detection Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0;
            font-size: 2em;
        }}
        .high {{ background: #ffebee; color: #c62828; }}
        .medium {{ background: #fff3e0; color: #ef6c00; }}
        .low {{ background: #e3f2fd; color: #1565c0; }}
        .smell {{
            border-left: 4px solid #ccc;
            padding: 15px;
            margin: 15px 0;
            background: #fafafa;
            border-radius: 4px;
        }}
        .smell.high {{ border-left-color: #c62828; }}
        .smell.medium {{ border-left-color: #ef6c00; }}
        .smell.low {{ border-left-color: #1565c0; }}
        .smell-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .location {{
            font-family: 'Courier New', monospace;
            background: #e0e0e0;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .category {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            background: #e0e0e0;
            color: #555;
        }}
        .message {{
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}
        .suggestion {{
            color: #666;
            font-style: italic;
            padding: 10px;
            background: #f0f7ff;
            border-radius: 4px;
            margin: 10px 0;
        }}
        pre {{
            background: #263238;
            color: #aed581;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Code Smell Detection Report</h1>
        
        <div class="summary">
            <div class="summary-card high">
                <h3>{len(by_severity['high'])}</h3>
                <p>High Severity</p>
            </div>
            <div class="summary-card medium">
                <h3>{len(by_severity['medium'])}</h3>
                <p>Medium Severity</p>
            </div>
            <div class="summary-card low">
                <h3>{len(by_severity['low'])}</h3>
                <p>Low Severity</p>
            </div>
        </div>
        
        <h2>Detected Issues</h2>
"""
        
        for severity in ['high', 'medium', 'low']:
            if severity in by_severity:
                html += f'<h3>{severity.upper()} Severity Issues</h3>\n'
                for smell in by_severity[severity]:
                    html += f"""
        <div class="smell {severity}">
            <div class="smell-header">
                <span class="location">{smell.file}:{smell.line}:{smell.column}</span>
                <span class="category">{smell.category}</span>
            </div>
            <div class="message">{smell.message}</div>
            <div class="suggestion">💡 {smell.suggestion}</div>
"""
                    if smell.code_snippet:
                        html += f'<pre>{smell.code_snippet}</pre>\n'
                    html += '        </div>\n'
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected smells."""
        by_category = defaultdict(int)
        by_severity = defaultdict(int)
        by_file = defaultdict(int)
        
        for smell in self.smells:
            by_category[smell.category] += 1
            by_severity[smell.severity] += 1
            by_file[smell.file] += 1
        
        return {
            'total_smells': len(self.smells),
            'by_category': dict(by_category),
            'by_severity': dict(by_severity),
            'by_file': dict(by_file),
            'files_analyzed': len(by_file)
        }


def main():
    """CLI entry point for code smell detector."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect code smells in Python code')
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'html'], default='text',
                        help='Report format (default: text)')
    parser.add_argument('--max-function-length', type=int, default=50,
                        help='Maximum function length (default: 50)')
    parser.add_argument('--max-parameters', type=int, default=5,
                        help='Maximum function parameters (default: 5)')
    parser.add_argument('--max-nesting', type=int, default=4,
                        help='Maximum nesting depth (default: 4)')
    
    args = parser.parse_args()
    
    detector = CodeSmellDetector(
        max_function_length=args.max_function_length,
        max_parameters=args.max_parameters,
        max_nesting=args.max_nesting
    )
    
    print(f"🔍 Analyzing {args.path} for code smells...")
    
    if os.path.isfile(args.path):
        smells = detector.analyze_file(args.path)
    else:
        smells = detector.analyze_directory(args.path)
    
    report = detector.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"✅ Report saved to {args.output}")
    else:
        print(report)
    
    # Return exit code based on high severity issues
    high_severity = sum(1 for s in smells if s.severity == 'high')
    return 1 if high_severity > 0 else 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
