#!/usr/bin/env python3
"""
Automated Test Generator for Migrated Code

Generates unit tests for Python code that has been migrated from Python 2 to Python 3.
Helps ensure that migration preserves functionality and catches runtime issues.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


class TestGenerator:
    """Generate unit tests for migrated Python code."""
    
    def __init__(self, target_path: str, output_dir: str = 'generated_tests'):
        """Initialize the test generator.
        
        Args:
            target_path: Path to the Python file or directory to generate tests for
            output_dir: Directory where generated tests will be saved
        """
        self.target_path = Path(target_path)
        self.output_dir = Path(output_dir)
        self.tests_generated = []
        
    def generate_tests(self, overwrite: bool = False) -> Dict[str, Any]:
        """Generate tests for the target path.
        
        Args:
            overwrite: Whether to overwrite existing test files
            
        Returns:
            dict: Summary of test generation
        """
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create __init__.py in test directory
        init_file = self.output_dir / '__init__.py'
        if not init_file.exists():
            init_file.write_text('"""Generated tests for migrated code."""\n')
        
        if self.target_path.is_file():
            files_to_process = [self.target_path]
        else:
            files_to_process = list(self.target_path.rglob('*.py'))
            # Filter out test files and special files
            files_to_process = [
                f for f in files_to_process 
                if not f.name.startswith('test_') 
                and not f.name.startswith('_')
                and 'test' not in f.parts
            ]
        
        summary = {
            'files_processed': 0,
            'tests_generated': 0,
            'functions_tested': 0,
            'classes_tested': 0,
            'test_files_created': [],
            'skipped_files': []
        }
        
        for file_path in files_to_process:
            try:
                result = self._generate_test_for_file(file_path, overwrite)
                if result['generated']:
                    summary['files_processed'] += 1
                    summary['tests_generated'] += result['test_count']
                    summary['functions_tested'] += result['functions']
                    summary['classes_tested'] += result['classes']
                    summary['test_files_created'].append(str(result['output_file']))
                else:
                    summary['skipped_files'].append(str(file_path))
            except Exception as e:
                summary['skipped_files'].append(f"{file_path} (Error: {e})")
        
        return summary
    
    def _generate_test_for_file(self, file_path: Path, overwrite: bool) -> Dict[str, Any]:
        """Generate tests for a single Python file.
        
        Args:
            file_path: Path to Python file
            overwrite: Whether to overwrite existing test file
            
        Returns:
            dict: Generation result
        """
        # Read and parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {'generated': False, 'reason': 'syntax_error'}
        
        # Analyze the code
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        
        # Skip if no testable items found
        if not analyzer.functions and not analyzer.classes:
            return {'generated': False, 'reason': 'no_testable_items'}
        
        # Generate test file
        test_filename = f'test_{file_path.stem}.py'
        output_file = self.output_dir / test_filename
        
        if output_file.exists() and not overwrite:
            return {'generated': False, 'reason': 'file_exists'}
        
        # Create test content
        test_content = self._create_test_content(
            file_path, 
            analyzer.functions, 
            analyzer.classes,
            analyzer.imports
        )
        
        # Write test file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return {
            'generated': True,
            'output_file': output_file,
            'test_count': len(analyzer.functions) + len(analyzer.classes),
            'functions': len(analyzer.functions),
            'classes': len(analyzer.classes)
        }
    
    def _create_test_content(
        self, 
        source_file: Path, 
        functions: List[Dict], 
        classes: List[Dict],
        imports: List[str]
    ) -> str:
        """Create the content of a test file.
        
        Args:
            source_file: Path to source file being tested
            functions: List of function information
            classes: List of class information
            imports: List of import statements from source
            
        Returns:
            str: Test file content
        """
        lines = []
        
        # Header
        lines.append('"""')
        lines.append(f'Generated tests for {source_file.name}')
        lines.append('')
        lines.append('These tests were automatically generated to help verify')
        lines.append('that Python 2 to 3 migration preserved functionality.')
        lines.append('Please review and enhance these tests as needed.')
        lines.append('"""')
        lines.append('')
        
        # Imports
        lines.append('import pytest')
        lines.append('import sys')
        lines.append('from pathlib import Path')
        lines.append('')
        lines.append('# Add source directory to path')
        lines.append(f'sys.path.insert(0, str(Path(__file__).parent.parent / "{source_file.parent.name}"))')
        lines.append('')
        
        # Import the module being tested
        module_name = source_file.stem
        lines.append(f'import {module_name}')
        lines.append('')
        
        # Generate tests for functions
        if functions:
            lines.append('# ===== Function Tests =====')
            lines.append('')
            
            for func in functions:
                test_code = self._generate_function_test(func, module_name)
                lines.extend(test_code)
                lines.append('')
        
        # Generate tests for classes
        if classes:
            lines.append('# ===== Class Tests =====')
            lines.append('')
            
            for cls in classes:
                test_code = self._generate_class_test(cls, module_name)
                lines.extend(test_code)
                lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_function_test(self, func_info: Dict, module_name: str) -> List[str]:
        """Generate test code for a function.
        
        Args:
            func_info: Function information dictionary
            module_name: Name of the module
            
        Returns:
            list: Lines of test code
        """
        lines = []
        func_name = func_info['name']
        args = func_info['args']
        has_return = func_info['has_return']
        docstring = func_info['docstring']
        
        lines.append(f'def test_{func_name}():')
        lines.append(f'    """Test {module_name}.{func_name} function."""')
        
        if docstring:
            lines.append('    # Function docstring:')
            for doc_line in docstring.split('\n')[:3]:  # First 3 lines
                lines.append(f'    # {doc_line.strip()}')
        
        lines.append('')
        lines.append('    # TODO: Add appropriate test inputs')
        
        # Generate sample test based on argument types
        if not args or (len(args) == 1 and args[0] == 'self'):
            # No arguments
            if has_return:
                lines.append(f'    result = {module_name}.{func_name}()')
                lines.append('    assert result is not None  # TODO: Add specific assertion')
            else:
                lines.append(f'    {module_name}.{func_name}()')
                lines.append('    # TODO: Verify side effects')
        else:
            # Has arguments - filter out 'self'
            args_filtered = [arg for arg in args if arg != 'self']
            
            if args_filtered:
                lines.append('    # Sample test inputs - please customize')
                arg_assignments = []
                for arg in args_filtered:
                    arg_assignments.append(f'{arg}=None  # TODO: Provide appropriate value')
                
                if has_return:
                    lines.append(f'    result = {module_name}.{func_name}({", ".join(arg_assignments)})')
                    lines.append('    assert result is not None  # TODO: Add specific assertion')
                else:
                    lines.append(f'    {module_name}.{func_name}({", ".join(arg_assignments)})')
                    lines.append('    # TODO: Verify side effects or state changes')
        
        lines.append('')
        lines.append('    # TODO: Add more test cases:')
        lines.append('    #   - Edge cases (empty input, None values, etc.)')
        lines.append('    #   - Boundary conditions')
        lines.append('    #   - Error cases')
        
        return lines
    
    def _generate_class_test(self, class_info: Dict, module_name: str) -> List[str]:
        """Generate test code for a class.
        
        Args:
            class_info: Class information dictionary
            module_name: Name of the module
            
        Returns:
            list: Lines of test code
        """
        lines = []
        class_name = class_info['name']
        methods = class_info['methods']
        has_init = class_info['has_init']
        
        lines.append(f'class Test{class_name}:')
        lines.append(f'    """Test {module_name}.{class_name} class."""')
        lines.append('')
        
        # Test instantiation
        lines.append('    def test_instantiation(self):')
        lines.append(f'        """Test {class_name} can be instantiated."""')
        if has_init:
            lines.append('        # TODO: Provide appropriate __init__ arguments')
            lines.append(f'        obj = {module_name}.{class_name}()  # Add required args')
        else:
            lines.append(f'        obj = {module_name}.{class_name}()')
        lines.append(f'        assert isinstance(obj, {module_name}.{class_name})')
        lines.append('')
        
        # Test each public method
        for method in methods:
            if not method.startswith('_') or method == '__init__':
                continue  # Skip private methods and __init__
                
            lines.append(f'    def test_{method}(self):')
            lines.append(f'        """Test {class_name}.{method} method."""')
            if has_init:
                lines.append('        # TODO: Provide appropriate __init__ arguments')
                lines.append(f'        obj = {module_name}.{class_name}()  # Add required args')
            else:
                lines.append(f'        obj = {module_name}.{class_name}()')
            lines.append('')
            lines.append('        # TODO: Add method test')
            lines.append(f'        # result = obj.{method}()  # Add required args')
            lines.append('        # assert result is not None  # Add specific assertion')
            lines.append('        pytest.skip("TODO: Implement test")')
            lines.append('')
        
        return lines


class CodeAnalyzer(ast.NodeVisitor):
    """Analyze Python code to extract testable components."""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.current_class = None
    
    def visit_Import(self, node):
        """Visit import statement."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from...import statement."""
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        # Skip private functions
        if node.name.startswith('_') and not node.name.startswith('__'):
            return
        
        # If we're inside a class, this is a method
        if self.current_class:
            self.current_class['methods'].append(node.name)
            if node.name == '__init__':
                self.current_class['has_init'] = True
        else:
            # Top-level function
            func_info = {
                'name': node.name,
                'args': [arg.arg for arg in node.args.args],
                'has_return': self._has_return(node),
                'docstring': ast.get_docstring(node) or ''
            }
            self.functions.append(func_info)
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definition."""
        # Skip private classes
        if node.name.startswith('_'):
            return
        
        # Store current class context
        prev_class = self.current_class
        self.current_class = {
            'name': node.name,
            'methods': [],
            'has_init': False
        }
        
        # Visit class body
        self.generic_visit(node)
        
        # Add class to list
        self.classes.append(self.current_class)
        
        # Restore previous context
        self.current_class = prev_class
    
    def _has_return(self, node):
        """Check if function has return statements with values."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
        return False


def main():
    """Command-line interface for test generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate unit tests for migrated Python code'
    )
    parser.add_argument(
        'path',
        help='Path to Python file or directory to generate tests for'
    )
    parser.add_argument(
        '-o', '--output',
        default='generated_tests',
        help='Output directory for generated tests (default: generated_tests)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing test files'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input path
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    # Generate tests
    print(f"Generating tests for: {args.path}")
    print(f"Output directory: {args.output}")
    print()
    
    generator = TestGenerator(args.path, args.output)
    summary = generator.generate_tests(overwrite=args.overwrite)
    
    # Display summary
    print("=" * 60)
    print("Test Generation Summary")
    print("=" * 60)
    print(f"Files processed:      {summary['files_processed']}")
    print(f"Test files created:   {len(summary['test_files_created'])}")
    print(f"Tests generated:      {summary['tests_generated']}")
    print(f"  - Functions tested: {summary['functions_tested']}")
    print(f"  - Classes tested:   {summary['classes_tested']}")
    print(f"Skipped files:        {len(summary['skipped_files'])}")
    print()
    
    if summary['test_files_created']:
        print("Generated test files:")
        for test_file in summary['test_files_created']:
            print(f"  ✓ {test_file}")
        print()
    
    if args.verbose and summary['skipped_files']:
        print("Skipped files:")
        for skipped in summary['skipped_files']:
            print(f"  - {skipped}")
        print()
    
    print("Next steps:")
    print("  1. Review generated tests and add specific assertions")
    print("  2. Provide appropriate test inputs and expected outputs")
    print("  3. Add edge cases and error handling tests")
    print(f"  4. Run tests: pytest {args.output}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
