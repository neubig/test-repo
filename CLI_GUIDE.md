# py2to3 CLI Tool Guide

A comprehensive command-line interface for Python 2 to Python 3 migration.

## Overview

The `py2to3` CLI tool provides a unified, user-friendly interface for the entire Python 2 to 3 migration process. It combines the fixer, verifier, and report generator into a single tool with beautiful colored output, progress indicators, and helpful error messages.

## Installation

### Option 1: Direct Usage (No Installation Required)

Simply run the tool directly from the repository:

```bash
./py2to3 --help
```

### Option 2: Install as a Package

Install the tool to make it available system-wide:

```bash
pip install -e .
```

Then you can run it from anywhere:

```bash
py2to3 --help
```

## Commands

### 1. `check` - Verify Python 3 Compatibility

Check your code for Python 3 compatibility issues without making any changes.

**Usage:**
```bash
py2to3 check <path> [options]
```

**Examples:**
```bash
# Check a single file
py2to3 check myfile.py

# Check an entire directory
py2to3 check src/

# Save results to a report file
py2to3 check src/ --report compatibility_report.txt
```

**Options:**
- `path`: File or directory to check (required)
- `-r, --report FILE`: Save report to file
- `-v, --verbose`: Enable verbose output

### 2. `fix` - Automatically Convert Python 2 to Python 3

Automatically apply fixes to convert Python 2 code to Python 3.

**Usage:**
```bash
py2to3 fix <path> [options]
```

**Examples:**
```bash
# Fix a single file (will prompt for confirmation)
py2to3 fix myfile.py

# Fix an entire directory with custom backup location
py2to3 fix src/ --backup-dir my_backups

# Dry run - see what would be changed without modifying files
py2to3 fix src/ --dry-run

# Skip confirmation prompt
py2to3 fix src/ --yes

# Save detailed report of fixes
py2to3 fix src/ --report fixes_applied.txt
```

**Options:**
- `path`: File or directory to fix (required)
- `-b, --backup-dir DIR`: Backup directory (default: backup)
- `-n, --dry-run`: Show changes without modifying files
- `-y, --yes`: Skip confirmation prompt
- `-r, --report FILE`: Save report to file
- `-v, --verbose`: Enable verbose output

### 3. `report` - Generate HTML Migration Report

Create a comprehensive HTML report with visualizations and statistics.

**Usage:**
```bash
py2to3 report [options]
```

**Examples:**
```bash
# Generate a basic report
py2to3 report

# Custom output file
py2to3 report --output my_migration_report.html

# Include data from a specific path
py2to3 report --scan-path src/ --output report.html
```

**Options:**
- `-o, --output FILE`: Output HTML file (default: migration_report.html)
- `-s, --scan-path PATH`: Path to scan for migration data
- `--include-fixes`: Include fixes in report (default: true)
- `--include-issues`: Include issues in report (default: true)
- `-v, --verbose`: Enable verbose output

### 4. `migrate` - Complete Migration Workflow

Run the complete migration process: fix → verify → report (all in one command).

**Usage:**
```bash
py2to3 migrate <path> [options]
```

**Examples:**
```bash
# Run complete migration (will prompt for confirmation)
py2to3 migrate src/

# Skip confirmation and use custom paths
py2to3 migrate src/ --yes --backup-dir backups --output full_report.html
```

**Options:**
- `path`: File or directory to migrate (required)
- `-b, --backup-dir DIR`: Backup directory (default: backup)
- `-o, --output FILE`: Output report base name (default: migration_report.html)
- `-y, --yes`: Skip confirmation prompt
- `-v, --verbose`: Enable verbose output

**What it does:**
1. **Initial Check**: Runs compatibility check and saves issues to `{output}.pre-fix-issues.txt`
2. **Apply Fixes**: Automatically fixes Python 2 code and saves report to `{output}.fixes-applied.txt`
3. **Post-Fix Check**: Verifies remaining issues and saves to `{output}.post-fix-issues.txt`
4. **Generate Report**: Creates comprehensive HTML report at `{output}`

## Global Options

These options work with all commands:

- `--version`: Show version information
- `--no-color`: Disable colored output (useful for CI/CD)
- `-v, --verbose`: Enable verbose output
- `-h, --help`: Show help message

## Examples

### Typical Workflow

```bash
# 1. First, check what issues exist
./py2to3 check src/ --report initial_issues.txt

# 2. Apply fixes (with dry-run first to be safe)
./py2to3 fix src/ --dry-run

# 3. Apply fixes for real
./py2to3 fix src/ --backup-dir backups

# 4. Check remaining issues
./py2to3 check src/ --report remaining_issues.txt

# 5. Generate final report
./py2to3 report --scan-path src/ --output migration_report.html
```

### Quick Migration

```bash
# Or just do everything in one command!
./py2to3 migrate src/ --yes --output complete_migration.html
```

### CI/CD Integration

```bash
# Check compatibility in CI without colors
py2to3 check src/ --no-color --report ci_report.txt
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "Python 3 compatibility issues found!"
    exit 1
fi
```

## Features

### Beautiful Output

- **Colored terminal output** for better readability
- **Progress indicators** to track operations
- **Formatted summaries** with statistics
- **Clear error messages** with helpful suggestions

### Safety Features

- **Automatic backups** before making changes
- **Dry-run mode** to preview changes
- **Confirmation prompts** for destructive operations
- **Comprehensive error handling**

### Comprehensive Reports

- Detailed text reports for each operation
- Beautiful HTML reports with visualizations
- Statistics on fixes applied and issues found
- Before/after code comparisons

## Tips

1. **Always start with `--dry-run`** to see what will be changed
2. **Use `check` before `fix`** to understand the scope of changes
3. **Keep the backup directory** until you've thoroughly tested the migrated code
4. **Review the HTML report** to understand all changes made
5. **Use `--no-color` in scripts** and CI/CD pipelines
6. **Enable `--verbose`** when debugging issues

## Troubleshooting

### "Command not found" error

If running `py2to3` gives a "command not found" error:
- If not installed: Use `./py2to3` from the repository root
- If installed: Make sure your Python scripts directory is in your PATH

### Import errors

If you see import errors for fixer, verifier, or report_generator:
- Make sure you're running from the repository root
- Or install the package with `pip install -e .`

### No color output in CI/CD

Some CI/CD systems don't support colored output. Use `--no-color` flag to disable it.

## Contributing

We welcome contributions! To add new features or patterns:

1. Add your fix pattern to `src/fixer.py`
2. Add verification logic to `src/verifier.py`
3. Update the CLI tool if needed
4. Submit a pull request

## License

This tool is part of the py2to3-toolkit and is available under the MIT License.
