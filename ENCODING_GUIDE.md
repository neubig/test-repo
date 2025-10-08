# Encoding Analysis Guide

## Overview

The encoding analyzer is a powerful tool for detecting and fixing file encoding issues during Python 2 to 3 migration. Encoding problems are one of the most common sources of runtime errors when migrating Python code, and this tool helps identify and resolve them before they cause issues.

## Why Encoding Matters in Python 2 to 3 Migration

Python 2 and Python 3 handle strings and encodings differently:

- **Python 2**: Default ASCII encoding, implicit str/unicode handling
- **Python 3**: Default UTF-8 encoding, explicit bytes/str distinction, requires encoding declarations for non-ASCII source files

Common encoding issues during migration:
- Missing encoding declarations in files with non-ASCII characters
- Mismatched declared vs. actual file encodings  
- Legacy encodings (Latin-1, CP1252, etc.) instead of UTF-8
- Files that can't be decoded with their declared encoding

## Installation

The encoding analyzer requires the `chardet` library for encoding detection:

```bash
pip install chardet
```

## Quick Start

### Analyze a directory for encoding issues

```bash
./py2to3 encoding src/ --recursive
```

### Add missing encoding declarations

```bash
./py2to3 encoding src/ --recursive --add-declarations
```

### Convert files to UTF-8

```bash
./py2to3 encoding src/ --recursive --convert-to-utf8
```

### Preview changes without modifying files

```bash
./py2to3 encoding src/ --recursive --add-declarations --convert-to-utf8 --dry-run
```

## Usage

### Basic Analysis

Analyze a single file:
```bash
./py2to3 encoding src/mymodule.py
```

Analyze a directory recursively:
```bash
./py2to3 encoding src/ --recursive
```

Analyze a directory (non-recursive):
```bash
./py2to3 encoding src/
```

### Generate Reports

Text format report:
```bash
./py2to3 encoding src/ -r --format text --output encoding_report.txt
```

JSON format report (for automation):
```bash
./py2to3 encoding src/ -r --format json --output encoding_report.json
```

Markdown format report:
```bash
./py2to3 encoding src/ -r --format markdown --output ENCODING_REPORT.md
```

### Fix Encoding Issues

Add encoding declarations to files that lack them:
```bash
./py2to3 encoding src/ -r --add-declarations
```

Convert non-UTF-8 files to UTF-8:
```bash
./py2to3 encoding src/ -r --convert-to-utf8
```

Both operations at once:
```bash
./py2to3 encoding src/ -r --add-declarations --convert-to-utf8
```

Preview what would be changed (dry run):
```bash
./py2to3 encoding src/ -r --add-declarations --convert-to-utf8 --dry-run
```

Convert without creating backups (not recommended):
```bash
./py2to3 encoding src/ -r --convert-to-utf8 --no-backup
```

## Command Options

| Option | Description |
|--------|-------------|
| `path` | File or directory to analyze (required) |
| `-r, --recursive` | Recursively analyze subdirectories |
| `-o, --output FILE` | Save report to file |
| `-f, --format FORMAT` | Report format: text, json, or markdown |
| `--add-declarations` | Add encoding declarations to files without them |
| `--convert-to-utf8` | Convert files to UTF-8 encoding |
| `--dry-run` | Preview changes without modifying files |
| `--no-backup` | Do not create backups when converting files |
| `-v, --verbose` | Show detailed error information |

## What the Analyzer Detects

### File Encoding Detection

The analyzer uses the `chardet` library to detect the actual encoding of each file, providing:
- Detected encoding (e.g., UTF-8, Latin-1, CP1252, ASCII)
- Confidence level (0.0 to 1.0)

### Encoding Declaration Analysis

Checks for PEP 263 encoding declarations in the first two lines:
```python
# -*- coding: utf-8 -*-
```
or
```python
# coding: utf-8
```

### Issue Detection

The analyzer identifies several types of issues:

1. **Missing Declarations**: Files with non-ASCII characters but no encoding declaration
2. **Encoding Mismatches**: Declared encoding doesn't match detected encoding
3. **Non-UTF-8 Encodings**: Files using encodings other than UTF-8 (the Python 3 standard)
4. **Decode Errors**: Files that cannot be decoded as UTF-8

## Output and Reports

### Console Summary

The analyzer provides a summary including:
- Total files analyzed
- Files with issues
- Files without encoding declarations
- Files with non-UTF-8 encoding
- Encoding distribution across files
- Status distribution (ok, info, warning, error)

### Text Report Example

```
======================================================================
ENCODING ANALYSIS REPORT
======================================================================

Total files analyzed:           45
Files with issues:              8
Files without declarations:     5
Files with non-UTF-8 encoding:  3

======================================================================

✓ src/mymodule.py
  Detected: utf-8 (confidence: 0.99)
  Declared: utf-8 (line 1)

⚠ src/legacy.py
  Detected: latin-1 (confidence: 0.85)
  Declared: None
  Issues:
    - File contains non-ASCII characters but has no encoding declaration
    - File uses 'latin-1' encoding instead of UTF-8
```

### JSON Report Structure

```json
{
  "file": "src/mymodule.py",
  "detected_encoding": "utf-8",
  "confidence": 0.99,
  "declared_encoding": "utf-8",
  "has_declaration": true,
  "declaration_line": 1,
  "issues": [],
  "status": "ok"
}
```

## Best Practices

### 1. Analyze Before Migrating

Run encoding analysis **before** starting your Python 2 to 3 migration:
```bash
./py2to3 encoding src/ -r --format markdown --output ENCODING_BASELINE.md
```

This establishes a baseline and identifies potential issues early.

### 2. Use Dry Run First

Always preview changes before applying them:
```bash
./py2to3 encoding src/ -r --add-declarations --convert-to-utf8 --dry-run
```

### 3. Keep Backups

The tool automatically creates `.bak` backups when converting files. Keep these until you've verified the conversion:
```bash
# Backup files are created as: original_file.py.bak
```

### 4. Test After Conversion

After converting encodings, test your code to ensure no issues were introduced:
```bash
./py2to3 encoding src/ -r --convert-to-utf8
pytest  # Run your test suite
```

### 5. Commit Changes Separately

Commit encoding fixes separately from other migration changes:
```bash
./py2to3 encoding src/ -r --add-declarations --convert-to-utf8
git add src/
git commit -m "Fix encoding declarations and convert to UTF-8"
```

### 6. Review High-Confidence Issues First

The confidence score helps prioritize which files to review:
- **>0.9**: Very confident - usually safe to auto-fix
- **0.7-0.9**: Confident - review changes
- **<0.7**: Low confidence - manual inspection recommended

## Integration with Migration Workflow

### Step 1: Pre-flight Check

Include encoding analysis in your pre-flight checks:
```bash
./py2to3 preflight src/
./py2to3 encoding src/ -r
```

### Step 2: Fix Encoding Issues

Before applying Python 2→3 fixes:
```bash
./py2to3 encoding src/ -r --add-declarations --convert-to-utf8
git commit -am "Fix encoding issues"
```

### Step 3: Apply Migration Fixes

Now apply the main migration fixes:
```bash
./py2to3 fix src/
```

### Step 4: Verify

Verify both encoding and Python 3 compatibility:
```bash
./py2to3 encoding src/ -r  # Should show no issues
./py2to3 check src/
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Encoding Check

on: [push, pull_request]

jobs:
  encoding-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install chardet
      - name: Check encodings
        run: ./py2to3 encoding src/ --recursive --format json --output encoding_report.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: encoding-report
          path: encoding_report.json
```

### Fail on Encoding Issues

Exit with error code if issues are found:
```bash
./py2to3 encoding src/ -r || exit 1
```

## Common Issues and Solutions

### Issue: "File contains non-ASCII characters but has no encoding declaration"

**Solution**: Add encoding declaration
```bash
./py2to3 encoding src/mymodule.py --add-declarations
```

The tool will add:
```python
# -*- coding: utf-8 -*-
```

### Issue: "Declared encoding doesn't match detected encoding"

**Cause**: File was saved with different encoding than declared

**Solution**: Convert to UTF-8
```bash
./py2to3 encoding src/mymodule.py --convert-to-utf8
```

### Issue: "File uses 'latin-1' encoding instead of UTF-8"

**Cause**: Legacy file from Python 2 era

**Solution**: Convert to UTF-8
```bash
./py2to3 encoding src/ -r --convert-to-utf8
```

### Issue: "File cannot be decoded as UTF-8"

**Cause**: File has binary data or wrong encoding

**Solution**: 
1. First, detect actual encoding:
   ```bash
   ./py2to3 encoding src/problem_file.py
   ```
2. Then convert to UTF-8:
   ```bash
   ./py2to3 encoding src/problem_file.py --convert-to-utf8
   ```

## Technical Details

### Encoding Detection

The analyzer uses the `chardet` library which:
- Analyzes byte sequences to identify character encoding
- Provides confidence scores
- Supports 30+ encoding types including:
  - UTF-8, UTF-16, UTF-32
  - Latin-1 (ISO-8859-1)
  - Windows-1252 (CP1252)
  - ASCII
  - And many more

### PEP 263 Compliance

The tool follows [PEP 263](https://www.python.org/dev/peps/pep-0263/) for encoding declarations:

Valid declaration formats:
```python
# coding: <encoding name>
# -*- coding: <encoding name> -*-
# coding=<encoding name>
```

Must appear in:
- Line 1, or
- Line 2 (if line 1 is a shebang)

### Supported Encoding Conversions

The tool can convert between any encodings supported by Python's `codecs` module, including:
- ASCII → UTF-8
- Latin-1 → UTF-8
- CP1252 → UTF-8
- ISO-8859-* → UTF-8
- And many others

## Examples

### Example 1: Clean Legacy Codebase

```bash
# 1. Analyze current state
./py2to3 encoding legacy_project/ -r --output encoding_baseline.txt

# 2. Preview fixes
./py2to3 encoding legacy_project/ -r --add-declarations --convert-to-utf8 --dry-run

# 3. Apply fixes
./py2to3 encoding legacy_project/ -r --add-declarations --convert-to-utf8

# 4. Verify
./py2to3 encoding legacy_project/ -r
```

### Example 2: CI/CD Integration

```bash
# In your CI pipeline
./py2to3 encoding src/ -r --format json --output encoding_report.json

# Fail if issues found
if [ $(jq '[.[] | select(.status == "warning" or .status == "error")] | length' encoding_report.json) -gt 0 ]; then
    echo "Encoding issues found!"
    exit 1
fi
```

### Example 3: Generate Team Report

```bash
# Generate markdown report for team review
./py2to3 encoding src/ -r --format markdown --output docs/ENCODING_STATUS.md

# Commit to repository
git add docs/ENCODING_STATUS.md
git commit -m "Add encoding status report"
```

## Troubleshooting

### chardet Not Found

**Error**: `ModuleNotFoundError: No module named 'chardet'`

**Solution**:
```bash
pip install chardet
```

### Permission Errors

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solution**: Check file permissions
```bash
chmod u+w src/mymodule.py
./py2to3 encoding src/mymodule.py --add-declarations
```

### Low Confidence Detection

**Issue**: Detected encoding has low confidence (<0.7)

**Solution**: Manually inspect the file
```bash
file -i src/problem_file.py  # Use system file command
hexdump -C src/problem_file.py | head  # View raw bytes
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI documentation
- [Migration Guide](README.md) - Full migration workflow
- [PEP 263](https://www.python.org/dev/peps/pep-0263/) - Defining Python Source Code Encodings
- [PEP 3120](https://www.python.org/dev/peps/pep-3120/) - Using UTF-8 as the default source encoding

## Support

For issues, questions, or contributions related to the encoding analyzer, please refer to the main project documentation or open an issue on the repository.
