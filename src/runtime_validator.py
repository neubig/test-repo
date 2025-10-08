#!/usr/bin/env python3
"""
Runtime Validator - Validate Python 3 code by attempting imports and checking for runtime issues
"""

import os
import sys
import ast
import importlib
import importlib.util
import traceback
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set


class RuntimeValidator:
    """Validates migrated Python code by attempting to import and run basic checks."""

    def __init__(self, target_path: str, verbose: bool = False):
        self.target_path = Path(target_path).resolve()
        self.verbose = verbose
        self.results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'warnings': []
        }
        self.original_path = sys.path.copy()

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the target path."""
        python_files = []
        
        if self.target_path.is_file():
            if self.target_path.suffix == '.py':
                python_files.append(self.target_path)
        else:
            for root, dirs, files in os.walk(self.target_path):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in {
                    '__pycache__', '.git', '.tox', 'venv', 'env', 
                    '.venv', 'node_modules', 'build', 'dist', '.eggs'
                }]
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(Path(root) / file)
        
        return sorted(python_files)

    def get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file_path.relative_to(self.target_path.parent)
            module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
            return '.'.join(module_parts)
        except ValueError:
            return file_path.stem

    def check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Check if file has valid Python 3 syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    def try_import_module(self, file_path: Path) -> Tuple[bool, str, List[str]]:
        """Try to import a module and return success status, error message, and warnings."""
        module_name = self.get_module_name(file_path)
        warnings = []
        
        # First check syntax
        syntax_ok, syntax_error = self.check_syntax(file_path)
        if not syntax_ok:
            return False, syntax_error, warnings

        # Temporarily add parent directory to path
        parent_dir = str(file_path.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Also add the target directory's parent for proper imports
        target_parent = str(self.target_path.parent)
        if target_parent not in sys.path:
            sys.path.insert(0, target_parent)

        try:
            # Try to load the module spec
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                return False, "Could not load module spec", warnings

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Check for common Python 2 remnants in the loaded module
            self._check_module_attributes(module, warnings)
            
            return True, "", warnings

        except ImportError as e:
            error_msg = f"Import error: {str(e)}"
            if self.verbose:
                error_msg += f"\n{traceback.format_exc()}"
            return False, error_msg, warnings

        except AttributeError as e:
            error_msg = f"Attribute error (possible Python 2 incompatibility): {str(e)}"
            if self.verbose:
                error_msg += f"\n{traceback.format_exc()}"
            return False, error_msg, warnings

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            if self.verbose:
                error_msg += f"\n{traceback.format_exc()}"
            return False, error_msg, warnings

        finally:
            # Clean up
            if module_name in sys.modules:
                try:
                    del sys.modules[module_name]
                except:
                    pass
            # Remove added paths
            if parent_dir in sys.path:
                sys.path.remove(parent_dir)
            if target_parent in sys.path and target_parent not in self.original_path:
                sys.path.remove(target_parent)

    def _check_module_attributes(self, module, warnings: List[str]):
        """Check module for common Python 2/3 compatibility issues."""
        # Check for Python 2 specific attributes that shouldn't be present
        py2_attributes = ['unicode', 'basestring', 'long', 'xrange']
        
        for attr in py2_attributes:
            if hasattr(module, attr):
                warnings.append(f"Contains Python 2 type '{attr}' - may cause issues")

    def validate(self) -> Dict:
        """Run validation on all Python files."""
        python_files = self.find_python_files()
        
        if not python_files:
            return {
                'success': [],
                'failed': [],
                'skipped': [],
                'warnings': [],
                'total': 0,
                'summary': 'No Python files found'
            }

        for file_path in python_files:
            rel_path = str(file_path.relative_to(self.target_path.parent))
            
            # Skip test files for now (they often have special requirements)
            if 'test' in file_path.parts or file_path.name.startswith('test_'):
                self.results['skipped'].append({
                    'file': rel_path,
                    'reason': 'Test file (requires test framework setup)'
                })
                continue

            success, error, warnings = self.try_import_module(file_path)
            
            if success:
                result = {'file': rel_path}
                if warnings:
                    result['warnings'] = warnings
                    self.results['warnings'].append(result)
                else:
                    self.results['success'].append(result)
            else:
                self.results['failed'].append({
                    'file': rel_path,
                    'error': error
                })

        return self._generate_summary()

    def _generate_summary(self) -> Dict:
        """Generate a summary of validation results."""
        total = (len(self.results['success']) + 
                len(self.results['failed']) + 
                len(self.results['skipped']) +
                len(self.results['warnings']))
        
        success_count = len(self.results['success']) + len(self.results['warnings'])
        failed_count = len(self.results['failed'])
        
        if total == 0:
            success_rate = 0
        else:
            # Count warnings as success for the rate calculation
            success_rate = (success_count / (total - len(self.results['skipped']))) * 100 if (total - len(self.results['skipped'])) > 0 else 0

        status = 'PASSED' if failed_count == 0 else 'FAILED'
        
        summary = {
            'total_files': total,
            'validated': total - len(self.results['skipped']),
            'success': len(self.results['success']),
            'warnings': len(self.results['warnings']),
            'failed': failed_count,
            'skipped': len(self.results['skipped']),
            'success_rate': round(success_rate, 2),
            'status': status
        }

        return {
            **self.results,
            'summary': summary
        }

    def generate_report(self, format: str = 'text') -> str:
        """Generate a validation report in the specified format."""
        results = self._generate_summary()
        summary = results['summary']

        if format == 'json':
            import json
            return json.dumps(results, indent=2)

        # Text format
        report = []
        report.append("=" * 70)
        report.append("RUNTIME VALIDATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        report.append(f"Total Files: {summary['total_files']}")
        report.append(f"Validated: {summary['validated']}")
        report.append(f"Success: {summary['success']}")
        report.append(f"Warnings: {summary['warnings']}")
        report.append(f"Failed: {summary['failed']}")
        report.append(f"Skipped: {summary['skipped']}")
        report.append(f"Success Rate: {summary['success_rate']}%")
        report.append(f"Status: {summary['status']}")
        report.append("")

        if results['success']:
            report.append("-" * 70)
            report.append(f"✓ SUCCESSFULLY VALIDATED ({len(results['success'])} files)")
            report.append("-" * 70)
            for item in results['success']:
                report.append(f"  ✓ {item['file']}")
            report.append("")

        if results['warnings']:
            report.append("-" * 70)
            report.append(f"⚠ VALIDATED WITH WARNINGS ({len(results['warnings'])} files)")
            report.append("-" * 70)
            for item in results['warnings']:
                report.append(f"  ⚠ {item['file']}")
                for warning in item['warnings']:
                    report.append(f"     - {warning}")
            report.append("")

        if results['failed']:
            report.append("-" * 70)
            report.append(f"✗ VALIDATION FAILED ({len(results['failed'])} files)")
            report.append("-" * 70)
            for item in results['failed']:
                report.append(f"  ✗ {item['file']}")
                report.append(f"     Error: {item['error']}")
                report.append("")

        if results['skipped']:
            report.append("-" * 70)
            report.append(f"○ SKIPPED ({len(results['skipped'])} files)")
            report.append("-" * 70)
            for item in results['skipped']:
                report.append(f"  ○ {item['file']}")
                report.append(f"     Reason: {item['reason']}")
            report.append("")

        report.append("=" * 70)
        
        if summary['failed'] == 0:
            report.append("✓ VALIDATION PASSED - All modules can be imported successfully!")
        else:
            report.append(f"✗ VALIDATION FAILED - {summary['failed']} module(s) have import errors")
        
        report.append("=" * 70)

        return '\n'.join(report)


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate Python 3 code by attempting to import all modules'
    )
    parser.add_argument('path', help='Path to Python file or directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed error tracebacks')
    parser.add_argument('-o', '--output', help='Save report to file')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')

    args = parser.parse_args()

    validator = RuntimeValidator(args.path, verbose=args.verbose)
    validator.validate()
    report = validator.generate_report(format=args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)

    # Exit with appropriate code
    results = validator._generate_summary()
    sys.exit(0 if results['summary']['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
