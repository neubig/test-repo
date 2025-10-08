# Migration Package Export/Import Guide

## Overview

The Export/Import feature allows you to package migration configurations, state, and learnings into portable files that can be shared across teams and projects. This is invaluable for:

- **Team Collaboration**: Share migration strategies and configurations with team members
- **Project Templates**: Create reusable migration templates from successful migrations
- **Multi-Environment Deployment**: Move migration state between development, staging, and production
- **Knowledge Sharing**: Share learnings and configurations with other teams or the community
- **Backup**: Create complete snapshots of your migration configuration and state

## Quick Start

### Exporting a Migration Package

```bash
# Export everything (default)
./py2to3 export create

# Export with description and tags
./py2to3 export create -d "Django project migration template" -t "django,web,template"

# Export specific components only
./py2to3 export create --no-stats --no-journal -o my_migration_config.tar.gz

# Include backups (careful - can be large!)
./py2to3 export create --backups --backup-pattern "*.py"
```

### Importing a Migration Package

```bash
# Import a package (dry run first to preview)
./py2to3 import migration_export_20240115_120000.tar.gz --dry-run

# Actually import
./py2to3 import migration_export_20240115_120000.tar.gz

# Import only specific components
./py2to3 import package.tar.gz --no-stats --no-journal

# Overwrite existing data instead of merging
./py2to3 import package.tar.gz --overwrite
```

### Listing Available Packages

```bash
# List packages in current directory
./py2to3 export list

# List packages in specific directory
./py2to3 export list -d /path/to/packages
```

## Package Components

A migration package can include the following components:

### 1. Configuration Files ✅ (Included by default)
- Project configuration (`.py2to3.config.json`)
- User configuration (from home directory)
- Todo configuration (`todo_config.json`)

**Use cases:**
- Share team-wide configuration standards
- Maintain consistent settings across environments
- Bootstrap new projects with proven settings

### 2. Custom Recipes ✅ (Included by default)
- Custom fix patterns and rules
- Project-specific transformations
- Custom validation rules

**Use cases:**
- Share domain-specific migration patterns
- Reuse custom fixes across similar projects
- Build a library of organization-specific recipes

### 3. Migration State ✅ (Included by default)
- File-by-file migration status
- What's been migrated and what hasn't
- Migration checkpoints

**Use cases:**
- Resume migration in different environments
- Track progress across team members
- Coordinate parallel migration efforts

### 4. Journal Entries ✅ (Included by default)
- Migration decisions and rationale
- Issues encountered and solutions
- Notes and documentation

**Use cases:**
- Share institutional knowledge
- Document why certain approaches were taken
- Create case studies from migrations

### 5. Statistics Snapshots ✅ (Included by default)
- Historical progress data
- Metrics over time
- Trend analysis data

**Use cases:**
- Compare migration velocities
- Analyze what worked well
- Generate progress reports

### 6. Backup Files ❌ (Not included by default)
- Backup copies of original files
- Can be very large!

**Use cases:**
- Full project restoration
- Testing migration in isolation
- Complete project snapshots

**Warning:** Including backups can make packages very large. Use `--backup-pattern` to filter.

## Common Use Cases

### Use Case 1: Create a Project Template

After successfully migrating one project, create a template for similar projects:

```bash
# In your successfully migrated project
./py2to3 export create \
  -d "Flask API migration template" \
  -t "flask,api,template" \
  --no-state \
  --no-journal \
  -o flask_migration_template.tar.gz

# In a new similar project
./py2to3 import flask_migration_template.tar.gz
```

This gives you the configuration and recipes without the specific project state.

### Use Case 2: Share Migration Progress with Team

Export current state to share with team members:

```bash
# Export everything including current state
./py2to3 export create \
  -d "Customer API migration - Week 3 checkpoint" \
  -t "customer-api,checkpoint,week3" \
  -o api_migration_week3.tar.gz

# Team member imports to sync up
./py2to3 import api_migration_week3.tar.gz --merge
```

The `--merge` option combines the imported state with existing local state.

### Use Case 3: Deploy Migration to Production

Move tested migration from staging to production:

```bash
# In staging, after successful migration
./py2to3 export create \
  -d "Production-ready migration configuration" \
  -t "production,release-2.0" \
  --no-stats \
  -o prod_migration_config.tar.gz

# In production
./py2to3 import prod_migration_config.tar.gz --dry-run  # Preview first!
./py2to3 import prod_migration_config.tar.gz            # Actually import
```

### Use Case 4: Backup Before Major Changes

Create a complete snapshot before experimenting:

```bash
# Create backup with everything
./py2to3 export create \
  -d "Backup before trying new approach" \
  -t "backup,experiment" \
  --backups \
  -o backup_before_experiment.tar.gz

# Later, if needed, restore in a fresh directory
mkdir recovery && cd recovery
../py2to3 import ../backup_before_experiment.tar.gz --backups
```

### Use Case 5: Share Knowledge with Community

Create an anonymized template to share publicly:

```bash
# Export only recipes and configuration (no project-specific data)
./py2to3 export create \
  -d "Python 2 to 3 migration recipes for scientific computing" \
  -t "numpy,scipy,scientific,template,community" \
  --no-state \
  --no-journal \
  --no-stats \
  -o scientific_python_migration.tar.gz
```

## Command Reference

### Export Command

```bash
./py2to3 export create [OPTIONS] [PATH]
```

**Arguments:**
- `PATH`: Project path to export (default: current directory)

**Options:**
- `-o, --output FILE`: Output file path (default: `migration_export_TIMESTAMP.tar.gz`)
- `--config`: Include configuration files (default: enabled)
- `--no-config`: Exclude configuration files
- `--recipes`: Include custom recipes (default: enabled)
- `--no-recipes`: Exclude custom recipes
- `--state`: Include migration state (default: enabled)
- `--no-state`: Exclude migration state
- `--journal`: Include journal entries (default: enabled)
- `--no-journal`: Exclude journal entries
- `--stats`: Include statistics (default: enabled)
- `--no-stats`: Exclude statistics
- `--backups`: Include backup files (default: disabled)
- `--backup-pattern PATTERN`: Pattern to filter backups
- `-d, --description TEXT`: Package description
- `-t, --tags TAGS`: Comma-separated tags

**Examples:**
```bash
# Minimal export (just config and recipes)
./py2to3 export create --no-state --no-journal --no-stats

# Full export with backups
./py2to3 export create --backups

# Filtered backup export
./py2to3 export create --backups --backup-pattern "core_*.py"

# Export with metadata
./py2to3 export create -d "My template" -t "tag1,tag2" -o my_export.tar.gz
```

### Import Command

```bash
./py2to3 import PACKAGE [PATH] [OPTIONS]
```

**Arguments:**
- `PACKAGE`: Path to migration package file (required)
- `PATH`: Target project path (default: current directory)

**Options:**
- `--config`: Import configuration files (default: enabled)
- `--no-config`: Skip configuration files
- `--recipes`: Import custom recipes (default: enabled)
- `--no-recipes`: Skip custom recipes
- `--state`: Import migration state (default: enabled)
- `--no-state`: Skip migration state
- `--journal`: Import journal entries (default: enabled)
- `--no-journal`: Skip journal entries
- `--stats`: Import statistics (default: enabled)
- `--no-stats`: Skip statistics
- `--backups`: Import backup files (default: disabled)
- `--merge`: Merge with existing data (default: enabled)
- `--overwrite`: Overwrite existing data
- `-n, --dry-run`: Preview import without making changes

**Examples:**
```bash
# Preview what would be imported
./py2to3 import package.tar.gz --dry-run

# Import everything
./py2to3 import package.tar.gz

# Import only configuration and recipes
./py2to3 import package.tar.gz --no-state --no-journal --no-stats

# Overwrite existing configuration
./py2to3 import package.tar.gz --overwrite

# Import to specific directory
./py2to3 import package.tar.gz /path/to/project
```

### List Command

```bash
./py2to3 export list [OPTIONS]
```

**Options:**
- `-d, --directory DIR`: Directory to search (default: current directory)

**Examples:**
```bash
# List packages in current directory
./py2to3 export list

# List packages in specific directory
./py2to3 export list -d ~/migration_packages
```

## Package Format

Migration packages are compressed tarballs (`.tar.gz`) with the following structure:

```
migration_package/
├── manifest.json           # Package metadata
├── config/
│   ├── project_config.json
│   ├── user_config.json
│   └── todo_config.json
├── recipes/
│   └── *.json             # Custom recipes
├── state/
│   └── migration_state.json
├── journal/
│   └── migration_journal.json
├── stats/
│   └── *.json             # Statistics snapshots
└── backups/               # Optional
    └── *                  # Backup files
```

### Manifest Format

The `manifest.json` file contains package metadata:

```json
{
  "version": "1.0",
  "created_at": "2024-01-15T12:00:00",
  "project_path": "/path/to/original/project",
  "description": "Package description",
  "tags": ["tag1", "tag2"],
  "components": {
    "config": true,
    "recipes": true,
    "state": true,
    "journal": true,
    "stats": true,
    "backups": false
  },
  "files": ["config/project_config.json", ...],
  "file_count": 10
}
```

## Best Practices

### 1. Use Descriptive Names and Tags

```bash
# Good
./py2to3 export create \
  -d "Django 2.2 to 3.2 migration - Auth module patterns" \
  -t "django,auth,2.2-to-3.2,tested"

# Less useful
./py2to3 export create -d "Migration stuff" -t "misc"
```

### 2. Don't Include Backups by Default

Backup files can make packages extremely large. Only include them when necessary:

```bash
# For templates (no backups needed)
./py2to3 export create --no-backups  # default

# For full snapshots (when you need them)
./py2to3 export create --backups --backup-pattern "critical_module_*.py"
```

### 3. Use Dry Run Before Importing

Always preview imports to understand what will change:

```bash
# Always do this first
./py2to3 import package.tar.gz --dry-run

# Then actually import
./py2to3 import package.tar.gz
```

### 4. Version Your Packages

Include version information in descriptions and filenames:

```bash
./py2to3 export create \
  -d "Migration template v2.1 - Updated for Python 3.10+" \
  -o migration_template_v2.1.tar.gz
```

### 5. Use Merge for Incremental Updates

When sharing updates, use merge mode to preserve local changes:

```bash
# Import updates while keeping local modifications
./py2to3 import updated_config.tar.gz --merge
```

### 6. Create Template Packages

For team distribution, export only configuration and recipes:

```bash
./py2to3 export create \
  --no-state --no-journal --no-stats \
  -d "Team migration configuration v1.0" \
  -o team_config_v1.0.tar.gz
```

## Integration with Other Commands

### With Git Integration

```bash
# Export before major change
./py2to3 export create -d "Before refactoring" -o pre_refactor.tar.gz
./py2to3 git checkpoint "Pre-refactoring checkpoint"

# After successful refactoring
./py2to3 export create -d "After refactoring" -o post_refactor.tar.gz
./py2to3 git commit "refactoring-done"
```

### With Rollback

Export provides a different backup strategy than rollback:
- **Rollback**: Undo recent operations within same environment
- **Export**: Share or move configuration across environments

```bash
# Use both for maximum safety
./py2to3 export create -d "Before experiment" --backups
./py2to3 fix src/ --experimental-pattern
# If it works:
./py2to3 export create -d "After experiment - successful"
# If it doesn't:
./py2to3 rollback undo
```

### With Configuration Management

```bash
# Export current config
./py2to3 config show > current_config.txt
./py2to3 export create -d "Working configuration"

# Later, compare with imported config
./py2to3 import old_config.tar.gz --dry-run
./py2to3 config show > imported_config.txt
diff current_config.txt imported_config.txt
```

## Troubleshooting

### Package Size is Too Large

**Problem**: Package is hundreds of MB or larger

**Solution**: Don't include backups, or use pattern filtering:
```bash
./py2to3 export create --no-backups
# Or
./py2to3 export create --backups --backup-pattern "critical_*.py"
```

### Import Overwrites Local Changes

**Problem**: Import replaced local configuration

**Solution**: Use merge mode (default) or dry-run first:
```bash
./py2to3 import package.tar.gz --dry-run  # Preview
./py2to3 import package.tar.gz --merge    # Merge (default)
```

### Cannot Find Package Files

**Problem**: `py2to3 export list` shows no packages

**Solution**: Packages must be named `migration_export_*.tar.gz`:
```bash
# Will be found
migration_export_20240115_120000.tar.gz

# Won't be found
my_migration.tar.gz  # rename to migration_export_my_migration.tar.gz
```

### Import Fails with Permission Error

**Problem**: Cannot write to import destination

**Solution**: Check directory permissions:
```bash
# Check permissions
ls -la

# Import to different directory
./py2to3 import package.tar.gz /path/with/write/access
```

## Security Considerations

### What to Include in Public Packages

**Safe to share publicly:**
- Custom recipes and patterns
- General configuration (after review)
- Documentation and journal entries (after anonymization)

**DO NOT share publicly:**
- Project-specific paths and configuration
- Internal URLs, credentials, or secrets
- Proprietary business logic
- Company-specific naming conventions

### Review Before Sharing

```bash
# Extract and review before sharing
tar -xzf migration_export_20240115_120000.tar.gz
cd migration_package
# Review all JSON files for sensitive data
find . -name "*.json" -exec cat {} \;
```

## Examples

See the [examples](examples/export_import/) directory for:
- `basic_export.sh` - Simple export examples
- `team_template.sh` - Creating team templates
- `environment_deploy.sh` - Moving between environments
- `backup_restore.sh` - Backup and restore workflows

## See Also

- [Backup Guide](BACKUP_GUIDE.md) - File-level backups
- [Rollback Guide](ROLLBACK_GUIDE.md) - Undo operations
- [Configuration Guide](CONFIG.md) - Configuration management
- [Git Integration Guide](GIT_INTEGRATION.md) - Version control integration
- [Journal Guide](JOURNAL_GUIDE.md) - Migration journaling
