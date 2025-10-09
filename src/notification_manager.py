"""
Notification Manager for Python 2 to 3 Migration Toolkit

Sends notifications about migration progress to various channels:
- Slack webhooks
- Discord webhooks
- Generic webhooks (for custom integrations)
- Email (SMTP)
- File output (for logging/CI artifacts)

Usage:
    from notification_manager import NotificationManager
    
    notifier = NotificationManager()
    notifier.send_milestone("50% Complete", "Half of the files have been migrated!")
    notifier.send_error("Critical Issue", "Found syntax error in module X")
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.request import Request, urlopen
from urllib.error import URLError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationManager:
    """Manages notifications for migration events"""
    
    NOTIFICATION_TYPES = {
        'milestone': '🎯',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'progress': '📊'
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize notification manager
        
        Args:
            config_file: Path to notification configuration file
        """
        self.config = self._load_config(config_file)
        self.enabled_channels = self.config.get('enabled_channels', [])
        self.notification_history = []
        
    def _load_config(self, config_file: Optional[str] = None) -> Dict:
        """Load notification configuration"""
        default_config = {
            'enabled_channels': [],
            'slack': {
                'webhook_url': os.environ.get('SLACK_WEBHOOK_URL', ''),
                'username': 'py2to3-bot',
                'channel': '#migration'
            },
            'discord': {
                'webhook_url': os.environ.get('DISCORD_WEBHOOK_URL', ''),
                'username': 'py2to3-bot'
            },
            'webhook': {
                'url': os.environ.get('WEBHOOK_URL', ''),
                'headers': {}
            },
            'email': {
                'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.environ.get('SMTP_PORT', '587')),
                'username': os.environ.get('EMAIL_USERNAME', ''),
                'password': os.environ.get('EMAIL_PASSWORD', ''),
                'from_addr': os.environ.get('EMAIL_FROM', ''),
                'to_addrs': os.environ.get('EMAIL_TO', '').split(',')
            },
            'file': {
                'output_path': os.environ.get('NOTIFICATION_FILE', 'notifications.log'),
                'format': 'json'
            },
            'milestones': [25, 50, 75, 100],
            'notify_on_start': True,
            'notify_on_complete': True,
            'notify_on_error': True,
            'min_severity': 'info'
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return default_config
    
    def send_notification(self, title: str, message: str, 
                         notification_type: str = 'info',
                         metadata: Optional[Dict] = None) -> bool:
        """
        Send a notification to all enabled channels
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification (milestone, success, error, warning, info, progress)
            metadata: Additional metadata to include
            
        Returns:
            True if at least one channel succeeded, False otherwise
        """
        if not self.enabled_channels:
            return False
            
        emoji = self.NOTIFICATION_TYPES.get(notification_type, 'ℹ️')
        timestamp = datetime.now().isoformat()
        
        notification_data = {
            'title': title,
            'message': message,
            'type': notification_type,
            'emoji': emoji,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        self.notification_history.append(notification_data)
        
        success_count = 0
        
        for channel in self.enabled_channels:
            try:
                if channel == 'slack' and self.config['slack']['webhook_url']:
                    if self._send_slack(notification_data):
                        success_count += 1
                        
                elif channel == 'discord' and self.config['discord']['webhook_url']:
                    if self._send_discord(notification_data):
                        success_count += 1
                        
                elif channel == 'webhook' and self.config['webhook']['url']:
                    if self._send_webhook(notification_data):
                        success_count += 1
                        
                elif channel == 'email' and self.config['email']['username']:
                    if self._send_email(notification_data):
                        success_count += 1
                        
                elif channel == 'file':
                    if self._send_file(notification_data):
                        success_count += 1
                        
            except Exception as e:
                print(f"Error sending to {channel}: {e}", file=sys.stderr)
                
        return success_count > 0
    
    def _send_slack(self, data: Dict) -> bool:
        """Send notification to Slack"""
        webhook_url = self.config['slack']['webhook_url']
        
        payload = {
            'username': self.config['slack'].get('username', 'py2to3-bot'),
            'channel': self.config['slack'].get('channel', '#migration'),
            'text': f"{data['emoji']} *{data['title']}*",
            'attachments': [{
                'text': data['message'],
                'color': self._get_color(data['type']),
                'footer': 'py2to3 Migration Toolkit',
                'ts': int(time.time())
            }]
        }
        
        if data['metadata']:
            fields = []
            for key, value in data['metadata'].items():
                fields.append({
                    'title': key.replace('_', ' ').title(),
                    'value': str(value),
                    'short': True
                })
            payload['attachments'][0]['fields'] = fields
        
        return self._post_json(webhook_url, payload)
    
    def _send_discord(self, data: Dict) -> bool:
        """Send notification to Discord"""
        webhook_url = self.config['discord']['webhook_url']
        
        embed = {
            'title': f"{data['emoji']} {data['title']}",
            'description': data['message'],
            'color': int(self._get_color(data['type'])[1:], 16),
            'timestamp': data['timestamp'],
            'footer': {
                'text': 'py2to3 Migration Toolkit'
            }
        }
        
        if data['metadata']:
            fields = []
            for key, value in data['metadata'].items():
                fields.append({
                    'name': key.replace('_', ' ').title(),
                    'value': str(value),
                    'inline': True
                })
            embed['fields'] = fields
        
        payload = {
            'username': self.config['discord'].get('username', 'py2to3-bot'),
            'embeds': [embed]
        }
        
        return self._post_json(webhook_url, payload)
    
    def _send_webhook(self, data: Dict) -> bool:
        """Send notification to generic webhook"""
        webhook_url = self.config['webhook']['url']
        headers = self.config['webhook'].get('headers', {})
        
        return self._post_json(webhook_url, data, headers)
    
    def _send_email(self, data: Dict) -> bool:
        """Send notification via email"""
        try:
            smtp_config = self.config['email']
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{data['emoji']} {data['title']}"
            msg['From'] = smtp_config['from_addr']
            msg['To'] = ', '.join(smtp_config['to_addrs'])
            
            text_body = f"""
{data['title']}

{data['message']}

Timestamp: {data['timestamp']}
Type: {data['type']}

---
py2to3 Migration Toolkit
"""
            
            html_body = f"""
<html>
  <body>
    <h2>{data['emoji']} {data['title']}</h2>
    <p>{data['message']}</p>
    {self._format_metadata_html(data['metadata'])}
    <hr>
    <small>
      <p>Timestamp: {data['timestamp']}</p>
      <p>Type: {data['type']}</p>
      <p><em>py2to3 Migration Toolkit</em></p>
    </small>
  </body>
</html>
"""
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                server.starttls()
                if smtp_config['username'] and smtp_config['password']:
                    server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email error: {e}", file=sys.stderr)
            return False
    
    def _send_file(self, data: Dict) -> bool:
        """Write notification to file"""
        try:
            output_path = self.config['file']['output_path']
            format_type = self.config['file'].get('format', 'json')
            
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            with open(output_path, 'a') as f:
                if format_type == 'json':
                    f.write(json.dumps(data) + '\n')
                else:
                    f.write(f"[{data['timestamp']}] {data['emoji']} {data['title']}: {data['message']}\n")
            
            return True
            
        except Exception as e:
            print(f"File write error: {e}", file=sys.stderr)
            return False
    
    def _post_json(self, url: str, payload: Dict, headers: Optional[Dict] = None) -> bool:
        """POST JSON data to URL"""
        try:
            req_headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'py2to3-migration-toolkit/1.0'
            }
            
            if headers:
                req_headers.update(headers)
            
            data = json.dumps(payload).encode('utf-8')
            req = Request(url, data=data, headers=req_headers)
            
            with urlopen(req, timeout=10) as response:
                return response.status == 200
                
        except URLError as e:
            print(f"HTTP error: {e}", file=sys.stderr)
            return False
    
    def _get_color(self, notification_type: str) -> str:
        """Get color code for notification type"""
        colors = {
            'milestone': '#6f42c1',
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'progress': '#007bff'
        }
        return colors.get(notification_type, '#6c757d')
    
    def _format_metadata_html(self, metadata: Dict) -> str:
        """Format metadata as HTML"""
        if not metadata:
            return ""
        
        html = "<table style='border-collapse: collapse; margin: 10px 0;'>"
        for key, value in metadata.items():
            html += f"<tr><td style='padding: 5px; font-weight: bold;'>{key.replace('_', ' ').title()}:</td>"
            html += f"<td style='padding: 5px;'>{value}</td></tr>"
        html += "</table>"
        return html
    
    # Convenience methods for common notification types
    
    def send_milestone(self, milestone: str, message: str, metadata: Optional[Dict] = None) -> bool:
        """Send a milestone notification"""
        return self.send_notification(
            f"Milestone: {milestone}",
            message,
            'milestone',
            metadata
        )
    
    def send_success(self, title: str, message: str, metadata: Optional[Dict] = None) -> bool:
        """Send a success notification"""
        return self.send_notification(title, message, 'success', metadata)
    
    def send_error(self, title: str, message: str, metadata: Optional[Dict] = None) -> bool:
        """Send an error notification"""
        return self.send_notification(title, message, 'error', metadata)
    
    def send_warning(self, title: str, message: str, metadata: Optional[Dict] = None) -> bool:
        """Send a warning notification"""
        return self.send_notification(title, message, 'warning', metadata)
    
    def send_progress(self, percent: float, files_done: int, files_total: int,
                     metadata: Optional[Dict] = None) -> bool:
        """Send a progress update notification"""
        message = f"Migrated {files_done} of {files_total} files"
        
        progress_metadata = {
            'completion_percent': f"{percent:.1f}%",
            'files_migrated': files_done,
            'files_total': files_total,
            'files_remaining': files_total - files_done
        }
        
        if metadata:
            progress_metadata.update(metadata)
        
        return self.send_notification(
            f"Migration Progress: {percent:.0f}%",
            message,
            'progress',
            progress_metadata
        )
    
    def send_start(self, project_name: str, files_count: int) -> bool:
        """Send migration start notification"""
        return self.send_notification(
            "Migration Started",
            f"Beginning migration of {project_name}",
            'info',
            {
                'project': project_name,
                'total_files': files_count,
                'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
    
    def send_complete(self, project_name: str, duration: str, stats: Optional[Dict] = None) -> bool:
        """Send migration complete notification"""
        metadata = {
            'project': project_name,
            'duration': duration,
            'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if stats:
            metadata.update(stats)
        
        return self.send_notification(
            "Migration Complete! 🎉",
            f"Successfully completed migration of {project_name}",
            'success',
            metadata
        )
    
    def get_history(self) -> List[Dict]:
        """Get notification history"""
        return self.notification_history
    
    def clear_history(self):
        """Clear notification history"""
        self.notification_history = []
    
    def test_channels(self) -> Dict[str, bool]:
        """Test all configured channels"""
        results = {}
        
        test_data = {
            'title': 'Test Notification',
            'message': 'This is a test notification from py2to3',
            'type': 'info',
            'emoji': '🧪',
            'timestamp': datetime.now().isoformat(),
            'metadata': {'test': True}
        }
        
        for channel in self.enabled_channels:
            try:
                if channel == 'slack' and self.config['slack']['webhook_url']:
                    results['slack'] = self._send_slack(test_data)
                    
                elif channel == 'discord' and self.config['discord']['webhook_url']:
                    results['discord'] = self._send_discord(test_data)
                    
                elif channel == 'webhook' and self.config['webhook']['url']:
                    results['webhook'] = self._send_webhook(test_data)
                    
                elif channel == 'email' and self.config['email']['username']:
                    results['email'] = self._send_email(test_data)
                    
                elif channel == 'file':
                    results['file'] = self._send_file(test_data)
                    
            except Exception as e:
                results[channel] = False
                print(f"Test failed for {channel}: {e}", file=sys.stderr)
        
        return results


def main():
    """CLI for testing notification manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test notification system')
    parser.add_argument('--config', help='Configuration file')
    parser.add_argument('--type', default='info', 
                       choices=['milestone', 'success', 'error', 'warning', 'info', 'progress'])
    parser.add_argument('--title', default='Test Notification')
    parser.add_argument('--message', default='This is a test notification')
    parser.add_argument('--test-all', action='store_true', help='Test all channels')
    
    args = parser.parse_args()
    
    notifier = NotificationManager(args.config)
    
    if args.test_all:
        print("Testing all notification channels...")
        results = notifier.test_channels()
        for channel, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {channel}: {status}")
    else:
        print(f"Sending {args.type} notification...")
        success = notifier.send_notification(args.title, args.message, args.type)
        if success:
            print("✅ Notification sent successfully!")
        else:
            print("❌ Failed to send notification")
            sys.exit(1)


if __name__ == '__main__':
    main()
