# Migration Health Monitor Guide

The **Migration Health Monitor** provides a comprehensive health score and monitoring dashboard for tracking your Python 2 to 3 migration progress. It gives you a single metric (0-100) to communicate status to stakeholders while providing actionable recommendations for improvement.

## Overview

The Health Monitor analyzes your migration across six key dimensions:

1. **Compatibility** (30% weight) - Python 3 compatibility issues
2. **Code Quality** (20% weight) - Overall code quality metrics
3. **Test Coverage** (15% weight) - Test presence and coverage
4. **Risk Level** (20% weight) - Migration safety measures
5. **Progress** (10% weight) - Migration completion status
6. **Backup & Safety** (5% weight) - Backup and rollback readiness

Each dimension receives a score (0-100) and status (excellent/good/warning/critical), combined into an overall weighted health score.

## Quick Start

### Basic Usage

Check your migration health:

```bash
./py2to3 health
```

This will:
- Analyze all six health dimensions
- Calculate an overall health score
- Provide status for each dimension
- List prioritized recommendations
- Save results to history for trend tracking

### Check Specific Directory

```bash
./py2to3 health src/
```

### View Detailed Recommendations

```bash
./py2to3 health -v
```

Shows detailed recommendations for each dimension, not just top-priority items.

### Track Trends Over Time

```bash
./py2to3 health --trend 7
```

Shows health trend analysis for the last 7 days, including:
- Number of measurements
- Average, min, and max scores
- Overall improvement/decline
- Trend direction

### Save JSON Report

```bash
./py2to3 health -o health_report.json
```

Save detailed JSON report for further analysis or CI/CD integration.

## Understanding Health Scores

### Overall Score Ranges

- **90-100** 🟢 **Excellent** - Migration is in great shape
- **75-89** 🟡 **Good** - Minor improvements needed
- **50-74** 🟠 **Warning** - Significant work required
- **0-49** 🔴 **Critical** - Immediate attention needed

### Health Dimensions Explained

#### 1. Compatibility (30% weight)

Measures Python 3 compatibility by detecting Python 2 patterns:

- Print statements without parentheses
- Old import modules (urllib2, ConfigParser, etc.)
- Dictionary methods (.iteritems(), .iterkeys())
- xrange() instead of range()
- Old-style exception syntax

**High Impact**: This is weighted most heavily because incompatible code won't run on Python 3.

**Recommendations**:
- Score 90+: Continue monitoring
- Score 70-89: Run `./py2to3 fix` for automated fixes
- Score 40-69: Run preflight check, then apply fixes carefully
- Score <40: Create backup, run preflight, plan incremental migration

#### 2. Code Quality (20% weight)

Evaluates overall code quality:

- File size (flags files >500 lines)
- Function complexity (flags functions >20 statements)
- Average file size
- Code organization

**Recommendations**:
- Consider splitting large files
- Refactor complex functions
- Maintain consistent code organization

#### 3. Test Coverage (15% weight)

Estimates test coverage by comparing test files to source files:

- Counts test files (test_*.py, *_test.py, tests.py)
- Compares to source file count
- Provides rough coverage estimate

**Recommendations**:
- Ratio ≥0.8: Excellent coverage
- Ratio 0.5-0.8: Good, add more tests
- Ratio 0.2-0.5: Needs improvement
- Ratio <0.2: Critical - generate baseline tests

Generate tests with: `./py2to3 test-gen`

#### 4. Risk Level (20% weight)

Assesses migration safety measures:

- Backup directory presence
- Git repository existence
- Uncommitted changes
- Configuration file
- Documentation

**Recommendations**:
- No backups: `./py2to3 backup create`
- No git: `git init`
- Uncommitted changes: Commit before migration
- No config: `./py2to3 config init`

#### 5. Progress (10% weight)

Tracks migration completion:

- Reads migration state from `.migration_state.json`
- Falls back to detecting Python 2 patterns
- Estimates completion percentage

**Recommendations**:
- Track with: `./py2to3 state show`
- Update progress: `./py2to3 stats collect`
- Plan remaining work: `./py2to3 plan`

#### 6. Backup & Safety (5% weight)

Verifies backup and safety infrastructure:

- Backup directory and backup count
- Rollback history
- Version control

**Recommendations**:
- Ensure backups exist before major changes
- Use git for additional safety
- Test rollback procedures: `./py2to3 rollback preview`

## Common Workflows

### Initial Health Check

Before starting migration:

```bash
# Check initial health
./py2to3 health -v

# Address critical issues first (usually backups and git)
./py2to3 backup create
git init && git add . && git commit -m "Initial commit"

# Run preflight check
./py2to3 preflight

# Check health again
./py2to3 health
```

### During Migration

Track health regularly:

```bash
# After each fix session
./py2to3 fix src/module1/
./py2to3 health

# Save detailed report
./py2to3 health -o reports/health_$(date +%Y%m%d).json

# Check trend
./py2to3 health --trend 7
```

### Weekly Status Report

Generate status for team/stakeholders:

```bash
# Generate comprehensive report
./py2to3 health -v > weekly_health_report.txt

# Show trend analysis
./py2to3 health --trend 7

# Generate dashboard
./py2to3 dashboard
```

### CI/CD Integration

Integrate health checks into your pipeline:

```bash
# Run health check and save JSON
./py2to3 health -o health.json

# Exit codes:
# 0 = Health ≥70 (good)
# 1 = Health 50-69 (warning)
# 2 = Health <50 (critical)
```

Example GitHub Actions workflow:

```yaml
- name: Check Migration Health
  run: |
    ./py2to3 health -o health.json
    
- name: Upload Health Report
  uses: actions/upload-artifact@v3
  with:
    name: health-report
    path: health.json
    
- name: Comment on PR
  if: github.event_name == 'pull_request'
  run: |
    SCORE=$(jq -r '.overall_score' health.json)
    STATUS=$(jq -r '.overall_status' health.json)
    echo "Migration Health: $SCORE/100 ($STATUS)" >> $GITHUB_STEP_SUMMARY
```

## Advanced Usage

### Historical Tracking

Health data is automatically saved to `.py2to3_health_history.json` (last 100 measurements).

View historical data:

```bash
# Show trend for different periods
./py2to3 health --trend 1   # Last day
./py2to3 health --trend 7   # Last week
./py2to3 health --trend 30  # Last month

# Disable history saving
./py2to3 health --no-history
```

### Custom Scripts

Use health monitor in custom scripts:

```python
from health_monitor import MigrationHealthMonitor

# Create monitor
monitor = MigrationHealthMonitor('.')

# Analyze health
report = monitor.analyze()

# Check score
if report['overall_score'] < 70:
    print("Health below threshold!")
    
# Get recommendations
for rec in report['recommendations']:
    if rec['priority'] == 'critical':
        print(f"CRITICAL: {rec['recommendation']}")

# Get trend
trend = monitor.get_trend_analysis(days=7)
if trend['available']:
    print(f"Trend: {trend['trend']}")
    print(f"Improvement: {trend['improvement']:+.1f}")
```

### Programmatic Analysis

```python
from health_monitor import MigrationHealthMonitor, format_health_report

# Analyze multiple projects
projects = ['project1/', 'project2/', 'project3/']
results = {}

for project in projects:
    monitor = MigrationHealthMonitor(project)
    results[project] = monitor.analyze(save_history=False)

# Compare scores
for project, report in results.items():
    print(f"{project}: {report['overall_score']}/100")

# Find lowest scoring dimension across all projects
all_dimensions = {}
for project, report in results.items():
    for dim in report['dimensions']:
        dim_name = dim['name']
        if dim_name not in all_dimensions:
            all_dimensions[dim_name] = []
        all_dimensions[dim_name].append(dim['score'])

for dim_name, scores in all_dimensions.items():
    avg_score = sum(scores) / len(scores)
    print(f"{dim_name} average: {avg_score:.1f}")
```

## Interpreting Recommendations

Recommendations are prioritized by impact:

### 🔴 Critical Priority

These prevent migration or pose high risk:
- No backups
- No version control
- Very low test coverage
- Many compatibility issues

**Action**: Address immediately before proceeding.

### 🟠 High Priority

These significantly impact migration success:
- Uncommitted changes
- Missing configuration
- Moderate compatibility issues

**Action**: Address in current sprint.

### 🟢 Normal Priority

These improve migration quality:
- Code quality improvements
- Documentation updates
- Additional test coverage

**Action**: Plan for upcoming work.

## Best Practices

### 1. Check Health Regularly

Run health checks:
- Before starting migration (baseline)
- After each major fix session
- Daily during active migration
- Weekly during maintenance

### 2. Track Trends

Monitor trends to:
- Ensure continuous improvement
- Detect regressions early
- Estimate completion time
- Demonstrate progress

### 3. Set Health Goals

Define health targets:
- Start: Establish baseline
- Week 1: Reach 50+ (warning → good)
- Week 2: Reach 70+ (good)
- Week 3: Reach 85+ (good → excellent)
- Completion: Maintain 90+ (excellent)

### 4. Use with Other Tools

Combine with complementary tools:

```bash
# Full workflow
./py2to3 health              # Check current health
./py2to3 preflight           # Verify environment
./py2to3 plan                # Plan work
./py2to3 fix src/            # Apply fixes
./py2to3 health              # Check improvement
./py2to3 dashboard           # Visualize progress
```

### 5. Communicate with Stakeholders

Use health score for clear communication:
- **Executives**: "We're at 75/100 health, on track"
- **Team**: Show detailed dimensions and recommendations
- **Retrospectives**: Compare trends week-over-week

### 6. CI/CD Integration

Enforce health standards:

```yaml
# Fail build if health drops
- name: Enforce Health
  run: |
    ./py2to3 health -o health.json
    SCORE=$(jq -r '.overall_score' health.json)
    if [ "$SCORE" -lt 70 ]; then
      echo "Health score too low: $SCORE"
      exit 1
    fi
```

## Troubleshooting

### "Could not analyze X"

Usually indicates:
- Missing dependencies
- File permission issues
- Corrupted files

**Solution**: Check error details with `-v` flag.

### Unexpected Low Score

If a dimension scores unexpectedly low:
1. Run with `-v` to see details
2. Check the dimension's details field
3. Review recommendations
4. Verify files are accessible

### No Historical Trend Data

Trends require at least 2 measurements:
- Run health checks regularly
- Data is saved to `.py2to3_health_history.json`
- History kept for last 100 measurements

### Score Not Improving

If health score stays low despite fixes:
1. Verify fixes were applied: `git diff`
2. Check all dimensions: `./py2to3 health -v`
3. Focus on high-weight dimensions (Compatibility, Risk)
4. Ensure backups and git are set up

## Integration Examples

### Slack Notifications

```bash
#!/bin/bash
# health-check-notify.sh

./py2to3 health -o health.json

SCORE=$(jq -r '.overall_score' health.json)
STATUS=$(jq -r '.overall_status' health.json)
TREND=$(jq -r '.trend' health.json)

curl -X POST -H 'Content-type: application/json' \
  --data "{
    \"text\": \"Migration Health: $SCORE/100 ($STATUS) - Trend: $TREND\"
  }" \
  $SLACK_WEBHOOK_URL
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run health check
./py2to3 health --no-history -o /tmp/health.json

SCORE=$(jq -r '.overall_score' /tmp/health.json)

if [ "$SCORE" -lt 50 ]; then
  echo "⚠️  Migration health is critical: $SCORE/100"
  echo "Consider addressing health issues before committing."
  echo "Run: ./py2to3 health -v"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi
```

### Daily Health Report

```bash
#!/bin/bash
# daily-health-report.sh

DATE=$(date +%Y-%m-%d)
REPORT_FILE="reports/health_$DATE.txt"

echo "Migration Health Report - $DATE" > $REPORT_FILE
echo "================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

./py2to3 health -v >> $REPORT_FILE
./py2to3 health --trend 7 >> $REPORT_FILE

# Email report (requires mail command)
mail -s "Daily Migration Health Report - $DATE" \
  team@example.com < $REPORT_FILE
```

## API Reference

### MigrationHealthMonitor

```python
class MigrationHealthMonitor:
    def __init__(self, project_path: str)
    def analyze(self, save_history: bool = True) -> Dict
    def get_trend_analysis(self, days: int = 7) -> Dict
```

### Report Structure

```python
{
    "overall_score": 75.5,           # 0-100
    "overall_status": "good",         # excellent/good/warning/critical
    "trend": "improving",             # improving/stable/declining
    "trend_value": 5.2,              # Change from previous
    "timestamp": "2024-01-15T10:30:00",
    "dimensions": [
        {
            "name": "Compatibility",
            "score": 80.0,
            "weight": 0.30,
            "status": "good",
            "details": "Found 10 issues in 50 files",
            "recommendations": [...]
        },
        # ... other dimensions
    ],
    "recommendations": [
        {
            "dimension": "Compatibility",
            "priority": "high",
            "recommendation": "Run: ./py2to3 fix"
        },
        # ... other recommendations
    ],
    "health_history": [...]
}
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Dashboard Guide](README.md#interactive-progress-dashboard) - Visual progress tracking
- [Status Guide](STATUS_GUIDE.md) - Status reporting
- [Statistics Guide](README.md#statistics-tracking) - Detailed metrics
- [CI/CD Guide](CI_CD_GUIDE.md) - Continuous integration

## Tips for Success

1. **Start Early**: Check health before migration begins
2. **Be Consistent**: Run checks at regular intervals
3. **Address Critical First**: Prioritize recommendations by severity
4. **Track Trends**: Monitor improvement over time
5. **Communicate Often**: Share health scores with stakeholders
6. **Automate Checks**: Integrate into CI/CD pipeline
7. **Celebrate Progress**: Acknowledge health improvements
8. **Set Goals**: Define target scores for milestones
9. **Use with Planning**: Combine with planner and state tools
10. **Document Issues**: Note why health dips for future reference

The Migration Health Monitor provides a simple, actionable view of your migration status. Use it regularly to ensure your migration stays on track and healthy! 🏥✅
