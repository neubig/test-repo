# Pre-commit Hooks for Python 2 to 3 Migration

Prevent Python 2 code regression during migration with automated pre-commit validation hooks.

## Table of Contents

- [Overview](#overview)
- [Why Pre-commit Hooks?](#why-pre-commit-hooks)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration Modes](#configuration-modes)
- [Commands](#commands)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Integration with CI/CD](#integration-with-cicd)

## Overview

The pre-commit hook generator creates and manages git pre-commit hooks that automatically validate Python 3 compatibility before each commit. This prevents developers from accidentally committing Python 2 code during migration, saving time and reducing regression issues.

## Why Pre-commit Hooks?

During Python 2 to 3 migration, teams often face these challenges:

1. **Code Regression**: Developers accidentally commit Python 2 code patterns
2. **Inconsistent Reviews**: Manual code reviews miss subtle Python 2 issues
3. **Delayed Detection**: Issues discovered late in the development cycle
4. **Wasted Time**: Time spent fixing preventable issues

Pre-commit hooks solve these problems by:

- ✅ Catching Python 2 code before it enters the repository
- ✅ Providing instant feedback to developers
- ✅ Enforcing consistency across the team
- ✅ Reducing code review burden
- ✅ Preventing migration regressions

## Installation

### Prerequisites

1. **Git Repository**: Your project must be a git repository
2. **Python 3**: Python 3.6 or later installed
3. **Pre-commit Framework** (optional but recommended): Install with `pip install pre-commit`

### Quick Start

Install pre-commit hooks with default settings:

```bash
./py2to3 precommit install
```

This will:
- Create `.pre-commit-config.yaml` in your repository root
- Generate a custom Python 3 validator hook
- Install the pre-commit framework hooks (if available)

### Custom Installation

Install with specific settings:

```bash
# Strict mode - fail on any Python 2 patterns
./py2to3 precommit install --mode strict

# Lenient mode - fail only on critical issues
./py2to3 precommit install --mode lenient

# Custom file patterns
./py2to3 precommit install --files-pattern "src/.*\\.py$"

# Exclude certain files
./py2to3 precommit install --exclude-pattern "tests/legacy/.*"

# Force overwrite existing configuration
./py2to3 precommit install --force
```

### Manual Installation of Pre-commit Framework

If the pre-commit framework is not installed:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks (run in your repository root)
pre-commit install
```

## Usage

### Automatic Usage

Once installed, hooks run automatically before each commit:

```bash
# Make changes to your code
vim myfile.py

# Stage changes
git add myfile.py

# Commit (hooks run automatically)
git commit -m "Update myfile.py"
```

If Python 2 code is detected:
```
🔍 Checking 1 Python file(s) for Python 3 compatibility...

❌ Python 2 compatibility issues detected:

  myfile.py: print statement at line 10

💡 Fix these issues before committing, or use 'git commit --no-verify' to bypass.
   (Not recommended during migration!)
```

### Bypassing Hooks (Not Recommended)

In rare cases where you need to bypass hooks:

```bash
git commit --no-verify -m "Emergency fix"
```

**Warning**: Only use this for exceptional cases. It defeats the purpose of the hooks.

## Configuration Modes

### Strict Mode

Fails on **any** Python 2 patterns, including:
- Print statements without parentheses
- Old-style imports (urllib2, ConfigParser, etc.)
- Dictionary iterator methods (iteritems, iterkeys, etc.)
- Unicode/basestring usage
- Old exception syntax
- And more...

**Use when**: Migration is complete and you want maximum protection.

```bash
./py2to3 precommit install --mode strict
```

### Normal Mode (Default)

Fails on **common** Python 2 issues that break Python 3:
- Print statements
- Old-style class definitions
- Common import changes
- Dictionary iterators
- Exception syntax issues

**Use when**: Actively migrating and want balanced protection.

```bash
./py2to3 precommit install --mode normal
```

### Lenient Mode

Fails only on **critical** issues that cause syntax errors:
- Critical syntax errors
- Import errors
- Major compatibility breaks

**Use when**: Starting migration and want gradual adoption.

```bash
./py2to3 precommit install --mode lenient
```

## Commands

### Install

Install pre-commit hooks:

```bash
./py2to3 precommit install [OPTIONS]
```

**Options:**
- `--mode {strict|normal|lenient}`: Validation strictness (default: normal)
- `--files-pattern PATTERN`: Regex pattern for files to check (default: `\.py$`)
- `--exclude-pattern PATTERN`: Regex pattern for files to exclude
- `--force`: Overwrite existing configuration
- `--repo-root PATH`: Repository root directory

### Uninstall

Remove pre-commit hooks:

```bash
./py2to3 precommit uninstall
```

This removes:
- `.pre-commit-config.yaml`
- Custom validator hook script
- Pre-commit framework hooks

### Status

Check pre-commit hook installation status:

```bash
./py2to3 precommit status
```

Shows:
- Git repository status
- Configuration file existence
- Hook script existence
- Pre-commit framework availability
- Installation status

Example output:
```
Git repository: Yes
Config exists: Yes
Custom hook exists: Yes
Pre-commit available: Yes
Pre-commit version: pre-commit 3.5.0
Pre-commit installed: Yes
Configuration mode: configured

✓ Pre-commit hooks are fully configured and active
```

### Test

Test pre-commit hooks without committing:

```bash
# Test all staged files
./py2to3 precommit test

# Test a specific file
./py2to3 precommit test --test-file myfile.py

# Test all files (runs on entire repository)
pre-commit run --all-files
```

## Examples

### Example 1: Basic Installation

```bash
# Navigate to your repository
cd my-project

# Install with default settings
./py2to3 precommit install

# Check status
./py2to3 precommit status

# Test without committing
./py2to3 precommit test
```

### Example 2: Strict Mode for Completed Migration

```bash
# Install strict hooks after migration
./py2to3 precommit install --mode strict

# Test all files
pre-commit run --all-files

# Commit changes
git add .
git commit -m "Add strict pre-commit hooks"
```

### Example 3: Custom File Patterns

```bash
# Only check src/ directory
./py2to3 precommit install --files-pattern "src/.*\\.py$"

# Exclude test files and migrations
./py2to3 precommit install \
  --exclude-pattern "(tests/|migrations/|docs/).*"
```

### Example 4: Team Setup

```bash
# 1. Install hooks
./py2to3 precommit install --mode normal

# 2. Commit configuration to repository
git add .pre-commit-config.yaml
git commit -m "Add pre-commit hooks for Python 3 migration"

# 3. Push to remote
git push origin main

# 4. Team members clone and install
git clone <repository>
cd <repository>
pre-commit install
```

### Example 5: Upgrading from Lenient to Strict

```bash
# Start with lenient mode
./py2to3 precommit install --mode lenient

# ... work on migration ...

# Upgrade to normal mode
./py2to3 precommit install --mode normal --force

# ... continue migration ...

# Final upgrade to strict mode
./py2to3 precommit install --mode strict --force
```

## Troubleshooting

### Hooks Not Running

**Problem**: Commits succeed without running hooks.

**Solution**:
```bash
# Check status
./py2to3 precommit status

# Reinstall if needed
./py2to3 precommit install

# If using pre-commit framework
pre-commit install
```

### False Positives

**Problem**: Hooks flag valid Python 3 code.

**Solution**:
- Switch to lenient mode: `./py2to3 precommit install --mode lenient --force`
- Exclude specific files: `./py2to3 precommit install --exclude-pattern "problematic/.*"`
- Bypass for specific commit (rare): `git commit --no-verify`

### Pre-commit Framework Not Found

**Problem**: Error message about missing pre-commit.

**Solution**:
```bash
# Install pre-commit framework
pip install pre-commit

# Reinstall hooks
./py2to3 precommit install
```

### Hooks Too Slow

**Problem**: Pre-commit hooks slow down commits.

**Solution**:
- Use lenient mode for faster checks
- Limit file patterns to reduce scope
- Run hooks in CI/CD instead for large files

### Permission Errors

**Problem**: Cannot create hook files.

**Solution**:
```bash
# Ensure you have write permissions
ls -la .git/hooks/

# Fix permissions if needed
chmod u+w .git/hooks/
```

## Integration with CI/CD

### GitHub Actions

Pre-commit hooks work seamlessly with CI/CD. Add to `.github/workflows/precommit.yml`:

```yaml
name: Pre-commit Checks

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install pre-commit
        run: pip install pre-commit
      - name: Run pre-commit
        run: pre-commit run --all-files
```

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
precommit:
  image: python:3.9
  before_script:
    - pip install pre-commit
  script:
    - pre-commit run --all-files
  only:
    - merge_requests
```

### Jenkins

```groovy
stage('Pre-commit') {
    steps {
        sh 'pip install pre-commit'
        sh 'pre-commit run --all-files'
    }
}
```

## Best Practices

### 1. Install Early

Install pre-commit hooks at the start of migration:
```bash
./py2to3 precommit install --mode lenient
```

### 2. Progressive Strictness

Start lenient, gradually increase strictness:
1. Begin: `--mode lenient`
2. Mid-migration: `--mode normal`
3. Post-migration: `--mode strict`

### 3. Team Adoption

Commit configuration to repository:
```bash
git add .pre-commit-config.yaml
git commit -m "Add Python 3 pre-commit hooks"
```

### 4. Document for Team

Add to your README:
```markdown
## Development Setup

After cloning, install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### 5. CI/CD Enforcement

Run hooks in CI/CD to catch bypassed commits:
```bash
pre-commit run --all-files
```

### 6. Regular Updates

Update hook configuration as migration progresses:
```bash
./py2to3 precommit install --mode normal --force
```

### 7. Test Before Committing

Test hooks on staged files before committing:
```bash
./py2to3 precommit test
```

## Advanced Usage

### Custom Validation Rules

Edit `.pre-commit-config.yaml` to add custom validators:

```yaml
  - repo: local
    hooks:
      - id: custom-check
        name: Custom Python 3 Check
        entry: python my_custom_checker.py
        language: system
        types: [python]
```

### Skip Specific Hooks

Skip specific hooks for a commit:
```bash
SKIP=py2to3-validator git commit -m "Special case"
```

### Automatic Fix and Commit

Combine with formatters for automatic fixes:
```yaml
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: ['--line-length=100']
```

## Related Commands

- `./py2to3 freeze` - Mark files as Python 3 only
- `./py2to3 check` - Manual compatibility check
- `./py2to3 validate` - Runtime validation
- `./py2to3 watch` - Continuous monitoring

## Summary

Pre-commit hooks are essential for successful Python 2 to 3 migration:

✅ **Prevention**: Stop Python 2 code before it enters the repository
✅ **Instant Feedback**: Developers get immediate validation
✅ **Team Consistency**: Enforce standards across the team
✅ **Time Savings**: Reduce manual review and fix time
✅ **Confidence**: Migrate with confidence, knowing code is validated

Install pre-commit hooks today:
```bash
./py2to3 precommit install
```

For more help:
```bash
./py2to3 precommit --help
```
