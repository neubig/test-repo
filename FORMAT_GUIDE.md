# Code Formatting Guide

## Overview

The **format** command automatically formats your Python code using modern formatters to ensure consistent, clean, and professional code style after migration from Python 2 to Python 3.

## Features

✨ **Automatic Code Formatting**
- Uses [black](https://black.readthedocs.io/) for consistent code style
- Uses [isort](https://pycqa.github.io/isort/) for organized import statements
- Configurable line length
- Respects black's formatting philosophy

🎯 **Smart Processing**
- Format individual files or entire directories
- Recursive directory processing
- Exclude patterns to skip specific files
- Automatic detection and exclusion of virtual environments

✅ **Safe Operations**
- Check mode to preview changes without modifying files
- Detailed statistics on formatting operations
- Per-file status reporting
- Non-zero exit codes for CI/CD integration

## Why Format After Migration?

After migrating code from Python 2 to Python 3, you often end up with:
- Inconsistent spacing and indentation
- Mixed quote styles
- Unorganized imports (mixing old Python 2 and new Python 3 imports)
- Long lines that need wrapping
- Inconsistent code style across files

The `format` command solves all these issues automatically!

## Quick Start

### Format a Single File

```bash
# Format a file
./py2to3 format src/fixer.py

# Check if a file needs formatting (no changes)
./py2to3 format src/fixer.py --check
```

### Format a Directory

```bash
# Format all Python files in src/
./py2to3 format src/

# Format with custom line length
./py2to3 format src/ --line-length 100

# Format without sorting imports
./py2to3 format src/ --no-isort

# Format only top-level files (no subdirectories)
./py2to3 format src/ --no-recursive
```

### Exclude Patterns

```bash
# Exclude test files
./py2to3 format src/ --exclude test_* *_test.py

# Exclude multiple patterns
./py2to3 format src/ --exclude backup_* legacy_* temp_*
```

## Command Options

### Required Arguments

- `path` - File or directory to format

### Optional Arguments

- `-l, --line-length LENGTH` - Maximum line length (default: 88, black's default)
- `--check` - Check formatting without making changes (useful for CI/CD)
- `--no-isort` - Skip import sorting with isort
- `--no-recursive` - Do not process subdirectories
- `--exclude PATTERN [PATTERN ...]` - Patterns to exclude

## Usage Examples

### Basic Workflow

```bash
# 1. Run the migration
./py2to3 fix src/

# 2. Format the migrated code
./py2to3 format src/

# 3. Verify everything works
./py2to3 check src/
```

### CI/CD Integration

```bash
# In your CI pipeline, check if code is properly formatted
./py2to3 format src/ --check

# Exit code 0 = properly formatted
# Exit code 1 = needs formatting
```

### Selective Formatting

```bash
# Format only core modules
./py2to3 format src/core/

# Format with longer lines for data science code
./py2to3 format notebooks/ --line-length 120

# Format excluding generated files
./py2to3 format src/ --exclude *_pb2.py *_pb2_grpc.py
```

### Integration with Other Commands

```bash
# Complete migration workflow
./py2to3 wizard                    # Run migration wizard
./py2to3 format src/               # Format the code
./py2to3 quality src/              # Check code quality
./py2to3 report                    # Generate report
```

## What Gets Formatted?

### Black Formatting

Black reformats entire files in place. It will:
- Normalize string quotes
- Adjust line length and line breaks
- Fix indentation and spacing
- Format function signatures
- Organize expressions and statements
- And much more...

Black's philosophy: "Any formatting that black makes is correct." This eliminates debates about code style!

### Import Sorting (isort)

isort organizes your imports into sections:
1. Standard library imports
2. Third-party imports
3. Local application imports

It also:
- Sorts imports alphabetically within each section
- Groups imports logically
- Removes duplicate imports
- Uses black-compatible style

## Automatic Formatter Installation

The format command will automatically install black and isort if they're not available:
- Checks for formatter availability
- Attempts pip installation if missing
- Reports installation status
- Proceeds with formatting

## Output and Statistics

After formatting, you'll see:

```
======================================================================
                          FORMATTING SUMMARY                          
======================================================================
Files processed:   42
Files formatted:   18
Files unchanged:   24
Imports sorted:    18
======================================================================
```

## Best Practices

### 1. Format After Migration

Always format code after running the migration:

```bash
./py2to3 fix src/ && ./py2to3 format src/
```

### 2. Use in Pre-commit Hooks

Add formatting to your pre-commit hooks:

```bash
# Install pre-commit hooks first
./py2to3 precommit install

# Then add format check to your workflow
```

### 3. Team Standards

Set consistent line length across your team:

```bash
# Use same line length in all projects
./py2to3 format src/ --line-length 100
```

### 4. Check Before Commit

Always check formatting before committing:

```bash
# Check formatting
./py2to3 format src/ --check

# If needed, format
./py2to3 format src/

# Then commit
git commit -am "Apply formatting"
```

## Integration with Configuration

You can set default formatting options in your `.py2to3.config.json`:

```json
{
  "format": {
    "line_length": 88,
    "use_isort": true,
    "exclude_patterns": ["test_*", "*_backup.py"]
  }
}
```

## Excluded Directories

The formatter automatically excludes:
- `venv/`, `env/`, `.env/` - Virtual environments
- `__pycache__/` - Python cache
- `.git/` - Git repository
- `node_modules/` - Node.js dependencies
- `build/`, `dist/` - Build artifacts
- `.tox/` - Tox environments

## Troubleshooting

### Black Not Installing

If black fails to install automatically:

```bash
# Install manually
pip install black

# Then run format command
./py2to3 format src/
```

### Syntax Errors

If black encounters syntax errors:

```bash
# First fix syntax errors
./py2to3 check src/
./py2to3 fix src/

# Then format
./py2to3 format src/
```

### Custom Line Length Not Working

Ensure you're passing the argument correctly:

```bash
# Correct
./py2to3 format src/ --line-length 100

# Not: --line-length=100
```

### Import Sorting Issues

If isort causes issues, you can disable it:

```bash
./py2to3 format src/ --no-isort
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Modernize Guide](MODERNIZER_GUIDE.md) - Upgrade to modern Python 3 idioms
- [Quality Guide](QUALITY_GUIDE.md) - Code quality analysis
- [Pre-commit Guide](PRECOMMIT_GUIDE.md) - Automated validation hooks

## More Information

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
