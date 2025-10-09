# Migration Doctor Guide 🏥

## Overview

The **Migration Doctor** is a comprehensive health check and diagnostics tool for the py2to3 migration toolkit, inspired by similar tools like `brew doctor` and `flutter doctor`. It performs automated checks on your environment and project to identify potential issues before, during, and after migration.

## Why Use Migration Doctor?

- 🔍 **Catch Issues Early**: Identify problems before they become blockers
- 🏥 **Comprehensive Checks**: Verifies environment, project structure, and code quality
- 💡 **Actionable Recommendations**: Get specific steps to fix identified issues
- 🎯 **Migration Readiness**: Verify your environment is ready for migration
- 🔧 **Troubleshooting**: Diagnose problems when things go wrong

## Quick Start

```bash
# Run health checks on current directory
./py2to3 doctor

# Check a specific project
./py2to3 doctor /path/to/project

# Output results in JSON format
./py2to3 doctor --json
```

## What Does It Check?

### Environment Checks

1. **Python Version**
   - Verifies you're running a compatible Python version
   - Recommends upgrading if using old versions
   - Status: OK, WARNING, or ERROR

2. **Python 3 Command**
   - Checks if `python3` command is available
   - Important for scripts that explicitly call `python3`
   - Status: OK or WARNING

3. **Python 2 Command** (Optional)
   - Checks if `python2` is available
   - Only needed for benchmarking features
   - Status: INFO

4. **Git Availability**
   - Verifies Git is installed and accessible
   - Required for version control integration features
   - Status: OK or WARNING

5. **Optional Packages**
   - Checks for pytest, coverage, black, isort, mypy, pylint
   - These enable additional features
   - Status: OK or INFO with installation instructions

### Project Checks

6. **Project Structure**
   - Validates project directory exists
   - Counts Python files in the project
   - Status: OK, WARNING, or ERROR

7. **Configuration Files**
   - Looks for py2to3 config files
   - Also checks for setup.py, pyproject.toml, etc.
   - Status: OK or INFO

8. **Backup Directory**
   - Checks if migration backups exist
   - Shows number of backed up files
   - Status: OK or INFO

9. **Migration State**
   - Looks for migration state tracking data
   - Shows progress if migration is in progress
   - Status: OK or INFO

### Code Quality Checks

10. **Syntax Errors**
    - Scans Python files for syntax errors
    - Critical issues that must be fixed
    - Status: OK or ERROR

11. **Python 2 Patterns**
    - Detects common Python 2 code patterns
    - Examples: print statements, xrange, iteritems
    - Status: OK or WARNING

12. **Python 2 Imports**
    - Finds Python 2-specific imports
    - Examples: urllib2, ConfigParser, Queue
    - Status: OK or ERROR

### Integration Checks

13. **Git Status**
    - Checks for uncommitted changes
    - Recommends committing before migration
    - Status: OK or WARNING

14. **Dependency Files**
    - Looks for requirements.txt, Pipfile, etc.
    - Helps ensure dependencies are documented
    - Status: OK or INFO

## Understanding Results

### Status Levels

- ✓ **OK** (Green): Everything is working correctly
- ⚠ **WARNING** (Yellow): Issue found but not critical, should be addressed
- ✗ **ERROR** (Red): Critical issue that must be fixed before migration
- ℹ **INFO** (Blue): Informational message, no action required

### Overall Assessment

At the end of the report, you'll see one of three overall statuses:

- ✅ **All systems go!** - Your environment is ready for migration
- ⚠️ **Ready with warnings** - You can proceed but should address warnings
- ❌ **Action required** - Critical errors must be fixed before migration

## Example Output

```
🏥 Running Migration Doctor...

======================================================================
                       MIGRATION DOCTOR REPORT
======================================================================

✓ Python Version
  Python 3.12.11 is installed and compatible

✓ Python 3 Command
  python3 command available: Python 3.12.11

ℹ Python 2 Command
  python2 command not found (optional)
     • Python 2 is optional, only needed for benchmarking features

✓ Git
  Git is available: git version 2.51.0

⚠ Python 2 Patterns
  Found Python 2 patterns: 18x old-style string format, 10x xrange
  💡 Recommendation: Run 'py2to3 fix' to automatically convert these patterns
     • old-style string format
     • xrange

======================================================================
                               SUMMARY
======================================================================

  ✓ 7 checks passed
  ⚠ 2 warnings
  ✗ 0 errors
  ℹ 4 informational

⚠️  Ready with warnings: Address 2 warning(s) if possible
```

## JSON Output

For programmatic use or integration with other tools, use the `--json` flag:

```bash
./py2to3 doctor --json > health-report.json
```

Example JSON output:

```json
{
  "checks": [
    {
      "name": "Python Version",
      "status": "OK",
      "message": "Python 3.12.11 is installed and compatible",
      "recommendation": null,
      "details": []
    },
    {
      "name": "Python 2 Patterns",
      "status": "WARNING",
      "message": "Found Python 2 patterns: 18x old-style string format",
      "recommendation": "Run 'py2to3 fix' to automatically convert these patterns",
      "details": ["old-style string format", "xrange", "iteritems"]
    }
  ]
}
```

## Common Issues and Solutions

### Issue: Python version too old

**Symptom**: 
```
⚠ Python Version
  Python 3.5.2 is old, consider upgrading
```

**Solution**: Upgrade to Python 3.6 or newer:
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.9

# On macOS
brew install python@3.9

# On Windows
# Download from python.org
```

### Issue: Git not available

**Symptom**:
```
⚠ Git
  Git not found in PATH
```

**Solution**: Install Git:
```bash
# On Ubuntu/Debian
sudo apt-get install git

# On macOS
brew install git

# On Windows
# Download from git-scm.com
```

### Issue: Python 2 imports found

**Symptom**:
```
✗ Python 2 Imports
  Found Python 2 imports: urllib2 (11x), ConfigParser (9x)
```

**Solution**: Run the automatic fixer:
```bash
./py2to3 fix . --backup-dir backup
```

### Issue: Uncommitted changes

**Symptom**:
```
⚠ Git Status
  You have 15 uncommitted changes
```

**Solution**: Commit your changes:
```bash
git add .
git commit -m "Pre-migration checkpoint"
```

### Issue: Missing optional packages

**Symptom**:
```
ℹ Optional Packages
  Some optional packages are missing: pytest, black, mypy
```

**Solution**: Install the packages:
```bash
pip install pytest black mypy
# Or install all at once
pip install -r requirements-dev.txt
```

## Integration with CI/CD

You can integrate migration doctor into your CI/CD pipeline:

```yaml
# .github/workflows/migration-check.yml
name: Migration Health Check

on: [push, pull_request]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Run Migration Doctor
        run: |
          ./py2to3 doctor --json > health-report.json
          cat health-report.json
      - name: Upload health report
        uses: actions/upload-artifact@v2
        with:
          name: health-report
          path: health-report.json
```

## When to Run Migration Doctor

### Before Migration
- ✅ Verify environment is properly set up
- ✅ Check for existing issues in code
- ✅ Ensure all tools are available

### During Migration
- ✅ Troubleshoot unexpected issues
- ✅ Verify fixes are working correctly
- ✅ Monitor progress and health

### After Migration
- ✅ Confirm no Python 2 patterns remain
- ✅ Verify all imports are updated
- ✅ Check project is in good state

### Regular Checks
- ✅ Include in pre-commit hooks
- ✅ Run in CI/CD pipeline
- ✅ Periodic health audits

## Best Practices

1. **Run Before Starting**: Always run doctor before beginning migration
2. **Fix Critical Issues First**: Address all ERROR status items before proceeding
3. **Address Warnings**: Try to resolve WARNING items for smoother migration
4. **Document Results**: Save JSON output for record-keeping
5. **Integrate with Workflow**: Make doctor checks part of your regular workflow
6. **Share with Team**: Use doctor output to communicate status to team members

## Command Reference

```bash
# Basic usage
./py2to3 doctor [path]

# Options
./py2to3 doctor                    # Check current directory
./py2to3 doctor /path/to/project   # Check specific project
./py2to3 doctor --json             # Output in JSON format
./py2to3 doctor --help             # Show help message
```

## Exit Codes

The doctor command uses exit codes to indicate overall health:

- **0**: No errors found (OK or WARNING status only)
- **1**: Critical errors found (one or more ERROR status items)

This makes it easy to use in scripts:

```bash
if ./py2to3 doctor; then
    echo "Environment is healthy, proceeding with migration..."
    ./py2to3 fix .
else
    echo "Environment has critical issues, aborting migration"
    exit 1
fi
```

## Related Commands

- `./py2to3 preflight` - Pre-migration safety checks
- `./py2to3 health` - Monitor ongoing migration health metrics
- `./py2to3 status` - Quick migration status summary
- `./py2to3 check` - Check Python 3 compatibility

## Comparison with Other Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `doctor` | Environment and project diagnostics | Before starting, troubleshooting |
| `preflight` | Pre-migration safety verification | Right before running fixes |
| `health` | Migration health metrics and trends | During active migration |
| `status` | Quick progress overview | Checking migration progress |
| `check` | Python 3 compatibility analysis | Detailed code analysis |

## Troubleshooting

### Doctor command fails to run

Check that you're in the correct directory and the script is executable:

```bash
chmod +x py2to3
./py2to3 doctor
```

### Too many false positives

The doctor scans files to detect patterns. For large projects, it limits scans to the first 50 files for performance. If you want more comprehensive checks, use the dedicated analysis commands:

```bash
./py2to3 check .     # Comprehensive compatibility check
./py2to3 search .    # Search for specific patterns
```

### Different results on different machines

Environment checks will naturally vary between machines. Focus on ensuring:
- Python 3.6+ is installed
- Git is available (if using version control features)
- Project structure is consistent

## Contributing

Have ideas for additional health checks? We'd love to hear them!

1. Check if the check would benefit most users
2. Ensure it provides actionable recommendations
3. Keep performance in mind (avoid slow operations)
4. Add documentation for the new check

## Summary

Migration Doctor is your first line of defense against migration issues. Run it early and often to ensure smooth sailing throughout your Python 2 to 3 migration journey. It's designed to catch problems before they become blockers and provide clear guidance on how to resolve them.

**Pro Tip**: Make `./py2to3 doctor` part of your daily workflow, just like `git status`!
