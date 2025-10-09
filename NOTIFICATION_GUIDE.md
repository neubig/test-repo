# 📢 Notification System Guide

The notification system allows teams to receive real-time alerts about migration progress via multiple channels. Perfect for team collaboration, CI/CD pipelines, and keeping stakeholders informed!

## 🚀 Quick Start

```bash
# 1. Create configuration template
./py2to3 notify --setup

# 2. Edit notification_config.json with your webhook URLs

# 3. Test your configuration
./py2to3 notify --test --config notification_config.json

# 4. Send a test notification
./py2to3 notify --title "Test" --message "Hello from py2to3!" --config notification_config.json
```

## 📋 Table of Contents

- [Supported Channels](#supported-channels)
- [Setup & Configuration](#setup--configuration)
- [Usage Examples](#usage-examples)
- [Integration with Migration Commands](#integration-with-migration-commands)
- [CI/CD Integration](#cicd-integration)
- [Notification Types](#notification-types)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## 🌐 Supported Channels

The notification system supports multiple delivery channels:

### 1. **Slack** 💬
Send notifications to Slack channels via incoming webhooks.

**Setup:**
1. Go to your Slack workspace settings
2. Create an incoming webhook: https://api.slack.com/messaging/webhooks
3. Copy the webhook URL
4. Add to configuration or set `SLACK_WEBHOOK_URL` environment variable

### 2. **Discord** 🎮
Send notifications to Discord channels via webhooks.

**Setup:**
1. Go to your Discord server settings
2. Create a webhook under Integrations
3. Copy the webhook URL
4. Add to configuration or set `DISCORD_WEBHOOK_URL` environment variable

### 3. **Email** 📧
Send notifications via SMTP email.

**Setup:**
Configure SMTP server details in the configuration file or via environment variables:
- `SMTP_SERVER`
- `SMTP_PORT`
- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

**Popular SMTP Settings:**
- Gmail: `smtp.gmail.com:587` (requires app password)
- Outlook: `smtp-mail.outlook.com:587`
- SendGrid: `smtp.sendgrid.net:587`

### 4. **Generic Webhooks** 🔗
Send JSON payloads to any HTTP endpoint.

Perfect for:
- Custom integrations
- Zapier workflows
- Internal monitoring systems
- Logging services

### 5. **File Output** 📁
Write notifications to a file (JSON or text format).

Perfect for:
- CI/CD artifacts
- Audit logs
- Local development
- Debugging

## ⚙️ Setup & Configuration

### Create Configuration File

```bash
./py2to3 notify --setup
```

This creates `notification_config.json` with a template:

```json
{
  "enabled_channels": ["file"],
  "slack": {
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "username": "py2to3-bot",
    "channel": "#migration"
  },
  "discord": {
    "webhook_url": "https://discord.com/api/webhooks/YOUR/WEBHOOK/URL",
    "username": "py2to3-bot"
  },
  "webhook": {
    "url": "https://your-webhook-url.com/endpoint",
    "headers": {}
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@example.com",
    "password": "your-password",
    "from_addr": "your-email@example.com",
    "to_addrs": ["recipient@example.com"]
  },
  "file": {
    "output_path": "migration_notifications.log",
    "format": "json"
  },
  "milestones": [25, 50, 75, 100],
  "notify_on_start": true,
  "notify_on_complete": true,
  "notify_on_error": true
}
```

### Enable Channels

Edit the `enabled_channels` array to activate channels:

```json
{
  "enabled_channels": ["slack", "file"],
  ...
}
```

### Test Configuration

```bash
./py2to3 notify --test --config notification_config.json
```

Output:
```
Testing Notification Channels
✅ Slack: Working
✅ File: Working
```

## 📝 Usage Examples

### Send Manual Notification

```bash
# Basic notification
./py2to3 notify \
  --title "Migration Update" \
  --message "Completed phase 1 of migration" \
  --config notification_config.json

# Success notification
./py2to3 notify \
  --type success \
  --title "Tests Passing" \
  --message "All unit tests are now passing!" \
  --config notification_config.json

# Error notification
./py2to3 notify \
  --type error \
  --title "Build Failed" \
  --message "Syntax error in module X" \
  --config notification_config.json

# With metadata
./py2to3 notify \
  --type milestone \
  --title "50% Complete" \
  --message "Half of the files have been migrated" \
  --metadata "files_done=50" "files_total=100" "time_elapsed=2h" \
  --config notification_config.json
```

### Integration with Python Code

```python
from notification_manager import NotificationManager

# Initialize
notifier = NotificationManager('notification_config.json')

# Send milestone notification
notifier.send_milestone(
    "75% Complete",
    "Three quarters of the migration is done!",
    metadata={
        'files_migrated': 75,
        'files_total': 100,
        'issues_remaining': 12
    }
)

# Send success notification
notifier.send_success(
    "Migration Complete",
    "All files have been successfully migrated!"
)

# Send error notification
notifier.send_error(
    "Critical Issue",
    "Found syntax error in authentication module",
    metadata={'file': 'auth.py', 'line': 42}
)

# Send progress update
notifier.send_progress(
    percent=65.5,
    files_done=65,
    files_total=100,
    metadata={'eta': '2 hours'}
)
```

## 🔄 Integration with Migration Commands

The notification system can be integrated into the migration workflow:

### Automated Notifications

```python
# In your migration script
from notification_manager import NotificationManager

notifier = NotificationManager('notification_config.json')

# Start notification
notifier.send_start('my-project', files_count=100)

# During migration
for i, file in enumerate(files):
    migrate_file(file)
    
    # Send milestone notifications
    percent = ((i + 1) / len(files)) * 100
    if percent in [25, 50, 75]:
        notifier.send_milestone(
            f"{percent}% Complete",
            f"Migration milestone reached!"
        )

# Completion notification
notifier.send_complete('my-project', duration='2h 30m', stats={
    'files_migrated': 100,
    'issues_fixed': 247,
    'tests_passing': 95
})
```

### Shell Script Integration

```bash
#!/bin/bash

# Start notification
./py2to3 notify --type info --title "Migration Started" \
  --message "Beginning migration of project X" \
  --config notification_config.json

# Run migration
./py2to3 migrate src/

# Check exit code
if [ $? -eq 0 ]; then
  ./py2to3 notify --type success --title "Migration Complete" \
    --message "Successfully migrated all files" \
    --config notification_config.json
else
  ./py2to3 notify --type error --title "Migration Failed" \
    --message "Migration encountered errors" \
    --config notification_config.json
fi
```

## 🔧 CI/CD Integration

### GitHub Actions

```yaml
name: Python 2 to 3 Migration

on: [push, pull_request]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Send start notification
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          echo '{"enabled_channels": ["slack"]}' > notify_config.json
          ./py2to3 notify --type info --title "Migration Started" \
            --message "GitHub Actions migration job started" \
            --config notify_config.json
      
      - name: Run migration
        id: migrate
        run: ./py2to3 migrate src/
      
      - name: Send success notification
        if: success()
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          ./py2to3 notify --type success --title "Migration Complete" \
            --message "Migration completed successfully in GitHub Actions" \
            --config notify_config.json
      
      - name: Send failure notification
        if: failure()
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          ./py2to3 notify --type error --title "Migration Failed" \
            --message "Migration failed in GitHub Actions - check logs" \
            --config notify_config.json
```

### GitLab CI

```yaml
migrate:
  stage: build
  script:
    # Setup notification config
    - echo '{"enabled_channels": ["slack"]}' > notify_config.json
    
    # Send start notification
    - ./py2to3 notify --type info --title "Migration Started" 
        --message "GitLab CI migration started" 
        --config notify_config.json
    
    # Run migration
    - ./py2to3 migrate src/
    
  after_script:
    # Send completion notification
    - |
      if [ $CI_JOB_STATUS == 'success' ]; then
        ./py2to3 notify --type success --title "Migration Complete" 
          --message "Migration successful in GitLab CI" 
          --config notify_config.json
      else
        ./py2to3 notify --type error --title "Migration Failed" 
          --message "Migration failed in GitLab CI" 
          --config notify_config.json
      fi
  
  variables:
    SLACK_WEBHOOK_URL: $SLACK_WEBHOOK_URL
```

### Jenkins

```groovy
pipeline {
    agent any
    
    environment {
        SLACK_WEBHOOK_URL = credentials('slack-webhook')
    }
    
    stages {
        stage('Notify Start') {
            steps {
                sh '''
                    echo '{"enabled_channels": ["slack"]}' > notify_config.json
                    ./py2to3 notify --type info --title "Migration Started" \
                        --message "Jenkins pipeline started" \
                        --config notify_config.json
                '''
            }
        }
        
        stage('Migrate') {
            steps {
                sh './py2to3 migrate src/'
            }
        }
    }
    
    post {
        success {
            sh '''
                ./py2to3 notify --type success --title "Migration Complete" \
                    --message "Jenkins migration successful" \
                    --config notify_config.json
            '''
        }
        failure {
            sh '''
                ./py2to3 notify --type error --title "Migration Failed" \
                    --message "Jenkins migration failed" \
                    --config notify_config.json
            '''
        }
    }
}
```

## 🎯 Notification Types

The system supports six notification types with different styling:

| Type | Emoji | Use Case | Color |
|------|-------|----------|-------|
| `milestone` | 🎯 | Major progress milestones (25%, 50%, 75%, 100%) | Purple |
| `success` | ✅ | Successful completions, passing tests | Green |
| `error` | ❌ | Critical errors, failures | Red |
| `warning` | ⚠️ | Non-critical issues, deprecation warnings | Yellow |
| `info` | ℹ️ | General information, status updates | Blue |
| `progress` | 📊 | Progress updates with percentages | Light Blue |

## 🔐 Environment Variables

Configure notifications using environment variables (alternative to config file):

```bash
# Slack
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Discord
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK/URL"

# Generic webhook
export WEBHOOK_URL="https://your-webhook-url.com/endpoint"

# Email
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export EMAIL_USERNAME="your-email@example.com"
export EMAIL_PASSWORD="your-password"
export EMAIL_FROM="your-email@example.com"
export EMAIL_TO="recipient1@example.com,recipient2@example.com"

# File output
export NOTIFICATION_FILE="migration_notifications.log"

# Create minimal config (channels only)
cat > notification_config.json << EOF
{
  "enabled_channels": ["slack", "file"]
}
EOF

# Now use notifications
./py2to3 notify --test --config notification_config.json
```

## 🔍 Troubleshooting

### Notifications Not Sending

1. **Test channels individually:**
   ```bash
   ./py2to3 notify --test --config notification_config.json
   ```

2. **Check webhook URLs:**
   - Ensure URLs are correct and not expired
   - Test webhooks with curl:
     ```bash
     curl -X POST -H 'Content-Type: application/json' \
       -d '{"text":"Test"}' YOUR_WEBHOOK_URL
     ```

3. **Check enabled channels:**
   - Verify channels are listed in `enabled_channels`
   - Check for typos in channel names

### Email Notifications Failing

1. **Use app passwords:**
   - Gmail requires app-specific passwords
   - Generate at: https://myaccount.google.com/apppasswords

2. **Check SMTP settings:**
   - Verify server address and port
   - Ensure firewall allows SMTP connections

3. **Test SMTP connection:**
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@example.com', 'your-password')
   ```

### File Output Not Working

1. **Check file permissions:**
   ```bash
   ls -la migration_notifications.log
   ```

2. **Verify directory exists:**
   ```bash
   mkdir -p $(dirname migration_notifications.log)
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

### Verbose Debugging

Enable verbose output to see detailed error messages:

```bash
./py2to3 notify --title "Test" --message "Debug test" \
  --config notification_config.json --verbose
```

## 💡 Best Practices

### 1. **Start with File Output**
Begin testing with file output before configuring external services:
```json
{
  "enabled_channels": ["file"]
}
```

### 2. **Use Environment Variables in CI/CD**
Store sensitive credentials as secrets, not in config files:
```bash
# In CI/CD, set as environment variables
SLACK_WEBHOOK_URL=${{ secrets.SLACK_WEBHOOK_URL }}
```

### 3. **Configure Milestone Percentages**
Customize which milestones trigger notifications:
```json
{
  "milestones": [10, 25, 50, 75, 90, 100]
}
```

### 4. **Rate Limiting**
For large migrations, avoid spamming channels:
- Use milestones instead of per-file notifications
- Aggregate updates in batches
- Consider file output + periodic summaries

### 5. **Rich Metadata**
Include useful context in notifications:
```python
notifier.send_progress(
    percent=50,
    files_done=50,
    files_total=100,
    metadata={
        'branch': 'migration-sprint-2',
        'started_at': '2024-01-15 09:00',
        'eta': '2 hours',
        'velocity': '5 files/hour'
    }
)
```

## 📚 Examples

### Complete Migration Script with Notifications

```python
#!/usr/bin/env python3
"""
Complete migration script with notification integration
"""

from notification_manager import NotificationManager
from pathlib import Path
import time

def main():
    # Initialize notification system
    notifier = NotificationManager('notification_config.json')
    
    # Get files to migrate
    files = list(Path('src').rglob('*.py'))
    total = len(files)
    
    # Send start notification
    notifier.send_start('my-project', total)
    
    start_time = time.time()
    migrated = 0
    errors = []
    
    try:
        for i, file in enumerate(files):
            try:
                # Migrate file
                migrate_file(file)
                migrated += 1
                
                # Calculate progress
                percent = ((i + 1) / total) * 100
                
                # Send milestone notifications
                if int(percent) in [25, 50, 75]:
                    notifier.send_milestone(
                        f"{int(percent)}% Complete",
                        f"Migrated {migrated} of {total} files",
                        metadata={
                            'files_migrated': migrated,
                            'files_total': total,
                            'errors': len(errors)
                        }
                    )
            
            except Exception as e:
                errors.append(f"{file}: {str(e)}")
                notifier.send_warning(
                    f"Error in {file.name}",
                    str(e)
                )
        
        # Send completion notification
        duration = time.time() - start_time
        duration_str = f"{int(duration // 60)}m {int(duration % 60)}s"
        
        notifier.send_complete(
            'my-project',
            duration_str,
            stats={
                'files_migrated': migrated,
                'files_total': total,
                'errors': len(errors),
                'success_rate': f"{(migrated / total) * 100:.1f}%"
            }
        )
    
    except KeyboardInterrupt:
        notifier.send_error(
            "Migration Interrupted",
            f"Migration stopped by user after {migrated} files"
        )
        raise

if __name__ == '__main__':
    main()
```

## 🤝 Contributing

Have ideas for new notification channels or features?
- Open an issue on GitHub
- Submit a pull request
- Share your integration examples

## 📄 License

Part of the py2to3 Migration Toolkit - MIT License
