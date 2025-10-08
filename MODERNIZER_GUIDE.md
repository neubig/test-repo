# Code Modernizer Guide

## Overview

The **Code Modernizer** is a powerful tool that helps upgrade your Python 3 compatible code to use modern Python 3.6+ idioms and features. After migrating from Python 2 to Python 3, your code may still use outdated patterns. This tool identifies opportunities to modernize your codebase for better readability, maintainability, and performance.

## Why Modernize?

After a successful Python 2 to 3 migration, your code is functional but may still contain:
- Old-style string formatting (`%` and `.format()`)
- Traditional file path operations (`os.path.*`)
- Missing type hints
- Verbose class definitions that could use dataclasses
- Manual resource management instead of context managers
- Verbose loops that could be comprehensions

The Code Modernizer helps you identify and optionally fix these patterns automatically!

## Features

The modernizer analyzes your code for the following improvement opportunities:

### 1. F-Strings (Python 3.6+)
**What it does**: Identifies old-style string formatting and suggests f-strings.

**Before:**
```python
name = "World"
message = "Hello, %s!" % name
greeting = "Hello, {}!".format(name)
```

**After:**
```python
name = "World"
message = f"Hello, {name}!"
greeting = f"Hello, {name}!"
```

**Benefits**: More readable, faster, and less prone to errors.

### 2. Pathlib (Python 3.4+)
**What it does**: Identifies `os.path` operations that could use pathlib.

**Before:**
```python
import os
path = os.path.join("/home", "user", "file.txt")
if os.path.exists(path):
    basename = os.path.basename(path)
```

**After:**
```python
from pathlib import Path
path = Path("/home") / "user" / "file.txt"
if path.exists():
    basename = path.name
```

**Benefits**: More intuitive and object-oriented path handling.

### 3. Dictionary Merge Operator (Python 3.9+)
**What it does**: Suggests using the `|` operator for dictionary merging.

**Before:**
```python
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3}
dict1.update(dict2)
```

**After:**
```python
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3}
dict1 = dict1 | dict2
```

**Benefits**: More concise and functional style.

### 4. Type Hints (Python 3.5+)
**What it does**: Identifies functions that could benefit from type hints.

**Before:**
```python
def calculate_total(price, quantity):
    return price * quantity
```

**After:**
```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

**Benefits**: Better IDE support, early error detection, and improved documentation.

### 5. Dataclasses (Python 3.7+)
**What it does**: Identifies simple classes that could use the `@dataclass` decorator.

**Before:**
```python
class Person:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email
```

**After:**
```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str
```

**Benefits**: Less boilerplate, automatic `__repr__`, `__eq__`, and more.

### 6. Context Managers (Python 2.5+, but often overlooked)
**What it does**: Identifies file operations that should use context managers.

**Before:**
```python
f = open("file.txt", "r")
content = f.read()
f.close()
```

**After:**
```python
with open("file.txt", "r") as f:
    content = f.read()
```

**Benefits**: Automatic resource cleanup, prevents resource leaks.

### 7. List Comprehensions
**What it does**: Identifies loops that could be more concisely written as comprehensions.

**Before:**
```python
result = []
for item in items:
    result.append(item * 2)
```

**After:**
```python
result = [item * 2 for item in items]
```

**Benefits**: More concise, often faster, and more Pythonic.

## Usage

### Basic Analysis

Analyze a single file:
```bash
./py2to3 modernize src/myfile.py
```

Analyze an entire directory:
```bash
./py2to3 modernize src/
```

Analyze current directory:
```bash
./py2to3 modernize
```

### Generate Reports

Save a detailed text report:
```bash
./py2to3 modernize src/ -o modernization_report.txt
```

Generate JSON output for CI/CD integration:
```bash
./py2to3 modernize src/ --format json -o report.json
```

### Filter by Category

Analyze only specific modernization categories:
```bash
# Only check for f-string opportunities
./py2to3 modernize src/ --categories f-strings

# Check multiple categories
./py2to3 modernize src/ --categories f-strings pathlib type-hints
```

Available categories:
- `f-strings` - String formatting modernization
- `pathlib` - Path handling modernization
- `dict-merge` - Dictionary operations
- `type-hints` - Type annotation suggestions
- `dataclass` - Dataclass opportunities
- `context-manager` - Context manager usage
- `comprehension` - List/dict/set comprehension opportunities

### Apply Suggestions (Experimental)

**Note**: Auto-apply is experimental and currently supports limited transformations.

Preview changes without modifying files (dry-run mode):
```bash
./py2to3 modernize src/ --apply --dry-run
```

Apply changes to files:
```bash
./py2to3 modernize src/ --apply --no-dry-run
```

Apply only specific categories:
```bash
./py2to3 modernize src/ --apply --categories f-strings context-manager
```

## Understanding the Report

The modernizer generates a comprehensive report with:

### Summary Section
```
SUMMARY
--------------------------------------------------------------------------------
Total suggestions: 42

By category:
  f-strings           :   18
  type-hints          :   12
  pathlib             :    7
  context-manager     :    5
```

### Detailed Suggestions
Each suggestion includes:
- **File path** and **line number**
- **Category** of the modernization
- **Severity indicator**:
  - ℹ️  Info - Optional improvement
  - 💡 Suggested - Good practice
  - ⭐ Recommended - Strongly recommended
- **Description** of the improvement
- **Current code** snippet
- **Suggested code** snippet

Example:
```
📄 src/utils/helpers.py
   ───────────────────────────────────────────────────────────────────────────
   ⭐ Line 42 [f-strings]
      Replace .format() with f-strings for better readability
      Current:  message = "Processing {} items".format(count)
      Suggested: Use f-string: f"text {variable}"
```

## Integration with Migration Workflow

### Recommended Workflow

1. **Complete Python 3 migration**:
   ```bash
   ./py2to3 migrate src/
   ```

2. **Verify compatibility**:
   ```bash
   ./py2to3 check src/
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Modernize the code**:
   ```bash
   ./py2to3 modernize src/ -o modernization_report.txt
   ```

5. **Review suggestions** and manually apply appropriate ones

6. **Run tests again** to ensure nothing broke

7. **Commit changes**:
   ```bash
   git add -A
   git commit -m "Modernize codebase with Python 3.6+ features"
   ```

### CI/CD Integration

Add modernization checks to your CI/CD pipeline:

```yaml
# .github/workflows/modernization-check.yml
name: Code Modernization Check

on: [push, pull_request]

jobs:
  check-modernization:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Check code modernization opportunities
        run: |
          ./py2to3 modernize src/ --format json -o modernization.json
          
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: modernization-report
          path: modernization.json
```

The command returns:
- **Exit code 0**: No suggestions found (code is modern)
- **Exit code 1**: Suggestions found (for CI/CD to flag)

## Best Practices

### 1. Start with High-Priority Categories
Focus on modernizations that provide the most benefit:
```bash
./py2to3 modernize src/ --categories f-strings context-manager
```

### 2. Review Before Applying
Always review suggestions before applying them automatically:
```bash
./py2to3 modernize src/ -o review.txt
# Review review.txt
./py2to3 modernize src/ --apply --categories f-strings
```

### 3. Test After Each Category
Apply and test one category at a time:
```bash
./py2to3 modernize src/ --apply --categories f-strings
pytest
git commit -am "Modernize: Replace string formatting with f-strings"
```

### 4. Consider Python Version Requirements
Some modernizations require specific Python versions:
- F-strings: Python 3.6+
- Dataclasses: Python 3.7+
- Dictionary merge (`|`): Python 3.9+

Check your project's minimum Python version before applying.

### 5. Use with Code Quality Tools
Combine with other quality tools for best results:
```bash
./py2to3 modernize src/
./py2to3 quality src/
./py2to3 lint src/
```

## Examples

### Example 1: Modernizing a Web Application

```bash
# Analyze the entire application
./py2to3 modernize webapp/ -o modernization_report.txt

# Review the report
cat modernization_report.txt

# Apply f-strings first (safe and impactful)
./py2to3 modernize webapp/ --apply --categories f-strings --dry-run
pytest  # Make sure tests still pass
./py2to3 modernize webapp/ --apply --categories f-strings

# Apply context manager improvements
./py2to3 modernize webapp/ --apply --categories context-manager
pytest

# Commit changes
git add -A
git commit -m "Modernize webapp: f-strings and context managers"
```

### Example 2: Gradual Modernization

```bash
# Day 1: Analyze and plan
./py2to3 modernize . -o day1_report.txt

# Day 2: Modernize string formatting
./py2to3 modernize . --apply --categories f-strings
pytest && git commit -am "Modernize: f-strings"

# Day 3: Add type hints (manual work)
# Review type-hints suggestions and add them manually
git commit -am "Add type hints to core modules"

# Day 4: Modernize path operations
./py2to3 modernize . --apply --categories pathlib
pytest && git commit -am "Modernize: pathlib"

# Day 5: Final review and cleanup
./py2to3 modernize . -o final_report.txt
```

### Example 3: Pre-Release Check

```bash
# Before releasing version 2.0, ensure code is modern
./py2to3 modernize src/ --format json -o pre_release_check.json

# Review and fix critical suggestions
# ...

# Verify no major modernization opportunities remain
./py2to3 modernize src/ | grep "⭐"
```

## Troubleshooting

### "No suggestions found" but code looks outdated
- The tool focuses on specific patterns. Some modernizations require manual review.
- Try analyzing with `--categories` to see if specific categories have suggestions.

### False positives in suggestions
- Review each suggestion carefully. Not all suggestions may be appropriate for your codebase.
- Some patterns may be intentionally kept for compatibility reasons.

### Applied changes break tests
- Always test after applying suggestions.
- Use `--dry-run` first to preview changes.
- Apply one category at a time and test incrementally.

### JSON output format
The JSON output includes:
```json
{
  "total_suggestions": 42,
  "stats": {
    "f-strings": 18,
    "type-hints": 12,
    "pathlib": 7
  },
  "suggestions": [
    {
      "file": "src/app.py",
      "line": 42,
      "category": "f-strings",
      "severity": "recommended",
      "description": "Replace .format() with f-strings",
      "old_code": "...",
      "new_code": "..."
    }
  ]
}
```

## Advanced Usage

### Scripting and Automation

Use the JSON output for scripting:
```python
import json
import subprocess

# Run modernizer
result = subprocess.run(
    ["./py2to3", "modernize", "src/", "--format", "json"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)

# Filter high-priority suggestions
high_priority = [
    s for s in data["suggestions"]
    if s["severity"] == "recommended"
]

print(f"Found {len(high_priority)} high-priority suggestions")
```

### Custom Reports

Process the JSON output to generate custom reports:
```bash
./py2to3 modernize src/ --format json | jq '.suggestions[] | select(.severity=="recommended")'
```

## Limitations

1. **Static Analysis**: The modernizer uses pattern matching and AST analysis. It may miss complex patterns or generate false positives.

2. **Auto-Apply**: The `--apply` feature is experimental and supports limited transformations. Manual review and application is recommended for most cases.

3. **Context Awareness**: The tool doesn't understand your specific requirements (e.g., Python version constraints, performance requirements).

4. **Type Hints**: Suggestions for type hints are based on function signatures only. Actual types must be determined by you.

## FAQ

**Q: Should I apply all suggestions?**  
A: No. Review each suggestion and consider your project's requirements, Python version constraints, and coding standards.

**Q: Will this break my code?**  
A: The analysis itself is safe. If you use `--apply`, always test thoroughly and use version control.

**Q: Can I modernize during migration?**  
A: It's better to complete the Python 2→3 migration first, verify everything works, then modernize.

**Q: How is this different from other modernization tools?**  
A: This tool is specifically designed for the post-migration phase and integrates with the py2to3 toolkit workflow.

**Q: Does this replace manual code review?**  
A: No. This tool assists by identifying opportunities, but human judgment is essential for deciding what to apply.

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Code Quality Guide](QUALITY_GUIDE.md) - Code quality analysis
- [Import Optimizer Guide](IMPORT_OPTIMIZER_GUIDE.md) - Import optimization
- [Lint Integration](CLI_GUIDE.md#linting-integration) - Linting integration

## Contributing

Have ideas for more modernization patterns? Contributions are welcome!

1. Add pattern detection logic in `src/code_modernizer.py`
2. Add tests
3. Update this guide
4. Submit a pull request

## License

This tool is part of the py2to3 migration toolkit and is available under the MIT License.
