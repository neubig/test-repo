#!/usr/bin/env python3
"""
Live Migration Monitor - Real-time terminal dashboard for migration progress

Provides a beautiful, auto-refreshing terminal interface showing real-time
migration statistics, progress, and activity. Perfect for keeping track of
long-running migrations.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.align import Align
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
except ImportError:
    print("Error: 'rich' library is required for live monitoring")
    print("Install it with: pip install rich")
    sys.exit(1)


class LiveMigrationMonitor:
    """Real-time terminal dashboard for migration monitoring."""
    
    def __init__(self, project_path: str, refresh_rate: int = 2):
        """Initialize the live monitor.
        
        Args:
            project_path: Path to the project being migrated
            refresh_rate: How often to refresh the display (seconds)
        """
        self.project_path = Path(project_path)
        self.refresh_rate = refresh_rate
        self.console = Console()
        self.start_time = datetime.now()
        
        # Paths for migration data
        self.state_file = self.project_path / '.migration_state.json'
        self.stats_dir = self.project_path / '.migration_stats'
        self.journal_file = self.project_path / '.migration_journal.json'
        
    def load_migration_data(self) -> Dict[str, Any]:
        """Load current migration data from various sources."""
        data = {
            'state': self._load_state(),
            'stats': self._load_latest_stats(),
            'journal': self._load_journal_entries(),
            'files': self._scan_project_files()
        }
        return data
    
    def _load_state(self) -> Dict[str, Any]:
        """Load migration state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'phase': 'Not Started',
            'files_migrated': 0,
            'files_total': 0,
            'issues_found': 0,
            'issues_fixed': 0
        }
    
    def _load_latest_stats(self) -> Dict[str, Any]:
        """Load the most recent statistics snapshot."""
        if not self.stats_dir.exists():
            return {}
        
        try:
            stat_files = sorted(self.stats_dir.glob('*.json'), reverse=True)
            if stat_files:
                with open(stat_files[0], 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _load_journal_entries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Load recent journal entries."""
        if not self.journal_file.exists():
            return []
        
        try:
            with open(self.journal_file, 'r') as f:
                journal = json.load(f)
                entries = journal.get('entries', [])
                return sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        except Exception:
            pass
        return []
    
    def _scan_project_files(self) -> Dict[str, Any]:
        """Scan project for Python files."""
        python_files = list(self.project_path.rglob('*.py'))
        # Filter out common excluded directories
        excluded = {'.venv', 'venv', '__pycache__', '.git', 'node_modules', 'env'}
        python_files = [f for f in python_files if not any(ex in f.parts for ex in excluded)]
        
        return {
            'total_files': len(python_files),
            'total_lines': sum(self._count_lines(f) for f in python_files)
        }
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len(f.readlines())
        except Exception:
            return 0
    
    def create_dashboard(self, data: Dict[str, Any]) -> Layout:
        """Create the dashboard layout."""
        layout = Layout()
        
        # Create main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into main and sidebar
        layout["body"].split_row(
            Layout(name="main"),
            Layout(name="sidebar", ratio=1)
        )
        
        # Split main into sections
        layout["main"].split_column(
            Layout(name="stats", size=10),
            Layout(name="activity")
        )
        
        # Populate sections
        layout["header"].update(self._create_header())
        layout["stats"].update(self._create_stats_panel(data))
        layout["sidebar"].update(self._create_issues_panel(data))
        layout["activity"].update(self._create_activity_panel(data))
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_header(self) -> Panel:
        """Create header panel."""
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]
        
        title = Text()
        title.append("🔴 ", style="bold red")
        title.append("LIVE MIGRATION MONITOR", style="bold white")
        title.append(f" │ Runtime: {elapsed_str}", style="dim")
        
        return Panel(
            Align.center(title),
            style="bold blue",
            box=box.DOUBLE
        )
    
    def _create_stats_panel(self, data: Dict[str, Any]) -> Panel:
        """Create statistics panel."""
        state = data.get('state', {})
        stats = data.get('stats', {})
        files = data.get('files', {})
        
        # Calculate metrics
        files_total = files.get('total_files', 0)
        files_migrated = state.get('files_migrated', 0)
        issues_total = state.get('issues_found', 0) + stats.get('total_issues', 0)
        issues_fixed = state.get('issues_fixed', 0) + stats.get('issues_fixed', 0)
        
        # Calculate progress percentages
        file_progress = (files_migrated / files_total * 100) if files_total > 0 else 0
        issue_progress = (issues_fixed / issues_total * 100) if issues_total > 0 else 0
        
        # Create stats table
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", justify="right", style="bold white", width=15)
        table.add_column("Progress", width=30)
        
        # Add rows
        table.add_row(
            "📁 Files",
            f"{files_migrated}/{files_total}",
            self._create_progress_bar(file_progress)
        )
        
        table.add_row(
            "🐛 Issues",
            f"{issues_fixed}/{issues_total}",
            self._create_progress_bar(issue_progress, "red", "green")
        )
        
        table.add_row(
            "📝 Total Lines",
            f"{files.get('total_lines', 0):,}",
            ""
        )
        
        table.add_row(
            "🎯 Phase",
            state.get('phase', 'Not Started'),
            ""
        )
        
        # Add issue breakdown if available
        if stats:
            high = stats.get('issues_by_severity', {}).get('high', 0)
            medium = stats.get('issues_by_severity', {}).get('medium', 0)
            low = stats.get('issues_by_severity', {}).get('low', 0)
            
            severity_text = Text()
            if high > 0:
                severity_text.append(f"🔴 {high} ", style="red")
            if medium > 0:
                severity_text.append(f"🟡 {medium} ", style="yellow")
            if low > 0:
                severity_text.append(f"🟢 {low}", style="green")
            
            if severity_text.plain:
                table.add_row(
                    "⚠️  By Severity",
                    "",
                    severity_text
                )
        
        return Panel(
            table,
            title="[bold white]📊 Migration Statistics[/bold white]",
            border_style="green",
            box=box.ROUNDED
        )
    
    def _create_progress_bar(self, percentage: float, 
                            color_start: str = "red", 
                            color_end: str = "green") -> Text:
        """Create a text-based progress bar."""
        width = 20
        filled = int(width * percentage / 100)
        empty = width - filled
        
        # Choose color based on progress
        if percentage < 33:
            color = "red"
        elif percentage < 66:
            color = "yellow"
        else:
            color = "green"
        
        bar = Text()
        bar.append("█" * filled, style=f"bold {color}")
        bar.append("░" * empty, style="dim white")
        bar.append(f" {percentage:.1f}%", style="white")
        
        return bar
    
    def _create_issues_panel(self, data: Dict[str, Any]) -> Panel:
        """Create issues breakdown panel."""
        stats = data.get('stats', {})
        
        if not stats or 'issues_by_category' not in stats:
            return Panel(
                Align.center("[dim]No issue data available[/dim]"),
                title="[bold white]🎯 Top Issues[/bold white]",
                border_style="yellow",
                box=box.ROUNDED
            )
        
        issues_by_cat = stats.get('issues_by_category', {})
        
        # Sort by count and take top 8
        sorted_issues = sorted(issues_by_cat.items(), key=lambda x: x[1], reverse=True)[:8]
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Issue", style="white", width=18)
        table.add_column("Count", justify="right", style="bold cyan", width=6)
        
        for category, count in sorted_issues:
            # Shorten category name if needed
            cat_display = category.replace('_', ' ').title()
            if len(cat_display) > 18:
                cat_display = cat_display[:15] + "..."
            table.add_row(cat_display, str(count))
        
        return Panel(
            table,
            title="[bold white]🎯 Top Issues[/bold white]",
            border_style="yellow",
            box=box.ROUNDED
        )
    
    def _create_activity_panel(self, data: Dict[str, Any]) -> Panel:
        """Create recent activity panel."""
        journal = data.get('journal', [])
        
        if not journal:
            return Panel(
                Align.center("[dim]No recent activity[/dim]"),
                title="[bold white]📋 Recent Activity[/bold white]",
                border_style="blue",
                box=box.ROUNDED
            )
        
        table = Table(show_header=True, box=box.SIMPLE_HEAD, padding=(0, 1))
        table.add_column("Time", style="dim", width=10)
        table.add_column("Action", style="cyan", width=15)
        table.add_column("Details", style="white")
        
        for entry in journal:
            timestamp = entry.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%H:%M:%S")
                except Exception:
                    time_str = timestamp[:10]
            else:
                time_str = "Unknown"
            
            action = entry.get('action', 'Unknown')
            details = entry.get('details', '')
            
            # Truncate details if too long
            if len(details) > 60:
                details = details[:57] + "..."
            
            table.add_row(time_str, action, details)
        
        return Panel(
            table,
            title="[bold white]📋 Recent Activity[/bold white]",
            border_style="blue",
            box=box.ROUNDED
        )
    
    def _create_footer(self) -> Panel:
        """Create footer panel."""
        text = Text()
        text.append("Press ", style="dim")
        text.append("Ctrl+C", style="bold red")
        text.append(" to exit", style="dim")
        text.append(" │ ", style="dim")
        text.append("Refreshing every ", style="dim")
        text.append(f"{self.refresh_rate}s", style="bold cyan")
        
        return Panel(
            Align.center(text),
            style="dim",
            box=box.ROUNDED
        )
    
    def run(self):
        """Run the live monitoring dashboard."""
        self.console.clear()
        
        try:
            with Live(
                self.create_dashboard(self.load_migration_data()),
                console=self.console,
                refresh_per_second=1,
                screen=True
            ) as live:
                self.console.print(
                    "[bold green]Live Migration Monitor Started![/bold green]\n"
                    f"Monitoring: [cyan]{self.project_path}[/cyan]\n"
                    f"Refresh rate: [cyan]{self.refresh_rate}s[/cyan]\n"
                )
                
                try:
                    while True:
                        time.sleep(self.refresh_rate)
                        data = self.load_migration_data()
                        live.update(self.create_dashboard(data))
                except KeyboardInterrupt:
                    pass
        except KeyboardInterrupt:
            pass
        finally:
            self.console.clear()
            self.console.print("\n[bold green]✓[/bold green] Monitor stopped\n")


def main():
    """Command-line entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Live terminal dashboard for migration monitoring"
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path to monitor (default: current directory)'
    )
    parser.add_argument(
        '-r', '--refresh',
        type=int,
        default=2,
        help='Refresh rate in seconds (default: 2)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    monitor = LiveMigrationMonitor(args.path, args.refresh)
    monitor.run()


if __name__ == '__main__':
    main()
