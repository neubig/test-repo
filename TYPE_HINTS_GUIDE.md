# Type Hints Generator Guide

## Overview

The Type Hints Generator is an automated tool that adds type hints to your Python 3 code after migration from Python 2. Since Python 2 didn't have type hints, this tool helps modernize your codebase by automatically inferring and adding type annotations based on code analysis.

## Why Use Type Hints?

Type hints are one of the most significant improvements in Python 3. They provide:

- **Better IDE Support**: Autocomplete, refactoring, and error detection
- **Early Bug Detection**: Catch type-related bugs before runtime
- **Improved Documentation**: Function signatures become self-documenting
- **Static Type Checking**: Use tools like mypy for additional safety
- **Better Code Maintenance**: Easier to understand and modify code

## Features

- ✨ **Automatic Type Inference**: Analyzes code patterns to infer types
- 📝 **Function Annotations**: Adds type hints to parameters and return values
- 📦 **Smart Import Management**: Automatically adds required typing imports
- 🔍 **Pattern Recognition**: Infers types from default values, return statements, and usage
- 🎯 **Dry Run Mode**: Preview changes before applying them
- 📊 **Detailed Reports**: See exactly what changes were made
- 🚀 **Batch Processing**: Process entire directories at once

## Quick Start

### Basic Usage

Add type hints to a single file:
```bash
./py2to3 typehints myfile.py
```

Add type hints to a directory:
```bash
./py2to3 typehints src/
```

Preview changes without modifying files:
```bash
./py2to3 typehints src/ --dry-run
```

Generate a detailed report:
```bash
./py2to3 typehints src/ --report type_hints_report.txt
```

Generate JSON output for automation:
```bash
./py2to3 typehints src/ --json type_hints.json
```

## How It Works

The Type Hints Generator analyzes your code using several strategies:

### 1. Default Value Analysis

If a parameter has a default value, the type is inferred from it:

```python
# Before
def greet(name, count=1):
    return f"Hello {name}" * count

# After
from typing import str, int
def greet(name: str, count: int = 1) -> str:
    return f"Hello {name}" * count
```

### 2. Return Statement Analysis

The tool analyzes all return statements to infer return types:

```python
# Before
def calculate(x, y):
    if x > y:
        return x - y
    return 0

# After
def calculate(x: int, y: int) -> int:
    if x > y:
        return x - y
    return 0
```

### 3. Collection Type Inference

Infers types for lists, dictionaries, sets, and tuples:

```python
# Before
def get_users():
    return [{"name": "Alice", "age": 30}]

# After
from typing import List, Dict
def get_users() -> List[Dict]:
    return [{"name": "Alice", "age": 30}]
```

### 4. Optional Type Detection

Detects when functions can return None:

```python
# Before
def find_user(user_id):
    if user_id in users:
        return users[user_id]
    return None

# After
from typing import Optional, Dict
def find_user(user_id: int) -> Optional[Dict]:
    if user_id in users:
        return users[user_id]
    return None
```

## Supported Type Constructs

The generator supports common typing module constructs:

- `int`, `str`, `float`, `bool`, `bytes` - Basic types
- `List[T]` - Lists with element types
- `Dict[K, V]` - Dictionaries with key/value types
- `Set[T]` - Sets with element types
- `Tuple[T1, T2, ...]` - Tuples with specific types
- `Optional[T]` - Values that can be None
- `Union[T1, T2]` - Multiple possible types
- `Any` - When type cannot be inferred

## Command Options

### `--dry-run`

Preview changes without modifying files:
```bash
./py2to3 typehints src/ --dry-run
```

This shows you what changes would be made without actually applying them. Perfect for:
- Reviewing proposed changes
- Testing on production code
- Understanding what the tool will do

### `-r, --report`

Save a detailed text report:
```bash
./py2to3 typehints src/ --report report.txt
```

The report includes:
- Summary statistics (files processed, functions annotated, etc.)
- List of modified files with specific changes
- Before/after comparisons for each function
- List of typing imports added

### `--json`

Save results in JSON format:
```bash
./py2to3 typehints src/ --json results.json
```

Useful for:
- Automation and CI/CD integration
- Programmatic analysis of changes
- Integration with other tools

## Examples

### Example 1: Simple Function

**Before:**
```python
def add(a, b):
    return a + b
```

**After:**
```python
def add(a: int, b: int) -> int:
    return a + b
```

### Example 2: Function with Defaults

**Before:**
```python
def create_user(name, age=18, active=True):
    return {"name": name, "age": age, "active": active}
```

**After:**
```python
from typing import Dict
def create_user(name: str, age: int = 18, active: bool = True) -> Dict:
    return {"name": name, "age": age, "active": active}
```

### Example 3: List Processing

**Before:**
```python
def filter_even(numbers):
    return [n for n in numbers if n % 2 == 0]
```

**After:**
```python
from typing import List
def filter_even(numbers: List[int]) -> List[int]:
    return [n for n in numbers if n % 2 == 0]
```

### Example 4: Optional Return

**Before:**
```python
def get_first(items):
    if items:
        return items[0]
    return None
```

**After:**
```python
from typing import List, Optional, Any
def get_first(items: List) -> Optional[Any]:
    if items:
        return items[0]
    return None
```

## Workflow Integration

### After Python 2 to 3 Migration

The typical workflow is:

1. **Migrate from Python 2 to 3**:
   ```bash
   ./py2to3 fix src/
   ```

2. **Verify migration**:
   ```bash
   ./py2to3 check src/
   ```

3. **Add type hints** (this tool):
   ```bash
   ./py2to3 typehints src/
   ```

4. **Check with mypy** (optional):
   ```bash
   mypy src/
   ```

5. **Commit changes**:
   ```bash
   git add -A
   git commit -m "Add type hints to migrated code"
   ```

### With Git Integration

Track your type hint additions:
```bash
# Create a branch for type hints
./py2to3 git branch add-type-hints

# Preview changes
./py2to3 typehints src/ --dry-run

# Apply type hints
./py2to3 typehints src/

# Commit with migration statistics
./py2to3 git commit "type-hints" -m "Add type hints to migrated code"
```

### With CI/CD

Integrate into your CI/CD pipeline:

```yaml
# .github/workflows/type-hints.yml
name: Add Type Hints

on:
  push:
    branches: [main]

jobs:
  add-type-hints:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Add type hints
        run: ./py2to3 typehints src/ --json results.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: type-hints-report
          path: results.json
```

## Best Practices

### 1. Start with Dry Run

Always preview changes first:
```bash
./py2to3 typehints src/ --dry-run --report preview.txt
```

Review the preview report before applying changes.

### 2. Process Incrementally

For large codebases, process one module at a time:
```bash
./py2to3 typehints src/module1/
./py2to3 typehints src/module2/
# etc.
```

### 3. Review Generated Hints

The tool makes educated guesses but may not always be perfect. Review the generated hints, especially:
- Complex functions with multiple return types
- Functions that work with multiple types (consider using Union or generics)
- Public API functions (ensure type hints match documentation)

### 4. Use Static Type Checking

After adding type hints, use mypy to catch type-related issues:
```bash
pip install mypy
mypy src/
```

### 5. Combine with Other Tools

Use with other modernization tools:
```bash
# Add type hints
./py2to3 typehints src/

# Format code with black
black src/

# Run linters
./py2to3 lint src/

# Check quality
./py2to3 quality src/
```

## Limitations

The Type Hints Generator has some limitations:

1. **Type Inference**: Can only infer types from visible patterns in the code
2. **Complex Types**: May use `Any` when specific types cannot be determined
3. **Generic Types**: Limited support for generic types and type variables
4. **Docstrings**: Currently doesn't parse type information from docstrings
5. **Third-party Types**: Doesn't know about custom types from libraries

For complex scenarios, manual refinement may be needed.

## Troubleshooting

### Issue: Types are too generic (e.g., `Any`, `List` without element type)

**Solution**: The tool couldn't infer specific types. Consider:
- Adding explicit type hints manually for complex cases
- Ensuring default values and return statements are clear
- Using more specific return types in your code

### Issue: Wrong type inferred

**Solution**: The tool made an incorrect guess. Options:
- Manually correct the type hint
- Improve code clarity (e.g., use more specific default values)
- Add type comments or annotations to guide inference

### Issue: Syntax errors after adding hints

**Solution**: This is rare but can happen. Check:
- Python version is 3.5+ (required for type hints)
- No circular import issues introduced by typing imports
- Generated code is syntactically valid (file a bug report if not)

### Issue: Import errors with typing module

**Solution**: Ensure you're using Python 3.5 or later:
```bash
python --version  # Should be 3.5+
```

## Integration with Other Commands

The Type Hints Generator works well with other py2to3 commands:

### With Modernize

Check for type hint opportunities:
```bash
./py2to3 modernize src/ --categories type-hints
```

Then apply them:
```bash
./py2to3 typehints src/
```

### With Quality Check

Check code quality before and after:
```bash
# Before
./py2to3 quality src/ > before.txt

# Add type hints
./py2to3 typehints src/

# After
./py2to3 quality src/ > after.txt
```

### With Code Review

Generate review report for type hints:
```bash
./py2to3 typehints src/
./py2to3 review src/ --pr
```

## Advanced Usage

### Programmatic Usage

You can also use the Type Hints Generator as a Python module:

```python
from type_hints_generator import TypeHintsGenerator

# Create generator
generator = TypeHintsGenerator(dry_run=False)

# Process files
results = generator.process_directory('src/')

# Generate reports
generator.generate_report(results, 'report.txt')
generator.generate_json_report(results, 'report.json')

# Access statistics
print(f"Functions annotated: {generator.stats['functions_annotated']}")
print(f"Parameters annotated: {generator.stats['parameters_annotated']}")
```

### Custom Integration

Integrate into your own scripts:

```python
import os
from type_hints_generator import TypeHintsGenerator

def add_type_hints_to_project(project_path):
    """Add type hints to an entire project."""
    generator = TypeHintsGenerator(dry_run=False)
    
    # Process each package
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            print(f"Processing {item}...")
            results = generator.process_directory(item_path)
    
    # Print summary
    print(f"\nTotal functions annotated: {generator.stats['functions_annotated']}")
    return generator.stats

# Usage
add_type_hints_to_project('src/')
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [MODERNIZER Guide](MODERNIZER_GUIDE.md) - Modern Python 3 idioms
- [Code Quality Guide](QUALITY_GUIDE.md) - Code quality analysis
- [Git Integration](GIT_INTEGRATION.md) - Version control integration
- [PEP 484](https://www.python.org/dev/peps/pep-0484/) - Type Hints specification
- [mypy documentation](https://mypy.readthedocs.io/) - Static type checker

## Contributing

To improve the Type Hints Generator:

1. **Add new type inference patterns**: Update `_infer_type_from_value()` in `type_hints_generator.py`
2. **Improve docstring parsing**: Add support for parsing types from docstrings
3. **Add generic type support**: Implement TypeVar and generic type handling
4. **Enhance accuracy**: Add more sophisticated type inference algorithms

## Support

If you encounter issues or have questions:

1. Check this guide for common issues
2. Review the generated reports for details
3. Use dry-run mode to preview changes
4. File bug reports with example code that causes issues

## License

This feature is part of the py2to3 migration toolkit and is available under the MIT License.
