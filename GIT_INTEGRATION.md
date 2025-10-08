# Git Integration Guide

## Overview

The **Git Integration** feature provides seamless version control for your Python 2 to 3 migration workflow. It automatically creates commits with detailed migration statistics, manages migration branches, and enables easy rollback of changes.

This guide covers all aspects of using git integration with the py2to3 migration toolkit.

## Table of Contents

- [Why Use Git Integration?](#why-use-git-integration)
- [Getting Started](#getting-started)
- [Commands Reference](#commands-reference)
- [Workflows](#workflows)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Why Use Git Integration?

Git integration provides several benefits for migration projects:

1. **Automatic Version Control**: Every migration step is tracked in git with detailed commit messages
2. **Easy Rollback**: Quickly revert to any previous state if issues arise
3. **Team Collaboration**: Share migration progress with team members through git
4. **Code Review**: Review migration changes before merging to main branch
5. **Audit Trail**: Maintain a complete history of migration decisions and changes
6. **Safety Net**: Combined with backups, provides multiple layers of protection
7. **Migration Statistics**: Commit messages include detailed statistics about changes

## Getting Started

### Prerequisites

- Git must be installed and available in your PATH
- Either an existing git repository or ability to create one

### Checking Repository Status

First, check if you're in a git repository:

```bash
./py2to3 git info
```

This will show:
- Current branch
- Repository status (clean or modified)
- Total number of commits
- Remote URL (if configured)
- Last commit information
- Migration commit count and history

### Initializing Git (if needed)

If you're not in a git repository, initialize one:

```bash
./py2to3 git init
```

## Commands Reference

### `git status`

Show the current git status of migration files.

```bash
./py2to3 git status
```

**Output includes:**
- Current branch name
- Working directory status (clean/modified)
- Modified files (M)
- Added files (A)
- Deleted files (D)
- Untracked files (?)

### `git info`

Display comprehensive repository information.

```bash
./py2to3 git info
```

**Output includes:**
- Repository details (branch, status, commit count)
- Remote URL (if configured)
- Last commit information
- Migration-specific statistics

### `git init`

Initialize a new git repository (if not already initialized).

```bash
./py2to3 git init
```

**Note:** This command is safe - it will not reinitialize an existing repository.

### `git branch`

Create a new migration branch.

```bash
# Auto-generate branch name with timestamp
./py2to3 git branch

# Specify custom branch name
./py2to3 git branch my-migration-branch
```

**Auto-generated format:** `py2to3-migration-YYYYMMDD-HHMMSS`

### `git checkpoint`

Create a simple git commit checkpoint.

```bash
# Basic checkpoint
./py2to3 git checkpoint "Migration checkpoint message"

# Checkpoint with tag
./py2to3 git checkpoint "Pre-migration baseline" --tag baseline
```

**Tags are prefixed with:** `py2to3-migration-`

### `git commit`

Create a migration commit with detailed statistics.

```bash
# Basic migration commit
./py2to3 git commit "fixes-applied"

# With statistics from JSON file
./py2to3 git commit "fixes-applied" -s migration-stats.json

# With additional message
./py2to3 git commit "verified" -m "All tests passed"
```

**Commit message includes:**
- Migration phase identifier
- Timestamp
- Migration statistics (if provided)
- Additional notes (if provided)
- Migration toolkit signature

### `git log`

Show migration commit history.

```bash
# Show last 10 migration commits (default)
./py2to3 git log

# Show last 20 migration commits
./py2to3 git log -n 20
```

**Note:** Only shows commits created by py2to3 (prefix: `py2to3:`)

### `git rollback`

Rollback to a previous migration state.

```bash
# Rollback to last migration commit
./py2to3 git rollback

# Rollback to specific commit
./py2to3 git rollback abc1234

# Hard reset (discard all changes)
./py2to3 git rollback --hard

# Skip confirmation
./py2to3 git rollback -y
```

**Reset types:**
- **Mixed (default):** Preserve changes as unstaged
- **Hard (`--hard`):** Discard all changes (use with caution!)

### `git diff`

Show differences between commits or working directory.

```bash
# Show unstaged changes
./py2to3 git diff

# Show changes between HEAD and working directory
./py2to3 git diff HEAD

# Show changes between two commits
./py2to3 git diff abc1234 def5678

# Show changes between HEAD and previous commit
./py2to3 git diff HEAD~1 HEAD
```

## Workflows

### Workflow 1: Basic Migration with Git Tracking

```bash
# 1. Check repository status
./py2to3 git info

# 2. Create migration branch
./py2to3 git branch

# 3. Create pre-migration checkpoint
./py2to3 git checkpoint "Pre-migration baseline" --tag baseline

# 4. Run preflight checks
./py2to3 preflight src/

# 5. Apply fixes
./py2to3 fix src/

# 6. Create post-fix commit
./py2to3 git commit "fixes-applied" -m "Applied Python 2 to 3 fixes"

# 7. Run verification
./py2to3 check src/

# 8. Create verification commit
./py2to3 git commit "verified" -m "Verification complete"

# 9. Generate report
./py2to3 report -s src/ -o migration_report.html

# 10. View migration history
./py2to3 git log
```

### Workflow 2: Migration with Rollback

```bash
# 1. Create checkpoint before making changes
./py2to3 git checkpoint "Before applying fixes"

# 2. Apply fixes
./py2to3 fix src/

# 3. Test the changes
pytest  # or your test command

# 4a. If tests pass - commit
./py2to3 git commit "fixes-applied"

# 4b. If tests fail - rollback
./py2to3 git rollback --hard
```

### Workflow 3: Team Migration Workflow

```bash
# Team Lead:
# 1. Create and push migration branch
./py2to3 git branch team-py2to3-migration
git push -u origin team-py2to3-migration

# 2. Create initial checkpoint
./py2to3 git checkpoint "Migration started"
git push

# Team Member:
# 3. Pull migration branch
git pull origin team-py2to3-migration

# 4. Work on specific module
./py2to3 fix src/module1/

# 5. Commit changes
./py2to3 git commit "module1-migrated"
git push

# 6. View team's migration progress
./py2to3 git log -n 20
```

## Best Practices

### 1. Create Checkpoints Frequently

Create checkpoints at key migration milestones:
- Before starting migration
- After fixing each major module
- After verification passes
- Before and after manual fixes

### 2. Use Descriptive Branch Names

```bash
# Good branch names
./py2to3 git branch py2to3-auth-module
./py2to3 git branch py2to3-database-migration
./py2to3 git branch py2to3-sprint-42

# Less descriptive (but still auto-generated is fine)
./py2to3 git branch
```

### 3. Leverage Tags for Milestones

```bash
./py2to3 git checkpoint "Baseline before migration" --tag baseline
./py2to3 git checkpoint "All core modules migrated" --tag core-complete
./py2to3 git checkpoint "Migration complete" --tag complete
```

### 4. Review Changes Before Committing

```bash
# Review what will be committed
./py2to3 git status
./py2to3 git diff

# Then commit
./py2to3 git checkpoint "Description of changes"
```

### 5. Use Soft Rollback by Default

```bash
# Preserve changes (you can review and re-commit)
./py2to3 git rollback

# Only use --hard when you're absolutely sure
./py2to3 git rollback --hard
```

### 6. Combine with Backup System

Git integration works alongside the backup system:

```bash
# Backups protect individual files
./py2to3 backup list

# Git protects the entire project state
./py2to3 git log
```

### 7. Document Migration Progress

Use commit messages to document decisions:

```bash
./py2to3 git commit "manual-fixes" -m "Fixed complex dictionary iteration in auth.py. Used list() wrapper instead of .items() due to mutation during iteration."
```

## Examples

### Example 1: Review Changes Before Committing

```bash
$ ./py2to3 fix src/auth/

# Review what changed
$ ./py2to3 git diff

# Review affected files
$ ./py2to3 git status

# Commit if satisfied
$ ./py2to3 git commit "auth-module-fixed"
```

### Example 2: Rollback Failed Migration

```bash
$ ./py2to3 fix src/

# Oops! Something broke
$ pytest
# Tests fail...

# Rollback to previous state
$ ./py2to3 git rollback --hard

# Try again with different approach
$ ./py2to3 fix src/ --dry-run
```

### Example 3: Track Migration Progress

```bash
# Start migration
$ ./py2to3 git checkpoint "Starting migration - Day 1"

# Work on it...
$ ./py2to3 fix src/module1/
$ ./py2to3 git commit "module1-complete"

# Next day...
$ ./py2to3 fix src/module2/
$ ./py2to3 git commit "module2-complete"

# View progress
$ ./py2to3 git log
1. a1b2c3d4
   py2to3: module2-complete
   2024-01-15 10:30:00 +0000

2. e5f6g7h8
   py2to3: module1-complete
   2024-01-14 16:45:00 +0000

3. i9j0k1l2
   py2to3: Starting migration - Day 1
   2024-01-14 09:00:00 +0000
```

### Example 4: Migration with Statistics

```bash
# Run migration with statistics tracking
$ ./py2to3 stats collect src/ --save

# Apply fixes
$ ./py2to3 fix src/

# Collect post-fix stats
$ ./py2to3 stats collect src/ --save

# Export stats to JSON
$ ./py2to3 stats show > migration-stats.json

# Create commit with statistics
$ ./py2to3 git commit "fixes-applied" -s migration-stats.json
```

## Troubleshooting

### Problem: "Not a git repository"

**Solution:**
```bash
./py2to3 git init
```

### Problem: "Failed to create commit: nothing to commit"

**Cause:** No changes have been made since last commit.

**Solution:** Make changes first, or verify with:
```bash
./py2to3 git status
```

### Problem: "Failed to create branch"

**Cause:** Branch name already exists.

**Solution:** Use a different branch name or switch to existing branch:
```bash
git checkout existing-branch-name
```

### Problem: Git command timed out

**Cause:** Very large repository or network issues (for remote operations).

**Solution:** 
- For local operations: Check repository integrity
- For remote operations: Check network connection
- Consider using git directly for large operations

### Problem: "Git is not installed"

**Solution:** Install git:
```bash
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com/
```

### Problem: Rollback didn't work as expected

**Understanding reset types:**
- `--mixed` (default): Keeps changes as unstaged files
- `--hard`: Completely discards changes

**To check status after rollback:**
```bash
./py2to3 git status
./py2to3 git diff
```

## Advanced Usage

### Integrating with CI/CD

```yaml
# .github/workflows/migration.yml
name: Python 2 to 3 Migration

on: [push]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Run preflight checks
        run: ./py2to3 preflight src/ --json > preflight.json
      
      - name: Create migration branch
        run: ./py2to3 git branch ci-migration-${{ github.run_number }}
      
      - name: Apply fixes
        run: ./py2to3 fix src/ -y
      
      - name: Create migration commit
        run: ./py2to3 git commit "ci-fixes-applied"
      
      - name: Run tests
        run: pytest
      
      - name: Push if tests pass
        run: git push origin HEAD
```

### Using with Pre-commit Hooks

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Verify migration status before committing

./py2to3 check src/ || {
    echo "Python 3 compatibility issues found!"
    echo "Run './py2to3 fix src/' to fix them."
    exit 1
}
```

### Exporting Migration History

```bash
# Export migration commits to JSON
./py2to3 git log -n 100 | grep "py2to3:" > migration-history.txt

# Or use git directly for more control
git log --grep="py2to3:" --pretty=format:'{"hash":"%H","date":"%ai","message":"%s"}' > migration-commits.json
```

## Related Documentation

- [CLI Guide](CLI_GUIDE.md) - Complete CLI command reference
- [Backup Guide](BACKUP_GUIDE.md) - Backup management documentation
- [Configuration Guide](CONFIG.md) - Configuration system documentation
- [README](README.md) - Main project documentation

## Contributing

Found a bug or have a feature request for git integration? Please open an issue on the project repository.

## License

This feature is part of the py2to3 migration toolkit and is available under the MIT License.
