#!/usr/bin/env python3
"""
Configuration Manager for py2to3 toolkit

Handles loading, saving, and managing configuration files for the py2to3 tool.
Supports both project-level and user-level configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration for py2to3 toolkit."""
    
    DEFAULT_CONFIG_NAME = ".py2to3.config.json"
    USER_CONFIG_PATH = Path.home() / ".py2to3" / "config.json"
    
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "backup_dir": "backup",
        "report_output": "migration_report.html",
        "auto_confirm": False,
        "verbose": False,
        "no_color": False,
        "ignore_patterns": [
            "**/node_modules/**",
            "**/venv/**",
            "**/env/**",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
            "**/__pycache__/**",
            "**/*.pyc"
        ],
        "fix_rules": {
            "fix_print_statements": True,
            "fix_imports": True,
            "fix_exceptions": True,
            "fix_iterators": True,
            "fix_unicode": True,
            "fix_comparisons": True
        },
        "verify_rules": {
            "check_syntax": True,
            "check_imports": True,
            "check_deprecated": True
        }
    }
    
    def __init__(self, project_dir: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            project_dir: Project directory to search for config file
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_configs()
    
    def _load_configs(self):
        """Load configuration from user and project config files."""
        # Load user-level config first
        if self.USER_CONFIG_PATH.exists():
            try:
                with open(self.USER_CONFIG_PATH, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load user config: {e}")
        
        # Load project-level config (overrides user config)
        project_config_path = self.project_dir / self.DEFAULT_CONFIG_NAME
        if project_config_path.exists():
            try:
                with open(project_config_path, 'r') as f:
                    project_config = json.load(f)
                    self._merge_config(project_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load project config: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """
        Merge new configuration with existing config.
        
        Args:
            new_config: Configuration dictionary to merge
        """
        for key, value in new_config.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_project_config(self, path: Optional[str] = None):
        """
        Save configuration to project config file.
        
        Args:
            path: Path to save config file (default: project directory)
        """
        if path is None:
            path = self.project_dir / self.DEFAULT_CONFIG_NAME
        else:
            path = Path(path)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error: Failed to save config: {e}")
            return False
    
    def save_user_config(self):
        """Save configuration to user config file."""
        try:
            self.USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.USER_CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error: Failed to save user config: {e}")
            return False
    
    def init_project_config(self, path: Optional[str] = None) -> bool:
        """
        Initialize a new project configuration file with defaults.
        
        Args:
            path: Path to create config file (default: current directory)
            
        Returns:
            True if successful, False otherwise
        """
        if path is None:
            path = Path.cwd() / self.DEFAULT_CONFIG_NAME
        else:
            path = Path(path)
        
        if path.exists():
            return False  # Don't overwrite existing config
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            return True
        except IOError as e:
            print(f"Error: Failed to create config: {e}")
            return False
    
    def get_config_path(self) -> Optional[Path]:
        """
        Get the path to the active project config file.
        
        Returns:
            Path to config file or None if not found
        """
        project_config_path = self.project_dir / self.DEFAULT_CONFIG_NAME
        if project_config_path.exists():
            return project_config_path
        return None
    
    def has_project_config(self) -> bool:
        """Check if project has a config file."""
        return (self.project_dir / self.DEFAULT_CONFIG_NAME).exists()
    
    def has_user_config(self) -> bool:
        """Check if user has a config file."""
        return self.USER_CONFIG_PATH.exists()
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config.copy()
    
    def apply_to_args(self, args: Any) -> Any:
        """
        Apply configuration defaults to argparse arguments.
        
        Args:
            args: Argparse namespace object
            
        Returns:
            Modified args object
        """
        # Apply configuration values if not explicitly set in command line
        if hasattr(args, 'backup_dir') and args.backup_dir == 'backup':
            args.backup_dir = self.get('backup_dir', 'backup')
        
        if hasattr(args, 'output') and args.output == 'migration_report.html':
            args.output = self.get('report_output', 'migration_report.html')
        
        if hasattr(args, 'yes') and not args.yes:
            args.yes = self.get('auto_confirm', False)
        
        if hasattr(args, 'verbose') and not args.verbose:
            args.verbose = self.get('verbose', False)
        
        if hasattr(args, 'no_color') and not args.no_color:
            args.no_color = self.get('no_color', False)
        
        return args
