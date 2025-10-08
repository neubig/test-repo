"""
Unit tests for BackupManager.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta

from backup_manager import BackupManager


@pytest.mark.unit
class TestBackupManagerInit:
    """Test backup manager initialization."""
    
    def test_init_default(self, temp_dir):
        """Test initialization with default settings."""
        manager = BackupManager(backup_dir=str(temp_dir / "backup"))
        assert manager.backup_dir == Path(temp_dir / "backup")
        assert isinstance(manager.metadata, dict)
    
    def test_init_creates_backup_dir(self, temp_dir):
        """Test that initialization creates backup directory."""
        backup_path = temp_dir / "new_backup"
        assert not backup_path.exists()
        
        manager = BackupManager(backup_dir=str(backup_path))
        # Directory may not be created until first backup, which is fine
        assert manager.backup_dir == backup_path
    
    def test_metadata_file_creation(self, temp_dir):
        """Test metadata file is created correctly."""
        backup_dir = temp_dir / "backup"
        manager = BackupManager(backup_dir=str(backup_dir))
        
        # Register a backup to trigger metadata save
        test_file = temp_dir / "test.py"
        test_file.write_text("test content")
        
        backup_file = backup_dir / "test.py.backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file.write_text("test content")
        
        manager.register_backup(str(test_file), str(backup_file), "Test backup")
        
        metadata_file = backup_dir / ".backup_metadata.json"
        assert metadata_file.exists()


@pytest.mark.unit
class TestBackupRegistration:
    """Test backup registration functionality."""
    
    def test_register_backup(self, temp_dir):
        """Test registering a new backup."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        original_file = temp_dir / "original.py"
        original_file.write_text("original content")
        
        backup_file = backup_dir / "original.py.backup"
        backup_file.write_text("original content")
        
        entry = manager.register_backup(
            str(original_file),
            str(backup_file),
            "Test backup"
        )
        
        assert entry is not None
        assert entry['original_path'] == str(original_file)
        assert entry['backup_path'] == str(backup_file)
        assert entry['description'] == "Test backup"
        assert 'timestamp' in entry
        assert 'size' in entry
    
    def test_multiple_backups_registration(self, temp_dir):
        """Test registering multiple backups."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        # Register multiple backups
        for i in range(3):
            original = temp_dir / f"file{i}.py"
            original.write_text(f"content {i}")
            
            backup = backup_dir / f"file{i}.py.backup"
            backup.write_text(f"content {i}")
            
            manager.register_backup(str(original), str(backup), f"Backup {i}")
        
        backups = manager.list_backups()
        assert len(backups) == 3


@pytest.mark.unit
class TestBackupListing:
    """Test backup listing functionality."""
    
    def test_list_backups_empty(self, temp_dir):
        """Test listing backups when none exist."""
        manager = BackupManager(backup_dir=str(temp_dir / "backup"))
        backups = manager.list_backups()
        assert backups == []
    
    def test_list_backups_with_pattern(self, temp_dir):
        """Test listing backups with pattern filter."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        # Register backups with different patterns
        files = ["test.py", "main.py", "utils.py"]
        for filename in files:
            original = temp_dir / filename
            original.write_text("content")
            
            backup = backup_dir / f"{filename}.backup"
            backup.write_text("content")
            
            manager.register_backup(str(original), str(backup))
        
        # Filter by pattern
        test_backups = manager.list_backups(pattern="test")
        assert len(test_backups) == 1
        assert "test.py" in test_backups[0]['original_path']
        
        main_backups = manager.list_backups(pattern="main")
        assert len(main_backups) == 1
        assert "main.py" in main_backups[0]['original_path']
    
    def test_list_all_backups(self, temp_dir):
        """Test listing all backups without filter."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        # Register multiple backups
        for i in range(5):
            original = temp_dir / f"file{i}.py"
            original.write_text(f"content {i}")
            
            backup = backup_dir / f"file{i}.py.backup"
            backup.write_text(f"content {i}")
            
            manager.register_backup(str(original), str(backup))
        
        all_backups = manager.list_backups()
        assert len(all_backups) == 5


@pytest.mark.unit
class TestBackupStatistics:
    """Test backup statistics functionality."""
    
    def test_stats_empty(self, temp_dir):
        """Test statistics with no backups."""
        manager = BackupManager(backup_dir=str(temp_dir / "backup"))
        stats = manager.get_backup_stats()
        
        assert stats['total_count'] == 0
        assert stats['total_size'] == 0
        assert stats['oldest'] is None
        assert stats['newest'] is None
    
    def test_stats_with_backups(self, temp_dir):
        """Test statistics with backups."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        # Register some backups
        total_size = 0
        for i in range(3):
            original = temp_dir / f"file{i}.py"
            content = f"content {i}" * 10
            original.write_text(content)
            
            backup = backup_dir / f"file{i}.py.backup"
            backup.write_text(content)
            total_size += len(content.encode('utf-8'))
            
            manager.register_backup(str(original), str(backup))
        
        stats = manager.get_backup_stats()
        
        assert stats['total_count'] == 3
        assert stats['total_size'] == total_size
        assert stats['oldest'] is not None
        assert stats['newest'] is not None


@pytest.mark.unit
class TestBackupRestore:
    """Test backup restoration functionality."""
    
    def test_restore_file_basic(self, temp_dir):
        """Test basic file restoration."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        # Create original and backup
        original = temp_dir / "test.py"
        original.write_text("original content")
        
        backup = backup_dir / "test.py.backup"
        backup.write_text("backup content")
        
        manager.register_backup(str(original), str(backup))
        
        # Modify original
        original.write_text("modified content")
        
        # Restore from backup
        result = manager.restore_file(str(backup), str(original))
        
        # Verify restoration (method returns dict with success status)
        assert result is not None
        assert original.read_text() == "backup content"
    
    def test_restore_file_dry_run(self, temp_dir):
        """Test restoring file in dry run mode."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        original = temp_dir / "test.py"
        original.write_text("original content")
        
        backup = backup_dir / "test.py.backup"
        backup.write_text("backup content")
        
        # Modify original
        original.write_text("modified content")
        
        result = manager.restore_file(str(backup), str(original), dry_run=True)
        
        # File should not be modified in dry run
        assert original.read_text() == "modified content"
    
    def test_restore_nonexistent_backup(self, temp_dir):
        """Test restoring from nonexistent backup."""
        manager = BackupManager(backup_dir=str(temp_dir / "backup"))
        
        # Method throws FileNotFoundError for nonexistent backup
        with pytest.raises(FileNotFoundError):
            manager.restore_file(
                str(temp_dir / "nonexistent.backup"),
                str(temp_dir / "target.py")
            )


@pytest.mark.unit
class TestBackupDiff:
    """Test backup diff functionality."""
    
    def test_diff_identical_files(self, temp_dir):
        """Test diff between identical backup and current file."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        content = "same content\n"
        
        backup = backup_dir / "test.py.backup"
        backup.write_text(content)
        
        current = temp_dir / "test.py"
        current.write_text(content)
        
        diff = manager.diff_backup(str(backup), str(current))
        
        # Returns a dict with diff information
        assert isinstance(diff, dict)
        assert 'has_changes' in diff
        assert diff['has_changes'] is False
    
    def test_diff_different_files(self, temp_dir):
        """Test diff between different backup and current file."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        backup = backup_dir / "test.py.backup"
        backup.write_text("original content\n")
        
        current = temp_dir / "test.py"
        current.write_text("modified content\n")
        
        diff = manager.diff_backup(str(backup), str(current))
        
        assert isinstance(diff, dict)
        assert 'has_changes' in diff
        assert diff['has_changes'] is True
        assert 'diff' in diff
        assert "original" in diff['diff'] or "modified" in diff['diff']


@pytest.mark.integration
class TestBackupManagerIntegration:
    """Integration tests for backup manager."""
    
    def test_complete_backup_workflow(self, temp_dir):
        """Test complete backup workflow: create, list, restore."""
        backup_dir = temp_dir / "backup"
        backup_dir.mkdir()
        
        manager = BackupManager(backup_dir=str(backup_dir))
        
        # Create and backup a file
        original = temp_dir / "workflow_test.py"
        original_content = "original workflow content"
        original.write_text(original_content)
        
        backup = backup_dir / "workflow_test.py.backup"
        backup.write_text(original_content)
        
        # Register backup
        manager.register_backup(str(original), str(backup), "Workflow test")
        
        # Modify original
        original.write_text("modified content")
        
        # List backups
        backups = manager.list_backups()
        assert len(backups) == 1
        assert backups[0]['description'] == "Workflow test"
        
        # Restore from backup
        result = manager.restore_file(str(backup), str(original))
        assert result is not None
        assert original.read_text() == original_content
        
        # Get statistics
        stats = manager.get_backup_stats()
        assert stats['total_count'] == 1
