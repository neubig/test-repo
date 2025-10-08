# Dependency Analyzer Guide

The Dependency Analyzer is a powerful tool for analyzing Python 2 dependencies and identifying compatibility issues when migrating to Python 3. It helps you understand which packages need to be updated, replaced, or verified before completing your migration.

## Overview

The dependency analyzer scans your project for:
- Dependencies declared in `requirements.txt`
- Dependencies in `setup.py` (install_requires)
- Import statements in Python source files

It then analyzes each dependency for Python 3 compatibility and provides detailed reports with recommendations.

## Quick Start

### Basic Analysis

Analyze dependencies in the current directory:

```bash
./py2to3 deps
```

Analyze a specific project path:

```bash
./py2to3 deps src/
```

### Save Report to File

Generate a text report:

```bash
./py2to3 deps src/ --output dependency_report.txt
```

Generate a JSON report for programmatic processing:

```bash
./py2to3 deps src/ --format json --output dependency_report.json
```

## What It Checks

### 1. Standard Library Renames

The analyzer identifies Python 2 standard library modules that have been renamed in Python 3:

- `ConfigParser` → `configparser`
- `Queue` → `queue`
- `urllib2` → `urllib.request, urllib.error`
- `urlparse` → `urllib.parse`
- `HTMLParser` → `html.parser`
- `cookielib` → `http.cookiejar`
- And many more...

### 2. Incompatible Packages

Identifies third-party packages that are not Python 3 compatible and suggests alternatives:

- `PIL` → Use `pillow` instead
- `mysql-python` → Use `mysqlclient` or `PyMySQL` instead

### 3. Packages Needing Upgrade

For packages that support Python 3 but require minimum versions:

- Django: Minimum 1.11, Recommended 4.2+
- Flask: Minimum 0.10, Recommended 2.3+
- NumPy: Minimum 1.11, Recommended 1.24+
- Pandas: Minimum 0.19, Recommended 2.0+
- And more...

## Command Line Options

```bash
py2to3 deps [path] [options]
```

### Arguments

- `path` (optional): Project path to analyze. Default: current directory

### Options

- `-o, --output FILE`: Save report to file instead of printing to console
- `-f, --format {text,json}`: Output format. Default: text
  - `text`: Human-readable formatted report
  - `json`: Structured JSON for programmatic processing
- `-h, --help`: Show help message

## Report Structure

### Text Format

The text report includes:

1. **Summary**: Total count by category
2. **Standard Library Renames**: Modules that need import updates
3. **Incompatible Packages**: Packages requiring alternatives
4. **Packages Needing Upgrade**: Minimum and recommended versions
5. **Compatible Packages**: Packages already compatible
6. **Unknown Packages**: Packages requiring manual verification
7. **Recommendations**: Action items based on findings

### JSON Format

The JSON report provides structured data:

```json
{
  "stdlib_renames": [
    {
      "package": "ConfigParser",
      "py3_name": "configparser",
      "locations": [
        {
          "source": "path/to/file.py",
          "line": 10,
          "raw": "ConfigParser"
        }
      ]
    }
  ],
  "incompatible": [...],
  "needs_upgrade": [...],
  "compatible": [...],
  "unknown": [...]
}
```

## Integration with Workflow

### Pre-Migration Analysis

Run dependency analysis before starting migration:

```bash
# Step 1: Run preflight checks
./py2to3 preflight src/

# Step 2: Analyze dependencies
./py2to3 deps src/ --output deps_report.txt

# Step 3: Review reports and plan migration
cat deps_report.txt

# Step 4: Update requirements.txt based on recommendations
# Step 5: Proceed with migration
./py2to3 migrate src/
```

### Update Requirements File

After analyzing dependencies, update your `requirements.txt`:

```bash
# Before (Python 2)
Django==1.8
mysql-python==1.2.5
PIL==1.1.7

# After (Python 3)
Django>=4.2
mysqlclient>=2.0  # or PyMySQL>=1.0
pillow>=10.0
```

### CI/CD Integration

Use JSON output in automated pipelines:

```bash
# Generate JSON report
./py2to3 deps . --format json --output deps.json

# Parse and act on results
python3 -c "
import json
with open('deps.json') as f:
    data = json.load(f)
    if data['incompatible'] or data['stdlib_renames']:
        print('Action required!')
        exit(1)
"
```

## Common Scenarios

### Scenario 1: Web Application with Django

```bash
$ ./py2to3 deps myproject/

# Output shows:
# - Django needs upgrade to 2.0+
# - urllib2 → urllib.request
# - Update requirements.txt
# - Fix import statements
```

### Scenario 2: Data Science Project

```bash
$ ./py2to3 deps data_analysis/

# Output shows:
# - NumPy, Pandas need version upgrades
# - cPickle → pickle (standard library)
# - No incompatible packages
```

### Scenario 3: Legacy Application

```bash
$ ./py2to3 deps legacy_app/

# Output shows:
# - Multiple standard library renames
# - Some packages have no Python 3 version
# - Suggestions for alternatives provided
```

## Understanding Results

### Exit Codes

- `0`: All dependencies are compatible or only need minor updates
- `1`: Action required - incompatible packages or standard library renames found

### Priority Actions

1. **Critical**: Replace incompatible packages
   - Must be done before Python 3 migration
   - Alternative packages suggested in report

2. **High**: Update standard library imports
   - The fixer tool can automate most of these
   - Run `./py2to3 fix` to apply automatically

3. **Medium**: Upgrade package versions
   - Update version specifiers in requirements.txt
   - Test thoroughly after upgrading

4. **Low**: Verify unknown packages
   - Check package documentation
   - Search PyPI for Python 3 support status

## Tips and Best Practices

### 1. Run Early and Often

Run dependency analysis at the start of your migration project:

```bash
./py2to3 deps . --output deps_baseline.txt
```

Re-run after making changes to track progress.

### 2. Use JSON for Automation

For large projects or CI/CD pipelines:

```bash
./py2to3 deps . --format json --output deps.json
```

Parse the JSON to integrate with other tools.

### 3. Update Virtual Environment

Create a Python 3 virtual environment and test package installation:

```bash
python3 -m venv venv3
source venv3/bin/activate
pip install -r requirements.txt  # May fail if incompatible packages exist
```

### 4. Check Package Documentation

For unknown packages, visit their:
- PyPI page
- GitHub repository
- Official documentation
- Release notes

### 5. Test After Updates

After updating dependencies:

```bash
# Install updated packages
pip install -r requirements.txt

# Run tests
pytest

# Run your application
python app.py
```

## Extending the Analyzer

### Adding Custom Package Rules

The analyzer includes compatibility information for common packages. To add more:

1. Edit `src/dependency_analyzer.py`
2. Add entries to `PACKAGE_COMPATIBILITY` dictionary
3. Include version info and notes

Example:

```python
PACKAGE_COMPATIBILITY = {
    'your-package': {
        'py3_min_version': '2.0',
        'recommended': '3.0',
        'notes': 'Version 2.0+ supports Python 3.'
    }
}
```

### Standalone Usage

The analyzer can also be used as a standalone Python module:

```python
from dependency_analyzer import DependencyAnalyzer

analyzer = DependencyAnalyzer('/path/to/project')
analyzer.scan_all()
report = analyzer.generate_report('text')
print(report)
```

## Troubleshooting

### Issue: False Positives in Unknown Packages

**Cause**: Local modules are listed as unknown packages.

**Solution**: This is expected. Local modules (like `models`, `utils`, etc.) will appear as unknown. Focus on the stdlib_renames and third-party packages.

### Issue: Missing Dependencies

**Cause**: Dependencies only in code, not in requirements.txt.

**Solution**: The analyzer scans both files and imports. Check the report for all discovered dependencies.

### Issue: Version Information Not Available

**Cause**: Package not in the built-in compatibility database.

**Solution**: Manually check PyPI or package documentation. Consider adding to `PACKAGE_COMPATIBILITY` for future use.

## Related Commands

- `./py2to3 preflight` - Pre-migration environment checks
- `./py2to3 check` - Check Python 3 compatibility
- `./py2to3 fix` - Apply automated fixes (including import updates)
- `./py2to3 migrate` - Complete migration workflow

## Best Practices Summary

1. ✅ Run dependency analysis before migration
2. ✅ Save reports for reference and comparison
3. ✅ Update requirements.txt based on findings
4. ✅ Replace incompatible packages first
5. ✅ Use fixer tool for standard library renames
6. ✅ Upgrade packages to Python 3 compatible versions
7. ✅ Test thoroughly after dependency updates
8. ✅ Re-run analysis to verify changes

## Support

For issues or questions:
- Check this guide
- Run `./py2to3 deps --help` for command syntax
- Review the main README.md for general information
- Check other guide files for related features

---

Happy migrating! 🚀
