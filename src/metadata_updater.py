#!/usr/bin/env python3
"""
Project Metadata Updater

Automatically updates project metadata and configuration files to reflect Python 3 compatibility.
Handles setup.py, pyproject.toml, tox.ini, CI configs, and more.
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class MetadataUpdater:
    """Updates project metadata files for Python 3 compatibility."""
    
    def __init__(self, project_dir: str = ".", min_python: str = "3.6", max_python: str = "3.12"):
        """
        Initialize the metadata updater.
        
        Args:
            project_dir: Root directory of the project
            min_python: Minimum Python 3 version to support (e.g., "3.6")
            max_python: Maximum Python 3 version to support (e.g., "3.12")
        """
        self.project_dir = Path(project_dir).resolve()
        self.min_python = min_python
        self.max_python = max_python
        self.changes = []
        self.backup_dir = self.project_dir / ".metadata_backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def update_all(self, dry_run: bool = False) -> Dict:
        """
        Update all project metadata files.
        
        Args:
            dry_run: If True, only report changes without making them
            
        Returns:
            Dictionary with update results
        """
        results = {
            "updated_files": [],
            "skipped_files": [],
            "errors": [],
            "dry_run": dry_run
        }
        
        # Define all updater methods
        updaters = [
            ("setup.py", self._update_setup_py),
            ("setup.cfg", self._update_setup_cfg),
            ("pyproject.toml", self._update_pyproject_toml),
            ("tox.ini", self._update_tox_ini),
            (".python-version", self._update_python_version),
            ("Pipfile", self._update_pipfile),
            ("README.md", self._update_readme),
            (".github/workflows/*.yml", self._update_github_actions),
            (".gitlab-ci.yml", self._update_gitlab_ci),
            (".travis.yml", self._update_travis_ci),
        ]
        
        for file_pattern, updater_func in updaters:
            try:
                if "*" in file_pattern:
                    # Handle wildcards
                    pattern_path = self.project_dir / file_pattern.replace("*", "")
                    if pattern_path.parent.exists():
                        for file_path in pattern_path.parent.glob(pattern_path.name.replace("", "*")):
                            self._process_file(file_path, updater_func, results, dry_run)
                else:
                    file_path = self.project_dir / file_pattern
                    self._process_file(file_path, updater_func, results, dry_run)
            except Exception as e:
                results["errors"].append(f"Error updating {file_pattern}: {str(e)}")
        
        return results
    
    def _process_file(self, file_path: Path, updater_func, results: Dict, dry_run: bool):
        """Process a single file with an updater function."""
        if file_path.exists():
            try:
                updated_content, changes = updater_func(file_path)
                if changes:
                    if not dry_run:
                        self._backup_file(file_path)
                        file_path.write_text(updated_content)
                    results["updated_files"].append({
                        "file": str(file_path.relative_to(self.project_dir)),
                        "changes": changes
                    })
                else:
                    results["skipped_files"].append(str(file_path.relative_to(self.project_dir)))
            except Exception as e:
                results["errors"].append(f"Error processing {file_path.name}: {str(e)}")
    
    def _backup_file(self, file_path: Path):
        """Create a backup of a file before modifying it."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)
    
    def _update_setup_py(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update setup.py with Python 3 metadata."""
        content = file_path.read_text()
        changes = []
        
        # Update python_requires
        if 'python_requires' not in content:
            # Add python_requires before the closing parenthesis of setup()
            if 'setup(' in content:
                content = re.sub(
                    r'(\s+)(.*?)\n(\s*)\)',
                    rf'\1\2,\n\1python_requires=">={self.min_python}",\n\3)',
                    content,
                    count=1
                )
                changes.append(f"Added python_requires='>={self.min_python}'")
        else:
            # Update existing python_requires
            old_requires = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
            if old_requires and '2' in old_requires.group(1):
                content = re.sub(
                    r'python_requires\s*=\s*["\'][^"\']+["\']',
                    f'python_requires=">={self.min_python}"',
                    content
                )
                changes.append(f"Updated python_requires from '{old_requires.group(1)}' to '>={self.min_python}'")
        
        # Update classifiers
        if 'Programming Language :: Python :: 2' in content:
            # Remove Python 2 classifiers
            content = re.sub(
                r'\s*["\']Programming Language :: Python :: 2[^"\']*["\'],?\n',
                '',
                content
            )
            changes.append("Removed Python 2 classifiers")
        
        # Add Python 3 classifiers if not present
        python3_classifiers = [
            "Programming Language :: Python :: 3"
        ] + [
            f"Programming Language :: Python :: 3.{v}"
            for v in range(int(self.min_python.split('.')[1]), int(self.max_python.split('.')[1]) + 1)
        ]
        
        if 'Programming Language :: Python :: 3' not in content and 'classifiers' in content:
            # Add Python 3 classifiers
            classifier_section = re.search(r'classifiers\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if classifier_section:
                new_classifiers = ',\n        '.join([f'"{c}"' for c in python3_classifiers])
                content = re.sub(
                    r'(classifiers\s*=\s*\[)',
                    rf'\1\n        {new_classifiers},',
                    content
                )
                changes.append("Added Python 3 classifiers")
        
        return content, changes
    
    def _update_setup_cfg(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update setup.cfg with Python 3 metadata."""
        content = file_path.read_text()
        changes = []
        
        # Update python_requires in [options] section
        if '[options]' in content:
            if 'python_requires' not in content:
                content = re.sub(
                    r'(\[options\])',
                    rf'\1\npython_requires = >={self.min_python}',
                    content
                )
                changes.append(f"Added python_requires = >={self.min_python}")
            else:
                old_requires = re.search(r'python_requires\s*=\s*(.+)', content)
                if old_requires and '2' in old_requires.group(1):
                    content = re.sub(
                        r'python_requires\s*=\s*.+',
                        f'python_requires = >={self.min_python}',
                        content
                    )
                    changes.append(f"Updated python_requires to >={self.min_python}")
        
        return content, changes
    
    def _update_pyproject_toml(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update pyproject.toml with Python 3 metadata."""
        content = file_path.read_text()
        changes = []
        
        # Update requires-python
        if 'requires-python' in content.lower():
            old_requires = re.search(r'requires-python\s*=\s*"([^"]+)"', content, re.IGNORECASE)
            if old_requires and '2' in old_requires.group(1):
                content = re.sub(
                    r'requires-python\s*=\s*"[^"]+"',
                    f'requires-python = ">={self.min_python}"',
                    content,
                    flags=re.IGNORECASE
                )
                changes.append(f"Updated requires-python to >={self.min_python}")
        else:
            # Add requires-python to [project] section if it exists
            if '[project]' in content:
                content = re.sub(
                    r'(\[project\])',
                    rf'\1\nrequires-python = ">={self.min_python}"',
                    content
                )
                changes.append(f"Added requires-python = >={self.min_python}")
        
        # Update Python version in [tool.poetry.dependencies] if using Poetry
        if '[tool.poetry.dependencies]' in content:
            content = re.sub(
                r'(python\s*=\s*")[^"]+"',
                rf'\1^{self.min_python}"',
                content
            )
            changes.append(f"Updated Poetry python dependency to ^{self.min_python}")
        
        return content, changes
    
    def _update_tox_ini(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update tox.ini with Python 3 test environments."""
        content = file_path.read_text()
        changes = []
        
        # Update envlist
        if 'envlist' in content:
            old_envlist = re.search(r'envlist\s*=\s*(.+)', content)
            if old_envlist and ('py2' in old_envlist.group(1) or 'py27' in old_envlist.group(1)):
                # Generate Python 3 envlist
                min_ver = int(self.min_python.split('.')[1])
                max_ver = int(self.max_python.split('.')[1])
                new_envlist = ','.join([f'py3{v}' for v in range(min_ver, max_ver + 1)])
                content = re.sub(
                    r'envlist\s*=\s*.+',
                    f'envlist = {new_envlist}',
                    content
                )
                changes.append(f"Updated envlist to {new_envlist}")
        
        # Update basepython if it references Python 2
        if 'basepython' in content and 'python2' in content.lower():
            content = re.sub(
                r'basepython\s*=\s*python2[^\n]*',
                f'basepython = python3',
                content,
                flags=re.IGNORECASE
            )
            changes.append("Updated basepython from python2 to python3")
        
        return content, changes
    
    def _update_python_version(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update .python-version file."""
        content = file_path.read_text().strip()
        changes = []
        
        if content.startswith('2.'):
            new_version = f"{self.min_python}.0"
            content = new_version + '\n'
            changes.append(f"Updated Python version from {content.strip()} to {new_version}")
        
        return content, changes
    
    def _update_pipfile(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update Pipfile with Python 3 version."""
        content = file_path.read_text()
        changes = []
        
        # Update python_version in [requires] section
        if 'python_version' in content:
            old_version = re.search(r'python_version\s*=\s*"([^"]+)"', content)
            if old_version and old_version.group(1).startswith('2'):
                content = re.sub(
                    r'python_version\s*=\s*"[^"]+"',
                    f'python_version = "{self.min_python}"',
                    content
                )
                changes.append(f"Updated python_version to {self.min_python}")
        
        return content, changes
    
    def _update_readme(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update README.md with Python 3 version badges and requirements."""
        content = file_path.read_text()
        changes = []
        
        # Update Python version badges (shields.io)
        if 'python-2.' in content.lower() or 'python%202' in content.lower():
            # Update badge version
            content = re.sub(
                r'python-2\.[0-9]+',
                f'python-{self.min_python}%2B',
                content,
                flags=re.IGNORECASE
            )
            content = re.sub(
                r'python%202\.[0-9]+',
                f'python-{self.min_python}%2B',
                content,
                flags=re.IGNORECASE
            )
            changes.append("Updated Python version badge to Python 3")
        
        # Update text mentions of Python 2
        patterns = [
            (r'Python 2\.[0-9]+', f'Python {self.min_python}+'),
            (r'python 2\.[0-9]+', f'Python {self.min_python}+'),
            (r'requires Python 2', f'requires Python {self.min_python}+'),
            (r'Requires: Python 2', f'Requires: Python {self.min_python}+'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                if not any('Updated README Python version mentions' in c for c in changes):
                    changes.append('Updated README Python version mentions')
        
        return content, changes
    
    def _update_github_actions(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update GitHub Actions workflow files."""
        content = file_path.read_text()
        changes = []
        
        # Update Python version matrix
        if 'python-version:' in content:
            # Look for version arrays
            version_matrix = re.search(r'python-version:\s*\[(.*?)\]', content, re.DOTALL)
            if version_matrix and ('2.' in version_matrix.group(1) or "'2" in version_matrix.group(1)):
                min_ver = int(self.min_python.split('.')[1])
                max_ver = int(self.max_python.split('.')[1])
                new_versions = ', '.join([f"'3.{v}'" for v in range(min_ver, max_ver + 1)])
                content = re.sub(
                    r'python-version:\s*\[.*?\]',
                    f'python-version: [{new_versions}]',
                    content,
                    flags=re.DOTALL
                )
                changes.append(f"Updated python-version matrix to Python 3 versions")
        
        # Update actions/setup-python version specifications
        if "setup-python@" in content:
            old_content = content
            content = re.sub(
                r"python-version:\s*['\"]?2\.[0-9]+['\"]?",
                f"python-version: '{self.min_python}'",
                content
            )
            if content != old_content:
                changes.append("Updated Python version in setup-python action")
        
        return content, changes
    
    def _update_gitlab_ci(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update GitLab CI configuration."""
        content = file_path.read_text()
        changes = []
        
        # Update image versions
        if 'python:2' in content:
            content = re.sub(
                r'image:\s*python:2[^\s]*',
                f'image: python:{self.min_python}',
                content
            )
            changes.append(f"Updated Docker image to python:{self.min_python}")
        
        # Update Python version variables
        if 'PYTHON_VERSION' in content:
            content = re.sub(
                r'PYTHON_VERSION:\s*["\']?2\.[0-9]+["\']?',
                f'PYTHON_VERSION: "{self.min_python}"',
                content
            )
            changes.append("Updated PYTHON_VERSION variable")
        
        return content, changes
    
    def _update_travis_ci(self, file_path: Path) -> Tuple[str, List[str]]:
        """Update Travis CI configuration."""
        content = file_path.read_text()
        changes = []
        
        # Update Python version list
        if 'python:' in content:
            # Find the python version section
            lines = content.split('\n')
            new_lines = []
            in_python_section = False
            python_section_indent = 0
            
            for line in lines:
                if line.strip().startswith('python:'):
                    new_lines.append(line)
                    in_python_section = True
                    python_section_indent = len(line) - len(line.lstrip())
                elif in_python_section:
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent > python_section_indent and line.strip():
                        if '2.' in line:
                            # Skip Python 2 versions
                            continue
                    else:
                        in_python_section = False
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # Add Python 3 versions if we removed Python 2 versions
            if '2.' in content and new_lines != lines:
                min_ver = int(self.min_python.split('.')[1])
                max_ver = int(self.max_python.split('.')[1])
                
                # Find where to insert Python 3 versions
                for i, line in enumerate(new_lines):
                    if line.strip().startswith('python:'):
                        indent = ' ' * (python_section_indent + 2)
                        versions = [f'{indent}- "3.{v}"' for v in range(min_ver, max_ver + 1)]
                        new_lines = new_lines[:i+1] + versions + new_lines[i+1:]
                        break
                
                content = '\n'.join(new_lines)
                changes.append("Updated Python versions from 2.x to 3.x")
        
        return content, changes


def main():
    """Main entry point for the metadata updater."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update project metadata files for Python 3 compatibility"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project directory to update (default: current directory)"
    )
    parser.add_argument(
        "--min-version",
        default="3.6",
        help="Minimum Python 3 version to support (default: 3.6)"
    )
    parser.add_argument(
        "--max-version",
        default="3.12",
        help="Maximum Python 3 version to support (default: 3.12)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    updater = MetadataUpdater(args.project_dir, args.min_version, args.max_version)
    results = updater.update_all(dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'=' * 70}")
        print("Project Metadata Update Results")
        print(f"{'=' * 70}\n")
        
        if args.dry_run:
            print("DRY RUN MODE - No files were modified\n")
        
        if results["updated_files"]:
            print(f"✓ Updated {len(results['updated_files'])} file(s):")
            for item in results["updated_files"]:
                print(f"\n  📄 {item['file']}")
                for change in item['changes']:
                    print(f"     • {change}")
        
        if results["skipped_files"]:
            print(f"\n⊘ Skipped {len(results['skipped_files'])} file(s) (no changes needed):")
            for file in results["skipped_files"]:
                print(f"  • {file}")
        
        if results["errors"]:
            print(f"\n✗ Encountered {len(results['errors'])} error(s):")
            for error in results["errors"]:
                print(f"  • {error}")
        
        if not args.dry_run and results["updated_files"]:
            backup_dir = Path(args.project_dir) / ".metadata_backups"
            if backup_dir.exists():
                print(f"\n💾 Backups saved to: {backup_dir}")
        
        print()


if __name__ == "__main__":
    main()
