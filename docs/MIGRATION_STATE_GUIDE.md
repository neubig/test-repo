# Migration State Tracker Guide

## Overview

The Migration State Tracker is a feature designed to help teams coordinate large-scale Python 2 to Python 3 migrations by tracking the migration status of individual files through various stages of the migration process.

## Why Use State Tracking?

When migrating large codebases:
- **Multiple team members** may be working on different files simultaneously
- **Progress tracking** helps identify what's done and what remains
- **Resumable workflows** allow you to pick up where you left off after interruptions
- **Lock mechanism** prevents conflicting edits to the same file
- **State history** provides audit trail of migration progress

## Migration States

Each file progresses through the following states:

1. **pending** - File identified for migration but not yet started
2. **in_progress** - Someone is actively migrating this file
3. **migrated** - Code changes complete, awaiting verification
4. **verified** - Changes reviewed and verified, awaiting tests
5. **tested** - Tests passing, ready for final approval
6. **done** - Migration complete and approved
7. **skipped** - File skipped (e.g., will be deprecated, not Python code)

## Quick Start

### Initialize State Tracking

```bash
# Initialize in current directory
./py2to3 state init

# Initialize and scan a specific directory
./py2to3 state init --scan-dir ./src

# Force reinitialize (resets all state)
./py2to3 state init --force
```

### View Statistics

```bash
./py2to3 state stats
```

Example output:
```
Migration State Statistics

Total Files: 47
Completion: 15.4%

By State:
  pending      :   38 (80.9%)
  in_progress  :    2 (4.3%)
  migrated     :    3 (6.4%)
  done         :    4 (8.5%)

Activity:
  In Progress  : 2
  Locked Files : 2
```

### List Files

```bash
# List all files
./py2to3 state list

# List only pending files
./py2to3 state list --filter-state pending

# List only in-progress files
./py2to3 state list --filter-state in_progress

# List only locked files
./py2to3 state list --locked

# List files owned by specific user
./py2to3 state list --owner alice@hostname
```

## Typical Workflow

### For Individual Developers

1. **Check what needs doing**:
   ```bash
   ./py2to3 state list --filter-state pending
   ```

2. **Lock a file you want to work on**:
   ```bash
   ./py2to3 state lock src/module.py
   ```

3. **Set state to in_progress**:
   ```bash
   ./py2to3 state set src/module.py in_progress
   ```

4. **Do the migration work**:
   ```bash
   # Use py2to3 tools to migrate
   ./py2to3 fix src/module.py
   ```

5. **Update state as you progress**:
   ```bash
   ./py2to3 state set src/module.py migrated --notes "Fixed all print statements and imports"
   ```

6. **After verification**:
   ```bash
   ./py2to3 state set src/module.py verified
   ```

7. **After testing**:
   ```bash
   ./py2to3 state set src/module.py tested
   ```

8. **Mark as done**:
   ```bash
   ./py2to3 state set src/module.py done
   ./py2to3 state unlock src/module.py
   ```

### For Team Coordination

**Team Lead - Initialize and assign work**:
```bash
# Initialize tracking
./py2to3 state init

# Export current state for team
./py2to3 state export -o migration-status.json

# Share migration-status.json with team
```

**Team Member - Pick up work**:
```bash
# Import shared state
./py2to3 state import migration-status.json

# See what's available
./py2to3 state list --filter-state pending

# Lock and start work
./py2to3 state lock src/myfile.py --owner me@myhost
./py2to3 state set src/myfile.py in_progress --user me
```

**Periodic Sync**:
```bash
# Export your progress
./py2to3 state export -o my-progress.json

# Team lead merges progress
./py2to3 state import alice-progress.json --merge
./py2to3 state import bob-progress.json --merge

# Export consolidated state
./py2to3 state export -o migration-status.json
```

## Command Reference

### init

Initialize state tracking for a project.

```bash
./py2to3 state init [--scan-dir DIR] [--force]
```

Options:
- `--scan-dir DIR`: Directory to scan for Python files (default: project root)
- `--force`: Reinitialize even if already initialized

### list

List files and their migration states.

```bash
./py2to3 state list [--filter-state STATE] [--locked] [--owner OWNER]
```

Options:
- `--filter-state STATE`: Filter by state (pending, in_progress, migrated, verified, tested, done, skipped)
- `--locked`: Show only locked files
- `--owner OWNER`: Filter by owner

### set

Set the migration state for a file.

```bash
./py2to3 state set FILE STATE [--notes NOTES] [--user USER]
```

Arguments:
- `FILE`: Path to the file
- `STATE`: New state (pending, in_progress, migrated, verified, tested, done, skipped)

Options:
- `--notes NOTES`: Add notes about the state change
- `--user USER`: User making the change

### lock

Lock a file for exclusive editing.

```bash
./py2to3 state lock FILE [--owner OWNER]
```

Arguments:
- `FILE`: Path to the file

Options:
- `--owner OWNER`: Owner of the lock (default: current user@hostname)

### unlock

Unlock a file.

```bash
./py2to3 state unlock FILE [--owner OWNER] [--force]
```

Arguments:
- `FILE`: Path to the file

Options:
- `--owner OWNER`: Owner requesting unlock
- `--force`: Force unlock regardless of owner

### stats

Show migration state statistics.

```bash
./py2to3 state stats
```

### reset

Reset a file to pending state.

```bash
./py2to3 state reset FILE
```

Arguments:
- `FILE`: Path to the file

### export

Export state to a file.

```bash
./py2to3 state export [-o OUTPUT]
```

Options:
- `-o OUTPUT`, `--output OUTPUT`: Output file path (default: stdout)

### import

Import state from a file.

```bash
./py2to3 state import FILE [--merge]
```

Arguments:
- `FILE`: File to import from

Options:
- `--merge`: Merge with existing state instead of replacing

## Advanced Usage

### Integration with CI/CD

You can integrate state tracking with your CI/CD pipeline:

```yaml
# .github/workflows/migration-progress.yml
name: Track Migration Progress

on:
  push:
    branches: [ main, migration/* ]

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Show migration stats
        run: |
          ./py2to3 state stats
          
      - name: Export state
        run: |
          ./py2to3 state export -o migration-state.json
          
      - name: Upload state artifact
        uses: actions/upload-artifact@v2
        with:
          name: migration-state
          path: migration-state.json
```

### Custom Scripts

You can use the state tracker from Python scripts:

```python
from migration_state import MigrationStateTracker, MigrationState

# Initialize tracker
tracker = MigrationStateTracker('.')

# Get all pending files
pending = tracker.list_files(state=MigrationState.PENDING)

# Process each file
for file_info in pending:
    file_path = file_info['path']
    print(f"Processing {file_path}...")
    
    # Lock file
    tracker.lock_file(file_path)
    
    # Set to in_progress
    tracker.set_state(file_path, MigrationState.IN_PROGRESS)
    
    # Do migration work...
    # ...
    
    # Update state
    tracker.set_state(file_path, MigrationState.MIGRATED, 
                     notes="Automated migration")
    
    # Unlock
    tracker.unlock_file(file_path)
```

### Filtering and Reporting

Generate custom reports:

```bash
# Count files by state
./py2to3 state export | jq '.files | group_by(.state) | map({state: .[0].state, count: length})'

# List files updated today
./py2to3 state export | jq '.files[] | select(.updated > "2024-01-01")'

# Find stale in-progress files
./py2to3 state export | jq '.files[] | select(.state == "in_progress" and .updated < "2024-01-01")'
```

## State File Format

The state is stored in `.py2to3.state.json` in the project root:

```json
{
  "version": "1.0",
  "project_root": "/path/to/project",
  "initialized_at": "2024-01-15T10:30:00",
  "last_updated": "2024-01-15T14:45:00",
  "files": {
    "src/module.py": {
      "path": "src/module.py",
      "state": "migrated",
      "locked": false,
      "owner": null,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T14:45:00",
      "history": [
        {
          "state": "pending",
          "timestamp": "2024-01-15T10:30:00",
          "user": "system"
        },
        {
          "state": "in_progress",
          "timestamp": "2024-01-15T12:00:00",
          "user": "alice@workstation",
          "notes": "Starting migration"
        },
        {
          "state": "migrated",
          "timestamp": "2024-01-15T14:45:00",
          "user": "alice@workstation",
          "notes": "Fixed all print statements and imports"
        }
      ]
    }
  }
}
```

## Best Practices

1. **Initialize early**: Run `state init` at the start of your migration project
2. **Lock before editing**: Always lock files before starting work to avoid conflicts
3. **Use notes**: Add meaningful notes when changing state to help with audit trail
4. **Regular stats**: Check `state stats` regularly to track overall progress
5. **Export frequently**: Export state regularly for backup and team coordination
6. **Atomic commits**: When committing migrated code, also commit the state file
7. **Clear ownership**: Use `--owner` flag to make it clear who's working on what

## Troubleshooting

### File Not Tracked

If a file isn't tracked, you can reinitialize or manually add it:

```bash
# Reinitialize to pick up new files
./py2to3 state init --force
```

### Lock Conflicts

If someone else has locked a file:

```bash
# Check who has it locked
./py2to3 state list --locked

# Contact them, or force unlock if necessary
./py2to3 state unlock src/file.py --force
```

### State File Corruption

If the state file becomes corrupted:

```bash
# Backup first (if possible)
cp .py2to3.state.json .py2to3.state.json.backup

# Reinitialize
./py2to3 state init --force

# If you have a backup, try importing
./py2to3 state import .py2to3.state.json.backup --merge
```

### Merge Conflicts

When multiple people work on state files:

```bash
# Export individual states
./py2to3 state export -o state1.json  # Person 1
./py2to3 state export -o state2.json  # Person 2

# One person imports both (later changes take precedence)
./py2to3 state import state1.json
./py2to3 state import state2.json --merge
```

## FAQ

**Q: Can I use this with git?**  
A: Yes! The state file `.py2to3.state.json` can be tracked in git. Commit it along with your migrations.

**Q: What if I want to skip a file?**  
A: Use the `skipped` state: `./py2to3 state set file.py skipped --notes "Reason for skipping"`

**Q: How do I undo a state change?**  
A: Use the reset command: `./py2to3 state reset file.py` or manually set it back: `./py2to3 state set file.py pending`

**Q: Can I track files outside the project?**  
A: No, the tracker is designed for files within the project root.

**Q: What happens if I delete a tracked file?**  
A: The state remains. You can either leave it (for historical record) or reinitialize to clean up.

**Q: Is the lock mechanism enforced?**  
A: No, locks are advisory only. They help coordination but don't prevent file edits.

## Integration with Other Tools

The state tracker works well with other py2to3 commands:

```bash
# Check files before migrating
./py2to3 state list --filter-state pending | while read -r state path; do
    ./py2to3 check "$path"
done

# Fix all in-progress files
./py2to3 state list --filter-state in_progress | while read -r state path; do
    ./py2to3 fix "$path"
    ./py2to3 state set "$path" migrated
done

# Run tests on migrated files
./py2to3 state list --filter-state migrated | while read -r state path; do
    python -m pytest "tests/test_${path##*/}" && \
        ./py2to3 state set "$path" tested
done
```

## See Also

- [Main README](../README.md) - Overview of py2to3 toolkit
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contributing guidelines
- [Status Reporter](status_reporter.py) - Related progress tracking functionality
