# Code Snippet Converter Guide

## Overview

The **Code Snippet Converter** is a lightweight, interactive tool for quickly converting Python 2 code snippets to Python 3. It's perfect for learning Python 3 changes, testing specific patterns, and serving as a quick reference guide.

Unlike the full `fix` command which operates on entire projects, the snippet converter is optimized for:
- **Learning**: Understand Python 2 to 3 changes with detailed explanations
- **Quick testing**: Try out specific code patterns instantly
- **Education**: Great for tutorials, documentation, and teaching
- **Reference**: Keep as a handy conversion cheat sheet

## Quick Start

### Convert inline code

```bash
./py2to3 convert -c 'print "Hello, World"'
```

### Convert a file

```bash
./py2to3 convert my_snippet.py
```

### Read from stdin

```bash
echo 'print "test"' | ./py2to3 convert
```

Or:

```bash
./py2to3 convert -
# Type your code, then press Ctrl+D
```

## Usage Examples

### Basic Conversion

Convert a simple print statement:

```bash
$ ./py2to3 convert -c 'print "Hello, World"'

=== Python 2 (Original) ===
print "Hello, World"

=== Python 3 (Converted) ===
print("Hello, World")

=== Changes Made ===
1. print_statement
   Line 1
   - print "Hello, World"
   + print("Hello, World")
   ℹ Print is now a function in Python 3, requiring parentheses
```

### Side-by-Side Comparison

Great for presentations and teaching:

```bash
./py2to3 convert my_code.py --side-by-side
```

Output:
```
================================================================================
Python 2                               | Python 3
================================================================================
import urllib2                         │ import urllib.request
print "Hello"                          │ print("Hello")
for item in mydict.iteritems():        │ for item in mydict.items():
    print item                         │     print(item)
================================================================================
```

### Unified Diff View

Perfect for understanding exactly what changed:

```bash
./py2to3 convert my_code.py --diff
```

Output:
```
--- Python 2
+++ Python 3
@@ -1,3 +1,3 @@
-import urllib2
-print "Hello"
-for item in mydict.iteritems():
+import urllib.request
+print("Hello")
+for item in mydict.items():
```

### Save Converted Code

Convert and save to a file:

```bash
./py2to3 convert input.py -o output.py
```

### Quiet Mode (Code Only)

Get just the converted code without formatting:

```bash
./py2to3 convert input.py --quiet
```

This is useful for:
- Piping to other tools
- Automated scripts
- Integration with other workflows

### Skip Explanations

Show only the conversion without detailed explanations:

```bash
./py2to3 convert my_code.py --no-explanation
```

## Supported Conversions

The snippet converter handles these common Python 2 to 3 changes:

### 1. Print Statements → Print Functions

**Python 2:**
```python
print "Hello"
print "Value:", x
print >> file, "output"
```

**Python 3:**
```python
print("Hello")
print("Value:", x)
print("output", file=file)
```

### 2. Exception Syntax

**Python 2:**
```python
except Exception, e:
    pass
raise Exception, "message"
```

**Python 3:**
```python
except Exception as e:
    pass
raise Exception("message")
```

### 3. Dictionary Methods

**Python 2:**
```python
for k, v in d.iteritems():
    pass
keys = d.iterkeys()
values = d.itervalues()
if d.has_key('x'):
    pass
```

**Python 3:**
```python
for k, v in d.items():
    pass
keys = d.keys()
values = d.values()
if 'x' in d:
    pass
```

### 4. Range Functions

**Python 2:**
```python
for i in xrange(10):
    pass
```

**Python 3:**
```python
for i in range(10):
    pass
```

### 5. Import Changes

**Python 2:**
```python
import urllib2
import ConfigParser
import Queue
```

**Python 3:**
```python
import urllib.request
import configparser
import queue
```

### 6. String Types

**Python 2:**
```python
if isinstance(x, basestring):
    pass
s = u"unicode string"
```

**Python 3:**
```python
if isinstance(x, str):
    pass
s = "unicode string"
```

### 7. Input Functions

**Python 2:**
```python
name = raw_input("Enter name: ")
```

**Python 3:**
```python
name = input("Enter name: ")
```

### 8. Integer Types

**Python 2:**
```python
big_num = long(1000000)
```

**Python 3:**
```python
big_num = int(1000000)
```

### 9. Exec Statement

**Python 2:**
```python
exec code
execfile('script.py')
```

**Python 3:**
```python
exec(code)
exec(open('script.py').read())
```

### 10. Other Changes

- **reduce()**: Adds `from functools import reduce` when needed
- **Octal literals**: `0777` → `0o777`
- **.next()**: `.next()` → `.__next__()`

## Use Cases

### 1. Learning Python 3

Use it to understand what changed between Python 2 and 3:

```bash
./py2to3 convert -c 'print "test"'
```

Read the explanations to understand *why* each change was made.

### 2. Documentation & Tutorials

Generate before/after examples for your documentation:

```bash
./py2to3 convert example.py --side-by-side > docs/conversion_example.txt
```

### 3. Quick Testing

Test how a specific pattern should be converted:

```bash
echo 'for k, v in d.iteritems(): print k' | ./py2to3 convert --quiet
```

### 4. Code Review

Review conversion suggestions during migration:

```bash
./py2to3 convert suspicious_code.py --diff
```

### 5. Education

Perfect for teaching Python 3 changes to teams migrating from Python 2:

```bash
./py2to3 convert legacy_example.py --side-by-side --no-explanation
```

## Command Reference

```
py2to3 convert [options] [input]
```

### Arguments

- `input`: Input file path (optional, uses stdin if omitted or set to `-`)

### Options

- `-c, --code CODE`: Convert inline code string
- `-o, --output FILE`: Save converted code to file
- `--side-by-side`: Display side-by-side comparison
- `--diff`: Display unified diff format
- `--no-explanation`: Skip detailed explanations
- `--quiet`: Output only converted code (no formatting)
- `-h, --help`: Show help message

## Integration Examples

### Vim Integration

Add to your `.vimrc` to convert Python 2 code in your buffer:

```vim
" Convert selected Python 2 code to Python 3
vnoremap <leader>py3 :!py2to3 convert -<CR>
```

### Git Hook

Check for Python 2 patterns before commit:

```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); do
    if ./py2to3 convert "$file" --quiet | diff -q "$file" - > /dev/null; then
        :
    else
        echo "Warning: $file may contain Python 2 code"
    fi
done
```

### CI/CD Pipeline

Add snippet conversion checks to your CI:

```yaml
# .github/workflows/py3-check.yml
- name: Check for Python 2 patterns
  run: |
    find . -name '*.py' -exec py2to3 convert {} --quiet --output /tmp/converted.py \;
    if ! diff {} /tmp/converted.py > /dev/null; then
      echo "Found Python 2 patterns in {}"
      py2to3 convert {} --diff
    fi
```

## Tips & Best Practices

### 1. Use for Learning, Not Production

The snippet converter is designed for:
- **Learning and understanding** Python 3 changes
- **Quick testing** of specific patterns
- **Educational purposes** and documentation

For production migrations, use the full `fix` command which:
- Includes backup management
- Integrates with git
- Handles entire projects
- Provides comprehensive reporting

### 2. Combine with Other Tools

Use alongside other commands:

```bash
# Check compatibility first
./py2to3 check my_code.py

# Test conversion on a snippet
./py2to3 convert my_code.py --diff

# Apply fixes to the project
./py2to3 fix my_code.py
```

### 3. Review Explanations

Don't skip the explanations! They help you understand:
- Why the change is needed
- What behavior changed in Python 3
- How to think about Python 3 idioms

### 4. Test Edge Cases

The converter handles common patterns, but edge cases may need manual review:

```bash
# Test complex code
./py2to3 convert complex_example.py --side-by-side
```

### 5. Save Examples

Build a library of conversion examples:

```bash
mkdir py2to3_examples
./py2to3 convert old_code.py -o py2to3_examples/converted.py
./py2to3 convert old_code.py --diff > py2to3_examples/changes.diff
```

## Comparison with Other Commands

| Feature | `convert` | `fix` | `check` |
|---------|-----------|-------|---------|
| **Purpose** | Quick snippet conversion | Full project migration | Compatibility analysis |
| **Scope** | Single files/snippets | Entire projects | Analysis only |
| **Backup** | No | Yes | N/A |
| **Git Integration** | No | Yes | No |
| **Explanations** | Detailed | Summary | Detailed issues |
| **Output** | Multiple formats | Files + report | Report |
| **Best For** | Learning, testing | Production migration | Planning, validation |

## Troubleshooting

### Issue: "No changes needed"

This means your code is already Python 3 compatible! Try:

```bash
# Verify it's already valid Python 3
python3 -m py_compile your_file.py
```

### Issue: Unexpected conversion

Some complex patterns may not convert perfectly. For production code:

1. Use the `convert` command to understand the pattern
2. Review the explanation
3. Use `fix` command with `--dry-run` for the full project
4. Review and test thoroughly

### Issue: Module import not converted

The converter handles common standard library renames. For third-party packages:

```bash
# Use dependency analyzer
./py2to3 deps analyze
```

## Related Commands

- **`fix`**: Apply fixes to entire projects with backup and git integration
- **`check`**: Verify Python 3 compatibility and identify issues
- **`interactive`**: Review and approve fixes interactively
- **`compare`**: Compare conversion approaches across branches
- **`docs`**: Generate documentation for your migration

## Examples Repository

Check out `/examples` (if available) for a collection of common Python 2 patterns and their Python 3 equivalents.

## Contributing

Have ideas for improving the converter? Contributions welcome!

- Add more conversion patterns
- Improve explanations
- Add new output formats
- Enhance detection logic

## Learn More

- [CLI Guide](CLI_GUIDE.md) - Full CLI documentation
- [Migration Guide](README.md) - Complete migration workflow
- [Config Guide](CONFIG.md) - Configuration options
- [Fix Command](README.md#fix-command) - Production migration tool

---

**Happy Converting! 🐍→🐍**
