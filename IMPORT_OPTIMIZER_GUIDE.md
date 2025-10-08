# Import Optimizer Guide

The Import Optimizer is a powerful tool for cleaning up and organizing Python imports after migration from Python 2 to Python 3. It helps maintain clean, PEP 8 compliant code by automatically detecting and fixing common import issues.

## Overview

After migrating code from Python 2 to Python 3, imports often become messy due to:
- Module renames (e.g., `urllib2` → `urllib.request`)
- Unused legacy imports left behind
- Duplicate imports added during fixes
- Unorganized import ordering

The Import Optimizer addresses all these issues automatically.

## Features

### 1. **Unused Import Detection**
Identifies and removes imports that are never used in the code:
```python
# Before
import os
import sys
import unused_module  # Not used anywhere

def main():
    print(sys.version)

# After (with --fix)
import sys

def main():
    print(sys.version)
```

### 2. **Duplicate Import Removal**
Finds and eliminates duplicate import statements:
```python
# Before
import json
from datetime import datetime
import json  # Duplicate!

# After (with --fix)
import json
from datetime import datetime
```

### 3. **PEP 8 Import Ordering**
Automatically sorts imports according to PEP 8 guidelines:
1. Standard library imports
2. Related third-party imports
3. Local application imports

```python
# Before
from myapp import models
import sys
import requests
import os

# After (with --fix)
import os
import sys

import requests

from myapp import models
```

### 4. **Wildcard Import Detection**
Identifies wildcard imports (considered bad practice):
```python
# Detected and reported
from module import *  # ⚠️ Wildcard import detected
```

### 5. **Comprehensive Reporting**
Generates detailed reports showing:
- Number of files analyzed
- Unused imports found
- Duplicate imports found
- Wildcard imports detected
- Import ordering issues
- File-by-file breakdown with line numbers

## Usage

### Basic Commands

#### Check Imports (Analysis Only)
Analyze imports without making changes:

```bash
# Check a single file
./py2to3 imports path/to/file.py

# Check a directory (recursive by default)
./py2to3 imports src/

# Save report to file
./py2to3 imports src/ -o import_report.txt
```

#### Fix Imports
Apply optimizations automatically:

```bash
# Fix imports in a single file (with backup)
./py2to3 imports path/to/file.py --fix

# Fix imports in entire directory
./py2to3 imports src/ --fix

# Fix without creating backups (use with caution)
./py2to3 imports src/ --fix --no-backup
```

### Command-Line Options

```
./py2to3 imports [PATH] [OPTIONS]

Arguments:
  PATH                    File or directory to analyze (default: current directory)

Options:
  --fix                   Apply import optimizations to files
  --no-backup            Do not create backup files when fixing
  --recursive            Recursively process directories (default: True)
  -o, --output FILE      Save report to file
  -h, --help             Show help message
```

## Workflow Examples

### Example 1: Post-Migration Cleanup

After migrating your code to Python 3:

```bash
# Step 1: Analyze the codebase
./py2to3 imports src/ -o pre_cleanup_imports.txt

# Step 2: Review the report
cat pre_cleanup_imports.txt

# Step 3: Apply fixes
./py2to3 imports src/ --fix

# Step 4: Verify results
./py2to3 imports src/
```

### Example 2: Pre-Commit Check

Add import checking to your workflow:

```bash
# Check imports before committing
./py2to3 imports src/

# Exit code 0 = all good, 1 = issues found
# Perfect for CI/CD integration!
```

### Example 3: Single File Quick Fix

Fix imports in a specific file:

```bash
# Analyze first
./py2to3 imports src/fixer.py

# Apply fix
./py2to3 imports src/fixer.py --fix

# Backup created automatically as src/fixer.py.bak
```

## Report Format

The Import Optimizer generates comprehensive reports:

```
======================================================================
IMPORT OPTIMIZATION REPORT
======================================================================

Summary Statistics:
  Files analyzed: 15
  Unused imports: 8
  Duplicate imports: 3
  Wildcard imports: 2
  Unsorted imports: 5
  Total optimizations: 18

======================================================================
DETAILED ISSUES
======================================================================

File: src/fixer.py
  Unused Import:
    Line 5: Unused import: tempfile
      → Remove unused import 'tempfile'
  Unsorted Imports:
    Line 1: Imports are not sorted according to PEP 8
      → Sort imports: stdlib → third-party → local

File: src/verifier.py
  Duplicate Import:
    Line 10: Duplicate import on line 3: sys
      → Remove duplicate import of 'sys'
  Wildcard Import:
    Line 15: Wildcard import from utils
      → Replace wildcard import with explicit imports
```

## Integration with Migration Workflow

### Recommended Migration Sequence

1. **Initial Migration**
   ```bash
   ./py2to3 fix src/
   ```

2. **Verify Python 3 Compatibility**
   ```bash
   ./py2to3 check src/
   ```

3. **Optimize Imports** ✨ **[NEW STEP]**
   ```bash
   ./py2to3 imports src/ --fix
   ```

4. **Run Linters**
   ```bash
   ./py2to3 lint src/
   ```

5. **Generate Report**
   ```bash
   ./py2to3 report -o migration_complete.html
   ```

## Best Practices

### 1. Always Create Backups
Keep backups enabled (default) until you're confident:
```bash
./py2to3 imports src/ --fix  # Creates .bak files
```

### 2. Review Before Applying
Analyze first, then fix:
```bash
./py2to3 imports src/ -o review.txt
# Review review.txt
./py2to3 imports src/ --fix
```

### 3. Use Version Control
Commit before running fixes:
```bash
git add -A
git commit -m "Pre-import-optimization snapshot"
./py2to3 imports src/ --fix
git diff  # Review changes
```

### 4. Incremental Approach
Fix one module at a time for large codebases:
```bash
./py2to3 imports src/core/ --fix
./py2to3 imports src/utils/ --fix
./py2to3 imports src/web/ --fix
```

## CI/CD Integration

Add import checking to your CI/CD pipeline:

### GitHub Actions Example

```yaml
- name: Check Python Imports
  run: |
    ./py2to3 imports src/
    if [ $? -ne 0 ]; then
      echo "Import issues detected. Please run: ./py2to3 imports src/ --fix"
      exit 1
    fi
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
./py2to3 imports src/
if [ $? -ne 0 ]; then
    echo "❌ Import issues detected. Fix with: ./py2to3 imports src/ --fix"
    exit 1
fi
```

## Advanced Usage

### Standalone Module Usage

You can also use the Import Optimizer directly as a Python module:

```python
from import_optimizer import ImportOptimizer

# Create optimizer instance
optimizer = ImportOptimizer()

# Analyze a file
result = optimizer.analyze_file('path/to/file.py')

# Check for issues
if result['issues']:
    for issue in result['issues']:
        print(f"{issue['type']}: {issue['message']}")

# Optimize a file
success = optimizer.optimize_file('path/to/file.py')

# Analyze a directory
results = optimizer.analyze_directory('src/', recursive=True)

# Generate report
optimizer.generate_report(results, 'import_report.txt')
```

## Limitations

### Current Limitations

1. **Wildcard Import Analysis**: Cannot determine if wildcard imports are used
2. **Dynamic Imports**: Does not analyze `importlib` or `__import__()` calls
3. **Conditional Imports**: May flag conditionally-used imports as unused
4. **Type Checking Imports**: May not recognize imports used only in type hints

### Known Edge Cases

- Imports used only in string type hints may be flagged as unused
- Imports used in `eval()` or `exec()` statements are flagged as unused
- Relative imports in packages may need manual verification

## Troubleshooting

### Issue: "Syntax Error" When Analyzing

**Cause**: File contains Python 2 syntax or syntax errors

**Solution**: Run the fixer first:
```bash
./py2to3 fix src/
./py2to3 imports src/ --fix
```

### Issue: Import Marked as Unused But Is Actually Used

**Cause**: Import might be used in eval(), type hints, or dynamic code

**Solution**: Add a comment to preserve:
```python
import needed_module  # noqa - used in eval
```

### Issue: Third-Party Package Classified as Local

**Cause**: Heuristic classification isn't perfect

**Solution**: The import will still work; it's just a sorting concern

## Tips for Clean Imports

1. **Avoid Wildcard Imports**: Use explicit imports
   ```python
   # Bad
   from module import *
   
   # Good
   from module import func1, func2
   ```

2. **Use Absolute Imports**: Prefer absolute over relative
   ```python
   # Better
   from myapp.utils import helper
   
   # Instead of
   from ..utils import helper
   ```

3. **Group Related Imports**: Keep related imports together
   ```python
   # Good
   from datetime import datetime, timedelta
   
   # Not as good
   from datetime import datetime
   from datetime import timedelta
   ```

4. **Remove Unused Imports Regularly**: Keep codebase clean
   ```bash
   # Make it part of your routine
   ./py2to3 imports src/ --fix
   ```

## Related Commands

- `./py2to3 check` - Check Python 3 compatibility
- `./py2to3 fix` - Fix Python 2 to 3 issues
- `./py2to3 lint` - Run linters for code quality
- `./py2to3 quality` - Analyze code quality metrics

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI documentation
- [Quality Guide](QUALITY_GUIDE.md) - Code quality analysis
- [Migration Guide](README.md) - Full migration workflow

## Contributing

Have ideas for improving the Import Optimizer? Contributions are welcome!

- Report issues or suggest features
- Add support for more import patterns
- Improve classification heuristics
- Enhance reporting formats

---

**Need Help?** Run `./py2to3 imports --help` for quick reference!
