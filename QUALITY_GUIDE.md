# Code Quality and Complexity Analysis Guide

The **Code Quality Analyzer** is a powerful tool that helps you understand and improve the quality of your Python codebase. It analyzes metrics like complexity, maintainability, and code structure to provide actionable insights.

## Overview

The quality analyzer measures several key metrics:

- **Lines of Code (LOC)**: Total lines including comments and blanks
- **Source Lines (SLOC)**: Actual code lines excluding comments and blanks
- **Cyclomatic Complexity**: Measure of code complexity based on decision points
- **Maintainability Index**: Overall quality score from 0-100 (higher is better)
- **Comment Ratio**: Percentage of lines that are comments
- **Code Structure**: Functions, classes, and their characteristics

## Quick Start

### Analyze a Directory

```bash
# Analyze the src directory (default)
./py2to3 quality

# Analyze a specific directory
./py2to3 quality path/to/code

# Include detailed per-file metrics
./py2to3 quality src/ --detailed
```

### Analyze a Single File

```bash
./py2to3 quality src/fixer.py
```

### Save Report to File

```bash
# Save as text report
./py2to3 quality src/ --output quality_report.txt

# Save as JSON for programmatic analysis
./py2to3 quality src/ --format json --output quality.json
```

## Understanding the Report

### Overall Statistics

Shows aggregate metrics across all analyzed files:

```
Overall Statistics:
  Total Files: 28
  Total Lines: 11,748
  Source Lines (SLOC): 4,091
  Comment Lines: 6,716
  Comment Ratio: 57.17%
  Total Functions: 355
  Total Classes: 41
  Total Complexity: 1738
```

- **Comment Ratio**: 10-30% is generally good; too low means insufficient documentation, too high might indicate over-commenting

### Average Metrics

Shows per-file averages to understand typical file characteristics:

```
Average Metrics:
  LOC per File: 419.57
  Complexity per File: 62.07
  Maintainability Index: 77.74/100
```

- **Maintainability Index (MI)**: 
  - 80-100: Excellent (Grade A)
  - 60-79: Good (Grade B)
  - 40-59: Fair (Grade C)
  - 20-39: Poor (Grade D)
  - 0-19: Very Poor (Grade F)

### Quality Grade Distribution

Visual representation of how files are distributed across quality grades:

```
Quality Grade Distribution:
  A:   8 files ( 28.6%) █████
  B:  19 files ( 67.9%) █████████████
  C:   1 files (  3.6%)
  D:   0 files (  0.0%)
  F:   0 files (  0.0%)
```

**Goal**: Aim for most files in A-B range. Files in C-F range need refactoring.

### Most Complex Files

Identifies files with highest cyclomatic complexity:

```
Most Complex Files:
  src/cli.py
    Complexity: 328
  src/utils/validators.py
    Complexity: 110
```

**Action**: Files with complexity >100 should be candidates for refactoring. Consider:
- Breaking down large functions
- Extracting complex logic into separate functions
- Simplifying conditional statements

### Files Needing Attention

Lists files with lowest maintainability scores:

```
Files Needing Attention (Lowest Quality):
  src/cli.py
    Maintainability: 50.00 (Grade C)
```

**Action**: Prioritize these files for quality improvements.

## Understanding Complexity

Cyclomatic complexity measures the number of linearly independent paths through code. It's calculated based on:

- Conditional statements (`if`, `elif`, `else`)
- Loops (`for`, `while`)
- Boolean operators (`and`, `or`)
- Exception handlers (`except`)

**Complexity Guidelines**:
- 1-10: Simple, easy to maintain
- 11-20: Moderate complexity, still manageable
- 21-50: High complexity, consider refactoring
- 50+: Very high complexity, definitely needs refactoring

## Common Use Cases

### Before Migration Quality Baseline

Establish a quality baseline before starting migration:

```bash
./py2to3 quality src/ --output reports/quality_before.txt
```

### After Migration Quality Comparison

After migration, compare quality to see if it improved:

```bash
./py2to3 quality src/ --output reports/quality_after.txt

# Compare the reports manually or use diff
diff reports/quality_before.txt reports/quality_after.txt
```

### Identify Refactoring Targets

Find files that need the most attention:

```bash
# Detailed report shows all files sorted by quality
./py2to3 quality src/ --detailed --output refactoring_targets.txt
```

### CI/CD Integration

Include quality checks in your CI pipeline:

```bash
# Generate JSON output for automated processing
./py2to3 quality src/ --format json --output quality.json

# You can parse the JSON to enforce quality gates
# Example: Fail CI if average MI < 60
```

### Track Quality Over Time

Take regular snapshots to track quality improvements:

```bash
# Weekly quality snapshot
./py2to3 quality src/ --output "quality_$(date +%Y%m%d).txt"
```

## JSON Output Format

When using `--format json`, you get structured data:

```json
{
  "files": [
    {
      "file": "src/fixer.py",
      "loc": 500,
      "sloc": 350,
      "comments": 120,
      "functions": 15,
      "classes": 2,
      "complexity": 45,
      "maintainability_index": 75.5,
      "grade": "B",
      "long_functions": [...],
      "complex_functions": [...]
    }
  ],
  "summary": {
    "total_files": 28,
    "avg_maintainability_index": 77.74,
    ...
  }
}
```

## Improving Code Quality

### Reduce Complexity

**Problem**: Functions with high cyclomatic complexity

**Solutions**:
1. Extract complex conditions into well-named functions
2. Use early returns to reduce nesting
3. Replace complex conditions with lookup tables or dictionaries
4. Apply the Strategy pattern for complex conditional logic

Example:
```python
# Before (Complex)
def process(data, type, options):
    if type == 'A':
        if options.get('x'):
            # complex logic
        else:
            # more logic
    elif type == 'B':
        # even more logic
    # ... continues

# After (Simple)
def process(data, type, options):
    processor = PROCESSORS.get(type, default_processor)
    return processor(data, options)
```

### Improve Maintainability

**Problem**: Low maintainability index

**Solutions**:
1. Break large files into smaller modules
2. Extract helper functions
3. Add meaningful docstrings and comments
4. Reduce code duplication
5. Simplify complex expressions

### Balance Documentation

**Problem**: Comment ratio too high or too low

**Solutions**:
- **Too Low** (<10%): Add docstrings to all functions/classes, explain complex logic
- **Too High** (>30%): Remove redundant comments that just restate the code, keep only valuable explanations

## Advanced Usage

### Analyze Specific Files Only

```bash
# Analyze only your most critical files
./py2to3 quality src/fixer.py src/verifier.py --detailed
```

### Programmatic Usage

You can also use the analyzer in your own Python scripts:

```python
from code_quality import CodeQualityAnalyzer

analyzer = CodeQualityAnalyzer()
analyzer.analyze_directory('src/')

# Access metrics
print(f"Average MI: {analyzer.summary['avg_maintainability_index']}")

# Get files needing attention
for file_metrics in sorted(analyzer.metrics, key=lambda x: x['maintainability_index']):
    if file_metrics['maintainability_index'] < 60:
        print(f"Refactor needed: {file_metrics['file']}")
```

## Integration with Other Tools

### With Risk Analyzer

Combine quality analysis with risk assessment:

```bash
# Identify high-complexity files that also have migration risks
./py2to3 quality src/ --format json -o quality.json
./py2to3 risk src/ --json -o risk.json

# Cross-reference the reports to prioritize carefully
```

### With Test Generator

Use quality metrics to decide which files need tests most:

```bash
# Generate tests for low-quality, high-complexity files
./py2to3 quality src/ --detailed -o quality.txt
# Review quality.txt
./py2to3 test-gen src/complex_file.py
```

## Tips and Best Practices

1. **Regular Monitoring**: Run quality analysis regularly, not just during migration
2. **Set Quality Gates**: Define minimum MI thresholds for your team
3. **Prioritize High-Impact Files**: Focus on frequently modified files first
4. **Document Intent**: When complexity is necessary, document why
5. **Incremental Improvement**: Don't try to fix everything at once
6. **Team Standards**: Agree on quality standards as a team

## Troubleshooting

### Syntax Errors

If a file has syntax errors, it will be skipped with an error message. Fix syntax errors first before analyzing quality.

### Misleading High Comment Ratio

Auto-generated files or files with large license headers can skew comment ratio. Consider excluding these files from analysis.

### Very Large Files

Files with thousands of lines naturally have higher complexity. Consider splitting them into multiple modules.

## Command Reference

```bash
# Basic usage
py2to3 quality [path]

# Options
-o, --output FILE      Save report to file
-f, --format FORMAT    Output format: text or json (default: text)
-d, --detailed         Include per-file metrics in report
-h, --help            Show help message
```

## Related Commands

- `py2to3 risk`: Analyze migration-specific risks
- `py2to3 stats`: Track migration progress over time
- `py2to3 deps`: Analyze dependencies
- `py2to3 test-gen`: Generate tests for code

## Examples

### Example 1: Quick Health Check

```bash
./py2to3 quality src/
# Quick overview of code quality
```

### Example 2: Detailed Analysis

```bash
./py2to3 quality src/ --detailed --output detailed_quality.txt
# Full per-file report saved to file
```

### Example 3: JSON for Automation

```bash
./py2to3 quality src/ --format json --output quality.json
# Machine-readable output for scripts
```

### Example 4: Single File Deep Dive

```bash
./py2to3 quality src/cli.py --detailed
# Analyze one specific file in detail
```

## Conclusion

The Code Quality Analyzer helps you:
- ✅ Understand your codebase's maintainability
- ✅ Identify refactoring priorities
- ✅ Track quality improvements over time
- ✅ Make data-driven decisions about code health
- ✅ Ensure migration doesn't degrade quality

Use it regularly to keep your codebase healthy and maintainable!
