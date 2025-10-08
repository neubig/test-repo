
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

1. **Fixer Tool (`src/fixer.py`)**:
   - Automatically converts Python 2 code to Python 3
   - Handles common patterns, imports, syntax, and more
   - Creates backups and generates detailed reports

2. **Verifier Tool (`src/verifier.py`)**:
   - Analyzes code for Python 3 compatibility
   - Identifies remaining issues with severity classification
   - Integrates with the official 2to3 tool

3. **Report Generator (`src/report_generator.py`)** 🆕:
   - Generates comprehensive HTML reports for migration progress
   - Beautiful, interactive visualizations with charts and statistics
   - Side-by-side code comparisons showing before/after changes
   - Detailed issue tracking with severity classification
   - Export data as JSON for further analysis
   - Perfect for presenting migration progress to stakeholders
   - **See `demo_report.html` for a live example!**

### Modern Web Application

The `my-vite-app/` directory contains a modern web application built with:
- React
- TypeScript
- Vite (with HMR support)
- ESLint with TypeScript integration

## Getting Started

### Python 2 to Python 3 Refactoring

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
