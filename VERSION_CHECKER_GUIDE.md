# Python Version Compatibility Checker Guide

## Overview

The **Python Version Compatibility Checker** is a powerful tool that analyzes your migrated Python 3 code to determine which Python 3.x versions it's compatible with. After migrating from Python 2 to Python 3, this tool helps you make informed decisions about which Python version(s) to target for deployment.

## Why Use the Version Checker?

After migrating to Python 3, you need to decide which Python 3.x version to support:
- **Different environments** may have different Python versions available
- **Modern features** (f-strings, walrus operator, pattern matching) require specific versions
- **Dependencies** may have version requirements
- **Deployment targets** (servers, containers, cloud platforms) may impose constraints
- **Team collaboration** benefits from knowing version requirements upfront

The version checker automatically analyzes your code and tells you:
- ✅ Minimum Python 3.x version required
- ✅ Which features require which versions
- ✅ Compatibility with specific target versions
- ✅ Standard library module usage and version requirements

## Quick Start

### Basic Usage

Check a single file:
```bash
./py2to3 version-check src/my_module.py
```

Check an entire directory:
```bash
./py2to3 version-check src/
```

### Check Compatibility with a Target Version

Check if your code works with Python 3.8:
```bash
./py2to3 version-check src/ -t 3.8
```

Check compatibility with Python 3.10:
```bash
./py2to3 version-check src/ --target 3.10
```

### Save Report to File

Save a text report:
```bash
./py2to3 version-check src/ -o compatibility_report.txt
```

Save a JSON report for CI/CD integration:
```bash
./py2to3 version-check src/ -f json -o compatibility_report.json
```

## Command Options

```
py2to3 version-check [options] <path>

Positional Arguments:
  path                  File or directory to analyze

Options:
  -o, --output FILE     Save report to file
  -f, --format FORMAT   Output format: text (default) or json
  -t, --target VERSION  Check compatibility with specific Python version
  -h, --help           Show help message
```

## Understanding the Report

### Text Report Format

The text report includes several sections:

#### 1. Summary
```
Files analyzed: 49
Minimum Python version required: 3.9
```

Shows how many files were analyzed and the minimum version needed.

#### 2. Version-Specific Features
```
Python 3.6+:
  • f-string literals (formatted string literals)
    Found 1636 occurrence(s)
  • Variable annotations (PEP 526)
    Found 35 occurrence(s)

Python 3.9+:
  • Union type operator (|) for type hints
    Found 10 occurrence(s)
```

Lists features found in your code grouped by the Python version they require.

#### 3. Standard Library Usage
```
Version-Specific Standard Library Usage:
  • dataclasses: Added in Python 3.7
    Found 2 occurrence(s)
```

Shows standard library modules that have version requirements.

#### 4. Compatibility Summary
```
Python 3.6: ✗ 2 incompatibility(ies)
Python 3.7: ✗ 1 incompatibility(ies)
Python 3.8: ✗ 1 incompatibility(ies)
Python 3.9: ✓ Compatible
Python 3.10: ✓ Compatible
Python 3.11: ✓ Compatible
Python 3.12: ✓ Compatible
```

Quick overview of compatibility with each Python 3.x version.

#### 5. Recommendations
```
Recommendations:
  • Target Python 3.9 or newer
  • Consider Python 3.8+ as minimum for modern features
```

Actionable recommendations based on the analysis.

### JSON Report Format

The JSON format is perfect for:
- CI/CD pipelines
- Automated tooling
- Custom analysis scripts
- Team dashboards

Example JSON structure:
```json
{
  "summary": {
    "files_analyzed": 49,
    "minimum_version": "3.9",
    "errors_count": 0
  },
  "features": {
    "f_strings": {
      "version": "3.6",
      "description": "f-string literals",
      "count": 1636,
      "locations": [...]
    }
  },
  "compatibility": {
    "3.8": {
      "compatible": false,
      "issues_count": 1,
      "issues": {...}
    },
    "3.9": {
      "compatible": true,
      "issues_count": 0,
      "issues": {}
    }
  }
}
```

## Detected Features by Python Version

### Python 3.5+
- Async/await syntax (`async def`, `await`)
- Async for loops and context managers
- Matrix multiplication operator (`@`)
- Extended unpacking generalizations

### Python 3.6+
- **f-strings** - Formatted string literals
- **Variable annotations** - Type hints on variables
- Async generators and comprehensions
- Underscores in numeric literals

### Python 3.7+
- **Dataclasses** - `@dataclass` decorator
- Postponed evaluation of annotations
- Built-in `breakpoint()` function

### Python 3.8+
- **Walrus operator** (`:=`) - Assignment expressions
- **Positional-only parameters** (`/` in function signatures)
- f-string `=` specifier for debugging

### Python 3.9+
- **Union type operator** (`|`) for type hints
- **Dict merge operator** (`|` and `|=`)
- `str.removeprefix()` and `str.removesuffix()`
- Generic type hints using built-in collections

### Python 3.10+
- **Pattern matching** (`match`/`case` statements)
- Parenthesized context managers
- Union types with `isinstance()`

### Python 3.11+
- Exception groups and `except*`
- Task groups in asyncio
- `tomllib` module in standard library

### Python 3.12+
- Type parameter syntax (PEP 695)
- `@override` decorator

## Common Use Cases

### 1. Post-Migration Version Decision

After migrating from Python 2:
```bash
# Analyze your entire codebase
./py2to3 version-check src/

# Result: Minimum Python version required: 3.8
# Decision: Target Python 3.8+ for deployment
```

### 2. Compatibility with Legacy Systems

Check if migrated code works with older Python 3:
```bash
# Your server only has Python 3.7
./py2to3 version-check src/ -t 3.7

# If incompatible, you'll see which features need refactoring
```

### 3. CI/CD Integration

Add version checking to your CI pipeline:
```bash
# In your CI script
./py2to3 version-check src/ -f json -o compatibility.json
python check_version_requirements.py compatibility.json
```

### 4. Multi-Version Support

Check compatibility across multiple versions:
```bash
# Check each version you want to support
./py2to3 version-check src/ -t 3.8 > compat_3.8.txt
./py2to3 version-check src/ -t 3.9 > compat_3.9.txt
./py2to3 version-check src/ -t 3.10 > compat_3.10.txt
```

### 5. Pre-Deployment Verification

Before deploying to a new environment:
```bash
# Target environment runs Python 3.9
./py2to3 version-check src/ -t 3.9

# Exit code 0 = compatible, non-zero = incompatible
if [ $? -eq 0 ]; then
  echo "Ready to deploy!"
else
  echo "Fix compatibility issues first"
fi
```

### 6. Documentation Generation

Generate compatibility docs for your project:
```bash
# Create comprehensive report
./py2to3 version-check src/ -o PYTHON_VERSION_REQUIREMENTS.txt

# Commit to repository for team reference
git add PYTHON_VERSION_REQUIREMENTS.txt
git commit -m "Add Python version requirements documentation"
```

## Best Practices

### 1. Run Early and Often

Check version compatibility:
- ✅ Immediately after migration
- ✅ Before adding new features
- ✅ Before deployment to new environments
- ✅ When updating dependencies

### 2. Target Appropriate Versions

Consider:
- **Modern features**: Python 3.8+ recommended for best experience
- **Long-term support**: Check EOL dates for Python versions
- **Deployment constraints**: Match your target environment
- **Team experience**: Consider team familiarity with versions

### 3. Document Requirements

- Add compatibility report to your repository
- Update `README.md` with version requirements
- Specify version in `setup.py` or `pyproject.toml`
- Include in deployment documentation

### 4. Use in CI/CD

Add to your CI pipeline:
```yaml
# .github/workflows/version-check.yml
name: Version Compatibility Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check version compatibility
        run: |
          ./py2to3 version-check src/ -t 3.8
```

### 5. Monitor Over Time

- Re-run checks after code changes
- Track minimum version requirements over time
- Update target version as needed
- Plan for version upgrades proactively

## Troubleshooting

### Issue: Syntax Errors Reported

**Cause**: Code contains Python 2 syntax or other syntax errors

**Solution**: Run the migration fixer first:
```bash
./py2to3 fix src/
./py2to3 version-check src/
```

### Issue: Higher Version Than Expected

**Cause**: Using modern features unintentionally

**Solution**: Review the detected features and refactor if needed:
```bash
# See what requires higher version
./py2to3 version-check src/ -f json -o report.json
# Review the features section in report.json
```

### Issue: Compatibility Check Fails

**Cause**: Code uses features not available in target version

**Solution**: Either upgrade target version or refactor code:
```bash
# See specific incompatibilities
./py2to3 version-check src/ -t 3.8

# Refactor features to work with target version
# For example, replace walrus operator with regular assignment
```

## Integration with Other Tools

### With Migration Workflow

```bash
# Complete workflow
./py2to3 preflight src/                    # Check readiness
./py2to3 fix src/                          # Apply fixes
./py2to3 check src/                        # Verify compatibility
./py2to3 version-check src/                # Determine version requirements
./py2to3 test-gen src/                     # Generate tests
./py2to3 report                            # Create comprehensive report
```

### With Virtual Environments

```bash
# Create venv with specific version
./py2to3 venv create py38 --python 3.8

# Check if code is compatible
./py2to3 version-check src/ -t 3.8

# Test in the venv
./py2to3 venv run py38 pytest
```

### With Git Integration

```bash
# Check before committing
./py2to3 version-check src/ -o version_requirements.txt
git add version_requirements.txt
git commit -m "Update version requirements"
```

## Exit Codes

The `version-check` command returns:
- **0**: Success (code is compatible with target if specified)
- **1**: Incompatibility found (when using `-t/--target` option)
- **1**: Error during analysis

## Examples

### Example 1: Basic Analysis

```bash
$ ./py2to3 version-check src/utils.py

Files analyzed: 1
Minimum Python version required: 3.6

Version-Specific Features Detected:
  Python 3.6+:
    • f-string literals
      Found 24 occurrence(s)

Compatibility Summary:
  Python 3.6: ✓ Compatible
  Python 3.7: ✓ Compatible
  Python 3.8: ✓ Compatible
  Python 3.9: ✓ Compatible
  Python 3.10: ✓ Compatible
  Python 3.11: ✓ Compatible
  Python 3.12: ✓ Compatible
```

### Example 2: Target Version Check

```bash
$ ./py2to3 version-check src/ -t 3.7

Files analyzed: 15
Minimum Python version required: 3.9

Found 1 incompatibility with Python 3.7:
  • Union type operator (|) for type hints
    Requires: Python 3.9
```

### Example 3: JSON Output

```bash
$ ./py2to3 version-check src/ -f json -o report.json
$ cat report.json | jq '.summary'

{
  "files_analyzed": 15,
  "minimum_version": "3.9",
  "errors_count": 0
}
```

## Summary

The Python Version Compatibility Checker is an essential tool for:
- ✅ Making informed version targeting decisions
- ✅ Ensuring deployment compatibility
- ✅ Documenting version requirements
- ✅ Avoiding runtime issues in production
- ✅ Planning Python version upgrades

Run it after every migration to understand your Python version requirements and make confident deployment decisions!

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Migration Guide](README.md) - Full migration workflow
- [Preflight Checker](README.md#pre-migration-safety-checker) - Pre-migration checks
- [Virtual Environment Manager](VENV_GUIDE.md) - Testing with different Python versions
- [CI/CD Integration](CI_CD_GUIDE.md) - Automated checking
