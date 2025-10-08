
# Python 2 to Python 3 Refactoring Example

This repository contains a comprehensive example of refactoring Python 2 code to Python 3, demonstrating the use of programmatic fixer and verifier tools for automated code migration.

## Overview

This project showcases a realistic Python 2 web scraping application with complex interdependencies that needs to be upgraded to Python 3. The repository includes:

1. **A complete Python 2 application** with 10 interconnected modules
2. **A programmatic fixer tool** that automatically converts Python 2 patterns to Python 3
3. **A programmatic verifier tool** that validates Python 3 compatibility and identifies remaining issues
4. **A modern web application** using React, TypeScript, and Vite (in `/my-vite-app`)

## Directory Structure

```
test-repo/
├── README.md                 # This file
├── my-vite-app/             # Modern web application (React + TypeScript + Vite)
│   ├── README.md            # Web app documentation
│   ├── package.json         # Web app dependencies
│   ├── vite.config.ts       # Vite configuration
│   └── ...                  # Web app source files
├── src/                     # Python 2 to Python 3 refactoring example
│   ├── README.md            # Detailed documentation for the Python refactoring example
│   ├── fixer.py             # Programmatic Python 2→3 fixer tool
│   ├── verifier.py          # Python 3 compatibility verifier tool
│   ├── core/                # Core application logic
│   ├── data/                # Data processing and database
│   ├── models/              # Data models
│   ├── web/                 # Web scraping functionality
│   ├── utils/               # Utility functions and validators
│   └── tests/               # Test functionality
└── ...                      # Other configuration files
```

## Key Features

### Python 2 to Python 3 Refactoring

The `src/` directory contains a comprehensive example of a Python 2 web scraper and data processor that demonstrates numerous Python 2 patterns that need updating:

- **Print statements**: `print "message"` → `print("message")`
- **Import changes**: `urllib2` → `urllib.request`, `ConfigParser` → `configparser`, etc.
- **String handling**: `basestring` → `str`, `unicode()` issues
- **Iterator methods**: `iteritems()` → `items()`, `xrange()` → `range()`
- **Exception syntax**: `except Exception, e:` → `except Exception as e:`
- **Class definitions**: Old-style classes → new-style classes
- **Comparison**: `cmp()` function and `__cmp__` methods

### Automated Tools

1. **Unified CLI Tool (`py2to3`)** **[NEW]**:
   - Single command-line interface for the entire migration workflow
   - Beautiful colored output with progress indicators
   - Five powerful commands: `check`, `fix`, `report`, `migrate`, `config`
   - Run `./py2to3 --help` to get started! See [CLI_GUIDE.md](CLI_GUIDE.md) for details.

2. **Fixer Tool (`src/fixer.py`)**:
   - Automatically converts Python 2 code to Python 3
   - Handles common patterns, imports, syntax, and more
   - Creates backups and generates detailed reports

3. **Verifier Tool (`src/verifier.py`)**:
   - Analyzes code for Python 3 compatibility
   - Identifies remaining issues with severity classification
   - Integrates with the official 2to3 tool

4. **Report Generator (`src/report_generator.py`)** 🆕:
   - Generates comprehensive HTML reports for migration progress
   - Beautiful, interactive visualizations with charts and statistics
   - Side-by-side code comparisons showing before/after changes
   - Detailed issue tracking with severity classification
   - Export data as JSON for further analysis
   - Perfect for presenting migration progress to stakeholders
   - **See `demo_report.html` for a live example!**

5. **Configuration Management** ✨ **[NEW]**:
   - Flexible configuration system with user and project-level settings
   - JSON-based configuration files (`.py2to3.config.json`)
   - Customize default behaviors, ignore patterns, and fix rules
   - Share configuration across teams via version control
   - Manage config via CLI: `py2to3 config init`, `show`, `get`, `set`
   - **See [CONFIG.md](CONFIG.md) for complete configuration guide!**

6. **Backup Management** 🔄 **[NEW]**:
   - Comprehensive backup management for migration safety
   - List all backups with detailed information and statistics
   - Restore files or entire directories from backups
   - Clean up old backups to save disk space
   - View differences between backups and current files
   - Scan backup directory for inconsistencies
   - Perfect safety net for your migration workflow!
   - **See [BACKUP_GUIDE.md](BACKUP_GUIDE.md) for complete backup management guide!**

7. **Comprehensive Test Suite** ✅ **[NEW]**:
   - Full pytest-based test suite for all migration tools
   - Unit tests for fixer, verifier, backup manager, and config manager
   - Integration tests for complete workflows
   - Test fixtures for easy test development
   - Ensures reliability and correctness of migration tools
   - **See [tests/README.md](tests/README.md) for complete testing guide!**

### Modern Web Application

The `my-vite-app/` directory contains a modern web application built with:
- React
- TypeScript
- Vite (with HMR support)
- ESLint with TypeScript integration

## Getting Started

### Python 2 to Python 3 Refactoring

#### Quick Start (Recommended - Using the CLI Tool)

The easiest way to get started is using the unified CLI tool:

```bash
# Run the complete migration in one command
./py2to3 migrate src/ --output my_migration_report.html
```

Or use individual commands for more control:

```bash
# Check compatibility
./py2to3 check src/

# Apply fixes (with confirmation)
./py2to3 fix src/

# Generate report
./py2to3 report --scan-path src/ --output report.html
```

**NEW: Use Configuration for Convenience**

Save your preferences to avoid repeating flags:

```bash
# Initialize project configuration
./py2to3 config init

# Set your preferences
./py2to3 config set backup_dir "my_backups"
./py2to3 config set report_output "reports/migration.html"

# Now these defaults are used automatically
./py2to3 fix src/  # Uses my_backups/ directory
```

**Manage Backups**

The fixer creates backups before modifying files. You can manage these backups:

```bash
# List all available backups
./py2to3 backup list

# View detailed information about a backup
./py2to3 backup info backup/path/to/file.py

# Compare backup with current file
./py2to3 backup diff backup/path/to/file.py

# Restore a file from backup
./py2to3 backup restore backup/path/to/file.py

# Clean up old backups (older than 30 days)
./py2to3 backup clean --older-than 30

# Scan backup directory for issues
./py2to3 backup scan
```

See [CLI_GUIDE.md](CLI_GUIDE.md), [CONFIG.md](CONFIG.md), and [BACKUP_GUIDE.md](BACKUP_GUIDE.md) for complete documentation.

#### Manual Approach (Using Individual Tools)

You can also run each tool separately:

1. **Examine the Python 2 code**: Look at the various files in `src/` to understand the patterns
2. **Run the verifier**: See what issues are detected in the original code
   ```bash
   cd src
   python verifier.py .
   ```
3. **Apply the fixer**: Watch how the code is automatically transformed
   ```bash
   python fixer.py . --backup-dir backups --report fixes_applied.txt
   ```
4. **Verify results**: Check what issues remain after fixing
   ```bash
   python verifier.py . --report post_fix_verification.txt
   ```
5. **Generate HTML report**: Create a beautiful, comprehensive migration report
   ```bash
   python report_generator.py -o migration_report.html
   ```
   Open `migration_report.html` in your browser to see:
   - Interactive charts and statistics
   - Before/after code comparisons
   - Detailed fix and issue tracking
   - Progress visualization

### Web Application

1. **Navigate to the web app directory**:
   ```bash
   cd my-vite-app
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Run the development server**:
   ```bash
   npm run dev
   ```

## Testing

The toolkit includes a comprehensive test suite to ensure reliability:

```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

For more details on running and writing tests, see [tests/README.md](tests/README.md).

## Learning Points

This example demonstrates:
- Realistic complexity with genuine interdependencies
- Automated tooling for bulk conversions
- Verification importance after automated fixes
- Incremental approach to large-scale refactoring
- Best practices for backup, reporting, and validation

## Contributing

Feel free to contribute by:
- Adding more Python 2 to Python 3 conversion patterns
- Improving the fixer and verifier tools
- Enhancing the web application
- Adding documentation and examples

## License

This project is open source and available under the MIT License.
