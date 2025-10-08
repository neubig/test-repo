#!/usr/bin/env python3
"""
Backup Manager for Python 2 to 3 Migration Toolkit

Manages backups created during the migration process, including:
- Listing available backups
- Restoring files from backups
- Cleaning up old backups
- Comparing backups with current files
"""

import difflib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Manage backups created during Python 2 to 3 migration."""

    def __init__(self, backup_dir="backup"):
        self.backup_dir = Path(backup_dir)
        self.metadata_file = self.backup_dir / ".backup_metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        """Load backup metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"backups": []}
        return {"backups": []}

    def _save_metadata(self):
        """Save backup metadata to JSON file."""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)

    def register_backup(self, original_path, backup_path, description=""):
        """Register a new backup in the metadata."""
        backup_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_path": str(original_path),
            "backup_path": str(backup_path),
            "description": description,
            "size": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
        }
        
        self.metadata["backups"].append(backup_entry)
        self._save_metadata()
        return backup_entry

    def list_backups(self, pattern=None):
        """List all available backups, optionally filtered by pattern."""
        backups = self.metadata.get("backups", [])
        
        if pattern:
            backups = [b for b in backups if pattern in b.get("original_path", "")]
        
        return backups

    def get_backup_stats(self):
        """Get statistics about backups."""
        backups = self.metadata.get("backups", [])
        
        if not backups:
            return {
                "total_count": 0,
                "total_size": 0,
                "oldest": None,
                "newest": None
            }
        
        total_size = sum(b.get("size", 0) for b in backups)
        timestamps = [b.get("timestamp", "") for b in backups if b.get("timestamp")]
        
        return {
            "total_count": len(backups),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest": min(timestamps) if timestamps else None,
            "newest": max(timestamps) if timestamps else None
        }

    def restore_file(self, backup_path, original_path=None, dry_run=False):
        """Restore a file from backup."""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Find the original path from metadata if not provided
        if original_path is None:
            for backup in self.metadata.get("backups", []):
                if Path(backup.get("backup_path", "")) == backup_path:
                    original_path = backup.get("original_path")
                    break
            
            if original_path is None:
                raise ValueError(f"Could not find original path for backup: {backup_path}")
        
        original_path = Path(original_path)
        
        if dry_run:
            return {
                "status": "dry_run",
                "backup_path": str(backup_path),
                "original_path": str(original_path),
                "would_restore": True
            }
        
        # Create directory if it doesn't exist
        original_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Restore the file
        shutil.copy2(backup_path, original_path)
        
        return {
            "status": "success",
            "backup_path": str(backup_path),
            "original_path": str(original_path),
            "restored": True
        }

    def restore_directory(self, backup_dir=None, target_dir=None, dry_run=False):
        """Restore all files from a backup directory."""
        if backup_dir is None:
            backup_dir = self.backup_dir
        else:
            backup_dir = Path(backup_dir)
        
        if not backup_dir.exists():
            raise FileNotFoundError(f"Backup directory not found: {backup_dir}")
        
        restored = []
        errors = []
        
        # Find all files in backup directory
        for backup_file in backup_dir.rglob("*"):
            if backup_file.is_file() and backup_file.name != ".backup_metadata.json":
                try:
                    # Try to find original path from metadata
                    original_path = None
                    for backup in self.metadata.get("backups", []):
                        if Path(backup.get("backup_path", "")) == backup_file:
                            original_path = backup.get("original_path")
                            break
                    
                    if original_path:
                        result = self.restore_file(backup_file, original_path, dry_run)
                        restored.append(result)
                except Exception as e:
                    errors.append({
                        "backup_path": str(backup_file),
                        "error": str(e)
                    })
        
        return {
            "restored": restored,
            "errors": errors,
            "total_restored": len(restored),
            "total_errors": len(errors)
        }

    def clean_backups(self, older_than_days=None, pattern=None, all_backups=False, dry_run=False):
        """Clean up old backups."""
        backups = self.metadata.get("backups", [])
        removed = []
        kept = []
        errors = []
        
        for backup in backups:
            should_remove = False
            backup_path = Path(backup.get("backup_path", ""))
            
            # Check if backup should be removed
            if all_backups:
                should_remove = True
            elif pattern and pattern in backup.get("original_path", ""):
                should_remove = True
            elif older_than_days is not None:
                try:
                    timestamp = datetime.fromisoformat(backup.get("timestamp", ""))
                    days_old = (datetime.now() - timestamp).days
                    if days_old > older_than_days:
                        should_remove = True
                except (ValueError, TypeError):
                    pass
            
            if should_remove:
                if dry_run:
                    removed.append({
                        "backup_path": str(backup_path),
                        "original_path": backup.get("original_path"),
                        "timestamp": backup.get("timestamp"),
                        "status": "would_remove"
                    })
                else:
                    try:
                        if backup_path.exists():
                            backup_path.unlink()
                        removed.append({
                            "backup_path": str(backup_path),
                            "original_path": backup.get("original_path"),
                            "timestamp": backup.get("timestamp"),
                            "status": "removed"
                        })
                    except Exception as e:
                        errors.append({
                            "backup_path": str(backup_path),
                            "error": str(e)
                        })
            else:
                kept.append(backup)
        
        # Update metadata if not dry run
        if not dry_run and removed:
            self.metadata["backups"] = kept
            self._save_metadata()
        
        return {
            "removed": removed,
            "kept_count": len(kept),
            "errors": errors,
            "total_removed": len(removed),
            "total_errors": len(errors)
        }

    def diff_backup(self, backup_path, original_path=None, context_lines=3):
        """Show differences between backup and current file."""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Find the original path from metadata if not provided
        if original_path is None:
            for backup in self.metadata.get("backups", []):
                if Path(backup.get("backup_path", "")) == backup_path:
                    original_path = backup.get("original_path")
                    break
            
            if original_path is None:
                raise ValueError(f"Could not find original path for backup: {backup_path}")
        
        original_path = Path(original_path)
        
        if not original_path.exists():
            return {
                "status": "original_missing",
                "message": f"Original file does not exist: {original_path}"
            }
        
        # Read files
        with open(backup_path, 'r', encoding='utf-8', errors='ignore') as f:
            backup_lines = f.readlines()
        
        with open(original_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_lines = f.readlines()
        
        # Generate unified diff
        diff = difflib.unified_diff(
            backup_lines,
            original_lines,
            fromfile=f"backup: {backup_path.name}",
            tofile=f"current: {original_path.name}",
            lineterm='',
            n=context_lines
        )
        
        diff_text = '\n'.join(diff)
        
        # Count changes
        added = len([line for line in original_lines if line not in backup_lines])
        removed = len([line for line in backup_lines if line not in original_lines])
        
        return {
            "status": "success",
            "backup_path": str(backup_path),
            "original_path": str(original_path),
            "diff": diff_text,
            "has_changes": bool(diff_text),
            "stats": {
                "lines_added": added,
                "lines_removed": removed,
                "backup_lines": len(backup_lines),
                "current_lines": len(original_lines)
            }
        }

    def get_backup_info(self, backup_path):
        """Get detailed information about a specific backup."""
        backup_path = Path(backup_path)
        
        # Find in metadata
        backup_info = None
        for backup in self.metadata.get("backups", []):
            if Path(backup.get("backup_path", "")) == backup_path:
                backup_info = backup.copy()
                break
        
        if backup_info is None:
            raise ValueError(f"Backup not found in metadata: {backup_path}")
        
        # Add file existence check
        backup_info["exists"] = backup_path.exists()
        backup_info["original_exists"] = Path(backup_info.get("original_path", "")).exists()
        
        # Add file size if exists
        if backup_info["exists"]:
            backup_info["current_size"] = os.path.getsize(backup_path)
            backup_info["current_size_kb"] = round(backup_info["current_size"] / 1024, 2)
        
        # Calculate age
        try:
            timestamp = datetime.fromisoformat(backup_info.get("timestamp", ""))
            age = datetime.now() - timestamp
            backup_info["age_days"] = age.days
            backup_info["age_hours"] = round(age.total_seconds() / 3600, 1)
        except (ValueError, TypeError):
            pass
        
        return backup_info

    def scan_backup_directory(self):
        """Scan backup directory and sync with metadata."""
        if not self.backup_dir.exists():
            return {
                "status": "no_backup_dir",
                "message": f"Backup directory does not exist: {self.backup_dir}"
            }
        
        # Get all backup files from filesystem
        fs_backups = set()
        for backup_file in self.backup_dir.rglob("*"):
            if backup_file.is_file() and backup_file.name != ".backup_metadata.json":
                fs_backups.add(backup_file)
        
        # Get all backup files from metadata
        meta_backups = set(Path(b.get("backup_path", "")) for b in self.metadata.get("backups", []))
        
        # Find orphaned files (in filesystem but not in metadata)
        orphaned = fs_backups - meta_backups
        
        # Find missing files (in metadata but not in filesystem)
        missing = meta_backups - fs_backups
        
        return {
            "status": "success",
            "total_fs_backups": len(fs_backups),
            "total_meta_backups": len(meta_backups),
            "orphaned_files": [str(p) for p in orphaned],
            "missing_files": [str(p) for p in missing],
            "orphaned_count": len(orphaned),
            "missing_count": len(missing)
        }
