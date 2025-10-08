# Migration Journal Guide

## Overview

The **Migration Journal** feature provides a comprehensive system for documenting your Python 2 to Python 3 migration journey. Keep track of decisions, issues, solutions, and insights in a searchable, organized knowledge base that helps your team collaborate effectively.

## Why Use the Migration Journal?

During a complex migration, many important decisions and learnings happen along the way. The journal helps you:

- 📝 **Document Decisions**: Record why you chose specific approaches
- 🐛 **Track Issues**: Keep a record of problems encountered and how they were solved
- 💡 **Share Insights**: Capture lessons learned for future reference
- 🔍 **Search History**: Quickly find past decisions and solutions
- 👥 **Team Collaboration**: Share knowledge across your team
- 📊 **Audit Trail**: Maintain a complete history for compliance and reference
- 📚 **Generate Documentation**: Export your journal as documentation

## Quick Start

### Adding Your First Entry

```bash
# Add a simple note
./py2to3 journal add "Started migration of authentication module"

# Add a decision with tags
./py2to3 journal add "Decided to use urllib instead of requests library for Python 3 compatibility" \
    --category decision \
    --tags urllib python3 dependencies \
    --files src/web/fetcher.py

# Document an issue
./py2to3 journal add "Unicode handling causing issues in email module" \
    --category issue \
    --tags unicode email \
    --files src/utils/email_sender.py
```

### Viewing Entries

```bash
# List all entries
./py2to3 journal list

# List only recent entries
./py2to3 journal list --limit 10

# Search for specific content
./py2to3 journal list --search "urllib"

# Filter by category
./py2to3 journal list --category decision
```

### Exporting Documentation

```bash
# Export as Markdown documentation
./py2to3 journal export migration_diary.md

# Export as JSON for further processing
./py2to3 journal export journal_backup.json --format json

# Export only specific categories
./py2to3 journal export decisions.md --category decision
```

## Entry Categories

The journal supports several categories to help organize your notes:

| Category | Purpose | Example Use |
|----------|---------|-------------|
| **decision** | Architecture or implementation decisions | "Using asyncio instead of threading for better Python 3 compatibility" |
| **issue** | Problems encountered during migration | "Dictionary iteration order causing test failures" |
| **solution** | How issues were resolved | "Fixed by using OrderedDict for Python 2/3 compatibility" |
| **insight** | Lessons learned or discoveries | "Mock library in Python 3 is now part of unittest.mock" |
| **todo** | Tasks that need to be completed | "Need to migrate database module next" |
| **question** | Open questions requiring answers | "Should we use type hints in migrated code?" |
| **general** | General notes and observations | "Team meeting scheduled for code review" |

## Command Reference

### `journal add` - Add New Entry

Add a new journal entry with optional metadata.

```bash
./py2to3 journal add "Your note content here" [OPTIONS]
```

**Options:**
- `--category {decision,issue,solution,insight,todo,question,general}` - Entry category (default: general)
- `--tags TAG [TAG ...]` - Tags for categorization
- `--files FILE [FILE ...]` - Related files
- `--author NAME` - Entry author (defaults to current user)

**Examples:**

```bash
# Simple note
./py2to3 journal add "Starting phase 2 of migration"

# Decision with context
./py2to3 journal add "Switching from print statements to logging module" \
    --category decision \
    --tags logging migration-pattern \
    --files src/utils/logger.py \
    --author "Alice"

# Issue documentation
./py2to3 journal add "Circular import detected in models module" \
    --category issue \
    --tags circular-import models \
    --files src/models/user.py src/models/profile.py
```

### `journal list` - List Entries

List journal entries with optional filtering.

```bash
./py2to3 journal list [OPTIONS]
```

**Options:**
- `--search TERM` - Search in entry content
- `--tags TAG [TAG ...]` - Filter by tags
- `--category CATEGORY` - Filter by category
- `--author AUTHOR` - Filter by author
- `--files FILE [FILE ...]` - Filter by related files
- `--limit N` - Limit number of results

**Examples:**

```bash
# List all entries
./py2to3 journal list

# Recent 5 entries
./py2to3 journal list --limit 5

# Search for specific term
./py2to3 journal list --search "unicode"

# Filter by multiple criteria
./py2to3 journal list --category decision --tags migration-pattern

# Find entries related to specific files
./py2to3 journal list --files src/utils/validator.py

# Find all entries by an author
./py2to3 journal list --author "Bob"
```

### `journal show` - Show Specific Entry

Display detailed information about a specific entry.

```bash
./py2to3 journal show ENTRY_ID
```

**Example:**

```bash
./py2to3 journal show entry_20240115_143022_123456
```

### `journal stats` - Show Statistics

Display comprehensive statistics about your journal.

```bash
./py2to3 journal stats
```

Shows:
- Total number of entries
- Breakdown by category
- Breakdown by author
- Top tags
- Number of related files
- Date range of entries

**Example Output:**

```
Total Entries: 47

Entries by Category:
  decision     12 entries
  issue         8 entries
  solution      8 entries
  insight       9 entries
  todo          6 entries
  question      3 entries
  general       1 entries

Entries by Author:
  Alice              23 entries
  Bob                18 entries
  Charlie             6 entries

Unique Tags: 28
  Top tags:
    migration-pattern    15 times
    unicode              10 times
    dependencies          8 times
    ...

Related Files: 34

Date Range:
  First: 2024-01-10T09:30:00
  Last:  2024-01-15T16:45:00
```

### `journal export` - Export Entries

Export journal entries for documentation or backup.

```bash
./py2to3 journal export OUTPUT_FILE [OPTIONS]
```

**Options:**
- `--format {markdown,json}` - Export format (default: markdown)
- `--category CATEGORY` - Export only this category
- `--tags TAG [TAG ...]` - Export only entries with these tags

**Examples:**

```bash
# Export complete journal as Markdown
./py2to3 journal export migration_diary.md

# Export as JSON for backup
./py2to3 journal export backup.json --format json

# Export only decisions
./py2to3 journal export decisions_made.md --category decision

# Export entries with specific tags
./py2to3 journal export unicode_migration.md --tags unicode encoding
```

### `journal import` - Import Entries

Import journal entries from a JSON export.

```bash
./py2to3 journal import INPUT_FILE
```

**Example:**

```bash
# Import entries from another project
./py2to3 journal import ../other-project/.migration_journal.json

# Import from backup
./py2to3 journal import backup.json
```

**Note:** Duplicate entries (same ID) are automatically skipped.

### `journal delete` - Delete Entry

Delete a specific journal entry.

```bash
./py2to3 journal delete ENTRY_ID [OPTIONS]
```

**Options:**
- `--confirm` - Skip confirmation prompt

**Examples:**

```bash
# Delete with confirmation
./py2to3 journal delete entry_20240115_143022_123456

# Delete without confirmation
./py2to3 journal delete entry_20240115_143022_123456 --confirm
```

## Best Practices

### 1. Document as You Go

Don't wait until the end! Add entries throughout your migration:

```bash
# When starting a module
./py2to3 journal add "Starting migration of database module" \
    --category todo \
    --tags database phase-2

# When making a decision
./py2to3 journal add "Using six library for Python 2/3 compatibility in legacy code" \
    --category decision \
    --tags compatibility six legacy

# When encountering issues
./py2to3 journal add "bytes vs str causing comparison errors" \
    --category issue \
    --tags bytes encoding
```

### 2. Use Consistent Tags

Create a tag vocabulary for your project:

**Common tags:**
- `python2-pattern` - Python 2 specific patterns
- `python3-pattern` - Python 3 replacements
- `compatibility` - Compatibility layers
- `breaking-change` - Breaking changes
- `performance` - Performance considerations
- `testing` - Testing-related notes
- `dependencies` - Dependency issues
- `unicode` - Unicode/encoding issues
- `imports` - Import changes

### 3. Link to Files

Always reference related files for context:

```bash
./py2to3 journal add "Refactored string handling to use six.text_type" \
    --category solution \
    --files src/utils/text.py src/utils/validators.py \
    --tags unicode six compatibility
```

### 4. Regular Exports

Export your journal regularly for backup and documentation:

```bash
# Daily or weekly backups
./py2to3 journal export backups/journal_$(date +%Y%m%d).json --format json

# Generate documentation at milestones
./py2to3 journal export docs/migration_progress_week1.md
```

### 5. Team Collaboration

Use author attribution for team environments:

```bash
# Set author explicitly
./py2to3 journal add "Code review feedback: need better error handling" \
    --category todo \
    --author "ReviewerName"

# Filter by team member
./py2to3 journal list --author "Alice"
```

## Integration with Workflow

### During Migration

```bash
# 1. Before starting work
./py2to3 journal add "Starting work on authentication module" --category todo

# 2. Run preflight checks
./py2to3 preflight src/auth/

# 3. Document initial state
./py2to3 journal add "Found 23 issues in auth module, mostly print statements and imports" \
    --category insight \
    --files src/auth/

# 4. Apply fixes
./py2to3 fix src/auth/

# 5. Document results
./py2to3 journal add "Applied automatic fixes. Manual review needed for custom exceptions" \
    --category solution \
    --tags auth fixes manual-review

# 6. Document decisions during manual fixes
./py2to3 journal add "Chose to use structlog instead of standard logging for better Python 3 support" \
    --category decision \
    --tags logging dependencies
```

### Code Review Process

```bash
# Before code review
./py2to3 journal export review_notes.md --category decision

# Document review feedback
./py2to3 journal add "Code review: Add type hints to public APIs" \
    --category todo \
    --tags code-review type-hints
```

### Team Handoffs

```bash
# Export your work
./py2to3 journal export handoff_notes.md --author "YourName"

# Import team member's work
./py2to3 journal import ../teammate-branch/.migration_journal.json
```

## Advanced Usage

### Programmatic Access

You can also use the journal module directly in Python:

```python
from migration_journal import MigrationJournal

# Create journal
journal = MigrationJournal('.migration_journal.json')

# Add entry
entry = journal.add_entry(
    content="Automated script completed successfully",
    tags=["automation", "batch-processing"],
    category="insight"
)

# Query entries
unicode_issues = journal.get_entries(
    tags=["unicode"],
    category="issue"
)

# Get statistics
stats = journal.get_statistics()
print(f"Total entries: {stats['total_entries']}")
```

### Custom Journal Location

```bash
# Use a different journal file
./py2to3 journal --journal-path custom_journal.json add "Custom location entry"

# Per-module journals
./py2to3 journal --journal-path src/auth/.journal.json add "Auth module note"
```

### Timeline Analysis

```bash
# Get statistics to see your migration timeline
./py2to3 journal stats

# Export by time period (using search)
./py2to3 journal export week1.md --search "2024-01-"
```

## Tips and Tricks

### Quick Issue Tracking

```bash
# Add issues quickly
alias journal-issue='./py2to3 journal add --category issue'
journal-issue "Unicode error in email module" --tags unicode email

# Track solutions
alias journal-solution='./py2to3 journal add --category solution'
journal-solution "Fixed by using .encode('utf-8')" --tags unicode
```

### Daily Standups

```bash
# Export today's work
./py2to3 journal list --search "$(date +%Y-%m-%d)" > today.txt

# Show your recent work
./py2to3 journal list --author "$USER" --limit 10
```

### Migration Retrospective

```bash
# Export insights for retrospective
./py2to3 journal export insights.md --category insight

# Review all issues encountered
./py2to3 journal list --category issue > issues_retrospective.txt
```

### Knowledge Base

```bash
# Build a searchable knowledge base
./py2to3 journal export full_migration_knowledge.md

# Find solutions to similar problems
./py2to3 journal list --search "circular import" --category solution
```

## Storage and Format

### Storage Location

By default, the journal is stored in `.migration_journal.json` in your project root. This is a JSON file that's easy to version control, backup, and share.

### Version Control

```bash
# Add to git (recommended for team collaboration)
git add .migration_journal.json
git commit -m "Update migration journal"

# Or add to .gitignore if you prefer private notes
echo ".migration_journal.json" >> .gitignore
```

### Backup Strategy

```bash
# Regular backups
cp .migration_journal.json backups/journal_$(date +%Y%m%d).json

# Or use the export feature
./py2to3 journal export backups/journal_$(date +%Y%m%d).json --format json
```

## Examples from Real Migrations

### Example 1: Django Project Migration

```bash
./py2to3 journal add "Starting Django 1.11 to 3.2 migration path" \
    --category decision \
    --tags django upgrade-path

./py2to3 journal add "Must upgrade to Django 2.2 first (LTS to LTS path)" \
    --category decision \
    --tags django dependencies

./py2to3 journal add "Found middleware syntax changes" \
    --category issue \
    --files myproject/middleware.py

./py2to3 journal add "Updated middleware to new-style MIDDLEWARE setting" \
    --category solution \
    --files myproject/settings.py myproject/middleware.py
```

### Example 2: Scientific Computing Project

```bash
./py2to3 journal add "NumPy array division behavior changed in Python 3" \
    --category issue \
    --tags numpy compatibility

./py2to3 journal add "Using from __future__ import division for backward compat" \
    --category solution \
    --tags numpy future-imports

./py2to3 journal add "All tests passing with both Python 2.7 and 3.8" \
    --category insight \
    --tags testing compatibility
```

### Example 3: CLI Tool Migration

```bash
./py2to3 journal add "Click library preferred over argparse for Py2/3 compat" \
    --category decision \
    --tags cli dependencies

./py2to3 journal add "Input/raw_input compatibility handled by six.moves" \
    --category solution \
    --tags input six compatibility

./py2to3 journal add "Consider adding type hints after migration complete" \
    --category todo \
    --tags future-improvement typing
```

## FAQ

**Q: Should I commit the journal to version control?**

A: Yes, if you're working in a team. The journal becomes a valuable shared knowledge base. If you prefer private notes, add it to `.gitignore`.

**Q: Can I have multiple journals?**

A: Yes! Use the `--journal-path` option to specify different journal files for different parts of your project.

**Q: How do I search for old decisions?**

A: Use `./py2to3 journal list --search "keyword" --category decision`

**Q: Can I edit an existing entry?**

A: Currently, you can delete and re-add entries. Entry editing will be added in a future version.

**Q: What's the best way to use this with code reviews?**

A: Export decision and solution entries before review: `./py2to3 journal export review_context.md --category decision`

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI reference
- [Migration Planner Guide](PLANNER_GUIDE.md) - Strategic migration planning
- [Status Reporter Guide](STATUS_GUIDE.md) - Track migration progress
- [Git Integration Guide](GIT_INTEGRATION.md) - Version control integration

---

**Next Steps:**
1. Start adding entries to your journal: `./py2to3 journal add "My first entry"`
2. Make it a habit to document decisions as you work
3. Export your journal at milestones for documentation
4. Share insights with your team using exports

Happy migrating! 📝
