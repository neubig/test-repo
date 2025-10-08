#!/usr/bin/env python3
"""
Type Hints Generator for Python 3

Automatically adds type hints to Python 3 code by analyzing function signatures,
return statements, default values, and usage patterns. Perfect for modernizing
code after Python 2 to 3 migration.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import json


class TypeInferenceVisitor(ast.NodeVisitor):
    """AST visitor that infers types from code patterns."""
    
    def __init__(self):
        self.function_info = {}
        self.current_function = None
        self.imports = set()
        self.typing_imports = set()
        
    def visit_Import(self, node):
        """Track imports."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Track from imports."""
        if node.module:
            self.imports.add(node.module)
            if node.module == 'typing':
                for alias in node.names:
                    self.typing_imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Analyze function definitions."""
        self.current_function = node.name
        
        info = {
            'name': node.name,
            'params': {},
            'return_type': None,
            'has_return_annotation': node.returns is not None,
            'return_values': [],
            'docstring': ast.get_docstring(node)
        }
        
        # Analyze parameters
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'annotation': arg.annotation,
                'inferred_type': None
            }
            info['params'][arg.arg] = param_info
        
        # Check for default values
        defaults = node.args.defaults
        if defaults:
            # Map defaults to their corresponding parameters
            num_params = len(node.args.args)
            num_defaults = len(defaults)
            default_offset = num_params - num_defaults
            
            for i, default in enumerate(defaults):
                param_idx = default_offset + i
                if param_idx < len(node.args.args):
                    param_name = node.args.args[param_idx].arg
                    default_type = self._infer_type_from_value(default)
                    if default_type:
                        info['params'][param_name]['inferred_type'] = default_type
        
        self.function_info[node.name] = info
        
        # Visit function body to analyze return statements
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                return_type = self._infer_type_from_value(child.value)
                if return_type:
                    info['return_values'].append(return_type)
        
        # Infer final return type
        if info['return_values']:
            info['return_type'] = self._consolidate_types(info['return_values'])
        elif not any(isinstance(n, ast.Return) for n in ast.walk(node) if isinstance(n, ast.Return) and n.value):
            # Function has no return statement or returns None
            info['return_type'] = 'None'
        
        self.current_function = None
        self.generic_visit(node)
    
    def _infer_type_from_value(self, node):
        """Infer type from an AST value node."""
        if isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, bool):
                return 'bool'
            elif isinstance(value, int):
                return 'int'
            elif isinstance(value, float):
                return 'float'
            elif isinstance(value, str):
                return 'str'
            elif isinstance(value, bytes):
                return 'bytes'
            elif value is None:
                return 'None'
        elif isinstance(node, ast.List):
            if node.elts:
                elem_types = [self._infer_type_from_value(e) for e in node.elts[:3]]
                elem_types = [t for t in elem_types if t]
                if elem_types:
                    elem_type = self._consolidate_types(elem_types)
                    return f'List[{elem_type}]'
            return 'List'
        elif isinstance(node, ast.Dict):
            if node.keys and node.values:
                key_types = [self._infer_type_from_value(k) for k in node.keys[:3] if k]
                val_types = [self._infer_type_from_value(v) for v in node.values[:3]]
                key_types = [t for t in key_types if t]
                val_types = [t for t in val_types if t]
                if key_types and val_types:
                    key_type = self._consolidate_types(key_types)
                    val_type = self._consolidate_types(val_types)
                    return f'Dict[{key_type}, {val_type}]'
            return 'Dict'
        elif isinstance(node, ast.Set):
            if node.elts:
                elem_types = [self._infer_type_from_value(e) for e in node.elts[:3]]
                elem_types = [t for t in elem_types if t]
                if elem_types:
                    elem_type = self._consolidate_types(elem_types)
                    return f'Set[{elem_type}]'
            return 'Set'
        elif isinstance(node, ast.Tuple):
            if node.elts:
                elem_types = [self._infer_type_from_value(e) for e in node.elts]
                elem_types = [t for t in elem_types if t]
                if elem_types and len(elem_types) <= 5:
                    return f'Tuple[{", ".join(elem_types)}]'
                elif elem_types:
                    elem_type = self._consolidate_types(elem_types)
                    return f'Tuple[{elem_type}, ...]'
            return 'Tuple'
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                type_map = {
                    'str': 'str', 'int': 'int', 'float': 'float',
                    'bool': 'bool', 'list': 'List', 'dict': 'Dict',
                    'set': 'Set', 'tuple': 'Tuple'
                }
                return type_map.get(func_name)
        
        return None
    
    def _consolidate_types(self, types):
        """Consolidate multiple types into a single type hint."""
        if not types:
            return 'Any'
        
        # Remove None and handle Optional
        non_none_types = [t for t in types if t != 'None']
        has_none = 'None' in types
        
        if not non_none_types:
            return 'None'
        
        # Get unique types
        unique_types = list(set(non_none_types))
        
        if len(unique_types) == 1:
            base_type = unique_types[0]
            if has_none:
                return f'Optional[{base_type}]'
            return base_type
        else:
            union_type = f'Union[{", ".join(sorted(unique_types))}]'
            if has_none:
                return f'Optional[{union_type}]'
            return union_type


class TypeHintsGenerator:
    """Generate type hints for Python code."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.changes_made = []
        self.stats = {
            'files_processed': 0,
            'functions_annotated': 0,
            'parameters_annotated': 0,
            'returns_annotated': 0,
            'imports_added': 0
        }
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single Python file and add type hints.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with processing results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Parse the AST
            try:
                tree = ast.parse(original_content)
            except SyntaxError as e:
                return {
                    'success': False,
                    'error': f'Syntax error: {e}',
                    'file': file_path
                }
            
            # Analyze the code
            visitor = TypeInferenceVisitor()
            visitor.visit(tree)
            
            # Generate new content with type hints
            new_content, changes = self._add_type_hints(
                original_content, visitor.function_info, visitor.typing_imports
            )
            
            # Check if changes were made
            if new_content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                
                self.stats['files_processed'] += 1
                self.changes_made.extend(changes)
                
                return {
                    'success': True,
                    'file': file_path,
                    'changes': changes,
                    'modified': True
                }
            else:
                return {
                    'success': True,
                    'file': file_path,
                    'changes': [],
                    'modified': False
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file': file_path
            }
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Process all Python files in a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            List of processing results
        """
        results = []
        directory_path = Path(directory_path)
        
        for root, dirs, files in os.walk(directory_path):
            # Skip hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    result = self.process_file(file_path)
                    results.append(result)
        
        return results
    
    def _add_type_hints(self, content: str, function_info: Dict, existing_typing_imports: Set) -> Tuple[str, List[Dict]]:
        """Add type hints to the content.
        
        Args:
            content: Original file content
            function_info: Function information from TypeInferenceVisitor
            existing_typing_imports: Existing typing imports
            
        Returns:
            Tuple of (modified content, list of changes)
        """
        lines = content.split('\n')
        changes = []
        needed_typing_imports = set()
        
        # Parse the content again to get line numbers
        try:
            tree = ast.parse(content)
        except:
            return content, []
        
        # Collect all needed typing imports
        for func_name, info in function_info.items():
            # Check parameters
            for param_name, param_info in info['params'].items():
                if param_info['annotation'] is None and param_info['inferred_type']:
                    type_hint = param_info['inferred_type']
                    needed_typing_imports.update(self._extract_typing_imports(type_hint))
            
            # Check return type
            if not info['has_return_annotation'] and info['return_type']:
                needed_typing_imports.update(self._extract_typing_imports(info['return_type']))
        
        # Add typing imports if needed
        new_imports = needed_typing_imports - existing_typing_imports
        if new_imports and ('typing' not in content or 'from typing import' not in content):
            # Find the best place to add the import (after shebang, encoding, docstrings, and other imports)
            import_line = 0
            in_docstring = False
            docstring_char = None
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Skip shebang and encoding lines
                if i == 0 and stripped.startswith('#!'):
                    import_line = i + 1
                    continue
                if stripped.startswith('#') and ('coding' in stripped or 'encoding' in stripped):
                    import_line = i + 1
                    continue
                
                # Track docstrings
                if not in_docstring:
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        docstring_char = stripped[:3]
                        if stripped.count(docstring_char) == 1:
                            in_docstring = True
                            import_line = i + 1
                        else:
                            import_line = i + 1
                        continue
                else:
                    if docstring_char in stripped:
                        in_docstring = False
                        import_line = i + 1
                        continue
                
                # After imports
                if stripped.startswith(('import ', 'from ')) and 'future' not in line:
                    import_line = i + 1
                    continue
                
                # Stop at first non-import, non-comment line
                if stripped and not stripped.startswith('#') and not in_docstring:
                    break
            
            if new_imports:
                import_statement = f"from typing import {', '.join(sorted(new_imports))}"
                lines.insert(import_line, import_statement)
                changes.append({
                    'type': 'import_added',
                    'line': import_line,
                    'imports': list(new_imports)
                })
                self.stats['imports_added'] += 1
        
        # Add type hints to functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                if func_name in function_info:
                    info = function_info[func_name]
                    func_line = node.lineno - 1  # Convert to 0-indexed
                    
                    # Adjust for any inserted import lines
                    if new_imports:
                        func_line += 1
                    
                    # Build new function signature
                    original_line = lines[func_line]
                    new_line = self._add_annotations_to_function(
                        original_line, node, info
                    )
                    
                    if new_line != original_line:
                        lines[func_line] = new_line
                        func_changes = {
                            'type': 'function_annotated',
                            'function': func_name,
                            'line': func_line + 1,
                            'original': original_line.strip(),
                            'modified': new_line.strip()
                        }
                        changes.append(func_changes)
                        self.stats['functions_annotated'] += 1
                        
                        # Count parameter and return annotations
                        for param_info in info['params'].values():
                            if param_info['annotation'] is None and param_info['inferred_type']:
                                self.stats['parameters_annotated'] += 1
                        
                        if not info['has_return_annotation'] and info['return_type']:
                            self.stats['returns_annotated'] += 1
        
        return '\n'.join(lines), changes
    
    def _extract_typing_imports(self, type_str: str) -> Set[str]:
        """Extract typing module names from a type string."""
        typing_names = {'List', 'Dict', 'Set', 'Tuple', 'Optional', 'Union', 'Any', 'Callable'}
        found = set()
        for name in typing_names:
            if name in type_str:
                found.add(name)
        return found
    
    def _add_annotations_to_function(self, line: str, node: ast.FunctionDef, info: Dict) -> str:
        """Add type annotations to a function definition line."""
        # This is a simplified implementation that handles basic cases
        # For production use, consider using a proper code rewriting tool like libcst
        
        # Extract the function signature
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        
        # Build parameter list with annotations
        params = []
        for i, arg in enumerate(node.args.args):
            param_name = arg.arg
            if param_name in info['params']:
                param_info = info['params'][param_name]
                if param_info['annotation'] is None and param_info['inferred_type']:
                    # Add type hint
                    type_hint = param_info['inferred_type']
                    params.append(f"{param_name}: {type_hint}")
                else:
                    params.append(param_name)
            else:
                params.append(param_name)
        
        # Add return type annotation
        return_annotation = ''
        if not info['has_return_annotation'] and info['return_type']:
            return_annotation = f" -> {info['return_type']}"
        
        # Reconstruct the function definition
        params_str = ', '.join(params)
        new_line = f"{indent_str}def {info['name']}({params_str}){return_annotation}:"
        
        return new_line
    
    def generate_report(self, results: List[Dict], output_file: Optional[str] = None):
        """Generate a detailed report of changes made.
        
        Args:
            results: List of processing results
            output_file: Optional output file path
        """
        report_lines = [
            "=" * 70,
            "Type Hints Generation Report",
            "=" * 70,
            "",
            "Summary:",
            f"  Files processed: {self.stats['files_processed']}",
            f"  Functions annotated: {self.stats['functions_annotated']}",
            f"  Parameters annotated: {self.stats['parameters_annotated']}",
            f"  Returns annotated: {self.stats['returns_annotated']}",
            f"  Typing imports added: {self.stats['imports_added']}",
            "",
            "Mode: " + ("DRY RUN (no files modified)" if self.dry_run else "LIVE (files modified)"),
            "",
            "=" * 70,
            ""
        ]
        
        # Group results by success
        successful = [r for r in results if r.get('success', False) and r.get('modified', False)]
        failed = [r for r in results if not r.get('success', False)]
        unchanged = [r for r in results if r.get('success', False) and not r.get('modified', False)]
        
        if successful:
            report_lines.extend([
                f"Modified Files ({len(successful)}):",
                ""
            ])
            for result in successful:
                report_lines.append(f"  {result['file']}")
                for change in result.get('changes', []):
                    if change['type'] == 'import_added':
                        report_lines.append(f"    + Added typing imports: {', '.join(change['imports'])}")
                    elif change['type'] == 'function_annotated':
                        report_lines.append(f"    • {change['function']}()")
                        if change['original'] != change['modified']:
                            report_lines.append(f"      Before: {change['original']}")
                            report_lines.append(f"      After:  {change['modified']}")
                report_lines.append("")
        
        if unchanged:
            report_lines.extend([
                f"Unchanged Files ({len(unchanged)}):",
                "  (Already have type hints or no functions to annotate)",
                ""
            ])
            for result in unchanged[:10]:  # Show first 10
                report_lines.append(f"  {result['file']}")
            if len(unchanged) > 10:
                report_lines.append(f"  ... and {len(unchanged) - 10} more")
            report_lines.append("")
        
        if failed:
            report_lines.extend([
                f"Failed Files ({len(failed)}):",
                ""
            ])
            for result in failed:
                report_lines.append(f"  {result['file']}")
                report_lines.append(f"    Error: {result.get('error', 'Unknown error')}")
                report_lines.append("")
        
        report_lines.extend([
            "=" * 70,
            "Type Hints Generation Complete",
            "=" * 70
        ])
        
        report = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {output_file}")
        else:
            print(report)
        
        return report
    
    def generate_json_report(self, results: List[Dict], output_file: str):
        """Generate a JSON report of changes.
        
        Args:
            results: List of processing results
            output_file: Output file path
        """
        report = {
            'stats': self.stats,
            'dry_run': self.dry_run,
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"JSON report saved to: {output_file}")


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate type hints for Python 3 code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add type hints to a single file
  python type_hints_generator.py myfile.py

  # Add type hints to a directory
  python type_hints_generator.py src/

  # Dry run to preview changes
  python type_hints_generator.py src/ --dry-run

  # Save report to file
  python type_hints_generator.py src/ --report type_hints_report.txt

  # Generate JSON report
  python type_hints_generator.py src/ --json report.json
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to Python file or directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--report',
        help='Save detailed report to file'
    )
    parser.add_argument(
        '--json',
        help='Save JSON report to file'
    )
    
    args = parser.parse_args()
    
    # Validate path
    if not os.path.exists(args.path):
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Create generator
    generator = TypeHintsGenerator(dry_run=args.dry_run)
    
    # Process path
    if os.path.isfile(args.path):
        results = [generator.process_file(args.path)]
    else:
        results = generator.process_directory(args.path)
    
    # Generate reports
    generator.generate_report(results, args.report)
    
    if args.json:
        generator.generate_json_report(results, args.json)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
