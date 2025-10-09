#!/usr/bin/env python3
"""
Package Upgrade Recommender for Python 2 to 3 Migration

Analyzes project dependencies, checks Python 3 compatibility on PyPI,
recommends version upgrades, and generates updated requirements files.
"""

import json
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import ssl


@dataclass
class PackageInfo:
    """Information about a package."""
    name: str
    current_version: Optional[str]
    latest_version: Optional[str]
    python3_compatible: bool
    requires_python: Optional[str]
    status: str  # 'ok', 'upgrade_available', 'python2_only', 'not_found', 'error'
    message: str
    homepage: Optional[str] = None


class PackageUpgradeRecommender:
    """Recommends package upgrades for Python 3 compatibility."""
    
    def __init__(self, requirements_file: str = 'requirements.txt'):
        """Initialize the recommender.
        
        Args:
            requirements_file: Path to requirements.txt file
        """
        self.requirements_file = Path(requirements_file)
        self.packages: List[PackageInfo] = []
        self.stats = {
            'total': 0,
            'ok': 0,
            'upgrade_available': 0,
            'python2_only': 0,
            'not_found': 0,
            'errors': 0
        }
    
    def analyze(self, verbose: bool = False) -> Dict[str, Any]:
        """Analyze all packages in requirements file.
        
        Args:
            verbose: Show detailed progress
            
        Returns:
            dict: Analysis results
        """
        if not self.requirements_file.exists():
            return {
                'success': False,
                'error': f'Requirements file not found: {self.requirements_file}'
            }
        
        # Parse requirements file
        requirements = self._parse_requirements()
        if not requirements:
            return {
                'success': False,
                'error': 'No packages found in requirements file'
            }
        
        self.stats['total'] = len(requirements)
        
        if verbose:
            print(f"Analyzing {len(requirements)} packages...\n")
        
        # Analyze each package
        for i, (package_name, version_spec) in enumerate(requirements, 1):
            if verbose:
                print(f"[{i}/{len(requirements)}] Checking {package_name}...", end=' ')
            
            info = self._check_package(package_name, version_spec)
            self.packages.append(info)
            self.stats[info.status] = self.stats.get(info.status, 0) + 1
            
            if verbose:
                status_emoji = {
                    'ok': '✓',
                    'upgrade_available': '↑',
                    'python2_only': '✗',
                    'not_found': '?',
                    'error': '!'
                }
                print(f"{status_emoji.get(info.status, '?')} {info.status}")
        
        if verbose:
            print()
        
        return {
            'success': True,
            'packages': [asdict(p) for p in self.packages],
            'stats': self.stats
        }
    
    def _parse_requirements(self) -> List[Tuple[str, Optional[str]]]:
        """Parse requirements.txt file.
        
        Returns:
            list: List of (package_name, version_spec) tuples
        """
        requirements = []
        
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Skip -r or -e directives
                if line.startswith('-'):
                    continue
                
                # Parse package name and version
                # Handle formats: package, package==1.0, package>=1.0, etc.
                match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+.*)?', line)
                if match:
                    package_name = match.group(1)
                    version_spec = match.group(2).strip() if match.group(2) else None
                    requirements.append((package_name, version_spec))
        
        return requirements
    
    def _check_package(self, package_name: str, version_spec: Optional[str]) -> PackageInfo:
        """Check a package on PyPI for Python 3 compatibility.
        
        Args:
            package_name: Name of the package
            version_spec: Version specification (e.g., '==1.0', '>=2.0')
            
        Returns:
            PackageInfo: Package information
        """
        try:
            # Fetch package info from PyPI
            pypi_data = self._fetch_pypi_data(package_name)
            
            if not pypi_data:
                return PackageInfo(
                    name=package_name,
                    current_version=self._extract_version(version_spec),
                    latest_version=None,
                    python3_compatible=False,
                    requires_python=None,
                    status='not_found',
                    message='Package not found on PyPI'
                )
            
            # Extract information
            latest_version = pypi_data['info'].get('version', 'unknown')
            requires_python = pypi_data['info'].get('requires_python', '')
            homepage = pypi_data['info'].get('home_page') or pypi_data['info'].get('project_url')
            
            # Check Python 3 compatibility
            python3_compatible = self._is_python3_compatible(pypi_data)
            
            # Determine status
            current_version = self._extract_version(version_spec)
            
            if not python3_compatible:
                status = 'python2_only'
                message = 'No Python 3 support found. Consider finding an alternative.'
            elif current_version and current_version != latest_version:
                status = 'upgrade_available'
                message = f'Upgrade available: {current_version} → {latest_version}'
            else:
                status = 'ok'
                message = 'Latest version, Python 3 compatible'
            
            return PackageInfo(
                name=package_name,
                current_version=current_version,
                latest_version=latest_version,
                python3_compatible=python3_compatible,
                requires_python=requires_python or 'Not specified',
                status=status,
                message=message,
                homepage=homepage
            )
            
        except Exception as e:
            return PackageInfo(
                name=package_name,
                current_version=self._extract_version(version_spec),
                latest_version=None,
                python3_compatible=False,
                requires_python=None,
                status='error',
                message=f'Error checking package: {str(e)}'
            )
    
    def _fetch_pypi_data(self, package_name: str) -> Optional[Dict]:
        """Fetch package data from PyPI JSON API.
        
        Args:
            package_name: Name of the package
            
        Returns:
            dict: Package data or None if not found
        """
        url = f'https://pypi.org/pypi/{package_name}/json'
        
        try:
            # Create SSL context that doesn't verify certificates (for compatibility)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            request = Request(url, headers={'User-Agent': 'Python-Migration-Tool/1.0'})
            with urlopen(request, context=context, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except (URLError, HTTPError, json.JSONDecodeError):
            return None
    
    def _is_python3_compatible(self, pypi_data: Dict) -> bool:
        """Check if package supports Python 3.
        
        Args:
            pypi_data: Package data from PyPI
            
        Returns:
            bool: True if Python 3 is supported
        """
        # Check requires_python field
        requires_python = pypi_data['info'].get('requires_python', '')
        if requires_python:
            # If it explicitly requires Python 3, it's compatible
            if '>=3' in requires_python or '>3' in requires_python:
                return True
            # If it requires Python 2, it's not compatible
            if '==2' in requires_python or '<3' in requires_python:
                return False
        
        # Check classifiers
        classifiers = pypi_data['info'].get('classifiers', [])
        python3_classifiers = [c for c in classifiers if 'Programming Language :: Python :: 3' in c]
        python2_only = [c for c in classifiers if c == 'Programming Language :: Python :: 2 :: Only']
        
        if python2_only:
            return False
        
        if python3_classifiers:
            return True
        
        # If no clear indication, assume it might work (user should test)
        return True
    
    def _extract_version(self, version_spec: Optional[str]) -> Optional[str]:
        """Extract version number from version specification.
        
        Args:
            version_spec: Version specification (e.g., '==1.0.0', '>=2.0')
            
        Returns:
            str: Version number or None
        """
        if not version_spec:
            return None
        
        # Extract version number from specification
        match = re.search(r'[\d.]+', version_spec)
        return match.group(0) if match else None
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate a report of package analysis.
        
        Args:
            output_format: Format of report ('text', 'markdown', 'json')
            
        Returns:
            str: Report content
        """
        if output_format == 'json':
            return json.dumps({
                'packages': [asdict(p) for p in self.packages],
                'stats': self.stats
            }, indent=2)
        
        if output_format == 'markdown':
            return self._generate_markdown_report()
        
        return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate text format report."""
        lines = []
        lines.append("=" * 80)
        lines.append("Package Upgrade Recommendations for Python 3 Migration")
        lines.append("=" * 80)
        lines.append("")
        
        # Statistics
        lines.append("Summary:")
        lines.append(f"  Total packages:        {self.stats['total']}")
        lines.append(f"  ✓ Up to date:          {self.stats['ok']}")
        lines.append(f"  ↑ Upgrades available:  {self.stats['upgrade_available']}")
        lines.append(f"  ✗ Python 2 only:       {self.stats['python2_only']}")
        lines.append(f"  ? Not found:           {self.stats['not_found']}")
        lines.append(f"  ! Errors:              {self.stats['errors']}")
        lines.append("")
        
        # Group packages by status
        groups = {
            'upgrade_available': ('Packages with Upgrades Available', '↑'),
            'python2_only': ('Python 2 Only Packages (Action Required)', '✗'),
            'not_found': ('Packages Not Found', '?'),
            'error': ('Packages with Errors', '!'),
            'ok': ('Packages Up to Date', '✓')
        }
        
        for status, (title, emoji) in groups.items():
            packages = [p for p in self.packages if p.status == status]
            if packages:
                lines.append("-" * 80)
                lines.append(f"{emoji} {title}")
                lines.append("-" * 80)
                for pkg in packages:
                    lines.append(f"\n{pkg.name}")
                    if pkg.current_version:
                        lines.append(f"  Current:  {pkg.current_version}")
                    if pkg.latest_version:
                        lines.append(f"  Latest:   {pkg.latest_version}")
                    lines.append(f"  Python 3: {'Yes' if pkg.python3_compatible else 'No'}")
                    if pkg.requires_python:
                        lines.append(f"  Requires: {pkg.requires_python}")
                    lines.append(f"  Status:   {pkg.message}")
                    if pkg.homepage:
                        lines.append(f"  Homepage: {pkg.homepage}")
                lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown format report."""
        lines = []
        lines.append("# Package Upgrade Recommendations")
        lines.append("")
        lines.append("*Python 2 to 3 Migration Analysis*")
        lines.append("")
        
        # Statistics
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total packages**: {self.stats['total']}")
        lines.append(f"- ✓ **Up to date**: {self.stats['ok']}")
        lines.append(f"- ↑ **Upgrades available**: {self.stats['upgrade_available']}")
        lines.append(f"- ✗ **Python 2 only**: {self.stats['python2_only']}")
        lines.append(f"- ? **Not found**: {self.stats['not_found']}")
        lines.append(f"- ! **Errors**: {self.stats['errors']}")
        lines.append("")
        
        # Detailed tables
        if self.stats['upgrade_available'] > 0:
            lines.append("## Packages with Upgrades Available")
            lines.append("")
            lines.append("| Package | Current | Latest | Python 3 | Requires Python |")
            lines.append("|---------|---------|--------|----------|-----------------|")
            for pkg in self.packages:
                if pkg.status == 'upgrade_available':
                    py3 = '✓' if pkg.python3_compatible else '✗'
                    lines.append(f"| {pkg.name} | {pkg.current_version or 'N/A'} | "
                               f"{pkg.latest_version or 'N/A'} | {py3} | "
                               f"{pkg.requires_python or 'N/A'} |")
            lines.append("")
        
        if self.stats['python2_only'] > 0:
            lines.append("## ⚠️ Python 2 Only Packages")
            lines.append("")
            lines.append("These packages do not support Python 3. Consider finding alternatives:")
            lines.append("")
            for pkg in self.packages:
                if pkg.status == 'python2_only':
                    lines.append(f"- **{pkg.name}** - {pkg.message}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_updated_requirements(self, output_file: str = 'requirements-py3.txt') -> str:
        """Generate updated requirements.txt with recommended versions.
        
        Args:
            output_file: Path to output file
            
        Returns:
            str: Path to generated file
        """
        lines = []
        lines.append("# Updated requirements for Python 3")
        lines.append(f"# Generated from: {self.requirements_file}")
        lines.append("")
        
        for pkg in self.packages:
            if pkg.status == 'python2_only':
                lines.append(f"# {pkg.name} - Python 2 only, find alternative")
                lines.append(f"# {pkg.name}=={pkg.current_version or 'unknown'}")
            elif pkg.latest_version:
                lines.append(f"{pkg.name}=={pkg.latest_version}")
            else:
                lines.append(f"{pkg.name}  # Version unknown, please verify")
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return str(output_path)


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze and recommend package upgrades for Python 3 migration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze requirements.txt
  %(prog)s
  
  # Analyze with verbose output
  %(prog)s -v
  
  # Generate markdown report
  %(prog)s -f markdown -o report.md
  
  # Generate updated requirements file
  %(prog)s --generate-requirements requirements-py3.txt
        """
    )
    
    parser.add_argument(
        'requirements_file',
        nargs='?',
        default='requirements.txt',
        help='Path to requirements.txt (default: requirements.txt)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'markdown', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save report to file'
    )
    parser.add_argument(
        '--generate-requirements',
        metavar='FILE',
        help='Generate updated requirements.txt with recommended versions'
    )
    
    args = parser.parse_args()
    
    # Check if requirements file exists
    if not Path(args.requirements_file).exists():
        print(f"Error: Requirements file not found: {args.requirements_file}")
        return 1
    
    # Create recommender and analyze
    recommender = PackageUpgradeRecommender(args.requirements_file)
    result = recommender.analyze(verbose=args.verbose)
    
    if not result['success']:
        print(f"Error: {result['error']}")
        return 1
    
    # Generate report
    report = recommender.generate_report(output_format=args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)
    
    # Generate updated requirements if requested
    if args.generate_requirements:
        output_file = recommender.generate_updated_requirements(args.generate_requirements)
        print(f"\nUpdated requirements saved to: {output_file}")
        print("⚠️  Please review and test the updated requirements before using!")
    
    # Return non-zero if there are issues
    if result['stats']['python2_only'] > 0 or result['stats']['errors'] > 0:
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
