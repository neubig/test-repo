"""
Tests for notification_manager module
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from notification_manager import NotificationManager


class TestNotificationManager:
    """Test the NotificationManager class"""
    
    def test_initialization(self):
        """Test basic initialization"""
        notifier = NotificationManager()
        assert notifier is not None
        assert isinstance(notifier.config, dict)
        assert isinstance(notifier.enabled_channels, list)
    
    def test_load_config_from_file(self, tmp_path):
        """Test loading configuration from file"""
        config_data = {
            'enabled_channels': ['file'],
            'file': {
                'output_path': 'test_notifications.log',
                'format': 'json'
            }
        }
        
        config_file = tmp_path / "test_config.json"
        config_file.write_text(json.dumps(config_data))
        
        notifier = NotificationManager(str(config_file))
        assert 'file' in notifier.enabled_channels
        assert notifier.config['file']['output_path'] == 'test_notifications.log'
    
    def test_file_notification(self, tmp_path):
        """Test sending notification to file"""
        log_file = tmp_path / "notifications.log"
        
        config_data = {
            'enabled_channels': ['file'],
            'file': {
                'output_path': str(log_file),
                'format': 'json'
            }
        }
        
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        notifier = NotificationManager(str(config_file))
        
        # Send notification
        success = notifier.send_notification(
            'Test Title',
            'Test Message',
            'info'
        )
        
        assert success is True
        assert log_file.exists()
        
        # Verify content
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            notification = json.loads(lines[0])
            assert notification['title'] == 'Test Title'
            assert notification['message'] == 'Test Message'
            assert notification['type'] == 'info'
    
    def test_file_notification_text_format(self, tmp_path):
        """Test sending notification to file in text format"""
        log_file = tmp_path / "notifications.txt"
        
        config_data = {
            'enabled_channels': ['file'],
            'file': {
                'output_path': str(log_file),
                'format': 'text'
            }
        }
        
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        notifier = NotificationManager(str(config_file))
        
        # Send notification
        success = notifier.send_notification(
            'Test Title',
            'Test Message',
            'info'
        )
        
        assert success is True
        assert log_file.exists()
        
        # Verify content
        content = log_file.read_text()
        assert 'Test Title' in content
        assert 'Test Message' in content
    
    def test_convenience_methods(self, tmp_path):
        """Test convenience methods for different notification types"""
        log_file = tmp_path / "notifications.log"
        
        config_data = {
            'enabled_channels': ['file'],
            'file': {
                'output_path': str(log_file),
                'format': 'json'
            }
        }
        
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        notifier = NotificationManager(str(config_file))
        
        # Test different notification types
        assert notifier.send_milestone('50%', 'Halfway there!') is True
        assert notifier.send_success('Success', 'Task completed') is True
        assert notifier.send_error('Error', 'Something went wrong') is True
        assert notifier.send_warning('Warning', 'Be careful') is True
        assert notifier.send_progress(50.0, 50, 100) is True
        
        # Verify all notifications were written
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 5
    
    def test_send_start_and_complete(self, tmp_path):
        """Test start and complete notifications"""
        log_file = tmp_path / "notifications.log"
        
        config_data = {
            'enabled_channels': ['file'],
            'file': {
                'output_path': str(log_file),
                'format': 'json'
            }
        }
        
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        notifier = NotificationManager(str(config_file))
        
        # Send start notification
        assert notifier.send_start('test-project', 100) is True
        
        # Send complete notification
        assert notifier.send_complete('test-project', '5m 30s', {
            'files_migrated': 100,
            'issues_fixed': 50
        }) is True
        
        # Verify notifications
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            
            start_notif = json.loads(lines[0])
            assert 'Started' in start_notif['title']
            assert start_notif['metadata']['total_files'] == 100
            
            complete_notif = json.loads(lines[1])
            assert 'Complete' in complete_notif['title']
            assert complete_notif['metadata']['duration'] == '5m 30s'
    
    def test_notification_with_metadata(self, tmp_path):
        """Test notification with custom metadata"""
        log_file = tmp_path / "notifications.log"
        
        config_data = {
            'enabled_channels': ['file'],
            'file': {
                'output_path': str(log_file),
                'format': 'json'
            }
        }
        
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        notifier = NotificationManager(str(config_file))
        
        # Send notification with metadata
        metadata = {
            'files_done': 50,
            'files_total': 100,
            'branch': 'main',
            'author': 'test-user'
        }
        
        assert notifier.send_notification(
            'Progress Update',
            'Migration in progress',
            'progress',
            metadata
        ) is True
        
        # Verify metadata
        with open(log_file, 'r') as f:
            notification = json.loads(f.readline())
            assert notification['metadata'] == metadata
    
    def test_notification_history(self, tmp_path):
        """Test notification history tracking"""
        log_file = tmp_path / "notifications.log"
        
        config_data = {
            'enabled_channels': ['file'],
            'file': {
                'output_path': str(log_file),
                'format': 'json'
            }
        }
        
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        notifier = NotificationManager(str(config_file))
        
        # Send multiple notifications
        notifier.send_notification('Test 1', 'Message 1', 'info')
        notifier.send_notification('Test 2', 'Message 2', 'success')
        notifier.send_notification('Test 3', 'Message 3', 'warning')
        
        # Check history
        history = notifier.get_history()
        assert len(history) == 3
        assert history[0]['title'] == 'Test 1'
        assert history[1]['title'] == 'Test 2'
        assert history[2]['title'] == 'Test 3'
        
        # Clear history
        notifier.clear_history()
        assert len(notifier.get_history()) == 0
    
    def test_no_channels_configured(self):
        """Test behavior when no channels are configured"""
        config_data = {
            'enabled_channels': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            notifier = NotificationManager(config_file)
            
            # Should return False when no channels configured
            result = notifier.send_notification('Test', 'Message', 'info')
            assert result is False
        finally:
            os.unlink(config_file)
    
    def test_environment_variables(self):
        """Test configuration via environment variables"""
        # Set environment variables
        os.environ['SLACK_WEBHOOK_URL'] = 'https://hooks.slack.com/test'
        os.environ['NOTIFICATION_FILE'] = '/tmp/test_notifications.log'
        
        try:
            notifier = NotificationManager()
            
            # Verify environment variables are loaded
            assert notifier.config['slack']['webhook_url'] == 'https://hooks.slack.com/test'
            assert notifier.config['file']['output_path'] == '/tmp/test_notifications.log'
        finally:
            # Clean up
            os.environ.pop('SLACK_WEBHOOK_URL', None)
            os.environ.pop('NOTIFICATION_FILE', None)
    
    def test_notification_types(self):
        """Test all notification types are defined"""
        notifier = NotificationManager()
        
        expected_types = ['milestone', 'success', 'error', 'warning', 'info', 'progress']
        
        for notif_type in expected_types:
            assert notif_type in NotificationManager.NOTIFICATION_TYPES
            assert len(NotificationManager.NOTIFICATION_TYPES[notif_type]) > 0  # Has emoji


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
