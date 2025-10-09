# Migration Readiness & Safety Score Guide

## Overview

The **Migration Readiness & Safety Score** feature provides comprehensive assessment tools to help you determine:

1. **Pre-Migration Readiness**: Is your project ready to start the Python 2 to 3 migration?
2. **Post-Migration Production Readiness**: Is your migrated code safe to deploy to production?

Each assessment provides a detailed score, grade, and actionable recommendations to ensure a successful migration.

## Quick Start

```bash
# Check if project is ready to start migration
./py2to3 readiness pre

# Check if migration is complete and ready for production
./py2to3 readiness post

# Run both assessments
./py2to3 readiness both

# Save results to JSON file
./py2to3 readiness pre --output readiness_report.json
```

## Features

### Pre-Migration Readiness Assessment

Evaluates whether your project is prepared to begin migration. Checks include:

#### Version Control (20 points)
- ✓ Git repository initialized
- ✓ Working directory is clean (no uncommitted changes)
- ✓ Remote repository configured for backup
- ✓ .gitignore file exists

#### Backup & Safety (20 points)
- ✓ Backup directory exists
- ✓ Recent backups available
- ✓ Rollback capability configured

#### Testing Infrastructure (25 points)
- ✓ Test suite exists
- ✓ All tests currently pass
- ✓ Test coverage is tracked

#### Project Structure (15 points)
- ✓ Dependencies documented (requirements.txt, setup.py, etc.)
- ✓ Running in virtual environment
- ✓ py2to3 configuration file exists

#### Documentation (10 points)
- ✓ README file exists
- ✓ Documentation directory present

#### Code Quality (10 points)
- ✓ Code is organized in modules
- ✓ No syntax errors in code

**Total: 100 points**

### Post-Migration Production Readiness Assessment

Evaluates whether your migration is complete and safe for production deployment. Checks include:

#### Compatibility (30 points)
- ✓ Python 3 compatibility verified
- ✓ No Python 2 specific imports
- ✓ No Python 2 syntax patterns

#### Testing (25 points)
- ✓ All tests pass with Python 3
- ✓ Test coverage >= 70%
- ✓ Integration tests exist

#### Code Quality (20 points)
- ✓ No code smells (quality score >= 7.0)
- ✓ Type hints added
- ✓ Modern Python 3 features used

#### Documentation (15 points)
- ✓ CHANGELOG updated
- ✓ Migration documented
- ✓ API documentation updated

#### Dependencies (10 points)
- ✓ All dependencies Python 3 compatible
- ✓ No deprecated packages

**Total: 100 points**

## Grading System

The assessment provides both a numeric score and letter grade:

- **A (Excellent)**: 90-100% - Ready to proceed
- **B (Good)**: 80-89% - Minor issues to address
- **C (Fair)**: 70-79% - Several improvements needed
- **D (Poor)**: 60-69% - Significant work required
- **F (Needs Improvement)**: 0-59% - Major preparation needed

## Example Usage

### Example 1: Pre-Migration Check

```bash
$ ./py2to3 readiness pre

================================================================================
  MIGRATION READINESS ASSESSMENT - PRE-MIGRATION
================================================================================

Overall Score: 87/100 (87.0%)
Grade: B (Good)

██████████████████████████████████████████████░░░░ 87.0%

Version Control: 20/20 (100%)
--------------------------------------------------------------------------------
  ✓ Git Repository: Project is in a git repository
  ✓ Clean Working Directory: Git working directory is clean
  ✓ Remote Repository: Remote repository configured
  ✓ .gitignore File: .gitignore file exists

Backup & Safety: 14/20 (70%)
--------------------------------------------------------------------------------
  ✓ Backup Directory: Backup directory exists
  ✓ Recent Backups: Recent backups found
  ✗ Rollback Capability: Rollback system not configured

Testing: 20/25 (80%)
--------------------------------------------------------------------------------
  ✓ Test Suite Exists: Found 15 test files
  ✓ Tests Pass: All tests pass
  ✗ Test Coverage Tracked: Test coverage not tracked

================================================================================
  RECOMMENDATIONS
================================================================================

1. [Backup & Safety] Rollback capability will be available after first migration operation
2. [Testing] Track coverage: pytest --cov=src --cov-report=html

================================================================================
  ✓ READY - Your project is well-prepared!
================================================================================
```

### Example 2: Post-Migration Check

```bash
$ ./py2to3 readiness post

================================================================================
  MIGRATION READINESS ASSESSMENT - POST-MIGRATION
================================================================================

Overall Score: 92/100 (92.0%)
Grade: A (Excellent)

██████████████████████████████████████████████████ 92.0%

Compatibility: 30/30 (100%)
--------------------------------------------------------------------------------
  ✓ Python 3 Compatibility: Code is Python 3 compatible
  ✓ No Python 2 Imports: No Python 2 imports found
  ✓ No Python 2 Syntax: No Python 2 syntax found

Testing: 23/25 (92%)
--------------------------------------------------------------------------------
  ✓ All Tests Pass (Python 3): All tests pass with Python 3
  ✓ Test Coverage >= 70%: Test coverage: 85%
  ✗ Integration Tests Exist: No integration tests found

================================================================================
  ✓ READY - Your project is well-prepared!
================================================================================
```

### Example 3: Both Assessments with JSON Output

```bash
$ ./py2to3 readiness both --output assessment.json

# Runs both pre and post assessments
# Saves pre_assessment.json and post_assessment.json
```

## Understanding the Results

### Color Coding

The progress bar and grade use color coding:
- 🟢 **Green** (80-100%): Ready to proceed
- 🟡 **Yellow** (60-79%): Address some issues first
- 🔴 **Red** (0-59%): Significant work needed

### Check Status

Each individual check shows:
- ✓ **Passed**: Requirement met
- ✗ **Failed**: Needs attention

### Recommendations

Failed checks include actionable recommendations:
```
[Category] Specific action to take
```

Example:
```
[Testing] Track coverage: pytest --cov=src --cov-report=html
[Dependencies] Update dependencies: pip install --upgrade -r requirements.txt
```

## Best Practices

### Before Migration

1. **Achieve at least 80% on pre-migration assessment**
   - Ensures proper safety nets are in place
   - Reduces risk of data loss or broken code

2. **Address all Version Control issues**
   - Critical for rollback capability
   - Essential for team collaboration

3. **Ensure tests pass**
   - Establishes baseline behavior
   - Enables regression detection

### After Migration

1. **Aim for 90%+ on post-migration assessment**
   - Indicates production-ready code
   - Minimizes deployment risks

2. **Must-have: 100% on Compatibility checks**
   - No Python 2 code remaining
   - All imports converted
   - Syntax fully updated

3. **Recommended: 80%+ on Testing**
   - High confidence in code correctness
   - Behavioral compatibility verified

## Integration with CI/CD

You can integrate readiness checks into your CI/CD pipeline:

```yaml
# .github/workflows/migration-readiness.yml
name: Migration Readiness Check

on: [push, pull_request]

jobs:
  assess:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Pre-migration assessment
        run: ./py2to3 readiness pre --output pre.json
      - name: Post-migration assessment
        run: ./py2to3 readiness post --output post.json
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: readiness-reports
          path: |
            pre.json
            post.json
```

## JSON Output Format

When using `--output`, the report is saved in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "assessment_type": "pre-migration",
  "checks": [
    {
      "category": "Version Control",
      "name": "Git Repository",
      "passed": true,
      "score": 5,
      "max_score": 5,
      "message": "Project is in a git repository"
    }
  ],
  "score": 87,
  "max_score": 100,
  "percentage": 87.0,
  "grade": "B (Good)",
  "recommendations": [
    "[Testing] Track coverage: pytest --cov=src --cov-report=html"
  ]
}
```

This format is useful for:
- Automated testing and validation
- Tracking progress over time
- Integration with dashboards and monitoring tools
- Custom analysis and reporting

## Troubleshooting

### "Could not check git status"

**Cause**: Git not installed or not in PATH

**Solution**: Install git and ensure it's accessible:
```bash
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Verify installation
git --version
```

### "Could not run tests"

**Cause**: pytest not installed

**Solution**: Install testing dependencies:
```bash
pip install pytest pytest-cov
```

### "No test files found"

**Cause**: Tests not in expected locations

**Solution**: Create tests or organize them in standard directories:
- `tests/`
- `test/`
- `src/tests/`

Name test files: `test_*.py` or `*_test.py`

### Low Score on First Run

**Cause**: Normal for projects starting migration

**Solution**: Follow recommendations systematically:
1. Fix critical issues (Version Control, Backups)
2. Address testing infrastructure
3. Improve documentation
4. Iterate and re-assess

## Tips for Maximum Score

### Pre-Migration (Checklist)

- [ ] Initialize git repository
- [ ] Commit all changes
- [ ] Add remote repository
- [ ] Create .gitignore
- [ ] Set up virtual environment
- [ ] Document dependencies
- [ ] Write initial tests
- [ ] Ensure tests pass
- [ ] Enable coverage tracking
- [ ] Create README
- [ ] Initialize py2to3 config: `./py2to3 config init`
- [ ] Create first backup: `./py2to3 backup create`

### Post-Migration (Checklist)

- [ ] Run `./py2to3 fix` on all files
- [ ] Verify no Python 2 imports remain
- [ ] Check all tests pass with Python 3
- [ ] Achieve 70%+ test coverage
- [ ] Add integration tests
- [ ] Apply modern Python 3 features: `./py2to3 modernize`
- [ ] Add type hints: `./py2to3 typehints`
- [ ] Update CHANGELOG
- [ ] Document migration process
- [ ] Update API documentation
- [ ] Verify all dependencies compatible
- [ ] Remove deprecated packages

## Related Commands

- `./py2to3 preflight` - Quick pre-migration checks
- `./py2to3 health` - Monitor migration health
- `./py2to3 coverage` - Track test coverage
- `./py2to3 quality` - Analyze code quality
- `./py2to3 validate` - Validate migration completeness
- `./py2to3 report-card` - Comprehensive project report

## When to Use

Use **readiness** assessment:

1. **Before starting migration**
   - Validates project is prepared
   - Identifies missing prerequisites
   - Establishes baseline metrics

2. **Before deploying to production**
   - Confirms migration completeness
   - Verifies production readiness
   - Reduces deployment risk

3. **During code reviews**
   - Objective quality metrics
   - Consistent standards
   - Automated validation

4. **For team communication**
   - Clear progress indicators
   - Stakeholder reporting
   - Shared understanding of status

5. **In CI/CD pipelines**
   - Automated quality gates
   - Continuous validation
   - Prevent regressions

## Conclusion

The Migration Readiness & Safety Score provides:

- ✅ **Objective Metrics**: Quantifiable readiness assessment
- ✅ **Actionable Guidance**: Specific recommendations for improvement
- ✅ **Risk Reduction**: Identifies issues before they cause problems
- ✅ **Confidence Building**: Clear criteria for success
- ✅ **Team Alignment**: Shared understanding of migration status

Use it throughout your migration journey to ensure a successful transition from Python 2 to Python 3!
