# Python 2 to Python 3 Refactoring Example

This directory contains a comprehensive example of refactoring Python 2 code to Python 3, demonstrating the use of programmatic fixer and verifier tools for automated code migration.

## Overview

This example showcases a realistic Python 2 web scraping application with complex interdependencies that needs to be upgraded to Python 3. The project includes:

1. **A complete Python 2 application** with 10 interconnected modules
2. **A programmatic fixer tool** that automatically converts Python 2 patterns to Python 3
3. **A programmatic verifier tool** that validates Python 3 compatibility and identifies remaining issues

## Directory Structure

```
examples/python-2to3/
├── README.md                 # This file
├── fixer.py                 # Programmatic Python 2→3 fixer tool
├── verifier.py              # Python 3 compatibility verifier tool
├── core/                    # Core application logic
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   └── config.py            # Configuration management with ConfigParser
├── models/                  # Data models
│   ├── __init__.py
│   └── models.py            # Data models (old-style and new-style classes)
├── data/                    # Data processing and database
│   ├── __init__.py
│   ├── data_processor.py    # Data processing and text extraction
│   └── database.py          # Database management with MySQL and threading
├── web/                     # Web scraping functionality
│   ├── __init__.py
│   └── web_scraper.py       # Web scraping using urllib2 and HTMLParser
├── utils/                   # Utility functions and validators
│   ├── __init__.py
│   ├── utils.py             # Utility functions and classes
│   └── validators.py        # Data validation utilities
└── tests/                   # Test functionality
    ├── __init__.py
    └── test_runner.py       # Test suite using unittest
```

## 1. Python 2 Application (organized in multiple directories)

The example Python 2 application is a web scraper and data processor that demonstrates numerous Python 2 patterns that need updating:

### Key Python 2 Patterns Demonstrated:

- **Print statements**: `print "message"` instead of `print("message")`
- **Import changes**: `urllib2`, `urlparse`, `ConfigParser`, `cPickle`, `StringIO`, `HTMLParser`, `Queue`
- **String handling**: `basestring`, `unicode()`, encoding issues
- **Iterator methods**: `iteritems()`, `iterkeys()`, `itervalues()`, `xrange()`
- **Exception syntax**: `except Exception, e:` instead of `except Exception as e:`
- **Class definitions**: Old-style classes without `object` inheritance
- **Comparison**: `cmp()` function and `__cmp__` methods
- **File handling**: Different default encodings and modes

### Application Components:

1. **core/main.py**: Entry point that orchestrates web scraping and data processing
2. **core/config.py**: Configuration management using ConfigParser
3. **data/database.py**: MySQL database operations with connection pooling and threading
4. **data/data_processor.py**: Text processing, regex operations, data transformation
5. **web/web_scraper.py**: HTTP requests using urllib2, HTML parsing, cookie handling
6. **models/models.py**: Data models showing old-style vs new-style classes
7. **utils/utils.py**: Utility functions for logging, file handling, caching, threading
8. **utils/validators.py**: Data validation with string and URL processing
9. **tests/test_runner.py**: Comprehensive test suite using unittest

### Directory Dependencies:

- **core/**: depends on models/, data/, web/, utils/
- **data/**: depends on models/, utils/
- **web/**: depends on utils/
- **tests/**: depends on all other directories
- **models/**: no dependencies (base layer)
- **utils/**: no dependencies (base layer)

## 2. Programmatic Fixer (`fixer.py`)

The fixer tool is a **Python 3 application** that automatically converts Python 2 code to Python 3 compatible code.

### Features:

- **Automatic pattern replacement**: Converts common Python 2 patterns to Python 3 equivalents
- **Import modernization**: Updates import statements to Python 3 modules
- **Syntax fixes**: Converts print statements, exception syntax, etc.
- **Backup creation**: Creates timestamped backups before making changes
- **Comprehensive reporting**: Generates detailed reports of all changes made
- **Batch processing**: Can process individual files or entire directory trees

### Usage:

```bash
# Fix a single file
python fixer.py core/main.py

# Fix entire directory recursively
python fixer.py .

# Fix with custom backup directory and report
python fixer.py . --backup-dir my_backups --report conversion_report.txt
```

### Supported Fixes:

- Print statements → print() functions
- urllib2 → urllib.request
- ConfigParser → configparser
- cPickle → pickle
- StringIO → io.StringIO
- basestring → str
- xrange() → range()
- dict.iteritems() → dict.items()
- Old exception syntax → new syntax
- Old-style classes → new-style classes
- And many more...

## 3. Programmatic Verifier (`verifier.py`)

The verifier tool is a **Python 3 application** that analyzes code for Python 3 compatibility and identifies remaining issues.

### Features:

- **Syntax validation**: Checks if code parses correctly with Python 3
- **Pattern detection**: Identifies remaining Python 2 patterns
- **Import analysis**: Detects problematic imports using AST parsing
- **Encoding checks**: Validates file encoding declarations
- **Severity classification**: Categorizes issues as errors vs warnings
- **Detailed reporting**: Provides specific suggestions for each issue
- **Integration with 2to3**: Can run the official 2to3 tool for comparison

### Usage:

```bash
# Verify a single file
python verifier.py core/main.py

# Verify entire directory
python verifier.py .

# Generate detailed report
python verifier.py . --report compatibility_report.txt

# Also run official 2to3 tool
python verifier.py . --use-2to3
```

### Verification Categories:

- **Errors**: Issues that will cause failures in Python 3
- **Warnings**: Issues that may cause problems or are not best practices
- **Syntax errors**: Code that doesn't parse in Python 3
- **Import issues**: Problematic module imports
- **Encoding issues**: Missing or incorrect encoding declarations

## Example Workflow

Here's how to use these tools together for a complete Python 2→3 migration:

### 1. Initial Assessment
```bash
# First, verify the current state
python verifier.py . --report initial_assessment.txt
```

### 2. Automatic Fixing
```bash
# Apply automatic fixes
python fixer.py . --backup-dir backups --report fixes_applied.txt
```

### 3. Verification
```bash
# Verify the results
python verifier.py . --report post_fix_verification.txt
```

### 4. Manual Review
- Review the generated reports
- Address any remaining issues manually
- Test the application thoroughly

### 5. Final Validation
```bash
# Final compatibility check
python verifier.py . --use-2to3
```

## Key Learning Points

This example demonstrates:

1. **Realistic complexity**: The application has genuine interdependencies and uses many Python 2 patterns
2. **Automated tooling**: Shows how programmatic tools can handle bulk conversions
3. **Verification importance**: Highlights the need for thorough validation after automated fixes
4. **Incremental approach**: Demonstrates a systematic approach to large-scale refactoring
5. **Best practices**: Shows proper backup, reporting, and validation procedures

## Running the Example

To experiment with this example:

1. **Examine the Python 2 code**: Look at the various files to understand the patterns
2. **Run the verifier**: See what issues are detected in the original code
3. **Apply the fixer**: Watch how the code is automatically transformed
4. **Verify results**: Check what issues remain after fixing
5. **Compare approaches**: Try different fixing strategies and compare results

This example provides a comprehensive foundation for understanding automated Python 2→3 migration and can be adapted for real-world refactoring projects.