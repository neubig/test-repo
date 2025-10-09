# Coverage Tracker Guide

## Overview

The **Coverage Tracker** is a powerful feature that helps you monitor test coverage during your Python 2 to 3 migration. It integrates seamlessly with popular coverage tools (coverage.py, pytest-cov) to help you identify risky migrations and ensure code quality throughout the migration process.

## Why Track Coverage During Migration?

When migrating Python 2 code to Python 3, it's critical to maintain or improve test coverage because:

- **Risk Mitigation**: Files with low test coverage are risky to migrate - bugs might be introduced and not caught
- **Quality Assurance**: Good test coverage ensures migrated code works correctly
- **Confidence Building**: High coverage gives you confidence that your migration is safe
- **Regression Prevention**: Tests catch issues introduced during migration
- **Documentation**: Tests serve as living documentation of expected behavior

## Installation

The coverage tracker works with standard Python testing tools. Install the required dependencies:

```bash
# Install pytest and coverage tools
pip install pytest pytest-cov coverage

# Or if using the project's requirements
pip install -r requirements.txt
```

## Quick Start

### 1. Collect Coverage Data

Run your tests with coverage collection:

```bash
# Auto-detect test configuration and run tests
./py2to3 coverage collect

# With a custom description
./py2to3 coverage collect --description "Before migration baseline"

# With a custom test command
./py2to3 coverage collect --test-command "pytest --cov=src --cov-report=json"
```

### 2. View Coverage Report

Generate a detailed coverage report:

```bash
# Display report in terminal
./py2to3 coverage report

# Save report to file
./py2to3 coverage report -o coverage_report.txt
```

### 3. Identify Risky Files

Find files with low coverage that need attention:

```bash
# Show files below 50% coverage (default threshold)
./py2to3 coverage risky

# Use a custom threshold
./py2to3 coverage risky --threshold 70
```

### 4. Track Coverage Trends

Monitor how coverage changes over time:

```bash
# Show coverage history with color-coded trends
./py2to3 coverage trend
```

## Detailed Usage

### Collecting Coverage Snapshots

The `collect` command runs your tests with coverage instrumentation and saves a snapshot:

```bash
./py2to3 coverage collect [OPTIONS]
```

**Options:**
- `--path PATH` - Project directory (default: current directory)
- `--description TEXT` - Description for this snapshot (helps track context)
- `--test-command CMD` - Custom test command to run

**What it does:**
1. Runs your test suite with coverage collection
2. Parses the generated `coverage.json` file
3. Analyzes coverage metrics for each file
4. Saves a timestamped snapshot
5. Reports overall statistics

**Example Workflow:**

```bash
# Collect baseline before migration
./py2to3 coverage collect --description "Pre-migration baseline"

# Apply some fixes
./py2to3 fix src/

# Collect coverage after fixes
./py2to3 coverage collect --description "After print statement fixes"

# Continue migration...
./py2to3 fix src/ --pattern import
./py2to3 coverage collect --description "After import fixes"
```

### Generating Coverage Reports

The `report` command creates a detailed coverage analysis:

```bash
./py2to3 coverage report [OPTIONS]
```

**Options:**
- `--path PATH` - Project directory
- `-o, --output FILE` - Save report to file

**Report Contents:**
- Overall coverage percentage
- Total files, statements, covered, and missing counts
- List of low coverage files (< 50%)
- List of uncovered files (0%)
- Coverage trend over time
- Improvement/decline indicators

**Example:**

```bash
# View in terminal
./py2to3 coverage report

# Save to file
./py2to3 coverage report -o reports/coverage_analysis.txt
```

### Viewing Coverage Trends

Track how coverage evolves throughout your migration:

```bash
./py2to3 coverage trend [OPTIONS]
```

**Options:**
- `--path PATH` - Project directory

**Features:**
- Chronological list of all snapshots
- Color-coded coverage percentages (green ≥80%, yellow ≥50%, red <50%)
- File counts for each snapshot
- Snapshot descriptions for context
- Trend direction indicator (improving/declining/stable)

**Example Output:**

```
Coverage Trend:
----------------------------------------------------------------------
2024-01-15 10:30:00  45.2%  (25 files)  Pre-migration baseline
2024-01-15 11:15:00  52.1%  (25 files)  After print statement fixes
2024-01-15 14:20:00  58.3%  (25 files)  After import fixes
2024-01-15 16:45:00  64.7%  (25 files)  After iterator fixes

✓ Coverage improved by 6.4%
```

### Identifying Risky Migrations

Find files that need more tests before migration:

```bash
./py2to3 coverage risky [OPTIONS]
```

**Options:**
- `--path PATH` - Project directory
- `--threshold PERCENT` - Coverage threshold for risk (default: 50%)

**Risk Categories:**
- **Critical (0% coverage)** - No tests at all, very high risk
- **High (< 25% coverage)** - Very little test coverage
- **Medium (25-50% coverage)** - Some coverage but below recommended

**Recommendations:**
1. Run `./py2to3 test-gen` to generate test templates for risky files
2. Write additional tests before migrating these files
3. Consider breaking large untested files into smaller modules
4. Use `./py2to3 quality` to assess complexity (complex + untested = very risky)

**Example:**

```bash
# Find all files below 50% coverage
./py2to3 coverage risky

# Be more strict - find files below 70%
./py2to3 coverage risky --threshold 70
```

### Clearing Coverage History

Remove all coverage snapshots to start fresh:

```bash
./py2to3 coverage clear [OPTIONS]
```

**Options:**
- `--path PATH` - Project directory

**Use cases:**
- Starting a new migration phase
- Cleaning up after completed migration
- Removing outdated historical data

## Integration with Migration Workflow

### Recommended Workflow

1. **Pre-Migration Baseline**
   ```bash
   # Collect initial coverage
   ./py2to3 coverage collect --description "Pre-migration baseline"
   
   # Identify risky files
   ./py2to3 coverage risky
   
   # Generate tests for risky files
   ./py2to3 test-gen src/risky_file.py
   ```

2. **During Migration**
   ```bash
   # After each fix session
   ./py2to3 fix src/ --pattern print
   ./py2to3 coverage collect --description "After print fixes"
   
   # Check if coverage dropped
   ./py2to3 coverage trend
   
   # Address any new risky areas
   ./py2to3 coverage risky
   ```

3. **Post-Migration Verification**
   ```bash
   # Final coverage check
   ./py2to3 coverage collect --description "Post-migration final"
   
   # Generate comprehensive report
   ./py2to3 coverage report -o final_coverage_report.txt
   
   # Ensure no regressions
   ./py2to3 coverage trend
   ```

### Integration with Other Commands

The coverage tracker works great with other py2to3 commands:

```bash
# Use with risk analyzer
./py2to3 coverage risky > low_coverage.txt
./py2to3 risk src/ --focus-files low_coverage.txt

# Use with quality analyzer
./py2to3 coverage risky --threshold 70
./py2to3 quality src/ --complexity

# Use with test generator
./py2to3 coverage risky | grep "0.0%" | awk '{print $2}' | \
  xargs -I {} ./py2to3 test-gen {}

# Use with interactive fixer (for risky files)
./py2to3 coverage risky
./py2to3 interactive src/risky_file.py
```

## Best Practices

### 1. Collect Baseline Early
Always collect a baseline before starting migration:
```bash
./py2to3 coverage collect --description "Pre-migration baseline"
```

### 2. Regular Snapshots
Take snapshots after each major fix session:
```bash
./py2to3 fix src/
./py2to3 coverage collect --description "After [fix type] fixes"
```

### 3. Address Low Coverage First
Prioritize adding tests to low-coverage files before migrating them:
```bash
./py2to3 coverage risky --threshold 50
# Add tests to these files first
./py2to3 test-gen src/low_coverage_file.py
```

### 4. Monitor Trends
Regularly check coverage trends to ensure you're not losing coverage:
```bash
./py2to3 coverage trend
```

### 5. Set Coverage Goals
Aim to maintain or improve coverage throughout migration:
- Pre-migration: Establish baseline
- During migration: Don't let coverage drop
- Post-migration: Aim for improvement

### 6. Use with CI/CD
Integrate coverage tracking into your CI/CD pipeline:
```yaml
# Example GitHub Actions workflow
- name: Collect Coverage
  run: |
    ./py2to3 coverage collect --description "CI run ${{ github.run_number }}"
    ./py2to3 coverage report
```

## Advanced Usage

### Custom Test Commands

If your project uses a non-standard test setup:

```bash
# Django projects
./py2to3 coverage collect --test-command "python manage.py test --with-coverage"

# Tox environments
./py2to3 coverage collect --test-command "tox -e py3 -- --cov"

# Custom pytest configuration
./py2to3 coverage collect --test-command "pytest tests/ --cov=myapp --cov-config=.coveragerc"
```

### Combining with Migration State

Track which files have been migrated and their coverage:

```bash
# Get migration state
./py2to3 state show > migrated_files.txt

# Get coverage for those files
./py2to3 coverage risky
```

### Scripting and Automation

Use coverage commands in scripts:

```bash
#!/bin/bash
# migration_with_coverage.sh

echo "Collecting baseline..."
./py2to3 coverage collect --description "Before $1 fixes"

echo "Applying fixes..."
./py2to3 fix src/ --pattern "$1"

echo "Collecting post-fix coverage..."
./py2to3 coverage collect --description "After $1 fixes"

echo "Checking for regressions..."
./py2to3 coverage trend
```

Usage:
```bash
./migration_with_coverage.sh print
./migration_with_coverage.sh import
./migration_with_coverage.sh iterator
```

## Troubleshooting

### No Coverage Data Collected

**Problem**: `Could not run coverage` error

**Solutions**:
1. Install pytest-cov: `pip install pytest-cov`
2. Verify tests exist and can run: `pytest`
3. Try a custom test command: `./py2to3 coverage collect --test-command "pytest --cov=src"`

### Coverage.json Not Found

**Problem**: Tests run but no coverage data

**Solutions**:
1. Ensure `--cov-report=json` flag is used
2. Check if `.coverage` file exists, run: `coverage json`
3. Verify coverage.py is installed: `pip install coverage`

### No Snapshots Available

**Problem**: `No coverage snapshots available` when running report/trend

**Solution**:
Run `./py2to3 coverage collect` first to create initial snapshot

### Tests Fail During Collection

**Problem**: Tests fail, preventing coverage collection

**Solutions**:
1. Fix test failures first: `pytest`
2. Skip failing tests temporarily: `pytest --ignore=failing_test.py`
3. Use `--test-command` to customize test execution

## Tips and Tricks

### Quick Coverage Check
```bash
# One-liner to collect and report
./py2to3 coverage collect && ./py2to3 coverage report
```

### Find Untested Files
```bash
# Get files with 0% coverage
./py2to3 coverage risky | grep "0.0%"
```

### Coverage Goals
```bash
# Check if coverage is above target
./py2to3 coverage report | grep "Overall Coverage" | \
  awk '{if ($3 < 80) exit 1}'
```

### Compare with Baseline
```bash
# Save baseline
./py2to3 coverage collect --description "Baseline"
./py2to3 coverage report > baseline_coverage.txt

# After migration
./py2to3 coverage collect --description "After migration"
./py2to3 coverage report > final_coverage.txt

# Compare
diff baseline_coverage.txt final_coverage.txt
```

## Related Commands

- `./py2to3 test-gen` - Generate unit tests for files
- `./py2to3 quality` - Analyze code quality and complexity
- `./py2to3 risk` - Analyze migration risks
- `./py2to3 validate` - Validate Python 3 code by running it
- `./py2to3 bench` - Benchmark performance (another quality metric)

## Summary

The Coverage Tracker helps you:
- ✅ Identify risky migrations before they happen
- ✅ Track coverage trends throughout migration
- ✅ Ensure code quality is maintained or improved
- ✅ Build confidence in your migration process
- ✅ Create a safety net for catching regressions

**Key Commands:**
```bash
./py2to3 coverage collect    # Collect coverage snapshot
./py2to3 coverage report     # View detailed report
./py2to3 coverage trend      # Show coverage over time
./py2to3 coverage risky      # Find low-coverage files
./py2to3 coverage clear      # Clear coverage history
```

**Remember**: Good test coverage is one of the best predictors of a successful, safe migration!
