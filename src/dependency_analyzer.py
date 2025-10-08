#!/usr/bin/env python3
"""
Dependency Analyzer for Python 2 to 3 Migration

Analyzes project dependencies for Python 3 compatibility, identifies
incompatible packages, and suggests alternatives or upgrades.
"""

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path


class DependencyAnalyzer:
    """Analyze dependencies for Python 3 compatibility."""
    
    # Known Python 2-only standard library modules and their Python 3 equivalents
    STDLIB_RENAMES = {
        'ConfigParser': 'configparser',
        'Queue': 'queue',
        'SocketServer': 'socketserver',
        'BaseHTTPServer': 'http.server',
        'SimpleHTTPServer': 'http.server',
        'CGIHTTPServer': 'http.server',
        'cookielib': 'http.cookiejar',
        'Cookie': 'http.cookies',
        'htmlentitydefs': 'html.entities',
        'HTMLParser': 'html.parser',
        'httplib': 'http.client',
        'urllib': 'urllib.parse, urllib.request, urllib.error',
        'urllib2': 'urllib.request, urllib.error',
        'urlparse': 'urllib.parse',
        'robotparser': 'urllib.robotparser',
        'xmlrpclib': 'xmlrpc.client',
        'DocXMLRPCServer': 'xmlrpc.server',
        'SimpleXMLRPCServer': 'xmlrpc.server',
        'commands': 'subprocess',
        'UserDict': 'collections.UserDict',
        'UserList': 'collections.UserList',
        'UserString': 'collections.UserString',
        '__builtin__': 'builtins',
        'thread': '_thread',
        'dummy_thread': '_dummy_thread',
        'Tkinter': 'tkinter',
        'tkMessageBox': 'tkinter.messagebox',
        'tkColorChooser': 'tkinter.colorchooser',
        'tkFileDialog': 'tkinter.filedialog',
        'tkCommonDialog': 'tkinter.commondialog',
        'tkSimpleDialog': 'tkinter.simpledialog',
        'tkFont': 'tkinter.font',
        'Tkconstants': 'tkinter.constants',
        'Tix': 'tkinter.tix',
        'ttk': 'tkinter.ttk',
        'ScrolledText': 'tkinter.scrolledtext',
        'repr': 'reprlib',
        'StringIO': 'io.StringIO',
        'cStringIO': 'io.StringIO',
    }
    
    # Known third-party packages with Python 3 compatibility info
    PACKAGE_COMPATIBILITY = {
        'django': {
            'py3_min_version': '1.11',
            'recommended': '4.2',
            'notes': 'Django 1.11+ supports Python 3. Django 2.0+ is Python 3 only.'
        },
        'flask': {
            'py3_min_version': '0.10',
            'recommended': '2.3',
            'notes': 'Flask has supported Python 3 since 0.10.'
        },
        'requests': {
            'py3_min_version': '2.0',
            'recommended': '2.31',
            'notes': 'Fully compatible with Python 3.'
        },
        'numpy': {
            'py3_min_version': '1.11',
            'recommended': '1.24',
            'notes': 'NumPy 1.11+ supports Python 3. Use latest version.'
        },
        'pandas': {
            'py3_min_version': '0.19',
            'recommended': '2.0',
            'notes': 'Pandas 0.19+ supports Python 3.'
        },
        'pillow': {
            'py3_min_version': '2.0',
            'recommended': '10.0',
            'notes': 'Pillow (PIL fork) fully supports Python 3.'
        },
        'pil': {
            'py3_compatible': False,
            'alternative': 'pillow',
            'notes': 'PIL is not Python 3 compatible. Use Pillow instead.'
        },
        'mysql-python': {
            'py3_compatible': False,
            'alternative': 'mysqlclient or PyMySQL',
            'notes': 'MySQLdb is not Python 3 compatible. Use mysqlclient or PyMySQL.'
        },
        'fabric': {
            'py3_min_version': '2.0',
            'recommended': '3.0',
            'notes': 'Fabric 2.0+ is Python 3 compatible. Major API changes from 1.x.'
        },
        'twisted': {
            'py3_min_version': '15.4',
            'recommended': '23.8',
            'notes': 'Twisted 15.4+ supports Python 3.'
        },
        'sqlalchemy': {
            'py3_min_version': '0.9',
            'recommended': '2.0',
            'notes': 'SQLAlchemy has good Python 3 support since 0.9.'
        },
        'celery': {
            'py3_min_version': '4.0',
            'recommended': '5.3',
            'notes': 'Celery 4.0+ is Python 3 compatible.'
        },
        'beautifulsoup4': {
            'py3_min_version': '4.0',
            'recommended': '4.12',
            'notes': 'BeautifulSoup4 fully supports Python 3.'
        },
        'scrapy': {
            'py3_min_version': '1.1',
            'recommended': '2.11',
            'notes': 'Scrapy 1.1+ supports Python 3.'
        },
    }
    
    def __init__(self, project_path='.'):
        """Initialize the dependency analyzer.
        
        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = Path(project_path).resolve()
        self.dependencies = defaultdict(set)
        self.import_locations = defaultdict(list)
        self.issues = []
        
    def scan_requirements_txt(self, req_file='requirements.txt'):
        """Scan requirements.txt for dependencies.
        
        Args:
            req_file: Path to requirements.txt file
        """
        req_path = self.project_path / req_file
        if not req_path.exists():
            return
        
        with open(req_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse package name and version
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    package = match.group(1).lower()
                    self.dependencies['requirements.txt'].add(package)
                    self.import_locations[package].append({
                        'source': 'requirements.txt',
                        'line': line_num,
                        'raw': line
                    })
    
    def scan_setup_py(self):
        """Scan setup.py for dependencies."""
        setup_path = self.project_path / 'setup.py'
        if not setup_path.exists():
            return
        
        try:
            with open(setup_path, 'r') as f:
                content = f.read()
            
            # Look for install_requires
            install_requires_match = re.search(
                r'install_requires\s*=\s*\[(.*?)\]',
                content,
                re.DOTALL
            )
            
            if install_requires_match:
                requires_str = install_requires_match.group(1)
                # Extract package names from strings
                packages = re.findall(r'["\']([a-zA-Z0-9_-]+)', requires_str)
                for package in packages:
                    package = package.lower()
                    self.dependencies['setup.py'].add(package)
                    self.import_locations[package].append({
                        'source': 'setup.py',
                        'line': None,
                        'raw': None
                    })
        except Exception as e:
            self.issues.append({
                'type': 'scan_error',
                'file': 'setup.py',
                'message': f"Error scanning setup.py: {e}"
            })
    
    def scan_imports(self, scan_path=None):
        """Scan Python files for import statements.
        
        Args:
            scan_path: Path to scan (defaults to project_path)
        """
        scan_path = scan_path or self.project_path
        
        python_files = []
        for root, dirs, files in os.walk(scan_path):
            # Skip hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['venv', 'env', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                module = alias.name.split('.')[0]
                                self.dependencies['imports'].add(module)
                                self.import_locations[module].append({
                                    'source': py_file,
                                    'line': node.lineno,
                                    'raw': alias.name
                                })
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                module = node.module.split('.')[0]
                                self.dependencies['imports'].add(module)
                                self.import_locations[module].append({
                                    'source': py_file,
                                    'line': node.lineno,
                                    'raw': node.module
                                })
                except SyntaxError:
                    # Might be Python 2 syntax, try basic regex extraction
                    imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
                    for module in imports:
                        self.dependencies['imports'].add(module)
                        self.import_locations[module].append({
                            'source': py_file,
                            'line': None,
                            'raw': module
                        })
            except Exception as e:
                self.issues.append({
                    'type': 'scan_error',
                    'file': py_file,
                    'message': f"Error scanning file: {e}"
                })
    
    def analyze_compatibility(self):
        """Analyze all dependencies for Python 3 compatibility.
        
        Returns:
            dict: Analysis results with categories
        """
        all_packages = set()
        for source, packages in self.dependencies.items():
            all_packages.update(packages)
        
        results = {
            'stdlib_renames': [],
            'incompatible': [],
            'needs_upgrade': [],
            'compatible': [],
            'unknown': []
        }
        
        for package in sorted(all_packages):
            locations = self.import_locations.get(package, [])
            
            # Check if it's a renamed standard library module
            if package in self.STDLIB_RENAMES:
                results['stdlib_renames'].append({
                    'package': package,
                    'py3_name': self.STDLIB_RENAMES[package],
                    'locations': locations
                })
            # Check known third-party packages
            elif package in self.PACKAGE_COMPATIBILITY:
                info = self.PACKAGE_COMPATIBILITY[package]
                
                if info.get('py3_compatible') == False:
                    results['incompatible'].append({
                        'package': package,
                        'alternative': info.get('alternative', 'Unknown'),
                        'notes': info.get('notes', ''),
                        'locations': locations
                    })
                elif 'py3_min_version' in info:
                    results['needs_upgrade'].append({
                        'package': package,
                        'min_version': info['py3_min_version'],
                        'recommended': info.get('recommended', 'latest'),
                        'notes': info.get('notes', ''),
                        'locations': locations
                    })
                else:
                    results['compatible'].append({
                        'package': package,
                        'notes': info.get('notes', ''),
                        'locations': locations
                    })
            # Check if it's likely a standard library module (no known issues)
            elif package in ['os', 'sys', 'json', 're', 'time', 'datetime', 
                           'collections', 'itertools', 'functools', 'math',
                           'random', 'string', 'io', 'subprocess', 'logging']:
                results['compatible'].append({
                    'package': package,
                    'notes': 'Standard library, compatible',
                    'locations': locations
                })
            else:
                # Unknown package - might need manual checking
                results['unknown'].append({
                    'package': package,
                    'locations': locations
                })
        
        return results
    
    def generate_report(self, output_format='text'):
        """Generate a compatibility report.
        
        Args:
            output_format: Format for the report ('text' or 'json')
            
        Returns:
            str: Formatted report
        """
        results = self.analyze_compatibility()
        
        if output_format == 'json':
            return json.dumps(results, indent=2, default=str)
        
        # Text format
        lines = []
        lines.append('=' * 70)
        lines.append('Python 3 Dependency Compatibility Report')
        lines.append('=' * 70)
        lines.append('')
        
        # Summary
        total = sum(len(results[key]) for key in results)
        lines.append(f"Total dependencies analyzed: {total}")
        lines.append(f"  Standard library renames: {len(results['stdlib_renames'])}")
        lines.append(f"  Incompatible packages: {len(results['incompatible'])}")
        lines.append(f"  Packages needing upgrade: {len(results['needs_upgrade'])}")
        lines.append(f"  Compatible packages: {len(results['compatible'])}")
        lines.append(f"  Unknown packages: {len(results['unknown'])}")
        lines.append('')
        
        # Standard library renames
        if results['stdlib_renames']:
            lines.append('=' * 70)
            lines.append('STANDARD LIBRARY RENAMES')
            lines.append('=' * 70)
            lines.append('These modules have been renamed in Python 3:')
            lines.append('')
            for item in results['stdlib_renames']:
                lines.append(f"• {item['package']}")
                lines.append(f"  → Python 3 name: {item['py3_name']}")
                if item['locations']:
                    lines.append(f"  Used in {len(item['locations'])} location(s)")
                    for loc in item['locations'][:3]:  # Show first 3 locations
                        if loc['line']:
                            lines.append(f"    - {loc['source']}:{loc['line']}")
                        else:
                            lines.append(f"    - {loc['source']}")
                lines.append('')
        
        # Incompatible packages
        if results['incompatible']:
            lines.append('=' * 70)
            lines.append('INCOMPATIBLE PACKAGES')
            lines.append('=' * 70)
            lines.append('These packages are NOT Python 3 compatible:')
            lines.append('')
            for item in results['incompatible']:
                lines.append(f"• {item['package']}")
                lines.append(f"  → Alternative: {item['alternative']}")
                if item.get('notes'):
                    lines.append(f"  Notes: {item['notes']}")
                if item['locations']:
                    lines.append(f"  Used in {len(item['locations'])} location(s)")
                lines.append('')
        
        # Packages needing upgrade
        if results['needs_upgrade']:
            lines.append('=' * 70)
            lines.append('PACKAGES NEEDING UPGRADE')
            lines.append('=' * 70)
            lines.append('These packages need to be upgraded for Python 3:')
            lines.append('')
            for item in results['needs_upgrade']:
                lines.append(f"• {item['package']}")
                lines.append(f"  → Minimum version: {item['min_version']}")
                lines.append(f"  → Recommended: {item['recommended']}")
                if item.get('notes'):
                    lines.append(f"  Notes: {item['notes']}")
                if item['locations']:
                    lines.append(f"  Used in {len(item['locations'])} location(s)")
                lines.append('')
        
        # Unknown packages
        if results['unknown']:
            lines.append('=' * 70)
            lines.append('UNKNOWN PACKAGES')
            lines.append('=' * 70)
            lines.append('These packages should be manually checked:')
            lines.append('')
            for item in results['unknown']:
                lines.append(f"• {item['package']}")
                lines.append(f"  → Please check PyPI or package documentation")
                if item['locations']:
                    lines.append(f"  Used in {len(item['locations'])} location(s)")
                lines.append('')
        
        # Scan issues
        if self.issues:
            lines.append('=' * 70)
            lines.append('SCAN ISSUES')
            lines.append('=' * 70)
            lines.append('Issues encountered during scanning:')
            lines.append('')
            for issue in self.issues:
                lines.append(f"• {issue['file']}: {issue['message']}")
            lines.append('')
        
        lines.append('=' * 70)
        lines.append('RECOMMENDATIONS')
        lines.append('=' * 70)
        
        if results['stdlib_renames']:
            lines.append('1. Update imports for renamed standard library modules')
            lines.append('   The fixer tool can handle these automatically.')
            lines.append('')
        
        if results['incompatible']:
            lines.append('2. Replace incompatible packages with alternatives')
            lines.append('   Update requirements.txt and code accordingly.')
            lines.append('')
        
        if results['needs_upgrade']:
            lines.append('3. Upgrade packages to Python 3 compatible versions')
            lines.append('   Update version specifiers in requirements.txt.')
            lines.append('')
        
        if results['unknown']:
            lines.append('4. Manually verify unknown packages')
            lines.append('   Check package documentation or PyPI for Python 3 support.')
            lines.append('')
        
        return '\n'.join(lines)
    
    def scan_all(self):
        """Scan all sources for dependencies."""
        self.scan_requirements_txt()
        self.scan_setup_py()
        self.scan_imports()


def main():
    """Main entry point for standalone usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze dependencies for Python 3 compatibility'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path to analyze (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for report (default: print to console)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer(args.path)
    analyzer.scan_all()
    report = analyzer.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
