#!/usr/bin/env python3
"""
Watch Mode for Python 2 to 3 Migration

Monitors Python files for changes and automatically runs compatibility checks.
Provides real-time feedback during the migration process.
"""

import os
import sys
import time
import threading
from pathlib import Path
from collections import defaultdict
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class MigrationWatchHandler(FileSystemEventHandler):
    """Handle file system events for Python files."""
    
    def __init__(self, callback, debounce_seconds=1.0):
        """Initialize the watch handler.
        
        Args:
            callback: Function to call when files change
            debounce_seconds: Seconds to wait before processing changes
        """
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.pending_files = set()
        self.timer = None
        self.lock = threading.Lock()
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        if event.src_path.endswith('.py'):
            with self.lock:
                self.pending_files.add(event.src_path)
                
                # Cancel existing timer
                if self.timer:
                    self.timer.cancel()
                
                # Start new timer
                self.timer = threading.Timer(
                    self.debounce_seconds,
                    self._process_pending
                )
                self.timer.start()
    
    def on_created(self, event):
        """Handle file creation events."""
        self.on_modified(event)
    
    def _process_pending(self):
        """Process pending file changes."""
        with self.lock:
            if self.pending_files:
                files = list(self.pending_files)
                self.pending_files.clear()
                self.callback(files)


class WatchMode:
    """Watch mode for continuous migration monitoring."""
    
    def __init__(self, watch_path, mode='check', config=None):
        """Initialize watch mode.
        
        Args:
            watch_path: Path to watch for changes
            mode: Watch mode - 'check', 'stats', or 'report'
            config: Optional configuration dictionary
        """
        self.watch_path = Path(watch_path).resolve()
        self.mode = mode
        self.config = config or {}
        self.stats = defaultdict(int)
        self.last_check_time = None
        self.observer = None
        
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError(
                "Watch mode requires the 'watchdog' package. "
                "Install it with: pip install watchdog"
            )
    
    def start(self):
        """Start watching for file changes."""
        print(f"\n{'='*70}")
        print(f"🔍 Watch Mode Started")
        print(f"{'='*70}")
        print(f"Path: {self.watch_path}")
        print(f"Mode: {self.mode}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nMonitoring Python files for changes...")
        print(f"Press Ctrl+C to stop\n")
        print(f"{'='*70}\n")
        
        # Do initial scan
        self._run_initial_scan()
        
        # Set up file watcher
        event_handler = MigrationWatchHandler(
            self._handle_file_changes,
            debounce_seconds=self.config.get('debounce_seconds', 1.0)
        )
        
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_path), recursive=True)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._stop()
    
    def _stop(self):
        """Stop watching."""
        print(f"\n{'='*70}")
        print("🛑 Watch Mode Stopped")
        print(f"{'='*70}")
        self._print_session_stats()
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def _run_initial_scan(self):
        """Run initial compatibility scan."""
        print("📊 Running initial scan...\n")
        
        try:
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            
            if self.watch_path.is_dir():
                verifier.verify_directory(str(self.watch_path))
            else:
                verifier.verify_file(str(self.watch_path))
            
            issues = verifier.issues_found
            
            # Analyze issues
            severity_counts = defaultdict(int)
            for issue in issues:
                severity = issue.get('severity', 'unknown')
                severity_counts[severity] += 1
            
            # Print summary
            print(f"Initial scan complete:")
            print(f"  Total issues: {len(issues)}")
            if severity_counts:
                for severity in ['error', 'warning', 'info']:
                    if severity in severity_counts:
                        print(f"  {severity.capitalize()}s: {severity_counts[severity]}")
            print()
            
            self.stats['initial_issues'] = len(issues)
            self.last_check_time = datetime.now()
            
        except Exception as e:
            print(f"❌ Error during initial scan: {e}\n")
    
    def _handle_file_changes(self, files):
        """Handle changed files.
        
        Args:
            files: List of file paths that changed
        """
        self.stats['checks_run'] += 1
        self.last_check_time = datetime.now()
        
        print(f"\n{'─'*70}")
        print(f"🔄 Change detected at {self.last_check_time.strftime('%H:%M:%S')}")
        print(f"{'─'*70}")
        
        for file_path in files:
            # Make path relative for display
            try:
                rel_path = Path(file_path).relative_to(Path.cwd())
            except ValueError:
                rel_path = Path(file_path)
            
            print(f"📝 Checking: {rel_path}")
            
            self._check_file(file_path)
        
        print(f"{'─'*70}\n")
    
    def _check_file(self, file_path):
        """Check a single file for compatibility issues.
        
        Args:
            file_path: Path to file to check
        """
        try:
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            verifier.verify_file(file_path)
            
            issues = verifier.issues_found
            
            if not issues:
                print(f"  ✅ No issues found")
                self.stats['clean_checks'] += 1
            else:
                print(f"  ⚠️  Found {len(issues)} issue(s):")
                
                # Group by severity
                by_severity = defaultdict(list)
                for issue in issues[:5]:  # Show first 5
                    severity = issue.get('severity', 'info')
                    by_severity[severity].append(issue)
                
                for severity in ['error', 'warning', 'info']:
                    if severity in by_severity:
                        for issue in by_severity[severity]:
                            line = issue.get('line', '?')
                            msg = issue.get('message', 'Unknown issue')
                            # Truncate long messages
                            if len(msg) > 60:
                                msg = msg[:57] + "..."
                            icon = self._get_severity_icon(severity)
                            print(f"     {icon} Line {line}: {msg}")
                
                if len(issues) > 5:
                    print(f"     ... and {len(issues) - 5} more issue(s)")
                
                self.stats['issues_found'] += len(issues)
                self.stats['files_with_issues'] += 1
            
            # Additional mode-specific actions
            if self.mode == 'stats':
                self._update_stats_file()
            elif self.mode == 'report':
                # Could trigger report generation here
                pass
                
        except Exception as e:
            print(f"  ❌ Error checking file: {e}")
            self.stats['errors'] += 1
    
    def _get_severity_icon(self, severity):
        """Get icon for severity level.
        
        Args:
            severity: Severity level
            
        Returns:
            str: Icon character
        """
        icons = {
            'error': '🔴',
            'warning': '🟡',
            'info': '🔵'
        }
        return icons.get(severity, '⚪')
    
    def _update_stats_file(self):
        """Update statistics file (for stats mode)."""
        try:
            from stats_tracker import MigrationStatsTracker
            
            tracker = MigrationStatsTracker(self.watch_path)
            stats = tracker.collect_stats(self.watch_path)
            tracker.save_snapshot(stats)
            
        except Exception as e:
            print(f"  ⚠️  Could not update stats: {e}")
    
    def _print_session_stats(self):
        """Print statistics for this watch session."""
        print("\n📈 Session Statistics:")
        print(f"  Checks run: {self.stats['checks_run']}")
        print(f"  Clean checks: {self.stats['clean_checks']}")
        print(f"  Files with issues: {self.stats['files_with_issues']}")
        print(f"  Total issues found: {self.stats['issues_found']}")
        if self.stats['errors'] > 0:
            print(f"  Errors: {self.stats['errors']}")
        
        if self.last_check_time:
            duration = (datetime.now() - self.last_check_time).total_seconds()
            print(f"  Last check: {int(duration)}s ago")
        
        print(f"{'='*70}\n")


def main():
    """Main entry point for watch mode."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Watch Python files and check for Python 3 compatibility"
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to watch (default: current directory)'
    )
    parser.add_argument(
        '-m', '--mode',
        choices=['check', 'stats', 'report'],
        default='check',
        help='Watch mode (default: check)'
    )
    parser.add_argument(
        '--debounce',
        type=float,
        default=1.0,
        help='Debounce delay in seconds (default: 1.0)'
    )
    
    args = parser.parse_args()
    
    if not WATCHDOG_AVAILABLE:
        print("❌ Error: Watch mode requires the 'watchdog' package")
        print("Install it with: pip install watchdog")
        sys.exit(1)
    
    config = {
        'debounce_seconds': args.debounce
    }
    
    try:
        watch = WatchMode(args.path, mode=args.mode, config=config)
        watch.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
