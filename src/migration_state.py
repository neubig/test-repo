#!/usr/bin/env python3
"""
Migration State Tracker for Python 2 to 3 Migration

Tracks the migration status of individual files through various stages:
pending → in_progress → migrated → verified → tested → done

Enables team coordination, resumable migrations, and granular progress tracking.
"""

import json
import os
import socket
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class MigrationState(Enum):
    """Possible states for a file during migration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    MIGRATED = "migrated"
    VERIFIED = "verified"
    TESTED = "tested"
    DONE = "done"
    SKIPPED = "skipped"


class MigrationStateTracker:
    """Tracks and persists migration state for individual files."""
    
    def __init__(self, project_root: str = ".", state_file: str = ".py2to3.state.json"):
        self.project_root = Path(project_root).resolve()
        self.state_file = self.project_root / state_file
        self.state_data: Dict = self._load_state()
        
    def _load_state(self) -> Dict:
        """Load state from persistent storage."""
        if not self.state_file.exists():
            return self._create_default_state()
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Ensure all required fields exist
                if 'metadata' not in data:
                    data['metadata'] = self._default_metadata()
                if 'files' not in data:
                    data['files'] = {}
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load state file: {e}")
            return self._create_default_state()
    
    def _save_state(self):
        """Save state to persistent storage."""
        self.state_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state_data, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save state file: {e}")
    
    def _create_default_state(self) -> Dict:
        """Create default state structure."""
        return {
            'metadata': self._default_metadata(),
            'files': {}
        }
    
    def _default_metadata(self) -> Dict:
        """Create default metadata."""
        return {
            'version': '1.0',
            'project_root': str(self.project_root),
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _normalize_path(self, file_path: str) -> str:
        """Normalize file path relative to project root."""
        abs_path = Path(file_path).resolve()
        try:
            return str(abs_path.relative_to(self.project_root))
        except ValueError:
            # Path is outside project root, use absolute
            return str(abs_path)
    
    def initialize(self, scan_directory: str = None, force: bool = False) -> Dict:
        """
        Initialize migration state by scanning for Python files.
        
        Args:
            scan_directory: Directory to scan for Python files (default: project root)
            force: If True, reinitialize even if state exists
            
        Returns:
            Dict with initialization statistics
        """
        if self.state_file.exists() and not force:
            return {
                'status': 'already_initialized',
                'state_file': str(self.state_file),
                'file_count': len(self.state_data['files'])
            }
        
        # Scan for Python files
        scan_dir = Path(scan_directory or self.project_root)
        python_files = []
        
        for root, dirs, files in os.walk(scan_dir):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in [
                '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                'build', 'dist', '.eggs', '*.egg-info'
            ]]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        # Initialize state for each file
        added_count = 0
        for file_path in python_files:
            normalized = self._normalize_path(str(file_path))
            if normalized not in self.state_data['files']:
                self.state_data['files'][normalized] = {
                    'state': MigrationState.PENDING.value,
                    'created': datetime.now().isoformat(),
                    'updated': datetime.now().isoformat(),
                    'locked': False,
                    'owner': None,
                    'history': [{
                        'state': MigrationState.PENDING.value,
                        'timestamp': datetime.now().isoformat(),
                        'user': os.environ.get('USER', 'unknown')
                    }]
                }
                added_count += 1
        
        self._save_state()
        
        return {
            'status': 'initialized',
            'state_file': str(self.state_file),
            'files_found': len(python_files),
            'files_added': added_count,
            'total_tracked': len(self.state_data['files'])
        }
    
    def set_state(self, file_path: str, new_state: MigrationState, 
                  notes: str = None, user: str = None) -> bool:
        """
        Set the migration state for a file.
        
        Args:
            file_path: Path to the file
            new_state: New migration state
            notes: Optional notes about the state change
            user: User making the change (default: current user)
            
        Returns:
            True if successful
        """
        normalized = self._normalize_path(file_path)
        
        if normalized not in self.state_data['files']:
            # Add new file
            self.state_data['files'][normalized] = {
                'state': new_state.value,
                'created': datetime.now().isoformat(),
                'updated': datetime.now().isoformat(),
                'locked': False,
                'owner': None,
                'history': []
            }
        
        file_data = self.state_data['files'][normalized]
        
        # Check if locked by someone else
        if file_data.get('locked') and file_data.get('owner') != user:
            raise ValueError(f"File is locked by {file_data['owner']}")
        
        # Update state
        old_state = file_data['state']
        file_data['state'] = new_state.value
        file_data['updated'] = datetime.now().isoformat()
        
        # Add to history
        history_entry = {
            'from_state': old_state,
            'to_state': new_state.value,
            'timestamp': datetime.now().isoformat(),
            'user': user or os.environ.get('USER', 'unknown')
        }
        if notes:
            history_entry['notes'] = notes
        
        if 'history' not in file_data:
            file_data['history'] = []
        file_data['history'].append(history_entry)
        
        self._save_state()
        return True
    
    def get_state(self, file_path: str) -> Optional[Dict]:
        """Get the current state for a file."""
        normalized = self._normalize_path(file_path)
        return self.state_data['files'].get(normalized)
    
    def lock_file(self, file_path: str, owner: str = None) -> bool:
        """
        Lock a file for exclusive editing.
        
        Args:
            file_path: Path to the file
            owner: Owner of the lock (default: current user@hostname)
            
        Returns:
            True if successfully locked
        """
        normalized = self._normalize_path(file_path)
        
        if normalized not in self.state_data['files']:
            raise ValueError(f"File not tracked: {file_path}")
        
        file_data = self.state_data['files'][normalized]
        
        if file_data.get('locked'):
            current_owner = file_data.get('owner', 'unknown')
            raise ValueError(f"File is already locked by {current_owner}")
        
        file_data['locked'] = True
        file_data['owner'] = owner or f"{os.environ.get('USER', 'unknown')}@{socket.gethostname()}"
        file_data['locked_at'] = datetime.now().isoformat()
        
        self._save_state()
        return True
    
    def unlock_file(self, file_path: str, owner: str = None, force: bool = False) -> bool:
        """
        Unlock a file.
        
        Args:
            file_path: Path to the file
            owner: Owner requesting unlock (must match lock owner unless force=True)
            force: Force unlock regardless of owner
            
        Returns:
            True if successfully unlocked
        """
        normalized = self._normalize_path(file_path)
        
        if normalized not in self.state_data['files']:
            raise ValueError(f"File not tracked: {file_path}")
        
        file_data = self.state_data['files'][normalized]
        
        if not file_data.get('locked'):
            return True  # Already unlocked
        
        if not force and file_data.get('owner') != owner:
            raise ValueError(f"File is locked by {file_data.get('owner')}, cannot unlock")
        
        file_data['locked'] = False
        file_data['owner'] = None
        if 'locked_at' in file_data:
            del file_data['locked_at']
        
        self._save_state()
        return True
    
    def list_files(self, state: MigrationState = None, locked: bool = None,
                   owner: str = None) -> List[Dict]:
        """
        List files with optional filtering.
        
        Args:
            state: Filter by migration state
            locked: Filter by lock status
            owner: Filter by owner
            
        Returns:
            List of file data dicts with 'path' added
        """
        results = []
        
        for file_path, file_data in self.state_data['files'].items():
            # Apply filters
            if state and file_data['state'] != state.value:
                continue
            if locked is not None and file_data.get('locked', False) != locked:
                continue
            if owner and file_data.get('owner') != owner:
                continue
            
            # Add path to result
            result = {'path': file_path, **file_data}
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about migration progress."""
        stats = {
            'total_files': len(self.state_data['files']),
            'by_state': {},
            'locked_files': 0,
            'completion_percentage': 0.0
        }
        
        # Count by state
        for file_data in self.state_data['files'].values():
            state = file_data['state']
            stats['by_state'][state] = stats['by_state'].get(state, 0) + 1
            if file_data.get('locked'):
                stats['locked_files'] += 1
        
        # Calculate completion
        done_count = stats['by_state'].get(MigrationState.DONE.value, 0)
        if stats['total_files'] > 0:
            stats['completion_percentage'] = (done_count / stats['total_files']) * 100
        
        # Add state progression
        in_progress = sum([
            stats['by_state'].get(MigrationState.IN_PROGRESS.value, 0),
            stats['by_state'].get(MigrationState.MIGRATED.value, 0),
            stats['by_state'].get(MigrationState.VERIFIED.value, 0),
            stats['by_state'].get(MigrationState.TESTED.value, 0),
        ])
        stats['in_progress_files'] = in_progress
        stats['pending_files'] = stats['by_state'].get(MigrationState.PENDING.value, 0)
        
        return stats
    
    def reset_file(self, file_path: str) -> bool:
        """Reset a file to pending state."""
        normalized = self._normalize_path(file_path)
        
        if normalized in self.state_data['files']:
            self.set_state(file_path, MigrationState.PENDING, 
                         notes="Reset to pending")
            return True
        return False
    
    def remove_file(self, file_path: str) -> bool:
        """Remove a file from tracking."""
        normalized = self._normalize_path(file_path)
        
        if normalized in self.state_data['files']:
            del self.state_data['files'][normalized]
            self._save_state()
            return True
        return False
    
    def export_state(self, output_file: str = None) -> Dict:
        """
        Export the current state.
        
        Args:
            output_file: Optional file to save export to
            
        Returns:
            The complete state data
        """
        export_data = {
            **self.state_data,
            'exported_at': datetime.now().isoformat(),
            'exported_by': os.environ.get('USER', 'unknown')
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        return export_data
    
    def import_state(self, import_file: str, merge: bool = False) -> Dict:
        """
        Import state from a file.
        
        Args:
            import_file: File to import from
            merge: If True, merge with existing state; if False, replace
            
        Returns:
            Import statistics
        """
        with open(import_file, 'r') as f:
            import_data = json.load(f)
        
        if not merge:
            self.state_data = import_data
            self._save_state()
            return {
                'status': 'replaced',
                'files_imported': len(import_data.get('files', {}))
            }
        
        # Merge mode
        imported = 0
        updated = 0
        
        for file_path, file_data in import_data.get('files', {}).items():
            if file_path in self.state_data['files']:
                # Update if import is newer
                existing_time = self.state_data['files'][file_path].get('updated', '')
                import_time = file_data.get('updated', '')
                if import_time > existing_time:
                    self.state_data['files'][file_path] = file_data
                    updated += 1
            else:
                self.state_data['files'][file_path] = file_data
                imported += 1
        
        self._save_state()
        
        return {
            'status': 'merged',
            'files_imported': imported,
            'files_updated': updated
        }


if __name__ == '__main__':
    # Quick CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: migration_state.py <command> [args...]")
        print("Commands: init, list, stats")
        sys.exit(1)
    
    tracker = MigrationStateTracker()
    command = sys.argv[1]
    
    if command == 'init':
        result = tracker.initialize()
        print(json.dumps(result, indent=2))
    elif command == 'list':
        files = tracker.list_files()
        for file_data in files:
            print(f"{file_data['path']}: {file_data['state']}")
    elif command == 'stats':
        stats = tracker.get_statistics()
        print(json.dumps(stats, indent=2))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
