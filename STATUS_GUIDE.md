# Quick Status Command Guide

The `status` command provides a comprehensive, at-a-glance view of your Python 2 to Python 3 migration progress directly in your terminal. It's perfect for quick checks during development without needing to generate full HTML reports.

## Features

✨ **At-a-Glance Overview**: See your entire migration status in one terminal screen  
📊 **Progress Visualization**: Beautiful progress bar showing completion percentage  
🔍 **Issue Summary**: Breakdown of issues by severity (Critical, High, Medium, Low)  
📈 **Trend Analysis**: Compare with previous snapshots to see progress  
🔀 **Git Integration**: See current branch, modified files, and recent commits  
💾 **Backup Status**: Quick check of available backups  
💡 **Smart Recommendations**: Actionable next steps based on your current state  
🎨 **Colorful Output**: Terminal colors make information easy to scan  

## Quick Start

### Basic Usage

```bash
# Show status for current directory
./py2to3 status

# Show status for specific project path
./py2to3 status src/

# Show status without colors (for CI/CD)
./py2to3 status --no-color
```

### JSON Output

Perfect for automation, CI/CD integration, or programmatic analysis:

```bash
# Output as JSON to console
./py2to3 status --json

# Export to file
./py2to3 status --json -o migration_status.json
```

## What the Status Report Shows

### 📁 Project Information
- **Path**: The absolute path to your project
- **Python Files**: Total count of `.py` files in the project
- **Timestamp**: When the report was generated

### 📊 Migration Progress
- **Visual Progress Bar**: Color-coded progress indicator (red → yellow → green)
- **Percentage**: Weighted calculation based on issue severity
- **Status Icon**: Quick visual indicator of progress state
  - ✓ (Green): Excellent progress (≥90%)
  - ◐ (Yellow): Good progress (≥70%)
  - ◑ (Yellow): In progress (≥40%)
  - ◯ (Red): Just started (<40%)

### 🔍 Issues Summary
- **Total Issues**: Overall count of compatibility issues
- **By Severity**: Breakdown showing:
  - 🔴 Critical: Will break in Python 3
  - 🟡 High: Significant compatibility issues
  - 🔵 Medium: Important but not urgent
  - 🔷 Low: Minor issues or improvements
- **Trend**: Shows increase/decrease from previous snapshot

### 🔀 Git Status (if in git repository)
- **Current Branch**: Active git branch
- **Modified Files**: Count of uncommitted changes
- **Last Commit**: Recent commit hash, message, and time

### 💾 Backup Status
- **Backup Count**: Number of available backups
- **Backup Directory**: Location of backups
- **Warning**: Alert if no backups exist

### 💡 Recommendations
Smart, context-aware suggestions for your next steps:
- First-time analysis recommendations
- Priority actions based on critical issues
- Commit reminders for many changed files
- Backup creation suggestions
- Test generation and verification prompts

## Progress Calculation

The progress percentage uses a weighted algorithm that considers issue severity:

```
Critical Issues × 4
High Issues     × 3
Medium Issues   × 2
Low Issues      × 1
```

This means fixing critical issues has more impact on progress than fixing low-severity issues, reflecting the real-world importance of different issue types.

## When to Use Status Command

### During Active Development
```bash
# Quick check after making changes
./py2to3 fix src/core/
./py2to3 status

# See if changes improved the situation
```

### In Team Standups
```bash
# Get talking points for daily standup
./py2to3 status
# "We're at 67% completion, down to 5 critical issues..."
```

### Before Committing
```bash
# Verify progress before committing
./py2to3 status
git add .
git commit -m "Fixed authentication module issues"
```

### In CI/CD Pipelines
```bash
# Generate status report for pipeline
./py2to3 status --json -o status.json --no-color

# Parse in your pipeline scripts
cat status.json | jq '.progress'
```

## Comparison with Other Commands

| Command | Purpose | Output | Best For |
|---------|---------|--------|----------|
| `status` | Quick at-a-glance overview | Terminal (colored) or JSON | Daily checks, standups, quick validation |
| `check` | Detailed compatibility analysis | Console + optional report file | Initial analysis, detailed investigation |
| `report` | Comprehensive HTML report | Interactive HTML with charts | Stakeholder presentations, documentation |
| `dashboard` | Interactive progress tracking | HTML with time-series data | Long-term tracking, velocity monitoring |
| `stats` | Detailed statistics | Console or JSON | Deep analysis, metrics collection |

## Examples

### Example 1: First-Time User

```bash
$ ./py2to3 status

======================================================================
                       MIGRATION STATUS REPORT
======================================================================

📁 Project Information
   Path: /home/user/myproject
   Python Files: 42
   Timestamp: 2024-01-15 14:30:00

📊 Migration Progress
   ◯ Status: Just Started
   [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.0%

🔍 Issues Summary
   No stats available - run './py2to3 check .' first

💡 Recommendations
   1. Run './py2to3 check .' to analyze your code
   2. Run './py2to3 preflight' to verify environment readiness

======================================================================
```

### Example 2: Mid-Migration

```bash
$ ./py2to3 status

======================================================================
                       MIGRATION STATUS REPORT
======================================================================

📁 Project Information
   Path: /home/user/myproject
   Python Files: 42
   Timestamp: 2024-01-16 10:15:00

📊 Migration Progress
   ◑ Status: In Progress
   [████████████████░░░░░░░░░░░░░░░░░░░░░░░░] 45.3%

🔍 Issues Summary
   Total Issues: 127
   ● Critical:    8
   ● High:       23
   ● Medium:     41
   ● Low:        55
   ↓ 34 fewer issues since last check

🔀 Git Status
   Branch: feature/py3-migration
   Modified Files: 12
   Last Commit: abc1234 - Fixed database module (2 hours ago)

💾 Backup Status
   ✓ 5 backup(s) in .migration_backups

💡 Recommendations
   1. Address 8 critical issue(s) first - these will break Python 3
   2. Run './py2to3 fix .' to apply automatic fixes
   3. Commit your changes - 12 files modified

======================================================================
```

### Example 3: Near Completion

```bash
$ ./py2to3 status

======================================================================
                       MIGRATION STATUS REPORT
======================================================================

📁 Project Information
   Path: /home/user/myproject
   Python Files: 42
   Timestamp: 2024-01-20 16:45:00

📊 Migration Progress
   ✓ Status: Excellent
   [████████████████████████████████████████] 95.8%

🔍 Issues Summary
   Total Issues: 7
   ● Medium:     3
   ● Low:        4
   ↓ 8 fewer issues since last check

🔀 Git Status
   Branch: feature/py3-migration
   Modified Files: 0 (clean)
   Last Commit: def5678 - Final compatibility fixes (1 hour ago)

💾 Backup Status
   ✓ 12 backup(s) in .migration_backups

💡 Recommendations
   1. Review remaining low/medium issues
   2. Run './py2to3 test-gen' to generate migration tests
   3. Migration appears complete! Run tests to verify

======================================================================
```

### Example 4: JSON Output

```bash
$ ./py2to3 status --json

{
  "timestamp": "2024-01-15T14:30:00.123456",
  "project_path": "/home/user/myproject",
  "python_files": 42,
  "progress": 45.3,
  "stats": {
    "total_issues": 127,
    "critical_issues": 8,
    "high_issues": 23,
    "medium_issues": 41,
    "low_issues": 55
  },
  "previous_stats": {
    "total_issues": 161
  },
  "git_status": {
    "branch": "feature/py3-migration",
    "modified_files": 12,
    "last_commit": "abc1234 - Fixed database module (2 hours ago)"
  },
  "backup_info": {
    "directory": ".migration_backups",
    "count": 5
  },
  "recommendations": [
    "Address 8 critical issue(s) first - these will break Python 3",
    "Run './py2to3 fix .' to apply automatic fixes",
    "Commit your changes - 12 files modified"
  ]
}
```

## Integration with Workflow

### Typical Workflow Using Status

```bash
# 1. Start fresh - check status
./py2to3 status

# 2. Run initial analysis (if needed)
./py2to3 check .

# 3. Check status again
./py2to3 status

# 4. Apply fixes
./py2to3 fix .

# 5. Verify progress
./py2to3 status

# 6. Commit if satisfied
git add .
git commit -m "Applied Python 3 compatibility fixes"

# 7. Final status check
./py2to3 status
```

### Morning Standup Routine

```bash
# Get your daily talking points
./py2to3 status > daily_status.txt
cat daily_status.txt

# In standup:
# "Yesterday we were at 45%, today we're at 58%"
# "We fixed 12 critical issues, 8 remain"
# "Planning to focus on the database module today"
```

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Show migration status before each commit

echo "=== Current Migration Status ==="
./py2to3 status --no-color

echo ""
echo "Proceed with commit? (y/n)"
read answer
if [ "$answer" != "y" ]; then
    exit 1
fi
```

## Advanced Usage

### Custom Stats Directory

If you're storing stats in a non-default location:

```bash
./py2to3 status --stats-dir custom_stats/
```

### Parsing in Scripts

```bash
#!/bin/bash
# Get progress percentage for automated decisions

progress=$(./py2to3 status --json | jq -r '.progress')

if (( $(echo "$progress >= 90" | bc -l) )); then
    echo "Migration is almost complete! 🎉"
    ./py2to3 test-gen .
else
    echo "Keep going, you're at ${progress}%"
fi
```

### Automated Reporting

```bash
# Cron job to email daily status
0 9 * * * cd /path/to/project && \
  ./py2to3 status --no-color | \
  mail -s "Daily Migration Status" team@company.com
```

## Troubleshooting

### "No stats available"

**Problem**: Status shows no stats available.

**Solution**: Run analysis first:
```bash
./py2to3 check .
./py2to3 stats collect --save
./py2to3 status
```

### No git information shown

**Problem**: Git status section doesn't appear.

**Cause**: Not in a git repository or git not installed.

**Solution**: Initialize git repository or install git:
```bash
git init
./py2to3 status
```

### Progress seems wrong

**Problem**: Progress percentage doesn't match expectations.

**Explanation**: Progress uses weighted calculation based on severity. Critical issues have more impact than low-severity issues.

**Check**: Review issue counts by severity in the Issues Summary section.

### Colors not showing in CI/CD

**Problem**: Colored output breaks CI/CD logs.

**Solution**: Use `--no-color` flag:
```bash
./py2to3 status --no-color
```

Or let it auto-detect (it disables colors when not in a TTY).

## Tips & Best Practices

1. **Run Status Frequently**: It's designed to be fast and lightweight - check it often!

2. **Use with Stats Collection**: For trend analysis, collect stats regularly:
   ```bash
   ./py2to3 stats collect --save
   ./py2to3 status  # Shows comparison with previous
   ```

3. **Combine with Other Commands**: Status works great alongside other commands:
   ```bash
   ./py2to3 preflight && ./py2to3 status
   ```

4. **Export for Records**: Keep JSON exports for historical tracking:
   ```bash
   ./py2to3 status --json -o "status_$(date +%Y%m%d).json"
   ```

5. **Use in Scripts**: The exit code is always 0 on success, making it script-friendly.

6. **Pipe for Processing**: JSON output can be piped to other tools:
   ```bash
   ./py2to3 status --json | jq '.recommendations[]'
   ```

## Related Commands

- **`./py2to3 check`** - Analyze code for Python 3 compatibility
- **`./py2to3 stats`** - Collect and manage statistics
- **`./py2to3 dashboard`** - Generate interactive HTML progress dashboard
- **`./py2to3 report`** - Generate comprehensive HTML migration report
- **`./py2to3 preflight`** - Run pre-migration safety checks

## Summary

The `status` command is your go-to tool for quick migration progress checks. It combines information from multiple sources (stats, git, backups) into a single, easy-to-read report that helps you:

- ✅ Track progress at a glance
- ✅ Identify what to work on next
- ✅ Stay motivated with visual progress
- ✅ Share updates with your team
- ✅ Make informed decisions about migration strategy

Use it frequently throughout your migration journey - it's designed to be fast, informative, and actionable!
