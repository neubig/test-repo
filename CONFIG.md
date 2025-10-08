# Configuration Guide

The `py2to3` toolkit supports flexible configuration through JSON configuration files, allowing you to customize default behaviors and avoid repetitive command-line flags.

## Configuration Files

The toolkit supports two levels of configuration:

1. **User-level config**: `~/.py2to3/config.json` - Global settings for all your projects
2. **Project-level config**: `.py2to3.config.json` - Project-specific settings (in project root)

Project-level configuration takes precedence over user-level configuration.

## Quick Start

### Initialize a Project Configuration

```bash
# Create a config file in the current directory
py2to3 config init

# Create with a custom path
py2to3 config init --path /path/to/.py2to3.config.json
```

### Initialize User Configuration

```bash
# Create a user-level config file
py2to3 config init --user
```

### View Current Configuration

```bash
# Show all active configuration
py2to3 config show
```

### Get a Configuration Value

```bash
# Get a specific value
py2to3 config get backup_dir

# Get nested values using dot notation
py2to3 config get fix_rules.fix_print_statements
```

### Set a Configuration Value

```bash
# Set a value in project config
py2to3 config set backup_dir "my_backups"

# Set a value in user config
py2to3 config set backup_dir "my_backups" --user

# Set boolean values
py2to3 config set auto_confirm true

# Set nested values
py2to3 config set fix_rules.fix_print_statements false
```

### Show Configuration File Paths

```bash
# Show project config path
py2to3 config path

# Show user config path
py2to3 config path --user
```

## Configuration Options

### General Settings

```json
{
  "version": "1.0.0",
  "backup_dir": "backup",
  "report_output": "migration_report.html",
  "auto_confirm": false,
  "verbose": false,
  "no_color": false
}
```

- **`backup_dir`**: Default directory for backup files (default: `"backup"`)
- **`report_output`**: Default filename for HTML reports (default: `"migration_report.html"`)
- **`auto_confirm`**: Skip confirmation prompts (default: `false`)
- **`verbose`**: Enable verbose output by default (default: `false`)
- **`no_color`**: Disable colored output (default: `false`)

### Ignore Patterns

```json
{
  "ignore_patterns": [
    "**/node_modules/**",
    "**/venv/**",
    "**/env/**",
    "**/.git/**",
    "**/build/**",
    "**/dist/**",
    "**/__pycache__/**",
    "**/*.pyc"
  ]
}
```

Patterns to exclude from scanning and processing. Uses glob-style patterns.

### Fix Rules

```json
{
  "fix_rules": {
    "fix_print_statements": true,
    "fix_imports": true,
    "fix_exceptions": true,
    "fix_iterators": true,
    "fix_unicode": true,
    "fix_comparisons": true
  }
}
```

Control which automatic fixes are applied:

- **`fix_print_statements`**: Convert `print "x"` to `print("x")` (default: `true`)
- **`fix_imports`**: Update Python 2 imports to Python 3 (default: `true`)
- **`fix_exceptions`**: Fix exception syntax (default: `true`)
- **`fix_iterators`**: Update iterator methods (default: `true`)
- **`fix_unicode`**: Handle unicode/string changes (default: `true`)
- **`fix_comparisons`**: Fix comparison methods (default: `true`)

### Verification Rules

```json
{
  "verify_rules": {
    "check_syntax": true,
    "check_imports": true,
    "check_deprecated": true
  }
}
```

Control verification checks:

- **`check_syntax`**: Verify Python 3 syntax compatibility (default: `true`)
- **`check_imports`**: Check for Python 2-only imports (default: `true`)
- **`check_deprecated`**: Check for deprecated patterns (default: `true`)

## Usage Examples

### Example 1: Project with Custom Backup Directory

```bash
# Initialize config
py2to3 config init

# Set custom backup directory
py2to3 config set backup_dir ".migration_backups"

# Now all commands will use this backup directory
py2to3 fix src/
# Will backup to .migration_backups/ instead of backup/
```

### Example 2: Team Configuration

Create `.py2to3.config.json` in your project root:

```json
{
  "version": "1.0.0",
  "backup_dir": "backups/py2to3",
  "report_output": "reports/migration.html",
  "auto_confirm": false,
  "ignore_patterns": [
    "**/tests/**",
    "**/docs/**",
    "**/node_modules/**"
  ],
  "fix_rules": {
    "fix_print_statements": true,
    "fix_imports": true,
    "fix_exceptions": true,
    "fix_iterators": true,
    "fix_unicode": true,
    "fix_comparisons": true
  }
}
```

Commit this file to your repository so all team members use the same settings.

### Example 3: User Preferences

Set your personal preferences that apply to all projects:

```bash
# Enable verbose output by default
py2to3 config set verbose true --user

# Disable colors (useful for CI/CD)
py2to3 config set no_color true --user

# Use a different default backup directory
py2to3 config set backup_dir ".backups" --user
```

### Example 4: Selective Fixing

If you want to apply only specific fixes:

```json
{
  "fix_rules": {
    "fix_print_statements": true,
    "fix_imports": true,
    "fix_exceptions": false,
    "fix_iterators": false,
    "fix_unicode": false,
    "fix_comparisons": false
  }
}
```

This configuration will only fix print statements and imports, leaving other patterns for manual review.

## Configuration Priority

When multiple configuration sources exist, they are merged in this order (later overrides earlier):

1. Default built-in configuration
2. User-level configuration (`~/.py2to3/config.json`)
3. Project-level configuration (`.py2to3.config.json`)
4. Command-line arguments (highest priority)

## Best Practices

1. **Version Control**: Commit project configuration (`.py2to3.config.json`) to share settings with your team
2. **User Config**: Use user-level config for personal preferences (editor settings, color preferences, etc.)
3. **Project Config**: Use project-level config for project-specific settings (ignore patterns, backup locations, etc.)
4. **Documentation**: Document any non-standard configuration choices in your project README
5. **Override When Needed**: Command-line arguments always override config file settings

## Troubleshooting

### Config file not found

```bash
# Check if config exists and where
py2to3 config path

# Show current active config
py2to3 config show
```

### Reset to defaults

```bash
# Remove project config
rm .py2to3.config.json

# Reinitialize with defaults
py2to3 config init
```

### Config not being applied

Verify the configuration is loaded correctly:

```bash
# Show what config is active
py2to3 config show

# Use verbose mode to see what's happening
py2to3 check src/ --verbose
```

## Advanced Usage

### Nested Configuration

Use dot notation to set nested values:

```bash
py2to3 config set fix_rules.fix_print_statements false
py2to3 config set verify_rules.check_syntax true
```

### JSON Values

Set complex values using JSON:

```bash
# Set an array
py2to3 config set ignore_patterns '["**/tests/**", "**/docs/**"]'

# Set an object
py2to3 config set fix_rules '{"fix_print_statements": true, "fix_imports": false}'
```

### Force Overwrite

When reinitializing configuration:

```bash
# Overwrite existing config
py2to3 config init --force
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI documentation
- [README](README.md) - General project overview
