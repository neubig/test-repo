#!/usr/bin/env python3
"""
Migration Documentation Generator

Generates comprehensive Markdown documentation for Python 2 to 3 migrations.
Creates version-control-friendly documentation that can be shared with teams.
"""

import datetime
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class MigrationDocGenerator:
    """Generate comprehensive migration documentation in Markdown format."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.docs_dir = self.project_path / ".migration_docs"
        self.docs_dir.mkdir(exist_ok=True)
        
    def generate_full_documentation(
        self,
        stats: Optional[Dict] = None,
        backup_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate complete migration documentation suite."""
        
        # Collect data
        if stats is None:
            stats = self._collect_stats()
        
        docs = {}
        
        # Generate different documentation types
        docs['summary'] = self._generate_summary(stats)
        docs['guide'] = self._generate_guide(stats)
        docs['changelog'] = self._generate_changelog(stats, backup_dir)
        docs['best_practices'] = self._generate_best_practices()
        
        # Save all documents
        saved_paths = {}
        for doc_type, content in docs.items():
            filename = f"MIGRATION_{doc_type.upper()}.md"
            filepath = self.docs_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            saved_paths[doc_type] = str(filepath)
        
        # Also create a master index
        index_content = self._generate_index(saved_paths)
        index_path = self.docs_dir / "README.md"
        with open(index_path, 'w') as f:
            f.write(index_content)
        saved_paths['index'] = str(index_path)
        
        return saved_paths
    
    def _collect_stats(self) -> Dict:
        """Collect current migration statistics."""
        try:
            from stats_tracker import MigrationStatsTracker
            tracker = MigrationStatsTracker()
            return tracker.collect_stats(str(self.project_path))
        except Exception as e:
            return {
                'summary': {
                    'total_files': 0,
                    'files_with_issues': 0,
                    'total_issues': 0,
                    'progress_percentage': 0
                },
                'by_severity': {},
                'by_type': {},
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def _generate_summary(self, stats: Dict) -> str:
        """Generate migration summary document."""
        summary = stats.get('summary', {})
        
        content = f"""# Python 2 to 3 Migration Summary

**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document provides a high-level summary of the Python 2 to Python 3 migration
project for this codebase.

## Migration Status

| Metric | Value |
|--------|-------|
| Total Files Analyzed | {summary.get('total_files', 0)} |
| Files with Issues | {summary.get('files_with_issues', 0)} |
| Total Issues Found | {summary.get('total_issues', 0)} |
| Migration Progress | {summary.get('progress_percentage', 0):.1f}% |
| Status | {'✅ Complete' if summary.get('progress_percentage', 0) == 100 else '🔄 In Progress'} |

## Issue Breakdown by Severity

"""
        
        by_severity = stats.get('by_severity', {})
        if by_severity:
            content += "| Severity | Count |\n|----------|-------|\n"
            for severity, count in sorted(by_severity.items(), key=lambda x: x[1], reverse=True):
                emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(severity.lower(), '⚪')
                content += f"| {emoji} {severity.title()} | {count} |\n"
        else:
            content += "_No issues found - migration complete!_ ✅\n"
        
        content += "\n## Issue Breakdown by Type\n\n"
        
        by_type = stats.get('by_type', {})
        if by_type:
            # Show top 10 issue types
            sorted_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]
            content += "| Issue Type | Count |\n|------------|-------|\n"
            for issue_type, count in sorted_types:
                content += f"| {issue_type} | {count} |\n"
        else:
            content += "_No issues found._\n"
        
        content += f"""

## Key Achievements

- ✅ Analyzed {summary.get('total_files', 0)} Python files
- ✅ Identified and documented {summary.get('total_issues', 0)} compatibility issues
- ✅ Achieved {summary.get('progress_percentage', 0):.1f}% migration progress
- ✅ Created comprehensive documentation and reports

## Next Steps

"""
        
        if summary.get('progress_percentage', 0) < 100:
            remaining = summary.get('files_with_issues', 0)
            content += f"""1. **Address Remaining Issues**: {remaining} files still have compatibility issues
2. **Run Automated Fixes**: Use `py2to3 fix` to automatically resolve common patterns
3. **Manual Review**: Review high-severity issues that require manual intervention
4. **Testing**: Run comprehensive tests to validate migrated code
5. **Documentation**: Update project documentation for Python 3
"""
        else:
            content += """1. ✅ **Migration Complete**: All known issues have been resolved
2. **Final Testing**: Run full test suite to validate functionality
3. **Performance Testing**: Verify performance meets expectations
4. **Team Review**: Conduct code review with team members
5. **Deployment**: Plan Python 3 deployment strategy
"""
        
        content += """

## Resources

- [Migration Guide](MIGRATION_GUIDE.md) - Detailed guide for working with migrated code
- [Changelog](MIGRATION_CHANGELOG.md) - Detailed list of all changes
- [Best Practices](MIGRATION_BEST_PRACTICES.md) - Python 3 best practices

## Support

For questions or issues related to this migration, please contact the development team
or refer to the project's documentation.

---

*This document was automatically generated by the py2to3 migration toolkit.*
"""
        
        return content
    
    def _generate_guide(self, stats: Dict) -> str:
        """Generate migration guide document."""
        content = f"""# Python 3 Migration Guide

**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Introduction

This guide helps developers understand and work with the Python 3 migrated codebase.
It covers key changes, common patterns, and how to maintain Python 3 compatibility.

## Environment Setup

### Python Version

This project now requires Python 3.6 or higher. To verify your Python version:

```bash
python3 --version
```

### Virtual Environment

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Key Changes from Python 2

### 1. Print Function

Python 3 uses `print()` as a function, not a statement.

```python
# Python 2 (old)
print "Hello, World!"

# Python 3 (new)
print("Hello, World!")
```

### 2. String Handling

All strings are Unicode by default in Python 3.

```python
# Python 2
unicode_text = u"Hello"
byte_string = "Hello"

# Python 3
text = "Hello"  # Already Unicode
byte_string = b"Hello"  # Explicit bytes
```

### 3. Dictionary Methods

Iterator methods return views instead of lists.

```python
# Python 2
for key, value in my_dict.iteritems():
    print key, value

# Python 3
for key, value in my_dict.items():
    print(key, value)
```

### 4. Division Operator

Division returns float by default.

```python
# Python 2
result = 5 / 2  # Returns 2 (integer division)

# Python 3
result = 5 / 2   # Returns 2.5 (float division)
result = 5 // 2  # Returns 2 (explicit integer division)
```

### 5. Exception Handling

New syntax for catching exceptions.

```python
# Python 2
try:
    risky_operation()
except Exception, e:
    handle_error(e)

# Python 3
try:
    risky_operation()
except Exception as e:
    handle_error(e)
```

### 6. Import Changes

Many standard library modules were reorganized.

```python
# Python 2
import ConfigParser
import urllib2
from urlparse import urljoin

# Python 3
import configparser
import urllib.request
from urllib.parse import urljoin
```

## Common Patterns

### File I/O

```python
# Always use context managers
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Specify encoding explicitly
with open('data.txt', 'w', encoding='utf-8') as f:
    f.write(text)
```

### Type Checking

```python
# Check for string types
if isinstance(value, str):  # Works for all text strings
    process_string(value)

# Check for bytes
if isinstance(value, bytes):
    decode_bytes(value)
```

### Working with Ranges

```python
# range() returns an iterator (like xrange in Python 2)
for i in range(1000000):  # Memory efficient
    process(i)

# Convert to list if needed
numbers = list(range(10))
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_module.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Writing Python 3 Compatible Tests

```python
import unittest

class TestExample(unittest.TestCase):
    def test_something(self):
        result = function_to_test()
        self.assertEqual(result, expected)
    
    def test_exception(self):
        with self.assertRaises(ValueError):
            invalid_operation()
```

## Maintaining Compatibility

### Code Review Checklist

- [ ] All print statements converted to functions
- [ ] No use of deprecated modules (urllib2, ConfigParser, etc.)
- [ ] Exception handling uses `as` syntax
- [ ] Dictionary iteration uses `.items()`, `.keys()`, `.values()`
- [ ] String types handled correctly (str vs bytes)
- [ ] Integer division explicit (// instead of /)
- [ ] File I/O includes encoding parameter
- [ ] All tests pass with Python 3

### Tools

Use these tools to maintain Python 3 compatibility:

```bash
# Check compatibility
./py2to3 check src/

# Run quality checks
./py2to3 quality src/

# Generate reports
./py2to3 report --output report.html
```

## Troubleshooting

### Import Errors

If you encounter import errors, verify:
1. Python 3 version is installed
2. All dependencies are installed (`pip install -r requirements.txt`)
3. Virtual environment is activated

### Encoding Issues

Always specify encoding explicitly:
```python
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()
```

### Type Errors

Check for:
- Mixing str and bytes
- Division operator usage
- Dictionary method returns (views vs lists)

## Additional Resources

- [Python 3 Official Documentation](https://docs.python.org/3/)
- [What's New in Python 3](https://docs.python.org/3/whatsnew/)
- [Porting Python 2 to Python 3](https://docs.python.org/3/howto/pyporting.html)

---

*This guide was automatically generated by the py2to3 migration toolkit.*
"""
        return content
    
    def _generate_changelog(self, stats: Dict, backup_dir: Optional[str]) -> str:
        """Generate detailed migration changelog."""
        content = f"""# Migration Changelog

**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document tracks all changes made during the Python 2 to Python 3 migration.

## Summary Statistics

"""
        summary = stats.get('summary', {})
        content += f"""- **Files Analyzed**: {summary.get('total_files', 0)}
- **Issues Identified**: {summary.get('total_issues', 0)}
- **Migration Progress**: {summary.get('progress_percentage', 0):.1f}%
- **Date**: {datetime.datetime.now().strftime('%Y-%m-%d')}

## Changes by Category

"""
        
        by_type = stats.get('by_type', {})
        if by_type:
            for issue_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                content += f"### {issue_type.replace('_', ' ').title()}\n\n"
                content += f"**Occurrences**: {count}\n\n"
                content += self._get_fix_description(issue_type)
                content += "\n\n"
        
        content += """## Migration Timeline

| Date | Activity | Status |
|------|----------|--------|
"""
        
        # Add timeline entry
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        content += f"| {today} | Documentation generated | ✅ Complete |\n"
        
        content += """

## Detailed Changes

### Automated Fixes Applied

The following categories of issues were automatically fixed:

1. **Print Statements**: Converted to print() function calls
2. **Import Statements**: Updated to Python 3 module names
3. **Exception Syntax**: Updated to use 'as' keyword
4. **Dictionary Methods**: Changed iteritems() to items()
5. **String Types**: Updated basestring to str
6. **Integer Division**: Made division explicit where needed

### Manual Review Required

Some changes may require manual review:

- Custom comparison methods (__cmp__)
- Complex encoding/decoding scenarios
- Third-party library compatibility
- Performance-critical sections

## Testing

### Test Results

After migration, ensure all tests pass:

```bash
pytest
```

### Recommended Tests

- Unit tests for all modified modules
- Integration tests for end-to-end workflows
- Performance tests for critical paths
- Edge case testing for data handling

## Rollback Information

"""
        
        if backup_dir:
            content += f"""Backups were created during migration and are stored in:
```
{backup_dir}
```

To restore a file:
```bash
./py2to3 backup restore {backup_dir}/path/to/file.py
```
"""
        else:
            content += "_No backup information available._\n"
        
        content += """

## Notes

- All changes are tracked in version control (git)
- Review git history for detailed commit-by-commit changes
- Use `git diff` to compare before and after states

## Sign-off

- [ ] Code review completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Team notified
- [ ] Deployment planned

---

*This changelog was automatically generated by the py2to3 migration toolkit.*
"""
        return content
    
    def _generate_best_practices(self) -> str:
        """Generate best practices document."""
        content = """# Python 3 Best Practices

**Generated:** """ + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

## Introduction

This document outlines best practices for maintaining Python 3 code after migration.

## Code Style

### 1. Use Modern String Formatting

```python
# Good
name = "World"
message = f"Hello, {name}!"

# Also good (for templates)
message = "Hello, {}!".format(name)

# Avoid (old style)
message = "Hello, %s!" % name
```

### 2. Type Hints

Add type hints for better code clarity:

```python
def process_data(items: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:
        result[item] = len(item)
    return result
```

### 3. Context Managers

Always use context managers for resources:

```python
# Good
with open('file.txt', 'r', encoding='utf-8') as f:
    data = f.read()

# Bad
f = open('file.txt', 'r')
data = f.read()
f.close()  # Can be forgotten
```

### 4. Pathlib

Use pathlib for file path manipulation:

```python
from pathlib import Path

# Good
config_file = Path('config') / 'settings.json'
if config_file.exists():
    content = config_file.read_text(encoding='utf-8')

# Avoid
import os
config_file = os.path.join('config', 'settings.json')
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        content = f.read()
```

## Performance

### 1. Use Generators

```python
# Memory efficient
def read_large_file(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield line.strip()

# Use it
for line in read_large_file('huge.txt'):
    process(line)
```

### 2. List Comprehensions

```python
# Fast and readable
squares = [x**2 for x in range(10)]

# Filter and transform
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

### 3. Dictionary Comprehensions

```python
# Create dictionaries efficiently
word_lengths = {word: len(word) for word in words}
```

## Error Handling

### 1. Specific Exceptions

```python
# Good - catch specific exceptions
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logging.error(f"JSON parsing failed: {e}")
    return None

# Bad - too broad
try:
    data = json.loads(text)
except Exception:
    return None
```

### 2. Context in Exceptions

```python
# Good - provide context
try:
    result = process_data(data)
except ValueError as e:
    raise ValueError(f"Failed to process data: {e}") from e
```

## Testing

### 1. Use pytest

```python
import pytest

def test_function():
    result = my_function(input_data)
    assert result == expected_value

def test_exception():
    with pytest.raises(ValueError):
        invalid_function()
```

### 2. Fixtures for Setup

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    result = process(sample_data)
    assert result is not None
```

## Documentation

### 1. Docstrings

```python
def calculate_total(items: List[float], tax_rate: float = 0.1) -> float:
    \"\"\"
    Calculate total price including tax.
    
    Args:
        items: List of item prices
        tax_rate: Tax rate (default 0.1 = 10%)
    
    Returns:
        Total price including tax
    
    Raises:
        ValueError: If tax_rate is negative
    \"\"\"
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

### 2. README Files

Keep README files up to date with:
- Python version requirements
- Installation instructions
- Usage examples
- Dependencies

## Dependencies

### 1. Use requirements.txt

```txt
# requirements.txt
requests>=2.25.0
pytest>=6.0.0
black>=20.8b1
```

### 2. Pin Dependencies

```txt
# For production
requests==2.25.1

# For development
pytest>=6.0.0,<7.0.0
```

## Code Quality

### 1. Use Linters

```bash
# Run flake8
flake8 src/

# Run pylint
pylint src/

# Format with black
black src/
```

### 2. Type Checking

```bash
# Run mypy
mypy src/
```

## Security

### 1. Validate Input

```python
def process_user_input(user_data: str) -> str:
    # Validate and sanitize
    if not user_data or len(user_data) > 1000:
        raise ValueError("Invalid input length")
    
    # Process safely
    return user_data.strip()
```

### 2. Use Secrets Module

```python
import secrets

# Generate secure tokens
token = secrets.token_urlsafe(32)

# Generate random numbers
secure_random = secrets.randbelow(100)
```

## Logging

### 1. Use Logging Module

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Processing started")
    try:
        result = transform(data)
        logger.info("Processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise
```

## Async Programming

### 1. Use Asyncio for I/O

```python
import asyncio
import aiohttp

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    urls = ['http://api1.com', 'http://api2.com']
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Run it
asyncio.run(main())
```

## Resources

- [PEP 8 - Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Python 3 Documentation](https://docs.python.org/3/)
- [Real Python Tutorials](https://realpython.com/)

---

*This guide was automatically generated by the py2to3 migration toolkit.*
"""
        return content
    
    def _generate_index(self, saved_paths: Dict[str, str]) -> str:
        """Generate index/readme for documentation."""
        content = f"""# Migration Documentation

**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This directory contains comprehensive documentation for the Python 2 to Python 3
migration project.

## Documents

### 📊 [Migration Summary](MIGRATION_SUMMARY.md)
High-level overview of the migration status, statistics, and progress.

### 📘 [Migration Guide](MIGRATION_GUIDE.md)
Detailed guide for developers working with the Python 3 codebase. Covers
key changes, common patterns, and development workflows.

### 📝 [Migration Changelog](MIGRATION_CHANGELOG.md)
Detailed changelog of all modifications made during the migration process.

### ✨ [Best Practices](MIGRATION_BEST_PRACTICES.md)
Python 3 best practices and coding standards for maintaining the codebase.

## Quick Start

1. **Read the Summary** - Get a quick overview of migration status
2. **Review the Guide** - Understand key changes and how to work with Python 3
3. **Check the Changelog** - See what was changed and why
4. **Follow Best Practices** - Write clean, modern Python 3 code

## Tools

This project uses the `py2to3` migration toolkit. Common commands:

```bash
# Check compatibility
./py2to3 check src/

# Apply fixes
./py2to3 fix src/

# Generate reports
./py2to3 report --output report.html

# View statistics
./py2to3 stats collect

# Update documentation
./py2to3 docs
```

## Support

For questions or issues:
1. Check the documentation in this directory
2. Review the main project README.md
3. Contact the development team

---

*This documentation was automatically generated by the py2to3 migration toolkit.*
"""
        return content
    
    def _get_fix_description(self, issue_type: str) -> str:
        """Get description of how an issue type was fixed."""
        descriptions = {
            'print_statement': """
**Fix Applied**: Converted print statements to function calls.

```python
# Before
print "Hello, World!"

# After
print("Hello, World!")
```
""",
            'import_urllib2': """
**Fix Applied**: Updated urllib2 imports to urllib.request.

```python
# Before
import urllib2

# After
import urllib.request
```
""",
            'import_configparser': """
**Fix Applied**: Updated ConfigParser import to configparser.

```python
# Before
import ConfigParser

# After
import configparser
```
""",
            'exception_syntax': """
**Fix Applied**: Updated exception handling syntax.

```python
# Before
except Exception, e:
    handle(e)

# After
except Exception as e:
    handle(e)
```
""",
            'dict_iteritems': """
**Fix Applied**: Changed iteritems() to items().

```python
# Before
for key, value in dict.iteritems():
    process(key, value)

# After
for key, value in dict.items():
    process(key, value)
```
""",
            'basestring': """
**Fix Applied**: Replaced basestring with str.

```python
# Before
if isinstance(value, basestring):
    process(value)

# After
if isinstance(value, str):
    process(value)
```
"""
        }
        
        return descriptions.get(issue_type, "_Automated fix applied._")


def main():
    """Command-line interface for documentation generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate migration documentation'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path to document (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for documentation (default: .migration_docs)'
    )
    parser.add_argument(
        '--backup-dir',
        help='Backup directory path for changelog'
    )
    
    args = parser.parse_args()
    
    generator = MigrationDocGenerator(args.path)
    if args.output_dir:
        generator.docs_dir = Path(args.output_dir)
        generator.docs_dir.mkdir(exist_ok=True)
    
    print("Generating migration documentation...")
    
    saved_paths = generator.generate_full_documentation(
        backup_dir=args.backup_dir
    )
    
    print("\n✅ Documentation generated successfully!\n")
    print("Generated documents:")
    for doc_type, path in saved_paths.items():
        print(f"  - {doc_type.title()}: {path}")
    
    print(f"\n📁 Documentation directory: {generator.docs_dir}")
    print(f"📖 Start with: {saved_paths.get('index', 'README.md')}")


if __name__ == '__main__':
    main()
