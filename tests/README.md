# Test Suite for py2to3 Toolkit

This directory contains comprehensive unit and integration tests for the Python 2 to 3 migration toolkit.

## Overview

The test suite ensures the reliability and correctness of the migration tools by testing:

- **Fixer** (`test_fixer.py`) - Python 2 to 3 code transformation
- **Verifier** (`test_verifier.py`) - Compatibility checking
- **Backup Manager** (`test_backup_manager.py`) - Backup operations
- **Configuration Manager** (`test_config_manager.py`) - Configuration handling
- **CLI** (`test_cli.py`) - Command-line interface

## Running Tests

### Prerequisites

Install pytest and required dependencies:

```bash
pip install pytest pytest-cov
```

Or install from the project's development dependencies:

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
# From the project root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=src --cov-report=html
```

### Run Specific Test Files

```bash
# Run only fixer tests
pytest tests/test_fixer.py

# Run only config manager tests
pytest tests/test_config_manager.py
```

### Run Tests by Category

Tests are marked with categories for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all except slow tests
pytest -m "not slow"
```

## Test Structure

### Fixtures (`conftest.py`)

Shared fixtures provide:

- `temp_dir` - Temporary directory for test files
- `sample_py2_file` - Sample Python 2 code file
- `sample_py3_file` - Sample Python 3 code file
- `sample_directory` - Directory with multiple Python files
- `backup_dir` - Backup directory for testing
- `config_file` - Sample configuration file

### Test Organization

Each test file follows a consistent structure:

```python
@pytest.mark.unit
class TestComponentName:
    """Tests for specific component functionality."""
    
    def test_specific_feature(self):
        """Test a specific feature."""
        # Arrange
        # Act
        # Assert
```

### Test Categories

- **Unit Tests** (`@pytest.mark.unit`) - Test individual components in isolation
- **Integration Tests** (`@pytest.mark.integration`) - Test component interactions
- **Slow Tests** (`@pytest.mark.slow`) - Tests that take significant time

## Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ Core functionality - All main features
- ✅ Error handling - Edge cases and error conditions
- ✅ File operations - Reading, writing, backup, restore
- ✅ Configuration - Loading, saving, merging configs
- ✅ Command-line interface - Argument parsing and command execution

## Writing New Tests

### Template for New Test

```python
import pytest
from module_name import ComponentClass


@pytest.mark.unit
class TestNewFeature:
    """Test new feature description."""
    
    def test_basic_functionality(self, temp_dir):
        """Test basic functionality."""
        # Arrange
        component = ComponentClass()
        
        # Act
        result = component.do_something()
        
        # Assert
        assert result is not None
        assert result.property == expected_value
```

### Best Practices

1. **Use descriptive names** - Test names should clearly describe what is being tested
2. **Follow AAA pattern** - Arrange, Act, Assert
3. **Use fixtures** - Leverage shared fixtures from `conftest.py`
4. **Mark appropriately** - Use `@pytest.mark.*` decorators
5. **Test edge cases** - Include error conditions and boundary cases
6. **Keep tests independent** - Each test should be able to run in isolation
7. **Clean up resources** - Use fixtures with cleanup or teardown

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=src --cov-report=xml
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure the `src` directory is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
pytest
```

### Permission Errors

Some tests create temporary files and directories. Ensure you have write permissions:

```bash
chmod -R u+w tests/
```

### Slow Tests

If tests are taking too long, run only fast tests:

```bash
pytest -m "not slow"
```

## Contributing

When adding new features to the toolkit:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before committing
3. Add new fixtures to `conftest.py` if they're reusable
4. Update this README if adding new test categories

## Coverage Reports

Generate detailed coverage reports:

```bash
# HTML report (opens in browser)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=src --cov-report=term

# XML report (for CI tools)
pytest --cov=src --cov-report=xml
```

## Example Output

```
tests/test_fixer.py ...................... [20%]
tests/test_backup_manager.py ............. [40%]
tests/test_config_manager.py ............. [60%]
tests/test_cli.py ........................ [80%]
tests/test_verifier.py ................... [100%]

======== 87 passed in 2.34s ========
```

## License

Tests are part of the py2to3 toolkit and follow the same MIT License.
