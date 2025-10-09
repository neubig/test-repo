#!/usr/bin/env python3
"""
Rollback Manager for Python 2 to 3 Migration Toolkit

Provides quick and safe rollback capabilities for migration operations:
- Track all migration operations in a history
- Quickly undo the last operation
- Preview what will be rolled back
- Selective rollback of specific files
- Integration with backup system
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class RollbackManager:
    """Manage rollback operations for Python 2 to 3 migration."""

    def __init__(self, history_dir=".migration_history"):
        self.history_dir = Path(history_dir)
        self.history_file = self.history_dir / "operations.json"
        self.operations = self._load_operations()

    def _load_operations(self) -> List[Dict]:
        """Load operation history from JSON file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    return data.get("operations", [])
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_operations(self):
        """Save operation history to JSON file."""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.history_file, 'w') as f:
            json.dump({"operations": self.operations}, f, indent=2, default=str)

    def record_operation(
        self,
        operation_type: str,
        files: List[Dict],
        description: str = "",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Record a migration operation in the history.
        
        Args:
            operation_type: Type of operation (e.g., 'fix', 'modernize', 'typehints')
            files: List of file operations with 'path', 'backup_path', 'action' keys
            description: Human-readable description of the operation
            metadata: Additional metadata about the operation
            
        Returns:
            Operation ID (timestamp-based)
        """
        operation_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        operation = {
            "id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "type": operation_type,
            "description": description,
            "files": files,
            "metadata": metadata or {},
            "rolled_back": False
        }
        
        self.operations.append(operation)
        self._save_operations()
        
        return operation_id

    def get_operations(
        self,
        operation_type: Optional[str] = None,
        include_rolled_back: bool = False
    ) -> List[Dict]:
        """
        Get list of operations, optionally filtered by type.
        
        Args:
            operation_type: Filter by operation type (None for all)
            include_rolled_back: Include operations that have been rolled back
            
        Returns:
            List of operation records
        """
        operations = self.operations
        
        if not include_rolled_back:
            operations = [op for op in operations if not op.get("rolled_back", False)]
        
        if operation_type:
            operations = [op for op in operations if op.get("type") == operation_type]
        
        return operations

    def get_last_operation(self, operation_type: Optional[str] = None) -> Optional[Dict]:
        """
        Get the most recent operation.
        
        Args:
            operation_type: Filter by operation type (None for any type)
            
        Returns:
            Most recent operation record or None
        """
        operations = self.get_operations(operation_type=operation_type)
        return operations[-1] if operations else None

    def preview_rollback(self, operation_id: Optional[str] = None) -> Dict:
        """
        Preview what will be rolled back without making changes.
        
        Args:
            operation_id: Specific operation to preview (None for last operation)
            
        Returns:
            Dictionary with rollback preview information
        """
        if operation_id:
            operation = next((op for op in self.operations if op["id"] == operation_id), None)
        else:
            operation = self.get_last_operation()
        
        if not operation:
            return {
                "success": False,
                "error": "No operation found to rollback"
            }
        
        if operation.get("rolled_back", False):
            return {
                "success": False,
                "error": f"Operation {operation['id']} has already been rolled back"
            }
        
        files_to_restore = []
        files_missing_backups = []
        
        for file_info in operation.get("files", []):
            backup_path = file_info.get("backup_path")
            original_path = file_info.get("path")
            
            if backup_path and os.path.exists(backup_path):
                files_to_restore.append({
                    "path": original_path,
                    "backup_path": backup_path,
                    "action": file_info.get("action", "modified")
                })
            else:
                files_missing_backups.append({
                    "path": original_path,
                    "backup_path": backup_path,
                    "reason": "backup not found"
                })
        
        return {
            "success": True,
            "operation": operation,
            "files_to_restore": files_to_restore,
            "files_missing_backups": files_missing_backups,
            "total_files": len(operation.get("files", [])),
            "restorable_files": len(files_to_restore)
        }

    def rollback(
        self,
        operation_id: Optional[str] = None,
        dry_run: bool = False,
        force: bool = False
    ) -> Dict:
        """
        Rollback a migration operation.
        
        Args:
            operation_id: Specific operation to rollback (None for last operation)
            dry_run: Preview changes without making them
            force: Force rollback even if some backups are missing
            
        Returns:
            Dictionary with rollback results
        """
        preview = self.preview_rollback(operation_id)
        
        if not preview["success"]:
            return preview
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": "Dry run - no changes made",
                "preview": preview
            }
        
        # Check if any backups are missing
        if preview["files_missing_backups"] and not force:
            return {
                "success": False,
                "error": "Some backup files are missing. Use --force to rollback anyway.",
                "missing_files": preview["files_missing_backups"]
            }
        
        # Perform the rollback
        restored_files = []
        failed_files = []
        
        for file_info in preview["files_to_restore"]:
            try:
                original_path = file_info["path"]
                backup_path = file_info["backup_path"]
                
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                
                # Restore the file
                shutil.copy2(backup_path, original_path)
                
                restored_files.append({
                    "path": original_path,
                    "status": "restored"
                })
            except Exception as e:
                failed_files.append({
                    "path": file_info["path"],
                    "error": str(e)
                })
        
        # Mark operation as rolled back
        operation = preview["operation"]
        for op in self.operations:
            if op["id"] == operation["id"]:
                op["rolled_back"] = True
                op["rollback_timestamp"] = datetime.now().isoformat()
                break
        
        self._save_operations()
        
        return {
            "success": len(failed_files) == 0,
            "operation_id": operation["id"],
            "operation_type": operation["type"],
            "restored_files": restored_files,
            "failed_files": failed_files,
            "total_restored": len(restored_files),
            "total_failed": len(failed_files)
        }

    def rollback_file(
        self,
        file_path: str,
        operation_id: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Rollback a specific file from an operation.
        
        Args:
            file_path: Path to the file to rollback
            operation_id: Specific operation to rollback from (None for last operation)
            dry_run: Preview changes without making them
            
        Returns:
            Dictionary with rollback results
        """
        if operation_id:
            operation = next((op for op in self.operations if op["id"] == operation_id), None)
        else:
            operation = self.get_last_operation()
        
        if not operation:
            return {
                "success": False,
                "error": "No operation found"
            }
        
        # Find the file in the operation
        file_info = next(
            (f for f in operation.get("files", []) if f.get("path") == file_path),
            None
        )
        
        if not file_info:
            return {
                "success": False,
                "error": f"File {file_path} not found in operation {operation['id']}"
            }
        
        backup_path = file_info.get("backup_path")
        
        if not backup_path or not os.path.exists(backup_path):
            return {
                "success": False,
                "error": f"Backup not found for {file_path}"
            }
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": "Dry run - no changes made",
                "file": file_path,
                "backup": backup_path
            }
        
        try:
            # Restore the file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            shutil.copy2(backup_path, file_path)
            
            return {
                "success": True,
                "file": file_path,
                "status": "restored",
                "backup": backup_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to restore {file_path}: {str(e)}"
            }

    def clear_history(self, keep_recent: int = 0) -> Dict:
        """
        Clear operation history.
        
        Args:
            keep_recent: Number of recent operations to keep (0 to clear all)
            
        Returns:
            Dictionary with clear results
        """
        original_count = len(self.operations)
        
        if keep_recent > 0:
            self.operations = self.operations[-keep_recent:]
        else:
            self.operations = []
        
        self._save_operations()
        
        return {
            "success": True,
            "cleared": original_count - len(self.operations),
            "remaining": len(self.operations)
        }

    def get_statistics(self) -> Dict:
        """
        Get statistics about operations and rollbacks.
        
        Returns:
            Dictionary with statistics
        """
        total_operations = len(self.operations)
        rolled_back = sum(1 for op in self.operations if op.get("rolled_back", False))
        active = total_operations - rolled_back
        
        operations_by_type = {}
        for op in self.operations:
            op_type = op.get("type", "unknown")
            operations_by_type[op_type] = operations_by_type.get(op_type, 0) + 1
        
        total_files = sum(len(op.get("files", [])) for op in self.operations)
        
        return {
            "total_operations": total_operations,
            "active_operations": active,
            "rolled_back_operations": rolled_back,
            "operations_by_type": operations_by_type,
            "total_files_tracked": total_files
        }

    def get_rolled_back_operations(
        self,
        operation_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get list of operations that have been rolled back and can be redone.
        
        Args:
            operation_type: Filter by operation type (None for all types)
            limit: Maximum number of operations to return
            
        Returns:
            List of rolled back operations, most recent first
        """
        rolled_back = [
            op for op in self.operations 
            if op.get("rolled_back", False)
        ]
        
        if operation_type:
            rolled_back = [op for op in rolled_back if op.get("type") == operation_type]
        
        rolled_back.reverse()
        
        if limit:
            rolled_back = rolled_back[:limit]
        
        return rolled_back

    def preview_redo(self, operation_id: Optional[str] = None) -> Dict:
        """
        Preview what will be redone without making changes.
        
        Args:
            operation_id: Specific operation to redo (None for last rolled back operation)
            
        Returns:
            Dictionary with preview information
        """
        # Find the operation to redo
        if operation_id:
            operation = next(
                (op for op in self.operations if op["id"] == operation_id),
                None
            )
        else:
            rolled_back = self.get_rolled_back_operations(limit=1)
            operation = rolled_back[0] if rolled_back else None
        
        if not operation:
            return {
                "success": False,
                "error": "No rolled back operation found to redo"
            }
        
        if not operation.get("rolled_back", False):
            return {
                "success": False,
                "error": f"Operation {operation['id']} has not been rolled back"
            }
        
        files = operation.get("files", [])
        files_to_apply = []
        files_missing_backups = []
        
        for file_info in files:
            backup_path = file_info.get("backup_path")
            original_path = file_info.get("path")
            
            if backup_path and Path(backup_path).exists():
                files_to_apply.append({
                    "path": original_path,
                    "backup_path": backup_path,
                    "action": file_info.get("action", "modified")
                })
            else:
                files_missing_backups.append({
                    "path": original_path,
                    "reason": "Backup file not found"
                })
        
        return {
            "success": True,
            "operation": {
                "id": operation["id"],
                "type": operation["type"],
                "description": operation.get("description", ""),
                "timestamp": operation["timestamp"],
                "rollback_timestamp": operation.get("rollback_timestamp")
            },
            "files_to_apply": files_to_apply,
            "files_missing_backups": files_missing_backups,
            "total_files": len(files),
            "files_ready": len(files_to_apply),
            "files_missing": len(files_missing_backups)
        }

    def redo(
        self,
        operation_id: Optional[str] = None,
        dry_run: bool = False,
        force: bool = False
    ) -> Dict:
        """
        Redo a rolled back migration operation.
        
        Args:
            operation_id: Specific operation to redo (None for last rolled back operation)
            dry_run: Preview changes without making them
            force: Force redo even if some backups are missing
            
        Returns:
            Dictionary with redo results
        """
        preview = self.preview_redo(operation_id)
        
        if not preview["success"]:
            return preview
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": "Dry run - no changes made",
                "preview": preview
            }
        
        # Check if any backups are missing
        if preview["files_missing_backups"] and not force:
            return {
                "success": False,
                "error": "Some backup files are missing. Use --force to redo anyway.",
                "missing_files": preview["files_missing_backups"]
            }
        
        # First, create backups of current state before redoing
        current_state_backups = []
        for file_info in preview["files_to_apply"]:
            original_path = file_info["path"]
            if Path(original_path).exists():
                # Create a backup of current state
                backup_dir = self.history_dir / "redo_backups" / preview["operation"]["id"]
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / Path(original_path).name
                
                try:
                    shutil.copy2(original_path, backup_path)
                    current_state_backups.append({
                        "path": original_path,
                        "backup_path": str(backup_path)
                    })
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to backup current state: {e}"
                    }
        
        # Perform the redo by restoring from the original backups
        applied_files = []
        failed_files = []
        
        for file_info in preview["files_to_apply"]:
            try:
                original_path = file_info["path"]
                backup_path = file_info["backup_path"]
                
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                
                # Apply the changes from backup (this is the migrated version)
                shutil.copy2(backup_path, original_path)
                
                applied_files.append({
                    "path": original_path,
                    "status": "reapplied"
                })
            except Exception as e:
                failed_files.append({
                    "path": file_info["path"],
                    "error": str(e)
                })
        
        # Mark operation as not rolled back anymore
        operation = preview["operation"]
        for op in self.operations:
            if op["id"] == operation["id"]:
                op["rolled_back"] = False
                op["redo_timestamp"] = datetime.now().isoformat()
                op["redo_backups"] = current_state_backups
                break
        
        self._save_operations()
        
        return {
            "success": len(failed_files) == 0,
            "operation_id": operation["id"],
            "operation_type": operation["type"],
            "applied_files": applied_files,
            "failed_files": failed_files,
            "total_applied": len(applied_files),
            "total_failed": len(failed_files),
            "message": f"Successfully reapplied {len(applied_files)} file(s)"
        }


def main():
    """Example usage and testing."""
    import sys
    
    manager = RollbackManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            operations = manager.get_operations()
            print(f"Found {len(operations)} operations:")
            for op in operations:
                status = " (rolled back)" if op.get("rolled_back") else ""
                print(f"  {op['id']}: {op['type']} - {op.get('description', 'No description')}{status}")
        
        elif command == "list-rolled-back":
            operations = manager.get_rolled_back_operations()
            print(f"Found {len(operations)} rolled back operations that can be redone:")
            for op in operations:
                print(f"  {op['id']}: {op['type']} - {op.get('description', 'No description')}")
        
        elif command == "preview":
            preview = manager.preview_rollback()
            print(json.dumps(preview, indent=2))
        
        elif command == "preview-redo":
            preview = manager.preview_redo()
            print(json.dumps(preview, indent=2))
        
        elif command == "stats":
            stats = manager.get_statistics()
            print(json.dumps(stats, indent=2))
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: list, list-rolled-back, preview, preview-redo, stats")
    else:
        print("Rollback Manager")
        print("Usage: python rollback_manager.py [list|list-rolled-back|preview|preview-redo|stats]")


if __name__ == "__main__":
    main()
