# Rollback Manager Guide

## Overview

The Rollback Manager provides quick and safe rollback capabilities for migration operations. It tracks all migration operations in a history and allows you to quickly undo changes if something goes wrong.

## Key Features

- **Automatic Operation Tracking**: All migration operations are automatically tracked
- **Quick Rollback**: Undo the last operation with a single command
- **Preview Mode**: See what will be rolled back before making changes
- **Selective Rollback**: Rollback specific operations by ID
- **Safety Checks**: Preview and confirmation prompts prevent accidental rollbacks
- **Statistics**: Track rollback usage and operation history

## How It Works

The Rollback Manager works by:

1. **Recording Operations**: When you run migration commands (fix, modernize, etc.), the operation details and file changes are recorded
2. **Storing Metadata**: Each operation is assigned a unique ID and stored with timestamp, type, and file information
3. **Linking to Backups**: The rollback manager links to the backup files created during the operation
4. **Restoring Files**: During rollback, files are restored from their backups to undo the changes

## Usage

### Basic Commands

#### Undo Last Operation

Quickly undo the most recent migration operation:

```bash
./py2to3 rollback undo
```

This will:
- Show you what will be rolled back
- Ask for confirmation
- Restore all files to their previous state

#### Undo Specific Operation

Rollback a specific operation by ID:

```bash
./py2to3 rollback undo --id 20240115_143022_123456
```

#### Dry Run (Preview)

See what would be rolled back without making changes:

```bash
./py2to3 rollback undo --dry-run
```

#### Skip Confirmation

Rollback without confirmation prompt (useful for scripts):

```bash
./py2to3 rollback undo --yes
```

#### Force Rollback

Force rollback even if some backup files are missing:

```bash
./py2to3 rollback undo --force
```

⚠️ **Warning**: Use `--force` carefully as it will skip files with missing backups.

### List Operations

View all operations in the history:

```bash
./py2to3 rollback list
```

Output example:
```
✓ 20240115_143022_123456
  Type: fix
  Time: 2024-01-15T14:30:22.123456
  Description: Applied Python 2 to 3 fixes to src/
  Files: 15

✓ 20240115_142010_789012
  Type: modernize
  Time: 2024-01-15T14:20:10.789012
  Description: Modernized code patterns
  Files: 8
```

Include rolled back operations:

```bash
./py2to3 rollback list --all
```

### Preview Rollback

Preview what would be rolled back for the last operation:

```bash
./py2to3 rollback preview
```

Preview a specific operation:

```bash
./py2to3 rollback preview --id 20240115_143022_123456
```

Output example:
```
Operation ID: 20240115_143022_123456
Type: fix
Timestamp: 2024-01-15T14:30:22.123456
Description: Applied Python 2 to 3 fixes

Files that can be restored: 15
  ✓ src/core/processor.py
  ✓ src/data/database.py
  ✓ src/utils/helpers.py
  ... and 12 more
```

### Show Statistics

View rollback statistics:

```bash
./py2to3 rollback stats
```

Output example:
```
Rollback Statistics:

Total operations: 25
Active operations: 23
Rolled back: 2
Total files tracked: 347

Operations by type:
  fix: 15
  modernize: 7
  typehints: 3
```

JSON output for automation:

```bash
./py2to3 rollback stats --json
```

### Clear History

Clear the operation history:

```bash
./py2to3 rollback clear
```

Keep recent operations:

```bash
./py2to3 rollback clear --keep 10
```

This will clear all but the 10 most recent operations.

## Use Cases

### 1. Undo a Bad Fix

If automated fixes caused issues:

```bash
# See what the last operation did
./py2to3 rollback preview

# Undo it
./py2to3 rollback undo
```

### 2. Test Migration Strategies

Try different approaches and rollback if needed:

```bash
# Apply fixes
./py2to3 fix src/

# Test the results
pytest

# If tests fail, rollback
./py2to3 rollback undo

# Try a different approach
./py2to3 fix src/ --aggressive
```

### 3. Selective Rollback

Rollback a specific operation while keeping others:

```bash
# List operations to find the one you want to undo
./py2to3 rollback list

# Rollback that specific operation
./py2to3 rollback undo --id 20240115_143022_123456
```

### 4. Automated Scripts

Include rollback in automated migration scripts:

```bash
#!/bin/bash
# Apply fixes
if ./py2to3 fix src/ --yes; then
    # Run tests
    if ! pytest; then
        echo "Tests failed, rolling back..."
        ./py2to3 rollback undo --yes
        exit 1
    fi
else
    echo "Fix failed"
    exit 1
fi
```

### 5. Cleanup Old History

Periodically clean up old operation history:

```bash
# Keep only last 50 operations
./py2to3 rollback clear --keep 50 --yes
```

## Integration with Other Features

### With Backup Manager

Rollback works seamlessly with the backup system:

```bash
# Backups are created automatically
./py2to3 fix src/ --backup-dir backup

# Rollback uses those backups
./py2to3 rollback undo

# You can also manually restore from backups
./py2to3 backup restore src/myfile.py
```

### With Git Integration

Combine with git for complete version control:

```bash
# Create a checkpoint
./py2to3 git checkpoint "Before experimental fixes"

# Apply fixes
./py2to3 fix src/

# If something goes wrong, rollback
./py2to3 rollback undo

# Or use git to revert
./py2to3 git rollback
```

### With Migration State

Rollback updates work with migration state tracking:

```bash
# Check current state
./py2to3 state list

# Apply fixes
./py2to3 fix src/

# Rollback if needed
./py2to3 rollback undo

# State is updated automatically
./py2to3 state list
```

## Best Practices

### 1. Preview Before Rolling Back

Always preview what will be rolled back:

```bash
./py2to3 rollback preview
./py2to3 rollback undo --dry-run
```

### 2. Keep Recent History

Don't clear all history - keep recent operations for safety:

```bash
# Good
./py2to3 rollback clear --keep 20

# Not recommended
./py2to3 rollback clear --yes
```

### 3. Regular Backups

Ensure backups are being created:

```bash
./py2to3 backup list
./py2to3 backup stats
```

### 4. Test After Rollback

Always test after rolling back:

```bash
./py2to3 rollback undo
pytest
./py2to3 check src/
```

### 5. Document Rollbacks

Add journal entries when rolling back:

```bash
./py2to3 rollback undo
./py2to3 journal add "Rolled back aggressive fixes due to test failures"
```

## Troubleshooting

### Missing Backups

If backups are missing, you'll see a warning:

```
✗ Some backup files are missing. Use --force to rollback anyway.
```

To proceed:

```bash
./py2to3 rollback undo --force
```

⚠️ Files without backups will be skipped.

### No Operations Found

If no operations are tracked:

```
⚠ No operations found in history
ℹ Operations are tracked automatically when you use 'fix', 'modernize', etc.
```

This is normal if you haven't run any migration commands yet.

### Operation Already Rolled Back

If you try to rollback an operation that's already been rolled back:

```
✗ Operation 20240115_143022_123456 has already been rolled back
```

Use `./py2to3 rollback list --all` to see all operations including rolled back ones.

### Permission Errors

If you get permission errors during rollback:

```bash
# Run with appropriate permissions
sudo ./py2to3 rollback undo

# Or fix permissions
chmod -R u+w src/
./py2to3 rollback undo
```

## Advanced Usage

### Programmatic Access

Use the rollback manager in Python scripts:

```python
from rollback_manager import RollbackManager

manager = RollbackManager()

# Record an operation
operation_id = manager.record_operation(
    operation_type='fix',
    files=[
        {'path': 'src/myfile.py', 'backup_path': 'backup/myfile.py', 'action': 'modified'}
    ],
    description='Applied Python 2 to 3 fixes'
)

# Preview rollback
preview = manager.preview_rollback()
print(preview)

# Perform rollback
result = manager.rollback(operation_id)
print(result)

# Get statistics
stats = manager.get_statistics()
print(stats)
```

### Custom History Location

Change the history directory:

```python
manager = RollbackManager(history_dir='.custom_history')
```

### Rollback Single File

Rollback just one file from an operation:

```python
result = manager.rollback_file('src/myfile.py')
print(result)
```

## Configuration

The rollback manager uses these default locations:

- **History Directory**: `.migration_history/`
- **History File**: `.migration_history/operations.json`

These are automatically created when you run migration commands.

## Security and Safety

### What Gets Tracked

The rollback manager tracks:
- Operation ID and timestamp
- Operation type (fix, modernize, etc.)
- List of modified files
- Backup file locations
- Operation metadata

### What Doesn't Get Tracked

- File contents (stored in backups)
- User credentials
- Temporary files

### Safety Features

1. **Confirmation Prompts**: Ask before rolling back
2. **Dry Run Mode**: Preview changes first
3. **Backup Validation**: Check backups exist before restoring
4. **Error Handling**: Graceful handling of missing files
5. **Operation Tracking**: Know exactly what will be rolled back

## Examples

### Example 1: Basic Rollback Workflow

```bash
# Apply fixes
./py2to3 fix src/

# Something went wrong, check what was changed
./py2to3 rollback preview

# Rollback the changes
./py2to3 rollback undo
```

### Example 2: Multiple Operations

```bash
# Apply fixes
./py2to3 fix src/
./py2to3 modernize src/
./py2to3 typehints src/

# List all operations
./py2to3 rollback list

# Rollback just the typehints operation
./py2to3 rollback undo --id <typehints-operation-id>
```

### Example 3: Automated Testing

```bash
#!/bin/bash
set -e

# Apply fixes
./py2to3 fix src/ --yes

# Run tests
if ! pytest tests/; then
    echo "Tests failed! Rolling back..."
    ./py2to3 rollback undo --yes
    exit 1
fi

echo "Tests passed! Fixes applied successfully."
```

### Example 4: Periodic Cleanup

```bash
# Monthly cleanup script
#!/bin/bash

# Keep last 100 operations
./py2to3 rollback clear --keep 100 --yes

# Clean old backups too
./py2to3 backup clean --days 90 --yes
```

## See Also

- [Backup Management Guide](BACKUP_GUIDE.md) - Managing backups
- [Git Integration Guide](GIT_INTEGRATION.md) - Version control integration
- [CLI Guide](CLI_GUIDE.md) - All CLI commands
- [Migration Journal](JOURNAL_GUIDE.md) - Track migration progress

## Summary

The Rollback Manager is your safety net during Python 2 to 3 migration. It provides:

✅ Quick undo of migration operations
✅ Preview before rolling back
✅ Operation history tracking
✅ Integration with backups and git
✅ Safe defaults with confirmation prompts

Use it to experiment confidently, knowing you can always undo changes if needed!
