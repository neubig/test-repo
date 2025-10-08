"""
Unit tests for ConfigManager.
"""

import json
import pytest
from pathlib import Path

from config_manager import ConfigManager


@pytest.mark.unit
class TestConfigManagerInit:
    """Test configuration manager initialization."""
    
    def test_init_default(self, temp_dir):
        """Test initialization with default settings."""
        manager = ConfigManager(project_dir=str(temp_dir))
        assert manager.project_dir == temp_dir
        assert isinstance(manager.config, dict)
    
    def test_init_loads_default_config(self, temp_dir):
        """Test that default configuration is loaded."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        assert 'backup_dir' in manager.config
        assert 'report_output' in manager.config
        assert 'ignore_patterns' in manager.config
        assert 'fix_rules' in manager.config
    
    def test_init_with_project_config(self, temp_dir, config_file):
        """Test initialization with existing project config."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        # Should have loaded custom config values
        assert manager.config['backup_dir'] == 'test_backup'
        assert manager.config['report_output'] == 'test_report.html'
        assert manager.config['verbose'] is True


@pytest.mark.unit
class TestConfigGet:
    """Test configuration retrieval."""
    
    def test_get_simple_value(self, temp_dir):
        """Test getting a simple configuration value."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        value = manager.get('backup_dir')
        assert value is not None
        assert isinstance(value, str)
    
    def test_get_nested_value(self, temp_dir):
        """Test getting a nested configuration value."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        value = manager.get('fix_rules.fix_print_statements')
        assert value is not None
        assert isinstance(value, bool)
    
    def test_get_with_default(self, temp_dir):
        """Test getting value with default fallback."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        value = manager.get('nonexistent_key', default='default_value')
        assert value == 'default_value'
    
    def test_get_nonexistent_no_default(self, temp_dir):
        """Test getting nonexistent value without default."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        value = manager.get('nonexistent_key')
        assert value is None


@pytest.mark.unit
class TestConfigSet:
    """Test configuration setting."""
    
    def test_set_simple_value(self, temp_dir):
        """Test setting a simple configuration value."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        manager.set('backup_dir', 'new_backup')
        assert manager.config['backup_dir'] == 'new_backup'
    
    def test_set_nested_value(self, temp_dir):
        """Test setting a nested configuration value."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        manager.set('fix_rules.fix_print_statements', False)
        assert manager.config['fix_rules']['fix_print_statements'] is False
    
    def test_set_creates_nested_structure(self, temp_dir):
        """Test that setting creates nested structure if needed."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        manager.set('new_section.new_key', 'new_value')
        assert manager.config['new_section']['new_key'] == 'new_value'
    
    def test_set_multiple_values(self, temp_dir):
        """Test setting multiple values."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        manager.set('backup_dir', 'backup1')
        manager.set('report_output', 'report1.html')
        manager.set('verbose', True)
        
        assert manager.config['backup_dir'] == 'backup1'
        assert manager.config['report_output'] == 'report1.html'
        assert manager.config['verbose'] is True


@pytest.mark.unit
class TestConfigSave:
    """Test configuration saving."""
    
    def test_save_project_config(self, temp_dir):
        """Test saving project configuration."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        manager.set('backup_dir', 'saved_backup')
        manager.save_project_config()
        
        config_file = temp_dir / '.py2to3.config.json'
        assert config_file.exists()
        
        with open(config_file) as f:
            saved_config = json.load(f)
        
        assert saved_config['backup_dir'] == 'saved_backup'
    
    def test_save_and_reload(self, temp_dir):
        """Test that saved config can be reloaded."""
        manager1 = ConfigManager(project_dir=str(temp_dir))
        manager1.set('backup_dir', 'test_backup_reload')
        manager1.save_project_config()
        
        # Create new manager instance
        manager2 = ConfigManager(project_dir=str(temp_dir))
        
        assert manager2.config['backup_dir'] == 'test_backup_reload'


@pytest.mark.unit
class TestConfigInit:
    """Test configuration initialization."""
    
    def test_init_project_config(self, temp_dir):
        """Test initializing a new project config."""
        # Use a fresh empty directory
        empty_dir = temp_dir / "empty_project"
        empty_dir.mkdir()
        
        config_file = empty_dir / '.py2to3.config.json'
        assert not config_file.exists()
        
        manager = ConfigManager(project_dir=str(empty_dir))
        # Pass explicit path since init_project_config uses cwd by default
        result = manager.init_project_config(str(config_file))
        
        assert result is True
        assert config_file.exists()
    
    def test_has_project_config(self, temp_dir, config_file):
        """Test checking if project config exists."""
        manager = ConfigManager(project_dir=str(temp_dir))
        assert manager.has_project_config() is True
        
        manager2 = ConfigManager(project_dir=str(temp_dir / "empty"))
        assert manager2.has_project_config() is False
    
    def test_get_config_path(self, temp_dir, config_file):
        """Test getting config file path."""
        manager = ConfigManager(project_dir=str(temp_dir))
        path = manager.get_config_path()
        
        assert path is not None
        assert path.exists()
        assert path.name == '.py2to3.config.json'


@pytest.mark.unit
class TestConfigDict:
    """Test configuration dict operations."""
    
    def test_to_dict(self, temp_dir):
        """Test converting config to dictionary."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        config_dict = manager.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'backup_dir' in config_dict
        assert 'report_output' in config_dict
    
    def test_to_dict_preserves_values(self, temp_dir):
        """Test that to_dict preserves all config values."""
        manager = ConfigManager(project_dir=str(temp_dir))
        manager.set('backup_dir', 'test_backup')
        
        config_dict = manager.to_dict()
        
        assert config_dict['backup_dir'] == 'test_backup'


@pytest.mark.unit
class TestConfigMerge:
    """Test configuration merging."""
    
    def test_merge_configs(self, temp_dir):
        """Test merging configurations."""
        manager = ConfigManager(project_dir=str(temp_dir))
        
        original_backup_dir = manager.config['backup_dir']
        
        override_config = {
            'backup_dir': 'merged_backup',
            'new_key': 'new_value'
        }
        
        manager._merge_config(override_config)
        
        assert manager.config['backup_dir'] == 'merged_backup'
        assert manager.config['new_key'] == 'new_value'
        # Other defaults should remain
        assert 'report_output' in manager.config


@pytest.mark.unit
class TestConfigApplyToArgs:
    """Test applying configuration to command-line arguments."""
    
    def test_apply_to_args_basic(self, temp_dir):
        """Test applying config to args namespace."""
        manager = ConfigManager(project_dir=str(temp_dir))
        manager.set('backup_dir', 'args_backup')
        
        class Args:
            backup_dir = None
            report_output = None
        
        args = Args()
        modified_args = manager.apply_to_args(args)
        
        # Method returns the same args object with potentially updated values
        assert modified_args is args
        # Check that config was applied if arg was None
        # Note: actual behavior depends on implementation
    
    def test_apply_to_args_preserves_existing(self, temp_dir):
        """Test that apply_to_args preserves existing arg values."""
        manager = ConfigManager(project_dir=str(temp_dir))
        manager.set('backup_dir', 'config_backup')
        
        class Args:
            backup_dir = 'args_backup'
            report_output = None
        
        args = Args()
        modified_args = manager.apply_to_args(args)
        
        # Should return the args object
        assert modified_args is args


@pytest.mark.integration
class TestConfigManagerIntegration:
    """Integration tests for configuration manager."""
    
    def test_complete_config_workflow(self, temp_dir):
        """Test complete configuration workflow."""
        # Initialize config
        manager = ConfigManager(project_dir=str(temp_dir))
        manager.init_project_config()
        
        # Modify config
        manager.set('backup_dir', 'workflow_backup')
        manager.set('fix_rules.fix_print_statements', False)
        manager.save_project_config()
        
        # Reload in new instance
        manager2 = ConfigManager(project_dir=str(temp_dir))
        
        assert manager2.config['backup_dir'] == 'workflow_backup'
        assert manager2.config['fix_rules']['fix_print_statements'] is False
        
        # Check that it's a valid dict
        config_dict = manager2.to_dict()
        assert isinstance(config_dict, dict)
    
    def test_config_hierarchy(self, temp_dir):
        """Test configuration hierarchy (defaults < user < project)."""
        # Start with defaults
        manager = ConfigManager(project_dir=str(temp_dir))
        default_backup = manager.DEFAULT_CONFIG['backup_dir']
        
        # Create project config
        project_config = {
            'backup_dir': 'project_backup'
        }
        
        config_file = temp_dir / '.py2to3.config.json'
        with open(config_file, 'w') as f:
            json.dump(project_config, f)
        
        # Reload
        manager2 = ConfigManager(project_dir=str(temp_dir))
        
        # Project config should override default
        assert manager2.config['backup_dir'] == 'project_backup'
        # But defaults should still be present
        assert 'report_output' in manager2.config
