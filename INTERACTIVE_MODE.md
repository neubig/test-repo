# Interactive Fix Mode Guide

## Overview

The **Interactive Fix Mode** provides a careful, user-controlled approach to Python 2 to 3 migration. Instead of automatically applying all fixes, it shows each proposed change and lets you decide whether to apply it. This gives you more control and confidence during the migration process.

## Why Use Interactive Mode?

Interactive mode is ideal when you:

- 🎓 **Want to learn** - See exactly what changes are being made and why
- 🔍 **Need careful control** - Review each change before it's applied
- 🛡️ **Work on critical code** - Want extra safety for production systems
- 👥 **Are training team members** - Use it as an educational tool
- ⚖️ **Have mixed Python 2/3 code** - Need to selectively apply fixes
- 🔬 **Want to understand the impact** - See context around each change

## Features

### 🎯 Precise Control
- Review each fix individually before applying it
- See context lines before and after the change
- Accept, reject, or skip changes on a per-file basis

### 📊 Rich Context Display
- View the original line and proposed fix side-by-side
- See surrounding code for better understanding
- Color-coded output for easy reading (green for fixes, red for originals)

### 🔄 Safe with Backups
- Automatic backup creation before applying changes
- Backups stored in timestamped directories
- Easy to restore if needed

### 📈 Comprehensive Statistics
- Track accepted vs. rejected fixes
- See breakdown by fix type
- List of all modified files

## Quick Start

### Basic Usage

```bash
# Run interactive mode on a directory
./py2to3 interactive src/

# Run with more context lines
./py2to3 interactive src/ --context 5

# Run without automatic backups
./py2to3 interactive src/ --no-backup
```

### Example Session

```
🔧 Interactive Python 2 to 3 Fixer
Scanning directory: /path/to/project/src

Found 15 Python files
Analyzing files for potential fixes...
  main.py: 3 fixes found
  utils.py: 2 fixes found
  models.py: 5 fixes found

Total fixes found: 10
Starting interactive review...

================================================================================
Fix 1/10: print_statement
File: /path/to/project/src/main.py:10
Description: Convert print statement to function
--------------------------------------------------------------------------------
    8 | def process_data(data):
    9 |     if not data:
-  10 |     print "No data provided"
+  10 |     print("No data provided")
   11 |         return None
   12 |     return analyze(data)
--------------------------------------------------------------------------------
Apply this fix? [y]es/[n]o/[a]ll/[q]uit/[s]kip file: y
✓ Fix accepted
```

## Interactive Commands

When reviewing each fix, you have several options:

| Command | Action | Description |
|---------|--------|-------------|
| **y** (yes) | Apply this fix | Accept and apply the current fix |
| **n** (no) | Reject this fix | Skip the current fix without applying |
| **a** (all) | Apply all remaining | Accept all remaining fixes automatically |
| **q** (quit) | Exit interactive mode | Stop and exit (already applied fixes are kept) |
| **s** (skip file) | Skip current file | Skip all remaining fixes in the current file |
| **Enter** | Default to yes | Pressing Enter accepts the fix |

## Command-Line Options

### Path (Required)

Specify the directory to analyze and fix:

```bash
./py2to3 interactive /path/to/project
```

### Context Lines (`-c`, `--context`)

Control how many lines of context to show around each fix:

```bash
# Show 5 lines before and after each change
./py2to3 interactive src/ --context 5

# Show minimal context (1 line)
./py2to3 interactive src/ --context 1

# Show extensive context (10 lines)
./py2to3 interactive src/ --context 10
```

**Default:** 3 lines

### Disable Backups (`--no-backup`)

Skip automatic backup creation:

```bash
./py2to3 interactive src/ --no-backup
```

**Note:** Only use this if you have other backup mechanisms in place (like git) or if you're certain about the changes.

## Types of Fixes Detected

Interactive mode detects and proposes fixes for common Python 2 to 3 migration issues:

### 1. Print Statements
```python
# Before
print "Hello, world"

# After
print("Hello, world")
```

### 2. Exception Syntax
```python
# Before
except ValueError, e:

# After
except ValueError as e:
```

### 3. Dictionary Iterator Methods
```python
# Before
for key, value in dict.iteritems():

# After
for key, value in dict.items():
```

### 4. Range Functions
```python
# Before
for i in xrange(100):

# After
for i in range(100):
```

### 5. Input Functions
```python
# Before
name = raw_input("Enter name: ")

# After
name = input("Enter name: ")
```

### 6. Type Changes
```python
# Before
if isinstance(s, basestring):
    text = unicode(s)

# After
if isinstance(s, str):
    text = str(s)
```

### 7. Import Updates
```python
# Before
import urllib2
import ConfigParser

# After
import urllib.request
import configparser
```

## Workflow Examples

### Example 1: Careful Migration of Critical Code

```bash
# Start interactive mode with extensive context
./py2to3 interactive src/ --context 7

# Review each fix carefully
# - Accept (y) changes that look correct
# - Reject (n) changes that need manual review
# - Skip (s) files that are complex
# - Quit (q) to stop and review so far

# After reviewing, run verification
./py2to3 check src/

# If issues remain, continue with more fixes
./py2to3 interactive src/
```

### Example 2: Educational Session

```bash
# Use interactive mode to teach Python 2 to 3 differences
./py2to3 interactive examples/

# For each fix:
# - Explain why the change is needed
# - Discuss the Python 2 vs Python 3 behavior
# - Decide as a group whether to apply it
```

### Example 3: Selective Migration

```bash
# Migrate specific subdirectories interactively
./py2to3 interactive src/core/

# Accept only certain types of fixes
# - Accept safe fixes like print statements
# - Reject complex changes for manual review later

# Run on next subdirectory
./py2to3 interactive src/utils/
```

## Understanding the Output

### Color Coding

- 🟢 **Green** - Fixed/new code to be applied
- 🔴 **Red** - Original code to be replaced
- 🔵 **Blue** - Section headers and information
- 🟡 **Yellow** - Prompts and descriptions
- ⚪ **White** - Context lines (unchanged)

### Statistics Summary

At the end of the session, you'll see a summary:

```
================================================================================
📊 Interactive Fix Summary
================================================================================
Total fixes reviewed:  25
Fixes accepted:        18
Fixes rejected:        7
Files modified:        5

Fixes by type:
  print_statement     : 8
  iterator_method     : 5
  import_update       : 3
  exception_syntax    : 2

Modified files:
  src/main.py
  src/utils.py
  src/models.py
  src/database.py
  src/validators.py
================================================================================
```

## Backup Management

Backups are stored in `backups_interactive/` with timestamps:

```
backups_interactive/
└── 20240115_143022/
    ├── main.py
    ├── utils.py
    └── models.py
```

To restore from a backup if needed:

```bash
# List available backups
ls -la backups_interactive/

# Restore a specific file
cp backups_interactive/20240115_143022/main.py src/main.py
```

Or use the backup management command:

```bash
# List all backups
./py2to3 backup list

# Restore from backup
./py2to3 backup restore backups_interactive/20240115_143022/main.py
```

## Tips and Best Practices

### 1. Start Small
Begin with a small directory or subset of files to get comfortable with the interactive mode.

```bash
./py2to3 interactive src/utils/  # Start with utilities
```

### 2. Use Version Control
Always commit your code before running interactive fixes:

```bash
git add -A
git commit -m "Pre-migration checkpoint"
./py2to3 interactive src/
```

### 3. Adjust Context as Needed
If you need more context to make decisions, increase the context lines:

```bash
./py2to3 interactive src/ --context 10
```

### 4. Combine with Other Tools
Use interactive mode in conjunction with other py2to3 tools:

```bash
# First, run preflight checks
./py2to3 preflight

# Then use interactive mode for careful migration
./py2to3 interactive src/

# Verify the results
./py2to3 check src/

# Generate a report
./py2to3 report -o migration_report.html
```

### 5. Take Breaks
For large codebases, you can quit (q) at any time. Accepted fixes are already applied, and you can resume later:

```bash
# First session - do first 50 fixes
./py2to3 interactive src/  # quit after 50

# Second session - continue with remaining files
./py2to3 interactive src/  # starts fresh
```

### 6. Use Skip for Complex Files
If a file has many fixes but you want to review it separately later:

```bash
# When prompted for a complex file, press 's' to skip
# This skips all remaining fixes in that file
```

## Integration with Existing Workflow

### With Git

```bash
# Create a migration branch
git checkout -b py3-migration

# Use interactive mode
./py2to3 interactive src/

# Commit incrementally
git add -A
git commit -m "Migrate print statements and imports"

# Continue with more fixes
./py2to3 interactive src/
git commit -am "Migrate exception handling"
```

### With Code Review

Interactive mode is perfect for preparing changes for code review:

```bash
# Apply fixes interactively
./py2to3 interactive src/

# Review changes before committing
git diff

# Commit and push for review
git commit -am "Python 2 to 3 migration: core modules"
git push origin py3-migration
```

### With Testing

```bash
# Apply some fixes
./py2to3 interactive src/

# Run tests after each session
pytest

# If tests fail, review the changes
git diff

# Revert specific files if needed
git checkout -- problematic_file.py

# Continue with remaining files
./py2to3 interactive src/
```

## Troubleshooting

### No Fixes Found

If interactive mode reports no fixes are needed:

```bash
✓ No fixes needed! Your code looks Python 3 compatible.
```

This means:
- Your code may already be Python 3 compatible
- Or the code doesn't have common Python 2 patterns
- You can verify with: `./py2to3 check src/`

### Can't See Colors

If colors are not displaying:
- Your terminal may not support ANSI colors
- The tool will automatically fall back to plain text
- You can also disable colors: `./py2to3 --no-color interactive src/`

### Interrupted Session

If you interrupt the session (Ctrl+C):
- Fixes that were already applied are kept
- You can restart and continue
- Check which files were modified: `git status`

## Frequently Asked Questions

### Q: Can I undo changes made in interactive mode?

**A:** Yes, several ways:
1. Use the automatic backups: `backups_interactive/`
2. Use git: `git checkout -- file.py`
3. Use the backup restore command: `./py2to3 backup restore`

### Q: What happens if I quit halfway through?

**A:** All fixes you've accepted up to that point are applied and saved. You can restart interactive mode later to handle remaining files.

### Q: How is this different from the regular fix command?

**A:** 
- **Regular fix (`./py2to3 fix`)**: Applies all fixes automatically
- **Interactive mode (`./py2to3 interactive`)**: Shows each fix and waits for your approval

### Q: Can I use interactive mode on a single file?

**A:** Interactive mode is designed for directories. For single files, use:
```bash
./py2to3 check single_file.py  # to see issues
./py2to3 fix single_file.py    # to fix automatically
```

### Q: Does interactive mode detect all Python 2/3 issues?

**A:** Interactive mode detects common patterns. For comprehensive analysis:
```bash
./py2to3 check src/  # Full compatibility check
./py2to3 deps src/   # Dependency analysis
./py2to3 risk src/   # Risk assessment
```

## See Also

- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI documentation
- [BACKUP_GUIDE.md](BACKUP_GUIDE.md) - Backup management
- [CONFIG.md](CONFIG.md) - Configuration options
- [GIT_INTEGRATION.md](GIT_INTEGRATION.md) - Git integration features
- [README.md](README.md) - Project overview

## Next Steps

After using interactive mode:

1. **Verify the changes**: `./py2to3 check src/`
2. **Run your tests**: `pytest` or your test command
3. **Review remaining issues**: `./py2to3 risk src/`
4. **Generate a report**: `./py2to3 report -o progress.html`
5. **Commit your changes**: `git commit -am "Interactive migration fixes"`

---

Interactive mode gives you the power to migrate with confidence. Happy migrating! 🚀
