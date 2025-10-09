# Redo Manager Guide 🔄

**Reapply rolled back migration operations with confidence**

The Redo Manager complements the Rollback Manager by allowing you to reapply migration operations that were previously rolled back. This is useful when you need to temporarily undo changes for testing or debugging, then reapply them later.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Use Cases](#use-cases)
- [Commands](#commands)
- [Workflow Examples](#workflow-examples)
- [Safety Features](#safety-features)
- [Best Practices](#best-practices)
- [Integration with Other Tools](#integration-with-other-tools)

## Overview

The Redo Manager provides a safe and efficient way to reapply migration operations that have been rolled back. It works seamlessly with the existing Rollback Manager to give you full control over your migration history.

### Key Features

- ✅ **Safe Reapplication**: Creates backups before redoing operations
- 🔍 **Preview Changes**: See what will be reapplied before committing
- 📋 **Operation Tracking**: List all operations that can be redone
- 🎯 **Selective Redo**: Choose specific operations to reapply
- 🛡️ **Force Mode**: Handle missing backups gracefully
- 📊 **Detailed Reports**: Get comprehensive feedback on redo operations

## Quick Start

### List Rolled Back Operations

See what operations can be redone:

```bash
./py2to3 redo list
```

### Preview a Redo

Preview what will be reapplied without making changes:

```bash
# Preview last rolled back operation
./py2to3 redo preview

# Preview specific operation
./py2to3 redo preview --id 20240115_143022_123456
```

### Reapply an Operation

Redo the last rolled back operation:

```bash
./py2to3 redo apply
```

Redo a specific operation:

```bash
./py2to3 redo apply --id 20240115_143022_123456
```

## Use Cases

### 1. Testing and Validation

Rollback to test your code without migration changes, then redo when ready:

```bash
# Rollback to test original code
./py2to3 rollback undo --yes

# Run tests on original code
pytest tests/

# Redo the migration when satisfied
./py2to3 redo apply --yes
```

### 2. Iterative Migration

Rollback to make manual adjustments, then redo with improvements:

```bash
# Rollback the migration
./py2to3 rollback undo

# Make manual code adjustments
vim src/myfile.py

# Redo the migration
./py2to3 redo apply
```

### 3. Branch Switching

Maintain different migration states across branches:

```bash
# On feature branch - rollback migrations
git checkout feature-branch
./py2to3 rollback undo --yes

# Switch to main branch and redo
git checkout main
./py2to3 redo apply --yes
```

### 4. Debugging Issues

Quickly toggle between migrated and original code:

```bash
# Rollback to debug
./py2to3 rollback undo --yes

# Debug the original code
python -m pdb src/myfile.py

# Redo when done
./py2to3 redo apply --yes
```

## Commands

### `redo list`

List all rolled back operations that can be redone.

```bash
./py2to3 redo list
```

**Options:**
- `-v, --verbose`: Show detailed information about each operation

**Example Output:**
```
Found 2 rolled back operation(s) that can be redone:

↻ 20240115_143022_123456
  Type: fix
  Time: 2024-01-15T14:30:22.123456
  Description: Applied Python 2 to 3 fixes
  Files: 5
  Rolled back: 2024-01-15T15:45:30.789012

↻ 20240115_120015_987654
  Type: modernize
  Time: 2024-01-15T12:00:15.987654
  Description: Code modernization
  Files: 3
  Rolled back: 2024-01-15T14:20:10.456789
```

### `redo preview`

Preview what will be reapplied without making changes.

```bash
# Preview last rolled back operation
./py2to3 redo preview

# Preview specific operation
./py2to3 redo preview --id 20240115_143022_123456
```

**Options:**
- `--id`: Specific operation ID to preview (default: last rolled back operation)

**Example Output:**
```
Operation ID: 20240115_143022_123456
Type: fix
Original timestamp: 2024-01-15T14:30:22.123456
Rolled back at: 2024-01-15T15:45:30.789012
Description: Applied Python 2 to 3 fixes

Files that can be reapplied: 5
  ✓ src/core/engine.py
  ✓ src/data/processor.py
  ✓ src/web/scraper.py
  ✓ src/utils/helpers.py
  ✓ src/models/user.py
```

### `redo apply`

Reapply a rolled back migration operation.

```bash
# Redo last rolled back operation
./py2to3 redo apply

# Redo specific operation
./py2to3 redo apply --id 20240115_143022_123456

# Dry run (preview only)
./py2to3 redo apply --dry-run

# Skip confirmation prompt
./py2to3 redo apply --yes

# Force redo even with missing backups
./py2to3 redo apply --force
```

**Options:**
- `--id`: Specific operation ID to redo (default: last rolled back operation)
- `-n, --dry-run`: Preview redo without making changes
- `-y, --yes`: Skip confirmation prompt
- `--force`: Force redo even if some backups are missing
- `-v, --verbose`: Show detailed information

**Example Output:**
```
====================================================================================
                                  Redo Manager                                    
====================================================================================

ℹ Redoing last rolled back operation...

ℹ Operation ID: 20240115_143022_123456
ℹ Type: fix
ℹ Original timestamp: 2024-01-15T14:30:22.123456
ℹ Rolled back at: 2024-01-15T15:45:30.789012
ℹ Description: Applied Python 2 to 3 fixes

ℹ Files to reapply: 5/5

⚠ Proceed with redo? (y/N): y

✓ Successfully reapplied operation 20240115_143022_123456
ℹ Reapplied 5 file(s)
```

## Workflow Examples

### Complete Rollback-Redo Cycle

```bash
# 1. Check operation history
./py2to3 rollback list

# 2. Rollback an operation
./py2to3 rollback undo --yes

# 3. Verify the rollback
./py2to3 check src/

# 4. List what can be redone
./py2to3 redo list

# 5. Preview the redo
./py2to3 redo preview

# 6. Redo the operation
./py2to3 redo apply --yes
```

### Multiple Rollback-Redo Operations

```bash
# Rollback the last 3 operations
./py2to3 rollback undo --yes
./py2to3 rollback undo --yes
./py2to3 rollback undo --yes

# List all rolled back operations
./py2to3 redo list

# Redo them in reverse order (oldest first)
./py2to3 redo apply --id 20240115_120015_987654 --yes
./py2to3 redo apply --id 20240115_140030_555555 --yes
./py2to3 redo apply --id 20240115_143022_123456 --yes
```

### Selective Redo

```bash
# List all rolled back operations
./py2to3 redo list

# Preview multiple operations
./py2to3 redo preview --id 20240115_120015_987654
./py2to3 redo preview --id 20240115_143022_123456

# Redo only specific operations you want
./py2to3 redo apply --id 20240115_120015_987654 --yes
# Skip the middle one
./py2to3 redo apply --id 20240115_143022_123456 --yes
```

## Safety Features

### 1. Automatic Backups

Before redoing any operation, the current state is backed up:

```bash
./py2to3 redo apply
# Creates backups in .migration_history/redo_backups/
```

This means you can safely rollback the redo if needed!

### 2. Preview Mode

Always preview changes before applying:

```bash
# Preview to see exactly what will be reapplied
./py2to3 redo preview

# Then apply if satisfied
./py2to3 redo apply
```

### 3. Dry Run Mode

Test the redo without making actual changes:

```bash
./py2to3 redo apply --dry-run
```

### 4. Confirmation Prompts

Interactive confirmation before reapplying changes:

```bash
./py2to3 redo apply
# Prompts: "Proceed with redo? (y/N):"
```

Skip with `--yes` flag for automation:

```bash
./py2to3 redo apply --yes
```

### 5. Missing Backup Detection

Automatically detects and reports missing backups:

```bash
./py2to3 redo preview
# Shows: "Files with missing backups: 1"
```

Use `--force` to proceed anyway:

```bash
./py2to3 redo apply --force
```

## Best Practices

### 1. Always Preview First

Before redoing an operation, preview it to understand the impact:

```bash
./py2to3 redo preview
./py2to3 redo apply
```

### 2. Keep Backups Safe

The redo feature relies on backups from the original migration. Don't delete `.migration_history/` directory:

```bash
# ❌ Don't do this
rm -rf .migration_history/

# ✅ Keep backups safe
# Add to .gitignore but keep locally
```

### 3. Use Dry Run for Testing

Test redos in dry run mode first:

```bash
./py2to3 redo apply --dry-run
# Review output
./py2to3 redo apply --yes
```

### 4. Document Your Workflow

Keep track of why you're rolling back and redoing:

```bash
# Add to journal
./py2to3 journal add "Rolling back to test original behavior"
./py2to3 rollback undo --yes

# Test and verify
pytest tests/

# Add journal entry
./py2to3 journal add "Redoing migration after successful tests"
./py2to3 redo apply --yes
```

### 5. Regular History Review

Periodically review your operation history:

```bash
./py2to3 rollback list --all
./py2to3 rollback stats
```

### 6. Clean Up Old Operations

Clear old operations that are no longer needed:

```bash
# Keep only last 10 operations
./py2to3 rollback clear --keep 10
```

## Integration with Other Tools

### With Git

Combine redo with Git operations:

```bash
# Create checkpoint before rollback
./py2to3 git checkpoint "Before testing rollback"

# Rollback for testing
./py2to3 rollback undo --yes

# Test changes
pytest tests/

# Redo if tests pass
./py2to3 redo apply --yes

# Commit the result
./py2to3 git commit "after-redo-test" -m "Verified migration works correctly"
```

### With Journal

Track your redo operations in the journal:

```bash
# Before redo
./py2to3 journal add "About to redo fix operation - previous rollback for debugging"

# Redo operation
./py2to3 redo apply --yes

# After redo
./py2to3 journal add "Successfully reapplied fix operation - all tests passing"
```

### With CI/CD

Use redo in automated workflows:

```yaml
# .github/workflows/test-migration.yml
- name: Test Migration Stability
  run: |
    # Apply migration
    ./py2to3 fix src/ --yes
    
    # Run tests with migration
    pytest tests/
    
    # Rollback
    ./py2to3 rollback undo --yes
    
    # Run tests without migration
    pytest tests/
    
    # Redo migration
    ./py2to3 redo apply --yes
    
    # Final tests
    pytest tests/
```

### With Recipes

Create recipes that include redo operations:

```bash
# Create a recipe
./py2to3 recipe create test-rollback-redo

# Add steps to recipe
./py2to3 recipe add-step test-rollback-redo \
  "rollback undo --yes" \
  "Rollback last operation"

./py2to3 recipe add-step test-rollback-redo \
  "redo apply --yes" \
  "Redo last operation"

# Run the recipe
./py2to3 recipe run test-rollback-redo
```

## Troubleshooting

### No Rolled Back Operations Found

```bash
./py2to3 redo list
# Warning: No rolled back operations found
```

**Solution**: First rollback an operation:
```bash
./py2to3 rollback undo
./py2to3 redo list
```

### Missing Backup Files

```bash
./py2to3 redo preview
# Warning: Files with missing backups: 2
```

**Solution**: Use force mode or re-apply the original migration:
```bash
# Option 1: Force redo
./py2to3 redo apply --force

# Option 2: Re-apply original migration
./py2to3 fix src/
```

### Operation Not Rolled Back

```bash
./py2to3 redo apply --id 20240115_143022_123456
# Error: Operation 20240115_143022_123456 has not been rolled back
```

**Solution**: Check the operation status:
```bash
./py2to3 rollback list --all
# Find operations marked as rolled back
```

## Summary

The Redo Manager provides powerful capabilities for managing your migration workflow:

- ✅ **Safe**: Automatic backups before reapplying changes
- 🔍 **Transparent**: Preview and dry-run modes
- 🎯 **Flexible**: Selective redo of specific operations
- 📊 **Trackable**: Comprehensive operation history
- 🛡️ **Robust**: Handles edge cases gracefully

Use it alongside the Rollback Manager for complete control over your Python 2 to 3 migration!

## Related Guides

- [ROLLBACK_GUIDE.md](ROLLBACK_GUIDE.md) - Rollback Manager documentation
- [BACKUP_GUIDE.md](BACKUP_GUIDE.md) - Backup system documentation
- [GIT_INTEGRATION.md](GIT_INTEGRATION.md) - Git integration features
- [JOURNAL_GUIDE.md](JOURNAL_GUIDE.md) - Migration journal documentation
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI reference
