#!/usr/bin/env python3
"""
Pull Request Generator for Python 2 to 3 Migration

Automatically generates pull requests with rich descriptions, migration statistics,
code comparisons, and reviewer suggestions based on code ownership.
"""

import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import re


class PRGeneratorError(Exception):
    """Custom exception for PR generator errors."""
    pass


class PRGenerator:
    """Generates pull requests for Python 2 to 3 migration changes."""
    
    # Issue types and their descriptions
    ISSUE_DESCRIPTIONS = {
        'print_statement': 'Convert print statements to print functions',
        'import_change': 'Update Python 3 compatible imports',
        'exception_syntax': 'Modernize exception handling syntax',
        'iterator_method': 'Update iterator methods (iteritems, itervalues, etc.)',
        'string_type': 'Fix string type compatibility issues',
        'division_operator': 'Update division operator behavior',
        'dict_method': 'Update dictionary methods',
        'xrange': 'Replace xrange with range',
        'unicode': 'Fix unicode type compatibility',
        'basestring': 'Replace basestring with str',
        'long_type': 'Remove long type references',
        'raw_input': 'Replace raw_input with input',
        'has_key': 'Replace has_key with in operator',
        'execfile': 'Replace execfile with exec',
        'cmp_function': 'Replace cmp function',
        '__cmp__': 'Remove __cmp__ method',
        'apply_function': 'Replace apply function',
        'buffer_type': 'Update buffer type usage',
        'file_type': 'Update file type usage',
        'reduce_import': 'Update reduce import',
        'metaclass': 'Update metaclass syntax',
        'oldstyle_class': 'Convert old-style classes',
    }
    
    def __init__(self, repo_path: str = ".", github_token: Optional[str] = None):
        """
        Initialize PR generator.
        
        Args:
            repo_path: Path to the git repository
            github_token: GitHub personal access token (optional, for automatic PR creation)
        """
        self.repo_path = os.path.abspath(repo_path)
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN')
        self.stats_file = os.path.join(self.repo_path, '.py2to3', 'stats.json')
        self.journal_file = os.path.join(self.repo_path, '.py2to3', 'migration_journal.json')
        
    def _run_git_command(self, args: List[str]) -> Tuple[int, str, str]:
        """Run a git command and return the result."""
        cmd = ["git", "-C", self.repo_path] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            raise PRGeneratorError("Git command timed out")
        except FileNotFoundError:
            raise PRGeneratorError("Git is not installed or not in PATH")
        except Exception as e:
            raise PRGeneratorError(f"Failed to run git command: {e}")
    
    def get_changed_files(self, base_branch: str = "main") -> List[str]:
        """Get list of files changed in current branch compared to base branch."""
        returncode, stdout, stderr = self._run_git_command([
            "diff", "--name-only", f"{base_branch}...HEAD"
        ])
        
        if returncode != 0:
            # Try 'master' if 'main' fails
            if base_branch == "main":
                return self.get_changed_files("master")
            raise PRGeneratorError(f"Failed to get changed files: {stderr}")
        
        return [f for f in stdout.split('\n') if f and f.endswith('.py')]
    
    def get_file_authors(self, filepath: str, limit: int = 3) -> List[str]:
        """Get the main authors of a file using git blame."""
        returncode, stdout, stderr = self._run_git_command([
            "log", "--format=%ae", "--", filepath
        ])
        
        if returncode != 0:
            return []
        
        # Count author contributions
        authors = stdout.split('\n')
        author_counts = defaultdict(int)
        for author in authors:
            if author:
                author_counts[author] += 1
        
        # Return top contributors
        sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        return [author for author, _ in sorted_authors[:limit]]
    
    def analyze_changes(self, files: List[str]) -> Dict:
        """Analyze the migration changes in the given files."""
        analysis = {
            'total_files': len(files),
            'files_by_module': defaultdict(list),
            'changes_by_type': defaultdict(int),
            'files': [],
            'suggested_reviewers': set(),
        }
        
        for filepath in files:
            # Group by module (top-level directory or package)
            parts = Path(filepath).parts
            module = parts[0] if len(parts) > 1 else 'root'
            analysis['files_by_module'][module].append(filepath)
            
            # Get file authors for reviewer suggestions
            authors = self.get_file_authors(filepath)
            analysis['suggested_reviewers'].update(authors)
            
            # Get file diff to analyze changes
            returncode, stdout, _ = self._run_git_command([
                "diff", "HEAD~1", "HEAD", "--", filepath
            ])
            
            if returncode == 0:
                # Analyze diff for migration patterns
                changes = self._analyze_diff(stdout)
                for change_type, count in changes.items():
                    analysis['changes_by_type'][change_type] += count
                
                analysis['files'].append({
                    'path': filepath,
                    'module': module,
                    'authors': authors,
                    'changes': changes,
                    'lines_added': stdout.count('\n+'),
                    'lines_removed': stdout.count('\n-'),
                })
        
        return analysis
    
    def _analyze_diff(self, diff_text: str) -> Dict[str, int]:
        """Analyze a diff to detect migration patterns."""
        changes = defaultdict(int)
        
        patterns = {
            'print_statement': [
                r'[-].*\bprint\s+["\']',
                r'[+].*\bprint\(["\']',
            ],
            'import_change': [
                r'[-].*\bimport\s+(urllib2|ConfigParser|Queue|__builtin__|httplib)',
                r'[+].*\bimport\s+(urllib\.request|configparser|queue|builtins|http\.client)',
            ],
            'exception_syntax': [
                r'[-].*except\s+\w+\s*,\s*\w+',
                r'[+].*except\s+\w+\s+as\s+\w+',
            ],
            'iterator_method': [
                r'[-].*\.(iteritems|itervalues|iterkeys)\(',
                r'[+].*\.(items|values|keys)\(',
            ],
            'string_type': [
                r'[-].*\bbasestring\b',
                r'[+].*\bstr\b',
            ],
            'xrange': [
                r'[-].*\bxrange\(',
                r'[+].*\brange\(',
            ],
        }
        
        for change_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, diff_text)
                if matches:
                    changes[change_type] += len(matches)
        
        return changes
    
    def load_migration_stats(self) -> Optional[Dict]:
        """Load migration statistics from stats file."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load stats: {e}", file=sys.stderr)
        return None
    
    def generate_pr_description(
        self,
        title: str,
        analysis: Dict,
        base_branch: str = "main",
        include_stats: bool = True,
        include_checklist: bool = True
    ) -> str:
        """Generate a comprehensive PR description."""
        lines = []
        
        # Title and overview
        lines.append(f"# {title}\n")
        lines.append("## 🚀 Overview\n")
        lines.append("This pull request contains automated Python 2 to Python 3 migration changes ")
        lines.append("generated by the py2to3 migration toolkit.\n")
        
        # Statistics
        if include_stats:
            lines.append("\n## 📊 Migration Statistics\n")
            lines.append(f"- **Files Modified**: {analysis['total_files']}")
            
            total_changes = sum(analysis['changes_by_type'].values())
            lines.append(f"- **Total Changes**: {total_changes}")
            
            if analysis['changes_by_type']:
                lines.append("\n### Changes by Type\n")
                for change_type, count in sorted(
                    analysis['changes_by_type'].items(),
                    key=lambda x: x[1],
                    reverse=True
                ):
                    desc = self.ISSUE_DESCRIPTIONS.get(change_type, change_type.replace('_', ' ').title())
                    lines.append(f"- **{desc}**: {count}")
        
        # Files by module
        if analysis['files_by_module']:
            lines.append("\n## 📁 Modified Files by Module\n")
            for module, files in sorted(analysis['files_by_module'].items()):
                lines.append(f"\n### {module} ({len(files)} files)")
                for filepath in sorted(files):
                    lines.append(f"- `{filepath}`")
        
        # Testing checklist
        if include_checklist:
            lines.append("\n## ✅ Testing Checklist\n")
            lines.append("- [ ] All unit tests pass")
            lines.append("- [ ] Manual testing completed for modified functionality")
            lines.append("- [ ] No Python 2 syntax remains (verified with linter)")
            lines.append("- [ ] Import statements are correct and working")
            lines.append("- [ ] String handling works as expected")
            lines.append("- [ ] Exception handling works correctly")
            lines.append("- [ ] Performance is acceptable")
        
        # Review notes
        lines.append("\n## 👀 Review Notes\n")
        lines.append("Please review the following aspects:\n")
        lines.append("1. **Automated Changes**: Most changes are automated conversions that are safe")
        lines.append("2. **String Handling**: Pay attention to unicode/bytes conversions")
        lines.append("3. **Iterator Changes**: Verify that iterator changes don't affect performance")
        lines.append("4. **Import Changes**: Ensure all imports are correct and working")
        
        # Suggested reviewers
        if analysis['suggested_reviewers']:
            lines.append("\n## 👥 Suggested Reviewers\n")
            lines.append("Based on code ownership analysis:\n")
            for reviewer in sorted(analysis['suggested_reviewers'])[:5]:
                lines.append(f"- @{reviewer.split('@')[0]}")
        
        # Footer
        lines.append("\n---")
        lines.append("\n*Generated by [py2to3 Migration Toolkit](https://github.com/yourusername/test-repo)*")
        lines.append(f"\n*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return '\n'.join(lines)
    
    def generate_pr_title(self, analysis: Dict, prefix: str = "migration") -> str:
        """Generate a descriptive PR title."""
        if len(analysis['files_by_module']) == 1:
            module = list(analysis['files_by_module'].keys())[0]
            return f"Python 3 Migration: {module} module ({analysis['total_files']} files)"
        else:
            modules = ', '.join(sorted(analysis['files_by_module'].keys())[:3])
            return f"Python 3 Migration: {modules} ({analysis['total_files']} files)"
    
    def create_pr_draft(
        self,
        output_file: str,
        base_branch: str = "main",
        title: Optional[str] = None,
    ) -> str:
        """Create a draft PR description file."""
        # Get changed files
        changed_files = self.get_changed_files(base_branch)
        
        if not changed_files:
            raise PRGeneratorError("No changed Python files found")
        
        # Analyze changes
        analysis = self.analyze_changes(changed_files)
        
        # Generate title and description
        pr_title = title or self.generate_pr_title(analysis)
        pr_description = self.generate_pr_description(pr_title, analysis, base_branch)
        
        # Write to file
        output_path = os.path.join(self.repo_path, output_file)
        with open(output_path, 'w') as f:
            f.write(f"TITLE: {pr_title}\n")
            f.write("=" * 80 + "\n\n")
            f.write(pr_description)
        
        return output_path
    
    def get_github_repo_info(self) -> Optional[Tuple[str, str]]:
        """Extract GitHub owner and repo name from git remote."""
        returncode, stdout, _ = self._run_git_command([
            "config", "--get", "remote.origin.url"
        ])
        
        if returncode != 0:
            return None
        
        # Parse GitHub URL (both HTTPS and SSH formats)
        url = stdout
        
        # HTTPS format: https://github.com/owner/repo.git
        https_pattern = r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$'
        https_match = re.match(https_pattern, url)
        if https_match:
            return https_match.group(1), https_match.group(2)
        
        # SSH format: git@github.com:owner/repo.git
        ssh_pattern = r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'
        ssh_match = re.match(ssh_pattern, url)
        if ssh_match:
            return ssh_match.group(1), ssh_match.group(2)
        
        return None
    
    def create_github_pr(
        self,
        base_branch: str = "main",
        title: Optional[str] = None,
        draft: bool = False,
        labels: Optional[List[str]] = None,
    ) -> Dict:
        """
        Create a pull request on GitHub using the GitHub API.
        
        Requires GITHUB_TOKEN environment variable or github_token parameter.
        """
        if not self.github_token:
            raise PRGeneratorError(
                "GitHub token not found. Set GITHUB_TOKEN environment variable or pass github_token parameter."
            )
        
        # Get repository information
        repo_info = self.get_github_repo_info()
        if not repo_info:
            raise PRGeneratorError("Could not determine GitHub repository from git remote")
        
        owner, repo = repo_info
        
        # Get current branch
        returncode, current_branch, _ = self._run_git_command([
            "rev-parse", "--abbrev-ref", "HEAD"
        ])
        
        if returncode != 0 or current_branch == base_branch:
            raise PRGeneratorError(
                f"Must be on a feature branch (current: {current_branch})"
            )
        
        # Get changed files and analyze
        changed_files = self.get_changed_files(base_branch)
        if not changed_files:
            raise PRGeneratorError("No changed Python files found")
        
        analysis = self.analyze_changes(changed_files)
        
        # Generate PR content
        pr_title = title or self.generate_pr_title(analysis)
        pr_body = self.generate_pr_description(pr_title, analysis, base_branch)
        
        # Prepare API request
        try:
            import requests
        except ImportError:
            raise PRGeneratorError(
                "requests library not found. Install with: pip install requests"
            )
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        data = {
            "title": pr_title,
            "body": pr_body,
            "head": current_branch,
            "base": base_branch,
            "draft": draft,
        }
        
        response = requests.post(api_url, json=data, headers=headers)
        
        if response.status_code == 201:
            pr_data = response.json()
            
            # Add labels if specified
            if labels:
                labels_url = f"{api_url}/{pr_data['number']}/labels"
                requests.post(labels_url, json={"labels": labels}, headers=headers)
            
            return {
                'success': True,
                'pr_number': pr_data['number'],
                'pr_url': pr_data['html_url'],
                'title': pr_title,
            }
        else:
            raise PRGeneratorError(
                f"Failed to create PR: {response.status_code} - {response.text}"
            )


def main():
    """Command-line interface for PR generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate pull requests for Python 2 to 3 migration"
    )
    parser.add_argument(
        '--base-branch',
        default='main',
        help='Base branch for PR (default: main)'
    )
    parser.add_argument(
        '--title',
        help='Custom PR title'
    )
    parser.add_argument(
        '--draft',
        action='store_true',
        help='Create as draft PR'
    )
    parser.add_argument(
        '--labels',
        nargs='+',
        help='Labels to add to PR'
    )
    parser.add_argument(
        '--create',
        action='store_true',
        help='Create PR on GitHub (requires GITHUB_TOKEN)'
    )
    parser.add_argument(
        '--output',
        default='PR_DRAFT.md',
        help='Output file for PR draft (default: PR_DRAFT.md)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = PRGenerator()
        
        if args.create:
            print("Creating pull request on GitHub...")
            result = generator.create_github_pr(
                base_branch=args.base_branch,
                title=args.title,
                draft=args.draft,
                labels=args.labels,
            )
            print(f"\n✅ Pull request created successfully!")
            print(f"   PR #{result['pr_number']}: {result['title']}")
            print(f"   URL: {result['pr_url']}")
        else:
            print("Generating pull request draft...")
            output_path = generator.create_pr_draft(
                output_file=args.output,
                base_branch=args.base_branch,
                title=args.title,
            )
            print(f"\n✅ PR draft generated: {output_path}")
            print(f"\nTo create the PR on GitHub, run with --create flag")
            print(f"Make sure GITHUB_TOKEN is set in your environment")
    
    except PRGeneratorError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
