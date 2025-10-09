#!/usr/bin/env python3
"""
Migration Session Manager

Track migration work sessions, time spent, and developer productivity.
Helps teams understand migration velocity and plan work more effectively.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class SessionManager:
    """Manages migration work sessions with time tracking and notes."""
    
    def __init__(self, session_dir: str = ".py2to3"):
        """Initialize the session manager.
        
        Args:
            session_dir: Directory to store session data
        """
        self.session_dir = Path(session_dir)
        self.session_file = self.session_dir / "sessions.json"
        self.active_session_file = self.session_dir / "active_session.json"
        self._ensure_session_dir()
    
    def _ensure_session_dir(self):
        """Create session directory if it doesn't exist."""
        self.session_dir.mkdir(exist_ok=True)
    
    def _load_sessions(self) -> List[Dict]:
        """Load all sessions from file."""
        if not self.session_file.exists():
            return []
        
        try:
            with open(self.session_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def _save_sessions(self, sessions: List[Dict]):
        """Save sessions to file."""
        with open(self.session_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def _load_active_session(self) -> Optional[Dict]:
        """Load the currently active session."""
        if not self.active_session_file.exists():
            return None
        
        try:
            with open(self.active_session_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    
    def _save_active_session(self, session: Optional[Dict]):
        """Save the active session."""
        if session is None:
            if self.active_session_file.exists():
                self.active_session_file.unlink()
        else:
            with open(self.active_session_file, 'w') as f:
                json.dump(session, f, indent=2)
    
    def start_session(self, developer: str = None, description: str = None) -> Dict:
        """Start a new migration session.
        
        Args:
            developer: Name of the developer (defaults to system username)
            description: Optional description of what will be worked on
            
        Returns:
            The created session
        """
        active = self._load_active_session()
        if active:
            raise ValueError(f"Session already active (ID: {active['id']}). Please end it first.")
        
        if developer is None:
            developer = os.getenv('USER', 'unknown')
        
        session = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'developer': developer,
            'description': description or '',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'files_modified': [],
            'notes': [],
            'tasks_completed': [],
            'breaks': [],
            'status': 'active'
        }
        
        self._save_active_session(session)
        return session
    
    def end_session(self, summary: str = None) -> Dict:
        """End the current active session.
        
        Args:
            summary: Optional summary of work completed
            
        Returns:
            The completed session
        """
        active = self._load_active_session()
        if not active:
            raise ValueError("No active session to end")
        
        # Calculate duration
        start = datetime.fromisoformat(active['start_time'])
        end = datetime.now()
        
        # Subtract break time
        break_time = sum(b.get('duration_seconds', 0) for b in active.get('breaks', []))
        duration = (end - start).total_seconds() - break_time
        
        active['end_time'] = end.isoformat()
        active['duration_seconds'] = int(duration)
        active['status'] = 'completed'
        
        if summary:
            active['summary'] = summary
        
        # Save to sessions history
        sessions = self._load_sessions()
        sessions.append(active)
        self._save_sessions(sessions)
        
        # Clear active session
        self._save_active_session(None)
        
        return active
    
    def pause_session(self) -> Dict:
        """Pause the current session (start a break).
        
        Returns:
            The updated session
        """
        active = self._load_active_session()
        if not active:
            raise ValueError("No active session to pause")
        
        # Check if already paused
        breaks = active.get('breaks', [])
        if breaks and breaks[-1].get('end_time') is None:
            raise ValueError("Session is already paused")
        
        breaks.append({
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration_seconds': 0
        })
        
        active['breaks'] = breaks
        active['status'] = 'paused'
        self._save_active_session(active)
        
        return active
    
    def resume_session(self) -> Dict:
        """Resume a paused session (end the current break).
        
        Returns:
            The updated session
        """
        active = self._load_active_session()
        if not active:
            raise ValueError("No active session to resume")
        
        breaks = active.get('breaks', [])
        if not breaks or breaks[-1].get('end_time') is not None:
            raise ValueError("Session is not paused")
        
        # End the current break
        break_start = datetime.fromisoformat(breaks[-1]['start_time'])
        break_end = datetime.now()
        duration = (break_end - break_start).total_seconds()
        
        breaks[-1]['end_time'] = break_end.isoformat()
        breaks[-1]['duration_seconds'] = int(duration)
        
        active['breaks'] = breaks
        active['status'] = 'active'
        self._save_active_session(active)
        
        return active
    
    def add_note(self, note: str) -> Dict:
        """Add a note to the current session.
        
        Args:
            note: The note to add
            
        Returns:
            The updated session
        """
        active = self._load_active_session()
        if not active:
            raise ValueError("No active session")
        
        notes = active.get('notes', [])
        notes.append({
            'timestamp': datetime.now().isoformat(),
            'note': note
        })
        
        active['notes'] = notes
        self._save_active_session(active)
        
        return active
    
    def add_file(self, filepath: str) -> Dict:
        """Record a file being worked on in the current session.
        
        Args:
            filepath: Path to the file
            
        Returns:
            The updated session
        """
        active = self._load_active_session()
        if not active:
            raise ValueError("No active session")
        
        files = active.get('files_modified', [])
        if filepath not in files:
            files.append(filepath)
            active['files_modified'] = files
            self._save_active_session(active)
        
        return active
    
    def add_task(self, task: str) -> Dict:
        """Record a completed task in the current session.
        
        Args:
            task: Description of the completed task
            
        Returns:
            The updated session
        """
        active = self._load_active_session()
        if not active:
            raise ValueError("No active session")
        
        tasks = active.get('tasks_completed', [])
        tasks.append({
            'timestamp': datetime.now().isoformat(),
            'task': task
        })
        
        active['tasks_completed'] = tasks
        self._save_active_session(active)
        
        return active
    
    def get_active_session(self) -> Optional[Dict]:
        """Get the currently active session."""
        return self._load_active_session()
    
    def get_session_history(self, limit: int = None) -> List[Dict]:
        """Get session history.
        
        Args:
            limit: Maximum number of sessions to return (most recent first)
            
        Returns:
            List of completed sessions
        """
        sessions = self._load_sessions()
        sessions.reverse()  # Most recent first
        
        if limit:
            sessions = sessions[:limit]
        
        return sessions
    
    def get_statistics(self) -> Dict:
        """Calculate statistics across all sessions.
        
        Returns:
            Dictionary with various statistics
        """
        sessions = self._load_sessions()
        
        if not sessions:
            return {
                'total_sessions': 0,
                'total_time_seconds': 0,
                'total_time_formatted': '0h 0m',
                'average_session_seconds': 0,
                'average_session_formatted': '0h 0m',
                'total_files_modified': 0,
                'total_tasks_completed': 0,
                'total_notes': 0,
                'developers': [],
                'sessions_by_developer': {}
            }
        
        total_time = sum(s.get('duration_seconds', 0) for s in sessions)
        total_files = sum(len(s.get('files_modified', [])) for s in sessions)
        total_tasks = sum(len(s.get('tasks_completed', [])) for s in sessions)
        total_notes = sum(len(s.get('notes', [])) for s in sessions)
        
        developers = list(set(s.get('developer', 'unknown') for s in sessions))
        sessions_by_dev = {}
        for dev in developers:
            dev_sessions = [s for s in sessions if s.get('developer') == dev]
            dev_time = sum(s.get('duration_seconds', 0) for s in dev_sessions)
            sessions_by_dev[dev] = {
                'sessions': len(dev_sessions),
                'time_seconds': dev_time,
                'time_formatted': self._format_duration(dev_time)
            }
        
        avg_time = total_time // len(sessions) if sessions else 0
        
        return {
            'total_sessions': len(sessions),
            'total_time_seconds': total_time,
            'total_time_formatted': self._format_duration(total_time),
            'average_session_seconds': avg_time,
            'average_session_formatted': self._format_duration(avg_time),
            'total_files_modified': total_files,
            'total_tasks_completed': total_tasks,
            'total_notes': total_notes,
            'developers': developers,
            'sessions_by_developer': sessions_by_dev
        }
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate a detailed session report.
        
        Args:
            output_file: Optional file to write report to
            
        Returns:
            The report as a string
        """
        stats = self.get_statistics()
        sessions = self.get_session_history(limit=10)
        active = self.get_active_session()
        
        lines = []
        lines.append("=" * 70)
        lines.append("Migration Session Report")
        lines.append("=" * 70)
        lines.append("")
        
        # Overall statistics
        lines.append("Overall Statistics:")
        lines.append("-" * 70)
        lines.append(f"  Total Sessions: {stats['total_sessions']}")
        lines.append(f"  Total Time: {stats['total_time_formatted']}")
        lines.append(f"  Average Session: {stats['average_session_formatted']}")
        lines.append(f"  Files Modified: {stats['total_files_modified']}")
        lines.append(f"  Tasks Completed: {stats['total_tasks_completed']}")
        lines.append(f"  Notes Recorded: {stats['total_notes']}")
        lines.append("")
        
        # By developer
        if stats['developers']:
            lines.append("By Developer:")
            lines.append("-" * 70)
            for dev, dev_stats in stats['sessions_by_developer'].items():
                lines.append(f"  {dev}:")
                lines.append(f"    Sessions: {dev_stats['sessions']}")
                lines.append(f"    Time: {dev_stats['time_formatted']}")
            lines.append("")
        
        # Active session
        if active:
            lines.append("Active Session:")
            lines.append("-" * 70)
            lines.append(f"  ID: {active['id']}")
            lines.append(f"  Developer: {active['developer']}")
            lines.append(f"  Started: {active['start_time']}")
            lines.append(f"  Status: {active['status']}")
            if active.get('description'):
                lines.append(f"  Description: {active['description']}")
            if active.get('files_modified'):
                lines.append(f"  Files: {len(active['files_modified'])}")
            if active.get('tasks_completed'):
                lines.append(f"  Tasks: {len(active['tasks_completed'])}")
            lines.append("")
        
        # Recent sessions
        if sessions:
            lines.append("Recent Sessions (last 10):")
            lines.append("-" * 70)
            for session in sessions:
                lines.append(f"  Session {session['id']}:")
                lines.append(f"    Developer: {session['developer']}")
                lines.append(f"    Duration: {self._format_duration(session.get('duration_seconds', 0))}")
                lines.append(f"    Files: {len(session.get('files_modified', []))}")
                lines.append(f"    Tasks: {len(session.get('tasks_completed', []))}")
                if session.get('description'):
                    lines.append(f"    Description: {session['description']}")
                lines.append("")
        
        lines.append("=" * 70)
        
        report = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
        
        return report


def main():
    """Command-line interface for session manager."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migration Session Manager - Track your migration work sessions"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start a new session')
    start_parser.add_argument('--developer', help='Developer name')
    start_parser.add_argument('--description', help='Session description')
    
    # End command
    end_parser = subparsers.add_parser('end', help='End the current session')
    end_parser.add_argument('--summary', help='Session summary')
    
    # Pause command
    subparsers.add_parser('pause', help='Pause the current session')
    
    # Resume command
    subparsers.add_parser('resume', help='Resume a paused session')
    
    # Note command
    note_parser = subparsers.add_parser('note', help='Add a note to current session')
    note_parser.add_argument('note', help='Note text')
    
    # File command
    file_parser = subparsers.add_parser('file', help='Record a file being worked on')
    file_parser.add_argument('filepath', help='File path')
    
    # Task command
    task_parser = subparsers.add_parser('task', help='Record a completed task')
    task_parser.add_argument('task', help='Task description')
    
    # Status command
    subparsers.add_parser('status', help='Show current session status')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show session history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of sessions to show')
    
    # Stats command
    subparsers.add_parser('stats', help='Show session statistics')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate detailed report')
    report_parser.add_argument('-o', '--output', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = SessionManager()
    
    try:
        if args.command == 'start':
            session = manager.start_session(args.developer, args.description)
            print(f"✓ Session started: {session['id']}")
            if session.get('description'):
                print(f"  Description: {session['description']}")
            print(f"  Developer: {session['developer']}")
        
        elif args.command == 'end':
            session = manager.end_session(args.summary)
            print(f"✓ Session ended: {session['id']}")
            print(f"  Duration: {manager._format_duration(session['duration_seconds'])}")
            print(f"  Files modified: {len(session.get('files_modified', []))}")
            print(f"  Tasks completed: {len(session.get('tasks_completed', []))}")
        
        elif args.command == 'pause':
            session = manager.pause_session()
            print(f"✓ Session paused: {session['id']}")
        
        elif args.command == 'resume':
            session = manager.resume_session()
            print(f"✓ Session resumed: {session['id']}")
        
        elif args.command == 'note':
            manager.add_note(args.note)
            print(f"✓ Note added")
        
        elif args.command == 'file':
            manager.add_file(args.filepath)
            print(f"✓ File recorded: {args.filepath}")
        
        elif args.command == 'task':
            manager.add_task(args.task)
            print(f"✓ Task recorded")
        
        elif args.command == 'status':
            active = manager.get_active_session()
            if active:
                print(f"Active Session: {active['id']}")
                print(f"  Developer: {active['developer']}")
                print(f"  Status: {active['status']}")
                print(f"  Started: {active['start_time']}")
                if active.get('description'):
                    print(f"  Description: {active['description']}")
                print(f"  Files modified: {len(active.get('files_modified', []))}")
                print(f"  Tasks completed: {len(active.get('tasks_completed', []))}")
                print(f"  Notes: {len(active.get('notes', []))}")
            else:
                print("No active session")
        
        elif args.command == 'history':
            sessions = manager.get_session_history(args.limit)
            if sessions:
                print(f"Recent Sessions (last {len(sessions)}):")
                print("-" * 70)
                for session in sessions:
                    print(f"Session {session['id']}:")
                    print(f"  Developer: {session['developer']}")
                    print(f"  Duration: {manager._format_duration(session.get('duration_seconds', 0))}")
                    print(f"  Files: {len(session.get('files_modified', []))}")
                    print(f"  Tasks: {len(session.get('tasks_completed', []))}")
                    if session.get('description'):
                        print(f"  Description: {session['description']}")
                    print()
            else:
                print("No session history")
        
        elif args.command == 'stats':
            stats = manager.get_statistics()
            print("Session Statistics:")
            print("-" * 70)
            print(f"Total Sessions: {stats['total_sessions']}")
            print(f"Total Time: {stats['total_time_formatted']}")
            print(f"Average Session: {stats['average_session_formatted']}")
            print(f"Files Modified: {stats['total_files_modified']}")
            print(f"Tasks Completed: {stats['total_tasks_completed']}")
            print(f"Notes Recorded: {stats['total_notes']}")
            if stats['developers']:
                print("\nBy Developer:")
                for dev, dev_stats in stats['sessions_by_developer'].items():
                    print(f"  {dev}: {dev_stats['sessions']} sessions, {dev_stats['time_formatted']}")
        
        elif args.command == 'report':
            report = manager.generate_report(args.output)
            if args.output:
                print(f"✓ Report written to {args.output}")
            else:
                print(report)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
