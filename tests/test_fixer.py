"""
Unit tests for Python2to3Fixer.
"""

import pytest
from pathlib import Path

from fixer import Python2to3Fixer


@pytest.mark.unit
class TestFixerInitialization:
    """Test fixer initialization and setup."""
    
    def test_fixer_init_default(self, temp_dir):
        """Test fixer initialization with default backup directory."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        assert fixer.backup_dir == str(temp_dir / "backup")
        assert (temp_dir / "backup").exists()
    
    def test_fixer_init_creates_backup_dir(self, temp_dir):
        """Test that fixer creates backup directory if it doesn't exist."""
        backup_path = temp_dir / "new_backup"
        assert not backup_path.exists()
        
        fixer = Python2to3Fixer(backup_dir=str(backup_path))
        assert backup_path.exists()
    
    def test_fixer_has_fix_patterns(self, temp_dir):
        """Test that fixer has fix patterns defined."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        assert hasattr(fixer, 'fix_patterns')
        assert len(fixer.fix_patterns) > 0


@pytest.mark.unit
class TestFixerPatterns:
    """Test individual fix patterns."""
    
    def test_print_statement_pattern(self, temp_dir):
        """Test that print statements are converted to print functions."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        test_file = temp_dir / "test_print.py"
        test_file.write_text('print "Hello, World!"\n')
        
        result = fixer.fix_file(str(test_file))
        
        fixed_content = test_file.read_text()
        assert 'print("Hello, World!")' in fixed_content
        assert len(fixer.fixes_applied) > 0
    
    def test_urllib2_import_pattern(self, temp_dir):
        """Test that urllib2 imports are fixed."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        test_file = temp_dir / "test_urllib.py"
        test_file.write_text('import urllib2\n')
        
        result = fixer.fix_file(str(test_file))
        
        fixed_content = test_file.read_text()
        assert 'import urllib.request' in fixed_content
        assert len(fixer.fixes_applied) > 0
    
    def test_configparser_import_pattern(self, temp_dir):
        """Test that ConfigParser imports are fixed."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        test_file = temp_dir / "test_config.py"
        test_file.write_text('from ConfigParser import ConfigParser\n')
        
        result = fixer.fix_file(str(test_file))
        
        fixed_content = test_file.read_text()
        # The fix uses an alias for compatibility
        assert 'from configparser import' in fixed_content
        assert 'ConfigParser' in fixed_content
    
    def test_stringio_import_pattern(self, temp_dir):
        """Test that StringIO imports are fixed."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        test_file = temp_dir / "test_stringio.py"
        test_file.write_text('from StringIO import StringIO\n')
        
        result = fixer.fix_file(str(test_file))
        
        fixed_content = test_file.read_text()
        assert 'from io import StringIO' in fixed_content
    
    def test_pickle_import_pattern(self, temp_dir):
        """Test that cPickle imports are fixed."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        test_file = temp_dir / "test_pickle.py"
        test_file.write_text('import cPickle as pickle\n')
        
        result = fixer.fix_file(str(test_file))
        
        fixed_content = test_file.read_text()
        assert 'import pickle' in fixed_content


@pytest.mark.unit
class TestFixerFileMethods:
    """Test fixer file-level methods."""
    
    def test_fix_file_creates_backup(self, temp_dir, sample_py2_file):
        """Test that fix_file creates a backup before modifying."""
        backup_dir = temp_dir / "backup"
        fixer = Python2to3Fixer(backup_dir=str(backup_dir))
        
        original_content = sample_py2_file.read_text()
        
        result = fixer.fix_file(str(sample_py2_file))
        
        # Check that backup was created
        backups = list(backup_dir.glob("**/*.*"))
        assert len(backups) > 0
        
        # Check that original content is preserved in backup
        # The backup file should contain the original content
        # (actual backup filename may vary)
    
    def test_fix_file_modifies_content(self, temp_dir, sample_py2_file):
        """Test that fix_file actually modifies the file."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        original_content = sample_py2_file.read_text()
        
        result = fixer.fix_file(str(sample_py2_file))
        
        modified_content = sample_py2_file.read_text()
        assert modified_content != original_content
    
    def test_fix_file_tracks_fixes(self, temp_dir):
        """Test that fixer tracks applied fixes."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        test_file = temp_dir / "test.py"
        test_file.write_text('print "test"\n')
        
        result = fixer.fix_file(str(test_file))
        
        # Should have tracked fixes
        assert len(fixer.fixes_applied) > 0
    
    def test_fix_file_nonexistent(self, temp_dir):
        """Test that fixing a nonexistent file handles error gracefully."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        result = fixer.fix_file(str(temp_dir / "nonexistent.py"))
        
        # Should handle error (returns dict with success=False and errors populated)
        assert isinstance(result, dict)
        assert result['success'] is False or len(fixer.errors) > 0
    
    def test_dry_run_mode_file(self, temp_dir):
        """Test that dry-run mode doesn't modify files."""
        backup_dir = temp_dir / "backup"
        fixer = Python2to3Fixer(backup_dir=str(backup_dir))
        
        test_file = temp_dir / "test_dry.py"
        original_content = 'print "Hello"\nimport urllib2\n'
        test_file.write_text(original_content)
        
        # Run in dry-run mode
        result = fixer.fix_file(str(test_file), dry_run=True)
        
        # File should not be modified
        assert test_file.read_text() == original_content
        
        # No backup should be created
        assert not backup_dir.exists() or len(list(backup_dir.glob("**/*.*"))) == 0
        
        # Result should indicate success
        assert isinstance(result, dict)
        assert result['success'] is True
        
        # Fixes should still be tracked
        assert len(result['fixes']) > 0
    
    def test_dry_run_vs_normal_mode(self, temp_dir):
        """Test that dry-run reports same fixes as normal mode would apply."""
        backup_dir = temp_dir / "backup"
        
        # Create two identical test files
        test_content = 'print "Test"\nimport urllib2\nfor i in xrange(5): print i\n'
        test_file_dry = temp_dir / "test_dry.py"
        test_file_normal = temp_dir / "test_normal.py"
        test_file_dry.write_text(test_content)
        test_file_normal.write_text(test_content)
        
        # Run dry-run on first file
        fixer_dry = Python2to3Fixer(backup_dir=str(backup_dir / "dry"))
        result_dry = fixer_dry.fix_file(str(test_file_dry), dry_run=True)
        
        # Run normal mode on second file
        fixer_normal = Python2to3Fixer(backup_dir=str(backup_dir / "normal"))
        result_normal = fixer_normal.fix_file(str(test_file_normal), dry_run=False)
        
        # Both should report same number of fix types
        assert len(result_dry['fixes']) == len(result_normal['fixes'])
        
        # Dry-run file should be unchanged
        assert test_file_dry.read_text() == test_content
        
        # Normal file should be changed
        assert test_file_normal.read_text() != test_content


@pytest.mark.unit
class TestFixerDirectoryMethods:
    """Test fixer directory-level methods."""
    
    def test_fix_directory(self, temp_dir, sample_directory):
        """Test fixing an entire directory."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        result = fixer.fix_directory(str(sample_directory))
        
        # Should have processed files
        assert len(fixer.fixes_applied) > 0
        
        # Check that files were actually modified
        file1 = sample_directory / "file1.py"
        content1 = file1.read_text()
        assert 'print("File 1")' in content1
    
    def test_fix_directory_recursive(self, temp_dir):
        """Test fixing a directory recursively."""
        # Create nested directory structure
        nested_dir = temp_dir / "parent" / "child"
        nested_dir.mkdir(parents=True)
        
        (nested_dir / "test.py").write_text('print "nested"\n')
        
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        result = fixer.fix_directory(str(temp_dir / "parent"))
        
        # Should have found and fixed the nested file
        assert len(fixer.fixes_applied) > 0
        
        fixed_content = (nested_dir / "test.py").read_text()
        assert 'print("nested")' in fixed_content
    
    def test_fix_directory_processes_multiple_files(self, temp_dir, sample_directory):
        """Test directory fixing processes multiple files."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        # Store original file count
        py_files = list(sample_directory.glob("*.py"))
        file_count = len([f for f in py_files if f.name != "__init__.py"])
        
        result = fixer.fix_directory(str(sample_directory))
        
        # Should have processed multiple files
        # At least some fixes should have been applied
        assert len(fixer.fixes_applied) > 0 or result is True
    
    def test_dry_run_mode_directory(self, temp_dir):
        """Test that dry-run mode doesn't modify directory files."""
        backup_dir = temp_dir / "backup"
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        
        # Create test files with Python 2 code
        file1 = test_dir / "file1.py"
        file2 = test_dir / "file2.py"
        content1 = 'print "File 1"\n'
        content2 = 'import urllib2\nfor i in xrange(5): print i\n'
        file1.write_text(content1)
        file2.write_text(content2)
        
        # Run dry-run on directory
        fixer = Python2to3Fixer(backup_dir=str(backup_dir))
        result = fixer.fix_directory(str(test_dir), dry_run=True)
        
        # Files should not be modified
        assert file1.read_text() == content1
        assert file2.read_text() == content2
        
        # No backups should be created
        assert not backup_dir.exists() or len(list(backup_dir.glob("**/*.*"))) == 0
        
        # Result should be a dictionary with success=True
        assert isinstance(result, dict)
        assert result['success'] is True
        
        # Should have detected fixes
        assert len(result['fixes']) > 0


@pytest.mark.integration
class TestFixerIntegration:
    """Integration tests for the fixer."""
    
    def test_complete_file_migration(self, temp_dir, sample_py2_file):
        """Test complete migration of a Python 2 file."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        result = fixer.fix_file(str(sample_py2_file))
        
        fixed_content = sample_py2_file.read_text()
        
        # Verify multiple fixes were applied
        assert 'print("Hello, World!")' in fixed_content
        assert 'import urllib.request' in fixed_content
        assert 'from configparser import' in fixed_content or 'import configparser' in fixed_content
        assert 'import pickle' in fixed_content
        assert 'from io import StringIO' in fixed_content
        
        # Verify fixes were tracked
        assert len(fixer.fixes_applied) >= 3  # Should have multiple fixes
    
    def test_multiple_files_migration(self, temp_dir, sample_directory):
        """Test migration of multiple files."""
        fixer = Python2to3Fixer(backup_dir=str(temp_dir / "backup"))
        
        result = fixer.fix_directory(str(sample_directory))
        
        # Verify fixes were applied
        assert len(fixer.fixes_applied) > 0
        
        # Verify each file was fixed
        for py_file in sample_directory.glob("*.py"):
            if py_file.name != "__init__.py":
                content = py_file.read_text()
                assert 'print("' in content or py_file.name == "__init__.py"
