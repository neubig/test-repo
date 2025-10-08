# Risk Analyzer Guide

## Overview

The **Risk Analyzer** is a powerful tool that helps you identify and prioritize high-risk changes during Python 2 to 3 migration. After automated fixes are applied, this tool analyzes the changes to determine which files require the most careful manual review, helping teams focus their code review efforts where they matter most.

## Why Use Risk Analysis?

Automated migration tools are great at handling common patterns, but they can't always understand the business logic and criticality of your code. The Risk Analyzer bridges this gap by:

- 🎯 **Prioritizing Review Efforts** - Focus on high-risk changes first
- 🔍 **Identifying Critical Areas** - Spot changes in error handling, I/O, database operations
- 📊 **Quantifying Risk** - Get numerical risk scores based on multiple factors
- 💡 **Providing Recommendations** - Receive actionable guidance for each file
- ⚡ **Accelerating Migration** - Reduce time spent reviewing low-risk changes

## How It Works

The Risk Analyzer compares your fixed code against the backup files created during migration, analyzing:

1. **Change Volume** - More changes = higher risk
2. **Change Categories** - Error handling, I/O, encoding, etc.
3. **Critical Patterns** - Database queries, network operations, file handling
4. **Function Impact** - Changes in frequently-called or critical functions
5. **Code Complexity** - Syntax errors, unparseable code, deep nesting

Each factor is weighted and combined to produce an overall risk score and level for each file.

## Risk Levels

Files are categorized into five risk levels:

| Level | Score Range | Description |
|-------|-------------|-------------|
| 🚨 **CRITICAL** | ≥ 30 | Requires immediate attention from senior developers |
| ⚠️ **HIGH** | 20-29 | Priority review needed before deployment |
| ⚡ **MEDIUM** | 10-19 | Standard thorough review recommended |
| 📝 **LOW** | 5-9 | Light review with existing test suite |
| ✅ **MINIMAL** | < 5 | Standard review process sufficient |

## Risk Categories

The analyzer detects changes in these critical categories:

### High-Impact Categories (Weight: 7-10)
- **Error Handling** (10) - Exception handling, try-except blocks, error raising
- **I/O Operations** (9) - File operations, reading, writing, resource management
- **Database** (9) - SQL queries, database connections, transactions
- **Network** (8) - HTTP requests, socket operations, API calls
- **Logic Changes** (8) - Control flow modifications in critical functions

### Medium-Impact Categories (Weight: 5-7)
- **Encoding** (7) - String encoding/decoding, Unicode handling
- **Type Conversion** (6) - Type checking, casting operations
- **Iterator Changes** (5) - Dictionary iteration, range() usage

### Low-Impact Categories (Weight: 2-3)
- **Imports** (3) - Import statement changes
- **Syntax** (2) - Print statements, syntax modernization

## Usage

### Basic Usage

Analyze risks in your project after running fixes:

```bash
# First, run the fixer to create backups and apply changes
./py2to3 fix src/

# Then analyze the risks
./py2to3 risk src/
```

### Command Options

```bash
./py2to3 risk [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - Path to analyze (default: `src`)

**Options:**
- `-b, --backup-dir DIR` - Backup directory path (default: `backup`)
- `-o, --output FILE` - Save report to file
- `--json` - Output in JSON format
- `-d, --detailed` - Include detailed per-file analysis
- `-h, --help` - Show help message

### Examples

#### 1. Basic Risk Analysis

```bash
./py2to3 risk src/
```

Output shows:
- Overall statistics
- Risk distribution
- High-risk files requiring priority review
- Top 10 files by risk score
- Recommendations

#### 2. Detailed Analysis

Get comprehensive per-file details:

```bash
./py2to3 risk src/ --detailed
```

Includes:
- Risk factors for each file
- Critical areas detected
- Specific recommendations per file
- Function changes

#### 3. Save Report to File

Export for sharing with your team:

```bash
./py2to3 risk src/ -o risk_assessment.txt
```

#### 4. JSON Output for CI/CD

Generate machine-readable output:

```bash
./py2to3 risk src/ --json -o risk_assessment.json
```

Perfect for:
- CI/CD pipeline integration
- Custom reporting tools
- Automated workflows

#### 5. Custom Backup Directory

If your backups are in a different location:

```bash
./py2to3 risk src/ --backup-dir my_backups/
```

## Typical Workflow

### Recommended Process

```bash
# Step 1: Run preflight checks
./py2to3 preflight src/

# Step 2: Apply automated fixes (creates backups)
./py2to3 fix src/

# Step 3: Analyze migration risks
./py2to3 risk src/ -o risk_report.txt

# Step 4: Review high-risk files manually
# Focus on files marked as CRITICAL or HIGH

# Step 5: Run verification
./py2to3 check src/

# Step 6: Run tests
pytest

# Step 7: Generate final report
./py2to3 report -o final_report.html
```

### Team Collaboration Workflow

For teams working on migration together:

```bash
# Create a migration branch
./py2to3 git branch py3-migration

# Run fixes and analyze risks
./py2to3 fix src/
./py2to3 risk src/ -o risk_assessment.txt

# Commit the risk assessment
git add risk_assessment.txt
git commit -m "Add risk assessment for migration"

# Share with team for review assignment
# Assign CRITICAL/HIGH risk files to senior developers
# Assign MEDIUM/LOW risk files to other team members
```

## Understanding the Report

### Sample Output

```
======================================================================
MIGRATION RISK ANALYSIS REPORT
======================================================================

📊 OVERALL STATISTICS
----------------------------------------------------------------------
Files Analyzed: 15
Total Changes: 247 lines
Average Risk Score: 12.3

📈 RISK DISTRIBUTION
----------------------------------------------------------------------
🚨 CRITICAL: 2 files
⚠️  HIGH: 4 files
⚡ MEDIUM: 5 files
📝 LOW: 3 files
✅ MINIMAL: 1 files

🎯 HIGH-RISK FILES (PRIORITY REVIEW)
----------------------------------------------------------------------
  CRITICAL   | Score: 35.0 | Changes:  45 | error_handler.py
  CRITICAL   | Score: 32.0 | Changes:  38 | database.py
  HIGH       | Score: 25.0 | Changes:  30 | file_processor.py
  HIGH       | Score: 22.0 | Changes:  28 | network_client.py

📋 TOP 10 FILES BY RISK SCORE
----------------------------------------------------------------------
 1. error_handler.py (Score: 35.0)
     • Exception handling modified
     • Changes in critical function: handle_exception
 2. database.py (Score: 32.0)
     • Database queries modified
     • Encoding operations changed

💡 RECOMMENDATIONS
----------------------------------------------------------------------
  ⚠️  6 high-risk files require priority review
  🔍 Focus code review efforts on critical and high-risk files first
  🚨 2 CRITICAL risk files need immediate attention
```

### Report Sections Explained

#### 1. Overall Statistics
- **Files Analyzed** - Number of files with detected changes
- **Total Changes** - Total lines modified across all files
- **Average Risk Score** - Mean risk score across all files

#### 2. Risk Distribution
Shows how many files fall into each risk category, giving you an overview of the migration's risk profile.

#### 3. High-Risk Files
Lists all CRITICAL and HIGH-risk files that need priority attention. For each file:
- Risk level
- Numerical risk score
- Number of changed lines
- File name

#### 4. Top Files by Risk Score
Shows the top 10 files with the highest risk scores, along with:
- Primary risk factors
- Changed functions

#### 5. Recommendations
Actionable guidance based on the risk analysis, including:
- Priority review requirements
- Testing recommendations
- Specific checks for detected risk categories

## Recommendations by Risk Category

Based on detected risk categories, the analyzer provides specific recommendations:

### Error Handling Changes
- ✅ Review exception handling logic carefully
- ✅ Test error paths and edge cases
- ✅ Verify exception message compatibility

### Encoding Changes
- ✅ Test with various character encodings (UTF-8, ASCII, etc.)
- ✅ Verify handling of non-ASCII characters
- ✅ Check byte/string boundaries

### I/O Operations
- ✅ Test file operations with different file types and sizes
- ✅ Verify file handling and resource cleanup
- ✅ Check for proper context manager usage

### Database Changes
- ✅ Review database queries and connection handling
- ✅ Test with actual database operations
- ✅ Verify transaction handling

### Iterator Changes
- ✅ Verify iterator behavior matches Python 2 expectations
- ✅ Test with large datasets if applicable
- ✅ Check for performance implications

## Integration with Other Tools

### With Git Integration

```bash
# Create checkpoint before migration
./py2to3 git checkpoint "Pre-migration baseline"

# Apply fixes
./py2to3 fix src/

# Analyze risks and save report
./py2to3 risk src/ -o risk_assessment.txt

# Commit with risk assessment
git add risk_assessment.txt src/
./py2to3 git commit "fixes-applied" -m "Applied Python 3 fixes"
```

### With CI/CD

Add risk analysis to your CI pipeline:

```yaml
# .github/workflows/migration.yml
- name: Analyze Migration Risks
  run: |
    ./py2to3 fix src/ --yes
    ./py2to3 risk src/ --json -o risk_assessment.json

- name: Check for Critical Risks
  run: |
    # Parse JSON and fail if critical risks found
    python -c "
    import json
    with open('risk_assessment.json') as f:
        data = json.load(f)
    critical = data['risk_distribution'].get('critical', 0)
    if critical > 0:
        print(f'❌ Found {critical} critical risk files!')
        exit(1)
    "
```

### With Comparison Tool

Compare risk levels between branches:

```bash
# Check risk in current branch
./py2to3 risk src/ --json -o risk_main.json

# Switch to feature branch
git checkout feature/alternative-migration

# Compare migration approaches
./py2to3 risk src/ --json -o risk_feature.json

# Use comparison tool to see which approach is safer
./py2to3 compare branches main feature/alternative-migration
```

## Best Practices

### 1. Always Run After Fixes
Risk analysis is only useful after fixes have been applied and backups created:

```bash
# ✅ Correct order
./py2to3 fix src/
./py2to3 risk src/

# ❌ Won't work (no backups yet)
./py2to3 risk src/
```

### 2. Focus on High-Risk Files First
Don't try to review everything at once:

```bash
# Generate risk report
./py2to3 risk src/ -o risk_report.txt

# Review CRITICAL files immediately
# Review HIGH files before deployment
# MEDIUM/LOW files can follow standard review process
```

### 3. Use with Test Suite
Risk analysis complements but doesn't replace testing:

```bash
./py2to3 risk src/ -o risk_report.txt

# Write additional tests for high-risk files
pytest tests/ -v

# Pay extra attention to tests for high-risk modules
pytest tests/test_error_handler.py -v
```

### 4. Track Risk Over Time
Monitor how risk changes as you refine your migration:

```bash
# Initial migration
./py2to3 fix src/
./py2to3 risk src/ --json -o risk_v1.json

# After manual fixes
./py2to3 risk src/ --json -o risk_v2.json

# Compare to see if risk decreased
```

### 5. Share Results with Team
Make risk assessments visible to all team members:

```bash
# Generate human-readable report
./py2to3 risk src/ -o risk_assessment.txt

# Commit to repository
git add risk_assessment.txt
git commit -m "Add risk assessment for team review"

# Or share in pull request description
```

## Troubleshooting

### No Changes Detected

**Problem:** Risk analyzer reports 0 files analyzed

**Solutions:**
```bash
# Make sure you ran fix first
./py2to3 fix src/

# Check backup directory exists and has correct path
ls -la backup/

# Specify correct backup directory
./py2to3 risk src/ --backup-dir my_backups/
```

### High Risk Scores for Simple Changes

**Problem:** Files with minor changes show high risk

**Possible causes:**
- Changes are in critical functions (error handlers, DB operations)
- Multiple risk categories triggered
- High volume of changes

**Actions:**
- Review the specific risk factors listed
- Check if the functions changed are indeed critical
- Use detailed mode to see exactly what triggered the risk

### Want to Adjust Risk Thresholds

The risk weights and thresholds are defined in `src/risk_analyzer.py`. You can modify:

```python
# Adjust category weights
CATEGORY_WEIGHTS = {
    ChangeCategory.ERROR_HANDLING: 10.0,  # Increase/decrease as needed
    # ... other categories
}

# Adjust risk level thresholds
def _calculate_risk_level(self, score: float) -> RiskLevel:
    if score >= 30:  # Adjust threshold
        return RiskLevel.CRITICAL
    # ... etc
```

## API Usage

You can also use the Risk Analyzer programmatically:

```python
from risk_analyzer import MigrationRiskAnalyzer

# Initialize analyzer
analyzer = MigrationRiskAnalyzer(
    backup_dir='backup',
    source_dir='src'
)

# Analyze project
summary = analyzer.analyze_project('src/')

# Access results
print(f"Total files: {summary['total_files_analyzed']}")
print(f"High risk files: {len(summary['high_risk_files'])}")

# Get detailed assessments
for assessment in summary['assessments']:
    if assessment['risk_level'] == 'critical':
        print(f"CRITICAL: {assessment['file_path']}")
        print(f"  Score: {assessment['risk_score']}")
        print(f"  Factors: {assessment['risk_factors']}")

# Export to JSON
analyzer.export_json(summary, 'risk_data.json')
```

## FAQ

### Q: When should I run risk analysis?
**A:** After running `py2to3 fix` to apply automated fixes, but before deployment. It's part of your migration review process.

### Q: Can I use this without backups?
**A:** No, the risk analyzer requires backups to compare changes. Run `py2to3 fix` first to create backups.

### Q: What if everything shows high risk?
**A:** This might indicate a complex migration. Consider:
- Breaking migration into smaller chunks
- Focusing on one module at a time
- Using the comparison tool to try different approaches
- Getting additional code review support

### Q: Can I customize risk weights?
**A:** Yes! Edit `src/risk_analyzer.py` and modify the `CATEGORY_WEIGHTS` dictionary to match your project's priorities.

### Q: Does high risk mean the fixes are wrong?
**A:** No! High risk means the changes are significant and need careful review. The automated fixes might be correct, but human verification is essential.

### Q: How does this relate to the verifier?
**A:** 
- **Verifier** - Finds Python 2/3 compatibility issues
- **Fixer** - Applies automated fixes
- **Risk Analyzer** - Identifies which fixes need the most careful review
- **Report Generator** - Documents everything

They work together in the migration workflow.

## Related Documentation

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Backup Guide](BACKUP_GUIDE.md) - Managing backups
- [Git Integration Guide](GIT_INTEGRATION.md) - Version control integration
- [CI/CD Guide](CI_CD_GUIDE.md) - Continuous integration setup
- [Main README](README.md) - Project overview

## Support

If you encounter issues or have questions:

1. Check this guide and related documentation
2. Review the risk analyzer source code: `src/risk_analyzer.py`
3. Open an issue on GitHub
4. Check existing issues for similar problems

## Contributing

Have ideas for improving risk analysis?

- Suggest new risk categories
- Propose weight adjustments
- Add new risk detection patterns
- Improve recommendations

See [Contributing](README.md#contributing) section in the main README.

---

**Remember:** Risk analysis is a tool to help prioritize your review efforts, not a replacement for thorough code review and testing. Always review critical changes manually and maintain comprehensive test coverage!
