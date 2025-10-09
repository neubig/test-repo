#!/usr/bin/env python3
"""
Automated CHANGELOG Generator for Python 2 to 3 Migration

Generates comprehensive changelogs from migration activities including:
- Git commit history
- Migration journal entries
- Statistics and metrics
- Fixed files and patterns
- Breaking changes detection
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ChangelogGenerator:
    """Generate changelogs for Python 2 to 3 migration progress."""

    def __init__(self, project_root: str = "."):
        """
        Initialize the changelog generator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        self.journal_file = self.project_root / ".migration_journal.json"
        self.stats_dir = self.project_root / ".migration_stats"
        self.state_file = self.project_root / ".migration_state.json"

    def parse_journal_entries(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> List[Dict]:
        """
        Parse migration journal entries within a date range.

        Args:
            since: Start date (ISO format or relative like '7 days ago')
            until: End date (ISO format or relative like 'now')

        Returns:
            List of journal entries
        """
        if not self.journal_file.exists():
            return []

        try:
            with open(self.journal_file, "r") as f:
                journal_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

        entries = journal_data.get("entries", [])

        # Filter by date range if specified
        if since or until:
            filtered = []
            since_dt = self._parse_date(since) if since else datetime.datetime.min
            until_dt = self._parse_date(until) if until else datetime.datetime.max

            for entry in entries:
                entry_dt = datetime.datetime.fromisoformat(entry["timestamp"])
                if since_dt <= entry_dt <= until_dt:
                    filtered.append(entry)
            entries = filtered

        return entries

    def parse_git_commits(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> List[Dict]:
        """
        Parse git commits related to migration.

        Args:
            since: Start date for git log
            until: End date for git log

        Returns:
            List of commit information
        """
        if not (self.project_root / ".git").exists():
            return []

        cmd = ["git", "log", "--pretty=format:%H|%at|%an|%ae|%s|%b", "--no-merges"]

        if since:
            cmd.append(f"--since={since}")
        if until:
            cmd.append(f"--until={until}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|", 5)
                if len(parts) >= 5:
                    commits.append(
                        {
                            "hash": parts[0],
                            "timestamp": datetime.datetime.fromtimestamp(
                                int(parts[1])
                            ).isoformat(),
                            "author": parts[2],
                            "email": parts[3],
                            "subject": parts[4],
                            "body": parts[5] if len(parts) > 5 else "",
                        }
                    )

            return commits
        except Exception:
            return []

    def get_stats_snapshots(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> List[Dict]:
        """
        Get statistics snapshots within a date range.

        Args:
            since: Start date
            until: End date

        Returns:
            List of stats snapshots
        """
        if not self.stats_dir.exists():
            return []

        snapshots = []
        since_dt = self._parse_date(since) if since else datetime.datetime.min
        until_dt = self._parse_date(until) if until else datetime.datetime.max

        for stats_file in sorted(self.stats_dir.glob("stats_*.json")):
            try:
                with open(stats_file, "r") as f:
                    stats = json.load(f)

                snapshot_dt = datetime.datetime.fromisoformat(stats["timestamp"])
                if since_dt <= snapshot_dt <= until_dt:
                    snapshots.append(stats)
            except (json.JSONDecodeError, IOError, KeyError):
                continue

        return snapshots

    def categorize_changes(
        self, entries: List[Dict], commits: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Categorize changes by type.

        Args:
            entries: Journal entries
            commits: Git commits

        Returns:
            Dictionary of categorized changes
        """
        categories = defaultdict(list)

        # Categorize journal entries
        for entry in entries:
            category = entry.get("category", "general")
            description = entry.get("notes", entry.get("description", ""))
            if description:
                categories[category].append(description)

        # Categorize commits by analyzing commit messages
        for commit in commits:
            subject = commit["subject"].lower()
            description = f"{commit['subject']} ({commit['hash'][:7]})"

            if any(
                kw in subject
                for kw in ["print", "syntax", "exception", "class", "string"]
            ):
                categories["syntax"].append(description)
            elif any(kw in subject for kw in ["import", "module", "package"]):
                categories["imports"].append(description)
            elif any(kw in subject for kw in ["test", "coverage"]):
                categories["testing"].append(description)
            elif any(kw in subject for kw in ["doc", "comment", "readme"]):
                categories["documentation"].append(description)
            elif any(kw in subject for kw in ["fix", "bug", "issue"]):
                categories["fixes"].append(description)
            elif any(kw in subject for kw in ["feature", "add", "implement"]):
                categories["features"].append(description)
            else:
                categories["other"].append(description)

        return dict(categories)

    def detect_breaking_changes(self, entries: List[Dict]) -> List[str]:
        """
        Detect potential breaking changes from journal entries.

        Args:
            entries: Journal entries

        Returns:
            List of breaking changes
        """
        breaking_changes = []

        breaking_keywords = [
            "breaking",
            "incompatible",
            "removed",
            "deprecated",
            "behavior change",
        ]

        for entry in entries:
            notes = entry.get("notes", "").lower()
            if any(kw in notes for kw in breaking_keywords):
                breaking_changes.append(entry.get("notes", ""))

        return breaking_changes

    def calculate_metrics(
        self, snapshots: List[Dict]
    ) -> Tuple[Optional[int], Optional[int], Optional[float]]:
        """
        Calculate migration metrics from stats snapshots.

        Args:
            snapshots: Stats snapshots

        Returns:
            Tuple of (total_issues_fixed, files_modified, completion_percentage)
        """
        if not snapshots:
            return None, None, None

        first = snapshots[0]
        last = snapshots[-1]

        initial_issues = first.get("total_issues", 0)
        final_issues = last.get("total_issues", 0)
        issues_fixed = initial_issues - final_issues

        files_modified = last.get("files_processed", 0)

        completion = 0.0
        if initial_issues > 0:
            completion = ((initial_issues - final_issues) / initial_issues) * 100

        return issues_fixed, files_modified, completion

    def generate_markdown(
        self,
        categories: Dict[str, List[str]],
        breaking_changes: List[str],
        metrics: Tuple[Optional[int], Optional[int], Optional[float]],
        version: str = "Unreleased",
        date: Optional[str] = None,
        format_style: str = "keepachangelog",
    ) -> str:
        """
        Generate changelog in markdown format.

        Args:
            categories: Categorized changes
            breaking_changes: List of breaking changes
            metrics: Migration metrics
            version: Version string
            date: Release date
            format_style: Changelog format style

        Returns:
            Markdown formatted changelog
        """
        lines = []

        if format_style == "keepachangelog":
            lines.extend(self._generate_keepachangelog(
                categories, breaking_changes, metrics, version, date
            ))
        else:
            lines.extend(self._generate_simple_changelog(
                categories, breaking_changes, metrics, version, date
            ))

        return "\n".join(lines)

    def _generate_keepachangelog(
        self,
        categories: Dict[str, List[str]],
        breaking_changes: List[str],
        metrics: Tuple[Optional[int], Optional[int], Optional[float]],
        version: str,
        date: Optional[str],
    ) -> List[str]:
        """Generate changelog in 'Keep a Changelog' format."""
        lines = []

        date_str = date or datetime.date.today().isoformat()
        lines.append(f"## [{version}] - {date_str}")
        lines.append("")

        # Add metrics summary
        issues_fixed, files_modified, completion = metrics
        if any(m is not None for m in metrics):
            lines.append("### 📊 Migration Progress")
            lines.append("")
            if issues_fixed is not None:
                lines.append(f"- **Issues Fixed**: {issues_fixed}")
            if files_modified is not None:
                lines.append(f"- **Files Modified**: {files_modified}")
            if completion is not None:
                lines.append(f"- **Completion**: {completion:.1f}%")
            lines.append("")

        # Breaking changes section
        if breaking_changes:
            lines.append("### ⚠️ BREAKING CHANGES")
            lines.append("")
            for change in breaking_changes:
                lines.append(f"- {change}")
            lines.append("")

        # Category mapping to Keep a Changelog sections
        category_map = {
            "features": "Added",
            "fixes": "Fixed",
            "syntax": "Changed",
            "imports": "Changed",
            "documentation": "Changed",
            "testing": "Added",
            "deprecation": "Deprecated",
            "removal": "Removed",
        }

        # Group by Keep a Changelog sections
        sections = defaultdict(list)
        for category, items in categories.items():
            section = category_map.get(category, "Changed")
            sections[section].extend(items)

        # Output sections in standard order
        section_order = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
        for section in section_order:
            if section in sections:
                lines.append(f"### {section}")
                lines.append("")
                for item in sections[section]:
                    lines.append(f"- {item}")
                lines.append("")

        return lines

    def _generate_simple_changelog(
        self,
        categories: Dict[str, List[str]],
        breaking_changes: List[str],
        metrics: Tuple[Optional[int], Optional[int], Optional[float]],
        version: str,
        date: Optional[str],
    ) -> List[str]:
        """Generate changelog in simple format."""
        lines = []

        date_str = date or datetime.date.today().isoformat()
        lines.append(f"# {version} ({date_str})")
        lines.append("")

        # Add metrics
        issues_fixed, files_modified, completion = metrics
        if any(m is not None for m in metrics):
            lines.append("## Migration Metrics")
            lines.append("")
            if issues_fixed is not None:
                lines.append(f"- Issues Fixed: {issues_fixed}")
            if files_modified is not None:
                lines.append(f"- Files Modified: {files_modified}")
            if completion is not None:
                lines.append(f"- Completion: {completion:.1f}%")
            lines.append("")

        # Breaking changes
        if breaking_changes:
            lines.append("## ⚠️ Breaking Changes")
            lines.append("")
            for change in breaking_changes:
                lines.append(f"- {change}")
            lines.append("")

        # All categories
        for category, items in sorted(categories.items()):
            if items:
                lines.append(f"## {category.title()}")
                lines.append("")
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")

        return lines

    def generate_changelog(
        self,
        output_file: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        version: str = "Unreleased",
        format_style: str = "keepachangelog",
        append: bool = False,
    ) -> str:
        """
        Generate a complete changelog.

        Args:
            output_file: Output file path (None for stdout)
            since: Start date for changelog
            until: End date for changelog
            version: Version string
            format_style: Format style ('keepachangelog' or 'simple')
            append: Append to existing changelog

        Returns:
            Generated changelog content
        """
        # Gather data
        entries = self.parse_journal_entries(since, until)
        commits = self.parse_git_commits(since, until)
        snapshots = self.get_stats_snapshots(since, until)

        # Process data
        categories = self.categorize_changes(entries, commits)
        breaking_changes = self.detect_breaking_changes(entries)
        metrics = self.calculate_metrics(snapshots)

        # Generate markdown
        changelog = self.generate_markdown(
            categories, breaking_changes, metrics, version, until, format_style
        )

        # Output
        if output_file:
            mode = "a" if append else "w"
            with open(output_file, mode) as f:
                if append:
                    f.write("\n\n")
                f.write(changelog)
            return changelog
        else:
            print(changelog)
            return changelog

    def _parse_date(self, date_str: str) -> datetime.datetime:
        """
        Parse date string to datetime.

        Args:
            date_str: Date string (ISO format or 'now')

        Returns:
            Datetime object
        """
        if date_str == "now":
            return datetime.datetime.now()

        try:
            return datetime.datetime.fromisoformat(date_str)
        except ValueError:
            return datetime.datetime.now()


def main():
    """Main entry point for changelog generator."""
    parser = argparse.ArgumentParser(
        description="Generate changelog for Python 2 to 3 migration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate changelog for all time
  python changelog_generator.py

  # Generate changelog for last 30 days
  python changelog_generator.py --since "30 days ago"

  # Generate and save to file
  python changelog_generator.py -o CHANGELOG.md

  # Append to existing changelog
  python changelog_generator.py -o CHANGELOG.md --append --version "0.2.0"

  # Use simple format
  python changelog_generator.py --format simple
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file (default: stdout)",
    )

    parser.add_argument(
        "--since",
        help="Start date (ISO format or relative like '30 days ago')",
    )

    parser.add_argument(
        "--until",
        help="End date (ISO format or relative like 'now')",
    )

    parser.add_argument(
        "--version",
        default="Unreleased",
        help="Version string for the changelog entry (default: Unreleased)",
    )

    parser.add_argument(
        "--format",
        choices=["keepachangelog", "simple"],
        default="keepachangelog",
        help="Changelog format style (default: keepachangelog)",
    )

    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing changelog file",
    )

    args = parser.parse_args()

    generator = ChangelogGenerator(args.path)
    generator.generate_changelog(
        output_file=args.output,
        since=args.since,
        until=args.until,
        version=args.version,
        format_style=args.format,
        append=args.append,
    )


if __name__ == "__main__":
    main()
