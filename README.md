
# Python 2 to Python 3 Refactoring Example

This repository contains a comprehensive example of refactoring Python 2 code to Python 3, demonstrating the use of programmatic fixer and verifier tools for automated code migration.

## 🚀 Quick Start

Get up and running in 2 minutes:

```bash
# Automated setup (recommended)
./setup.sh

# Or use Make
make setup

# Start migrating with the wizard
./py2to3 wizard
```

That's it! The setup script will install everything you need. See [QUICK_START.md](QUICK_START.md) for detailed instructions.

## Overview

This project showcases a realistic Python 2 web scraping application with complex interdependencies that needs to be upgraded to Python 3. The repository includes:

1. **A complete Python 2 application** with 10 interconnected modules
2. **A programmatic fixer tool** that automatically converts Python 2 patterns to Python 3
3. **A programmatic verifier tool** that validates Python 3 compatibility and identifies remaining issues
4. **A modern web application** using React, TypeScript, and Vite (in `/my-vite-app`)
5. **Automated setup tools** for easy installation and getting started

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

## Installation

### Quick Installation (Recommended)

The easiest way to get started:

```bash
# Run the automated setup script
./setup.sh

# Or if you prefer Make
make setup
```

The setup script will:
- ✅ Check your Python version
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Validate the installation
- ✅ Show you next steps

### Manual Installation

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make py2to3 executable
chmod +x py2to3
```

### Development Installation

For development with testing and linting tools:

```bash
./setup.sh --dev
# Or manually:
pip install -r requirements-dev.txt
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

1. **Smart Migration Wizard** 🧙 ✨ **[NEW]**:
   - Interactive guided workflow for Python 2 to 3 migration
   - Perfect for beginners - no need to learn all the commands!
   - Analyzes your project and recommends personalized migration strategies
   - Asks questions to understand your needs and experience level
   - Automatically orchestrates the entire migration workflow
   - Creates backups, runs checks, applies fixes, and generates reports
   - Provides helpful tips and best practices at every step
   - One command does everything: `./py2to3 wizard`
   - **See [WIZARD_GUIDE.md](WIZARD_GUIDE.md) for complete guide!**

2. **Unified CLI Tool (`py2to3`)** **[NEW]**:
   - Single command-line interface for the entire migration workflow
   - Beautiful colored output with progress indicators
   - Six powerful commands: `check`, `preflight`, `fix`, `report`, `migrate`, `config`
   - Run `./py2to3 --help` to get started! See [CLI_GUIDE.md](CLI_GUIDE.md) for details.

3. **Code Snippet Converter** ✨ **[NEW]**:
   - Lightning-fast interactive tool for converting Python 2 snippets to Python 3
   - Perfect for learning, quick testing, and educational purposes
   - Multiple output formats: side-by-side comparison, unified diff, or plain text
   - Detailed explanations of every change made
   - Works with files, inline code, or stdin
   - Great for tutorials, documentation, and teaching Python 3
   - Run `./py2to3 convert --help` to explore!
   - **See [SNIPPET_CONVERTER_GUIDE.md](SNIPPET_CONVERTER_GUIDE.md) for complete guide!**

4. **Fixer Tool (`src/fixer.py`)**:
   - Automatically converts Python 2 code to Python 3
   - Handles common patterns, imports, syntax, and more
   - Creates backups and generates detailed reports

5. **Verifier Tool (`src/verifier.py`)**:
   - Analyzes code for Python 3 compatibility
   - Identifies remaining issues with severity classification
   - Integrates with the official 2to3 tool

6. **Report Generator (`src/report_generator.py`)** 🆕:
   - Generates comprehensive HTML reports for migration progress
   - Beautiful, interactive visualizations with charts and statistics
   - Side-by-side code comparisons showing before/after changes
   - Detailed issue tracking with severity classification
   - Export data as JSON for further analysis
   - Perfect for presenting migration progress to stakeholders
   - **See `demo_report.html` for a live example!**

7. **Configuration Management** ✨ **[NEW]**:
   - Flexible configuration system with user and project-level settings
   - JSON-based configuration files (`.py2to3.config.json`)
   - Customize default behaviors, ignore patterns, and fix rules
   - Share configuration across teams via version control
   - Manage config via CLI: `py2to3 config init`, `show`, `get`, `set`
   - **See [CONFIG.md](CONFIG.md) for complete configuration guide!**

8. **Backup Management** 🔄 **[NEW]**:
   - Comprehensive backup management for migration safety
   - List all backups with detailed information and statistics
   - Restore files or entire directories from backups
   - Clean up old backups to save disk space
   - View differences between backups and current files
   - Scan backup directory for inconsistencies
   - Perfect safety net for your migration workflow!
   - **See [BACKUP_GUIDE.md](BACKUP_GUIDE.md) for complete backup management guide!**

9. **Rollback Manager** ⏪ **[NEW]**:
   - Quick and safe rollback of migration operations
   - Automatically track all migration operations in history
   - Undo the last operation with a single command
   - Preview what will be rolled back before making changes
   - Rollback specific operations by ID
   - View operation history and statistics
   - Force rollback even with missing backups (when needed)
   - Perfect for experimenting with migration strategies!
   - Run `./py2to3 rollback --help` to explore rollback features!
   - **See [ROLLBACK_GUIDE.md](ROLLBACK_GUIDE.md) for complete rollback guide!**

10. **Comprehensive Test Suite** ✅ **[NEW]**:
   - Full pytest-based test suite for all migration tools
   - Unit tests for fixer, verifier, backup manager, and config manager
   - Integration tests for complete workflows
   - Test fixtures for easy test development
   - Ensures reliability and correctness of migration tools
   - **See [tests/README.md](tests/README.md) for complete testing guide!**

11. **Security Auditor** 🔒 ✨ **[NEW]**:
   - Scan code for security vulnerabilities introduced during migration
   - Detects SQL injection, command injection, and code injection risks
   - Identifies weak cryptographic functions (MD5, SHA-1) and unsafe deserialization
   - Checks for encoding vulnerabilities and path traversal issues
   - Finds hardcoded secrets, API keys, and passwords in code
   - Severity-based reporting (CRITICAL, HIGH, MEDIUM, LOW, INFO)
   - CI/CD integration with `--fail-on-high` option
   - JSON and text report formats for automation
   - Perfect for ensuring migration doesn't introduce security holes!
   - Run `./py2to3 security --help` to explore security auditing!
   - **See [SECURITY_AUDIT_GUIDE.md](SECURITY_AUDIT_GUIDE.md) for complete security audit guide!**

12. **Coverage Tracker** 📊 ✨ **[NEW]**:
   - Monitor test coverage during Python 2 to 3 migration
   - Identify risky migrations (files with low/no test coverage)
   - Track coverage trends over time with timestamped snapshots
   - Integrates seamlessly with pytest-cov and coverage.py
   - Generate detailed coverage reports with migration context
   - Color-coded visual indicators for coverage health
   - Find untested code before migration to reduce risk
   - Perfect safety metric alongside the migration workflow!
   - Run `./py2to3 coverage --help` to explore coverage tracking!
   - **See [COVERAGE_GUIDE.md](COVERAGE_GUIDE.md) for complete coverage tracking guide!**

13. **Code Formatter** ✨ **[NEW]**:
   - Automatically format migrated code with modern Python formatters
   - Integrates with black for consistent, beautiful code style
   - Uses isort for organized, clean import statements
   - Configurable line length and formatting options
   - Check mode to preview changes before applying
   - Batch processing for directories with exclusion patterns
   - Detailed statistics and per-file status reporting
   - Perfect final step after migration to ensure professional code!
   - Run `./py2to3 format --help` to explore formatting options!
   - **See [FORMAT_GUIDE.md](FORMAT_GUIDE.md) for complete formatting guide!**

14. **Pre-Migration Safety Checker** ✅ **[NEW]**:
   - Comprehensive environment validation before migration
   - Checks git status, disk space, file permissions, and more
   - Identifies potential issues early to prevent migration failures
   - Provides actionable fix suggestions for detected issues
   - Validates project structure and Python version compatibility
   - Estimates migration complexity and scope
   - JSON output support for CI/CD integration
   - Run `./py2to3 preflight` before starting your migration!

15. **Migration Readiness & Safety Score** 🎯 ✨ **[NEW]**:
   - Comprehensive assessment tool for migration readiness and production safety
   - Pre-migration readiness score: Are you prepared to start migration?
   - Post-migration safety score: Is your code ready for production?
   - 100-point scoring system with letter grades (A-F)
   - Evaluates version control, backups, testing, documentation, and code quality
   - Actionable recommendations for every failed check
   - Color-coded progress bars and detailed category breakdowns
   - JSON export for CI/CD integration and progress tracking
   - Run `./py2to3 readiness pre` before migration!
   - Run `./py2to3 readiness post` before production deployment!
   - **See [READINESS_GUIDE.md](READINESS_GUIDE.md) for complete guide!**

16. **Git Integration** 🔧 **[NEW]**:
   - Seamless git integration for tracking migration progress
   - Create migration branches and checkpoints automatically
   - Generate detailed commit messages with migration statistics
   - View migration history and rollback to previous states
   - Show git status and diff for migration changes
   - Perfect for team collaboration and code review workflows
   - Integrates with existing git repositories or creates new ones
   - Run `./py2to3 git --help` to explore git integration features!
   - **See [GIT_INTEGRATION.md](GIT_INTEGRATION.md) for complete git integration guide!**

17. **Pre-commit Hooks** 🛡️ **[NEW]**:
   - Prevent Python 2 code regression with automated pre-commit validation
   - Generate and manage git pre-commit hooks for Python 3 compatibility
   - Three strictness modes: strict, normal, and lenient
   - Integrates with popular pre-commit framework
   - Catches Python 2 patterns before they enter the repository
   - Provides instant feedback to developers during commits
   - Easy installation, configuration, and team sharing
   - Test hooks without committing with `./py2to3 precommit test`
   - Run `./py2to3 precommit install` to start preventing regressions!
   - **See [PRECOMMIT_GUIDE.md](PRECOMMIT_GUIDE.md) for complete pre-commit hooks guide!**

14. **Code Review Assistant** 🔍 **[NEW]**:
   - Intelligent code review assistance for migration changes
   - Automatically analyzes changes and identifies what needs review
   - Generates comprehensive review checklists tailored to your code
   - Risk assessment with high/medium/low priority categorization
   - Creates PR descriptions with migration statistics and recommendations
   - Estimates review time based on change complexity

14. **Migration Health Monitor** 🏥 **[NEW]**:
   - Comprehensive health scoring system for migration tracking (0-100)
   - Single metric to communicate status to stakeholders
   - Analyzes 6 key dimensions: compatibility, quality, tests, risk, progress, safety
   - Provides actionable, prioritized recommendations
   - Tracks health trends over time with historical data
   - CI/CD integration with exit codes based on health score
   - Beautiful visual output with emoji indicators and progress bars
   - JSON export for custom reporting and dashboards
   - Run `./py2to3 health` to check your migration health!
   - **See [HEALTH_GUIDE.md](HEALTH_GUIDE.md) for complete health monitoring guide!**

15. **Runtime Validator** ✨ **[NEW]**:
   - Validate migrated code by attempting to import all modules
   - Catch runtime errors that static analysis can't detect
   - Quick smoke test to verify code actually works after migration
   - Detailed reports showing which modules succeed, fail, or have warnings
   - JSON output support for CI/CD integration
   - Calculates overall validation success rate
   - Perfect complement to static analysis tools
   - Run `./py2to3 validate src/` after applying fixes!
   - **See [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) for complete validation guide!**

16. **CI/CD Integration** 🚀 **[NEW]**:
   - GitHub Actions workflow for automated compatibility checking
   - Runs on every push and pull request automatically
   - Generates and uploads comprehensive reports as artifacts
   - Posts detailed results as PR comments with emoji indicators
   - Tracks migration statistics over time
   - Smart triggers - only runs when Python files change
   - Manual dispatch with configurable parameters
   - Zero configuration needed - works out of the box!
   - **See [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for complete CI/CD integration guide!**

15. **Migration Package Export/Import** 📦✨ **[NEW]**:
   - Package migration configurations, state, and learnings into portable files
   - Share migration strategies and templates across teams and projects
   - Move migration state between development, staging, and production environments
   - Create reusable migration templates from successful migrations
   - Includes configuration, recipes, state, journal entries, and statistics
   - Optional backup inclusion for complete project snapshots
   - Merge or overwrite modes for flexible importing
   - Dry-run support to preview imports before applying
   - List and browse available migration packages
   - Perfect for team collaboration and knowledge sharing!
   - Run `./py2to3 export --help` and `./py2to3 import --help` to explore!
   - **See [EXPORT_GUIDE.md](EXPORT_GUIDE.md) for complete export/import guide!**

16. **Dependency Analyzer** 📦 **[NEW]**:
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

17. **Python Version Compatibility Checker** 🐍 **[NEW]**:
   - Analyzes migrated code to determine Python 3.x version requirements
   - Detects version-specific features (f-strings, walrus operator, pattern matching, etc.)
   - Identifies minimum Python version required for your code
   - Checks compatibility with specific target versions (3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12)
   - Detects standard library changes across Python versions
   - Helps make informed decisions about deployment targets
   - Generates comprehensive compatibility matrix
   - Essential for understanding version constraints after migration
   - Run `./py2to3 version-check src/` to analyze version requirements!
   - Run `./py2to3 version-check src/ -t 3.8` to check Python 3.8 compatibility!
   - **See [VERSION_CHECKER_GUIDE.md](VERSION_CHECKER_GUIDE.md) for complete version checking guide!**

18. **Project Metadata Updater** 📝 **[NEW]**:
   - Automatically updates all project metadata files for Python 3 compatibility
   - Updates setup.py (python_requires, classifiers), pyproject.toml, setup.cfg
   - Updates CI/CD configs: GitHub Actions, GitLab CI, Travis CI
   - Updates tox.ini, Pipfile, .python-version files
   - Updates README.md Python version badges and mentions
   - Ensures consistency across all project configuration files
   - Dry-run mode to preview changes before applying
   - Automatic backups of all modified files
   - Customizable Python version range support
   - JSON output for scripting and automation
   - Perfect final step after code migration!
   - Run `./py2to3 metadata --dry-run` to preview changes!
   - Run `./py2to3 metadata` to update all metadata files!
   - **See [METADATA_GUIDE.md](METADATA_GUIDE.md) for complete metadata updater guide!**

19. **Migration Comparison Tool** 🔍:
   - Compare migration progress between different contexts
   - Compare two git branches side-by-side to evaluate different approaches
   - Compare commits to track progress over time
   - Compare different file system paths or projects
   - Get detailed metrics: progress percentage, issue counts, severity

16. **Automated Test Generator** 🧪 **[NEW]**:
   - Automatically generate unit tests for migrated code
   - Helps verify that migration preserves functionality
   - Creates pytest-style test scaffolds with smart placeholders
   - Analyzes code structure using AST to identify testable components
   - Generates tests for functions and classes with customizable templates
   - Bridges the gap between "code compiles" and "code works correctly"
   - Perfect safety net to catch runtime issues after migration
   - Run `./py2to3 test-gen src/` to generate tests for your code!
   - **See [TEST_GEN_GUIDE.md](TEST_GEN_GUIDE.md) for complete test generation guide!**

17. **Interactive Fix Mode** 🎯 **[NEW]**:
   - Review and approve each fix before it's applied
   - Gives you complete control over the migration process
   - Shows context around each change for informed decisions
   - Accept, reject, skip files, or apply all remaining fixes
   - Automatic backup creation for safety
   - Color-coded diff display for easy review
   - Perfect for learning, critical code, or selective migration
   - Comprehensive statistics tracking (accepted/rejected by type)
   - Run `./py2to3 interactive src/` to start reviewing fixes!
   - **See [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md) for complete interactive mode guide!**

18. **Migration Recipes & Templates** 📋✨ **[NEW]**:
   - Pre-configured migration strategies for different project types
   - Built-in recipes for Django, Flask, CLI tools, data science, and libraries
   - Framework-specific configurations, fix priorities, and best practices
   - Save and share custom recipes with your team
   - Quick-start migrations with proven strategies
   - Import/export recipes for team collaboration
   - Ignore patterns, fix order recommendations, and important notes
   - Eliminates guesswork - get started with confidence
   - Perfect for standardizing migration across multiple projects
   - Run `./py2to3 recipe list` to see available recipes!
   - Run `./py2to3 recipe show django` to view recipe details!
   - Run `./py2to3 recipe apply flask` to apply a recipe!
   - **See [RECIPES_GUIDE.md](RECIPES_GUIDE.md) for complete recipes guide!**

19. **Risk Analyzer** ⚠️:
   - Intelligent risk assessment of migration changes
   - Identifies high-risk changes requiring careful manual review
   - Analyzes critical areas: error handling, I/O, database, encoding, etc.
   - Scores files by risk level: CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
   - Prioritizes code review efforts where they matter most
   - Provides specific recommendations for each risk category
   - Helps teams focus on the most important changes first
   - Generates detailed reports in text or JSON format

20. **Migration Planner** 📋 **[NEW]**:
   - Strategic planning tool for large-scale migrations
   - Analyzes codebase structure and builds complete dependency graph
   - Creates optimized phased migration plan based on dependencies
   - Breaks down complex migrations into manageable phases
   - Assesses complexity and risk level for each file
   - Estimates effort (hours) for planning and resource allocation
   - Exports plans in multiple formats: text, Markdown, JSON
   - Start with Phase 1 (leaf nodes) for safest migration approach
   - Perfect for understanding scope before starting migration
   - Run `./py2to3 plan src/` to create your migration strategy!
   - **See [PLANNER_GUIDE.md](PLANNER_GUIDE.md) for complete migration planning guide!**

21. **Watch Mode** 👁️ **[NEW]**:
   - Real-time file monitoring with automatic compatibility checking
   - Get instant feedback as you edit Python files during migration
   - Monitor entire directories or specific files for changes
   - Debouncing to avoid excessive checks during active editing
   - Multiple modes: check-only, stats tracking, report generation
   - Clean, formatted output with icons and color coding
   - Session statistics to track your progress
   - Perfect for active development with immediate feedback loop
   - Like webpack watch or jest --watch for Python migration
   - Run `./py2to3 watch src/` to start monitoring your code!
   - **See [WATCH_MODE.md](WATCH_MODE.md) for complete watch mode guide!**

22. **Migration Statistics Dashboard** 📊 **[NEW]**:
   - Interactive web-based dashboard for visualizing migration progress
   - Beautiful charts and graphs showing issue distribution and trends
   - Real-time progress tracking with comparison to previous scans
   - Ranked list of most problematic files for prioritization
   - JSON export from stats command for dashboard visualization
   - Built with React, TypeScript, and Recharts for modern UX
   - Upload stats files from anywhere or serve from public directory
   - Perfect for team visibility and stakeholder reporting!
   - Generate stats: `./py2to3 stats collect src/ --format json --output my-vite-app/public/migration-stats.json`
   - Start dashboard: `cd my-vite-app && npm install && npm run dev`
   - **See [my-vite-app/README.md](my-vite-app/README.md) for complete dashboard guide!**

23. **Code Quality and Complexity Analyzer** 📈 **[NEW]**:
   - Comprehensive code quality metrics and complexity analysis
   - Measures cyclomatic complexity, maintainability index, and code structure
   - Analyzes lines of code, functions, classes, and comment ratios
   - Quality grading system (A-F) for quick assessment
   - Identifies high-complexity functions and files needing refactoring
   - Provides actionable recommendations for code improvements
   - Track code quality before and after migration
   - JSON export for integration with CI/CD pipelines
   - Compare quality trends over time
   - Perfect for ensuring migration improves (or at least maintains) code quality!
   - Run `./py2to3 quality src/` to analyze your code!
   - **See [QUALITY_GUIDE.md](QUALITY_GUIDE.md) for complete code quality guide!**

24. **Linting Integration** 🔍 **[NEW]**:
   - Integrate popular Python linters for comprehensive code quality checking
   - Supports pylint, flake8, mypy, and black formatters
   - Unified reporting across all linters with severity classification
   - Identifies style issues, type errors, and potential bugs
   - Generates actionable recommendations for improving code
   - Detects which linters are available and provides installation instructions
   - JSON and text output formats for CI/CD integration
   - Returns non-zero exit code when issues found (perfect for CI pipelines)
   - Helps ensure migrated code meets modern Python standards
   - Run specific linters or all available ones
   - Perfect companion to the quality analyzer for holistic code assessment
   - Run `./py2to3 lint src/` to check your code!

25. **Migration Documentation Generator** 📚 **[NEW]**:
   - Automatically generates comprehensive Markdown documentation for your migration
   - Creates version-control-friendly documentation that renders beautifully on GitHub
   - Four key documents: Summary, Guide, Changelog, and Best Practices
   - Migration summary with status, statistics, and progress metrics
   - Developer guide covering Python 3 changes, patterns, and workflows
   - Detailed changelog documenting all modifications by category
   - Best practices document for maintaining Python 3 code quality
   - Perfect for team communication, onboarding, and historical reference
   - Documentation stored in `.migration_docs/` directory
   - Easy to commit, share, and update as migration progresses
   - Complements HTML reports with team-friendly Markdown format
   - Run `./py2to3 docs` to generate migration documentation!

26. **Performance Benchmark Tool** 🚀 **[NEW]**:
   - Compare execution time and performance between Python 2 and Python 3 code
   - Quantify performance improvements to demonstrate ROI of migration
   - Measure execution time with configurable iterations for accuracy
   - Identifies performance improvements (faster) and regressions (slower)
   - Generates detailed reports with speedup metrics and change percentages
   - Helps catch performance issues before they reach production
   - Supports benchmarking individual files or entire directories
   - JSON export for CI/CD integration and automated tracking
   - Guides optimization efforts by highlighting high-impact wins
   - Perfect for justifying migration efforts to stakeholders!
   - Run `./py2to3 bench src/` to benchmark your code!
   - **See [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) for complete performance benchmarking guide!**

27. **Interactive Progress Dashboard** 📊✨ **[NEW]**:
   - Stunning interactive HTML dashboard with real-time charts and visualizations
   - Zero setup required - single HTML file with embedded Chart.js
   - Beautiful burndown chart showing issues decreasing over time
   - Progress chart tracking migration completion percentage
   - Issue distribution by type and severity with colorful doughnut/bar charts
   - Velocity tracking - calculates your team's progress rate per day
   - Smart ETA prediction - estimates completion date based on velocity
   - Trend analysis showing if progress is improving, stable, or declining
   - Historical tracking - visualizes progress across multiple snapshots
   - Responsive design with gradient cards and modern UI
   - Perfect for team standups and stakeholder presentations!
   - Run `./py2to3 dashboard` to generate your progress dashboard!
   - Update regularly: collect stats with `--save` flag, then regenerate dashboard

28. **Live Migration Monitor** 🔴✨ **[NEW]**:
   - Real-time terminal dashboard for monitoring migration progress live
   - Beautiful, auto-refreshing interface built with Rich library
   - Live statistics showing files migrated, issues found/fixed, and completion percentage
   - Color-coded progress bars with visual indicators (red → yellow → green)
   - Top issues breakdown showing most common migration patterns
   - Recent activity feed displaying latest migration actions
   - Issue severity tracking (high/medium/low) with emoji indicators
   - Customizable refresh rate (default: 2 seconds)
   - Perfect for keeping an eye on long-running migrations
   - No browser needed - runs directly in your terminal
   - Press Ctrl+C to exit anytime
   - Run `./py2to3 live` to start monitoring in real-time!
   - Works great alongside the wizard, fix, and other commands
   - Keep it open in a split terminal while working on migration

29. **Quick Status Command** 📋⚡ **[NEW]**:
   - Lightning-fast terminal-based status report for at-a-glance progress checking
   - Shows comprehensive migration status without generating HTML reports
   - Beautiful colorful output with progress bars, icons, and visual indicators
   - Displays project info, progress percentage, issue breakdown by severity
   - Git integration showing current branch, modified files, and recent commits
   - Backup status and count of available backups
   - Smart recommendations for next steps based on current state
   - Trend analysis comparing with previous snapshots
   - JSON output support for CI/CD integration and automation
   - Perfect for quick daily checks, team standups, and pre-commit validation
   - Run `./py2to3 status` anytime for instant status update!
   - **See [STATUS_GUIDE.md](STATUS_GUIDE.md) for complete status command guide!**

30. **Migration State Tracker** 🎯✨ **[NEW]**:
   - Track migration status of individual files through the entire migration workflow
   - File-level state management: pending → in_progress → migrated → verified → tested → done
   - Advisory file locking to coordinate team work and prevent conflicts
   - Export/import state for team synchronization and backup
   - Rich statistics and progress reporting by state
   - Filter and list files by state, lock status, or owner
   - Full history tracking with notes and timestamps for each state change
   - Perfect for large-scale migrations with multiple team members
   - Resumable workflows - easily pick up where you left off after interruptions
   - Integrates seamlessly with git for shared state tracking
   - JSON-based state persistence in `.py2to3.state.json`
   - Run `./py2to3 state init` to start tracking migration progress!
   - Run `./py2to3 state stats` to see comprehensive statistics!
   - Run `./py2to3 state list --filter-state pending` to find work to do!
   - **See [docs/MIGRATION_STATE_GUIDE.md](docs/MIGRATION_STATE_GUIDE.md) for complete state tracking guide!**

31. **Pattern Search Tool** 🔍✨ **[NEW]**:
   - Smart search for specific Python 2 patterns in your codebase
   - Find all instances of particular issues (print statements, xrange, iteritems, etc.)
   - 19 pre-defined patterns covering common Python 2 to 3 migration issues
   - Beautiful colored output with context lines and highlighting
   - Search all patterns or target specific ones for focused analysis
   - Perfect for understanding migration scope before starting fixes
   - Supports custom workflows - tackle patterns one type at a time
   - JSON export for automation and integration with custom tools
   - Non-zero exit code when patterns found (CI/CD integration)
   - Adjustable context lines for better understanding of matches
   - List all available patterns with examples and descriptions
   - Ideal for planning targeted fixes and code review focus
   - Complements `check` command with targeted pattern discovery
   - Run `./py2to3 search src/` to find all Python 2 patterns!
   - Run `./py2to3 search --list-patterns` to see available patterns!
   - **See [SEARCH_GUIDE.md](SEARCH_GUIDE.md) for complete pattern search guide!**

31. **Migration Journal** 📝✨ **[NEW]**:
   - Comprehensive note-taking and decision-tracking system for your migration
   - Document decisions, issues, solutions, and insights as you work
   - Organize entries by category: decision, issue, solution, insight, todo, question, general
   - Tag entries for easy filtering and discovery
   - Link entries to specific files for context
   - Track team contributions with author attribution
   - Search through entries to find past decisions quickly
   - Export journal as Markdown documentation for stakeholders
   - Import/export for team collaboration and knowledge sharing
   - Build a searchable knowledge base of migration decisions
   - Perfect audit trail for compliance and future reference
   - Statistics and tag cloud for migration retrospectives
   - JSON-based storage in `.migration_journal.json`
   - Run `./py2to3 journal add "Your note here"` to add entries!
   - Run `./py2to3 journal list` to view your migration history!
   - Run `./py2to3 journal export migration_diary.md` for documentation!
   - **See [JOURNAL_GUIDE.md](JOURNAL_GUIDE.md) for complete journal guide!**

33. **Virtual Environment Manager** 🐍✨ **[NEW]**:
   - Integrated Python 3 virtual environment management for migration testing
   - Create isolated Python 3 environments to test migrated code safely
   - Support for multiple Python versions (3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12)
   - Install dependencies from requirements.txt in clean environments
   - Run tests in isolated environments to validate migration
   - Execute Python scripts in specific environments for testing
   - Track all environments with metadata and package information
   - Easy activation commands for manual testing
   - Perfect bridge between migration and validation workflows
   - Test against multiple Python versions to ensure compatibility
   - Remove old environments when no longer needed
   - Run `./py2to3 venv create my-env` to create an environment!
   - Run `./py2to3 venv install my-env -r requirements.txt` to install dependencies!
   - Run `./py2to3 venv test my-env` to run tests in the environment!
   - **See [VENV_GUIDE.md](VENV_GUIDE.md) for complete virtual environment guide!**

34. **Import Optimizer** 🎯✨ **[NEW]**:
   - Automatically clean up and organize Python imports after migration
   - Removes unused imports left behind from migration
   - Eliminates duplicate imports added during fixes
   - Sorts imports according to PEP 8 (stdlib → third-party → local)
   - Detects and reports wildcard imports
   - Groups related imports for better readability
   - Creates backups before applying changes
   - Generates detailed reports with file-by-file breakdown
   - Perfect final polish after migration
   - CI/CD integration with non-zero exit on issues
   - Run `./py2to3 imports src/` to analyze imports!
   - Run `./py2to3 imports src/ --fix` to optimize imports!
   - **See [IMPORT_OPTIMIZER_GUIDE.md](IMPORT_OPTIMIZER_GUIDE.md) for complete import optimization guide!**

35. **Code Modernizer** 🚀✨ **[NEW]**:
   - Upgrade Python 3 compatible code to use modern Python 3.6+ idioms
   - Identifies opportunities to use f-strings instead of % or .format()
   - Suggests pathlib instead of os.path for better path handling
   - Recommends type hints for improved code documentation and IDE support
   - Detects classes that could use @dataclass decorator
   - Finds file operations that should use context managers
   - Suggests list comprehensions for more concise code
   - Recommends dictionary merge operators (Python 3.9+)
   - Generates comprehensive reports with severity indicators
   - Filter by category to focus on specific modernizations
   - JSON output for CI/CD integration
   - Makes your code more Pythonic, readable, and maintainable
   - Perfect post-migration step to modernize legacy patterns
   - Run `./py2to3 modernize src/` to analyze code!
   - Run `./py2to3 modernize src/ -o report.txt` to save detailed report!
   - **See [MODERNIZER_GUIDE.md](MODERNIZER_GUIDE.md) for complete modernization guide!**

36. **Type Hints Generator** 🎯✨ **[NEW]**:
   - Automatically add type hints to Python 3 code after migration
   - Infers types from default values, return statements, and usage patterns
   - Adds annotations to function parameters and return values
   - Smart import management for typing module constructs
   - Supports List, Dict, Set, Tuple, Optional, Union, and more
   - Dry-run mode to preview changes before applying
   - Detailed reports showing all changes made
   - Batch processing for entire directories
   - Perfect for modernizing code that came from Python 2
   - Improves IDE support, documentation, and enables static type checking
   - Makes code more maintainable and self-documenting
   - Run `./py2to3 typehints src/` to add type hints!
   - Run `./py2to3 typehints src/ --dry-run` to preview changes!
   - Run `./py2to3 typehints src/ --report report.txt` for detailed report!
   - **See [TYPE_HINTS_GUIDE.md](TYPE_HINTS_GUIDE.md) for complete type hints guide!**

37. **Migration Effort Estimator** 📊💼 **[NEW]**:
   - Analyze codebase and estimate time/resources required for migration
   - Provides detailed breakdown of fix, testing, review, and documentation time
   - Recommends optimal team size and composition
   - Generates project timeline with milestones and phases
   - Risk assessment based on issue severity and complexity
   - Calculates contingency buffer (10-30%) based on risk factors
   - Multiple output formats: text, JSON, and CSV
   - Perfect for project planning and getting stakeholder buy-in
   - Helps with budget estimation and resource allocation
   - Tracks complexity factors like issue density and project size
   - Run `./py2to3 estimate src/` to get effort estimates!
   - Run `./py2to3 estimate src/ --format json -o estimate.json` for JSON export!
   - Run `./py2to3 estimate src/ -o report.txt` to save detailed report!
   - **See [EFFORT_ESTIMATOR_GUIDE.md](EFFORT_ESTIMATOR_GUIDE.md) for complete effort estimation guide!**

38. **Freeze Guard - Python 2 Prevention** 🔒✨ **[NEW]**:
   - Prevent Python 2 code from being re-introduced during active migration
   - Mark migrated files/directories as "frozen" (Python 3 only)
   - Automatically blocks commits containing Python 2 patterns in frozen files
   - Pre-commit git hook integration for automatic enforcement
   - Perfect for team coordination during gradual migration
   - Protects migration progress from accidental regression
   - Detects print statements, old imports, iterator methods, and more
   - CI/CD integration to block PRs with Python 2 code
   - Check git staged files or specific paths on demand
   - Track which parts of codebase are migrated vs. pending
   - Complements the fix/verify workflow with prevention
   - Run `./py2to3 freeze mark src/auth/` to freeze migrated modules!
   - Run `./py2to3 freeze install-hook` to enable pre-commit protection!
   - Run `./py2to3 freeze check --staged` to verify staged changes!
   - **See [FREEZE_GUIDE.md](FREEZE_GUIDE.md) for complete freeze guard guide!**

39. **Encoding Analyzer** 🔤✨ **[NEW]**:
   - Detect and fix file encoding issues during Python 2→3 migration
   - Automatically detect actual file encodings (UTF-8, Latin-1, CP1252, etc.)
   - Identify missing or incorrect encoding declarations
   - Add proper PEP 263 encoding declarations automatically
   - Convert files to UTF-8 (Python 3 standard) with automatic backups
   - Detailed reports in text, JSON, or Markdown format
   - Detect mismatched declared vs. actual encodings
   - Find files with non-ASCII characters but no encoding declaration
   - CI/CD integration with exit codes for automation
   - Dry-run mode to preview changes before applying
   - Essential for catching runtime encoding errors early
   - Run `./py2to3 encoding src/ -r` to analyze your codebase!
   - Run `./py2to3 encoding src/ -r --add-declarations` to fix declarations!
   - Run `./py2to3 encoding src/ -r --convert-to-utf8` to standardize encodings!
   - **See [ENCODING_GUIDE.md](ENCODING_GUIDE.md) for complete encoding guide!**

40. **Automated Changelog Generator** 📝✨ **[NEW]**:
   - Automatically generate professional changelogs from migration activities
   - Consolidates git commits, journal entries, and statistics
   - Supports industry-standard "Keep a Changelog" format
   - Categorizes changes by type (syntax, imports, fixes, features, etc.)
   - Automatically detects and highlights breaking changes
   - Includes migration metrics (issues fixed, files modified, completion %)
   - Generate for specific date ranges or entire migration history
   - Append new versions to existing changelogs
   - Perfect for stakeholder communication and release documentation
   - Multiple output formats: Keep a Changelog or simple categorized
   - Integrates seamlessly with journal, stats, and git tools
   - Run `./py2to3 changelog` to generate changelog!
   - Run `./py2to3 changelog -o CHANGELOG.md` to save to file!
   - Run `./py2to3 changelog --since "30 days ago" --append` for updates!
   - **See [CHANGELOG_GUIDE.md](CHANGELOG_GUIDE.md) for complete changelog guide!**

41. **Migration Report Card** 🎓✨ **[NEW]**:
   - Comprehensive quality assessment for Python 2→3 migrations
   - Letter grades (A-F) for overall migration and individual categories
   - Evaluates 6 key quality dimensions with weighted scoring
   - **Compatibility** (30%): Python 3 compatibility issues
   - **Modernization** (20%): Use of modern Python 3 features
   - **Code Quality** (20%): Docstrings, structure, naming
   - **Test Coverage** (15%): Ratio of tests to source files
   - **Documentation** (10%): Essential docs and guides
   - **Best Practices** (5%): Project structure and configuration
   - Actionable recommendations prioritized by severity
   - Multiple output formats: text, HTML, JSON, and Markdown
   - Perfect for stakeholder presentations and quality gates
   - HTML format provides beautiful, executive-friendly reports
   - JSON format enables CI/CD quality gate integration
   - Track quality trends over time by saving periodic reports
   - Identifies weak areas requiring focused attention
   - Measures *how well* migration was done, not just *what* changed
   - Run `./py2to3 report-card src/` for quality assessment!
   - Run `./py2to3 report-card -f html -o quality.html` for stakeholders!
   - Run `./py2to3 report-card -f json -o quality.json` for CI/CD!
   - **See [REPORT_CARD_GUIDE.md](REPORT_CARD_GUIDE.md) for complete report card guide!**

42. **Shell Completions** 🎯✨ **[NEW]**:
   - Powerful Tab completion for bash, zsh, and fish shells
   - Auto-complete all 47 commands and subcommands instantly
   - Context-aware suggestions for options and arguments
   - Dramatically improves productivity and reduces typos
   - Easy one-command installation and setup
   - Auto-detects your current shell
   - Works with both local and globally installed py2to3
   - Completions for all command options and flags
   - File path completion for relevant options
   - Perfect for learning the toolkit interactively
   - Generate completion scripts for distribution
   - Check installation status across all shells
   - Simple uninstall when needed
   - Run `./py2to3 completion install` to enable completions!
   - Run `./py2to3 completion status` to check installation!
   - Run `./py2to3 completion generate bash` to view script!
   - **See [COMPLETION_GUIDE.md](COMPLETION_GUIDE.md) for complete shell completion guide!**

43. **Visual Dependency Graph** 🕸️✨ **[NEW]**:
   - Interactive visualization of module dependencies
   - Understand complex codebases at a glance
   - Plan migration order based on dependency relationships
   - Color-coded risk levels (red=high, yellow=medium, green=low)
   - Node size represents lines of code
   - Drag-and-drop interface for exploring relationships
   - Hover tooltips with detailed module information
   - Automatic circular dependency detection with warnings
   - Statistics dashboard showing total modules and risk distribution
   - Identifies modules with no dependencies (migrate first!)
   - Shows most-depended-upon modules (migrate last!)
   - Force-directed layout for optimal visualization
   - Zoom and pan controls for large codebases
   - Self-contained HTML output (no external dependencies)
   - Perfect for team presentations and stakeholder communication
   - Track progress by regenerating graphs over time
   - Text summary mode for quick command-line insights
   - Run `./py2to3 graph src/` to generate interactive visualization!
   - Run `./py2to3 graph src/ --summary` for text overview!
   - **See [DEPENDENCY_GRAPH_GUIDE.md](DEPENDENCY_GRAPH_GUIDE.md) for complete visualization guide!**

44. **REST API Server** 🌐✨ **[NEW]**:
   - Full REST API for programmatic access to all migration features
   - HTTP endpoints for check, fix, report, stats, backup, and more
   - Enable CI/CD pipeline integration with automated migration checks
   - Build custom web dashboards and monitoring tools
   - Third-party tool integration via standardized JSON API
   - CORS enabled for browser-based clients
   - Comprehensive error handling and validation
   - Health check and API info endpoints
   - Support for all toolkit operations: dependency analysis, security audits, quality checks
   - Perfect for automation, remote access, and custom integrations
   - Start server: `./py2to3 api`
   - Custom port: `./py2to3 api --port 8080`
   - Remote access: `./py2to3 api --host 0.0.0.0 --port 8080`
   - **See [API_SERVER_GUIDE.md](API_SERVER_GUIDE.md) for complete API documentation with examples!**

### Modern Web Application

The `my-vite-app/` directory contains a modern **Migration Statistics Dashboard** built with:
- React 18 - Modern UI library
- TypeScript - Type-safe development
- Vite - Fast build tool with HMR support
- Recharts - Interactive data visualizations
- ESLint - Code quality enforcement

**Quick Start:**
```bash
# Generate migration statistics
./py2to3 stats collect src/ --format json --output my-vite-app/public/migration-stats.json

# Start the dashboard
cd my-vite-app
npm install
npm run dev
```

Open `http://localhost:5173` to view your migration progress dashboard!

## Getting Started

### Python 2 to Python 3 Refactoring

#### Absolute Easiest Way: Smart Migration Wizard 🧙 ✨ **[NEW]**

The **absolute easiest** way to get started is using the Smart Migration Wizard - perfect for beginners!

```bash
# One command does everything - just answer a few questions!
./py2to3 wizard

# Or specify your project path
./py2to3 wizard /path/to/your/project
```

The wizard will:
- Analyze your project automatically
- Ask you questions to understand your needs
- Recommend a personalized migration strategy
- Execute the entire migration workflow for you
- Provide helpful tips and guidance at every step

**See [WIZARD_GUIDE.md](WIZARD_GUIDE.md) for complete documentation!**

#### Quick Start (Using the CLI Tool)

If you prefer more control, use the unified CLI tool:

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

# Create a strategic migration plan (NEW!)
./py2to3 plan src/ -o migration_plan.txt

# Analyze dependencies (NEW!)
./py2to3 deps src/

# Check compatibility
./py2to3 check src/

# Quick status check (NEW!)
./py2to3 status

# Preview changes with dry-run mode (NEW! - fully functional) ✨
./py2to3 fix src/ --dry-run

# Apply fixes (with confirmation)
./py2to3 fix src/

# Check status again to see progress (NEW!)
./py2to3 status

# Analyze migration risks (NEW!)
./py2to3 risk src/ -o risk_assessment.txt

# Generate unit tests to verify migration correctness (NEW!)
./py2to3 test-gen src/ -o migration_tests

# Generate report
./py2to3 report --scan-path src/ --output report.html
```

**Quick Status Checks** 📋 **[NEW]**

Get an instant overview of your migration progress at any time:

```bash
# Show current migration status in the terminal
./py2to3 status

# Export status as JSON for CI/CD or automation
./py2to3 status --json -o status.json

# Check status for specific project path
./py2to3 status src/
```

The status command shows:
- Migration progress percentage with visual progress bar
- Issue counts by severity (Critical, High, Medium, Low)
- Git status (current branch, modified files, recent commits)
- Backup information
- Smart recommendations for next steps
- Progress trends compared to previous snapshots

Perfect for quick daily checks, team standups, and pre-commit validation!

See [STATUS_GUIDE.md](STATUS_GUIDE.md) for complete documentation.

**Dry-Run Mode for Safe Preview** 🔍 **[NEW - FULLY FUNCTIONAL]** ✨

Preview exactly what changes will be made before committing to them:

```bash
# Preview changes to a single file without modifying it
./py2to3 fix src/myfile.py --dry-run

# Preview changes to an entire directory
./py2to3 fix src/ --dry-run

# See detailed changes with report output
./py2to3 fix src/ --dry-run --report preview_report.txt
```

The dry-run mode provides:
- **Zero Risk** - No files are modified, no backups created
- **Detailed Preview** - See exactly what fixes would be applied
- **Fix Counting** - Know how many changes will be made per file
- **Type Breakdown** - Understand which patterns will be fixed
- **Same Analysis** - Uses identical logic as actual fixing
- **Quick Validation** - Perfect for checking before committing changes
- **Team Sharing** - Generate reports to share preview with team members

**Example Output:**
```
⚠ DRY RUN MODE: No files will be modified
Analyzing file (dry run): src/myfile.py
  Would apply 3 types of fixes (DRY RUN)
    - Convert print statements to print() functions (5 occurrence(s))
    - Fix urllib2 imports (1 occurrence(s))
    - Replace iteritems() with items() (2 occurrence(s))
```

Perfect for:
- Testing configuration changes safely
- Understanding migration scope before starting
- Generating previews for code review
- Validating migration strategies
- Training team members on expected changes
- CI/CD pre-checks without side effects

**Search for Specific Patterns** 🔍 **[NEW]**

Find specific Python 2 patterns in your codebase with context and highlighting:

```bash
# List all available patterns
./py2to3 search --list-patterns

# Search for all Python 2 patterns
./py2to3 search src/

# Search for specific patterns only
./py2to3 search src/ -p print_statement xrange

# Search with more context lines
./py2to3 search src/ -p iteritems -c 5

# Export results as JSON
./py2to3 search src/ -o patterns.json
```

The search command helps you:
- Find all instances of specific Python 2 patterns quickly
- Plan targeted fixes by focusing on one pattern type at a time
- Understand migration scope before starting
- Create custom migration workflows
- Integrate with CI/CD pipelines (non-zero exit when patterns found)

Perfect for targeted pattern discovery and phased migration strategies!

See [SEARCH_GUIDE.md](SEARCH_GUIDE.md) for complete pattern search guide.

**Generate Tests to Verify Migration** 🧪 **[NEW]**

Ensure your migration preserves functionality by generating unit tests:

```bash
# Generate tests for migrated code
./py2to3 test-gen src/ -o migration_tests

# Review and customize generated tests
# Edit files in migration_tests/ to add specific assertions

# Run tests to verify functionality
pytest migration_tests/

# Run tests with coverage
pytest migration_tests/ --cov=src --cov-report=html
```

See [TEST_GEN_GUIDE.md](TEST_GEN_GUIDE.md) for complete guide on test generation.

**Use Watch Mode for Real-Time Feedback** 👁️ **[NEW]**

Get instant feedback as you work on migration with watch mode:

```bash
# Start watch mode in current directory
./py2to3 watch

# Watch a specific directory
./py2to3 watch src/

# Watch with automatic stats tracking
./py2to3 watch src/ --mode stats

# Adjust debounce delay (wait 2 seconds after changes)
./py2to3 watch src/ --debounce 2.0

# In another terminal, edit files and see instant feedback
vim src/core/processor.py  # Save changes and watch terminal
```

Watch mode is perfect for active development - it automatically checks files as you save them, providing immediate feedback on any Python 3 compatibility issues. Like webpack watch or jest --watch, but for Python migration!

See [WATCH_MODE.md](WATCH_MODE.md) for complete guide on watch mode.

**Generate Migration Documentation** 📚 **[NEW]**

Create comprehensive Markdown documentation for your migration project:

```bash
# Generate documentation for your project
./py2to3 docs

# Generate docs for a specific directory
./py2to3 docs src/

# Specify custom output directory
./py2to3 docs src/ --output-dir docs/migration

# Include backup directory information
./py2to3 docs src/ --backup-dir backup
```

The documentation generator creates:
- **Migration Summary** - Overview, statistics, and progress
- **Migration Guide** - How to work with Python 3 code
- **Migration Changelog** - Detailed list of all changes
- **Best Practices** - Python 3 coding standards

All documentation is in Markdown format, perfect for:
- Committing to version control
- Rendering on GitHub/GitLab
- Team communication and onboarding
- Historical reference and audit trails

```bash
# Generate docs and commit to repository
./py2to3 docs
git add .migration_docs
git commit -m "Add migration documentation"
```

**Use Configuration for Convenience**

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

**Code Quality and Complexity Analysis**

Analyze code quality metrics to ensure migration improves or maintains code health:

```bash
# Analyze code quality for current project
./py2to3 quality src/

# Save detailed quality report
./py2to3 quality src/ --detailed --output quality_report.txt

# Generate JSON for automated quality gates
./py2to3 quality src/ --format json --output quality.json

# Analyze a specific file
./py2to3 quality src/fixer.py
```

The quality analyzer provides:
- **Cyclomatic complexity** - Identifies complex code that needs refactoring
- **Maintainability index** - Overall quality score (0-100) with A-F grading
- **Code statistics** - LOC, SLOC, functions, classes, comment ratios
- **Quality distribution** - Visual representation of quality across files
- **Actionable recommendations** - Specific suggestions for improvement

Perfect for:
- Establishing quality baselines before migration
- Identifying refactoring priorities
- Tracking quality improvements over time
- Ensuring migration doesn't degrade code quality
- Setting quality gates in CI/CD pipelines

See [QUALITY_GUIDE.md](QUALITY_GUIDE.md) for complete documentation.

**Linting Integration for Code Quality**

Integrate popular Python linters to ensure migrated code meets modern standards:

```bash
# Run all available linters on your project
./py2to3 lint src/

# Run specific linters only
./py2to3 lint src/ --linters pylint flake8

# Check a specific file
./py2to3 lint src/fixer.py

# Save report to file
./py2to3 lint src/ --output lint_report.txt

# Generate JSON for CI/CD integration
./py2to3 lint src/ --format json --output lint_results.json
```

The linting integration provides:
- **Pylint** - Comprehensive code analysis with style and error detection
- **Flake8** - Style guide enforcement (PEP 8 compliance)
- **Mypy** - Static type checking for type safety
- **Black** - Code formatting verification
- **Unified reporting** - All results in one place with severity classification
- **Installation detection** - Automatically detects available linters

Perfect for:
- Ensuring code meets PEP 8 and modern Python standards
- Catching type errors and potential bugs early
- Enforcing consistent code style across the team
- CI/CD integration with non-zero exit on issues
- Complementing quality analysis with linting checks
- Verifying migrated code is production-ready

**Code Review Assistant for Migration Changes**

Streamline code review with intelligent analysis and automated checklists:

```bash
# Generate comprehensive review report
./py2to3 review src/ -o review_report.md

# Create PR description with migration statistics
./py2to3 review src/ --pr

# Export review data as JSON for automation
./py2to3 review src/ --format json -o review.json

# Analyze single file for review
./py2to3 review src/mymodule.py

# Generate text report for email
./py2to3 review src/ --format text -o review.txt
```

The review assistant provides:
- **Automated change detection** - Identifies all Python 2→3 patterns
- **Risk categorization** - High/medium/low priority assessment
- **Review checklists** - Tailored to your specific changes
- **Time estimates** - Know how long the review will take
- **PR descriptions** - Ready-to-use pull request templates
- **Multiple formats** - Markdown, text, or JSON output

Perfect for:
- Ensuring thorough code review before production
- Generating PR descriptions with migration context
- Focusing reviewers on critical changes first
- CI/CD integration for automated review checks
- Team collaboration and knowledge sharing
- Training reviewers on what to look for

See [REVIEW_GUIDE.md](REVIEW_GUIDE.md) for complete documentation.

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

**Rollback Manager for Safe Experimentation**

Quickly undo migration operations if something goes wrong:

```bash
# Undo the last operation
./py2to3 rollback undo

# Preview what would be rolled back without making changes
./py2to3 rollback preview

# List all operations in history
./py2to3 rollback list

# Undo a specific operation by ID
./py2to3 rollback undo --id 20240115_143022_123456

# Dry run to see what would happen
./py2to3 rollback undo --dry-run

# View rollback statistics
./py2to3 rollback stats

# Clear old history (keep last 50 operations)
./py2to3 rollback clear --keep 50
```

**Use Cases:**
- Test migration strategies safely
- Undo bad automated fixes
- Experiment with different approaches
- Quick recovery from mistakes

Perfect for:
- Trying different fix patterns and comparing results
- Learning which migration strategies work best
- Ensuring you can always undo changes
- Building confidence during migration

See [ROLLBACK_GUIDE.md](ROLLBACK_GUIDE.md) for complete documentation.

**Migration Package Export/Import for Team Collaboration**

Package and share migration configurations, state, and learnings across teams and projects:

```bash
# Export your migration configuration and state
./py2to3 export create -d "Django migration template" -t "django,template"

# Export with custom components
./py2to3 export create --no-stats --no-journal -o config_only.tar.gz

# Export with backups (can be large!)
./py2to3 export create --backups --backup-pattern "*.py"

# List available packages
./py2to3 export list

# Import a package (preview first)
./py2to3 import migration_package.tar.gz --dry-run

# Actually import the package
./py2to3 import migration_package.tar.gz

# Import only specific components
./py2to3 import package.tar.gz --no-state --no-journal

# Import with overwrite instead of merge
./py2to3 import package.tar.gz --overwrite
```

**Use Cases:**
- Share migration strategies and configurations with team members
- Create reusable templates from successful migrations
- Move migration state between dev, staging, and production
- Bootstrap new similar projects with proven configurations
- Share knowledge and learnings with the community

Perfect for:
- Team collaboration on large migrations
- Creating organization-wide migration standards
- Distributing best practices across projects
- Backing up complete migration configurations
- Testing migrations in isolated environments

See [EXPORT_GUIDE.md](EXPORT_GUIDE.md) for complete documentation.

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

**Pre-commit Hooks for Preventing Regression**

Prevent Python 2 code from being committed with automated pre-commit hooks:

```bash
# Install pre-commit hooks (normal strictness)
./py2to3 precommit install

# Install with strict mode (maximum protection)
./py2to3 precommit install --mode strict

# Install with lenient mode (gradual adoption)
./py2to3 precommit install --mode lenient

# Check hook status
./py2to3 precommit status

# Test hooks without committing
./py2to3 precommit test

# Uninstall hooks if needed
./py2to3 precommit uninstall
```

**Use Cases:**
- Prevent Python 2 code regression during migration
- Enforce Python 3 compatibility across the team
- Catch issues before code review
- Reduce CI/CD failures from Python 2 code

Perfect for:
- Teams working on migration together
- Preventing accidental Python 2 commits
- Enforcing migration standards
- Providing instant developer feedback

**How it works:**
1. Generates `.pre-commit-config.yaml` configuration
2. Creates custom Python 3 validator hook
3. Integrates with popular pre-commit framework
4. Runs automatically before each commit
5. Blocks commits with Python 2 code

**Three Strictness Modes:**
- **Strict**: Catches any Python 2 patterns (post-migration)
- **Normal**: Catches common Python 2 issues (during migration)
- **Lenient**: Catches only critical issues (starting migration)

See [PRECOMMIT_GUIDE.md](PRECOMMIT_GUIDE.md) for complete documentation.

**Interactive Progress Dashboard for Visual Tracking**

Visualize your migration progress with beautiful interactive charts:

```bash
# Generate the dashboard (uses existing stats snapshots)
./py2to3 dashboard

# For best results, collect stats regularly during migration
./py2to3 stats collect --save    # After each fix session
./py2to3 dashboard                # Regenerate dashboard

# Open the dashboard in your browser
open migration_dashboard.html    # macOS
xdg-open migration_dashboard.html # Linux
start migration_dashboard.html    # Windows
```

**Dashboard Features:**
- 📉 **Burndown Chart** - Visualize issues decreasing over time
- 📈 **Progress Chart** - Track completion percentage
- 📊 **Distribution Charts** - Issues by type and severity
- ⚡ **Velocity Tracking** - See your progress rate (% per day)
- 🎯 **ETA Prediction** - Estimated completion date based on velocity
- 📈 **Trend Analysis** - Know if you're improving, stable, or declining

Perfect for:
- Team standups and status meetings
- Stakeholder presentations and reporting
- Tracking migration velocity over time
- Identifying when to allocate more resources
- Celebrating progress with visual proof!

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
