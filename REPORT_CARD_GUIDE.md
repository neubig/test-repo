# Migration Report Card Guide

## Overview

The **Migration Report Card** feature provides a comprehensive quality assessment of your Python 2 to 3 migration. Unlike progress tracking tools that show _what_ has been done, the report card evaluates _how well_ the migration has been executed, assigning letter grades (A-F) to different quality aspects.

## Features

- **Overall Grade**: Weighted score across all assessment categories
- **Category Scores**: Individual grades for:
  - Python 3 Compatibility (30% weight)
  - Modern Python 3 Features (20% weight)
  - Code Quality (20% weight)
  - Test Coverage (15% weight)
  - Documentation (10% weight)
  - Best Practices (5% weight)
- **Actionable Recommendations**: Prioritized suggestions for improvement
- **Multiple Output Formats**: Text, HTML, JSON, and Markdown
- **Executive-Friendly**: Perfect for stakeholder presentations

## Basic Usage

### Generate a Report Card

```bash
# Generate report card for current directory (text format)
./py2to3 report-card

# Generate report card for specific project
./py2to3 report-card /path/to/project

# Generate HTML report card
./py2to3 report-card -f html -o migration_report_card.html

# Generate JSON for further analysis
./py2to3 report-card -f json -o report_card.json

# Generate Markdown for documentation
./py2to3 report-card -f markdown -o MIGRATION_GRADE.md
```

## Output Formats

### Text Format (Default)

Simple, readable text output suitable for terminal display:

```
======================================================================
                PYTHON 2 TO 3 MIGRATION REPORT CARD
======================================================================
Generated: 2024-01-15 14:30:22
Project: my-project

OVERALL GRADE: B (82.5/100)

CATEGORY SCORES:
----------------------------------------------------------------------
Python 3 Compatibility.................. A (92.0/100) [30% weight]
Modern Python 3 Features................ C (72.0/100) [20% weight]
Code Quality............................ B (85.0/100) [20% weight]
Test Coverage........................... B (80.0/100) [15% weight]
Documentation........................... A (90.0/100) [10% weight]
Best Practices.......................... B (85.0/100) [5% weight]

RECOMMENDATIONS:
----------------------------------------------------------------------

HIGH:
  • [test_coverage] Only 8 test files for 10 source files. Add more tests!

MEDIUM:
  • [modernization] Consider using f-strings instead of .format() or % formatting
  • [modernization] Add type hints to improve code quality and IDE support
```

### HTML Format

Beautiful, interactive HTML report with:
- Color-coded grades
- Visual styling
- Easy-to-read tables
- Professional presentation

Perfect for:
- Sharing with stakeholders
- Team presentations
- Progress documentation

### JSON Format

Structured data format for:
- Integration with CI/CD pipelines
- Custom analysis tools
- Tracking over time
- Automated reporting

Example structure:
```json
{
  "generated": "2024-01-15T14:30:22",
  "project": "my-project",
  "overall": {
    "score": 82.5,
    "grade": "B"
  },
  "categories": {
    "compatibility": {
      "name": "Python 3 Compatibility",
      "score": 92.0,
      "grade": "A",
      "weight": 30
    },
    ...
  },
  "recommendations": [...]
}
```

### Markdown Format

Documentation-friendly format that can be:
- Committed to version control
- Included in project documentation
- Rendered on GitHub/GitLab
- Shared in wikis

## Assessment Categories

### 1. Python 3 Compatibility (30% weight)

Evaluates how well the code runs on Python 3:
- Checks for Python 2-specific code patterns
- Identifies critical/high/medium/low severity issues
- Uses the verifier tool for comprehensive analysis

**Scoring:**
- Critical issues: -10 points each
- High issues: -5 points each
- Medium issues: -2 points each
- Low issues: -1 point each

**Grades:**
- A (90-100): No critical issues, minimal other issues
- B (80-89): Some high-priority issues
- C (70-79): Multiple issues requiring attention
- D (60-69): Many issues, significant work needed
- F (<60): Critical compatibility problems

### 2. Modern Python 3 Features (20% weight)

Assesses use of modern Python 3 idioms and features:
- F-strings vs old-style formatting
- Type hints
- Pathlib vs os.path
- Dataclasses
- Async/await syntax
- Walrus operator (:=)

**Note:** This is a nice-to-have category, so base scores are boosted.

### 3. Code Quality (20% weight)

Evaluates overall code quality:
- Presence of docstrings
- Reasonable file lengths (<500 lines)
- Absence of TODO/FIXME comments
- Good naming conventions

### 4. Test Coverage (15% weight)

Measures test coverage using a simple heuristic:
- Ratio of test files to source files
- Ideal ratio: 1:1 or better

**Grades:**
- A (90-100): Excellent coverage (≥90% ratio)
- B (80-89): Good coverage (≥80% ratio)
- C (70-79): Adequate coverage (≥70% ratio)
- D (60-69): Poor coverage (≥60% ratio)
- F (<60): Insufficient testing

### 5. Documentation (10% weight)

Checks for essential documentation:
- README.md
- CHANGELOG.md
- CONTRIBUTING.md
- LICENSE
- Additional markdown files

### 6. Best Practices (5% weight)

Verifies adherence to Python best practices:
- .gitignore present
- requirements.txt or setup.py
- Tests directory
- Configuration files
- No .pyc files committed

## Use Cases

### 1. Executive Reporting

Generate an HTML report card for stakeholder presentations:

```bash
./py2to3 report-card -f html -o quarterly_migration_report.html
```

The HTML format provides a professional, easy-to-understand visualization of migration quality.

### 2. Quality Gate in CI/CD

Use JSON output to fail builds if quality is below threshold:

```bash
./py2to3 report-card -f json -o report.json

# Parse JSON and check overall grade
python -c "
import json
with open('report.json') as f:
    data = json.load(f)
    grade = data['overall']['grade']
    print(f'Grade: {grade}')
    if grade in ['D', 'F']:
        exit(1)
"
```

### 3. Team Communication

Generate a markdown report for your project documentation:

```bash
./py2to3 report-card -f markdown -o docs/MIGRATION_QUALITY.md
git add docs/MIGRATION_QUALITY.md
git commit -m "Update migration quality report"
```

### 4. Before/After Comparison

Track improvement over time:

```bash
# Before migration work
./py2to3 report-card -f json -o before.json

# ... do migration work ...

# After migration work
./py2to3 report-card -f json -o after.json

# Compare scores
python compare_scores.py before.json after.json
```

### 5. Identifying Weak Areas

Focus your efforts where they're needed most:

```bash
./py2to3 report-card -f text

# Review recommendations and focus on high-severity items
# Work on lowest-scoring categories first
```

## Recommendations System

The report card includes an intelligent recommendations system that provides:

### Severity Levels

- **Critical**: Must be fixed immediately
- **High**: Should be addressed soon
- **Medium**: Important but not urgent
- **Low**: Nice-to-have improvements
- **Info**: Informational messages

### Example Recommendations

```
CRITICAL:
  • [compatibility] Fix 3 critical compatibility issues immediately

HIGH:
  • [test_coverage] Only 8 test files for 10 source files. Add more tests!

MEDIUM:
  • [modernization] Consider using f-strings instead of .format()
  • [code_quality] Add docstrings to modules, classes, and functions
  • [documentation] Add missing documentation: CHANGELOG.md, CONTRIBUTING.md

LOW:
  • [modernization] Consider using pathlib.Path instead of os.path
  • [best_practices] Add a .gitignore file to exclude unnecessary files
```

## Integration with Other Tools

The report card works seamlessly with other py2to3 tools:

### 1. After Running Fixes

```bash
./py2to3 fix src/
./py2to3 report-card
```

### 2. With Preflight Check

```bash
./py2to3 preflight
./py2to3 report-card
```

### 3. Combined with Dashboard

```bash
# Track progress over time
./py2to3 stats collect --save
./py2to3 dashboard

# Assess quality
./py2to3 report-card -f html -o quality_report.html
```

### 4. Before Code Review

```bash
./py2to3 report-card -f markdown > QUALITY_ASSESSMENT.md
./py2to3 review src/ -o CODE_REVIEW.md
```

## Advanced Usage

### Customizing Output

```bash
# Minimal text output
./py2to3 report-card 2>/dev/null | grep "OVERALL GRADE"

# Only show recommendations
./py2to3 report-card | grep -A 100 "RECOMMENDATIONS:"

# Extract overall score for scripting
./py2to3 report-card -f json | python -c "
import json, sys
data = json.load(sys.stdin)
print(data['overall']['score'])
"
```

### Monitoring Quality Over Time

Create a script to track quality trends:

```bash
#!/bin/bash
# track_quality.sh

DATE=$(date +%Y%m%d)
./py2to3 report-card -f json -o "reports/quality_${DATE}.json"

# Store in git
git add "reports/quality_${DATE}.json"
git commit -m "Quality report for ${DATE}"
```

Run regularly (e.g., weekly) to build a quality history.

## Understanding Grades

### Grade Scale

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| A | 90-100 | Excellent - Migration is high quality |
| B | 80-89 | Good - Minor improvements needed |
| C | 70-79 | Satisfactory - Some work required |
| D | 60-69 | Poor - Significant issues to address |
| F | <60 | Failing - Major problems exist |

### What Each Grade Means

**A (90-100): Excellent**
- Minimal compatibility issues
- Good use of modern Python 3 features
- Well-tested and documented
- Ready for production

**B (80-89): Good**
- No critical issues
- Some areas for improvement
- Generally production-ready with minor enhancements

**C (70-79): Satisfactory**
- Migration is functional
- Several improvements needed
- May have some high-priority issues
- Needs work before production

**D (60-69): Poor**
- Multiple serious issues
- Significant gaps in testing or documentation
- Not production-ready
- Requires substantial work

**F (<60): Failing**
- Critical compatibility problems
- Major quality issues
- Substantial migration work needed
- Far from production-ready

## Tips for Improving Your Grade

### To Improve Compatibility Score:
1. Run `./py2to3 check` to identify issues
2. Use `./py2to3 fix` to automatically fix common problems
3. Address critical and high-priority issues first
4. Test thoroughly in Python 3 environment

### To Improve Modernization Score:
1. Use f-strings: `f"Hello {name}"` instead of `"Hello %s" % name`
2. Add type hints to functions
3. Replace `os.path` with `pathlib.Path`
4. Consider using dataclasses for data structures
5. Run `./py2to3 modernize` for automated improvements

### To Improve Code Quality Score:
1. Add docstrings to all modules, classes, and functions
2. Break down large files (>500 lines) into smaller modules
3. Address TODO and FIXME comments
4. Follow PEP 8 naming conventions
5. Run `./py2to3 quality` for detailed analysis

### To Improve Test Coverage Score:
1. Add unit tests for migrated code
2. Aim for at least 1 test file per source file
3. Use `./py2to3 test-gen` to generate test templates
4. Run tests regularly during migration

### To Improve Documentation Score:
1. Create/update README.md
2. Add CHANGELOG.md to track changes
3. Include CONTRIBUTING.md for team guidelines
4. Ensure LICENSE file exists
5. Add migration notes and guides

### To Improve Best Practices Score:
1. Add .gitignore file
2. Create requirements.txt or setup.py
3. Organize tests in a dedicated directory
4. Add configuration files (.py2to3.config.json)
5. Clean up cached .pyc files

## Troubleshooting

### Issue: "Failed to import report card generator"

**Solution:** Ensure you're running from the project root or the src directory is in your Python path:
```bash
cd /path/to/project
./py2to3 report-card
```

### Issue: "Failed to assess compatibility"

**Solution:** Make sure the verifier is available and working:
```bash
./py2to3 check src/
```

### Issue: Scores seem inaccurate

**Explanation:** The report card uses heuristics for quick assessment. For detailed analysis:
- Run `./py2to3 check` for comprehensive compatibility checking
- Use `./py2to3 quality` for in-depth code quality analysis
- Run `pytest --cov` for accurate test coverage

### Issue: No recommendations shown

**Explanation:** If your migration is already high quality, you may receive few or no recommendations. This is a good sign!

## Frequently Asked Questions

**Q: How often should I generate a report card?**

A: Generate report cards at key milestones:
- Before starting migration (baseline)
- After major migration phases
- Before code reviews
- Weekly/monthly for large projects

**Q: Can I customize the grading criteria?**

A: The current version uses fixed criteria. Future versions may support custom weights and thresholds.

**Q: Does the report card modify any code?**

A: No, the report card is read-only. It only analyzes your code and generates reports.

**Q: How does this differ from the regular report command?**

A: The regular `report` command shows *what* was changed during migration. The `report-card` command assesses *how well* the migration was done.

**Q: Can I use this for Python 3 to 3.x upgrades?**

A: Yes! While designed for Python 2→3 migrations, many quality metrics apply to any Python codebase.

## Examples

### Example 1: Quick Assessment

```bash
$ ./py2to3 report-card src/

======================================================================
                PYTHON 2 TO 3 MIGRATION REPORT CARD
======================================================================
Generated: 2024-01-15 14:30:22
Project: src

OVERALL GRADE: B (83.2/100)

...
```

### Example 2: HTML Report for Presentation

```bash
$ ./py2to3 report-card -f html -o migration_quality.html
✓ Report card saved to: migration_quality.html
ℹ Open the HTML file in your browser to view the report card

$ open migration_quality.html  # macOS
$ xdg-open migration_quality.html  # Linux
$ start migration_quality.html  # Windows
```

### Example 3: JSON for CI/CD

```yaml
# .github/workflows/quality-check.yml
- name: Generate Quality Report
  run: ./py2to3 report-card -f json -o quality.json

- name: Check Quality Gate
  run: |
    GRADE=$(python -c "import json; print(json.load(open('quality.json'))['overall']['grade'])")
    if [ "$GRADE" = "F" ] || [ "$GRADE" = "D" ]; then
      echo "Quality grade is too low: $GRADE"
      exit 1
    fi
```

### Example 4: Markdown for Documentation

```bash
$ ./py2to3 report-card -f markdown -o docs/QUALITY.md
$ cat docs/QUALITY.md

# Python 2 to 3 Migration Report Card

**Generated:** 2024-01-15 14:30:22
**Project:** src

## Overall Grade: B
**Score:** 83.2/100

...
```

## Best Practices

1. **Generate a Baseline**: Create a report card before starting migration work
2. **Track Progress**: Generate report cards at regular intervals
3. **Focus on Weakest Areas**: Prioritize improvements in lowest-scoring categories
4. **Share with Team**: Use HTML reports for team meetings and presentations
5. **Automate**: Integrate report card generation into your CI/CD pipeline
6. **Set Quality Gates**: Define minimum acceptable grades for production releases
7. **Document Changes**: Commit markdown reports to track quality over time

## Related Commands

- `./py2to3 check` - Detailed compatibility checking
- `./py2to3 quality` - In-depth code quality analysis
- `./py2to3 report` - Migration progress report
- `./py2to3 status` - Quick status summary
- `./py2to3 dashboard` - Interactive progress dashboard
- `./py2to3 review` - Code review assistance

## Conclusion

The Migration Report Card provides a quick, comprehensive assessment of your migration quality. Use it to:
- Identify areas needing improvement
- Track quality over time
- Communicate progress to stakeholders
- Maintain high standards throughout migration

For questions or issues, refer to the main [README.md](README.md) or other guide documents.
