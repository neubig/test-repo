# Package Upgrade Recommender Guide

## Overview

The **Package Upgrade Recommender** is a powerful tool that helps you upgrade your Python package dependencies during Python 2 to 3 migration. It analyzes your `requirements.txt`, checks each package for Python 3 compatibility on PyPI, and recommends version upgrades.

## Why Use This Tool?

When migrating from Python 2 to Python 3, one of the biggest challenges is ensuring all your dependencies are compatible with Python 3. This tool automates that process by:

- 🔍 **Checking Python 3 compatibility** for all packages
- 📦 **Finding latest versions** available on PyPI
- ⚠️ **Identifying Python 2-only packages** that need alternatives
- 📋 **Generating updated requirements** with recommended versions
- 📊 **Providing detailed reports** in multiple formats

## Quick Start

### Basic Usage

```bash
# Analyze your requirements.txt
python3 src/package_upgrade_recommender.py

# Or via the CLI tool
./py2to3 packages analyze
```

### With Verbose Output

```bash
# See detailed progress as each package is checked
python3 src/package_upgrade_recommender.py -v
```

### Generate Updated Requirements

```bash
# Create a new requirements-py3.txt with recommended versions
python3 src/package_upgrade_recommender.py --generate-requirements requirements-py3.txt
```

## Command Reference

### Basic Command

```bash
python3 src/package_upgrade_recommender.py [OPTIONS] [REQUIREMENTS_FILE]
```

### Options

| Option | Description |
|--------|-------------|
| `requirements_file` | Path to requirements.txt (default: requirements.txt) |
| `-v, --verbose` | Show detailed progress for each package |
| `-f, --format` | Output format: text, markdown, or json (default: text) |
| `-o, --output` | Save report to file |
| `--generate-requirements FILE` | Generate updated requirements.txt |

## Examples

### Example 1: Basic Analysis

```bash
$ python3 src/package_upgrade_recommender.py
================================================================================
Package Upgrade Recommendations for Python 3 Migration
================================================================================

Summary:
  Total packages:        8
  ✓ Up to date:          3
  ↑ Upgrades available:  4
  ✗ Python 2 only:       1
  ? Not found:           0
  ! Errors:              0

--------------------------------------------------------------------------------
↑ Packages with Upgrades Available
--------------------------------------------------------------------------------

requests
  Current:  2.18.0
  Latest:   2.31.0
  Python 3: Yes
  Requires: >=3.7
  Status:   Upgrade available: 2.18.0 → 2.31.0
  Homepage: https://requests.readthedocs.io
...
```

### Example 2: Verbose Analysis

```bash
$ python3 src/package_upgrade_recommender.py -v
Analyzing 8 packages...

[1/8] Checking requests... ↑ upgrade_available
[2/8] Checking flask... ✓ ok
[3/8] Checking django... ↑ upgrade_available
[4/8] Checking pylint... ✓ ok
[5/8] Checking futures... ✗ python2_only
[6/8] Checking six... ↑ upgrade_available
[7/8] Checking pytest... ✓ ok
[8/8] Checking beautifulsoup4... ↑ upgrade_available
...
```

### Example 3: Generate Markdown Report

```bash
$ python3 src/package_upgrade_recommender.py -f markdown -o package_report.md
Report saved to: package_report.md
```

### Example 4: Generate Updated Requirements

```bash
$ python3 src/package_upgrade_recommender.py --generate-requirements requirements-py3.txt

Updated requirements saved to: requirements-py3.txt
⚠️  Please review and test the updated requirements before using!
```

### Example 5: Custom Requirements File

```bash
$ python3 src/package_upgrade_recommender.py requirements-dev.txt -v
```

## Output Formats

### Text Format (Default)

Clean, readable text output suitable for terminal viewing:

```
================================================================================
Package Upgrade Recommendations for Python 3 Migration
================================================================================

Summary:
  Total packages:        5
  ✓ Up to date:          2
  ↑ Upgrades available:  3
...
```

### Markdown Format

Structured markdown with tables, perfect for documentation and tracking:

```markdown
# Package Upgrade Recommendations

## Summary

- **Total packages**: 5
- ✓ **Up to date**: 2
- ↑ **Upgrades available**: 3

## Packages with Upgrades Available

| Package | Current | Latest | Python 3 | Requires Python |
|---------|---------|--------|----------|-----------------|
| requests | 2.18.0 | 2.31.0 | ✓ | >=3.7 |
...
```

### JSON Format

Machine-readable format for automation and integration:

```json
{
  "packages": [
    {
      "name": "requests",
      "current_version": "2.18.0",
      "latest_version": "2.31.0",
      "python3_compatible": true,
      "requires_python": ">=3.7",
      "status": "upgrade_available",
      "message": "Upgrade available: 2.18.0 → 2.31.0",
      "homepage": "https://requests.readthedocs.io"
    }
  ],
  "stats": {
    "total": 5,
    "ok": 2,
    "upgrade_available": 3
  }
}
```

## Package Status Codes

The tool categorizes each package with one of these status codes:

| Status | Symbol | Meaning |
|--------|--------|---------|
| `ok` | ✓ | Package is up to date and Python 3 compatible |
| `upgrade_available` | ↑ | Newer version available that supports Python 3 |
| `python2_only` | ✗ | Package only supports Python 2, find alternative |
| `not_found` | ? | Package not found on PyPI |
| `error` | ! | Error occurred while checking package |

## Understanding the Results

### Packages with Upgrades Available (↑)

These packages have newer versions available. You should:

1. Check the changelog for breaking changes
2. Update your requirements.txt to the latest version
3. Test your application thoroughly

Example:
```
requests
  Current:  2.18.0
  Latest:   2.31.0
  Python 3: Yes
  Requires: >=3.7
```

### Python 2 Only Packages (✗)

These packages don't support Python 3. You need to:

1. Find an alternative package
2. Check if the package has a Python 3 fork
3. Consider if you really need this dependency

Common Python 2-only packages and alternatives:
- `futures` → Use built-in `concurrent.futures` in Python 3
- `trollius` → Use built-in `asyncio` in Python 3
- `subprocess32` → Use built-in `subprocess` in Python 3

### Up to Date Packages (✓)

These packages are already at the latest version and support Python 3. No action needed!

## Generated Requirements File

When you use `--generate-requirements`, the tool creates a new requirements file with:

1. **Updated versions**: Latest Python 3 compatible versions
2. **Comments for Python 2-only packages**: Marked with comments
3. **Warnings**: Packages that need manual review

Example generated file:

```
# Updated requirements for Python 3
# Generated from: requirements.txt

requests==2.31.0
flask==3.0.0
django==4.2.7

# futures - Python 2 only, find alternative
# futures==3.3.0

pytest==7.4.3
six==1.16.0
```

## Best Practices

### 1. Review Before Applying

Always review the recommended upgrades before applying them:

```bash
# Generate report first
python3 src/package_upgrade_recommender.py -o review.txt

# Review the changes
cat review.txt

# Then generate updated requirements
python3 src/package_upgrade_recommender.py --generate-requirements requirements-py3.txt
```

### 2. Test Incrementally

Don't upgrade all packages at once:

```bash
# 1. Start with a few packages
# 2. Test your application
# 3. Upgrade more packages
# 4. Repeat until all upgraded
```

### 3. Check Changelogs

For major version upgrades, always check the changelog:

```bash
# The tool provides homepage URLs
# Visit them to read about breaking changes
```

### 4. Use Virtual Environments

Always test in a virtual environment:

```bash
# Create test environment
python3 -m venv test-env
source test-env/bin/activate

# Install updated requirements
pip install -r requirements-py3.txt

# Run your tests
pytest

# If everything works, update main requirements
```

### 5. Handle Python 2-Only Packages

For packages marked as Python 2-only:

1. **Check for alternatives**: Search PyPI for similar packages
2. **Check package repository**: Some have Python 3 branches
3. **Remove if unnecessary**: Maybe you don't need it anymore

## Integration with Migration Workflow

### Step 1: Before Migration

```bash
# Analyze current dependencies
python3 src/package_upgrade_recommender.py -v -o pre-migration-packages.txt
```

### Step 2: During Migration

```bash
# Generate updated requirements
python3 src/package_upgrade_recommender.py --generate-requirements requirements-py3.txt

# Review and edit as needed
vim requirements-py3.txt
```

### Step 3: After Migration

```bash
# Install updated packages
pip install -r requirements-py3.txt

# Run tests
pytest

# If successful, replace old requirements
mv requirements-py3.txt requirements.txt
```

## Troubleshooting

### Package Not Found

**Problem**: Package shows as "not found" but you know it exists.

**Solutions**:
- Check the package name spelling
- Some packages were renamed (e.g., `PIL` → `Pillow`)
- Package might have been removed from PyPI

### Connection Errors

**Problem**: Errors connecting to PyPI.

**Solutions**:
- Check your internet connection
- Check if PyPI is accessible: `ping pypi.org`
- Try again later if PyPI is having issues

### Version Conflicts

**Problem**: Updated packages have conflicting dependencies.

**Solutions**:
- Use `pip-tools` to resolve dependencies
- Check compatibility matrices on package documentation
- Consider using `poetry` or `pipenv` for better dependency management

## Common Scenarios

### Scenario 1: Legacy Django Project

```bash
# Analyze Django and related packages
python3 src/package_upgrade_recommender.py

# You might see:
# Django: 1.11 → 4.2 (major upgrade!)
# Check Django upgrade guide for migration path
```

### Scenario 2: Scientific Computing Stack

```bash
# numpy, scipy, pandas, matplotlib
# These usually have good Python 3 support
# But check for NumPy API changes between versions
```

### Scenario 3: Web Scraping Tools

```bash
# Beautiful Soup, requests, lxml
# Usually straightforward upgrades
# Test thoroughly with your specific use cases
```

## Tips and Tricks

### Tip 1: Save Reports for Tracking

```bash
# Generate dated reports
python3 src/package_upgrade_recommender.py -f markdown -o "package-report-$(date +%Y%m%d).md"
```

### Tip 2: Use with Git

```bash
# Commit before upgrading
git add requirements.txt
git commit -m "Pre-upgrade requirements snapshot"

# Generate and test upgrades
python3 src/package_upgrade_recommender.py --generate-requirements requirements-py3.txt
cp requirements-py3.txt requirements.txt

# Test...
# If it works:
git add requirements.txt
git commit -m "Upgrade packages for Python 3"

# If it doesn't work:
git checkout requirements.txt
```

### Tip 3: Automate in CI/CD

```yaml
# .github/workflows/check-packages.yml
name: Check Package Upgrades
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for upgrades
        run: python3 src/package_upgrade_recommender.py -f json -o upgrades.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: package-upgrades
          path: upgrades.json
```

## FAQ

**Q: Will this tool automatically upgrade my packages?**

A: No, it only recommends upgrades. You need to review and apply them manually.

**Q: How does it determine Python 3 compatibility?**

A: It checks PyPI metadata including `requires_python` field and classifiers.

**Q: What if a package claims Python 3 support but doesn't work?**

A: Always test! The tool relies on package metadata, which may not be accurate.

**Q: Can I use this with `setup.py` or `pyproject.toml`?**

A: Currently it only supports `requirements.txt`. Convert your dependencies first:
```bash
pip freeze > requirements.txt
```

**Q: Does it check for security vulnerabilities?**

A: No, use tools like `pip-audit` or `safety` for security checking.

## Related Tools

- **dependency_analyzer.py**: Analyzes import statements
- **verifier.py**: Checks code for Python 3 compatibility
- **doctor.py**: Comprehensive environment diagnostics

## Additional Resources

- [Python 3 Porting Guide](https://docs.python.org/3/howto/pyporting.html)
- [PyPI Package Search](https://pypi.org/)
- [Python 3 Statement](https://python3statement.org/)
- [Can I Use Python 3?](https://caniusepython3.com/)

## Getting Help

If you encounter issues:

1. Check this guide
2. Run with `-v` for verbose output
3. Check the package on PyPI manually
4. Review the error messages carefully

## Contributing

Found a bug or have suggestions? This tool is part of the Python 2 to 3 migration toolkit. Contributions welcome!

---

**Happy migrating! 🚀**
