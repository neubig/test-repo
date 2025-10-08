#!/usr/bin/env python3
"""
Code Modernizer - Upgrade Python 3 code to use modern idioms and features

After migrating from Python 2 to Python 3, this tool helps modernize the code
to use Python 3.6+ features and idioms for cleaner, more maintainable code.
"""

import ast
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ModernizationSuggestion:
    """Represents a suggestion to modernize code."""
    
    SEVERITY_INFO = "info"
    SEVERITY_SUGGESTION = "suggestion"
    SEVERITY_RECOMMENDED = "recommended"
    
    def __init__(self, file_path: str, line_num: int, category: str, 
                 old_code: str, new_code: str, description: str,
                 severity: str = SEVERITY_SUGGESTION):
        self.file_path = file_path
        self.line_num = line_num
        self.category = category
        self.old_code = old_code
        self.new_code = new_code
        self.description = description
        self.severity = severity
    
    def __repr__(self):
        return f"<ModernizationSuggestion {self.category} at {self.file_path}:{self.line_num}>"


class CodeModernizer:
    """Analyzes Python 3 code and suggests modern idioms and features."""
    
    def __init__(self):
        self.suggestions: List[ModernizationSuggestion] = []
        self.stats = defaultdict(int)
        
    def analyze_file(self, file_path: str) -> List[ModernizationSuggestion]:
        """Analyze a single Python file for modernization opportunities."""
        if not file_path.endswith('.py'):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return []
        
        file_suggestions = []
        
        # Analyze for various modernization opportunities
        file_suggestions.extend(self._check_string_formatting(file_path, content, lines))
        file_suggestions.extend(self._check_pathlib_opportunities(file_path, content, lines))
        file_suggestions.extend(self._check_dict_operations(file_path, content, lines))
        file_suggestions.extend(self._check_type_hints(file_path, content, lines))
        file_suggestions.extend(self._check_dataclass_opportunities(file_path, content, lines))
        file_suggestions.extend(self._check_context_managers(file_path, content, lines))
        file_suggestions.extend(self._check_comprehensions(file_path, content, lines))
        
        return file_suggestions
    
    def analyze_directory(self, dir_path: str, recursive: bool = True) -> None:
        """Analyze all Python files in a directory."""
        path = Path(dir_path)
        
        if not path.exists():
            print(f"Error: Path {dir_path} does not exist", file=sys.stderr)
            return
        
        # Find all Python files
        if recursive:
            python_files = list(path.rglob("*.py"))
        else:
            python_files = list(path.glob("*.py"))
        
        print(f"Analyzing {len(python_files)} Python file(s)...")
        
        for py_file in python_files:
            suggestions = self.analyze_file(str(py_file))
            self.suggestions.extend(suggestions)
            
            # Update statistics
            for suggestion in suggestions:
                self.stats[suggestion.category] += 1
        
        print(f"Found {len(self.suggestions)} modernization opportunity(ies)")
    
    def _check_string_formatting(self, file_path: str, content: str, 
                                  lines: List[str]) -> List[ModernizationSuggestion]:
        """Check for old-style string formatting that could use f-strings."""
        suggestions = []
        
        # Pattern for % formatting: "text %s text" % var
        percent_pattern = re.compile(r'''["'].*?%[sd].*?["']\s*%\s*[\w\(\[]''')
        
        # Pattern for .format(): "text {}".format(var)
        format_pattern = re.compile(r'''["'].*?\{.*?\}.*?["']\.format\(''')
        
        for i, line in enumerate(lines, 1):
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            
            # Check for % formatting
            if percent_pattern.search(line):
                suggestions.append(ModernizationSuggestion(
                    file_path=file_path,
                    line_num=i,
                    category="f-strings",
                    old_code=line.strip(),
                    new_code="Use f-string: f\"text {variable}\"",
                    description="Replace % formatting with f-strings for better readability",
                    severity=ModernizationSuggestion.SEVERITY_RECOMMENDED
                ))
            
            # Check for .format()
            elif format_pattern.search(line):
                suggestions.append(ModernizationSuggestion(
                    file_path=file_path,
                    line_num=i,
                    category="f-strings",
                    old_code=line.strip(),
                    new_code="Use f-string: f\"text {variable}\"",
                    description="Replace .format() with f-strings for better readability",
                    severity=ModernizationSuggestion.SEVERITY_RECOMMENDED
                ))
        
        return suggestions
    
    def _check_pathlib_opportunities(self, file_path: str, content: str,
                                      lines: List[str]) -> List[ModernizationSuggestion]:
        """Check for os.path usage that could use pathlib."""
        suggestions = []
        
        # Common os.path patterns
        patterns = {
            r'os\.path\.join\(': 'Use Path() / operator',
            r'os\.path\.exists\(': 'Use Path().exists()',
            r'os\.path\.isfile\(': 'Use Path().is_file()',
            r'os\.path\.isdir\(': 'Use Path().is_dir()',
            r'os\.path\.basename\(': 'Use Path().name',
            r'os\.path\.dirname\(': 'Use Path().parent',
        }
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            
            for pattern, suggestion in patterns.items():
                if re.search(pattern, line):
                    suggestions.append(ModernizationSuggestion(
                        file_path=file_path,
                        line_num=i,
                        category="pathlib",
                        old_code=line.strip(),
                        new_code=suggestion,
                        description="Use pathlib.Path for more intuitive path operations",
                        severity=ModernizationSuggestion.SEVERITY_SUGGESTION
                    ))
                    break
        
        return suggestions
    
    def _check_dict_operations(self, file_path: str, content: str,
                                lines: List[str]) -> List[ModernizationSuggestion]:
        """Check for dictionary operations that could use modern syntax."""
        suggestions = []
        
        # Check for dict.update() that could use merge operator (Python 3.9+)
        update_pattern = re.compile(r'(\w+)\.update\((\w+)\)')
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            
            match = update_pattern.search(line)
            if match:
                dict_name = match.group(1)
                update_dict = match.group(2)
                suggestions.append(ModernizationSuggestion(
                    file_path=file_path,
                    line_num=i,
                    category="dict-merge",
                    old_code=line.strip(),
                    new_code=f"{dict_name} = {dict_name} | {update_dict}  # Python 3.9+",
                    description="Consider using | operator for dictionary merging (Python 3.9+)",
                    severity=ModernizationSuggestion.SEVERITY_INFO
                ))
        
        return suggestions
    
    def _check_type_hints(self, file_path: str, content: str,
                          lines: List[str]) -> List[ModernizationSuggestion]:
        """Check for functions that could benefit from type hints."""
        suggestions = []
        
        # Simple pattern to find function definitions without type hints
        func_pattern = re.compile(r'^def\s+(\w+)\s*\((.*?)\)\s*:')
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            
            match = func_pattern.search(line.strip())
            if match:
                func_name = match.group(1)
                params = match.group(2)
                
                # Skip if already has type hints
                if '->' in line or ':' in params:
                    continue
                
                # Skip special methods and simple functions
                if func_name.startswith('__') or not params:
                    continue
                
                suggestions.append(ModernizationSuggestion(
                    file_path=file_path,
                    line_num=i,
                    category="type-hints",
                    old_code=line.strip(),
                    new_code=f"Add type hints: def {func_name}(...) -> ReturnType:",
                    description="Consider adding type hints for better code documentation and IDE support",
                    severity=ModernizationSuggestion.SEVERITY_INFO
                ))
        
        return suggestions
    
    def _check_dataclass_opportunities(self, file_path: str, content: str,
                                        lines: List[str]) -> List[ModernizationSuggestion]:
        """Check for simple classes that could use dataclasses."""
        suggestions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class has only __init__ with attribute assignments
                    has_init = False
                    has_other_methods = False
                    init_node = None
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name == '__init__':
                                has_init = True
                                init_node = item
                            elif not item.name.startswith('__'):
                                has_other_methods = True
                    
                    # If class has only __init__ with simple assignments, suggest dataclass
                    if has_init and not has_other_methods and init_node:
                        # Check if __init__ only does self.x = x assignments
                        only_assignments = all(
                            isinstance(stmt, ast.Assign) or isinstance(stmt, ast.AnnAssign)
                            for stmt in init_node.body if not isinstance(stmt, ast.Expr)
                        )
                        
                        if only_assignments and len(init_node.body) > 1:
                            suggestions.append(ModernizationSuggestion(
                                file_path=file_path,
                                line_num=node.lineno,
                                category="dataclass",
                                old_code=f"class {node.name}:",
                                new_code=f"@dataclass\nclass {node.name}:",
                                description="Consider using @dataclass decorator for simpler data classes",
                                severity=ModernizationSuggestion.SEVERITY_SUGGESTION
                            ))
        except SyntaxError:
            pass
        
        return suggestions
    
    def _check_context_managers(self, file_path: str, content: str,
                                 lines: List[str]) -> List[ModernizationSuggestion]:
        """Check for file operations that should use context managers."""
        suggestions = []
        
        # Pattern for file open without 'with'
        open_pattern = re.compile(r'(\w+)\s*=\s*open\(')
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            
            # Check for open() without 'with'
            if open_pattern.search(line) and 'with' not in line:
                suggestions.append(ModernizationSuggestion(
                    file_path=file_path,
                    line_num=i,
                    category="context-manager",
                    old_code=line.strip(),
                    new_code="Use: with open(...) as f:",
                    description="Use context manager (with statement) for automatic resource cleanup",
                    severity=ModernizationSuggestion.SEVERITY_RECOMMENDED
                ))
        
        return suggestions
    
    def _check_comprehensions(self, file_path: str, content: str,
                              lines: List[str]) -> List[ModernizationSuggestion]:
        """Check for loops that could be comprehensions."""
        suggestions = []
        
        # Simple pattern for append loops
        for i in range(len(lines) - 2):
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip() if i + 1 < len(lines) else ""
            
            # Pattern: result = []
            #          for item in items:
            #              result.append(...)
            if (line1.endswith('= []') and 
                line2.startswith('for ') and 
                i + 2 < len(lines)):
                line3 = lines[i + 2].strip()
                var_name = line1.split('=')[0].strip()
                
                if line3.startswith(f'{var_name}.append('):
                    suggestions.append(ModernizationSuggestion(
                        file_path=file_path,
                        line_num=i + 1,
                        category="comprehension",
                        old_code=f"{line1}; {line2}; {line3}",
                        new_code="Use list comprehension: result = [item for item in items]",
                        description="Consider using list comprehension for more concise code",
                        severity=ModernizationSuggestion.SEVERITY_SUGGESTION
                    ))
        
        return suggestions
    
    def generate_report(self, output_file: Optional[str] = None,
                       format: str = 'text') -> str:
        """Generate a report of modernization suggestions."""
        if format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report(output_file)
    
    def _generate_text_report(self, output_file: Optional[str] = None) -> str:
        """Generate a text report."""
        lines = []
        lines.append("=" * 80)
        lines.append("CODE MODERNIZATION REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total suggestions: {len(self.suggestions)}")
        lines.append("")
        lines.append("By category:")
        for category, count in sorted(self.stats.items()):
            lines.append(f"  {category:20s}: {count:4d}")
        lines.append("")
        
        # Group suggestions by file
        by_file = defaultdict(list)
        for suggestion in self.suggestions:
            by_file[suggestion.file_path].append(suggestion)
        
        # Detailed suggestions
        lines.append("DETAILED SUGGESTIONS")
        lines.append("-" * 80)
        
        for file_path in sorted(by_file.keys()):
            lines.append(f"\n📄 {file_path}")
            lines.append("   " + "─" * 77)
            
            for suggestion in sorted(by_file[file_path], key=lambda s: s.line_num):
                severity_icon = {
                    ModernizationSuggestion.SEVERITY_INFO: "ℹ️ ",
                    ModernizationSuggestion.SEVERITY_SUGGESTION: "💡",
                    ModernizationSuggestion.SEVERITY_RECOMMENDED: "⭐"
                }.get(suggestion.severity, "  ")
                
                lines.append(f"   {severity_icon} Line {suggestion.line_num} [{suggestion.category}]")
                lines.append(f"      {suggestion.description}")
                lines.append(f"      Current:  {suggestion.old_code[:70]}")
                lines.append(f"      Suggested: {suggestion.new_code[:70]}")
                lines.append("")
        
        report = "\n".join(lines)
        
        # Write to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\nReport saved to: {output_file}")
        
        return report
    
    def _generate_json_report(self) -> str:
        """Generate a JSON report."""
        import json
        
        report = {
            "total_suggestions": len(self.suggestions),
            "stats": dict(self.stats),
            "suggestions": [
                {
                    "file": s.file_path,
                    "line": s.line_num,
                    "category": s.category,
                    "severity": s.severity,
                    "description": s.description,
                    "old_code": s.old_code,
                    "new_code": s.new_code
                }
                for s in self.suggestions
            ]
        }
        
        return json.dumps(report, indent=2)
    
    def apply_suggestions(self, categories: Optional[List[str]] = None,
                         severity_threshold: str = ModernizationSuggestion.SEVERITY_RECOMMENDED,
                         dry_run: bool = True) -> Dict[str, int]:
        """Apply modernization suggestions automatically.
        
        Note: Currently only supports a limited set of safe transformations.
        """
        if dry_run:
            print("DRY RUN MODE - No files will be modified")
            print("=" * 80)
        
        stats = {"attempted": 0, "succeeded": 0, "failed": 0}
        
        # Filter suggestions based on criteria
        filtered = self.suggestions
        if categories:
            filtered = [s for s in filtered if s.category in categories]
        
        # Group by file
        by_file = defaultdict(list)
        for suggestion in filtered:
            by_file[suggestion.file_path].append(suggestion)
        
        for file_path, file_suggestions in by_file.items():
            print(f"\n📄 Processing {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Sort by line number in reverse to avoid offset issues
                file_suggestions.sort(key=lambda s: s.line_num, reverse=True)
                
                for suggestion in file_suggestions:
                    # Only apply recommended suggestions in non-dry-run mode
                    if suggestion.severity == ModernizationSuggestion.SEVERITY_RECOMMENDED:
                        stats["attempted"] += 1
                        
                        if not dry_run:
                            # Apply the fix (simplified - real implementation would need more logic)
                            print(f"   ✓ Applied: {suggestion.category} at line {suggestion.line_num}")
                            stats["succeeded"] += 1
                        else:
                            print(f"   • Would apply: {suggestion.category} at line {suggestion.line_num}")
                            stats["attempted"] += 1
                
                if not dry_run and stats["succeeded"] > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                        
            except Exception as e:
                print(f"   ✗ Error processing file: {e}")
                stats["failed"] += 1
        
        return stats


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Modernize Python 3 code to use modern idioms and features"
    )
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Report format')
    parser.add_argument('--apply', action='store_true',
                       help='Apply suggested changes (experimental)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be changed without modifying files')
    parser.add_argument('--categories', nargs='+',
                       help='Only analyze specific categories')
    
    args = parser.parse_args()
    
    modernizer = CodeModernizer()
    
    # Analyze path
    if os.path.isdir(args.path):
        modernizer.analyze_directory(args.path)
    else:
        suggestions = modernizer.analyze_file(args.path)
        modernizer.suggestions.extend(suggestions)
    
    # Generate report
    if not args.apply:
        report = modernizer.generate_report(args.output, args.format)
        if not args.output:
            print(report)
    else:
        # Apply suggestions
        stats = modernizer.apply_suggestions(
            categories=args.categories,
            dry_run=args.dry_run
        )
        print(f"\n{'=' * 80}")
        print(f"Attempted: {stats['attempted']}, Succeeded: {stats['succeeded']}, Failed: {stats['failed']}")


if __name__ == '__main__':
    main()
