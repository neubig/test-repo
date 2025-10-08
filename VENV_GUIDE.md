# Virtual Environment Manager Guide

The Virtual Environment Manager provides an integrated solution for creating, managing, and testing Python 3 virtual environments during your migration workflow. It bridges the gap between migrating code and actually testing it in isolated Python 3 environments.

## Overview

Virtual environments are essential for:
- **Isolated Testing**: Test migrated code in a clean Python 3 environment
- **Dependency Management**: Install and manage Python 3 compatible packages
- **Version Testing**: Test against different Python 3 versions (3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12)
- **Safe Experimentation**: Try changes without affecting your system Python
- **Team Consistency**: Ensure everyone tests with the same environment

## Quick Start

```bash
# Create a new Python 3 virtual environment
./py2to3 venv create py3-test

# Activate it (follow the instructions shown)
source .py2to3_venvs/py3-test/bin/activate  # Linux/Mac
# or
.py2to3_venvs\py3-test\Scripts\activate.bat  # Windows

# Install your dependencies
./py2to3 venv install py3-test -r requirements.txt

# Run your tests
./py2to3 venv test py3-test

# When done, list all environments
./py2to3 venv list
```

## Commands

### Create a Virtual Environment

Create a new Python 3 virtual environment for testing:

```bash
# Create with default Python 3
./py2to3 venv create my-env

# Create with specific Python version
./py2to3 venv create py38-env --python 3.8
./py2to3 venv create py39-env --python 3.9
./py2to3 venv create py310-env --python 3.10

# Create with access to system packages
./py2to3 venv create sys-env --system-site-packages
```

**Options:**
- `name`: Name for your virtual environment (required)
- `--python VERSION`: Specific Python version (e.g., 3.8, 3.9, 3.10)
- `--system-site-packages`: Allow access to system-wide packages

After creation, you'll see instructions for activating the environment.

### List Virtual Environments

See all managed virtual environments:

```bash
./py2to3 venv list
```

Shows:
- Environment name and status (exists or not)
- File system path
- Python version
- Number of installed packages

### Install Packages

Install packages into a virtual environment:

```bash
# Install from requirements.txt
./py2to3 venv install my-env -r requirements.txt

# Install a single package
./py2to3 venv install my-env -p pytest

# Install with version specification
./py2to3 venv install my-env -p "numpy>=1.19.0"
```

**Options:**
- `-r, --requirements FILE`: Install from requirements file
- `-p, --package PACKAGE`: Install a single package

### Run Commands

Execute Python commands in a virtual environment:

```bash
# Run a Python script
./py2to3 venv run my-env my_script.py

# Run a Python module
./py2to3 venv run my-env -m pytest

# Run with arguments
./py2to3 venv run my-env my_script.py --arg1 value1
```

### Run Tests

Run pytest tests in a virtual environment:

```bash
# Run tests in default location (tests/)
./py2to3 venv test my-env

# Run tests in specific path
./py2to3 venv test my-env --test-path src/tests

# Run specific test file
./py2to3 venv test my-env --test-path tests/test_mymodule.py
```

If pytest is not installed in the environment, it will be installed automatically.

### Get Environment Info

View detailed information about a virtual environment:

```bash
./py2to3 venv info my-env
```

Shows:
- Full path to environment
- Existence status
- Creation timestamp
- Python version
- System site-packages setting
- List of installed packages (top 20)

### Show Activation Command

Display the command to activate a virtual environment:

```bash
./py2to3 venv activate my-env
```

This shows the platform-specific activation command:
- Linux/Mac: `source .py2to3_venvs/my-env/bin/activate`
- Windows: `.py2to3_venvs\my-env\Scripts\activate.bat`

### Remove Virtual Environment

Delete a virtual environment:

```bash
# Remove with confirmation prompt
./py2to3 venv remove my-env

# Force removal without confirmation
./py2to3 venv remove my-env --force
```

**Options:**
- `--force`: Skip confirmation prompt

## Typical Workflow

### 1. Pre-Migration Setup

Before migrating, create a Python 3 environment to understand your target:

```bash
# Create Python 3 environment
./py2to3 venv create py3-target --python 3.9

# Try installing your current dependencies
./py2to3 venv install py3-target -r requirements.txt

# This may reveal incompatible packages
```

### 2. During Migration

Test your changes as you migrate:

```bash
# Apply some fixes
./py2to3 fix src/mymodule.py

# Test in Python 3 environment
./py2to3 venv test py3-test --test-path tests/test_mymodule.py

# Run specific script to verify
./py2to3 venv run py3-test src/mymodule.py
```

### 3. Post-Migration Validation

After migration, validate across multiple Python versions:

```bash
# Create environments for different versions
./py2to3 venv create py36 --python 3.6
./py2to3 venv create py38 --python 3.8
./py2to3 venv create py310 --python 3.10

# Install dependencies in each
for env in py36 py38 py310; do
    ./py2to3 venv install $env -r requirements.txt
    ./py2to3 venv test $env
done
```

### 4. CI/CD Integration

Use virtual environments in your CI pipeline:

```bash
# In CI script
./py2to3 venv create ci-test --python 3.9
./py2to3 venv install ci-test -r requirements.txt
./py2to3 venv run ci-test -m pytest --cov=src --cov-report=xml
```

## Integration with Other Tools

### With Dependency Analyzer

Analyze dependencies, then test in Python 3:

```bash
# Check dependency compatibility
./py2to3 deps analyze requirements.txt

# Create environment and test
./py2to3 venv create dep-test
./py2to3 venv install dep-test -r requirements.txt
```

### With Migration Workflow

Integrate into complete migration:

```bash
# 1. Check current state
./py2to3 check src/

# 2. Create test environment
./py2to3 venv create migration-test

# 3. Apply fixes
./py2to3 fix src/ -y

# 4. Install dependencies
./py2to3 venv install migration-test -r requirements.txt

# 5. Run tests
./py2to3 venv test migration-test

# 6. Generate report
./py2to3 report -o migration_report.html
```

### With Git Integration

Create checkpoints with environment snapshots:

```bash
# Create checkpoint before testing
./py2to3 git checkpoint "Pre-test baseline"

# Test in environment
./py2to3 venv test my-env

# Commit if tests pass
if [ $? -eq 0 ]; then
    ./py2to3 git commit "tested" -m "Tests passing in Python 3"
fi
```

## Advanced Usage

### Testing Multiple Python Versions

Create a script to test against all available Python versions:

```bash
#!/bin/bash
# test-all-versions.sh

VERSIONS="3.6 3.7 3.8 3.9 3.10 3.11 3.12"

for version in $VERSIONS; do
    echo "Testing Python $version..."
    env_name="py${version/./}"
    
    # Create environment if it doesn't exist
    ./py2to3 venv list | grep -q "$env_name" || \
        ./py2to3 venv create "$env_name" --python "$version"
    
    # Install and test
    ./py2to3 venv install "$env_name" -r requirements.txt
    
    if ./py2to3 venv test "$env_name"; then
        echo "✓ Python $version: PASSED"
    else
        echo "✗ Python $version: FAILED"
    fi
done
```

### Comparing Python 2 and Python 3 Behavior

```bash
# Run same script in Python 2 (system) and Python 3 (venv)
python2 my_script.py > output_py2.txt
./py2to3 venv run py3-env my_script.py > output_py3.txt

# Compare outputs
diff output_py2.txt output_py3.txt
```

### Environment Templates

Create template requirements for quick setup:

```bash
# requirements-py3-minimal.txt
pytest>=6.0
black>=22.0
flake8>=4.0

# Create and setup new environment
./py2to3 venv create new-env
./py2to3 venv install new-env -r requirements-py3-minimal.txt
```

## Storage and State

Virtual environments are stored in `.py2to3_venvs/` directory by default. The manager keeps track of:

- Environment metadata in `.py2to3_venvs/venvs.json`
- Python version used
- Creation timestamp
- Installed packages (updated after each install)
- System site-packages setting

This state file allows the manager to:
- Track environments even if directories are moved
- Show environment information without activating
- Provide quick status checks

## Troubleshooting

### Python Version Not Found

**Problem**: `Error: Python 3.9 not found`

**Solution**: 
- Install the desired Python version on your system
- Use `python3 --version` to see your default Python 3
- Create environment without `--python` flag to use default

### Import Errors After Migration

**Problem**: Migrated code imports fail in Python 3 environment

**Solution**:
```bash
# Check what's installed
./py2to3 venv info my-env

# Install missing packages
./py2to3 venv install my-env -p <missing-package>

# Or reinstall all dependencies
./py2to3 venv install my-env -r requirements.txt
```

### Permission Errors

**Problem**: Cannot create virtual environment

**Solution**:
- Ensure you have write permission in the current directory
- Check disk space
- Try creating in a different location (modify base directory)

### Environment Not Activating

**Problem**: Activation command not working

**Solution**:
```bash
# Get the activation command again
./py2to3 venv activate my-env

# Make sure you're using 'source' on Linux/Mac
source .py2to3_venvs/my-env/bin/activate

# On Windows, don't use 'source'
.py2to3_venvs\my-env\Scripts\activate.bat
```

## Best Practices

1. **One environment per Python version**: Create separate environments for testing compatibility
   ```bash
   ./py2to3 venv create py38-test --python 3.8
   ./py2to3 venv create py39-test --python 3.9
   ```

2. **Keep requirements.txt updated**: Always test with your actual dependencies
   ```bash
   # After migrating, update requirements
   ./py2to3 deps analyze requirements.txt > requirements-py3.txt
   ./py2to3 venv install test-env -r requirements-py3.txt
   ```

3. **Clean up old environments**: Remove environments you no longer need
   ```bash
   ./py2to3 venv list
   ./py2to3 venv remove old-env --force
   ```

4. **Document your test environments**: Keep notes on which environments are for what
   ```bash
   # Add to your project README:
   # - py3-test: Main testing environment (Python 3.9)
   # - py3-minimal: Minimal deps for CI (Python 3.8)
   # - py3-latest: Latest Python for compatibility testing (Python 3.12)
   ```

5. **Integrate with CI/CD**: Use virtual environments in your automated tests
   ```yaml
   # .github/workflows/test.yml
   - name: Test Python 3 compatibility
     run: |
       ./py2to3 venv create ci-test --python 3.9
       ./py2to3 venv install ci-test -r requirements.txt
       ./py2to3 venv test ci-test
   ```

## Examples

### Complete Migration Workflow with Virtual Environments

```bash
#!/bin/bash
# Complete migration with virtual environment testing

echo "=== Python 2 to 3 Migration with Testing ==="

# 1. Pre-flight checks
echo "1. Running pre-flight checks..."
./py2to3 preflight .

# 2. Create backup
echo "2. Creating backup..."
./py2to3 backup create pre-migration

# 3. Analyze current state
echo "3. Analyzing current state..."
./py2to3 check src/ -r pre-migration-report.txt

# 4. Create Python 3 test environment
echo "4. Creating Python 3 test environment..."
./py2to3 venv create py3-migration --python 3.9

# 5. Try installing current dependencies in Python 3
echo "5. Testing dependency compatibility..."
./py2to3 venv install py3-migration -r requirements.txt

# 6. Apply automated fixes
echo "6. Applying automated fixes..."
./py2to3 fix src/ -y

# 7. Install dependencies in test environment
echo "7. Installing dependencies..."
./py2to3 venv install py3-migration -r requirements.txt

# 8. Run tests in Python 3 environment
echo "8. Running tests in Python 3..."
if ./py2to3 venv test py3-migration; then
    echo "✓ Tests passed!"
else
    echo "✗ Tests failed - manual fixes needed"
    exit 1
fi

# 9. Generate report
echo "9. Generating migration report..."
./py2to3 report -o migration_report.html

# 10. Create git checkpoint
echo "10. Creating git checkpoint..."
./py2to3 git checkpoint "Migration completed with passing tests"

echo "=== Migration Complete! ==="
echo "View report: migration_report.html"
echo "Activate environment: source .py2to3_venvs/py3-migration/bin/activate"
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI command reference
- [Dependency Guide](DEPENDENCY_GUIDE.md) - Analyzing Python 3 dependency compatibility
- [Migration Workflow](README.md#usage) - Complete migration workflow documentation
- [Testing Guide](tests/README.md) - Writing and running tests
