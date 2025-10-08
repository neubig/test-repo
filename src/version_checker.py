#!/usr/bin/env python3
"""
Python Version Compatibility Checker

Analyzes Python 3 code to determine version compatibility and minimum requirements.
Helps teams decide which Python 3.x version to target after migration.
"""

import ast
import os
import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional


class VersionChecker:
    """Checks Python code for version-specific features and compatibility."""
    
    # Features and their minimum Python version requirements
    FEATURE_REQUIREMENTS = {
        # Python 3.5+
        'async_def': ('3.5', 'Async/await syntax (async def, await)'),
        'await': ('3.5', 'Async/await expressions'),
        'async_for': ('3.5', 'Async for loops'),
        'async_with': ('3.5', 'Async context managers'),
        'matrix_multiply': ('3.5', 'Matrix multiplication operator (@)'),
        'unpacking_generalizations': ('3.5', 'Extended unpacking generalizations'),
        
        # Python 3.6+
        'f_strings': ('3.6', 'f-string literals (formatted string literals)'),
        'variable_annotations': ('3.6', 'Variable annotations (PEP 526)'),
        'async_generators': ('3.6', 'Async generators'),
        'async_comprehensions': ('3.6', 'Async comprehensions'),
        'underscores_in_numeric_literals': ('3.6', 'Underscores in numeric literals'),
        
        # Python 3.7+
        'dataclasses': ('3.7', 'Dataclasses (@dataclass decorator)'),
        'postponed_annotations': ('3.7', 'Postponed evaluation of annotations'),
        'breakpoint': ('3.7', 'Built-in breakpoint() function'),
        
        # Python 3.8+
        'walrus_operator': ('3.8', 'Walrus operator (:=) - assignment expressions'),
        'positional_only_params': ('3.8', 'Positional-only parameters (/)'),
        'f_string_equals': ('3.8', 'f-string = specifier for self-documenting expressions'),
        
        # Python 3.9+
        'union_type_operator': ('3.9', 'Union type operator (|) for type hints'),
        'dict_merge_operator': ('3.9', 'Dict merge (|) and update (|=) operators'),
        'string_methods_removeprefix_removesuffix': ('3.9', 'str.removeprefix() and str.removesuffix()'),
        'type_hint_generics': ('3.9', 'Generic type hints using built-in collections'),
        
        # Python 3.10+
        'match_statement': ('3.10', 'Structural pattern matching (match/case)'),
        'parenthesized_context_managers': ('3.10', 'Parenthesized context managers'),
        'union_type_operator_isinstance': ('3.10', 'Union types with isinstance()'),
        
        # Python 3.11+
        'exception_groups': ('3.11', 'Exception groups and except*'),
        'task_groups': ('3.11', 'Task groups (asyncio)'),
        'tomllib': ('3.11', 'tomllib module in standard library'),
        
        # Python 3.12+
        'type_parameter_syntax': ('3.12', 'Type parameter syntax (PEP 695)'),
        'override_decorator': ('3.12', '@override decorator'),
    }
    
    # Standard library modules and their version changes
    STDLIB_CHANGES = {
        # Removed in Python 3.x
        'asynchat': ('removed', '3.12', 'Removed in Python 3.12'),
        'asyncore': ('removed', '3.12', 'Removed in Python 3.12'),
        'distutils': ('removed', '3.12', 'Removed in Python 3.12'),
        'imp': ('removed', '3.12', 'Removed in Python 3.12, use importlib'),
        
        # Added in specific versions
        'dataclasses': ('added', '3.7', 'Added in Python 3.7'),
        'contextvars': ('added', '3.7', 'Added in Python 3.7'),
        'importlib.metadata': ('added', '3.8', 'Added in Python 3.8'),
        'importlib.resources': ('added', '3.7', 'Added in Python 3.7'),
        'graphlib': ('added', '3.9', 'Added in Python 3.9'),
        'zoneinfo': ('added', '3.9', 'Added in Python 3.9'),
        'tomllib': ('added', '3.11', 'Added in Python 3.11'),
    }
    
    def __init__(self):
        self.features_found: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.imports_found: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.min_version: Optional[str] = None
        self.analyzed_files: int = 0
        self.errors: List[Tuple[str, str]] = []
    
    def analyze_file(self, filepath: str) -> None:
        """Analyze a single Python file for version-specific features."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filepath)
            self.analyzed_files += 1
            
            # Check for various features
            self._check_f_strings(tree, filepath)
            self._check_walrus_operator(tree, filepath)
            self._check_match_statement(tree, filepath)
            self._check_async_features(tree, filepath)
            self._check_type_annotations(tree, filepath)
            self._check_imports(tree, filepath)
            self._check_operators(tree, filepath)
            self._check_function_signatures(tree, filepath)
            
        except SyntaxError as e:
            self.errors.append((filepath, f"Syntax error: {e}"))
        except Exception as e:
            self.errors.append((filepath, f"Error analyzing file: {e}"))
    
    def analyze_directory(self, dirpath: str) -> None:
        """Recursively analyze all Python files in a directory."""
        for root, dirs, files in os.walk(dirpath):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules', '.tox'}]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self.analyze_file(filepath)
    
    def _check_f_strings(self, tree: ast.AST, filepath: str) -> None:
        """Check for f-string usage (Python 3.6+)."""
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                self.features_found['f_strings'].append((filepath, node.lineno))
    
    def _check_walrus_operator(self, tree: ast.AST, filepath: str) -> None:
        """Check for walrus operator usage (Python 3.8+)."""
        for node in ast.walk(tree):
            if isinstance(node, ast.NamedExpr):
                self.features_found['walrus_operator'].append((filepath, node.lineno))
    
    def _check_match_statement(self, tree: ast.AST, filepath: str) -> None:
        """Check for match statement usage (Python 3.10+)."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Match):
                self.features_found['match_statement'].append((filepath, node.lineno))
    
    def _check_async_features(self, tree: ast.AST, filepath: str) -> None:
        """Check for async/await features."""
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                self.features_found['async_def'].append((filepath, node.lineno))
            elif isinstance(node, ast.Await):
                self.features_found['await'].append((filepath, node.lineno))
            elif isinstance(node, ast.AsyncFor):
                self.features_found['async_for'].append((filepath, node.lineno))
            elif isinstance(node, ast.AsyncWith):
                self.features_found['async_with'].append((filepath, node.lineno))
    
    def _check_type_annotations(self, tree: ast.AST, filepath: str) -> None:
        """Check for type annotation features."""
        for node in ast.walk(tree):
            # Variable annotations (3.6+)
            if isinstance(node, ast.AnnAssign):
                self.features_found['variable_annotations'].append((filepath, node.lineno))
            
            # Check for | in type hints (3.10+)
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                # This is a heuristic; could be regular bitwise OR or union types
                # In practice, union types in annotations are common enough to flag
                parent_is_annotation = False
                for parent in ast.walk(tree):
                    if isinstance(parent, (ast.AnnAssign, ast.FunctionDef, ast.AsyncFunctionDef)):
                        parent_is_annotation = True
                        break
                if parent_is_annotation:
                    self.features_found['union_type_operator'].append((filepath, node.lineno))
    
    def _check_imports(self, tree: ast.AST, filepath: str) -> None:
        """Check for version-specific imports."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in self.STDLIB_CHANGES:
                        self.imports_found[module_name].append((filepath, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    if module_name in self.STDLIB_CHANGES:
                        self.imports_found[module_name].append((filepath, node.lineno))
    
    def _check_operators(self, tree: ast.AST, filepath: str) -> None:
        """Check for version-specific operators."""
        for node in ast.walk(tree):
            # Matrix multiply operator @ (3.5+)
            if isinstance(node, ast.MatMult):
                self.features_found['matrix_multiply'].append((filepath, node.lineno))
            
            # Dict merge operator | (3.9+)
            # This is tricky as | can be used in multiple contexts
            # We'll check for it in specific contexts
    
    def _check_function_signatures(self, tree: ast.AST, filepath: str) -> None:
        """Check for positional-only parameters (3.8+)."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node.args, 'posonlyargs') and node.args.posonlyargs:
                    self.features_found['positional_only_params'].append((filepath, node.lineno))
    
    def get_minimum_version(self) -> str:
        """Determine the minimum Python version required."""
        if not self.features_found and not self.imports_found:
            return "3.0"
        
        max_version = "3.0"
        
        # Check features
        for feature in self.features_found:
            if feature in self.FEATURE_REQUIREMENTS:
                required_version = self.FEATURE_REQUIREMENTS[feature][0]
                if self._version_compare(required_version, max_version) > 0:
                    max_version = required_version
        
        # Check imports
        for module in self.imports_found:
            if module in self.STDLIB_CHANGES:
                change_type, version, _ = self.STDLIB_CHANGES[module]
                if change_type == 'added':
                    if self._version_compare(version, max_version) > 0:
                        max_version = version
                elif change_type == 'removed':
                    # This is a problem - using removed module
                    pass
        
        return max_version
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal."""
        parts1 = [int(x) for x in v1.split('.')]
        parts2 = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(parts1), len(parts2))):
            p1 = parts1[i] if i < len(parts1) else 0
            p2 = parts2[i] if i < len(parts2) else 0
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0
    
    def check_compatibility(self, target_version: str) -> Dict[str, List]:
        """Check if code is compatible with a target Python version."""
        incompatible = {}
        
        # Check features
        for feature, occurrences in self.features_found.items():
            if feature in self.FEATURE_REQUIREMENTS:
                required_version, description = self.FEATURE_REQUIREMENTS[feature]
                if self._version_compare(required_version, target_version) > 0:
                    incompatible[feature] = {
                        'required_version': required_version,
                        'description': description,
                        'occurrences': len(occurrences),
                        'locations': occurrences[:5]  # First 5 occurrences
                    }
        
        # Check imports
        for module, occurrences in self.imports_found.items():
            if module in self.STDLIB_CHANGES:
                change_type, version, description = self.STDLIB_CHANGES[module]
                if change_type == 'added':
                    if self._version_compare(version, target_version) > 0:
                        incompatible[f'import_{module}'] = {
                            'required_version': version,
                            'description': description,
                            'occurrences': len(occurrences),
                            'locations': occurrences[:5]
                        }
                elif change_type == 'removed':
                    if self._version_compare(target_version, version) >= 0:
                        incompatible[f'import_{module}'] = {
                            'required_version': f'<{version}',
                            'description': description,
                            'occurrences': len(occurrences),
                            'locations': occurrences[:5]
                        }
        
        return incompatible
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate a compatibility report."""
        min_version = self.get_minimum_version()
        
        if output_format == 'json':
            return self._generate_json_report(min_version)
        else:
            return self._generate_text_report(min_version)
    
    def _generate_text_report(self, min_version: str) -> str:
        """Generate a text-based report."""
        lines = []
        lines.append("=" * 80)
        lines.append("Python Version Compatibility Report".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        lines.append(f"Files analyzed: {self.analyzed_files}")
        lines.append(f"Minimum Python version required: {min_version}")
        lines.append("")
        
        if self.errors:
            lines.append(f"Errors encountered: {len(self.errors)}")
            for filepath, error in self.errors[:5]:
                lines.append(f"  - {filepath}: {error}")
            if len(self.errors) > 5:
                lines.append(f"  ... and {len(self.errors) - 5} more errors")
            lines.append("")
        
        if self.features_found:
            lines.append("Version-Specific Features Detected:")
            lines.append("-" * 80)
            
            # Group by version
            features_by_version = defaultdict(list)
            for feature, occurrences in self.features_found.items():
                if feature in self.FEATURE_REQUIREMENTS:
                    version, description = self.FEATURE_REQUIREMENTS[feature]
                    features_by_version[version].append((feature, description, len(occurrences)))
            
            for version in sorted(features_by_version.keys(), key=lambda v: [int(x) for x in v.split('.')]):
                lines.append(f"\nPython {version}+:")
                for feature, description, count in sorted(features_by_version[version]):
                    lines.append(f"  • {description}")
                    lines.append(f"    Found {count} occurrence(s)")
        
        if self.imports_found:
            lines.append("\n")
            lines.append("Version-Specific Standard Library Usage:")
            lines.append("-" * 80)
            
            for module, occurrences in sorted(self.imports_found.items()):
                if module in self.STDLIB_CHANGES:
                    change_type, version, description = self.STDLIB_CHANGES[module]
                    lines.append(f"\n  • {module}: {description}")
                    lines.append(f"    Found {len(occurrences)} occurrence(s)")
        
        lines.append("\n")
        lines.append("Compatibility Summary:")
        lines.append("-" * 80)
        
        test_versions = ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12']
        for version in test_versions:
            incompatible = self.check_compatibility(version)
            status = "✓ Compatible" if not incompatible else f"✗ {len(incompatible)} incompatibility(ies)"
            lines.append(f"  Python {version}: {status}")
        
        lines.append("\n")
        lines.append("Recommendations:")
        lines.append("-" * 80)
        lines.append(f"  • Target Python {min_version} or newer")
        
        if self._version_compare(min_version, '3.8') >= 0:
            lines.append(f"  • Consider Python 3.8+ as minimum for modern features")
        
        if self._version_compare(min_version, '3.9') < 0:
            lines.append(f"  • Your code is compatible with older Python 3.x versions")
            lines.append(f"  • Consider using newer features for better code quality")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_json_report(self, min_version: str) -> str:
        """Generate a JSON report."""
        report = {
            'summary': {
                'files_analyzed': self.analyzed_files,
                'minimum_version': min_version,
                'errors_count': len(self.errors)
            },
            'features': {},
            'imports': {},
            'compatibility': {},
            'errors': [{'file': f, 'error': e} for f, e in self.errors]
        }
        
        # Add features
        for feature, occurrences in self.features_found.items():
            if feature in self.FEATURE_REQUIREMENTS:
                version, description = self.FEATURE_REQUIREMENTS[feature]
                report['features'][feature] = {
                    'version': version,
                    'description': description,
                    'count': len(occurrences),
                    'locations': [{'file': f, 'line': l} for f, l in occurrences[:10]]
                }
        
        # Add imports
        for module, occurrences in self.imports_found.items():
            if module in self.STDLIB_CHANGES:
                change_type, version, description = self.STDLIB_CHANGES[module]
                report['imports'][module] = {
                    'change_type': change_type,
                    'version': version,
                    'description': description,
                    'count': len(occurrences),
                    'locations': [{'file': f, 'line': l} for f, l in occurrences[:10]]
                }
        
        # Add compatibility checks
        test_versions = ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12']
        for version in test_versions:
            incompatible = self.check_compatibility(version)
            report['compatibility'][version] = {
                'compatible': len(incompatible) == 0,
                'issues_count': len(incompatible),
                'issues': incompatible
            }
        
        return json.dumps(report, indent=2)


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Check Python version compatibility for migrated code',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('-t', '--target', help='Target Python version to check compatibility')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    checker = VersionChecker()
    
    print(f"Analyzing {args.path}...")
    if os.path.isfile(args.path):
        checker.analyze_file(args.path)
    else:
        checker.analyze_directory(args.path)
    
    report = checker.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")
    else:
        print(report)
    
    if args.target:
        print(f"\n\nChecking compatibility with Python {args.target}...")
        incompatible = checker.check_compatibility(args.target)
        if incompatible:
            print(f"Found {len(incompatible)} incompatibility(ies):")
            for issue, details in incompatible.items():
                print(f"  • {details['description']}")
                print(f"    Requires: Python {details['required_version']}")
        else:
            print(f"✓ Code is compatible with Python {args.target}")


if __name__ == '__main__':
    main()
