# Runtime Validation Guide

## Overview

The **Runtime Validator** is a powerful tool that performs runtime validation of your Python 3 migrated code by attempting to import all modules and checking for runtime errors. This complements static analysis (like the `check` command) by verifying that your code actually works at runtime.

## Why Runtime Validation?

After migrating Python 2 code to Python 3, static analysis tools can identify patterns and syntax issues, but they can't tell you if the code actually runs. The runtime validator bridges this gap by:

- **Actually importing modules** - Verifies imports work and dependencies are satisfied
- **Catching runtime errors** - Identifies issues that only appear when code executes
- **Providing quick feedback** - Gives immediate validation without running full test suites
- **CI/CD integration** - Can be used as a smoke test in continuous integration

## Key Features

- ✅ **Import Validation** - Attempts to import all Python modules in your project
- 🔍 **Syntax Checking** - Detects Python 2 syntax that wasn't caught by static analysis
- 📊 **Detailed Reporting** - Shows which modules succeed, fail, or have warnings
- 🎯 **Success Rate Calculation** - Provides an overall validation score
- 📁 **Multiple Formats** - Supports text and JSON output for automation
- 🚀 **Fast Execution** - Quick smoke test before running full test suites

## Basic Usage

### Validate a Single File

```bash
./py2to3 validate src/my_module.py
```

### Validate an Entire Directory

```bash
./py2to3 validate src/
```

### Save Report to File

```bash
./py2to3 validate src/ -o validation_report.txt
```

### JSON Output for CI/CD

```bash
./py2to3 validate src/ --format json -o validation.json
```

### Verbose Mode (Show Detailed Tracebacks)

```bash
./py2to3 validate src/ -v
```

## Understanding the Results

The validator categorizes files into four groups:

### ✓ Successfully Validated

Files that can be imported without any issues. These modules are ready to use!

```
✓ src/utils.py
✓ src/helpers.py
✓ src/config.py
```

### ⚠ Validated with Warnings

Files that import successfully but have potential issues (e.g., deprecated patterns):

```
⚠ src/legacy_code.py
   - Contains Python 2 type 'basestring' - may cause issues
```

### ✗ Validation Failed

Files that cannot be imported due to errors:

```
✗ src/old_module.py
   Error: Import error: No module named 'urllib2'
```

Common failure reasons:
- Syntax errors (Python 2 code not yet migrated)
- Missing dependencies (Python 2 modules not available in Python 3)
- Import errors (incorrect module paths)
- Runtime errors (code that raises exceptions during import)

### ○ Skipped

Test files are automatically skipped since they often require test framework setup:

```
○ src/test_module.py
   Reason: Test file (requires test framework setup)
```

## Example Workflows

### Quick Validation After Fixes

After running the fixer, validate that your changes work:

```bash
# Apply fixes
./py2to3 fix src/

# Validate the results
./py2to3 validate src/
```

### Pre-Commit Validation

Ensure code can be imported before committing:

```bash
# Validate before committing
./py2to3 validate src/
if [ $? -eq 0 ]; then
    git commit -a -m "Migration changes"
else
    echo "Validation failed! Fix errors before committing."
fi
```

### CI/CD Pipeline Integration

Use in your CI/CD pipeline as a smoke test:

```bash
# In your CI script
./py2to3 validate src/ --format json -o validation.json

# Check exit code (0 = success, 1 = failures)
if [ $? -ne 0 ]; then
    echo "Runtime validation failed!"
    exit 1
fi
```

### Progressive Migration Tracking

Track validation success rate over time:

```bash
# Week 1
./py2to3 validate src/ | grep "Success Rate"
# Success Rate: 45.2%

# Week 2 (after more fixes)
./py2to3 validate src/ | grep "Success Rate"
# Success Rate: 78.9%

# Week 3 (nearly complete)
./py2to3 validate src/ | grep "Success Rate"
# Success Rate: 95.1%
```

## Integration with Other Commands

The validate command works great with other py2to3 tools:

### Complete Validation Workflow

```bash
# 1. Static analysis
./py2to3 check src/

# 2. Apply fixes
./py2to3 fix src/

# 3. Runtime validation
./py2to3 validate src/

# 4. Run tests (if they pass validation)
pytest

# 5. Generate report
./py2to3 report
```

### Find What Needs Attention

Use validation to identify which modules need manual review:

```bash
# Validate and save report
./py2to3 validate src/ -o validation.txt

# Review failed modules
grep "^  ✗" validation.txt
```

## Exit Codes

The validate command uses exit codes for automation:

- **0** - All modules validated successfully
- **1** - One or more modules failed validation

Use in scripts:

```bash
if ./py2to3 validate src/ --format json > /dev/null 2>&1; then
    echo "✓ All modules valid!"
else
    echo "✗ Validation errors found"
fi
```

## JSON Output Format

When using `--format json`, the output includes:

```json
{
  "success": [
    {"file": "src/module1.py"}
  ],
  "failed": [
    {
      "file": "src/module2.py",
      "error": "Import error: No module named 'urllib2'"
    }
  ],
  "skipped": [
    {
      "file": "src/test_module.py",
      "reason": "Test file (requires test framework setup)"
    }
  ],
  "warnings": [
    {
      "file": "src/module3.py",
      "warnings": ["Contains Python 2 type 'basestring'"]
    }
  ],
  "summary": {
    "total_files": 10,
    "validated": 9,
    "success": 7,
    "warnings": 1,
    "failed": 1,
    "skipped": 1,
    "success_rate": 88.89,
    "status": "FAILED"
  }
}
```

## Troubleshooting

### "No module named X"

If you see import errors for standard library modules:
- Check if the module was renamed in Python 3 (e.g., `urllib2` → `urllib.request`)
- Run `./py2to3 fix` to update imports automatically

### Syntax Errors

If syntax errors appear:
- These are Python 2 patterns that weren't migrated yet
- Run `./py2to3 check` to identify all syntax issues
- Run `./py2to3 fix` to automatically fix them

### Missing Dependencies

If validation fails due to missing packages:
- Check `requirements.txt` for Python 3 compatible versions
- Install dependencies: `pip install -r requirements.txt`
- Use `./py2to3 deps` to analyze dependency compatibility

## Best Practices

1. **Run after every fix session** - Validate immediately after applying fixes
2. **Use in CI/CD pipelines** - Add as a smoke test before running full tests
3. **Track success rate over time** - Monitor progress towards 100% validation
4. **Combine with static analysis** - Use both `check` and `validate` for comprehensive coverage
5. **Fix failures progressively** - Address high-priority failures first
6. **Use verbose mode for debugging** - Add `-v` when investigating specific failures

## Limitations

The runtime validator has some limitations:

- **Test files are skipped** - Test files often need special setup
- **Side effects may occur** - Importing modules may have side effects
- **Doesn't run all code** - Only imports modules, doesn't execute all code paths
- **Requires dependencies** - All dependencies must be installed

For comprehensive testing, use the validator as a quick smoke test, then run your full test suite.

## Comparison with Other Commands

| Feature | `check` (Static) | `validate` (Runtime) | `test-gen` (Testing) |
|---------|------------------|----------------------|---------------------|
| Speed | ⚡ Very Fast | ⚡ Fast | 🐢 Slower |
| Coverage | Syntax & Patterns | Import Validation | Full Code Paths |
| Dependencies | None | Must be installed | Must be installed |
| Side Effects | None | Possible | Expected |
| Best For | Initial analysis | Smoke testing | Comprehensive testing |

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI documentation
- [Check Command](README.md#check-command) - Static compatibility analysis
- [Test Generation](TEST_GEN_GUIDE.md) - Generate unit tests
- [CI/CD Integration](CI_CD_GUIDE.md) - Automation workflows
