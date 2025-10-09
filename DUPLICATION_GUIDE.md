# Code Duplication Detector Guide 🔍

## Overview

The **Code Duplication Detector** is a powerful tool that identifies duplicated and similar code blocks across your Python codebase. This feature is especially valuable during Python 2 to 3 migrations, as it helps you:

- **Reduce migration work** by identifying code that should be consolidated before migration
- **Improve code quality** by highlighting opportunities for refactoring
- **Follow DRY principles** (Don't Repeat Yourself) automatically
- **Save time** by finding patterns that can be extracted into reusable functions

## Why Use the Duplication Detector?

### During Migration

When migrating from Python 2 to Python 3, discovering duplicated code early can:
- Reduce the amount of code you need to migrate
- Ensure consistent fixes across all instances
- Prevent fixing the same pattern multiple times
- Improve overall code maintainability

### For Code Quality

Even outside of migration contexts, the detector helps you:
- Identify refactoring opportunities
- Find copy-paste programming issues
- Maintain clean, maintainable codebases
- Track technical debt

## Quick Start

### Basic Usage

Analyze a directory for code duplication:

```bash
./py2to3 duplication src/
```

Or use the shorter alias:

```bash
./py2to3 dedup src/
```

### Generate an HTML Report

Create a beautiful, interactive HTML report:

```bash
./py2to3 duplication src/ -f html -o duplication_report.html
```

Then open `duplication_report.html` in your browser to see:
- Visual statistics with colorful charts
- Detailed duplicate code blocks with syntax highlighting
- Recommendations for refactoring
- Duplication rate metrics

### Save to JSON for Automation

Export findings to JSON for CI/CD integration:

```bash
./py2to3 duplication src/ -f json -o duplication.json
```

## Command Options

### Basic Options

```bash
./py2to3 duplication [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - File or directory to analyze (default: `src`)

**Options:**
- `-m, --min-lines N` - Minimum lines per code block (default: 5)
- `-o, --output FILE` - Save report to file
- `-f, --format FORMAT` - Output format: `text`, `json`, or `html` (default: text)
- `-e, --exclude PATTERN` - Patterns to exclude (can be used multiple times)

### Aliases

The following commands are equivalent:
- `./py2to3 duplication`
- `./py2to3 dedup`
- `./py2to3 dup`

## Usage Examples

### Example 1: Basic Analysis

Analyze the `src/` directory with default settings:

```bash
./py2to3 duplication src/
```

**Output:**
```
================================================================================
CODE DUPLICATION ANALYSIS REPORT
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Files analyzed:           42
Total lines:              8,534
Duplicate blocks found:   12
Duplicate locations:      28
Duplicate lines:          156
Duplication rate:         1.83%

DUPLICATE CODE BLOCKS
--------------------------------------------------------------------------------

Duplicate Group #1 (4 instances, 6 lines each)

  📄 src/core/parser.py:45-50
  📄 src/web/scraper.py:123-128
  📄 src/data/processor.py:89-94
  📄 src/utils/helpers.py:234-239

  Code Preview:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")
    with open(path, 'r') as f:
    ...
```

### Example 2: Adjust Sensitivity

Find smaller duplicate blocks (3+ lines):

```bash
./py2to3 duplication src/ -m 3
```

Or find only larger duplications (10+ lines):

```bash
./py2to3 duplication src/ -m 10
```

### Example 3: Exclude Test Files

Exclude test files and build directories:

```bash
./py2to3 duplication src/ -e test_ -e __pycache__ -e build
```

### Example 4: Generate All Report Formats

Create reports in all formats:

```bash
# Text report for console
./py2to3 duplication src/ -o duplication.txt

# JSON report for automation
./py2to3 duplication src/ -f json -o duplication.json

# HTML report for sharing
./py2to3 duplication src/ -f html -o duplication.html
```

### Example 5: Analyze Before and After Migration

Track duplication reduction during migration:

```bash
# Before migration
./py2to3 duplication src/ -f json -o duplication_before.json

# Apply fixes
./py2to3 fix src/

# After migration
./py2to3 duplication src/ -f json -o duplication_after.json

# Compare the results
```

### Example 6: Single File Analysis

Analyze just one file:

```bash
./py2to3 duplication src/core/parser.py
```

## Understanding the Results

### Summary Statistics

- **Files analyzed**: Number of Python files scanned
- **Total lines**: Total lines of code across all files
- **Duplicate blocks found**: Number of unique duplicate patterns
- **Duplicate locations**: Total number of places where duplicates occur
- **Duplicate lines**: Total lines of duplicated code
- **Duplication rate**: Percentage of code that is duplicated

### Duplicate Groups

Each duplicate group shows:
- Number of instances (how many times it appears)
- Lines per instance (size of the duplicate block)
- File locations with line numbers
- Code preview of the duplicated content

### Duplication Rate Guidelines

- **< 3%**: Excellent! Minimal duplication
- **3-5%**: Good - Some duplication but manageable
- **5-10%**: Fair - Consider refactoring
- **> 10%**: Poor - Significant refactoring needed

## Best Practices

### 1. Run Before Migration

Always analyze duplication before starting migration:

```bash
./py2to3 duplication src/ -o duplication_baseline.txt
```

This helps you:
- Identify consolidation opportunities
- Reduce the amount of code to migrate
- Plan refactoring work

### 2. Focus on High-Impact Duplicates

Prioritize duplicates by:
- **Number of instances**: More instances = more savings
- **Lines per instance**: Larger blocks = bigger impact
- **Complexity**: Harder logic benefits more from consolidation

### 3. Refactor Before Migration

Extract duplicated code into utilities:

```python
# Before: Duplicated validation logic
if not os.path.exists(path):
    raise FileNotFoundError(f"Path not found: {path}")

# After: Extracted to utility
validate_path(path)
```

Then migrate the utility once instead of fixing multiple duplicates.

### 4. Set Appropriate Thresholds

Choose `--min-lines` based on your goals:
- **3-5 lines**: Catch all duplication (may have false positives)
- **5-7 lines**: Balanced (default, recommended)
- **8-12 lines**: Focus on significant duplication only

### 5. Integrate into Workflow

Add to your migration workflow:

```bash
# 1. Analyze duplication
./py2to3 duplication src/ -o duplication_report.html

# 2. Review and refactor duplicates
# ... manual refactoring ...

# 3. Run migration
./py2to3 wizard src/

# 4. Verify reduced duplication
./py2to3 duplication src/
```

## Integration with Other Tools

### With CI/CD

Add duplication checking to your CI pipeline:

```yaml
# .github/workflows/migration.yml
- name: Check Duplication
  run: |
    ./py2to3 duplication src/ -f json -o duplication.json
    # Fail if duplication rate > 10%
```

### With Pre-commit Hooks

Prevent commits with high duplication:

```bash
./py2to3 precommit install
```

### With Quality Reports

Combine with quality analysis:

```bash
# Run quality analysis
./py2to3 quality src/ -o quality.txt

# Run duplication analysis
./py2to3 duplication src/ -o duplication.txt

# Generate comprehensive report
./py2to3 report -o migration_report.html
```

## Common Patterns to Look For

### 1. Validation Logic

```python
# Often duplicated across modules
if not isinstance(data, dict):
    raise TypeError("Expected dict")
if 'key' not in data:
    raise KeyError("Missing required key")
```

**Solution**: Extract to validation utilities

### 2. Error Handling

```python
# Common in multiple functions
try:
    result = operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return None
```

**Solution**: Use decorators or context managers

### 3. Data Transformation

```python
# Repeated data processing
data = [item.strip().lower() for item in items]
data = [item for item in data if item]
```

**Solution**: Create reusable transformation functions

### 4. File Operations

```python
# File handling patterns
with open(path, 'r') as f:
    content = f.read()
return json.loads(content)
```

**Solution**: Create file utility functions

## Troubleshooting

### High False Positive Rate

If you're seeing too many false positives:

1. Increase `--min-lines`: `./py2to3 duplication src/ -m 8`
2. Exclude common patterns: `./py2to3 duplication src/ -e utils`
3. Focus on specific directories

### Low Duplication Found

If duplication seems lower than expected:

1. Decrease `--min-lines`: `./py2to3 duplication src/ -m 3`
2. Check if files are being excluded
3. Verify the path is correct

### Performance Issues

For very large codebases:

1. Analyze subdirectories separately
2. Increase `--min-lines` to reduce processing
3. Use `--exclude` to skip large generated files

## Tips and Tricks

### 1. Combine with Other Commands

```bash
# Find duplicates in high-risk areas
./py2to3 risk src/
./py2to3 duplication src/high_risk_module/
```

### 2. Use Before Code Reviews

```bash
# Check for duplication before PR
./py2to3 duplication src/ -o pr_duplication.html
```

### 3. Track Progress Over Time

```bash
# Weekly duplication tracking
./py2to3 duplication src/ -f json -o "duplication_$(date +%Y%m%d).json"
```

### 4. Generate Team Reports

```bash
# Create sharable HTML report
./py2to3 duplication src/ -f html -o duplication_report.html
# Share with team via email or wiki
```

## FAQ

### Q: What counts as duplication?

**A:** The detector identifies code blocks with identical or very similar content after normalization (removing whitespace differences). By default, it looks for blocks of 5+ lines.

### Q: Does it detect similar but not identical code?

**A:** The current version focuses on exact duplicates after normalization. Future versions may add fuzzy matching for similar code.

### Q: Should I eliminate all duplication?

**A:** Not necessarily. Some duplication is acceptable:
- Simple initialization code
- Configuration patterns
- Test setup boilerplate

Focus on complex logic and business rules.

### Q: How is this different from other duplication detectors?

**A:** This tool is:
- Integrated with the migration workflow
- Focused on Python-specific patterns
- Optimized for migration use cases
- Provides multiple output formats

### Q: Can I use this outside of migration projects?

**A:** Absolutely! The duplication detector is useful for any Python project, regardless of whether you're doing a Python 2 to 3 migration.

### Q: Does it support other languages?

**A:** Currently, it's optimized for Python. Support for other languages may be added in future versions.

## Examples of Reports

### Text Report (Console)

Perfect for quick checks and terminal output:

```
================================================================================
CODE DUPLICATION ANALYSIS REPORT
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Files analyzed:           42
Total lines:              8,534
Duplicate blocks found:   12
Duplication rate:         1.83%
...
```

### JSON Report (Automation)

Great for CI/CD and automated analysis:

```json
{
  "summary": {
    "files_analyzed": 42,
    "total_lines": 8534,
    "duplicate_blocks": 12,
    "duplicate_lines": 156
  },
  "duplicates": [
    {
      "hash": "abc123...",
      "instances": 4,
      "lines_per_instance": 6,
      "locations": [...]
    }
  ]
}
```

### HTML Report (Sharing)

Beautiful visualizations with:
- Color-coded statistics cards
- Interactive duplicate groups
- Syntax-highlighted code previews
- Actionable recommendations

## Advanced Configuration

### Custom Exclusion Patterns

Create a config file for complex exclusions:

```bash
# Use multiple exclude patterns
./py2to3 duplication src/ \
  -e "test_*" \
  -e "*_test.py" \
  -e "__pycache__" \
  -e "*.pyc" \
  -e "build/" \
  -e "dist/"
```

### Scripted Analysis

Automate duplication analysis:

```bash
#!/bin/bash
# analyze_duplication.sh

DIRS="src/ lib/ scripts/"
for dir in $DIRS; do
    echo "Analyzing $dir..."
    ./py2to3 duplication $dir -f json -o "duplication_${dir//\//_}.json"
done
```

## Related Tools

- **`./py2to3 quality`** - Overall code quality metrics
- **`./py2to3 complexity`** - Code complexity analysis
- **`./py2to3 smell`** - Code smell detection
- **`./py2to3 review`** - Code review assistant

## Support and Feedback

Found duplicated code? Great! Now you can refactor it before migration.

Have questions or suggestions? Check out:
- The main [README.md](README.md)
- Other guide documents in the repository
- Run `./py2to3 duplication --help` for quick reference

Happy refactoring! 🚀✨
