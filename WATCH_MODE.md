# Watch Mode Guide

The Watch Mode feature provides real-time monitoring and feedback during Python 2 to 3 migration. It watches your Python files for changes and automatically runs compatibility checks, giving you instant feedback as you work.

## Overview

Watch mode is like having a continuous integration system running locally on your machine. As you edit Python files during migration, watch mode automatically:

- Detects file changes in real-time
- Runs Python 3 compatibility checks
- Displays results immediately in your terminal
- Tracks statistics across your session
- Provides clean, formatted output with icons and colors

This is particularly useful during the migration process when you're actively fixing issues and want immediate feedback without manually running the checker after each change.

## Installation

Watch mode requires the `watchdog` Python package for file system monitoring:

```bash
pip install watchdog
```

## Basic Usage

### Start Watching Current Directory

```bash
./py2to3 watch
```

This starts watch mode in the current directory with default settings.

### Watch a Specific Path

```bash
./py2to3 watch src/
```

Watch a specific directory or file path.

### Watch with Stats Tracking

```bash
./py2to3 watch src/ --mode stats
```

Automatically update statistics snapshots as files change.

## Watch Modes

Watch mode supports three different modes:

### 1. Check Mode (Default)

```bash
./py2to3 watch --mode check
```

Simply checks files for compatibility issues and displays results. This is the fastest mode and best for active development.

**Output includes:**
- Number of issues found
- Issue severity (errors, warnings, info)
- Line numbers and descriptions
- Real-time session statistics

### 2. Stats Mode

```bash
./py2to3 watch --mode stats
```

Checks files and automatically updates statistics snapshots. Use this when you want to track progress over time while working.

**Features:**
- All check mode features
- Automatic stats snapshot updates
- Historical progress tracking
- Integration with `./py2to3 stats` commands

### 3. Report Mode

```bash
./py2to3 watch --mode report
```

Monitors files and can trigger report generation. Currently displays the same output as check mode but designed for future report auto-generation.

## Advanced Options

### Adjust Debounce Delay

The debounce delay controls how long watch mode waits after file changes before running checks. This prevents running checks on every keystroke.

```bash
./py2to3 watch --debounce 2.0
```

- Default: 1.0 second
- Increase for slower systems or to reduce check frequency
- Decrease for faster feedback (may trigger more often during editing)

## Example Workflows

### Active Migration Development

When actively fixing Python 2 code:

```bash
# Terminal 1: Start watch mode
./py2to3 watch src/

# Terminal 2: Edit files
vim src/core/processor.py
# Save changes and immediately see results in Terminal 1
```

### Progress Tracking While Working

When you want to track progress in real-time:

```bash
# Terminal 1: Watch with stats
./py2to3 watch src/ --mode stats

# Terminal 2: View trends
./py2to3 stats trend

# Terminal 3: Work on fixes
code src/
```

### Focused File Monitoring

Watch a single problematic file:

```bash
./py2to3 watch src/data/processor.py
```

## Understanding the Output

### Initial Scan

When watch mode starts, it performs an initial scan:

```
======================================================================
🔍 Watch Mode Started
======================================================================
Path: /path/to/project/src
Mode: check
Time: 2024-01-15 10:30:00

Monitoring Python files for changes...
Press Ctrl+C to stop

======================================================================

📊 Running initial scan...

Initial scan complete:
  Total issues: 42
  Errors: 15
  Warnings: 20
  Infos: 7
```

### Change Detection

When you save a file:

```
──────────────────────────────────────────────────────────────────────
🔄 Change detected at 10:32:15
──────────────────────────────────────────────────────────────────────
📝 Checking: src/core/processor.py
  ⚠️  Found 3 issue(s):
     🔴 Line 45: Using removed 'unicode()' function
     🟡 Line 67: Dictionary method 'iteritems()' not available
     🔵 Line 89: Consider using context manager
──────────────────────────────────────────────────────────────────────
```

### Clean Files

When a file has no issues:

```
──────────────────────────────────────────────────────────────────────
🔄 Change detected at 10:35:22
──────────────────────────────────────────────────────────────────────
📝 Checking: src/utils/helpers.py
  ✅ No issues found
──────────────────────────────────────────────────────────────────────
```

### Session Statistics

When you stop watch mode (Ctrl+C):

```
======================================================================
🛑 Watch Mode Stopped
======================================================================

📈 Session Statistics:
  Checks run: 15
  Clean checks: 8
  Files with issues: 7
  Total issues found: 23
  Last check: 5s ago
======================================================================
```

## Icon Reference

Watch mode uses icons to make output easier to scan:

- 🔍 Watch mode started
- 🛑 Watch mode stopped
- 📊 Running scan
- 🔄 Change detected
- 📝 Checking file
- ✅ No issues found
- ⚠️ Issues found
- 🔴 Error severity
- 🟡 Warning severity
- 🔵 Info severity
- 📈 Session statistics

## Tips and Best Practices

### 1. Use Appropriate Debounce

If watch mode is triggering too frequently while you type:

```bash
./py2to3 watch --debounce 2.0
```

### 2. Focus on Specific Areas

Watch only the code you're actively working on:

```bash
./py2to3 watch src/core/  # Just one module
```

### 3. Combine with Git

Keep your changes in version control:

```bash
# Terminal 1: Watch mode
./py2to3 watch src/

# Terminal 2: Git workflow
git checkout -b feature/py3-migration
# Make fixes...
git add src/core/processor.py
git commit -m "Fix unicode issues in processor"
```

### 4. Multi-Terminal Workflow

```bash
# Terminal 1: Watch mode for instant feedback
./py2to3 watch src/ --mode stats

# Terminal 2: Your editor
vim src/

# Terminal 3: Run tests
pytest tests/

# Terminal 4: Monitor overall progress
watch -n 5 './py2to3 stats show'
```

### 5. Use with Pre-commit Hooks

Watch mode complements pre-commit hooks - use watch mode during development and pre-commit hooks as a safety net:

```bash
# Development: immediate feedback
./py2to3 watch src/

# Commit: safety check
git commit  # Triggers pre-commit hook
```

## Troubleshooting

### Watch Mode Won't Start

**Problem:** Error about missing watchdog package

**Solution:**
```bash
pip install watchdog
```

### Too Many Checks Running

**Problem:** Watch mode checks files too frequently

**Solution:** Increase debounce delay:
```bash
./py2to3 watch --debounce 3.0
```

### Not Detecting Changes

**Problem:** File changes aren't being detected

**Solution:**
- Ensure the path exists and is correct
- Check file permissions
- Try restarting watch mode
- Some editors use atomic saves - try a direct edit

### Performance Issues

**Problem:** Watch mode slows down your system

**Solution:**
- Watch a smaller directory
- Increase debounce delay
- Exclude directories with `.gitignore` patterns
- Close other resource-intensive applications

## Integration with Other Commands

Watch mode works well with other py2to3 commands:

```bash
# Get initial report
./py2to3 check src/ -r initial_report.txt

# Start watching during development
./py2to3 watch src/ --mode stats

# Periodically check progress
./py2to3 stats show

# Generate final report
./py2to3 report -o final_report.html
```

## Comparison with Other Modes

| Feature | Regular Check | Watch Mode | CI/CD |
|---------|--------------|------------|-------|
| Manual trigger | ✓ | ✗ | ✗ |
| Automatic | ✗ | ✓ | ✓ |
| Real-time feedback | ✗ | ✓ | ✗ |
| Local development | ✓ | ✓ | ✗ |
| Team collaboration | ✗ | ✗ | ✓ |
| Historical tracking | ✗ | ✓ (stats mode) | ✓ |

**Use regular check when:** You want one-time analysis

**Use watch mode when:** Actively developing and fixing issues

**Use CI/CD when:** Team collaboration and automated validation

## Examples

### Example 1: Quick Feedback Loop

```bash
# Start watch mode
./py2to3 watch src/core/

# Edit processor.py - see results immediately
# Fix issue - see it clear immediately
# Continue iterating with instant feedback
```

### Example 2: Track Progress While Migrating

```bash
# Morning: Check baseline
./py2to3 stats collect src/

# During work: Watch with stats
./py2to3 watch src/ --mode stats

# End of day: View progress
./py2to3 stats trend
```

### Example 3: Focus on Problem Files

```bash
# Identify problematic files
./py2to3 check src/ | grep "issues found"

# Watch the worst file
./py2to3 watch src/data/legacy_processor.py

# Fix issues one by one with immediate feedback
```

## Advanced Configuration

### Through Config File

You can set watch mode defaults in your config file:

```bash
# Initialize config
./py2to3 config init

# Set defaults
./py2to3 config set watch_mode "stats"
./py2to3 config set watch_debounce "1.5"
```

Then simply run:

```bash
./py2to3 watch  # Uses configured defaults
```

## Future Enhancements

Planned improvements for watch mode:

- [ ] Auto-fix mode (automatically apply fixes)
- [ ] Custom ignore patterns
- [ ] Notification integration (desktop notifications)
- [ ] Live HTML report generation
- [ ] Multiple path watching
- [ ] Watch mode plugins/hooks
- [ ] Performance profiling integration

## Related Commands

- `./py2to3 check` - One-time compatibility check
- `./py2to3 stats` - View statistics and trends
- `./py2to3 preflight` - Pre-migration environment check
- `./py2to3 fix` - Apply automatic fixes

## Conclusion

Watch mode provides a modern, developer-friendly workflow for Python migration. It brings the convenience of real-time feedback found in modern JavaScript tools (like webpack watch or jest --watch) to the Python migration process.

For more information:
- Run `./py2to3 watch --help`
- See the main [README.md](README.md)
- Check out [CLI_GUIDE.md](CLI_GUIDE.md) for all commands
