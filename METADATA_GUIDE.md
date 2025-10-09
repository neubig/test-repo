# Project Metadata Updater Guide

The Project Metadata Updater is a powerful tool that automatically updates all project configuration and metadata files to reflect Python 3 compatibility. This ensures consistency across your entire project and properly advertises Python 3 support in all relevant places.

## Overview

After migrating your Python code from Python 2 to Python 3, you need to update various configuration files to reflect this change. The metadata updater automates this tedious process by scanning your project for common metadata files and updating them with Python 3 version requirements.

## What Files Are Updated?

The metadata updater handles the following files:

### Python Package Metadata
- **setup.py** - Updates `python_requires`, removes Python 2 classifiers, adds Python 3 classifiers
- **setup.cfg** - Updates `python_requires` in `[options]` section
- **pyproject.toml** - Updates `requires-python` and Poetry `python` dependency
- **Pipfile** - Updates `python_version` in `[requires]` section

### Testing & Development
- **tox.ini** - Updates `envlist` with Python 3 versions, fixes `basepython` references
- **.python-version** - Updates version from 2.x to 3.x

### CI/CD Configuration
- **.github/workflows/*.yml** - Updates GitHub Actions python-version matrices and setup-python actions
- **.gitlab-ci.yml** - Updates GitLab CI Docker images and Python version variables
- **.travis.yml** - Updates Travis CI Python version list

### Documentation
- **README.md** - Updates Python version badges and text mentions

## Usage

### Basic Usage

Update metadata files in the current directory:

```bash
./py2to3 metadata
```

Update metadata files in a specific directory:

```bash
./py2to3 metadata /path/to/project
```

### Preview Changes (Dry Run)

See what would be changed without actually modifying files:

```bash
./py2to3 metadata --dry-run
```

This is highly recommended before running the actual update to review what changes will be made.

### Specify Python Version Range

By default, the tool configures your project to support Python 3.6 through 3.12. You can customize this:

```bash
# Support Python 3.8 through 3.11
./py2to3 metadata --min-version 3.8 --max-version 3.11

# Support Python 3.7+
./py2to3 metadata --min-version 3.7 --max-version 3.12
```

### JSON Output

Get results in JSON format for scripting or CI/CD integration:

```bash
./py2to3 metadata --json
```

Example JSON output:

```json
{
  "updated_files": [
    {
      "file": "setup.py",
      "changes": [
        "Added python_requires='>=3.6'",
        "Removed Python 2 classifiers",
        "Added Python 3 classifiers"
      ]
    }
  ],
  "skipped_files": ["README.md", "tox.ini"],
  "errors": [],
  "dry_run": false
}
```

## Examples

### Example 1: First-Time Migration

You've just migrated your codebase from Python 2 to Python 3. Update all metadata:

```bash
# Preview changes
./py2to3 metadata --dry-run

# Review the output, then apply changes
./py2to3 metadata

# Commit the changes
git add -A
git commit -m "Update project metadata for Python 3"
```

### Example 2: Custom Version Range

Your project uses features from Python 3.8, so you want to require Python 3.8 as minimum:

```bash
./py2to3 metadata --min-version 3.8 --max-version 3.12
```

### Example 3: CI/CD Integration

In your CI/CD pipeline, verify metadata is up-to-date:

```bash
# Check if any updates are needed (dry run)
./py2to3 metadata --dry-run --json > metadata-check.json

# Parse JSON and fail if updates are needed
python -c "import json; data = json.load(open('metadata-check.json')); exit(1 if data['updated_files'] else 0)" || {
  echo "Error: Project metadata needs updating!"
  exit 1
}
```

## What Gets Updated in Each File

### setup.py

**Before:**
```python
setup(
    name='myproject',
    version='1.0.0',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    # python_requires not specified
)
```

**After:**
```python
setup(
    name='myproject',
    version='1.0.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.6',
)
```

### pyproject.toml

**Before:**
```toml
[project]
name = "myproject"
requires-python = ">=2.7"
```

**After:**
```toml
[project]
name = "myproject"
requires-python = ">=3.6"
```

### tox.ini

**Before:**
```ini
[tox]
envlist = py27,py35,py36

[testenv]
basepython = python2.7
```

**After:**
```ini
[tox]
envlist = py36,py37,py38,py39,py310,py311,py312

[testenv]
basepython = python3
```

### GitHub Actions

**Before:**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['2.7', '3.6', '3.7']
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
```

**After:**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
```

### README.md

**Before:**
```markdown
# My Project

Requires Python 2.7 or later.

![Python Version](https://img.shields.io/badge/python-2.7-blue.svg)
```

**After:**
```markdown
# My Project

Requires Python 3.6+ or later.

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)
```

## Backups

The metadata updater automatically creates backups of all modified files before making changes. Backups are stored in:

```
.metadata_backups/<timestamp>/
```

For example:
```
.metadata_backups/20240115_143022/
├── setup.py
├── setup.cfg
├── pyproject.toml
└── tox.ini
```

You can use these backups to restore files if needed.

## Integration with Migration Workflow

The metadata updater fits perfectly into your migration workflow:

1. **Analyze code** - Run preflight checks
   ```bash
   ./py2to3 preflight
   ```

2. **Fix Python code** - Apply automated fixes
   ```bash
   ./py2to3 fix src/ --backup
   ```

3. **Verify code** - Check for remaining issues
   ```bash
   ./py2to3 check src/
   ```

4. **Update metadata** - Update configuration files
   ```bash
   ./py2to3 metadata --dry-run  # Preview changes
   ./py2to3 metadata             # Apply changes
   ```

5. **Run tests** - Verify everything works
   ```bash
   pytest
   ```

6. **Commit changes** - Save your work
   ```bash
   git add -A
   git commit -m "Complete Python 2 to 3 migration"
   ```

## Best Practices

### 1. Always Preview First

Use `--dry-run` to see what will be changed before applying modifications:

```bash
./py2to3 metadata --dry-run
```

### 2. Review Changes

After running the updater, review the changes with `git diff`:

```bash
git diff
```

### 3. Test After Updating

Ensure your project still works correctly after metadata updates:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Try importing your package
python -c "import mypackage"
```

### 4. Update CI/CD Gradually

When updating CI/CD configurations, you might want to:

1. Add Python 3 versions while keeping Python 2 temporarily
2. Test that Python 3 CI jobs pass
3. Remove Python 2 versions once migration is complete

You can do this by manually editing the CI files after running the metadata updater.

### 5. Document Your Support Policy

After updating metadata, update your documentation to clearly state:

- Minimum Python version required
- Which Python versions are actively tested
- When support for older Python versions will be dropped

## Troubleshooting

### Files Not Updated

**Problem:** Some files aren't being updated even though they contain Python 2 references.

**Solution:** The updater looks for specific patterns. If your file has unusual formatting, it might not be detected. You can:

1. Check the file format matches common patterns
2. Update the file manually
3. Report the issue so we can improve pattern matching

### Custom Configuration Formats

**Problem:** Your project uses a non-standard configuration format.

**Solution:** The metadata updater handles the most common formats. For custom formats:

1. Use `--dry-run` to see what's updated
2. Manually update files that aren't handled
3. Consider migrating to standard formats (e.g., pyproject.toml)

### Version Range Too Restrictive

**Problem:** The default version range (3.6-3.12) doesn't match your needs.

**Solution:** Use `--min-version` and `--max-version` to customize:

```bash
# Only support latest Python versions
./py2to3 metadata --min-version 3.10 --max-version 3.12

# Support a wide range
./py2to3 metadata --min-version 3.7 --max-version 3.13
```

## Advanced Usage

### Combining with Git Integration

Track metadata updates with git:

```bash
# Create a checkpoint before updating
./py2to3 git checkpoint "Before metadata update"

# Update metadata
./py2to3 metadata

# Commit with git integration
./py2to3 git commit "metadata-updated" -m "Update project metadata for Python 3"
```

### Scripting

Use JSON output for scripting:

```bash
#!/bin/bash

# Update metadata and capture results
results=$(./py2to3 metadata --json)

# Extract updated files count
updated_count=$(echo "$results" | python -c "import json, sys; print(len(json.load(sys.stdin)['updated_files']))")

echo "Updated $updated_count file(s)"

# Send notification
if [ "$updated_count" -gt 0 ]; then
    curl -X POST https://hooks.slack.com/... \
         -d "{\"text\": \"Project metadata updated: $updated_count files\"}"
fi
```

### Custom Validation

After updating, validate the changes:

```bash
# Update metadata
./py2to3 metadata

# Validate setup.py
python setup.py check --strict

# Validate pyproject.toml
pip install validate-pyproject
validate-pyproject pyproject.toml

# Run tests
tox
```

## FAQ

**Q: Will this break my existing Python 2 support?**

A: Yes, this tool updates your project metadata to declare Python 3 support and remove Python 2 declarations. Only run this after you've completed your code migration.

**Q: Can I update only specific files?**

A: Currently, the tool updates all supported files it finds. If you only want to update specific files, use `--dry-run` to see the full list, then manually update the files you want.

**Q: Does this modify my Python code?**

A: No, this tool only updates metadata and configuration files. Use `./py2to3 fix` to update your Python code.

**Q: What if I need to support both Python 2 and 3?**

A: This tool is designed for projects migrating fully to Python 3. If you need dual support, manually configure your metadata files or don't run this tool.

**Q: Can I undo the changes?**

A: Yes! The tool creates backups in `.metadata_backups/`. You can also use git to revert changes:

```bash
git checkout -- .
```

Or use the rollback manager:

```bash
./py2to3 rollback undo
```

## See Also

- [CLI Guide](CLI_GUIDE.md) - Complete CLI documentation
- [Migration Workflow](README.md#migration-workflow) - Full migration process
- [Configuration Guide](CONFIG.md) - Configure default settings
- [Rollback Guide](ROLLBACK_GUIDE.md) - Undo changes safely

## Contributing

Found a metadata file format we don't support? Please:

1. Open an issue with an example
2. Submit a pull request with pattern support
3. Share your use case

We're always looking to improve the metadata updater!
