# Code Complexity Analyzer Guide 📊

## Overview

The **Code Complexity Analyzer** is a powerful tool that helps you understand how Python 2 to 3 migration affects your code's complexity. It measures various complexity metrics and compares before/after states to identify files that may have become more complex and need manual refactoring.

## Why Code Complexity Matters

Automated migration tools are excellent at converting syntax, but they can sometimes make code more complex:

- **Verbose Conversions**: Simple Python 2 patterns might convert to more verbose Python 3 code
- **Type Handling**: String and Unicode handling changes can add complexity
- **Import Changes**: Multiple import statements might be needed
- **Compatibility Layers**: Temporary compatibility code can increase complexity

By measuring complexity, you can:
- **Identify hotspots**: Find files that need manual attention
- **Track quality**: Ensure migration doesn't reduce code quality
- **Prioritize refactoring**: Focus on files with the biggest complexity increases
- **Measure progress**: Track improvements over time

## Complexity Metrics

The analyzer tracks several industry-standard metrics:

### 1. Cyclomatic Complexity (McCabe)
- Measures the number of linearly independent paths through code
- **Good**: < 10 (Simple, easy to test)
- **Moderate**: 10-20 (More complex, needs attention)
- **High**: > 20 (Very complex, refactor recommended)

### 2. Maintainability Index
- Microsoft's formula combining various metrics
- Scored 0-100 (higher is better)
- **Good**: > 85 (Highly maintainable)
- **Moderate**: 65-85 (Acceptable)
- **Poor**: < 65 (Difficult to maintain)

### 3. Halstead Metrics
- **Volume**: Size and vocabulary of the program
- **Difficulty**: How difficult the code is to write/understand
- **Effort**: Mental effort required to develop/maintain

### 4. Source Lines of Code (SLOC)
- Non-comment, non-blank lines of code
- Indicator of file size and scope

### 5. Comment Ratio
- Percentage of lines that are comments
- Good documentation typically has 10-30% comments

## Quick Start

### Basic Analysis

Analyze current code complexity without comparison:

```bash
# Analyze a directory
./py2to3 complexity src/

# Save report to file
./py2to3 complexity src/ --output complexity_report.txt

# JSON format for automation
./py2to3 complexity src/ --format json --output complexity.json
```

### Comparison Analysis

Compare current code with backup to see migration impact:

```bash
# Create backup first (if not already done)
./py2to3 backup create src/ --destination backups/

# Analyze and compare
./py2to3 complexity src/ --backup-dir backups/ --compare

# Save detailed comparison report
./py2to3 complexity src/ --backup-dir backups/ --compare --output migration_impact.txt
```

## Usage Examples

### Example 1: Post-Migration Review

After running automatic migration, check complexity impact:

```bash
# Step 1: Backup before migration
./py2to3 backup create src/ --destination pre-migration/

# Step 2: Run migration
./py2to3 fix src/ --backup-dir backups/

# Step 3: Analyze complexity changes
./py2to3 complexity src/ --backup-dir pre-migration/ --compare

# Step 4: Review files that increased in complexity
./py2to3 complexity src/ --backup-dir pre-migration/ --compare --output review_needed.txt
```

### Example 2: Tracking Progress

Monitor complexity as you refactor:

```bash
# Initial analysis
./py2to3 complexity src/ --output baseline.txt

# After refactoring some files
./py2to3 complexity src/ --output iteration1.txt

# Compare metrics to see improvement
diff baseline.txt iteration1.txt
```

### Example 3: CI/CD Integration

Add complexity checks to your CI pipeline:

```bash
# Generate JSON report for processing
./py2to3 complexity src/ --format json --output complexity.json

# Parse and fail build if complexity is too high
python check_complexity_threshold.py complexity.json
```

### Example 4: Focus on Specific Modules

Analyze specific parts of your codebase:

```bash
# Just the core module
./py2to3 complexity src/core/ --backup-dir backups/core/ --compare

# Multiple specific files
./py2to3 complexity src/utils/ --backup-dir backups/utils/ --compare
```

## Understanding the Report

### Text Format Report

The text report includes:

```
================================================================================
CODE COMPLEXITY ANALYSIS REPORT
================================================================================
Timestamp: 2024-01-15T10:30:00
Directory: src/

SUMMARY
--------------------------------------------------------------------------------
Total Python files: 45
Successfully analyzed: 43
Syntax errors: 2
Other errors: 0

Average Metrics:
  Lines of Code (LOC): 156
  Cyclomatic Complexity: 8.3
  Maintainability Index: 72.5/100
  Halstead Difficulty: 12.7

MIGRATION IMPACT ANALYSIS
--------------------------------------------------------------------------------
Complexity Trends:
  Significantly Worse: 5 files
  Worse: 8 files
  Neutral: 25 files
  Better: 5 files

FILES NEEDING REVIEW (Top 10):
--------------------------------------------------------------------------------

src/data/parser.py [SIGNIFICANTLY_WORSE]
  Cyclomatic: 15 → 28 (+13, +86.7%)
  Maintainability: 75.2 → 58.4 (-16.8, -22.3%)

src/utils/converter.py [WORSE]
  Cyclomatic: 8 → 12 (+4, +50.0%)
  Maintainability: 82.1 → 74.3 (-7.8, -9.5%)

FILES IMPROVED (Top 5):
--------------------------------------------------------------------------------

src/models/base.py
  Maintainability: 68.3 → 81.2 (+12.9)

================================================================================
RECOMMENDATIONS
--------------------------------------------------------------------------------
⚠️  13 files have increased in complexity after migration.
   Consider manual refactoring for files listed above.

⚠️  Average maintainability index is low (<65).
   Focus on improving code structure and documentation.

✓ Analysis complete!
================================================================================
```

### JSON Format Report

For automation and custom processing:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "directory": "src/",
  "files": {
    "src/data/parser.py": {
      "current": {
        "loc": 234,
        "cyclomatic": 28,
        "maintainability": 58.4,
        "status": "success"
      },
      "backup": {
        "loc": 198,
        "cyclomatic": 15,
        "maintainability": 75.2,
        "status": "success"
      },
      "changes": {
        "cyclomatic": {
          "old": 15,
          "new": 28,
          "delta": 13,
          "percent": 86.7
        }
      },
      "trend": "significantly_worse"
    }
  },
  "summary": {
    "total_files": 45,
    "analyzed": 43,
    "trends": {
      "significantly_worse": 5,
      "worse": 8,
      "neutral": 25,
      "better": 5
    }
  }
}
```

## Interpreting Results

### Trend Classifications

- **Significantly Worse**: Cyclomatic complexity increased AND maintainability decreased > 5 points
  - **Action**: Immediate refactoring recommended
  
- **Worse**: Cyclomatic complexity increased OR maintainability decreased
  - **Action**: Review and consider refactoring
  
- **Neutral**: No significant changes
  - **Action**: No action needed
  
- **Better**: Maintainability increased > 5 points
  - **Action**: Good migration result!

### When to Refactor

Consider manual refactoring when:

1. **Cyclomatic complexity > 20**: Break down complex functions
2. **Maintainability index < 65**: Improve structure and documentation
3. **Complexity increased > 50%**: Review migration results
4. **Many nested conditions**: Simplify logic
5. **Large LOC increase**: May indicate verbose conversions

## Best Practices

### 1. Baseline Before Migration

Always establish a baseline:

```bash
# Before any changes
./py2to3 complexity src/ --output pre-migration-baseline.txt
```

### 2. Incremental Analysis

Analyze after each major change:

```bash
# After fixing imports
./py2to3 complexity src/ --output after-imports.txt

# After fixing print statements
./py2to3 complexity src/ --output after-prints.txt
```

### 3. Set Thresholds

Define acceptable complexity levels for your project:

```bash
# Create a script to check thresholds
cat > check_complexity.sh << 'EOF'
#!/bin/bash
./py2to3 complexity src/ --format json --output complexity.json
AVG_CYCLO=$(jq '.summary.avg_cyclomatic' complexity.json)
if (( $(echo "$AVG_CYCLO > 15" | bc -l) )); then
  echo "Average complexity too high: $AVG_CYCLO"
  exit 1
fi
EOF
chmod +x check_complexity.sh
```

### 4. Focus on Critical Paths

Prioritize complexity reduction in:
- Core business logic
- Frequently modified code
- Security-sensitive code
- Complex algorithms

### 5. Document Complexity Decisions

When high complexity is justified:

```python
# Complex but necessary for performance
# Cyclomatic: 25 (high but optimized)
def optimized_parser(data):
    ...
```

## Integration with Other Tools

### With Migration Workflow

```bash
# Complete workflow with complexity tracking
./py2to3 backup create src/ --destination pre-migration/
./py2to3 preflight src/
./py2to3 fix src/
./py2to3 complexity src/ --backup-dir pre-migration/ --compare
./py2to3 report --output migration_report.html
```

### With Git Integration

```bash
# Track complexity in commits
./py2to3 complexity src/ --output complexity_$(git rev-parse --short HEAD).txt
git add complexity_*.txt
git commit -m "Complexity analysis for migration phase 1"
```

### With Quality Tools

```bash
# Combined quality check
./py2to3 complexity src/ --output complexity.txt
./py2to3 quality src/ --output quality.txt
./py2to3 security src/ --output security.txt

# Create combined report
cat complexity.txt quality.txt security.txt > full_analysis.txt
```

## Troubleshooting

### Syntax Errors During Analysis

If files have syntax errors:

```bash
# Fix syntax errors first
./py2to3 fix src/ --safe-only

# Then analyze
./py2to3 complexity src/
```

### High False Positives

Some patterns naturally increase complexity scores:

- Error handling with many except clauses
- State machines with many conditions
- Configuration parsing with validation

These may be justified; review manually.

### Missing Backup Directory

If backup directory doesn't exist:

```bash
# Check backup location
./py2to3 backup list

# Use correct backup
./py2to3 complexity src/ --backup-dir $(./py2to3 backup list | tail -1)
```

## Advanced Usage

### Custom Metric Thresholds

Create custom analysis scripts:

```python
import json
from complexity_analyzer import ComplexityAnalyzer

analyzer = ComplexityAnalyzer(backup_dir='backups/')
results = analyzer.analyze_directory('src/', compare_backups=True)

# Custom threshold checking
for filepath, data in results['files'].items():
    if data.get('trend') == 'significantly_worse':
        cyclo_change = data['changes']['cyclomatic']['percent']
        if cyclo_change > 100:  # Doubled complexity
            print(f"CRITICAL: {filepath} complexity doubled!")
```

### Automated Refactoring Suggestions

Combine with other tools:

```bash
# Find complex files
./py2to3 complexity src/ --format json > complexity.json

# Extract files needing refactoring
jq -r '.files | to_entries[] | select(.value.trend == "significantly_worse") | .key' complexity.json > needs_refactoring.txt

# Run quality analysis on those files
while read file; do
  ./py2to3 quality "$file" --suggestions
done < needs_refactoring.txt
```

## Tips and Tricks

1. **Regular Monitoring**: Run complexity analysis regularly, not just once
2. **Team Standards**: Define team-wide complexity thresholds
3. **Documentation**: Document why high complexity is acceptable where it is
4. **Incremental Improvement**: Focus on reducing complexity gradually
5. **Automated Checks**: Add complexity checks to CI/CD pipeline
6. **Visual Tracking**: Use trends over time to track improvement
7. **Combine Metrics**: Don't rely on one metric alone
8. **Context Matters**: High complexity may be justified for complex problems

## FAQ

**Q: What's a good target maintainability index?**  
A: Aim for > 75. Above 85 is excellent, below 65 needs attention.

**Q: Should I always reduce complexity?**  
A: Not always. Some problems are inherently complex. Focus on unnecessary complexity.

**Q: How often should I run complexity analysis?**  
A: After major changes, weekly during active migration, monthly for maintenance.

**Q: Can I analyze non-migrated code?**  
A: Yes! Use it without `--compare` to analyze any Python code.

**Q: What if complexity increased after migration?**  
A: Review the file manually. Sometimes automated fixes are verbose. Refactor if needed.

**Q: How do I know which files to refactor first?**  
A: Start with "significantly_worse" files with highest cyclomatic complexity increases.

## See Also

- [Quality Checker Guide](QUALITY_GUIDE.md) - Code quality analysis
- [Review Assistant Guide](REVIEW_GUIDE.md) - Manual code review help
- [Risk Analyzer Guide](RISK_GUIDE.md) - Identify high-risk changes
- [Backup Manager Guide](BACKUP_GUIDE.md) - Creating backups for comparison
- [Report Generator Guide](REPORT_CARD_GUIDE.md) - Comprehensive reports

## Support

For issues or questions:
- Review the metrics definitions above
- Check the [QUICK_START.md](QUICK_START.md) guide
- Run `./py2to3 complexity --help` for command-line help
- See existing complexity analysis examples in the repo

---

**Remember**: Complexity analysis is a guide, not a rule. Use your judgment to balance simplicity with functionality. The goal is maintainable code, not just low complexity scores.
