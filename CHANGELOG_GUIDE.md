# Changelog Generator Guide

The **Changelog Generator** is an automated tool that generates comprehensive changelogs from your Python 2 to 3 migration activities. It consolidates information from git commits, migration journal entries, and statistics to create professional, well-structured changelogs.

## Overview

During a migration project, keeping stakeholders informed about progress and changes is crucial. The Changelog Generator automates this documentation process by:

- **Parsing git commits** to track code changes
- **Reading migration journal entries** for detailed migration notes
- **Analyzing statistics snapshots** to calculate metrics
- **Categorizing changes** by type (syntax, imports, fixes, features, etc.)
- **Detecting breaking changes** automatically
- **Generating professional markdown** in industry-standard formats

## Quick Start

### Basic Usage

Generate a changelog for your entire migration history:

```bash
./py2to3 changelog
```

This displays the changelog to stdout by default.

### Save to File

Save the changelog to a file:

```bash
./py2to3 changelog -o CHANGELOG.md
```

### Generate for Recent Changes

Generate a changelog for the last 30 days:

```bash
./py2to3 changelog --since "30 days ago" -o CHANGELOG.md
```

### Append to Existing Changelog

Add a new version entry to an existing changelog:

```bash
./py2to3 changelog --version "1.0.0" --append -o CHANGELOG.md
```

## Command Reference

### Basic Syntax

```bash
./py2to3 changelog [path] [options]
```

### Arguments

- `path` - Project directory (default: current directory)

### Options

#### Output Options

- `-o, --output FILE` - Write changelog to file (default: stdout)
- `--append` - Append to existing file instead of overwriting

#### Date Range Options

- `--since DATE` - Start date for changelog entries
  - ISO format: `2024-01-01`
  - Relative: `"30 days ago"`, `"1 week ago"`
- `--until DATE` - End date for changelog entries
  - ISO format: `2024-12-31`
  - `"now"` for current date

#### Format Options

- `--version VERSION` - Version string for the entry (default: "Unreleased")
- `--format {keepachangelog,simple}` - Changelog format style
  - `keepachangelog` - Industry-standard "Keep a Changelog" format (default)
  - `simple` - Simple categorized format

## Changelog Formats

### Keep a Changelog Format

The default format follows the [Keep a Changelog](https://keepachangelog.com/) standard:

```markdown
## [1.0.0] - 2024-01-15

### 📊 Migration Progress

- **Issues Fixed**: 127
- **Files Modified**: 45
- **Completion**: 89.5%

### ⚠️ BREAKING CHANGES

- Removed Python 2 print statement support
- Changed default string encoding to UTF-8

### Added

- Type hints for all public APIs
- Async/await support in web scraper

### Changed

- Updated all imports from Python 2 to Python 3
- Modernized exception handling syntax

### Fixed

- Fixed unicode string handling
- Resolved iterator method compatibility issues
```

### Simple Format

A straightforward categorized format:

```markdown
# 1.0.0 (2024-01-15)

## Migration Metrics

- Issues Fixed: 127
- Files Modified: 45
- Completion: 89.5%

## ⚠️ Breaking Changes

- Removed Python 2 print statement support
- Changed default string encoding to UTF-8

## Syntax

- Updated print statements to function calls
- Modernized exception handling

## Imports

- Changed urllib2 to urllib.request
- Updated ConfigParser to configparser

## Fixes

- Fixed unicode string handling
- Resolved dictionary iterator issues
```

## Use Cases

### 1. Regular Progress Updates

Generate weekly progress reports for stakeholders:

```bash
# Every Monday, generate last week's changes
./py2to3 changelog --since "7 days ago" --version "Week-$(date +%W)" -o weekly_report.md
```

### 2. Release Documentation

Create release notes when completing migration milestones:

```bash
# For version 1.0.0 release
./py2to3 changelog --since "v0.9.0" --version "1.0.0" --append -o CHANGELOG.md
```

### 3. Sprint Summaries

Document changes during agile sprints:

```bash
# Sprint 5 summary (2 weeks)
./py2to3 changelog --since "14 days ago" --version "Sprint-5" -o sprint_5_summary.md
```

### 4. Milestone Tracking

Track progress between major milestones:

```bash
# Changes between milestone 2 and 3
./py2to3 changelog --since "2024-03-01" --until "2024-04-01" --version "Milestone-3" -o CHANGELOG.md
```

### 5. Audit Trail

Create comprehensive audit documentation:

```bash
# Complete migration history
./py2to3 changelog --format keepachangelog -o MIGRATION_AUDIT.md
```

## Integration with Other Tools

### With Migration Journal

The changelog generator reads from your migration journal:

```bash
# Add journal entries during migration
./py2to3 journal add --category syntax --notes "Converted all print statements"

# Generate changelog including journal entries
./py2to3 changelog -o CHANGELOG.md
```

### With Git Integration

Changelog automatically includes git commit information:

```bash
# Make migration commits with descriptive messages
./py2to3 fix src/
./py2to3 git commit "fixes-applied" -m "Fixed syntax in core modules"

# Generate changelog from commits
./py2to3 changelog --since "last week" -o CHANGELOG.md
```

### With Statistics Tracking

Include migration metrics in your changelog:

```bash
# Collect stats regularly
./py2to3 stats collect --save

# Changelog will include before/after metrics
./py2to3 changelog --since "30 days ago" -o CHANGELOG.md
```

## Best Practices

### 1. **Generate Regularly**

Create changelogs at regular intervals to track steady progress:

```bash
# Weekly changelog generation
./py2to3 changelog --since "7 days ago" --append -o CHANGELOG.md
```

### 2. **Use Semantic Versioning**

Follow semantic versioning for version strings:

```bash
# Major version for breaking changes
./py2to3 changelog --version "2.0.0" -o CHANGELOG.md

# Minor version for new features
./py2to3 changelog --version "1.1.0" -o CHANGELOG.md

# Patch version for fixes
./py2to3 changelog --version "1.0.1" -o CHANGELOG.md
```

### 3. **Document Breaking Changes**

Use clear markers in journal entries for breaking changes:

```bash
./py2to3 journal add --category breaking --notes "BREAKING: Removed legacy Python 2 compatibility layer"
```

### 4. **Maintain Clean Git History**

Write descriptive commit messages that will appear in changelogs:

```bash
# Good commit messages
git commit -m "fix: Resolve unicode handling in data processor"
git commit -m "feat: Add type hints to public API"
git commit -m "refactor: Modernize exception handling syntax"
```

### 5. **Combine with Reviews**

Generate changelogs before code reviews:

```bash
# Review preparation
./py2to3 changelog --since "last sprint" -o review_notes.md
./py2to3 review src/ --output review_report.html
```

## Advanced Usage

### Custom Date Ranges

Generate changelogs for specific periods:

```bash
# Q1 2024 changelog
./py2to3 changelog \
  --since "2024-01-01" \
  --until "2024-03-31" \
  --version "Q1-2024" \
  -o CHANGELOG_Q1.md

# Between git tags
./py2to3 changelog \
  --since "v1.0" \
  --until "v2.0" \
  --version "2.0.0" \
  -o CHANGELOG.md
```

### Multiple Changelog Files

Maintain separate changelogs for different purposes:

```bash
# Developer changelog (detailed)
./py2to3 changelog --format simple -o CHANGELOG_DEV.md

# Stakeholder changelog (summarized)
./py2to3 changelog --format keepachangelog -o CHANGELOG.md

# Technical audit log
./py2to3 changelog --format simple -o TECHNICAL_CHANGES.md
```

### Automated Changelog in CI/CD

Include changelog generation in your CI/CD pipeline:

```yaml
# .github/workflows/migration.yml
- name: Generate Changelog
  run: |
    ./py2to3 changelog \
      --since "1 week ago" \
      --version "Build-${{ github.run_number }}" \
      --append \
      -o CHANGELOG.md
    
    git add CHANGELOG.md
    git commit -m "Update changelog" || true
    git push
```

## Troubleshooting

### No Changes Detected

If changelog is empty:

1. **Check journal entries**: `./py2to3 journal list`
2. **Verify git commits**: `git log --oneline`
3. **Check date range**: Ensure `--since` and `--until` include your changes
4. **Verify project path**: Ensure you're in the correct directory

### Missing Metrics

If metrics are not showing:

1. **Collect statistics**: `./py2to3 stats collect --save`
2. **Check stats directory**: Verify `.migration_stats/` exists
3. **Run verification**: `./py2to3 check . --report`

### Duplicate Entries

If you see duplicate entries when appending:

1. **Use `--append` carefully**: Only use when adding new versions
2. **Check date ranges**: Ensure new range doesn't overlap with existing entries
3. **Consider overwriting**: Generate full changelog without `--append`

### Format Issues

If output format looks wrong:

1. **Try different format**: Use `--format simple` or `--format keepachangelog`
2. **Check file encoding**: Ensure UTF-8 encoding for output file
3. **Validate markdown**: Use a markdown linter on generated file

## Examples

### Complete Workflow

A complete example of using the changelog generator throughout a migration:

```bash
# 1. Start migration and initialize tracking
./py2to3 wizard

# 2. During migration, add journal entries
./py2to3 journal add --category syntax --notes "Converted print statements in core modules"
./py2to3 journal add --category imports --notes "Updated all urllib2 imports"

# 3. Collect statistics regularly
./py2to3 stats collect --save

# 4. Make git commits with good messages
git add src/
git commit -m "fix: Update print statements to Python 3 syntax"

# 5. Generate changelog weekly
./py2to3 changelog --since "7 days ago" --append -o CHANGELOG.md

# 6. Final release changelog
./py2to3 changelog --version "1.0.0" --format keepachangelog -o CHANGELOG.md
```

### Team Communication

Generate different changelogs for different audiences:

```bash
# For developers (technical details)
./py2to3 changelog \
  --format simple \
  --since "sprint start" \
  -o DEVELOPER_NOTES.md

# For managers (high-level summary)
./py2to3 changelog \
  --format keepachangelog \
  --version "Sprint-5" \
  -o SPRINT_SUMMARY.md

# For stakeholders (metrics focused)
./py2to3 stats show --detailed > METRICS_REPORT.txt
./py2to3 changelog --version "Q1-2024" -o CHANGELOG.md
```

## Tips

1. **Start Early**: Begin generating changelogs from day one of migration
2. **Be Consistent**: Use the same format and version scheme throughout
3. **Automate**: Add changelog generation to your regular workflow
4. **Review Before Publishing**: Always review generated changelogs before sharing
5. **Keep Backups**: Version control your changelogs with git
6. **Link to Documentation**: Reference detailed guides in changelog entries
7. **Celebrate Progress**: Use changelogs to showcase completed work

## Related Tools

- **Migration Journal** (`./py2to3 journal`) - Add detailed migration notes
- **Statistics Tracker** (`./py2to3 stats`) - Track quantitative metrics
- **Git Integration** (`./py2to3 git`) - Create meaningful commits
- **Report Generator** (`./py2to3 report`) - Generate detailed HTML reports
- **Report Card** (`./py2to3 report-card`) - Get quality assessment

## Further Reading

- [Keep a Changelog](https://keepachangelog.com/) - Industry standard format
- [Semantic Versioning](https://semver.org/) - Version numbering guide
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message standard
- [CLI Guide](CLI_GUIDE.md) - Complete CLI documentation
- [Journal Guide](JOURNAL_GUIDE.md) - Migration journal documentation

---

**Pro Tip**: Combine changelog generation with report cards and dashboards for comprehensive migration communication:

```bash
# Complete communication package
./py2to3 changelog --version "1.0.0" -o CHANGELOG.md
./py2to3 report-card -o quality_report.md
./py2to3 dashboard
```

This gives you a complete picture: what changed (changelog), how well it was done (report card), and visual progress (dashboard).
