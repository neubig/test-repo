# Custom Rules Guide 🎨

**Extend the migration toolkit with your own patterns!**

The Custom Rules feature allows you to define, manage, and apply your own migration patterns beyond the built-in rules. Perfect for organization-specific coding standards, project-specific patterns, and custom library migrations.

## 🚀 Quick Start

```bash
# Initialize with example rules
./py2to3 rules init

# List all custom rules
./py2to3 rules list

# Add a new rule interactively
./py2to3 rules add

# Apply custom rules to a file
./py2to3 rules apply src/myfile.py

# Test a rule without making changes
./py2to3 rules test my_rule_id "print 'test'"
```

## 📋 Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Managing Rules](#managing-rules)
- [Rule Format](#rule-format)
- [Applying Rules](#applying-rules)
- [Sharing Rules](#sharing-rules)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

### What Are Custom Rules?

Custom rules are user-defined patterns that specify how to transform code during migration. Each rule consists of:

- **Pattern**: What to look for (regex or literal string)
- **Replacement**: What to replace it with
- **Metadata**: Name, description, category, settings

### Why Use Custom Rules?

- 🏢 **Organization Standards**: Enforce company-specific coding conventions
- 📦 **Custom Libraries**: Handle internal or third-party library migrations
- 🔧 **Special Cases**: Address patterns not covered by built-in rules
- 🤝 **Team Collaboration**: Share migration strategies across teams
- 🎯 **Precision Control**: Fine-tune migrations for your specific needs

## Getting Started

### Initialize Custom Rules

Create a rules file with helpful examples:

```bash
./py2to3 rules init
```

This creates `.py2to3_custom_rules.json` in your project directory with example rules.

### Check Rules Status

View all your custom rules:

```bash
./py2to3 rules list
```

Get detailed statistics:

```bash
./py2to3 rules stats
```

## Managing Rules

### Add a New Rule

#### Interactive Mode (Recommended for Beginners)

```bash
./py2to3 rules add
```

You'll be prompted for:
- Rule ID (unique identifier)
- Name (human-readable)
- Description
- Pattern to match
- Replacement text
- Category
- Options (regex, case-sensitive, etc.)

#### Command-Line Mode

```bash
./py2to3 rules add \
  --id "my_custom_rule" \
  --name "My Custom Pattern" \
  --description "Replaces old pattern with new pattern" \
  --pattern "old_function\(" \
  --replacement "new_function(" \
  --category "custom" \
  --regex
```

#### From JSON

```bash
# Create a rule JSON file
cat > my_rule.json << EOF
{
  "rule_id": "custom_logger",
  "name": "Custom Logger Migration",
  "description": "Update logger calls",
  "pattern": "logger\\.logMessage\\(",
  "replacement": "logger.log_message(",
  "category": "custom",
  "regex": true,
  "enabled": true
}
EOF

# Import the rule
./py2to3 rules import my_rule.json
```

### List Rules

```bash
# List all rules
./py2to3 rules list

# List by category
./py2to3 rules list --category imports

# List only enabled rules
./py2to3 rules list --enabled-only

# Detailed view
./py2to3 rules list --verbose
```

### Enable/Disable Rules

```bash
# Disable a rule
./py2to3 rules disable my_rule_id

# Enable a rule
./py2to3 rules enable my_rule_id
```

### Remove Rules

```bash
# Remove a specific rule
./py2to3 rules remove my_rule_id

# Remove with confirmation
./py2to3 rules remove my_rule_id --confirm
```

### View Rule Details

```bash
./py2to3 rules show my_rule_id
```

## Rule Format

### JSON Structure

```json
{
  "version": "1.0",
  "updated_at": "2024-01-15T10:30:00",
  "rules": [
    {
      "rule_id": "unique_identifier",
      "name": "Human Readable Name",
      "description": "Detailed description of what this rule does",
      "pattern": "regex_or_literal_pattern",
      "replacement": "replacement_text",
      "category": "custom",
      "enabled": true,
      "regex": true,
      "whole_word": false,
      "case_sensitive": true,
      "created_at": "2024-01-15T10:00:00",
      "applied_count": 0
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `rule_id` | string | Unique identifier (no spaces) |
| `name` | string | Human-readable name |
| `description` | string | Detailed explanation |
| `pattern` | string | Pattern to match (regex or literal) |
| `replacement` | string | Replacement text |
| `category` | string | Category (custom, imports, strings, etc.) |
| `enabled` | boolean | Whether rule is active |
| `regex` | boolean | Use regex matching (vs literal) |
| `whole_word` | boolean | Match whole words only |
| `case_sensitive` | boolean | Case-sensitive matching |
| `applied_count` | integer | Times rule has been applied |

### Pattern Syntax

#### Regular Expression Patterns

When `regex: true`:

```json
{
  "pattern": "old_function\\(([^)]*)\\)",
  "replacement": "new_function(\\1)"
}
```

**Common regex patterns:**
- `.` - Any character
- `\\.` - Literal dot (escaped)
- `\\(` - Literal parenthesis (escaped)
- `([^)]*)` - Capture group (anything except `)`)
- `\\1`, `\\2` - Backreferences to capture groups
- `\\b` - Word boundary
- `.*?` - Non-greedy match

#### Literal String Patterns

When `regex: false`:

```json
{
  "pattern": "from old_module import",
  "replacement": "from new_module import",
  "regex": false
}
```

Simpler but less flexible - exact string matching only.

## Applying Rules

### Apply to Files

```bash
# Apply all enabled rules to a file
./py2to3 rules apply src/myfile.py

# Apply specific rules only
./py2to3 rules apply src/myfile.py --rules rule1,rule2

# Apply without backup
./py2to3 rules apply src/myfile.py --no-backup

# Dry run (preview changes)
./py2to3 rules apply src/myfile.py --dry-run
```

### Apply to Directories

```bash
# Apply to all Python files in directory
./py2to3 rules apply src/ --recursive

# Apply to specific file patterns
./py2to3 rules apply src/ --pattern "*.py"

# Exclude certain paths
./py2to3 rules apply src/ --exclude "test_*,*_backup.py"
```

### Integrate with Fixer

Custom rules can be applied automatically during the fix process:

```bash
# Apply built-in + custom rules
./py2to3 fix src/ --custom-rules

# Use only custom rules
./py2to3 fix src/ --only-custom-rules
```

### Test Rules

Test a rule on sample content without making changes:

```bash
# Test with inline content
./py2to3 rules test my_rule_id "sample code here"

# Test with file content
./py2to3 rules test my_rule_id --file sample.py

# See before/after comparison
./py2to3 rules test my_rule_id --file sample.py --diff
```

## Sharing Rules

### Export Rules

Share rules with your team:

```bash
# Export all rules
./py2to3 rules export team_rules.json

# Export specific rules
./py2to3 rules export team_rules.json --rules rule1,rule2,rule3

# Export by category
./py2to3 rules export imports_rules.json --category imports
```

### Import Rules

Load rules from others:

```bash
# Import rules (skip duplicates)
./py2to3 rules import team_rules.json

# Import and overwrite existing
./py2to3 rules import team_rules.json --overwrite

# Preview before importing
./py2to3 rules import team_rules.json --dry-run
```

### Share via Git

Add rules to version control:

```bash
# Include in .gitignore (if private)
echo ".py2to3_custom_rules.json" >> .gitignore

# Or commit to share with team
git add .py2to3_custom_rules.json
git commit -m "Add custom migration rules"
```

## Examples

### Example 1: Custom Logger Migration

Replace organization-specific logger methods:

```json
{
  "rule_id": "company_logger_info",
  "name": "Company Logger Info",
  "description": "Replace logger.logInfo() with logger.info()",
  "pattern": "\\.logInfo\\(",
  "replacement": ".info(",
  "category": "custom",
  "regex": true,
  "enabled": true
}
```

### Example 2: Legacy Database API

Update old database connection calls:

```json
{
  "rule_id": "legacy_db_connect",
  "name": "Legacy Database Connection",
  "description": "Replace db.connect() with db.create_connection()",
  "pattern": "\\bdb\\.connect\\(",
  "replacement": "db.create_connection(",
  "category": "custom",
  "regex": true,
  "whole_word": true,
  "enabled": true
}
```

### Example 3: Import Path Updates

Update internal module paths:

```json
{
  "rule_id": "old_utils_import",
  "name": "Old Utils Import",
  "description": "Replace old utils import with new path",
  "pattern": "from company.old.utils import",
  "replacement": "from company.common.utils import",
  "category": "imports",
  "regex": false,
  "enabled": true
}
```

### Example 4: Deprecated Function with Arguments

Capture and transform function arguments:

```json
{
  "rule_id": "old_config_get",
  "name": "Old Config Get",
  "description": "Replace config.getValue(key) with config.get(key, default=None)",
  "pattern": "config\\.getValue\\(([^)]*)\\)",
  "replacement": "config.get(\\1, default=None)",
  "category": "custom",
  "regex": true,
  "enabled": true
}
```

### Example 5: String Formatting

Update old-style string formatting:

```json
{
  "rule_id": "custom_string_format",
  "name": "Custom String Format",
  "description": "Replace custom % formatting with .format()",
  "pattern": "\"%s: %s\" % \\(([^,]+), ([^)]+)\\)",
  "replacement": "\"{}: {}\".format(\\1, \\2)",
  "category": "strings",
  "regex": true,
  "enabled": true
}
```

## Best Practices

### 1. Start Simple

Begin with literal string patterns before moving to complex regex:

```json
// Good for beginners
{
  "pattern": "from old_module import",
  "replacement": "from new_module import",
  "regex": false
}
```

### 2. Test Before Applying

Always test rules on sample content:

```bash
./py2to3 rules test my_rule --file sample.py --diff
```

### 3. Use Descriptive IDs

Make rule IDs self-explanatory:

```
✓ Good: "legacy_logger_error", "db_connection_v2"
✗ Bad: "rule1", "fix_thing", "temp"
```

### 4. Add Detailed Descriptions

Help your future self and teammates:

```json
{
  "description": "Replaces legacy ErrorHandler.logError(msg, level) with new logger.log(level, msg). Note: argument order is reversed!"
}
```

### 5. Categorize Rules

Use consistent categories:

- `imports` - Import statement changes
- `strings` - String handling updates
- `functions` - Function call updates
- `classes` - Class definition changes
- `custom` - Project-specific patterns

### 6. Use Whole Word Matching

Avoid partial matches:

```json
{
  "pattern": "\\blog\\(",
  "whole_word": true  // Won't match "catalog()" or "dialog()"
}
```

### 7. Escape Special Characters

Properly escape regex special characters:

```
. → \\.
( → \\(
) → \\)
[ → \\[
\ → \\\\
```

### 8. Version Control Your Rules

Track rule changes over time:

```bash
git add .py2to3_custom_rules.json
git commit -m "Add custom rules for database migration"
```

### 9. Document Complex Patterns

Add comments in your rule management docs:

```json
{
  "name": "Complex Async Pattern",
  "description": "Replaces @async_decorator(timeout=N) with @asyncio.timeout(N). Note: Only works with literal timeout values, not variables."
}
```

### 10. Regular Maintenance

Review and update rules periodically:

```bash
# Check which rules are actually being used
./py2to3 rules stats

# Disable unused rules
./py2to3 rules disable rarely_used_rule
```

## Advanced Usage

### Combining Rules

Apply rules in specific order:

```bash
# Create rule chains for complex transformations
./py2to3 rules apply src/ --rules rule1,rule2,rule3 --ordered
```

### Conditional Rules

Enable/disable rules based on context:

```bash
# Enable rules for specific migration phase
./py2to3 rules enable phase1_*
./py2to3 rules apply src/

# Then switch to next phase
./py2to3 rules disable phase1_*
./py2to3 rules enable phase2_*
```

### Rule Templates

Create rule templates for common patterns:

```bash
# Export template rules
./py2to3 rules export templates.json --category templates

# Share with team
./py2to3 rules import templates.json --prefix "team_"
```

## Troubleshooting

### Pattern Not Matching

1. Test with simple literal pattern first
2. Check regex escaping
3. Try without `whole_word` option
4. Verify case sensitivity

### Too Many Matches

1. Make pattern more specific
2. Use word boundaries (`\\b`)
3. Add context to pattern
4. Enable `whole_word` option

### Replacement Not Working

1. Check backreference syntax (`\\1`, not `$1`)
2. Verify capture groups in pattern
3. Test with simple literal replacement first

### Rules File Corrupted

1. Check JSON syntax with validator
2. Restore from backup
3. Reinitialize: `./py2to3 rules init --force`

## Integration with Other Tools

### With Fixer

```bash
./py2to3 fix src/ --custom-rules --backup
```

### With Wizard

The wizard can guide you through creating custom rules:

```bash
./py2to3 wizard --advanced
```

### With Export/Import

Include rules in migration packages:

```bash
./py2to3 export create --include-custom-rules
```

## FAQ

**Q: Can I use Python code in patterns?**  
A: No, only regex patterns are supported. For complex logic, consider using the plugin system.

**Q: How do I share rules with my team?**  
A: Use `./py2to3 rules export` to create a shareable JSON file, then teammates can import it.

**Q: Can I apply rules to non-Python files?**  
A: Yes! Custom rules work on any text file, not just Python files.

**Q: Do custom rules run before or after built-in rules?**  
A: By default, built-in rules run first, then custom rules. Use `--only-custom-rules` to run only custom rules.

**Q: Can I test rules without modifying files?**  
A: Yes! Use `./py2to3 rules test` or `--dry-run` flag.

## See Also

- [CLI Guide](CLI_GUIDE.md) - Command-line interface reference
- [Fixer Guide](README.md#fixer-tool) - Automated fixing tool
- [Pattern Library](PATTERNS_GUIDE.md) - Built-in migration patterns
- [Configuration Guide](CONFIG.md) - Configuration options

## Contributing

Have a great custom rule? Share it!

1. Export your rule: `./py2to3 rules export my_rule.json --rules my_rule_id`
2. Submit to our community rule collection
3. Help others with similar migration challenges!

---

**Need Help?**

- Check examples: `./py2to3 rules list`
- Test rules: `./py2to3 rules test`
- View stats: `./py2to3 rules stats`

Happy migrating! 🎨✨
