# CI/CD Integration Guide

## Overview

The Python 2 to 3 Migration Toolkit includes comprehensive CI/CD integration support through the `ci_helper.py` script, which works with any CI/CD system (GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis CI, etc.). This guide shows you how to set up automated Python 3 compatibility checking that runs on every push and pull request.

## Quick Start

The toolkit provides two ways to integrate with CI/CD:

1. **ci_helper.py script** - Standalone script that works with any CI/CD system
2. **Workflow templates** - Ready-to-use templates for popular CI/CD platforms

## Features

CI/CD integration provides:

- ✅ **Automated Compatibility Checks** - Runs on every push and PR
- 📊 **Migration Statistics** - Tracks progress over time
- 🛡️ **Preflight Safety Checks** - Validates environment before analysis
- 📝 **HTML Reports** - Beautiful, detailed compatibility reports
- 💬 **PR Comments** - Automatic feedback on pull requests (platform-dependent)
- 📦 **Artifact Storage** - Stores reports and statistics
- 🎯 **Smart Triggers** - Only runs when Python files change
- 🔧 **Platform Agnostic** - Works with any CI/CD system
- 📤 **Structured Output** - JSON and text formats for easy parsing
- ⚙️ **Configurable** - Flexible options for different workflows

## CI Helper Script

The `ci_helper.py` script is a standalone tool that runs py2to3 checks in any CI/CD environment.

### Usage

```bash
# Run full check (preflight + compatibility + stats + report)
python ci_helper.py full-check --scan-path src/ --output reports/

# Quick compatibility check only
python ci_helper.py quick-check --scan-path src/

# Preflight checks only
python ci_helper.py preflight --scan-path src/

# Generate report only
python ci_helper.py report --scan-path src/ --output reports/

# Collect statistics
python ci_helper.py stats --scan-path src/
```

### Options

- `--scan-path PATH` - Path to scan (default: src/)
- `--output DIR` - Output directory for reports (default: ci-reports)
- `--no-color` - Disable colored output
- `--ci-mode` - Enable CI/CD mode (JSON output, appropriate exit codes)
- `--fail-on-issues` - Exit with code 1 if compatibility issues found
- `--format {text,json}` - Output format

### Exit Codes

- `0` - Success (no errors)
- `1` - Failure (critical issues or compatibility issues if `--fail-on-issues` is set)
- `130` - Interrupted by user

### Examples

```bash
# Basic usage in CI/CD
python ci_helper.py full-check --scan-path src/

# Strict mode - fail build if issues found
python ci_helper.py full-check --scan-path src/ --fail-on-issues

# CI mode with JSON output
python ci_helper.py quick-check --scan-path src/ --ci-mode

# Custom output directory
python ci_helper.py full-check --scan-path myapp/ --output build/reports/
```

## Workflow Templates

Below are ready-to-use CI/CD workflow templates for popular platforms. Copy the appropriate template to your repository and customize as needed.

### GitHub Actions

Create `.github/workflows/py2to3-check.yml`:

```yaml
name: Python 2 to 3 Compatibility Check

on:
  push:
    branches: [ main, develop ]
    paths:
      - '**.py'
  pull_request:
    branches: [ main, develop ]
    paths:
      - '**.py'

jobs:
  py3-compatibility:
    name: Check Python 3 Compatibility
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          chmod +x py2to3 ci_helper.py
      
      - name: Run full migration check
        run: |
          python ci_helper.py full-check --scan-path src/ --output ci-reports/
      
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: py3-compatibility-reports
          path: ci-reports/
          retention-days: 30
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
py3-compatibility-check:
  stage: test
  image: python:3.11
  
  script:
    - python -m pip install --upgrade pip
    - pip install pytest
    - if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - chmod +x py2to3 ci_helper.py
    - python ci_helper.py full-check --scan-path src/ --output ci-reports/
  
  artifacts:
    paths:
      - ci-reports/
    expire_in: 30 days
    when: always
  
  only:
    changes:
      - "**/*.py"
```

### CircleCI

Create `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  py3-compatibility:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: |
            python -m pip install --upgrade pip
            pip install pytest
            if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
            chmod +x py2to3 ci_helper.py
      - run:
          name: Run migration check
          command: |
            python ci_helper.py full-check --scan-path src/ --output ci-reports/
      - store_artifacts:
          path: ci-reports/
          destination: py3-compatibility-reports

workflows:
  version: 2
  test:
    jobs:
      - py3-compatibility:
          filters:
            branches:
              only:
                - main
                - develop
```

### Jenkins

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install pytest
                    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
                '''
            }
        }
        
        stage('Python 3 Compatibility Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    chmod +x py2to3 ci_helper.py
                    python ci_helper.py full-check --scan-path src/ --output ci-reports/
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'ci-reports/**', allowEmptyArchive: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'ci-reports',
                reportFiles: 'py3-compatibility-report.html',
                reportName: 'Python 3 Compatibility Report'
            ])
        }
    }
}
```

### Travis CI

Create `.travis.yml`:

```yaml
language: python
python:
  - "3.11"

install:
  - pip install pytest
  - if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
  - chmod +x py2to3 ci_helper.py

script:
  - python ci_helper.py full-check --scan-path src/ --output ci-reports/

after_success:
  - echo "Python 3 compatibility check completed"

cache:
  directories:
    - $HOME/.cache/pip
```

## Workflow Steps

The `ci_helper.py` script runs the following checks in sequence:

### 1. Preflight Safety Checks

Validates the project environment:
- Git status and uncommitted changes
- Disk space availability
- File permissions
- Python version compatibility
- Project structure integrity

### 2. Python 3 Compatibility Check

Scans code for Python 2 patterns:
- Print statements, import changes, iterator methods
- Exception syntax, string handling
- 30+ other Python 2 patterns

### 3. Migration Statistics

Collects comprehensive progress statistics:
- Total Python files, clean vs. problematic files
- Issue counts by type and severity
- Progress percentage, historical trends

### 4. HTML Report Generation

Creates an interactive HTML report with:
- Visual charts and graphs
- Before/after code comparisons
- Issue tracking with severity levels
- Progress visualization

## Setup Instructions

### Option 1: Quick Setup with Template

1. **Choose your CI/CD platform** from the templates above
2. **Copy the template** to the appropriate file in your repository
3. **Customize paths** if needed (default is `src/`)
4. **Commit and push** - The CI/CD will run automatically!

```bash
# Example for GitHub Actions
mkdir -p .github/workflows
# Copy the GitHub Actions template to .github/workflows/py2to3-check.yml
git add .github/workflows/py2to3-check.yml
git commit -m "Add Python 3 compatibility CI/CD check"
git push
```

### Option 2: Manual Integration

If you have an existing CI/CD pipeline:

1. **Add ci_helper.py to your repository** (already included)
2. **Add a step to your pipeline** to run the check:

```bash
python ci_helper.py full-check --scan-path src/ --output ci-reports/
```

3. **Configure artifact storage** to save the reports
4. **Optionally enable strict mode** with `--fail-on-issues` to block PRs with issues

### Customization

All templates can be customized:

**Change scan path:**
```bash
python ci_helper.py full-check --scan-path myapp/ --output ci-reports/
```

**Enable strict mode (fail on issues):**
```bash
python ci_helper.py full-check --scan-path src/ --fail-on-issues
```

**JSON output for parsing:**
```bash
python ci_helper.py full-check --scan-path src/ --ci-mode
```

**Quick check only (faster):**
```bash
python ci_helper.py quick-check --scan-path src/
```

## Viewing Results

### CI/CD Dashboard

Results are available in your CI/CD platform:

**GitHub Actions:**
- Go to **Actions** tab → Click workflow run → View logs and download artifacts

**GitLab CI:**
- Go to **CI/CD** → **Pipelines** → Click pipeline → View jobs and artifacts

**Jenkins:**
- Open build → View console output and published HTML reports

**CircleCI:**
- Go to **Jobs** → Click job → View steps and download artifacts

### Generated Files

The `ci_helper.py` script generates:

**In ci-reports/ directory:**
- `py3-compatibility-report.html` - Interactive HTML report with charts
- `compatibility-report-TIMESTAMP.txt` - Text report with issue list
- `ci-results.json` - Structured JSON results for parsing

**In .py2to3-stats/ directory:**
- `snapshot_TIMESTAMP.json` - Statistics snapshot
- `latest.json` - Most recent statistics
- Enables trend analysis over time

### Report Contents

The HTML report includes:

- **Overview:** Summary statistics and progress percentage
- **Issue List:** Detailed compatibility issues with severity
- **File Analysis:** Per-file breakdown with issue counts
- **Charts:** Visual representation of issues by type and severity
- **Timeline:** Progress over time (if multiple snapshots exist)

### JSON Output Format

When using `--ci-mode` or `--format json`, output structure:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "scan_path": "src/",
  "preflight": {
    "status": "READY",
    "critical_issues": 0
  },
  "compatibility_check": {
    "issue_count": 5,
    "report_file": "compatibility-report-20240115_103000.txt"
  },
  "statistics": {
    "collected": true
  },
  "report": {
    "generated": true,
    "report_file": "ci-reports/py3-compatibility-report.html"
  }
}
```

## Integration with Migration Workflow

The CI/CD checks complement your migration process:

### Recommended Workflow

1. **Initial Setup**
   ```bash
   ./py2to3 preflight src/              # Check readiness
   ./py2to3 stats collect src/ --save    # Baseline statistics
   ```

2. **Iterative Migration** (per module/file)
   ```bash
   ./py2to3 fix src/mymodule/ --backup-dir backups
   pytest tests/test_mymodule.py
   git commit -am "Migrate mymodule to Python 3"
   git push                              # CI/CD runs automatically
   ```

3. **Track Progress**
   ```bash
   ./py2to3 stats trend                  # View local trends
   # Or download artifacts from CI/CD to compare snapshots
   ```

## Best Practices

### Development
- Run checks locally before pushing: `./py2to3 check src/`
- Review preflight checks: `./py2to3 preflight src/ --verbose`
- Always use backups: `./py2to3 fix src/ --backup-dir backups`

### CI/CD
- Review HTML reports - they provide detailed context
- Monitor statistics over time to track progress
- Use `--fail-on-issues` for strict quality gates
- Configure branch protection to require checks to pass

### Team Collaboration
- Commit `.py2to3.config.json` for shared settings
- Set migration goals and milestones
- Celebrate progress as modules become clean!

## Troubleshooting

### CI Helper Issues

**Script not found:**
```bash
# Ensure ci_helper.py is executable and in the repo
chmod +x ci_helper.py
```

**py2to3 not found:**
```bash
# Ensure py2to3 is executable and in PATH or current directory
chmod +x py2to3
export PATH=$PATH:$(pwd)
```

**Incorrect results:**
- Clear cache: `rm -rf .py2to3-stats/` and re-run
- Verify Python version matches your environment
- Ensure latest code is being checked

**Timeout on large codebases:**
- Use `quick-check` instead of `full-check`
- Limit scan path to specific directories
- Split into multiple jobs

### Platform-Specific Issues

**GitHub Actions:**
- Verify Python files were modified (check workflow trigger paths)
- Ensure Actions are enabled for your repository

**GitLab CI:**
- Check that runner has required permissions
- Verify artifact storage is enabled

**Jenkins:**
- Ensure Python 3 is installed on build agents
- Configure artifact archiving in post-build actions

## Advanced Configuration

### Multiple Scan Paths

Run separate checks for different parts of your codebase:

```bash
# In your CI/CD pipeline
python ci_helper.py full-check --scan-path src/core/ --output reports/core/
python ci_helper.py full-check --scan-path src/web/ --output reports/web/
python ci_helper.py full-check --scan-path src/utils/ --output reports/utils/
```

### Scheduled Runs

Most CI/CD platforms support scheduled runs:

**GitHub Actions:** Add `schedule:` trigger with cron syntax  
**GitLab CI:** Use `only: - schedules` with pipeline schedules  
**Jenkins:** Configure build triggers with cron syntax  
**CircleCI:** Use `workflows` with `triggers` section

### Integration with Notifications

Parse JSON output to send notifications:

```bash
# Run with JSON output
python ci_helper.py full-check --scan-path src/ --ci-mode > results.json

# Parse and send to Slack/email/etc.
issue_count=$(jq '.compatibility_check.issue_count' results.json)
if [ "$issue_count" -gt 0 ]; then
  echo "Found $issue_count issues" | send-notification
fi
```

## Performance Optimization

### Quick Check Mode
For faster feedback, use `quick-check` instead of `full-check`:
```bash
python ci_helper.py quick-check --scan-path src/
```

### Caching
Cache dependencies and results between runs:
```yaml
# Example for GitHub Actions
- uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      .py2to3-stats/
    key: ${{ runner.os }}-py2to3-${{ hashFiles('**/*.py') }}
```

### Parallel Execution
Split large codebases into parallel jobs:
```bash
# Run multiple checks in parallel
python ci_helper.py quick-check --scan-path src/core/ &
python ci_helper.py quick-check --scan-path src/web/ &
python ci_helper.py quick-check --scan-path src/utils/ &
wait
```

## FAQ

**Q: Will this fail my build if issues are found?**  
A: By default, no. Use `--fail-on-issues` flag to fail on compatibility issues.

**Q: Can I use this with any CI/CD system?**  
A: Yes! The `ci_helper.py` script works with any CI/CD platform. Use the templates provided or integrate manually.

**Q: How long does it take to run?**  
A: Typically 2-5 minutes depending on codebase size. Use `quick-check` for faster results.

**Q: Can I customize the output format?**  
A: Yes! Use `--format json` for JSON output, or parse the generated reports.

**Q: Do I need special permissions?**  
A: Only read access to your code is required. Some platforms may need artifact storage permissions configured.

## Related Documentation

- 📚 [Main README](README.md) - Overview and getting started
- 🛠️ [CLI Guide](CLI_GUIDE.md) - Command-line interface
- 📊 [Statistics Guide](STATISTICS_GUIDE.md) - Migration tracking
- 💾 [Backup Guide](BACKUP_GUIDE.md) - Backup best practices

## Summary

The CI/CD integration provides automated Python 3 compatibility checking through:

1. **ci_helper.py script** - Universal tool for any CI/CD platform
2. **Ready-to-use templates** - For GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis CI
3. **Flexible configuration** - Customize paths, output formats, and failure conditions
4. **Comprehensive reports** - HTML, text, and JSON output formats
5. **Progress tracking** - Historical statistics for migration monitoring

Get started by copying a template or integrating `ci_helper.py` into your existing pipeline!

---

Happy migrating! 🐍✨
