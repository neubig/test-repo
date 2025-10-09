# Documentation Modernizer Guide

The Documentation Modernizer automatically updates docstrings, comments, and inline documentation in Python files to reflect Python 3 syntax and conventions.

## Overview

During Python 2 to 3 migration, code changes are automatically handled by the fixer tool, but documentation often lags behind. Comments and docstrings frequently contain:

- Example code using Python 2 syntax (e.g., `print "hello"`)
- References to Python 2 types (e.g., `basestring`, `unicode`)
- Outdated import names (e.g., `urllib2`, `ConfigParser`)
- Python 2-specific method calls (e.g., `.iteritems()`, `xrange()`)
- Exception handling syntax from Python 2

The Documentation Modernizer scans your codebase and automatically updates documentation to match Python 3 conventions.

## Features

✨ **Automatic Pattern Detection**: Recognizes 40+ common Python 2 patterns in documentation
📝 **Safe Backup System**: Creates `.docbackup` files before making changes
📊 **Detailed Reporting**: Shows exactly what was changed and where
🔍 **Python 2 Reference Flagging**: Identifies comments mentioning Python 2 compatibility
⚡ **Fast Processing**: Efficiently handles entire directories
🔄 **Easy Restoration**: Restore original documentation from backups

## Quick Start

```bash
# Modernize documentation in a single file
./py2to3 doc-modernizer src/my_module.py

# Modernize all Python files in a directory
./py2to3 doc-modernizer src/

# Modernize with report output
./py2to3 doc-modernizer src/ -r doc_changes.txt

# Dry run - see what would be changed without modifying files
./py2to3 doc-modernizer src/ --no-backup -r preview.txt

# Restore from backups if needed
./py2to3 doc-modernizer src/ --restore
```

## What Gets Updated

### 1. Print Statements

**Before:**
```python
"""
Example usage:
    print "Hello, World!"
    print 'Debug:', value
"""
```

**After:**
```python
"""
Example usage:
    print("Hello, World!")
    print('Debug:', value)
"""
```

### 2. String Types

**Before:**
```python
"""
Args:
    text (basestring): Input text to process
    data (unicode): Unicode string data
"""
```

**After:**
```python
"""
Args:
    text (str): Input text to process
    data (str): Unicode string data
"""
```

### 3. Dictionary Methods

**Before:**
```python
"""
Iterate over items:
    for key, value in my_dict.iteritems():
        print key, value
"""
```

**After:**
```python
"""
Iterate over items:
    for key, value in my_dict.items():
        print(key, value)
"""
```

### 4. Range Functions

**Before:**
```python
# Use xrange for memory efficiency in Python 2
for i in xrange(1000000):
    process(i)
```

**After:**
```python
# Use range for memory efficiency in Python 3
for i in range(1000000):
    process(i)
```

### 5. Import Statements

**Before:**
```python
"""
Required imports:
    import ConfigParser
    import urllib2
    from Queue import Queue
"""
```

**After:**
```python
"""
Required imports:
    import configparser
    import urllib.request
    from queue import Queue
"""
```

### 6. Exception Syntax

**Before:**
```python
"""
Example:
    try:
        risky_operation()
    except Exception, e:
        print e
"""
```

**After:**
```python
"""
Example:
    try:
        risky_operation()
    except Exception as e:
        print(e)
"""
```

## Command-Line Options

### Basic Usage

```bash
./py2to3 doc-modernizer <path> [options]
```

### Options

- **`path`**: File or directory to modernize (required)
- **`-r, --report <file>`**: Save detailed report to file
- **`--no-backup`**: Do not create backup files (use with caution!)
- **`--restore`**: Restore all files from `.docbackup` backups

## Examples

### Example 1: Process a Single Module

```bash
./py2to3 doc-modernizer src/data_processor.py -r changes.txt
```

Output:
```
================================================================================
                        Documentation Modernizer                          
================================================================================

ℹ Modernizing documentation in: src/data_processor.py
ℹ Creating backups with .docbackup extension

✓ Processed src/data_processor.py
ℹ   Made 5 documentation update(s)

ℹ Generating report...
✓ Report saved to: changes.txt
```

### Example 2: Process Entire Project

```bash
./py2to3 doc-modernizer src/
```

Output:
```
================================================================================
                        Documentation Modernizer                          
================================================================================

ℹ Modernizing documentation in: src/
ℹ Creating backups with .docbackup extension

✓ Scanned 42 files
✓ Modified 18 files
✓ Total updates: 67

ℹ Generating report...

================================================================================
Documentation Modernization Report
================================================================================

Files scanned: 18
Files modified: 18
Total updates: 67
...
```

### Example 3: Review Before Applying

```bash
# First, see what would change (creates report but no backups)
./py2to3 doc-modernizer src/ -r preview.txt

# Review the report
cat preview.txt

# If satisfied, run without --no-backup
./py2to3 doc-modernizer src/
```

### Example 4: Restore from Backups

```bash
# If you need to undo the changes
./py2to3 doc-modernizer src/ --restore
```

Output:
```
✓ Restored 18 files from backups
```

## Report Format

The report shows detailed information about each change:

```
================================================================================
Documentation Modernization Report
================================================================================

Files scanned: 18
Files modified: 18
Total updates: 67

================================================================================
Detailed Changes
================================================================================

File: src/data_processor.py
--------------------------------------------------------------------------------

  Line 15:
    - Old: """Uses xrange for iteration"""
    + New: """Uses range for iteration"""

  Line 32:
    - Old: # Returns basestring type
    + New: # Returns str type

File: src/utils/validators.py
--------------------------------------------------------------------------------

  Line 8:
    ⚠ Contains Python 2 reference - consider updating
      # Compatible with Python 2.7+
...
```

## Integration with Migration Workflow

The Documentation Modernizer fits naturally into your migration workflow:

### Recommended Workflow

1. **Run Preflight Checks**
   ```bash
   ./py2to3 preflight src/
   ```

2. **Create Backup**
   ```bash
   ./py2to3 backup create
   ```

3. **Fix Code**
   ```bash
   ./py2to3 fix src/
   ```

4. **Modernize Documentation** ⬅️ New Step!
   ```bash
   ./py2to3 doc-modernizer src/ -r doc_changes.txt
   ```

5. **Run Tests**
   ```bash
   pytest
   ```

6. **Generate Report**
   ```bash
   ./py2to3 report
   ```

## Best Practices

### ✅ Do's

- **Always review the report** before committing changes
- **Run with backup enabled** (default) for safety
- **Test after modernization** to ensure examples still work
- **Commit separately** from code changes for clearer history
- **Use version control** - commit before running

### ❌ Don'ts

- **Don't skip backups** unless you're absolutely certain
- **Don't modernize generated files** (exclude build directories)
- **Don't assume all changes are perfect** - review edge cases
- **Don't forget to update README** files too

## Advanced Usage

### Exclude Specific Directories

```bash
# Process only application code, skip tests and examples
./py2to3 doc-modernizer src/ --exclude tests,examples
```

### Integration with Git

```bash
# Create a dedicated branch for documentation updates
git checkout -b docs/python3-modernization

# Modernize documentation
./py2to3 doc-modernizer src/ -r doc_modernization.txt

# Review changes
git diff

# Commit if satisfied
git add src/
git commit -m "Modernize documentation for Python 3

- Updated docstrings to use Python 3 syntax
- Changed print statements in examples
- Updated type references (basestring → str)
- Fixed import references in documentation

See doc_modernization.txt for details."
```

## Limitations

### What It Doesn't Update

The Documentation Modernizer focuses on **documentation only**. It does not:

- Modify actual Python code (use `./py2to3 fix` for that)
- Update external documentation files (README, CHANGELOG, etc.)
- Change code comments outside of docstrings (by design)
- Fix semantic meaning (only syntax patterns)

### Manual Review Needed

Some updates may need manual review:

- **Context-specific references**: Comments discussing Python 2 vs 3 differences
- **Tutorial content**: Step-by-step guides that intentionally show Python 2
- **Version-specific notes**: Compatibility matrices and version requirements
- **Historical comments**: Git commit messages or changelog entries

## Troubleshooting

### Issue: No Changes Made

**Cause**: Documentation may already be Python 3 compatible

**Solution**: Check the report - you might not need any updates!

### Issue: Too Many Changes

**Cause**: Tool is detecting patterns in unexpected places

**Solution**: Review report carefully and use `--restore` if needed

### Issue: Backups Taking Space

**Cause**: `.docbackup` files accumulate over time

**Solution**: Clean up after confirming changes:
```bash
find . -name "*.py.docbackup" -delete
```

### Issue: Want to Undo Changes

**Solution**: Use the restore feature:
```bash
./py2to3 doc-modernizer src/ --restore
```

## FAQ

**Q: Does this modify my actual code?**

A: No, it only modifies **comments and docstrings**, not the actual Python code.

**Q: Is it safe to run?**

A: Yes! Backups are created by default (`.docbackup` files), and you can always restore.

**Q: Can I preview changes first?**

A: Yes! Generate a report with `-r` flag to see all changes before applying them.

**Q: Does it work with Python 2 code?**

A: It works on any Python files, updating documentation to Python 3 conventions.

**Q: Can I customize the patterns?**

A: Currently patterns are built-in. If you need custom patterns, modify `src/doc_modernizer.py`.

**Q: Does it handle multi-line strings?**

A: Yes, it processes both single-line and multi-line docstrings.

## See Also

- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI reference
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [WIZARD_GUIDE.md](WIZARD_GUIDE.md) - Interactive migration wizard
- [PATTERNS_GUIDE.md](PATTERNS_GUIDE.md) - Python 2 to 3 pattern reference

## Support

If you encounter issues or have suggestions:
1. Check the report output for details
2. Review the backup files to see what changed
3. Use `--restore` to revert if needed
4. Report bugs with example files

## License

Part of the py2to3 migration toolkit. See main README for license information.
