# Code Smell Detector Guide

## Overview

The Code Smell Detector is a powerful tool that identifies anti-patterns and code smells in your Python codebase. During Python 2 to 3 migration is the perfect time to also improve code quality by refactoring problematic patterns!

## Why Use the Code Smell Detector?

- **Improve Code Quality**: Identify and fix problematic patterns during migration
- **Reduce Technical Debt**: Clean up code smells while you're already making changes
- **Prevent Bugs**: Catch potential bugs like mutable default arguments
- **Enhance Maintainability**: Find complex code that needs simplification
- **Educational**: Learn about code smells and best practices

## Quick Start

```bash
# Analyze a single file
./py2to3 smell path/to/file.py

# Analyze entire directory
./py2to3 smell src/

# Generate HTML report
./py2to3 smell src/ --format html --output smell_report.html

# Generate JSON for automation
./py2to3 smell src/ --format json --output smells.json
```

## What Code Smells Are Detected?

### 1. **Complexity Smells**

#### Long Functions
Functions that are too long (default: >50 lines) are hard to understand and maintain.

```python
# ❌ Bad: Long function
def process_data(data):
    # ... 80 lines of code ...
    pass

# ✅ Good: Break into smaller functions
def process_data(data):
    validated = validate_data(data)
    transformed = transform_data(validated)
    return save_data(transformed)
```

#### Too Many Parameters
Functions with many parameters (default: >5) are hard to use and understand.

```python
# ❌ Bad: Too many parameters
def create_user(name, email, age, address, phone, city, state, zip):
    pass

# ✅ Good: Use a parameter object
def create_user(user_info):
    pass
```

#### Deep Nesting
Code nested too deeply (default: >4 levels) is hard to follow.

```python
# ❌ Bad: Deep nesting
if condition1:
    if condition2:
        if condition3:
            if condition4:
                if condition5:
                    do_something()

# ✅ Good: Use early returns
if not condition1:
    return
if not condition2:
    return
# ... etc
```

### 2. **Bug-Prone Smells**

#### Mutable Default Arguments
Using mutable objects as default arguments is a common Python pitfall.

```python
# ❌ Bad: Mutable default
def add_item(item, items=[]):
    items.append(item)
    return items

# ✅ Good: Use None and create inside
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

#### Bare Except Clauses
Catching all exceptions can hide bugs.

```python
# ❌ Bad: Bare except
try:
    risky_operation()
except:
    pass

# ✅ Good: Catch specific exceptions
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
```

### 3. **Maintainability Smells**

#### Magic Numbers
Hard-coded numbers make code less maintainable.

```python
# ❌ Bad: Magic numbers
if user.age > 65:
    discount = price * 0.15

# ✅ Good: Named constants
SENIOR_AGE = 65
SENIOR_DISCOUNT_RATE = 0.15

if user.age > SENIOR_AGE:
    discount = price * SENIOR_DISCOUNT_RATE
```

#### Global Variable Usage
Global variables make code harder to test and reason about.

```python
# ❌ Bad: Global usage
count = 0

def increment():
    global count
    count += 1

# ✅ Good: Pass as parameter or use class
class Counter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
```

### 4. **Duplication Smells**

#### Duplicate Code
Repeated code blocks should be extracted into functions.

```python
# ❌ Bad: Duplicate code
def process_order():
    print("Starting process")
    validate_input()
    check_inventory()
    # ...

def process_return():
    print("Starting process")
    validate_input()
    check_inventory()
    # ...

# ✅ Good: Extract common code
def common_setup():
    print("Starting process")
    validate_input()
    check_inventory()

def process_order():
    common_setup()
    # ...

def process_return():
    common_setup()
    # ...
```

### 5. **Documentation Smells**

#### Missing Docstrings
Public functions and classes should have docstrings.

```python
# ❌ Bad: No docstring
def calculate_tax(income, rate):
    return income * rate

# ✅ Good: With docstring
def calculate_tax(income, rate):
    """
    Calculate tax amount based on income and rate.
    
    Args:
        income: Annual income amount
        rate: Tax rate as decimal (e.g., 0.15 for 15%)
    
    Returns:
        Calculated tax amount
    """
    return income * rate
```

### 6. **Style Smells**

#### Long Lines
Lines over 120 characters are hard to read.

```python
# ❌ Bad: Long line
result = some_function(parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8)

# ✅ Good: Break into multiple lines
result = some_function(
    parameter1, parameter2, parameter3,
    parameter4, parameter5, parameter6,
    parameter7, parameter8
)
```

## Command-Line Options

### Basic Usage

```bash
./py2to3 smell <path> [options]
```

### Options

- `path`: File or directory to analyze (required)
- `-o, --output FILE`: Save report to file (default: stdout)
- `-f, --format FORMAT`: Report format: text, html, json (default: text)
- `--max-function-length N`: Maximum function length (default: 50)
- `--max-parameters N`: Maximum function parameters (default: 5)
- `--max-nesting N`: Maximum nesting depth (default: 4)
- `--severity LEVEL`: Only show issues of this severity or higher (high/medium/low)
- `--category CAT`: Only show issues in this category
- `--exclude-files PATTERN`: Exclude files matching pattern

## Output Formats

### Text Format (Default)

Human-readable text report with summary and detailed findings:

```bash
./py2to3 smell src/
```

Output:
```
================================================================================
CODE SMELL DETECTION REPORT
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Total smells found: 23
  • High severity:   5
  • Medium severity: 12
  • Low severity:    6

BY CATEGORY
--------------------------------------------------------------------------------
  • Bugs: 5
  • Complexity: 8
  • Maintainability: 6
  • Documentation: 4

...
```

### HTML Format

Beautiful, interactive HTML report:

```bash
./py2to3 smell src/ --format html --output report.html
open report.html  # macOS
```

Features:
- Color-coded severity levels
- Grouped by severity
- Code snippets with syntax highlighting
- Summary statistics

### JSON Format

Machine-readable format for automation:

```bash
./py2to3 smell src/ --format json --output smells.json
```

Use with other tools:
```bash
# Count high-severity issues
jq '[.[] | select(.severity == "high")] | length' smells.json

# Get all bugs category issues
jq '[.[] | select(.category == "bugs")]' smells.json
```

## Customizing Detection Thresholds

Adjust detection sensitivity based on your project:

```bash
# More lenient (good for legacy code)
./py2to3 smell src/ \
  --max-function-length 100 \
  --max-parameters 8 \
  --max-nesting 6

# Stricter (good for new projects)
./py2to3 smell src/ \
  --max-function-length 30 \
  --max-parameters 3 \
  --max-nesting 3
```

## Integration with Migration Workflow

### 1. Before Migration
Assess code quality baseline:

```bash
./py2to3 smell src/ --format json --output smells_before.json
```

### 2. During Migration
Fix smells while migrating:

```bash
# Analyze file before fixing
./py2to3 smell src/module.py

# Fix Python 2 issues
./py2to3 fix src/module.py

# Analyze again and fix smells
./py2to3 smell src/module.py
# ... refactor based on suggestions ...
```

### 3. After Migration
Compare before and after:

```bash
./py2to3 smell src/ --format json --output smells_after.json

# Compare counts
echo "Before: $(jq 'length' smells_before.json)"
echo "After: $(jq 'length' smells_after.json)"
```

## Filtering Results

### By Severity

```bash
# Only high-severity issues
./py2to3 smell src/ --severity high

# High and medium
./py2to3 smell src/ --severity medium
```

### By Category

```bash
# Only bug-related smells
./py2to3 smell src/ --category bugs

# Only complexity issues
./py2to3 smell src/ --category complexity
```

### By File Pattern

```bash
# Exclude test files
./py2to3 smell src/ --exclude-files "test_*.py"

# Exclude multiple patterns
./py2to3 smell src/ --exclude-files "test_*.py,*_old.py"
```

## Best Practices

### 1. **Start with High-Severity Issues**
Focus on bugs and security issues first:

```bash
./py2to3 smell src/ --severity high
```

### 2. **Address Smells File-by-File**
Don't try to fix everything at once:

```bash
# Analyze one file
./py2to3 smell src/module.py

# Fix issues
# ... edit file ...

# Verify
./py2to3 smell src/module.py
```

### 3. **Track Progress**
Monitor improvement over time:

```bash
# Weekly smell check
./py2to3 smell src/ --format json --output "smells_$(date +%Y%m%d).json"

# Compare with last week
diff smells_20240101.json smells_20240108.json
```

### 4. **Integrate into CI/CD**
Prevent smell regression:

```yaml
# .github/workflows/quality.yml
- name: Check code smells
  run: |
    ./py2to3 smell src/ --severity high --format json > smells.json
    if [ $(jq 'length' smells.json) -gt 0 ]; then
      echo "High-severity smells detected!"
      exit 1
    fi
```

### 5. **Combine with Other Tools**
Use alongside other quality tools:

```bash
# Full quality check
./py2to3 quality src/           # Complexity analysis
./py2to3 smell src/              # Code smells
./py2to3 security src/           # Security issues
./py2to3 lint src/               # Style issues
```

## Common Patterns and Solutions

### Pattern 1: Large Legacy Module

**Problem**: 500-line module with multiple smells

**Solution**:
1. Extract classes into separate files
2. Break long functions into smaller ones
3. Use dependency injection instead of globals

```bash
# Before
./py2to3 smell legacy_module.py
# 45 smells found

# After refactoring
./py2to3 smell refactored/
# 8 smells found
```

### Pattern 2: Copy-Pasted Code

**Problem**: Duplicate code in multiple places

**Solution**:
1. Identify common patterns
2. Extract into utility functions
3. Update all call sites

```bash
./py2to3 smell src/ --category duplication
# Shows all duplicate blocks
```

### Pattern 3: Complex Business Logic

**Problem**: Deep nesting in business logic

**Solution**:
1. Use early returns
2. Extract conditions into named functions
3. Use strategy pattern for complex conditions

```bash
./py2to3 smell src/business/ --severity medium
# Focus on complexity issues
```

## Understanding the Report

### Severity Levels

- **High**: Should fix immediately (bugs, security)
- **Medium**: Should fix soon (complexity, maintainability)
- **Low**: Fix when convenient (style, documentation)

### Categories

- **bugs**: Likely to cause runtime errors
- **complexity**: Hard to understand/maintain
- **maintainability**: Makes future changes difficult
- **duplication**: Repeated code
- **documentation**: Missing or poor documentation
- **style**: Formatting and readability

## Tips for Success

1. **Don't Fix Everything at Once**: Start small and iterate
2. **Prioritize by Impact**: High-severity issues first
3. **Test After Refactoring**: Ensure changes don't break functionality
4. **Document Decisions**: Track why you chose certain refactorings
5. **Get Team Buy-In**: Make smell detection part of your workflow

## Real-World Example

```bash
# 1. Analyze current state
$ ./py2to3 smell src/ --format html -o before.html
Found 67 smells: 12 high, 31 medium, 24 low

# 2. Fix high-severity issues
$ ./py2to3 smell src/ --severity high
# ... fix mutable defaults, bare excepts ...

# 3. Refactor complex functions
$ ./py2to3 smell src/ --category complexity --severity medium
# ... break up long functions ...

# 4. Verify improvement
$ ./py2to3 smell src/ --format html -o after.html
Found 23 smells: 0 high, 12 medium, 11 low

# 5. Track remaining work
$ ./py2to3 smell src/ --format json -o smells_tracking.json
```

## Troubleshooting

### "Too Many Smells Found"

**Solution**: Start with higher severity only:
```bash
./py2to3 smell src/ --severity high
```

### "False Positives"

**Solution**: Use custom thresholds or exclude specific files:
```bash
./py2to3 smell src/ --max-function-length 80 --exclude-files "generated_*.py"
```

### "Can't Fix Duplicate Code"

**Solution**: Use the report to guide refactoring, not as automatic fixes. Code smell detection is about identifying issues, not fixing them automatically.

## Related Commands

- `./py2to3 quality` - Code quality and complexity analysis
- `./py2to3 complexity` - Detailed complexity metrics
- `./py2to3 security` - Security vulnerability scanning
- `./py2to3 modernize` - Upgrade to modern Python 3 idioms

## Learn More

- [Code Quality Guide](QUALITY_GUIDE.md)
- [Complexity Analysis Guide](COMPLEXITY_GUIDE.md)
- [Modernization Guide](MODERNIZER_GUIDE.md)
- [Best Practices](https://docs.python.org/3/howto/functional.html)

---

Remember: The goal isn't to have zero smells, but to have **maintainable, understandable code**. Use this tool as a guide, not a strict requirement!
