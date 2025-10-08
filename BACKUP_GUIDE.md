# Backup Management Guide

The Python 2 to 3 migration toolkit includes comprehensive backup management features to ensure you can safely migrate your code and easily recover if needed.

## Overview

When the fixer modifies your Python files, it automatically creates backups of the original files. The backup management system provides tools to:

- **List** all available backups with detailed metadata
- **Restore** individual files or entire directories
- **Compare** backups with current files to see what changed
- **Clean up** old backups to save disk space
- **Scan** for backup integrity issues

## Quick Start

```bash
# List all available backups
./py2to3 backup list

# Restore a specific file
./py2to3 backup restore backup/src/core/main.py

# View differences between backup and current file
./py2to3 backup diff backup/src/core/main.py

# Clean up backups older than 30 days
./py2to3 backup clean --older-than 30
```

## Command Reference

### `backup list`

List all available backups with metadata including timestamps, file sizes, and original paths.

**Usage:**
```bash
./py2to3 backup list [OPTIONS]
```

**Options:**
- `-p, --pattern PATTERN` - Filter backups by pattern (matches against original path)
- `-b, --backup-dir DIR` - Specify backup directory (default: backup)

**Example:**
```bash
# List all backups
./py2to3 backup list

# List only backups for files in the 'core' directory
./py2to3 backup list --pattern core
```

**Output includes:**
- Original file path
- Backup file path
- Timestamp of backup creation
- File size
- Summary statistics (total backups, total size, oldest/newest)

### `backup restore`

Restore a file from its backup. This will overwrite the current file with the backup version.

**Usage:**
```bash
./py2to3 backup restore BACKUP_PATH [OPTIONS]
```

**Arguments:**
- `BACKUP_PATH` - Path to the backup file to restore

**Options:**
- `-t, --target PATH` - Target path to restore to (defaults to original location)
- `-n, --dry-run` - Show what would be restored without making changes
- `-y, --yes` - Skip confirmation prompt
- `-b, --backup-dir DIR` - Specify backup directory (default: backup)

**Examples:**
```bash
# Restore a file to its original location
./py2to3 backup restore backup/src/core/main.py

# Dry run to see what would happen
./py2to3 backup restore backup/src/core/main.py --dry-run

# Restore to a different location
./py2to3 backup restore backup/src/core/main.py --target /tmp/restored.py

# Skip confirmation prompt
./py2to3 backup restore backup/src/core/main.py --yes
```

**Safety:**
- By default, asks for confirmation before overwriting files
- Use `--dry-run` to preview the operation
- Original file metadata (timestamps, permissions) is preserved

### `backup diff`

Show differences between a backup and the current file using unified diff format.

**Usage:**
```bash
./py2to3 backup diff BACKUP_PATH [OPTIONS]
```

**Arguments:**
- `BACKUP_PATH` - Path to the backup file to compare

**Options:**
- `-t, --target PATH` - File to compare with (defaults to original location)
- `-c, --context N` - Number of context lines in diff (default: 3)
- `-b, --backup-dir DIR` - Specify backup directory (default: backup)

**Examples:**
```bash
# Show differences between backup and current file
./py2to3 backup diff backup/src/core/main.py

# Show more context lines
./py2to3 backup diff backup/src/core/main.py --context 10

# Compare backup with a different file
./py2to3 backup diff backup/src/core/main.py --target /tmp/other.py
```

**Output includes:**
- Unified diff format showing additions/deletions
- Line count statistics
- Color-coded output for easy reading

### `backup clean`

Remove old or unnecessary backups to free up disk space.

**Usage:**
```bash
./py2to3 backup clean [OPTIONS]
```

**Options:**
- `-o, --older-than DAYS` - Remove backups older than N days
- `-p, --pattern PATTERN` - Remove backups matching pattern
- `-a, --all` - Remove all backups
- `-n, --dry-run` - Show what would be removed without deleting
- `-y, --yes` - Skip confirmation prompt
- `-b, --backup-dir DIR` - Specify backup directory (default: backup)

**Examples:**
```bash
# Remove backups older than 30 days
./py2to3 backup clean --older-than 30

# Remove backups matching a pattern
./py2to3 backup clean --pattern "test_"

# Remove all backups (with confirmation)
./py2to3 backup clean --all

# Dry run to see what would be removed
./py2to3 backup clean --older-than 7 --dry-run

# Skip confirmation
./py2to3 backup clean --older-than 30 --yes
```

**Safety:**
- Always asks for confirmation unless `--yes` is used
- Use `--dry-run` to preview what will be deleted
- Shows count of removed backups and any errors

### `backup info`

Display detailed information about a specific backup.

**Usage:**
```bash
./py2to3 backup info BACKUP_PATH [OPTIONS]
```

**Arguments:**
- `BACKUP_PATH` - Path to the backup file

**Options:**
- `-b, --backup-dir DIR` - Specify backup directory (default: backup)

**Example:**
```bash
./py2to3 backup info backup/src/core/main.py
```

**Output includes:**
- Original file path
- Backup file path
- Creation timestamp
- File size
- Age (in days and hours)
- Status (whether backup and original files exist)
- Description (if any)

### `backup scan`

Scan the backup directory and check for inconsistencies between the filesystem and metadata.

**Usage:**
```bash
./py2to3 backup scan [OPTIONS]
```

**Options:**
- `-b, --backup-dir DIR` - Specify backup directory (default: backup)

**Example:**
```bash
./py2to3 backup scan
```

**What it checks:**
- **Orphaned files**: Backup files that exist but aren't tracked in metadata
- **Missing files**: Backups in metadata that no longer exist on disk
- Total count comparison

**Use cases:**
- Verify backup integrity after manual file operations
- Identify backups that aren't properly tracked
- Find missing backup files

## Backup Metadata

The backup system maintains metadata in `.backup_metadata.json` within the backup directory. This file tracks:

- Original file paths
- Backup file paths
- Timestamps
- File sizes
- Optional descriptions

**Note:** Don't manually edit this file unless you know what you're doing!

## Best Practices

### 1. Regular Backups Review

Periodically review your backups:

```bash
# See what backups you have
./py2to3 backup list

# Check overall stats
./py2to3 backup scan
```

### 2. Verify Changes Before Committing

Before committing migration changes, compare with backups:

```bash
# Review what changed
./py2to3 backup diff backup/src/core/main.py
```

### 3. Clean Up Old Backups

Save disk space by removing old backups:

```bash
# Remove backups older than 30 days
./py2to3 backup clean --older-than 30

# Always use dry-run first to preview
./py2to3 backup clean --older-than 30 --dry-run
```

### 4. Test Restores

Occasionally test that backups can be restored:

```bash
# Test restore with dry-run
./py2to3 backup restore backup/src/test.py --dry-run
```

### 5. Use Patterns for Selective Operations

Work with specific subsets of backups:

```bash
# List only test file backups
./py2to3 backup list --pattern "test_"

# Clean only backups from a specific directory
./py2to3 backup clean --pattern "old_code/" --yes
```

## Integration with Migration Workflow

The backup system integrates seamlessly with the migration workflow:

```bash
# 1. Check code for issues
./py2to3 check src/

# 2. Apply fixes (backups created automatically)
./py2to3 fix src/

# 3. Review what changed
./py2to3 backup list

# 4. Compare specific files
./py2to3 backup diff backup/src/core/main.py

# 5. If needed, restore a file
./py2to3 backup restore backup/src/core/main.py

# 6. Clean up after successful migration
./py2to3 backup clean --older-than 7
```

## Troubleshooting

### Backup Not Found

If you get "Backup not found in metadata":

1. Check the backup path is correct
2. Run `./py2to3 backup scan` to identify orphaned files
3. Verify the backup directory is correct

### Cannot Restore

If restore fails:

1. Check file permissions
2. Verify the original directory exists
3. Use `--dry-run` to see what would happen

### Large Backup Directory

If backups are taking up too much space:

```bash
# See total size
./py2to3 backup list

# Clean old backups
./py2to3 backup clean --older-than 30

# Or remove all after successful migration
./py2to3 backup clean --all
```

## Advanced Usage

### Scripting with Backup Commands

You can use backup commands in scripts:

```bash
#!/bin/bash
# Automated migration with backup management

# Apply fixes
./py2to3 fix src/ --yes

# List new backups
echo "Backups created:"
./py2to3 backup list

# Auto-clean old backups
./py2to3 backup clean --older-than 30 --yes

echo "Migration complete!"
```

### Custom Backup Directory

Use a different backup location:

```bash
# All commands support --backup-dir
./py2to3 fix src/ --backup-dir /path/to/backups
./py2to3 backup list --backup-dir /path/to/backups
./py2to3 backup restore /path/to/backups/file.py
```

### Batch Operations

Process multiple backups:

```bash
# List backups and process with grep/awk
./py2to3 backup list | grep "2024-" | awk '{print $2}'

# Clean by pattern
./py2to3 backup clean --pattern "temp_" --yes
```

## FAQ

**Q: Are backups created automatically?**  
A: Yes, the fixer automatically creates backups before modifying any files.

**Q: Can I restore multiple files at once?**  
A: Currently, you need to restore files individually. Use a script if you need to restore many files.

**Q: What happens if I run fix again?**  
A: New backups will be created. Old backups are preserved unless you clean them.

**Q: Can I disable backups?**  
A: While possible by modifying the code, it's strongly discouraged. Backups are your safety net!

**Q: Are backups included in version control?**  
A: No, the backup directory should be added to `.gitignore`. Backups are for local safety only.

**Q: How much disk space do backups use?**  
A: Roughly the same size as your source code. Run `./py2to3 backup list` to see total size.

**Q: Can I export backup metadata?**  
A: Yes, the metadata is stored in JSON format at `backup/.backup_metadata.json`.

## See Also

- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI documentation
- [CONFIG.md](CONFIG.md) - Configuration management
- [README.md](README.md) - Project overview and quick start

## Support

If you encounter issues with backup management:

1. Run `./py2to3 backup scan` to check for problems
2. Use `--verbose` flag for detailed error messages
3. Check file permissions in the backup directory
4. Consult the troubleshooting section above

---

**Remember:** Backups are your safety net during migration. Always verify backups exist before making major changes!
