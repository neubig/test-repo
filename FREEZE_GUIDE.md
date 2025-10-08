# Freeze Guard - Python 2 Prevention Guide

## Overview

**Freeze Guard** is a prevention-focused tool that stops Python 2 code from being re-introduced into your codebase during active migration. While other tools in the py2to3 toolkit help you *fix* and *verify* Python 2 code, Freeze Guard helps you *prevent* Python 2 patterns from coming back.

### Why Freeze Guard?

During a Python 2 to 3 migration, especially in active development environments:

- 🚫 **Prevents Regression**: Stop Python 2 code from accidentally being added to migrated files
- 🔒 **Protects Progress**: Mark files/directories as "frozen" (Python 3 only) once migrated
- 🎯 **Focuses Review**: CI/CD integration blocks PRs with Python 2 patterns in frozen code
- 👥 **Team Coordination**: Multiple developers can work without stepping on each other
- 🛡️ **Pre-commit Protection**: Git hooks prevent Python 2 code from being committed

## Quick Start

### 1. Mark a File as Frozen (After Migrating It)

```bash
# After successfully migrating a file to Python 3
./py2to3 freeze mark src/utils/helpers.py

# Or freeze an entire directory
./py2to3 freeze mark src/auth/
```

### 2. Install Pre-commit Hook (Recommended)

```bash
# Install hook to check on every commit
./py2to3 freeze install-hook
```

### 3. Check Files for Python 2 Patterns

```bash
# Check specific files
./py2to3 freeze check src/utils/helpers.py

# Check all frozen files in the project
./py2to3 freeze check --frozen-only

# Check only staged files (useful in CI)
./py2to3 freeze check --staged
```

## Commands

### `freeze mark` - Mark Files as Frozen

Mark files or directories as "frozen" (Python 3 only). These paths will be monitored for Python 2 patterns.

```bash
# Mark a single file
./py2to3 freeze mark src/module.py

# Mark multiple files
./py2to3 freeze mark src/auth.py src/utils.py src/models.py

# Mark an entire directory
./py2to3 freeze mark src/core/

# Mark multiple directories
./py2to3 freeze mark src/auth/ src/api/ src/models/
```

**What it does:**
- Adds paths to `.freeze-guard.json` configuration
- Creates config file if it doesn't exist
- Validates that paths exist
- Can be run multiple times safely

### `freeze unmark` - Remove Frozen Status

Remove the "frozen" status from files or directories.

```bash
# Unmark a file
./py2to3 freeze unmark src/module.py

# Unmark a directory
./py2to3 freeze unmark src/legacy/

# Unmark multiple paths
./py2to3 freeze unmark src/old1.py src/old2.py
```

**When to use:**
- Temporarily allowing Python 2 code in a file (not recommended)
- Removing deprecated/deleted files from tracking
- Reorganizing frozen path structure

### `freeze check` - Check for Python 2 Patterns

Check files for Python 2 patterns. Returns exit code 1 if violations found.

```bash
# Check specific files
./py2to3 freeze check src/auth.py

# Check specific directory
./py2to3 freeze check src/core/

# Check only frozen files
./py2to3 freeze check --frozen-only

# Check git staged files (great for CI)
./py2to3 freeze check --staged

# Get JSON output
./py2to3 freeze check src/ --format json
```

**Output:**
```
❌ Found 3 Python 2 pattern(s) in 2 file(s)
======================================================================

📄 src/auth.py
  Line 15: Python 2 print statement without parentheses
    print "User authenticated"
  Line 42: Python 2 iteritems() method
    for key, value in config.iteritems():

📄 src/utils.py
  Line 8: Python 2 urllib2 import
    import urllib2

======================================================================
```

**Patterns Detected:**
- Print statements without parentheses
- Old-style imports (urllib2, ConfigParser, Queue)
- Python 2 string types (basestring, unicode())
- Dictionary methods (.iteritems(), .iterkeys(), .itervalues())
- xrange() function
- Old exception syntax (except E, e:)

### `freeze status` - Show Frozen Paths

Display all frozen paths and their status.

```bash
# Show frozen paths
./py2to3 freeze status

# Get JSON output
./py2to3 freeze status --json
```

**Example output:**
```
🔒 Frozen Paths (5):

  [✓] src/auth/                              (exists)
  [✓] src/api/handlers.py                    (exists)
  [✓] src/models/user.py                     (exists)
  [✗] src/old_module.py                      (not found)
  [✓] src/utils/                             (exists)

Config file: .freeze-guard.json
```

### `freeze install-hook` - Install Git Pre-commit Hook

Install a git pre-commit hook that checks frozen files automatically.

```bash
./py2to3 freeze install-hook
```

**What it does:**
- Creates `.git/hooks/pre-commit` file
- Checks staged files on every commit
- Blocks commits with Python 2 patterns in frozen files
- Shows clear error messages with line numbers
- Can be bypassed with `git commit --no-verify` (not recommended)

**Hook behavior:**
```bash
# When you commit...
git add src/auth.py
git commit -m "Update auth"

# If Python 2 patterns found in frozen files:
❌ Freeze Guard: Python 2 patterns detected in frozen files!
======================================================================
  src/auth.py:15
    ⚠️  Python 2 print statement
    📝 print "Invalid login"

======================================================================
Found 1 violation(s) in 1 file(s)

Please fix these issues before committing.
Or unfreeze the files with: ./py2to3 freeze unmark <path>

# If all clear:
✅ Freeze Guard: Checked 3 frozen file(s) - all clear!
```

## Integration Workflows

### Workflow 1: Gradual Module Migration

```bash
# 1. Migrate a module
./py2to3 fix src/auth/

# 2. Verify it's clean
./py2to3 check src/auth/

# 3. Freeze it to prevent regression
./py2to3 freeze mark src/auth/

# 4. Continue with other modules...
./py2to3 fix src/api/
./py2to3 check src/api/
./py2to3 freeze mark src/api/

# 5. Check status anytime
./py2to3 freeze status
```

### Workflow 2: CI/CD Integration

Add to your CI pipeline (e.g., GitHub Actions):

```yaml
name: Python 2 Freeze Guard

on: [push, pull_request]

jobs:
  freeze-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Check frozen files
        run: |
          ./py2to3 freeze check --frozen-only
          
      - name: Check staged changes (for PRs)
        if: github.event_name == 'pull_request'
        run: |
          ./py2to3 freeze check --staged
```

### Workflow 3: Team Development

```bash
# Developer A: Migrates auth module
./py2to3 fix src/auth/
./py2to3 freeze mark src/auth/
git add src/auth/ .freeze-guard.json
git commit -m "Migrate auth to Python 3"
git push

# Developer B: Pulls changes
git pull
./py2to3 freeze install-hook  # Get pre-commit protection

# Developer B: Works on different module
./py2to3 fix src/utils/
./py2to3 freeze mark src/utils/
# ... pre-commit hook checks frozen files automatically

# Both developers: Auth module stays frozen
# Any accidental Python 2 code in auth/ will be caught
```

### Workflow 4: Monitoring Mode

```bash
# Weekly check: Ensure no regressions
./py2to3 freeze check --frozen-only

# Add to cron job
0 0 * * 1 cd /path/to/project && ./py2to3 freeze check --frozen-only || echo "Python 2 patterns detected!" | mail -s "Freeze Guard Alert" team@example.com
```

## Configuration File

Freeze Guard uses `.freeze-guard.json` to track frozen paths:

```json
{
  "frozen_paths": [
    "src/auth/",
    "src/api/handlers.py",
    "src/models/",
    "src/utils/validators.py"
  ],
  "excluded_patterns": [],
  "strict_mode": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-20T15:45:00"
}
```

### Configuration Options

- **frozen_paths**: List of files/directories marked as Python 3 only
- **excluded_patterns**: Patterns to exclude from checking (future feature)
- **strict_mode**: Enable stricter checking (future feature)
- **created_at**: When config was first created
- **updated_at**: Last modification time

### Version Control

**Should you commit `.freeze-guard.json`?**

✅ **Yes!** - Recommended for team projects:
- Share frozen status across team
- Consistent checks in CI/CD
- Track migration progress
- Coordinate team efforts

```bash
# Add to version control
git add .freeze-guard.json
git commit -m "Track frozen paths for migration"
```

❌ **No** - If you want local-only tracking:
```bash
# Add to .gitignore
echo ".freeze-guard.json" >> .gitignore
```

## Use Cases

### 1. Active Development During Migration

**Problem**: Team is adding features while migrating to Python 3

**Solution**:
```bash
# As modules are migrated, freeze them
./py2to3 fix src/module1/
./py2to3 freeze mark src/module1/

# Install hooks for all developers
./py2to3 freeze install-hook

# Frozen modules are protected, development continues
```

### 2. Preventing Copy-Paste Mistakes

**Problem**: Developer copies code from old Python 2 file into migrated file

**Solution**:
```bash
# Pre-commit hook catches it automatically
git commit -m "Add feature"
# ❌ Freeze Guard: Python 2 patterns detected!

# Developer fixes the issue
# ✅ Commit succeeds
```

### 3. Code Review Assistance

**Problem**: Reviewers need to verify no Python 2 code in PRs

**Solution**:
```bash
# In CI/CD pipeline
./py2to3 freeze check --staged

# Automatic pass/fail on PRs
# Reviewers trust CI to catch Python 2 patterns
```

### 4. Incremental Migration Tracking

**Problem**: Hard to track which parts are done

**Solution**:
```bash
# Check overall progress
./py2to3 freeze status

# Shows:
# - What's frozen (migrated)
# - What's not frozen (pending)
# - Clear progress indicator
```

### 5. Post-Migration Monitoring

**Problem**: Need to ensure no regressions after migration

**Solution**:
```bash
# After full migration, freeze everything
./py2to3 freeze mark src/

# Regular monitoring
./py2to3 freeze check --frozen-only

# Catches any accidental Python 2 code
```

## Best Practices

### ✅ Do's

1. **Freeze After Verification**: Always verify migration before freezing
   ```bash
   ./py2to3 fix src/module.py
   ./py2to3 check src/module.py  # Verify clean
   ./py2to3 freeze mark src/module.py  # Then freeze
   ```

2. **Install Hooks for Team**: Ensure all developers have the hook
   ```bash
   # Add to setup docs
   ./py2to3 freeze install-hook
   ```

3. **Commit Config File**: Share frozen paths with team
   ```bash
   git add .freeze-guard.json
   ```

4. **Use in CI/CD**: Automate checking in your pipeline
   ```yaml
   - run: ./py2to3 freeze check --frozen-only
   ```

5. **Check Status Regularly**: Monitor progress
   ```bash
   ./py2to3 freeze status
   ```

### ❌ Don'ts

1. **Don't Freeze Unverified Code**: Freezing doesn't fix Python 2 code
   ```bash
   # ❌ Bad: Freezing without fixing
   ./py2to3 freeze mark src/legacy.py
   
   # ✅ Good: Fix, verify, then freeze
   ./py2to3 fix src/legacy.py
   ./py2to3 check src/legacy.py
   ./py2to3 freeze mark src/legacy.py
   ```

2. **Don't Bypass Hooks Casually**: The hook is there to protect you
   ```bash
   # ❌ Avoid: git commit --no-verify
   # ✅ Fix the Python 2 code instead
   ```

3. **Don't Freeze Everything at Once**: Gradual is better
   ```bash
   # ❌ Bad: ./py2to3 freeze mark .
   # ✅ Good: Freeze module by module
   ```

4. **Don't Ignore Violations**: They indicate real issues
   ```bash
   # When violations found, fix them!
   # Don't just unmark the file
   ```

## Troubleshooting

### Issue: Pre-commit Hook Not Running

**Symptoms**: Commits go through without checking

**Solutions**:
```bash
# 1. Check if hook exists
ls -la .git/hooks/pre-commit

# 2. Check if executable
chmod +x .git/hooks/pre-commit

# 3. Reinstall hook
./py2to3 freeze install-hook

# 4. Test hook manually
.git/hooks/pre-commit
```

### Issue: False Positives

**Symptoms**: Freeze check reports Python 2 in valid Python 3 code

**Solutions**:
```bash
# 1. Verify the line - might actually be Python 2
./py2to3 freeze check src/file.py

# 2. Check if it's in comments - comments are checked
# Remove Python 2 examples from comments or use backticks

# 3. If truly a false positive, report as issue
# For now, you can add comment to explain
```

### Issue: Config File Conflicts

**Symptoms**: Merge conflicts in `.freeze-guard.json`

**Solutions**:
```bash
# 1. Keep both frozen paths (union)
# Edit JSON to include all paths from both branches

# 2. Use merge tool
git mergetool .freeze-guard.json

# 3. Regenerate if needed
# Back up current, then regenerate
cp .freeze-guard.json .freeze-guard.json.bak
./py2to3 freeze mark src/module1/ src/module2/
```

### Issue: Slow Checks

**Symptoms**: `freeze check` takes too long

**Solutions**:
```bash
# 1. Check specific paths instead of whole project
./py2to3 freeze check src/specific_module/

# 2. Use --frozen-only to skip non-frozen files
./py2to3 freeze check --frozen-only

# 3. Use --staged in CI to check only changed files
./py2to3 freeze check --staged
```

## Advanced Usage

### Programmatic Usage

You can import and use Freeze Guard in Python:

```python
from freeze_guard import FreezeGuard

# Create guard
guard = FreezeGuard('.freeze-guard.json')

# Mark paths
guard.config.add_frozen_path('src/module.py')

# Check files
violations = guard.check_directory('src/')

# Check for violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line_num} - {v.pattern}")
        print(f"  {v.line}")
```

### Custom Patterns (Future)

Future versions will support custom pattern definitions:

```json
{
  "custom_patterns": {
    "deprecated_function": {
      "pattern": "old_function\\(",
      "message": "Use new_function instead",
      "severity": "warning"
    }
  }
}
```

## FAQ

**Q: Can I freeze files that still have Python 2 code?**  
A: Technically yes, but not recommended. Freeze after migration to prevent regression.

**Q: Does freezing automatically fix Python 2 code?**  
A: No. Freezing only prevents future Python 2 code. Use `./py2to3 fix` to migrate code.

**Q: Can I have some frozen and some unfrozen files?**  
A: Yes! That's the whole point. Freeze modules as you migrate them.

**Q: Will the hook slow down my commits?**  
A: No. It only checks frozen files that are staged, which is very fast.

**Q: Can I use this without git?**  
A: Yes. The `freeze check`, `mark`, and `status` commands work without git. Only `install-hook` requires git.

**Q: What happens if I delete a frozen file?**  
A: It stays in config but shows as "not found" in status. You can unmark it.

**Q: Can multiple developers use the same frozen paths?**  
A: Yes! Commit `.freeze-guard.json` to share frozen paths across team.

**Q: Does this work with other pre-commit frameworks?**  
A: The hook is standalone, but you can integrate it with `pre-commit` framework:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: freeze-guard
        name: Freeze Guard
        entry: ./py2to3 freeze check --staged
        language: system
        pass_filenames: false
```

## Related Tools

- **`./py2to3 fix`**: Migrate Python 2 code to Python 3
- **`./py2to3 check`**: Verify Python 3 compatibility
- **`./py2to3 state`**: Track migration state per file
- **`./py2to3 git`**: Git integration for migration

## Summary

Freeze Guard completes the migration toolkit by adding **prevention** to **detection** and **fixing**:

1. 🔧 **Fix**: `./py2to3 fix` - Convert Python 2 to Python 3
2. ✅ **Verify**: `./py2to3 check` - Detect remaining issues
3. 🔒 **Prevent**: `./py2to3 freeze` - Stop Python 2 from returning

Use Freeze Guard to:
- Protect migrated code from regression
- Coordinate team efforts during migration
- Integrate Python 2 checks into CI/CD
- Track migration progress clearly

**Get started:**
```bash
./py2to3 freeze --help
```
