# Pattern Search Guide

## Overview

The **Pattern Search** feature allows you to search for specific Python 2 patterns in your codebase with context and highlighting. This is a powerful tool for understanding your migration scope, planning targeted fixes, and finding patterns that need attention.

## Why Use Pattern Search?

Unlike the `check` command which performs a comprehensive compatibility check, the `search` command is designed for:

- **Quick Pattern Discovery**: Find all instances of a specific Python 2 pattern (e.g., "where are all my print statements?")
- **Targeted Analysis**: Focus on specific patterns before fixing them
- **Migration Planning**: Understand the scope of specific issues
- **Custom Workflows**: Create your own migration strategy by pattern type
- **Code Review**: Identify patterns not caught by automated tools
- **Learning**: Understand what Python 2 patterns exist in your code

## Basic Usage

### Search All Patterns

Search your entire project for all known Python 2 patterns:

```bash
./py2to3 search src/
```

### Search Specific Patterns

Search for specific patterns only:

```bash
# Search for print statements
./py2to3 search src/ -p print_statement

# Search for multiple specific patterns
./py2to3 search src/ -p xrange iteritems basestring

# Search for dictionary iterator methods
./py2to3 search src/ -p iteritems iterkeys itervalues
```

### List Available Patterns

See all patterns that can be searched:

```bash
./py2to3 search --list-patterns
```

## Available Patterns

The search tool recognizes these Python 2 patterns:

| Pattern Name | Description | Example |
|-------------|-------------|---------|
| `print_statement` | Print statements (not function calls) | `print "hello"` |
| `except_comma` | Old-style exception syntax | `except Exception, e:` |
| `iteritems` | dict.iteritems() method | `dict.iteritems()` |
| `iterkeys` | dict.iterkeys() method | `dict.iterkeys()` |
| `itervalues` | dict.itervalues() method | `dict.itervalues()` |
| `xrange` | xrange() function | `xrange(10)` |
| `basestring` | basestring type | `isinstance(x, basestring)` |
| `unicode` | unicode() function | `unicode(text)` |
| `long_type` | long() type | `long(123)` |
| `urllib2` | urllib2 module (renamed) | `import urllib2` |
| `configparser` | ConfigParser module (renamed) | `import ConfigParser` |
| `raw_input` | raw_input() function | `raw_input("Enter: ")` |
| `execfile` | execfile() function | `execfile("script.py")` |
| `has_key` | dict.has_key() method | `dict.has_key(key)` |
| `oldstyle_class` | Old-style class definition | `class MyClass:` |
| `cmp_function` | cmp() function | `cmp(a, b)` |
| `apply` | apply() function | `apply(func, args)` |
| `reduce` | reduce() function (moved) | `reduce(lambda x,y: x+y, list)` |
| `file_builtin` | file() builtin | `file("path.txt")` |

## Advanced Options

### Adjust Context Lines

By default, the search shows 2 lines of context around each match. You can adjust this:

```bash
# Show 5 lines of context
./py2to3 search src/ -p xrange -c 5

# Show only 1 line of context
./py2to3 search src/ -p print_statement -c 1
```

### JSON Output

Export results as JSON for automation or further processing:

```bash
# Output to console as JSON
./py2to3 search src/ -p xrange --json

# Save JSON to file
./py2to3 search src/ -o search_results.json
```

JSON output includes:
- Summary statistics
- Pattern counts
- Detailed match information with file, line, column
- Context lines for each match

### Disable Color

For scripts or when redirecting to files:

```bash
./py2to3 search src/ --no-color > search_output.txt
```

## Example Workflows

### Workflow 1: Phased Migration by Pattern Type

Tackle patterns one at a time:

```bash
# Step 1: Find all print statements
./py2to3 search src/ -p print_statement

# Step 2: Fix print statements
./py2to3 fix src/ --pattern print

# Step 3: Find all iterator methods
./py2to3 search src/ -p iteritems iterkeys itervalues

# Step 4: Fix iterator methods
./py2to3 fix src/ --pattern iter
```

### Workflow 2: Pre-Migration Assessment

Understand what you're dealing with before starting:

```bash
# Get full picture
./py2to3 search src/ -o assessment.json

# Focus on high-priority patterns
./py2to3 search src/ -p except_comma xrange basestring
```

### Workflow 3: Code Review Focus

After automated fixes, find patterns that might need manual attention:

```bash
# Search for patterns that often need manual review
./py2to3 search src/ -p unicode basestring oldstyle_class
```

### Workflow 4: CI/CD Integration

Use in continuous integration:

```bash
# In your CI script
./py2to3 search src/ -o ci_search_results.json
if [ $? -ne 0 ]; then
  echo "Python 2 patterns found - see ci_search_results.json"
  exit 1
fi
```

The command exits with status 1 if patterns are found, making it perfect for CI/CD gates.

## Understanding the Output

### Terminal Output Format

```
================================================================================
Python 2 Pattern Search Results
================================================================================

Summary:
  Total matches: 12
  Patterns found: 2
  Files affected: 3

Pattern Counts:
  xrange                 8 matches - xrange() function
  iteritems              4 matches - dict.iteritems() method

Detailed Results:

[xrange] xrange() function
Example: xrange(10)
Found 8 occurrence(s):

  src/example.py
    Line 42, Column 15:
         40  def process_items():
         41      items = []
      →  42      for i in xrange(100):
         43          items.append(i)
         44      return items
```

The `→` symbol indicates the line with the match. Context lines are shown before and after for clarity.

### JSON Output Format

```json
{
  "summary": {
    "total_matches": 12,
    "patterns_found": 2,
    "files_affected": 3,
    "pattern_counts": {
      "xrange": 8,
      "iteritems": 4
    }
  },
  "statistics": {
    "xrange": 8,
    "iteritems": 4,
    "total": 12
  },
  "patterns": {
    "xrange": {
      "description": "xrange() function",
      "matches": [
        {
          "file": "src/example.py",
          "line": 42,
          "column": 15,
          "matched_text": "xrange(",
          "full_line": "    for i in xrange(100):",
          "context": [...],
          "context_start_line": 40,
          "highlight_line": 2
        }
      ]
    }
  }
}
```

## Tips and Best Practices

### 1. Start Specific, Then Go Broad

Begin with specific patterns you know are problematic:

```bash
# Start with known issues
./py2to3 search src/ -p print_statement

# Then expand
./py2to3 search src/ -p print_statement xrange iteritems

# Finally, do full search
./py2to3 search src/
```

### 2. Use with Other Commands

Combine with other py2to3 commands:

```bash
# Search for patterns
./py2to3 search src/ -p xrange

# Estimate migration effort
./py2to3 plan src/

# Run preflight checks
./py2to3 preflight src/

# Apply fixes
./py2to3 fix src/
```

### 3. Export for Documentation

Create documentation of what needs fixing:

```bash
# Export current state
./py2to3 search src/ -o before_migration.json

# After fixes
./py2to3 search src/ -o after_migration.json

# Compare in reports
```

### 4. Focus on High-Impact Patterns

Some patterns are more critical than others:

```bash
# Critical patterns that often cause runtime errors
./py2to3 search src/ -p except_comma xrange iteritems

# Type-related patterns needing careful review
./py2to3 search src/ -p basestring unicode long_type
```

### 5. False Positives

The search uses regex patterns and may find false positives:
- Comments containing pattern names
- Strings that look like code
- Pattern names in documentation

Review results carefully and use context to determine real matches.

## Integration with Other Tools

### With Git

Track pattern elimination over time:

```bash
# Before migration
git checkout main
./py2to3 search src/ -o main_patterns.json

# After migration
git checkout migration-branch
./py2to3 search src/ -o migration_patterns.json

# Compare (manually or with tools)
```

### With Custom Scripts

Parse JSON output for custom workflows:

```python
import json

with open('search_results.json') as f:
    results = json.load(f)

# Count patterns
for pattern, count in results['summary']['pattern_counts'].items():
    print(f"{pattern}: {count} occurrences")

# Find files with most issues
file_counts = {}
for pattern_data in results['patterns'].values():
    for match in pattern_data['matches']:
        file = match['file']
        file_counts[file] = file_counts.get(file, 0) + 1

# Show top 5 files
for file, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"{file}: {count} patterns")
```

### With CI/CD

Add to your continuous integration pipeline:

```yaml
# GitHub Actions example
- name: Search for Python 2 patterns
  run: |
    ./py2to3 search src/ -o search_results.json
    
- name: Upload search results
  uses: actions/upload-artifact@v3
  with:
    name: pattern-search-results
    path: search_results.json
```

## Comparison with Other Commands

| Command | Purpose | Use When |
|---------|---------|----------|
| `search` | Find specific patterns | You want to focus on particular issues |
| `check` | Full compatibility check | You want comprehensive analysis |
| `fix` | Apply fixes | You're ready to modify code |
| `preflight` | Pre-migration validation | You're planning migration |
| `plan` | Strategic planning | You need migration roadmap |
| `status` | Quick overview | You want current state |

## Troubleshooting

### "No patterns found" but you know there are issues

- Check the path is correct
- Verify you're searching the right directory
- Try `--list-patterns` to see available pattern names
- Some patterns might be in comments or strings (false negatives)

### Too many false positives

- Use more specific patterns
- Adjust context with `-c` to better understand matches
- Export to JSON and filter programmatically

### Performance with large codebases

The search is efficient, but for very large projects:
- Search specific subdirectories
- Use specific patterns instead of searching all
- Run in parallel for different directories

## Summary

The pattern search command is a powerful tool for:
- Understanding your Python 2 codebase
- Planning migration strategies
- Finding specific issues quickly
- Creating custom migration workflows
- Integrating with automation tools

Start with `./py2to3 search --list-patterns` to see what you can find, then use `./py2to3 search src/` to analyze your code!

For more migration tools, see:
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI documentation
- [PLANNER_GUIDE.md](PLANNER_GUIDE.md) - Migration planning
- [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md) - Interactive fixing
- [STATUS_GUIDE.md](STATUS_GUIDE.md) - Status tracking
