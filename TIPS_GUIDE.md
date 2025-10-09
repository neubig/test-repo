# Migration Tips & FAQ Guide 💡

Get instant answers to common Python 2 to 3 migration questions with the powerful `tips` command. This feature provides context-aware suggestions, quick solutions, and practical examples without needing to read full documentation.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Available Commands](#available-commands)
- [Use Cases](#use-cases)
- [Tip Topics](#tip-topics)
- [Examples](#examples)
- [Integration with Other Commands](#integration-with-other-commands)

## Overview

The Tips Engine is designed to provide:
- 📚 **Quick Reference**: Instant access to common migration patterns
- 🎯 **Context-Aware**: Scans your code and shows relevant tips
- 🔍 **Searchable**: Find tips by keyword, category, or topic
- 💡 **Practical Examples**: Before/after code comparisons
- ⚡ **Fast**: Get answers without reading comprehensive guides

### Why Use Tips?

- **For Beginners**: Learn Python 3 migration patterns quickly
- **For Teams**: Share common solutions and best practices
- **For Quick Reference**: Look up specific issues without searching docs
- **For Learning**: See examples of correct Python 3 code
- **For Validation**: Confirm your migration approach is correct

## Quick Start

### View All Available Topics

```bash
./py2to3 tips list
```

Shows all available tip topics with brief descriptions.

### Get Help on a Specific Topic

```bash
./py2to3 tips show print
```

Displays detailed information about print statement migration.

### Scan Your Code for Issues

```bash
./py2to3 tips scan src/
```

Analyzes your codebase and shows the most relevant tips based on detected Python 2 patterns.

### Search for Tips

```bash
./py2to3 tips search unicode
```

Finds all tips related to unicode handling.

## Available Commands

### `tips` - Show General Help

```bash
./py2to3 tips
```

Displays overview of the tips system with available actions.

### `tips list` - List All Topics

```bash
./py2to3 tips list
```

**Output**: Alphabetically sorted list of all available tip topics.

### `tips show <topic>` - Show Detailed Tip

```bash
./py2to3 tips show <topic>
```

**Arguments**:
- `topic` - Topic ID (from `tips list`)

**Options**:
- `--no-color` - Disable colored output

**Example**:
```bash
./py2to3 tips show imports
./py2to3 tips show unicode --no-color
```

**Output**: Comprehensive information including:
- Category and topic ID
- Problem description
- Multiple before/after examples
- Quick fix instructions
- Common mistakes to avoid
- Links to related comprehensive guides

### `tips search <query>` - Search Tips

```bash
./py2to3 tips search <query>
```

**Arguments**:
- `query` - Search term (matches topic ID, title, problem description, category)

**Options**:
- `--detail` - Show full tip information instead of just titles
- `--no-color` - Disable colored output

**Examples**:
```bash
# Quick search - shows matching topic titles
./py2to3 tips search exception

# Detailed search - shows full tip information
./py2to3 tips search dict --detail
```

### `tips categories` - List Categories

```bash
./py2to3 tips categories
```

**Output**: List of all categories with tip counts:
- built-ins (6 tips)
- strings (1 tip)
- imports (2 tips)
- iterators (1 tip)
- exceptions (1 tip)
- operators (1 tip)
- classes (2 tips)
- syntax (1 tip)
- advanced (1 tip)

### `tips category <name>` - Show Category Tips

```bash
./py2to3 tips category <name>
```

**Arguments**:
- `category_name` - Category name (from `tips categories`)

**Options**:
- `--detail` - Show full tip information
- `--no-color` - Disable colored output

**Examples**:
```bash
# List tips in category
./py2to3 tips category built-ins

# Show detailed tips
./py2to3 tips category imports --detail
```

### `tips scan <path>` - Scan and Get Relevant Tips

```bash
./py2to3 tips scan <path>
```

**Arguments**:
- `path` - Path to file or directory to scan

**Options**:
- `--max-tips N` - Maximum number of tips to show (default: 5)
- `--detail` - Show code examples in tips
- `--no-color` - Disable colored output

**Examples**:
```bash
# Quick scan - summary only
./py2to3 tips scan src/

# Detailed scan with examples
./py2to3 tips scan myfile.py --detail

# Show more tips
./py2to3 tips scan src/ --max-tips 10 --detail
```

**Output**:
1. List of detected Python 2 patterns with occurrence counts
2. Most relevant tips ordered by frequency
3. Detection count shown for each tip
4. Quick fixes and examples (with --detail)

## Use Cases

### 1. Learning Python 3 Migration

**Scenario**: You're new to Python 3 migration and want to learn common patterns.

```bash
# Start with the list
./py2to3 tips list

# Learn about each category
./py2to3 tips categories
./py2to3 tips category built-ins --detail

# Deep dive into specific topics
./py2to3 tips show print
./py2to3 tips show imports
./py2to3 tips show unicode
```

### 2. Quick Problem Solving

**Scenario**: You encounter a specific error and need a quick solution.

```bash
# Search for the issue
./py2to3 tips search "basestring"
./py2to3 tips search "iteritems"

# Get detailed help
./py2to3 tips show unicode --detail
```

### 3. Code Review Preparation

**Scenario**: Before reviewing migrated code, refresh on common issues.

```bash
# Scan the code being reviewed
./py2to3 tips scan path/to/code --detail

# Review specific categories relevant to the code
./py2to3 tips category imports --detail
./py2to3 tips category strings --detail
```

### 4. Team Training

**Scenario**: Training team members on Python 3 migration.

```bash
# Start with overview
./py2to3 tips list

# Walk through most common issues
./py2to3 tips show print
./py2to3 tips show unicode
./py2to3 tips show imports
./py2to3 tips show iterators

# Show project-specific issues
./py2to3 tips scan our-project/ --detail
```

### 5. Pre-Migration Assessment

**Scenario**: Understanding what issues exist before starting migration.

```bash
# Scan to identify issues
./py2to3 tips scan src/ --max-tips 10

# Get detailed help on top issues
./py2to3 tips show <topic> --detail

# Review related comprehensive guides
# (Links provided in each tip)
```

## Tip Topics

### Built-ins Category

1. **print** - Print Statement → Print Function
   - Adding parentheses
   - File redirection with `file=` parameter
   - Common gotchas

2. **input** - Input Function Changes
   - `raw_input()` → `input()`
   - Expression evaluation changes
   - Input validation

3. **dict_methods** - Dictionary Method Changes
   - `has_key()` removal
   - View objects vs lists
   - Sorting dictionaries

4. **reduce** - reduce() Function
   - Import from functools
   - Alternative approaches

5. **exec** - exec Statement
   - Statement to function conversion
   - Namespace handling

6. **long** - Long Integer Type
   - `long` → `int` unification
   - Removing `L` suffixes

### Strings Category

1. **unicode** - String and Unicode Handling
   - `basestring` → `str`
   - Unicode literals
   - Bytes vs strings
   - Encoding/decoding

### Imports Category

1. **imports** - Standard Library Module Renames
   - ConfigParser → configparser
   - urllib2 → urllib.request
   - Queue → queue
   - And many more...

2. **relative_imports** - Relative Import Changes
   - Explicit vs implicit imports
   - Dot notation

### Iterators Category

1. **iterators** - Iterator Methods and Functions
   - `iteritems()` → `items()`
   - `xrange()` → `range()`
   - View objects
   - List wrapping when needed

### Exceptions Category

1. **exceptions** - Exception Syntax
   - Comma → `as` keyword
   - Raise statement syntax

### Operators Category

1. **division** - Integer Division Behavior
   - `/` → float division
   - `//` for integer division
   - Future imports

### Classes Category

1. **classes** - New-Style Classes
   - Inheriting from `object`
   - Default behavior in Python 3

2. **metaclass** - Metaclass Syntax
   - `__metaclass__` attribute → keyword argument
   - Inheritance considerations

### Syntax Category

1. **octal** - Octal Literal Syntax
   - `0755` → `0o755`
   - File permissions

### Advanced Category

1. **metaclass** - Metaclass Syntax
   - Complex metaclass patterns
   - Multiple inheritance

## Examples

### Example 1: Starting a New Migration

```bash
# Step 1: Scan the codebase
$ ./py2to3 tips scan myproject/

ℹ Detected 5 types of issues:
  • print: 45 occurrence(s)
  • imports: 23 occurrence(s)
  • unicode: 18 occurrence(s)
  • iterators: 12 occurrence(s)
  • exceptions: 5 occurrence(s)

# Step 2: Learn about top issues
$ ./py2to3 tips show print
$ ./py2to3 tips show imports

# Step 3: Review related comprehensive guides
# (URLs shown in each tip)
```

### Example 2: Solving a Specific Problem

```bash
# You see: TypeError: 'dict_keys' object does not support indexing
$ ./py2to3 tips search "dict_keys"
$ ./py2to3 tips show iterators

# Output shows:
#   Python 2: dict.keys()[0]
#   Python 3: list(dict.keys())[0]
#   Note: Wrap with list() if you need indexing
```

### Example 3: Quick Reference During Coding

```bash
# Quick lookup while coding
$ ./py2to3 tips show unicode
$ ./py2to3 tips show exceptions

# Search for specific pattern
$ ./py2to3 tips search "basestring"
```

## Integration with Other Commands

The tips command complements other py2to3 commands:

### With `check` Command

```bash
# Run compatibility check
./py2to3 check src/

# Get tips for found issues
./py2to3 tips scan src/ --detail
```

### With `patterns` Command

```bash
# Browse pattern library for detailed reference
./py2to3 patterns list

# Get quick tips for common issues
./py2to3 tips list
```

### With `wizard` Command

```bash
# Use wizard for guided migration
./py2to3 wizard

# Get specific tips during migration
./py2to3 tips show <topic>
```

### With `fix` Command

```bash
# Get tips before applying fixes
./py2to3 tips scan src/ --max-tips 10

# Apply fixes
./py2to3 fix src/

# Verify with tips
./py2to3 tips scan src/
```

## Tips Format

Each tip includes:

1. **Title**: Clear, descriptive name
2. **Category**: Logical grouping (built-ins, strings, etc.)
3. **Topic ID**: Short identifier for quick access
4. **Problem**: What changed between Python 2 and 3
5. **Examples**: Multiple before/after code samples with notes
6. **Quick Fix**: One-line solution summary
7. **Common Mistakes**: Gotchas and pitfalls to avoid
8. **Related Guides**: Links to comprehensive documentation

## Best Practices

### For Individual Developers

1. **Start with scan**: `./py2to3 tips scan yourcode/`
2. **Learn incrementally**: Focus on your most common issues first
3. **Keep tips handy**: Bookmark common topics
4. **Use search**: Faster than scrolling through guides
5. **Check examples**: Verify your approach matches the examples

### For Teams

1. **Share tips**: Reference tip topics in code reviews
2. **Create checklists**: Based on scan results
3. **Training material**: Use tips for onboarding
4. **Document decisions**: Reference tips in migration docs
5. **Track progress**: Regular scans show improvement

### For Large Projects

1. **Scan modules**: Check individual modules/packages
2. **Prioritize by count**: Fix high-occurrence issues first
3. **Category review**: Address one category at a time
4. **Compare scans**: Track reduction in issue counts
5. **Automate checks**: Include in CI/CD pipeline

## Tips vs Other Commands

| Feature | Tips | Patterns | Guides |
|---------|------|----------|--------|
| Quick lookup | ✅ Best | ✅ Good | ❌ Slow |
| Code examples | ✅ Yes | ✅ Yes | ✅ Yes |
| Comprehensive | ❌ Brief | ✅ Detailed | ✅ Complete |
| Context-aware | ✅ Yes (scan) | ❌ No | ❌ No |
| Best for | Quick answers | Pattern library | In-depth learning |

**Use tips when**: You need a fast answer or context-aware suggestions

**Use patterns when**: You want detailed pattern reference with all variants

**Use guides when**: You need comprehensive understanding of a topic

## Frequently Asked Questions

### How is this different from the patterns command?

**Tips** provides quick, context-aware solutions for common issues with a focus on practical problem-solving.

**Patterns** provides a comprehensive reference library of all migration patterns with detailed variations.

Use **tips** for quick answers, **patterns** for detailed reference.

### Can I add custom tips?

The current version includes 15+ core tips covering the most common migration issues. Custom tips support may be added in a future version.

### How accurate is the scan feature?

The scan uses regex patterns to detect common Python 2 code. It may have false positives/negatives but provides a good estimate of issue types and their frequency.

### Can I use tips in CI/CD?

Yes! Use `--no-color` for clean output:

```bash
./py2to3 tips scan src/ --no-color > tips-report.txt
```

### What if a tip doesn't match my case?

1. Check the comprehensive guides linked in each tip
2. Use `./py2to3 patterns` for more variations
3. Use `./py2to3 wizard` for interactive help
4. Search documentation with `./py2to3 find search`

## Summary

The Tips command provides fast, context-aware answers to Python 2 to 3 migration questions:

- ⚡ **Fast**: Get answers in seconds
- 🎯 **Smart**: Scans your code for relevant tips
- 📚 **Complete**: Covers all major migration issues
- 💡 **Practical**: Clear examples and quick fixes
- 🔗 **Integrated**: Links to comprehensive guides

Perfect for beginners learning Python 3, teams coordinating migrations, and experienced developers who need quick reference.

**Next Steps**:
- Run `./py2to3 tips scan yourcode/` to identify issues
- Use `./py2to3 tips show <topic>` for specific help
- Combine with other commands for complete migration workflow

For comprehensive information, see also:
- [PATTERNS_GUIDE.md](PATTERNS_GUIDE.md) - Complete pattern library
- [WIZARD_GUIDE.md](WIZARD_GUIDE.md) - Interactive migration assistant
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [CLI_GUIDE.md](CLI_GUIDE.md) - All CLI commands
