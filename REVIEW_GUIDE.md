# Code Review Assistant Guide

The Code Review Assistant is a powerful tool that helps teams review Python 2→3 migration changes more effectively. It analyzes your code, identifies changes that need review, generates checklists, and provides risk assessments.

## Overview

After migrating code from Python 2 to Python 3, the changes need to be reviewed before going to production. The Code Review Assistant automates much of the analysis work, helping reviewers focus on the most critical changes.

### Key Features

- **Automated Change Detection**: Identifies all Python 2→3 migration patterns
- **Risk Assessment**: Categorizes changes by risk level (high, medium, low)
- **Review Checklists**: Generates actionable checklists tailored to your changes
- **Multiple Output Formats**: Markdown, plain text, or JSON
- **PR Descriptions**: Auto-generates pull request descriptions
- **Time Estimates**: Provides estimated review time based on complexity

## Quick Start

### Basic Usage

Analyze a directory and get a review report:

```bash
./py2to3 review src/
```

This will output a comprehensive Markdown report to your terminal with:
- Summary of changes
- Risk breakdown
- Review checklist
- Detailed file-by-file analysis

### Save to File

Save the review report to a file:

```bash
./py2to3 review src/ -o review_report.md
```

### Generate PR Description

Create a pull request description for your migration:

```bash
./py2to3 review src/ --pr
```

This generates a concise PR description perfect for GitHub/GitLab.

## Output Formats

### Markdown Format (Default)

Beautiful, structured reports with emoji indicators:

```bash
./py2to3 review src/ --format markdown -o review.md
```

Best for:
- GitHub/GitLab documentation
- Team wikis
- Readable reports

### Text Format

Plain text format without special formatting:

```bash
./py2to3 review src/ --format text -o review.txt
```

Best for:
- Email reports
- Simple terminals
- Text-only environments

### JSON Format

Machine-readable format for automation:

```bash
./py2to3 review src/ --format json -o review.json
```

Best for:
- CI/CD integration
- Custom tooling
- Data processing

## Understanding the Report

### Summary Section

```markdown
## Summary

- **Files Analyzed:** 46
- **Files Changed:** 40
- **Total Changes:** 1901
- **Critical Items:** 201 ⚠️
- **Estimated Review Time:** 3423 minutes

**Recommendation:** ⚠️ High number of critical changes - recommend thorough review by senior developer
```

The summary gives you a quick overview of:
- How many files were analyzed
- How many files have migration changes
- Total number of changes detected
- Number of critical/high-risk changes
- Estimated time needed for review
- Recommendation for review approach

### Risk Breakdown

Changes are categorized by risk level:

- **🔴 High Risk**: Critical changes that could break functionality
  - Division operations (`/` vs `//`)
  - String/bytes conversions and encoding
  - Metaclass changes
- **🟡 Medium Risk**: Changes that should be reviewed carefully
  - Import statement changes
  - File operations (text vs binary mode)
  - String type handling
- **🟢 Low Risk**: Safe changes that just need quick verification
  - Print statement syntax
  - Exception handling syntax
  - Range usage

### Review Checklist

A prioritized list of items to verify:

```markdown
## Review Checklist

- [ ] 🔴 **General**: All tests pass after migration
- [ ] 🔴 **General**: Code runs without warnings under Python 3
- [ ] 🟡 **General**: All imports work correctly
- [ ] 🔴 **Division**: Verify integer division behavior (/ vs //)
- [ ] 🔴 **Strings**: Check all string/bytes conversions
```

The checklist is automatically customized based on what changes were detected in your code.

### Detailed Changes

File-by-file breakdown showing:
- Which files have changes
- Risk counts per file
- Specific lines of code that changed
- Review notes for each change type
- Examples of the actual code

```markdown
### src/example.py

- High risk: 5, Medium risk: 10, Low risk: 20

**🔴 Division** (5 occurrences)
- Review: CRITICAL: Verify division behavior (/ vs //) is correct
  - Line 42: `result = total / count`
  - Line 58: `percentage = numerator / denominator`
```

## Use Cases

### 1. Pre-Merge Review

Before merging a migration PR:

```bash
# Generate comprehensive review report
./py2to3 review src/ -o MIGRATION_REVIEW.md

# Share with team for review
git add MIGRATION_REVIEW.md
git commit -m "Add migration review report"
git push
```

### 2. Pull Request Creation

When creating a PR for your migration:

```bash
# Generate PR description
./py2to3 review src/ --pr > pr_description.txt

# Use the output to create your PR
# (Copy pr_description.txt content to GitHub PR)
```

### 3. Code Review Checklist

During code review:

```bash
# Generate checklist for reviewer
./py2to3 review src/ --format text -o checklist.txt

# Reviewer uses checklist to verify changes
```

### 4. CI/CD Integration

Automated review reports in CI:

```bash
# In your CI pipeline
./py2to3 review src/ --format json -o review.json

# Process the JSON output
# Post to PR as comment
# Check for critical issues
```

### 5. Batch Review

Reviewing multiple modules:

```bash
# Review each module separately
./py2to3 review src/module1/ -o reviews/module1.md
./py2to3 review src/module2/ -o reviews/module2.md
./py2to3 review src/module3/ -o reviews/module3.md

# Or review everything at once
./py2to3 review src/ -o reviews/full_review.md
```

## Integration with Other Tools

### With Git Integration

Combine with git commands for branch-specific reviews:

```bash
# Create migration branch
./py2to3 git branch py3-migration

# Apply fixes
./py2to3 fix src/

# Generate review report
./py2to3 review src/ -o REVIEW.md

# Commit with review report
git add .
git commit -m "Python 3 migration with review report"
```

### With Migration Dashboard

Track review progress over time:

```bash
# Generate review report
./py2to3 review src/ --format json -o current_review.json

# Collect stats
./py2to3 stats collect --save

# Update dashboard
./py2to3 dashboard
```

### With CI/CD Workflows

Add to your GitHub Actions:

```yaml
- name: Generate Review Report
  run: |
    ./py2to3 review src/ --format markdown -o review_report.md
    
- name: Upload Review Report
  uses: actions/upload-artifact@v3
  with:
    name: review-report
    path: review_report.md

- name: Comment on PR
  run: |
    ./py2to3 review src/ --pr > pr_comment.txt
    # Use GitHub API to post comment
```

## Command Reference

### Main Command

```bash
py2to3 review <path> [options]
```

### Options

| Option | Description |
|--------|-------------|
| `path` | File or directory to analyze (required) |
| `-f, --format {markdown,text,json}` | Output format (default: markdown) |
| `-o, --output FILE` | Save report to file (default: stdout) |
| `--pr` | Generate PR description instead of full report |

### Examples

```bash
# Basic analysis
py2to3 review src/

# Save markdown report
py2to3 review src/ -o review.md

# Generate text report
py2to3 review src/ --format text -o review.txt

# Export JSON for automation
py2to3 review src/ --format json -o review.json

# Create PR description
py2to3 review src/ --pr -o pr_description.txt

# Analyze single file
py2to3 review src/mymodule.py

# Combine with other commands
py2to3 fix src/ && py2to3 review src/ -o review.md
```

## Tips and Best Practices

### 1. Review High-Risk Changes First

Focus on high-risk changes:
- Division operations
- String/bytes conversions
- Metaclass modifications

These are most likely to cause runtime issues.

### 2. Use with Version Control

Generate review reports as part of your git workflow:

```bash
# Before migration
./py2to3 review src/ -o pre_migration_review.md

# After migration
./py2to3 fix src/
./py2to3 review src/ -o post_migration_review.md

# Compare reports
diff pre_migration_review.md post_migration_review.md
```

### 3. Share Reports with Team

Make review reports part of your documentation:
- Add to PR descriptions
- Include in team wikis
- Share in code review tools
- Use as training materials

### 4. Customize Review Process

Different projects need different review approaches:

**Small Projects:**
```bash
# Quick single-pass review
./py2to3 review src/ --pr
```

**Large Projects:**
```bash
# Module-by-module review
for module in src/*/; do
  ./py2to3 review "$module" -o "reviews/$(basename $module).md"
done
```

**Critical Projects:**
```bash
# Full detailed review with all formats
./py2to3 review src/ -o review.md
./py2to3 review src/ --format json -o review.json
./py2to3 review src/ --pr -o pr_description.txt
```

### 5. Automate in CI/CD

Add review checks to your pipeline:

```bash
#!/bin/bash
# In .github/workflows or CI config

# Generate review report
./py2to3 review src/ --format json -o review.json

# Check for critical issues
critical_count=$(jq '.high_risk_changes' review.json)

if [ "$critical_count" -gt 10 ]; then
  echo "Too many critical changes: $critical_count"
  exit 1
fi
```

## Understanding Risk Levels

### High Risk (🔴) - Requires Careful Review

**Division Operations:**
- Python 2: `3 / 2 = 1` (integer division)
- Python 3: `3 / 2 = 1.5` (float division)
- Check: Verify `/` vs `//` usage

**String/Bytes Conversions:**
- Python 2: Strings and bytes are mixed
- Python 3: Strict str/bytes separation
- Check: All encode/decode operations

**Metaclasses:**
- Syntax changed significantly
- Complex inheritance implications
- Check: Verify metaclass behavior

### Medium Risk (🟡) - Should Review

**Import Changes:**
- Module renames (urllib2 → urllib.request)
- API differences between versions
- Check: Verify imports work correctly

**File Operations:**
- Text vs binary mode handling
- Default encodings changed
- Check: Verify open() calls

**String Type Handling:**
- basestring removed
- unicode type removed
- Check: Type checking code

### Low Risk (🟢) - Quick Verification

**Print Statements:**
- Syntax change only
- Usually safe conversion
- Check: Verify file parameter usage

**Exception Handling:**
- Syntax change (`except E, e:` → `except E as e:`)
- Logic unchanged
- Check: Quick verification

**Dictionary Methods:**
- .keys()/.values()/.items() now return views
- Usually compatible
- Check: Verify list conversion if needed

## Troubleshooting

### Report Shows No Changes

If your code is already Python 3 compatible:
```bash
✓ No significant changes detected
```

This is good! Your code may already be compatible.

### Too Many False Positives

The tool uses pattern matching and may flag some safe constructs. Review the actual code to verify.

### Large Estimated Review Time

For large codebases:
- Break into modules
- Focus on high-risk changes first
- Spread review across team

### Missing Expected Changes

The tool detects common patterns. Some edge cases may not be detected. Always combine automated review with manual code inspection.

## Advanced Usage

### Programmatic Access

Use the module directly in Python:

```python
from review_assistant import MigrationReviewAssistant

assistant = MigrationReviewAssistant()
analysis = assistant.analyze_changes('src/')

print(f"Found {analysis['summary']['total_changes']} changes")
print(f"Critical: {analysis['high_risk_changes']}")

# Generate custom report
report = assistant.generate_report(analysis, 'markdown')
print(report)
```

### Custom Report Processing

Process JSON output:

```bash
# Generate JSON
./py2to3 review src/ --format json -o review.json

# Extract critical files
jq '.files[] | select(.high_risk_count > 5)' review.json

# Count changes by type
jq '[.files[].changes[].type] | group_by(.) | map({type: .[0], count: length})' review.json
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Git Integration Guide](GIT_INTEGRATION.md) - Version control integration
- [CI/CD Guide](CI_CD_GUIDE.md) - Continuous integration setup
- [Migration Planner](PLANNER_GUIDE.md) - Planning your migration
- [Risk Analyzer](RISK_GUIDE.md) - Risk assessment

## Contributing

Found an issue or want to add new review patterns? Contributions are welcome!

- Add new change patterns to `CHANGE_PATTERNS` in `review_assistant.py`
- Improve risk categorization
- Add new checklist items
- Enhance report formatting

## License

This tool is part of the py2to3 migration toolkit and is available under the MIT License.
