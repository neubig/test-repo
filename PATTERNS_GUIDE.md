# Pattern Library Guide 📚

The **Pattern Library** is an interactive reference tool that helps you quickly look up common Python 2 patterns and their Python 3 equivalents. It's perfect for learning, manual migration work, and as a quick reference during code reviews.

## Overview

The Pattern Library contains 30+ migration patterns covering:
- **Built-ins**: print, input, and other built-in function changes
- **Strings**: Unicode handling, string types, and formatting
- **Iterators**: Dictionary methods, range/xrange, map/filter/zip
- **Imports**: Module reorganizations and renames
- **Exceptions**: Syntax changes for handling and raising exceptions
- **Classes**: Metaclasses and class definition updates
- **Operators**: Division behavior changes
- **Functional**: reduce, sorted, and comparison functions
- **Files**: File I/O best practices
- **Numbers**: Integer types and literals

Each pattern includes:
- ✅ **Python 2 code example**
- ✅ **Python 3 equivalent**
- ✅ **Detailed explanation**
- ✅ **Gotchas and warnings** (where applicable)
- ✅ **Difficulty rating** (easy 🟢, medium 🟡, hard 🔴)

## Basic Usage

### Show Library Summary

Get an overview of available patterns:

```bash
./py2to3 patterns
```

This displays:
- Total number of patterns
- Categories and pattern counts
- Difficulty distribution
- Usage tips

### List All Patterns

See a condensed list of all patterns organized by category:

```bash
./py2to3 patterns --list
```

This shows pattern names grouped by category with difficulty indicators.

## Searching and Filtering

### Browse by Category

View all patterns in a specific category:

```bash
# String-related patterns
./py2to3 patterns --category Strings

# Iterator patterns (dict methods, range, map, etc.)
./py2to3 patterns --category Iterators

# Import changes
./py2to3 patterns --category Imports

# Built-in function changes
./py2to3 patterns --category Built-ins

# Exception handling
./py2to3 patterns --category Exceptions

# Class definition changes
./py2to3 patterns --category Classes
```

**Available Categories:**
- Built-ins
- Classes
- Dictionary
- Exceptions
- Files
- Functional
- Imports
- Iterators
- Literals
- Numbers
- Operators
- Sorting
- Strings

### Search by Keyword

Find patterns related to a specific topic:

```bash
# Find print-related patterns
./py2to3 patterns --search print

# Find exception patterns
./py2to3 patterns --search exception

# Find dictionary patterns
./py2to3 patterns --search dict

# Find unicode patterns
./py2to3 patterns --search unicode

# Find import patterns
./py2to3 patterns --search import
```

### Filter by Difficulty

Focus on patterns matching your current skill level or the complexity you're dealing with:

```bash
# Easy patterns (good for beginners)
./py2to3 patterns --difficulty easy

# Medium difficulty patterns
./py2to3 patterns --difficulty medium

# Hard patterns (semantic changes, complex migrations)
./py2to3 patterns --difficulty hard
```

**Difficulty Levels:**
- 🟢 **Easy**: Simple syntax changes, straightforward replacements
- 🟡 **Medium**: Requires understanding of behavior changes, may need list() conversions
- 🔴 **Hard**: Semantic changes, requires careful review and testing

## Combining Filters

You can combine multiple filters to narrow down your search:

```bash
# Easy string patterns
./py2to3 patterns --category Strings --difficulty easy

# Search for "print" in Built-ins category
./py2to3 patterns --category Built-ins --search print

# Hard iterator patterns
./py2to3 patterns --category Iterators --difficulty hard
```

## Example Workflows

### Learning Python 3

Start with easy patterns to understand basic changes:

```bash
# Step 1: Get overview
./py2to3 patterns

# Step 2: Start with easy patterns
./py2to3 patterns --difficulty easy

# Step 3: Progress to medium patterns
./py2to3 patterns --difficulty medium

# Step 4: Tackle hard patterns
./py2to3 patterns --difficulty hard
```

### Manual Migration

Quick reference while migrating code:

```bash
# Encountered print statement
./py2to3 patterns --search print

# Working on dictionary methods
./py2to3 patterns --category Dictionary

# Fixing import errors
./py2to3 patterns --category Imports

# Understanding division issues
./py2to3 patterns --search division
```

### Code Review

Reference patterns during code review:

```bash
# Review string handling changes
./py2to3 patterns --category Strings

# Check exception handling patterns
./py2to3 patterns --category Exceptions

# Verify iterator usage
./py2to3 patterns --category Iterators
```

### Teaching/Training

Use patterns for educational purposes:

```bash
# Show students basic changes
./py2to3 patterns --difficulty easy

# Demonstrate built-in changes
./py2to3 patterns --category Built-ins

# Explain string/unicode handling
./py2to3 patterns --category Strings
```

## Pattern Categories Explained

### Built-ins
Changes to built-in functions like print, input, next, and others.
**Common patterns**: print statement → function, raw_input → input, next() method → function

### Strings
String type changes, Unicode handling, and string operations.
**Common patterns**: basestring removal, unicode literals, str vs bytes

### Iterators
Changes to iteration methods and lazy evaluation.
**Common patterns**: dict.iteritems(), range/xrange, map/filter/zip

### Imports
Module reorganizations and naming changes.
**Common patterns**: urllib/urllib2, ConfigParser, Queue, SocketServer

### Exceptions
Exception syntax changes for handling and raising.
**Common patterns**: except Exception as e, raise Exception()

### Operators
Operator behavior changes, especially division.
**Common patterns**: / vs //, true division vs floor division

### Classes
Class definition and metaclass changes.
**Common patterns**: New-style classes, metaclass syntax

### Functional
Changes to functional programming features.
**Common patterns**: reduce import, sorted key parameter, cmp removal

### Dictionary
Dictionary-specific method changes.
**Common patterns**: has_key removal, dict.keys() returning views

### Files
File I/O best practices and changes.
**Common patterns**: file() removal, context managers

### Numbers
Numeric type unification and literal syntax.
**Common patterns**: Long type removal, octal literals

### Literals
Syntax changes for literals.
**Common patterns**: Octal notation, long suffix removal

### Sorting
Changes to sorting and comparison.
**Common patterns**: cmp parameter removal, key parameter usage

## Tips for Effective Use

1. **Start Broad**: Begin with `--list` or a category view to get context
2. **Narrow Down**: Use `--search` to find specific patterns you're working with
3. **Learn Progressively**: Start with easy patterns, move to harder ones
4. **Reference Frequently**: Keep the pattern library handy during migration
5. **Understand Gotchas**: Pay special attention to warnings about semantic changes
6. **Combine with Other Tools**: Use alongside the fixer and verifier tools

## Integration with Other Tools

The Pattern Library complements other toolkit features:

```bash
# Check code for issues
./py2to3 check src/

# Look up specific patterns found
./py2to3 patterns --search "issue_keyword"

# Apply automatic fixes
./py2to3 fix src/

# Verify results
./py2to3 check src/

# Reference any remaining manual fixes
./py2to3 patterns --category RelevantCategory
```

## Common Questions

### Q: Can I add custom patterns?
A: Currently, patterns are built-in. Future versions may support custom pattern files. You can modify `src/pattern_library.py` to add your own patterns.

### Q: Why does my pattern search return no results?
A: Try different keywords or browse by category. Search is case-insensitive and matches pattern names, categories, and explanations.

### Q: What's the difference between easy, medium, and hard patterns?
A: 
- **Easy**: Simple syntax changes, low risk
- **Medium**: Behavior changes, need to understand nuances
- **Hard**: Semantic changes, require careful testing

### Q: Can I export patterns to a file?
A: Use shell redirection to save output: `./py2to3 patterns --list > patterns.txt`

### Q: How often is the pattern library updated?
A: The library includes the most common Python 2 to 3 patterns. New patterns are added based on community feedback.

## Best Practices

1. **Understand Before Applying**: Read the explanation and gotchas before making changes
2. **Test After Changes**: Always test code after applying pattern-based fixes
3. **Watch for Hard Patterns**: Patterns marked as "hard" often require manual testing
4. **Combine Automated and Manual**: Use the fixer for bulk changes, patterns for understanding
5. **Share Knowledge**: Use patterns as teaching tools for team members

## Related Commands

- `./py2to3 check` - Verify Python 3 compatibility
- `./py2to3 fix` - Apply automated fixes
- `./py2to3 wizard` - Interactive migration guide
- `./py2to3 convert` - Convert code snippets
- `./py2to3 docs` - Generate migration documentation

## Troubleshooting

### Pattern not found
- Verify the category name: `./py2to3 patterns` to see all categories
- Try searching instead: `./py2to3 patterns --search keyword`
- The pattern might be grouped under a different category

### Too many results
- Add filters: combine `--category`, `--search`, and `--difficulty`
- Search for more specific keywords
- Browse by category first, then search within results

### Need more examples
- Look at the fixer tool output: `./py2to3 fix --dry-run`
- Check the test files in `tests/` for real-world examples
- Generate a report: `./py2to3 report` for before/after comparisons

## Summary

The Pattern Library is your quick-reference guide for Python 2 to 3 migration patterns. Use it to:

- 📖 **Learn** Python 3 changes systematically
- 🔍 **Look up** specific patterns during migration
- 🎓 **Teach** others about Python 3 differences
- ✅ **Verify** your manual fixes are correct
- 💡 **Understand** the "why" behind automated fixes

**Quick Start:**
```bash
./py2to3 patterns                    # Overview
./py2to3 patterns --list             # All patterns
./py2to3 patterns --category Strings # Specific category
./py2to3 patterns --search dict      # Search patterns
```

Happy migrating! 🚀
