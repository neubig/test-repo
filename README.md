
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
   - Six powerful commands: `check`, `preflight`, `fix`, `report`, `migrate`, `config`
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

8. **Pre-Migration Safety Checker** ✅ **[NEW]**:
   - Comprehensive environment validation before migration
   - Checks git status, disk space, file permissions, and more
   - Identifies potential issues early to prevent migration failures
   - Provides actionable fix suggestions for detected issues
   - Validates project structure and Python version compatibility
   - Estimates migration complexity and scope
   - JSON output support for CI/CD integration
   - Run `./py2to3 preflight` before starting your migration!

9. **Git Integration** 🔧 **[NEW]**:
   - Seamless git integration for tracking migration progress
   - Create migration branches and checkpoints automatically
   - Generate detailed commit messages with migration statistics
   - View migration history and rollback to previous states
   - Show git status and diff for migration changes
   - Perfect for team collaboration and code review workflows
   - Integrates with existing git repositories or creates new ones
   - Run `./py2to3 git --help` to explore git integration features!
   - **See [GIT_INTEGRATION.md](GIT_INTEGRATION.md) for complete git integration guide!**

10. **CI/CD Integration** 🚀 **[NEW]**:
   - GitHub Actions workflow for automated compatibility checking
   - Runs on every push and pull request automatically
   - Generates and uploads comprehensive reports as artifacts
   - Posts detailed results as PR comments with emoji indicators
   - Tracks migration statistics over time
   - Smart triggers - only runs when Python files change
   - Manual dispatch with configurable parameters
   - Zero configuration needed - works out of the box!
   - **See [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for complete CI/CD integration guide!**

11. **Dependency Analyzer** 📦 **[NEW]**:
   - Comprehensive dependency analysis for Python 3 compatibility
   - Scans requirements.txt, setup.py, and import statements
   - Identifies standard library module renames (urllib2 → urllib.request, etc.)
   - Detects incompatible packages and suggests alternatives
   - Recommends minimum and optimal versions for Python 3
   - Generates detailed reports in text or JSON format
   - Helps plan dependency upgrades before migration
   - Perfect for understanding the full scope of migration work!
   - Run `./py2to3 deps --help` to analyze your dependencies!
   - **See [DEPENDENCY_GUIDE.md](DEPENDENCY_GUIDE.md) for complete dependency analysis guide!**

12. **Migration Comparison Tool** 🔍:
   - Compare migration progress between different contexts
   - Compare two git branches side-by-side to evaluate different approaches
   - Compare commits to track progress over time
   - Compare different file system paths or projects
   - Get detailed metrics: progress percentage, issue counts, severity distribution
   - Identify which approach performs better with automatic winner determination
   - Generate comparison reports in text or JSON format
   - Perfect for team collaboration and evaluating migration strategies!
   - Run `./py2to3 compare --help` to explore comparison features!

13. **Risk Analyzer** ⚠️ **[LATEST]**:
   - Intelligent risk assessment of migration changes
   - Identifies high-risk changes requiring careful manual review
   - Analyzes critical areas: error handling, I/O, database, encoding, etc.
   - Scores files by risk level: CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
   - Prioritizes code review efforts where they matter most
   - Provides specific recommendations for each risk category
   - Helps teams focus on the most important changes first
   - Generates detailed reports in text or JSON format
   - Perfect for ensuring thorough review of critical changes!
   - Run `./py2to3 risk --help` to analyze migration risks!
   - **See [RISK_GUIDE.md](RISK_GUIDE.md) for complete risk analysis guide!**

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
# STEP 1: Run preflight checks before starting (recommended!)
./py2to3 preflight src/

# STEP 2: Analyze dependencies for Python 3 compatibility (NEW!)
./py2to3 deps src/ --output dependency_report.txt

# STEP 3: Run the complete migration in one command
./py2to3 migrate src/ --output my_migration_report.html
```

Or use individual commands for more control:

```bash
# Validate environment and project readiness
./py2to3 preflight src/ -v

# Analyze dependencies (NEW!)
./py2to3 deps src/

# Check compatibility
./py2to3 check src/

# Apply fixes (with confirmation)
./py2to3 fix src/

# Analyze migration risks (NEW!)
./py2to3 risk src/ -o risk_assessment.txt

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

**Dependency Analysis**

Analyze your project's dependencies for Python 3 compatibility:

```bash
# Analyze dependencies in current directory
./py2to3 deps

# Analyze specific project path
./py2to3 deps src/

# Save report to file
./py2to3 deps src/ --output dependency_report.txt

# Generate JSON output for CI/CD integration
./py2to3 deps src/ --format json --output deps.json
```

The dependency analyzer will:
- Scan requirements.txt, setup.py, and import statements
- Identify standard library modules that were renamed in Python 3
- Detect incompatible packages and suggest alternatives
- Recommend minimum and optimal versions for Python 3
- Help you plan dependency upgrades before migration

See [DEPENDENCY_GUIDE.md](DEPENDENCY_GUIDE.md) for complete documentation.

**Migration Comparison for Strategy Evaluation**

Compare migration progress across different contexts to evaluate approaches:

```bash
# Compare two different file system paths (e.g., two projects)
./py2to3 compare paths project_a/src project_b/src

# Compare two git branches to evaluate different migration strategies
./py2to3 compare branches main feature/migration-v2

# Compare two commits to track progress over time
./py2to3 compare commits abc1234 def5678

# Save comparison to file for sharing with team
./py2to3 compare branches main feature/py3-migration -o comparison_report.txt

# Generate JSON output for CI/CD integration
./py2to3 compare paths src_old src_new --format json -o comparison.json
```

The comparison tool will:
- Analyze migration progress in both contexts
- Show side-by-side metrics (files, issues, progress percentage)
- Determine which approach is performing better
- Break down differences by issue type and severity
- Provide actionable recommendations

Perfect for:
- Evaluating different migration approaches in parallel branches
- Tracking progress between commits
- Comparing your project with reference implementations
- Team collaboration and code review

**Git Integration for Migration Tracking**

Track your migration progress with automatic git integration:

```bash
# Check repository status
./py2to3 git status

# View repository information
./py2to3 git info

# Create a migration branch
./py2to3 git branch py2to3-migration

# Create a checkpoint before starting migration
./py2to3 git checkpoint "Pre-migration baseline"

# Apply fixes and create a commit with statistics
./py2to3 fix src/
./py2to3 git commit "fixes-applied" -m "Applied Python 2 to 3 fixes"

# View migration commit history
./py2to3 git log

# Rollback to a previous state if needed
./py2to3 git rollback

# Show differences between commits
./py2to3 git diff HEAD~1 HEAD
```

See [CLI_GUIDE.md](CLI_GUIDE.md), [CONFIG.md](CONFIG.md), [BACKUP_GUIDE.md](BACKUP_GUIDE.md), and [GIT_INTEGRATION.md](GIT_INTEGRATION.md) for complete documentation.

#### Using CI/CD Integration (Recommended for Teams)

Enable automated compatibility checking on every commit and pull request:

```bash
# The workflow is already set up! Just push your code:
git add .
git commit -m "Migrate authentication module"
git push

# The GitHub Actions workflow will automatically:
# ✓ Run preflight safety checks
# ✓ Check Python 3 compatibility
# ✓ Collect migration statistics
# ✓ Generate HTML reports
# ✓ Post results as PR comments
# ✓ Upload reports as artifacts
```

**Benefits:**
- 🔄 Continuous validation during migration
- 👥 Automatic feedback on pull requests
- 📊 Track progress over time
- 🛡️ Prevent introduction of new Python 2 code
- 📦 Historical reports stored for 30 days

See [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for advanced configuration and usage.

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
4. **Analyze risks**: Identify high-risk changes for priority review
   ```bash
   python risk_analyzer.py . --backup-dir backups --output risk_assessment.txt
   ```
5. **Verify results**: Check what issues remain after fixing
   ```bash
   python verifier.py . --report post_fix_verification.txt
   ```
6. **Generate HTML report**: Create a beautiful, comprehensive migration report
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
