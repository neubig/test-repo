# Test Generation Guide

## Overview

The Test Generator is an automated tool that creates unit tests for your Python code after migration from Python 2 to Python 3. This feature helps ensure that the migration preserves functionality and catches runtime issues that syntax checking alone cannot detect.

## Why Generate Tests?

When migrating from Python 2 to Python 3, the toolkit can:
- ✅ Fix syntax issues (print statements, imports, etc.)
- ✅ Verify Python 3 compatibility
- ✅ Generate detailed reports

But it **cannot** verify that:
- ❌ The migrated code behaves the same as the original
- ❌ No runtime errors were introduced
- ❌ Edge cases still work correctly

**Test Generation bridges this gap** by creating unit tests that help verify runtime behavior.

## Features

- 🔍 **AST Analysis**: Analyzes Python code structure to identify testable functions and classes
- 🧪 **Pytest-Style Tests**: Generates tests using pytest framework conventions
- 📝 **Smart Scaffolding**: Creates test stubs with TODOs for easy customization
- 🎯 **Selective Generation**: Skips private functions and focuses on public APIs
- 📊 **Detailed Summary**: Shows what was tested and what was skipped
- 🔄 **Overwrite Protection**: Prevents accidentally overwriting existing tests

## Quick Start

### Generate Tests for a Single File

```bash
./py2to3 test-gen src/fixer.py
```

This will:
1. Analyze `src/fixer.py`
2. Extract testable functions and classes
3. Generate `generated_tests/test_fixer.py`

### Generate Tests for an Entire Directory

```bash
./py2to3 test-gen src/ -o my_tests
```

This will:
1. Recursively scan all Python files in `src/`
2. Generate tests for each file
3. Save tests in `my_tests/` directory

### Overwrite Existing Tests

```bash
./py2to3 test-gen src/ --overwrite
```

Use this to regenerate tests if you've modified the source code.

## Command-Line Options

```
usage: py2to3 test-gen [-h] [-o OUTPUT] [--overwrite] path

positional arguments:
  path                  File or directory to generate tests for

options:
  -h, --help            Show help message
  -o OUTPUT, --output OUTPUT
                        Output directory for generated tests (default: generated_tests)
  --overwrite           Overwrite existing test files
```

## Usage Examples

### Example 1: Generate Tests After Migration

```bash
# Step 1: Run the migration
./py2to3 fix src/

# Step 2: Generate tests to verify the migration
./py2to3 test-gen src/ -o tests_migration

# Step 3: Review and enhance the generated tests
# Edit files in tests_migration/ to add specific assertions

# Step 4: Run the tests
pytest tests_migration/
```

### Example 2: Test-Driven Migration

```bash
# Step 1: Generate tests for the original Python 2 code
./py2to3 test-gen src/ -o tests_baseline

# Step 2: Enhance the tests with proper assertions
# Edit tests to verify expected behavior

# Step 3: Run tests on Python 2 code (should fail or pass)
python2 -m pytest tests_baseline/ || true

# Step 4: Migrate to Python 3
./py2to3 fix src/

# Step 5: Run the same tests on Python 3 code
pytest tests_baseline/

# Step 6: Fix any failing tests
```

### Example 3: Generate Tests for Specific Modules

```bash
# Generate tests only for critical modules
./py2to3 test-gen src/core/ -o tests_core
./py2to3 test-gen src/data/ -o tests_data
./py2to3 test-gen src/web/ -o tests_web
```

## Generated Test Structure

The test generator creates well-structured test files:

```python
"""
Generated tests for module.py

These tests were automatically generated to help verify
that Python 2 to 3 migration preserved functionality.
Please review and enhance these tests as needed.
"""

import pytest
import sys
from pathlib import Path

# Add source directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import module

# ===== Function Tests =====

def test_my_function():
    """Test module.my_function function."""
    # Function docstring:
    # Description from original function
    
    # TODO: Add appropriate test inputs
    result = module.my_function(param=None)  # TODO: Provide appropriate value
    assert result is not None  # TODO: Add specific assertion
    
    # TODO: Add more test cases:
    #   - Edge cases (empty input, None values, etc.)
    #   - Boundary conditions
    #   - Error cases

# ===== Class Tests =====

class TestMyClass:
    """Test module.MyClass class."""
    
    def test_instantiation(self):
        """Test MyClass can be instantiated."""
        obj = module.MyClass()
        assert isinstance(obj, module.MyClass)
    
    def test_method(self):
        """Test MyClass.method method."""
        obj = module.MyClass()
        # TODO: Add method test
        pytest.skip("TODO: Implement test")
```

## What Gets Tested

### ✅ Included

- Public functions (not starting with `_`)
- Public classes (not starting with `_`)
- Public methods of classes
- Functions with docstrings (docstring is included in test)

### ❌ Excluded

- Private functions (starting with `_`)
- Private classes (starting with `_`)
- Test files themselves (files starting with `test_`)
- Files in `test/` or `tests/` directories
- Magic methods except `__init__`

## Customizing Generated Tests

The generated tests are **scaffolds** that need customization:

### 1. Add Appropriate Test Inputs

```python
# Generated (needs work):
result = module.process_data(data=None)  # TODO: Provide appropriate value

# After customization:
result = module.process_data(data={'key': 'value'})
```

### 2. Add Specific Assertions

```python
# Generated (too generic):
assert result is not None  # TODO: Add specific assertion

# After customization:
assert result['status'] == 'success'
assert len(result['items']) == 5
assert result['timestamp'] > 0
```

### 3. Add Edge Cases

```python
def test_process_data_empty_input():
    """Test with empty input."""
    result = module.process_data(data={})
    assert result['status'] == 'success'
    assert result['items'] == []

def test_process_data_none_input():
    """Test with None input."""
    with pytest.raises(ValueError):
        module.process_data(data=None)

def test_process_data_large_input():
    """Test with large dataset."""
    large_data = {'items': list(range(10000))}
    result = module.process_data(data=large_data)
    assert result['status'] == 'success'
```

### 4. Add Error Cases

```python
def test_process_data_invalid_type():
    """Test with invalid data type."""
    with pytest.raises(TypeError):
        module.process_data(data="invalid")

def test_process_data_missing_key():
    """Test with missing required key."""
    with pytest.raises(KeyError):
        module.process_data(data={'wrong_key': 'value'})
```

## Best Practices

### 1. Generate Tests Early
Generate tests immediately after migration to catch issues quickly.

### 2. Review All Generated Tests
Don't skip the TODO items - they indicate where customization is needed.

### 3. Run Tests Incrementally
```bash
# Run one test file at a time
pytest generated_tests/test_fixer.py -v

# Run all tests
pytest generated_tests/ -v
```

### 4. Use with Coverage
```bash
pytest generated_tests/ --cov=src --cov-report=html
```

### 5. Integrate with CI/CD
Add the generated tests to your CI/CD pipeline:
```yaml
- name: Run generated tests
  run: pytest generated_tests/ --junitxml=test-results.xml
```

### 6. Version Control
Commit generated tests to version control after customization:
```bash
git add generated_tests/
git commit -m "Add generated tests for migration verification"
```

## Integration with Migration Workflow

### Recommended Workflow

```bash
# 1. Pre-flight checks
./py2to3 preflight src/

# 2. Analyze dependencies
./py2to3 deps src/

# 3. Create backup
./py2to3 fix src/ --dry-run

# 4. Apply fixes
./py2to3 fix src/

# 5. Generate tests  ⭐ NEW!
./py2to3 test-gen src/ -o migration_tests

# 6. Customize tests
# Edit migration_tests/ files

# 7. Run tests
pytest migration_tests/

# 8. Generate report
./py2to3 report --scan-path src/ --output report.html

# 9. Create git checkpoint
./py2to3 git checkpoint "Migration with tests"
```

## Troubleshooting

### No Tests Generated

**Problem**: `No tests were generated`

**Solutions**:
- Check that the target path contains Python files
- Verify files have public functions or classes
- Use `--verbose` to see why files were skipped

### Syntax Errors in Generated Tests

**Problem**: Generated tests have syntax errors

**Solution**: The source file likely has syntax errors. Fix them first:
```bash
./py2to3 check src/problematic_file.py
./py2to3 fix src/problematic_file.py
./py2to3 test-gen src/problematic_file.py
```

### Import Errors When Running Tests

**Problem**: `ModuleNotFoundError` when running tests

**Solutions**:
1. Ensure source directory structure is correct
2. Check that `__init__.py` files exist
3. Adjust the sys.path in generated tests if needed

### Tests Skip Everything

**Problem**: All generated tests are skipped with pytest.skip

**Solution**: This is expected for method tests. Customize them:
```python
# Generated:
pytest.skip("TODO: Implement test")

# Customized:
obj.method()
assert obj.state == expected_state
```

## Advanced Usage

### Programmatic Usage

You can use the test generator programmatically:

```python
from test_generator import TestGenerator

# Create generator
generator = TestGenerator('src/', 'my_tests')

# Generate tests
summary = generator.generate_tests(overwrite=False)

# Access results
print(f"Generated {summary['tests_generated']} tests")
print(f"Files processed: {summary['files_processed']}")
```

### Custom Test Templates

To customize the generated test templates, modify `src/test_generator.py`:
- Edit `_create_test_content()` for file-level changes
- Edit `_generate_function_test()` for function test templates
- Edit `_generate_class_test()` for class test templates

## Examples

See `demo_generated_tests/` for example output of the test generator.

## Integration with Other Tools

### With pytest-cov
```bash
pytest generated_tests/ --cov=src --cov-report=html --cov-report=term
```

### With pytest-xdist (parallel execution)
```bash
pytest generated_tests/ -n auto
```

### With pytest-timeout
```bash
pytest generated_tests/ --timeout=10
```

### With tox (multiple Python versions)
```toml
# tox.ini
[testenv]
deps = pytest
commands = pytest generated_tests/
```

## FAQ

**Q: Can I regenerate tests after modifying source code?**  
A: Yes, use `--overwrite` flag to regenerate tests.

**Q: Will the generator test my existing test files?**  
A: No, it automatically skips files starting with `test_` and directories named `test/` or `tests/`.

**Q: Can I customize the test template?**  
A: Yes, edit `src/test_generator.py` to modify the templates.

**Q: Does it work with Python 2 code?**  
A: The generator itself requires Python 3, but you can generate tests for any Python code.

**Q: What if my functions have complex signatures?**  
A: The generator creates placeholders for arguments. You'll need to provide appropriate values.

**Q: Can I use it with other testing frameworks?**  
A: The generator creates pytest-style tests, but you can modify the templates for unittest or nose.

## Contributing

To improve the test generator:
1. Add support for more test patterns
2. Improve argument type inference
3. Add support for fixtures and mocks
4. Create better test templates for common patterns

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI documentation
- [Testing Guide](tests/README.md) - Guide for the project's test suite
- [Migration Guide](README.md) - Main project documentation
- [CI/CD Guide](CI_CD_GUIDE.md) - Continuous integration setup
