#!/usr/bin/env python3
"""
Git Integration Module for py2to3 Migration Toolkit

Provides seamless git integration for tracking migration progress,
creating checkpoints, and enabling easy rollback of changes.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GitIntegrationError(Exception):
    """Custom exception for git integration errors."""
    pass


class GitIntegration:
    """Manages git operations for Python 2 to 3 migration workflow."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize git integration.
        
        Args:
            repo_path: Path to the git repository (default: current directory)
        """
        self.repo_path = os.path.abspath(repo_path)
        self.migration_tag_prefix = "py2to3-migration"
        
    def _run_git_command(self, args: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Run a git command and return the result.
        
        Args:
            args: Git command arguments
            capture_output: Whether to capture output
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = ["git", "-C", self.repo_path] + args
        
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode, result.stdout.strip(), result.stderr.strip()
            else:
                result = subprocess.run(cmd, timeout=30)
                return result.returncode, "", ""
        except subprocess.TimeoutExpired:
            raise GitIntegrationError("Git command timed out")
        except FileNotFoundError:
            raise GitIntegrationError("Git is not installed or not in PATH")
        except Exception as e:
            raise GitIntegrationError(f"Failed to run git command: {e}")
    
    def is_git_repo(self) -> bool:
        """Check if the current directory is a git repository."""
        returncode, _, _ = self._run_git_command(["rev-parse", "--git-dir"])
        return returncode == 0
    
    def is_clean(self) -> bool:
        """Check if the working directory is clean (no uncommitted changes)."""
        returncode, stdout, _ = self._run_git_command(["status", "--porcelain"])
        return returncode == 0 and not stdout
    
    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current branch."""
        returncode, stdout, _ = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        if returncode == 0:
            return stdout
        return None
    
    def get_status(self) -> Dict[str, List[str]]:
        """
        Get the status of the repository.
        
        Returns:
            Dictionary with lists of modified, added, deleted, and untracked files
        """
        returncode, stdout, _ = self._run_git_command(["status", "--porcelain"])
        
        if returncode != 0:
            raise GitIntegrationError("Failed to get git status")
        
        status = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": []
        }
        
        for line in stdout.split('\n'):
            if not line:
                continue
            
            status_code = line[:2]
            filename = line[3:].strip()
            
            if status_code.strip() == 'M':
                status["modified"].append(filename)
            elif status_code.strip() == 'A':
                status["added"].append(filename)
            elif status_code.strip() == 'D':
                status["deleted"].append(filename)
            elif status_code.strip() == '??':
                status["untracked"].append(filename)
        
        return status
    
    def create_migration_branch(self, branch_name: Optional[str] = None) -> str:
        """
        Create a new branch for the migration.
        
        Args:
            branch_name: Name of the branch (default: py2to3-migration-TIMESTAMP)
            
        Returns:
            Name of the created branch
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        if branch_name is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            branch_name = f"{self.migration_tag_prefix}-{timestamp}"
        
        returncode, _, stderr = self._run_git_command(["checkout", "-b", branch_name])
        
        if returncode != 0:
            raise GitIntegrationError(f"Failed to create branch: {stderr}")
        
        return branch_name
    
    def create_checkpoint(self, message: str, tag: Optional[str] = None) -> str:
        """
        Create a git commit checkpoint.
        
        Args:
            message: Commit message
            tag: Optional tag name for the checkpoint
            
        Returns:
            Commit hash
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        # Stage all changes
        returncode, _, stderr = self._run_git_command(["add", "-A"])
        if returncode != 0:
            raise GitIntegrationError(f"Failed to stage changes: {stderr}")
        
        # Create commit
        returncode, stdout, stderr = self._run_git_command(["commit", "-m", message])
        if returncode != 0:
            # Check if there were no changes to commit
            if "nothing to commit" in stderr or "nothing to commit" in stdout:
                raise GitIntegrationError("No changes to commit")
            raise GitIntegrationError(f"Failed to create commit: {stderr}")
        
        # Get commit hash
        returncode, commit_hash, _ = self._run_git_command(["rev-parse", "HEAD"])
        if returncode != 0:
            raise GitIntegrationError("Failed to get commit hash")
        
        # Create tag if requested
        if tag:
            tag_name = f"{self.migration_tag_prefix}-{tag}"
            returncode, _, stderr = self._run_git_command(["tag", "-a", tag_name, "-m", message])
            if returncode != 0:
                print(f"Warning: Failed to create tag: {stderr}", file=sys.stderr)
        
        return commit_hash
    
    def create_migration_commit(
        self,
        phase: str,
        stats: Optional[Dict] = None,
        additional_info: Optional[str] = None
    ) -> str:
        """
        Create a commit for a migration phase with detailed message.
        
        Args:
            phase: Migration phase (e.g., "pre-migration", "fixes-applied", "verified")
            stats: Dictionary with migration statistics
            additional_info: Additional information to include in commit message
            
        Returns:
            Commit hash
        """
        # Build commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_lines = [
            f"py2to3: {phase}",
            "",
            f"Migration phase: {phase}",
            f"Timestamp: {timestamp}",
        ]
        
        # Add statistics if provided
        if stats:
            message_lines.append("")
            message_lines.append("Statistics:")
            for key, value in stats.items():
                message_lines.append(f"  - {key}: {value}")
        
        # Add additional info if provided
        if additional_info:
            message_lines.append("")
            message_lines.append(additional_info)
        
        # Add migration tracking footer
        message_lines.extend([
            "",
            "---",
            "Generated by py2to3 migration toolkit",
        ])
        
        commit_message = "\n".join(message_lines)
        
        return self.create_checkpoint(commit_message, tag=phase)
    
    def get_migration_commits(self) -> List[Dict]:
        """
        Get list of all migration commits.
        
        Returns:
            List of dictionaries with commit information
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        # Get commits with py2to3 prefix
        returncode, stdout, _ = self._run_git_command([
            "log",
            "--grep=^py2to3:",
            "--pretty=format:%H|%s|%ai",
            "--all"
        ])
        
        if returncode != 0:
            return []
        
        commits = []
        for line in stdout.split('\n'):
            if not line:
                continue
            
            parts = line.split('|', 2)
            if len(parts) == 3:
                commits.append({
                    "hash": parts[0],
                    "message": parts[1],
                    "date": parts[2]
                })
        
        return commits
    
    def rollback_to_commit(self, commit_hash: str, hard: bool = False) -> bool:
        """
        Rollback to a specific commit.
        
        Args:
            commit_hash: Commit hash to rollback to
            hard: Whether to do a hard reset (discard changes)
            
        Returns:
            True if successful
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        reset_type = "--hard" if hard else "--mixed"
        returncode, _, stderr = self._run_git_command(["reset", reset_type, commit_hash])
        
        if returncode != 0:
            raise GitIntegrationError(f"Failed to rollback: {stderr}")
        
        return True
    
    def get_diff(self, commit1: str = "HEAD", commit2: Optional[str] = None) -> str:
        """
        Get diff between commits or working directory.
        
        Args:
            commit1: First commit (default: HEAD)
            commit2: Second commit (default: working directory)
            
        Returns:
            Diff output
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        args = ["diff", commit1]
        if commit2:
            args.append(commit2)
        
        returncode, stdout, _ = self._run_git_command(args)
        
        if returncode != 0:
            raise GitIntegrationError("Failed to get diff")
        
        return stdout
    
    def get_changed_files(self, commit1: str = "HEAD", commit2: Optional[str] = None) -> List[str]:
        """
        Get list of changed files between commits.
        
        Args:
            commit1: First commit (default: HEAD)
            commit2: Second commit (default: working directory)
            
        Returns:
            List of changed file paths
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        args = ["diff", "--name-only", commit1]
        if commit2:
            args.append(commit2)
        
        returncode, stdout, _ = self._run_git_command(args)
        
        if returncode != 0:
            raise GitIntegrationError("Failed to get changed files")
        
        return [f for f in stdout.split('\n') if f]
    
    def init_repo(self) -> bool:
        """
        Initialize a new git repository.
        
        Returns:
            True if successful
        """
        if self.is_git_repo():
            raise GitIntegrationError("Already a git repository")
        
        returncode, _, stderr = self._run_git_command(["init"])
        
        if returncode != 0:
            raise GitIntegrationError(f"Failed to initialize repository: {stderr}")
        
        return True
    
    def add_files(self, patterns: List[str]) -> bool:
        """
        Stage files for commit.
        
        Args:
            patterns: List of file patterns to stage
            
        Returns:
            True if successful
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        for pattern in patterns:
            returncode, _, stderr = self._run_git_command(["add", pattern])
            if returncode != 0:
                raise GitIntegrationError(f"Failed to add files: {stderr}")
        
        return True
    
    def get_repo_info(self) -> Dict:
        """
        Get information about the repository.
        
        Returns:
            Dictionary with repository information
        """
        if not self.is_git_repo():
            raise GitIntegrationError("Not a git repository")
        
        info = {}
        
        # Get current branch
        info["branch"] = self.get_current_branch()
        
        # Get commit count
        returncode, stdout, _ = self._run_git_command(["rev-list", "--count", "HEAD"])
        info["commit_count"] = int(stdout) if returncode == 0 else 0
        
        # Get remote URL if available
        returncode, stdout, _ = self._run_git_command(["remote", "get-url", "origin"])
        info["remote_url"] = stdout if returncode == 0 else None
        
        # Get last commit info
        returncode, stdout, _ = self._run_git_command(["log", "-1", "--pretty=format:%H|%s|%ai"])
        if returncode == 0 and stdout:
            parts = stdout.split('|', 2)
            if len(parts) == 3:
                info["last_commit"] = {
                    "hash": parts[0],
                    "message": parts[1],
                    "date": parts[2]
                }
        
        # Check if clean
        info["is_clean"] = self.is_clean()
        
        return info


def format_commit_message(phase: str, stats: Dict) -> str:
    """
    Format a migration commit message.
    
    Args:
        phase: Migration phase
        stats: Statistics dictionary
        
    Returns:
        Formatted commit message
    """
    lines = [
        f"py2to3: {phase}",
        "",
        f"Migration phase: {phase}",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Statistics:",
    ]
    
    for key, value in stats.items():
        lines.append(f"  - {key}: {value}")
    
    lines.extend([
        "",
        "---",
        "Generated by py2to3 migration toolkit"
    ])
    
    return "\n".join(lines)
