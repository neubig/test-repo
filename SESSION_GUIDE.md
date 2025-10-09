# Migration Session Manager Guide ⏱️

Track your migration work sessions, time spent, and developer productivity with the Migration Session Manager. This tool helps you understand migration velocity and plan work more effectively.

## Why Track Sessions?

- **Time Tracking**: Know exactly how much time is spent on migration
- **Productivity Metrics**: Measure files migrated, tasks completed, and velocity
- **Team Coordination**: Track multiple developers working on migration
- **Project Planning**: Use historical data to estimate remaining work
- **Documentation**: Keep notes and observations during migration
- **Accountability**: Generate reports for stakeholders

## Quick Start

```bash
# Start a new session
./py2to3 session start --description "Migrating authentication module"

# Record your work
./py2to3 session file src/auth.py
./py2to3 session task "Fixed print statements in auth module"
./py2to3 session note "Found some tricky unicode issues"

# Take a break
./py2to3 session pause

# Resume work
./py2to3 session resume

# End the session
./py2to3 session end --summary "Completed auth module migration"

# View your progress
./py2to3 session stats
```

## Commands

### Starting a Session

Start a new migration work session:

```bash
# Basic start
./py2to3 session start

# With developer name
./py2to3 session start --developer "Jane Doe"

# With description
./py2to3 session start --description "Fixing core module imports"

# Complete example
./py2to3 session start \
  --developer "Jane Doe" \
  --description "Migrating database layer to Python 3"
```

**Note**: Only one session can be active at a time. End the current session before starting a new one.

### Ending a Session

End your current work session:

```bash
# Basic end
./py2to3 session end

# With summary
./py2to3 session end --summary "Migrated 15 files, all tests passing"
```

When you end a session, it calculates the total time spent (excluding breaks) and saves it to history.

### Pausing and Resuming

Take breaks without stopping your session:

```bash
# Pause for a break (lunch, meeting, etc.)
./py2to3 session pause

# Resume when you return
./py2to3 session resume
```

Break time is automatically tracked and excluded from your work time calculation.

### Recording Activity

Track what you're working on during the session:

```bash
# Record a file you're working on
./py2to3 session file src/models/user.py
./py2to3 session file src/utils/helpers.py

# Record completed tasks
./py2to3 session task "Fixed print statements in user model"
./py2to3 session task "Updated imports in helpers module"
./py2to3 session task "Ran test suite - all passing"

# Add notes and observations
./py2to3 session note "Found unicode encoding issue in helper.py"
./py2to3 session note "Need to review exception handling in next session"
```

### Viewing Status

Check your current session status:

```bash
./py2to3 session status
```

This shows:
- Session ID and developer name
- Start time and current status (active/paused)
- Session description
- Files modified, tasks completed, notes recorded
- Number of breaks taken
- List of files being worked on

### Session History

View your past sessions:

```bash
# Show last 10 sessions (default)
./py2to3 session history

# Show more sessions
./py2to3 session history --limit 20

# Show last 5 sessions
./py2to3 session history --limit 5
```

Each session shows:
- Session ID and developer
- Duration (excluding breaks)
- Number of files and tasks
- Description and summary (if provided)

### Statistics

View aggregate statistics across all sessions:

```bash
./py2to3 session stats
```

Shows:
- Total number of sessions
- Total time spent on migration
- Average session duration
- Total files modified
- Total tasks completed
- Total notes recorded
- Breakdown by developer (for team migrations)

### Generate Reports

Create detailed session reports:

```bash
# Print report to console
./py2to3 session report

# Save report to file
./py2to3 session report -o session_report.txt
```

Reports include:
- Overall statistics summary
- Statistics by developer
- Current active session details
- Recent session history
- Productivity metrics

## Workflow Examples

### Solo Developer Workflow

```bash
# Morning - Start your work
./py2to3 session start --description "Migrating web scraping module"

# Record as you work
./py2to3 session file src/web/scraper.py
./py2to3 session task "Updated urllib2 imports"
./py2to3 session note "Need to test with real websites"

# Lunch break
./py2to3 session pause

# Back from lunch
./py2to3 session resume

# More work
./py2to3 session file src/web/parser.py
./py2to3 session task "Fixed string encoding in parser"

# End of day
./py2to3 session end --summary "Completed web scraping module, needs testing"

# Check your productivity
./py2to3 session stats
```

### Team Migration Workflow

```bash
# Developer A - Morning
./py2to3 session start --developer "Alice" --description "Core module migration"
# ... work ...
./py2to3 session end --summary "Completed core module"

# Developer B - Afternoon
./py2to3 session start --developer "Bob" --description "Utils and helpers"
# ... work ...
./py2to3 session end --summary "Completed utils module"

# Team lead - View team progress
./py2to3 session stats

# Generate report for standup
./py2to3 session report -o team_progress.txt
```

### Sprint Planning Workflow

```bash
# At end of sprint, generate report
./py2to3 session report -o sprint_1_report.txt

# View statistics
./py2to3 session stats

# Use data for planning:
# - Total time spent: 40 hours
# - Average session: 2 hours
# - Files completed: 30
# - Velocity: ~0.75 files per hour
# - Estimate remaining: 50 files = ~67 hours = ~17 days at 4h/day
```

## Integration with Other Commands

The session manager integrates well with other py2to3 commands:

```bash
# Start a session
./py2to3 session start --description "Fixing core modules"

# Run verification
./py2to3 check src/core/

# Apply fixes
./py2to3 fix src/core/ --backup

# Record your work
./py2to3 session task "Fixed core modules"
./py2to3 session note "Some manual fixes required in database.py"

# Generate report
./py2to3 report -o migration_report.html

# End session
./py2to3 session end --summary "Core modules completed and verified"
```

## Data Storage

Session data is stored in `.py2to3/` directory:

- `.py2to3/sessions.json` - Completed session history
- `.py2to3/active_session.json` - Currently active session

The data is stored in JSON format and can be:
- Backed up with version control (consider gitignoring for privacy)
- Exported for analysis
- Shared with team members
- Used for project reporting

## Tips and Best Practices

### 1. Be Consistent

Start a session every time you work on migration:

```bash
# Good habit
./py2to3 session start
# ... do your work ...
./py2to3 session end
```

### 2. Record Tasks Frequently

Don't wait until the end - record tasks as you complete them:

```bash
# After fixing each file
./py2to3 session file src/utils.py
./py2to3 session task "Fixed utils.py imports and print statements"
```

### 3. Use Descriptive Summaries

Help your future self and teammates understand what was done:

```bash
# Vague
./py2to3 session end --summary "Did stuff"

# Better
./py2to3 session end --summary "Migrated 5 files in data layer, all tests passing"
```

### 4. Track Breaks Accurately

Use pause/resume for accurate time tracking:

```bash
# Going to a meeting
./py2to3 session pause

# Back from meeting
./py2to3 session resume
```

### 5. Add Context with Notes

Record issues, decisions, and observations:

```bash
./py2to3 session note "Found compatibility issue with Python 3.6"
./py2to3 session note "Decided to target Python 3.8+ for new features"
./py2to3 session note "Need to update requirements.txt"
```

### 6. Regular Reporting

Generate reports regularly for visibility:

```bash
# Weekly report
./py2to3 session report -o weekly_report_$(date +%Y%m%d).txt

# Share with team
cat weekly_report_*.txt
```

## Use Cases

### Project Management

- Track actual time vs. estimated time
- Calculate burn rate and velocity
- Forecast completion dates
- Identify bottlenecks

### Team Collaboration

- Coordinate work across developers
- Avoid duplicate effort
- Share progress and blockers
- Maintain team accountability

### Documentation

- Create audit trail of migration work
- Document decisions and issues
- Generate progress reports for stakeholders
- Support retrospectives

### Personal Productivity

- Understand your work patterns
- Identify productive times
- Track learning and improvements
- Celebrate progress

## Advanced Usage

### Scripting with Sessions

You can script common workflows:

```bash
#!/bin/bash
# migration_workflow.sh

# Start session
./py2to3 session start --description "$1"

# Run preflight checks
./py2to3 preflight "$2"

# Apply fixes
./py2to3 fix "$2" --backup

# Record work
./py2to3 session task "Ran fixer on $2"

# Verify results
./py2to3 check "$2"

# End session
./py2to3 session end --summary "Completed migration of $2"
```

Usage:
```bash
./migration_workflow.sh "Core module migration" src/core/
```

### Analyzing Session Data

The JSON files can be analyzed with other tools:

```python
import json

# Load sessions
with open('.py2to3/sessions.json') as f:
    sessions = json.load(f)

# Calculate total time
total_seconds = sum(s['duration_seconds'] for s in sessions)
total_hours = total_seconds / 3600

print(f"Total migration time: {total_hours:.1f} hours")

# Files per hour
total_files = sum(len(s['files_modified']) for s in sessions)
velocity = total_files / total_hours

print(f"Velocity: {velocity:.2f} files/hour")
```

## Troubleshooting

### "Session already active" Error

End the current session first:

```bash
./py2to3 session status  # Check current session
./py2to3 session end     # End it
./py2to3 session start   # Start new one
```

### Lost Session After Crash

If your session was interrupted, you can still end it:

```bash
./py2to3 session status  # Check if session exists
./py2to3 session end --summary "Session interrupted"
```

### Incorrect Time Tracking

Remember to pause during breaks:

```bash
# Before break
./py2to3 session pause

# After break
./py2to3 session resume
```

### Cannot Start Session

Check for active session file:

```bash
ls -la .py2to3/
cat .py2to3/active_session.json
```

Remove manually if needed:
```bash
rm .py2to3/active_session.json
```

## See Also

- [JOURNAL_GUIDE.md](JOURNAL_GUIDE.md) - Track migration events and changes
- [TIMELINE_GUIDE.md](TIMELINE_GUIDE.md) - Visualize migration progress over time
- [STATUS_GUIDE.md](STATUS_GUIDE.md) - View current migration status
- [PLANNER_GUIDE.md](PLANNER_GUIDE.md) - Plan migration strategy
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI reference

## Questions?

The Session Manager helps you understand and improve your migration process. Use it to track work, measure progress, and plan effectively.

For more information, see the main README or run:

```bash
./py2to3 session --help
```
