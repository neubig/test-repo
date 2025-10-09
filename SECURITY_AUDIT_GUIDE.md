# 🔒 Security Audit Guide

## Overview

The Security Auditor is a specialized tool designed to identify security vulnerabilities that may be introduced during Python 2 to Python 3 migration. During migration, subtle changes in string handling, encoding, and API usage can inadvertently create security holes.

## Why Security Auditing Matters

Python 2 to 3 migrations often involve:
- **String/bytes handling changes** that can mask encoding vulnerabilities
- **API updates** that may change security-critical behavior
- **Automatic fixes** that might introduce unsafe patterns
- **Input validation changes** due to type system differences
- **Cryptographic function updates** with different security properties

The Security Auditor helps catch these issues before they reach production.

## Quick Start

```bash
# Audit current directory
./py2to3 security

# Audit specific directory
./py2to3 security src/

# Audit with detailed output
./py2to3 security src/ -v

# Save report to file
./py2to3 security src/ -o security_report.txt

# Generate JSON report
./py2to3 security src/ -f json -o security_report.json

# Fail CI/CD if critical/high issues found
./py2to3 security src/ --fail-on-high
```

## What It Detects

### 1. Encoding Vulnerabilities 🔤

**Issues Detected:**
- Latin-1 decoding that can mask encoding errors
- Unnecessary encode/decode chains
- Direct `str()` conversion of bytes without proper handling

**Example:**
```python
# VULNERABLE
data = response.content.decode('latin-1')  # HIGH severity

# SECURE
data = response.content.decode('utf-8', errors='strict')
```

### 2. Injection Vulnerabilities 💉

**Issues Detected:**
- SQL injection via string formatting or concatenation
- Command injection in `os.system()` or subprocess
- Code injection via `eval()` or `exec()`

**Examples:**
```python
# VULNERABLE - SQL Injection
cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)  # CRITICAL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")     # CRITICAL

# SECURE
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# VULNERABLE - Command Injection
os.system("ls " + user_input)                     # CRITICAL
subprocess.run("ls " + user_input, shell=True)    # HIGH

# SECURE
subprocess.run(["ls", user_input], shell=False)
```

### 3. Cryptographic Weaknesses 🔐

**Issues Detected:**
- Use of MD5 or SHA-1 for security purposes
- Weak random number generation with `random` module
- Unsafe deserialization with pickle

**Examples:**
```python
# VULNERABLE
import hashlib
password_hash = hashlib.md5(password).hexdigest()  # HIGH severity

import random
token = random.random()  # MEDIUM severity for security use

# SECURE
import hashlib
password_hash = hashlib.sha256(password).hexdigest()

import secrets
token = secrets.token_hex(32)
```

### 4. Deserialization Vulnerabilities 📦

**Issues Detected:**
- Pickle, YAML, or marshal deserialization
- Can lead to arbitrary code execution

**Examples:**
```python
# VULNERABLE
import pickle
data = pickle.loads(untrusted_data)  # HIGH severity

# SECURE - Use JSON instead
import json
data = json.loads(untrusted_data)
```

### 5. Path Traversal Vulnerabilities 📁

**Issues Detected:**
- User input in file paths without validation
- Unsafe path construction

**Examples:**
```python
# VULNERABLE
filename = request.args.get('file')
with open(filename, 'r') as f:  # MEDIUM severity
    content = f.read()

# SECURE
from pathlib import Path
filename = request.args.get('file')
safe_path = Path('/safe/directory') / filename
safe_path = safe_path.resolve()
if safe_path.is_relative_to('/safe/directory'):
    with open(safe_path, 'r') as f:
        content = f.read()
```

### 6. Timing Attack Vulnerabilities ⏱️

**Issues Detected:**
- Direct string comparison for passwords or tokens
- Should use constant-time comparison

**Examples:**
```python
# VULNERABLE
if user_password == stored_password:  # HIGH severity
    authenticate()

# SECURE
import secrets
if secrets.compare_digest(user_password, stored_password):
    authenticate()
```

### 7. Hardcoded Secrets 🔑

**Issues Detected:**
- API keys, passwords, tokens hardcoded in source
- Detected via AST analysis

**Examples:**
```python
# VULNERABLE
API_KEY = "sk_live_abc123xyz789"  # CRITICAL severity
PASSWORD = "mySecretPass123"       # CRITICAL severity

# SECURE
import os
API_KEY = os.environ.get('API_KEY')
PASSWORD = os.environ.get('PASSWORD')
```

## Command Options

### Basic Usage

```bash
./py2to3 security [path] [options]
```

### Options

| Option | Description |
|--------|-------------|
| `path` | File or directory to audit (default: current directory) |
| `-o, --output FILE` | Save report to file |
| `-f, --format {text,json}` | Report format (default: text) |
| `--exclude PATTERN [PATTERN ...]` | Patterns to exclude from scanning |
| `--fail-on-high` | Exit with error code if high/critical issues found |
| `-v, --verbose` | Enable verbose output |

### Examples

```bash
# Audit with custom exclusions
./py2to3 security src/ --exclude test_* *_test.py fixtures

# JSON output for CI/CD integration
./py2to3 security src/ -f json -o security.json

# Fail build on serious issues
./py2to3 security src/ --fail-on-high
if [ $? -ne 0 ]; then
    echo "Security audit failed!"
    exit 1
fi
```

## Understanding Severity Levels

### CRITICAL 🔴
- Immediate risk of compromise
- **Examples:** SQL injection, code injection, hardcoded secrets
- **Action:** Fix immediately before deployment

### HIGH 🟠
- Significant security risk
- **Examples:** Command injection with shell=True, weak crypto, deserialization
- **Action:** Fix in current sprint/release

### MEDIUM 🟡
- Moderate security concern
- **Examples:** Encoding issues, file path concerns, weak RNG
- **Action:** Address in upcoming releases

### LOW 🔵
- Minor security issue
- **Examples:** Unvalidated input (context-dependent)
- **Action:** Review and address as time permits

### INFO ℹ️
- Informational findings
- **Examples:** Best practice suggestions
- **Action:** Consider for code quality improvements

## Integration with CI/CD

### GitHub Actions

```yaml
name: Security Audit

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run security audit
        run: |
          ./py2to3 security src/ --fail-on-high -o security_report.txt
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: security_report.txt
```

### GitLab CI

```yaml
security_audit:
  stage: test
  script:
    - pip install -r requirements.txt
    - ./py2to3 security src/ --fail-on-high -f json -o security.json
  artifacts:
    reports:
      junit: security.json
    paths:
      - security.json
    when: always
```

## Best Practices

### 1. **Run Early and Often**
- Run security audit after each migration fix session
- Include in pre-commit hooks for critical projects
- Run in CI/CD on every pull request

### 2. **Address by Severity**
- Fix CRITICAL issues immediately
- Schedule HIGH issues for current sprint
- Plan MEDIUM/LOW issues for upcoming releases

### 3. **Review Automated Fixes**
- Always review automatic migration fixes for security implications
- Pay special attention to string handling changes
- Verify input validation remains intact

### 4. **Use with Other Tools**
- Complement with tools like Bandit, Safety, and Snyk
- Security auditor focuses on migration-specific issues
- Use traditional security tools for general vulnerabilities

### 5. **Document Exceptions**
- If a finding is a false positive, document why
- Add code comments explaining security considerations
- Consider using `# nosec` comments for acknowledged exceptions

## Report Formats

### Text Format (Default)

Provides human-readable report with:
- Summary statistics by severity
- Issues grouped by category
- Detailed findings with remediation advice
- Security recommendations

**Example:**
```
================================================================================
SECURITY AUDIT REPORT - Python 2 to Python 3 Migration
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Total Issues Found: 12
  • CRITICAL: 2
  • HIGH:     4
  • MEDIUM:   5
  • LOW:      1
  • INFO:     0

ISSUES BY CATEGORY
--------------------------------------------------------------------------------
  • injection: 6
  • crypto: 3
  • encoding: 2
  • secrets: 1

DETAILED FINDINGS
================================================================================

CRITICAL SEVERITY (2 issues)
--------------------------------------------------------------------------------
File: src/database.py:45
Category: injection
Description: SQL injection vulnerability: String formatting in SQL queries
Code: cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)
Remediation: Use parameterized queries with placeholders
...
```

### JSON Format

Machine-readable format for CI/CD integration:

```json
{
  "summary": {
    "total_issues": 12,
    "by_severity": {
      "critical": 2,
      "high": 4,
      "medium": 5,
      "low": 1,
      "info": 0
    },
    "by_category": {
      "injection": 6,
      "crypto": 3,
      "encoding": 2,
      "secrets": 1
    }
  },
  "issues": [
    {
      "filename": "src/database.py",
      "line": 45,
      "severity": "CRITICAL",
      "category": "injection",
      "description": "SQL injection vulnerability: String formatting in SQL queries",
      "code_snippet": "cursor.execute(\"SELECT * FROM users WHERE id = %s\" % user_id)",
      "remediation": "Use parameterized queries with placeholders: execute(\"SELECT * FROM table WHERE id = ?\", (id,))"
    }
  ]
}
```

## Common False Positives

### String Comparisons
- **Finding:** Token/password comparison flagged
- **False Positive When:** Comparing non-security-critical strings
- **Solution:** Document or rename variables to avoid security keywords

### Pickle Usage
- **Finding:** Pickle deserialization flagged
- **False Positive When:** Only used with trusted internal data
- **Solution:** Add comment explaining trust model

### eval() Usage
- **Finding:** eval() usage flagged
- **False Positive When:** Input is fully controlled (e.g., test data)
- **Solution:** Consider `ast.literal_eval()` or document safety

## Advanced Usage

### Programmatic Usage

You can use the Security Auditor as a Python library:

```python
from security_auditor import SecurityAuditor, SecurityIssue

# Create auditor
auditor = SecurityAuditor(verbose=True)

# Audit directory
issues = auditor.audit_directory('src/', exclude_patterns=['tests'])

# Filter critical issues
critical = [i for i in issues if i.severity == SecurityIssue.SEVERITY_CRITICAL]

# Generate report
report = auditor.generate_report('json')

# Custom analysis
for issue in critical:
    print(f"{issue.filename}:{issue.line} - {issue.description}")
    print(f"  Fix: {issue.remediation}\n")
```

### Custom Integration

```python
from security_auditor import SecurityAuditor
import sys

def check_security(path, fail_threshold='HIGH'):
    auditor = SecurityAuditor()
    auditor.audit_directory(path)
    
    severity_map = {
        'CRITICAL': 4,
        'HIGH': 3,
        'MEDIUM': 2,
        'LOW': 1
    }
    
    threshold = severity_map.get(fail_threshold, 3)
    
    for issue in auditor.issues:
        issue_level = severity_map.get(issue.severity, 0)
        if issue_level >= threshold:
            print(f"Security issue in {issue.filename}:{issue.line}")
            print(f"  {issue.description}")
            return False
    
    return True

if __name__ == '__main__':
    if not check_security('src/', fail_threshold='HIGH'):
        sys.exit(1)
```

## Troubleshooting

### Issue: Too Many False Positives

**Solution:** Use `--exclude` to skip test files and known-safe code:
```bash
./py2to3 security src/ --exclude tests test_* *_test.py fixtures
```

### Issue: Report Too Large

**Solution:** Use JSON format and process with jq or Python:
```bash
./py2to3 security src/ -f json | jq '.issues[] | select(.severity == "CRITICAL")'
```

### Issue: Can't Parse File

**Solution:** Run with `-v` to see which files cause issues:
```bash
./py2to3 security src/ -v
```

## Related Tools

### Complementary Security Tools
- **Bandit:** General Python security linter
- **Safety:** Checks dependencies for known vulnerabilities
- **Snyk:** Comprehensive security scanning
- **pip-audit:** Audits Python dependencies

### Migration-Specific Tools
- Use Security Auditor alongside:
  - `./py2to3 check` - Compatibility checking
  - `./py2to3 risk` - Change risk analysis
  - `./py2to3 quality` - Code quality metrics

## FAQ

**Q: Should I fix all issues before deploying?**
A: Fix CRITICAL and HIGH severity issues before deployment. MEDIUM and LOW can be scheduled for upcoming releases.

**Q: Are these all real vulnerabilities?**
A: Context matters. Review each finding to determine if it's a real vulnerability in your specific use case.

**Q: Can this replace other security tools?**
A: No. Use it alongside general security tools. It focuses on migration-specific issues.

**Q: How often should I run this?**
A: Run after each migration fix session, and include in CI/CD for continuous monitoring.

**Q: What about third-party dependencies?**
A: This tool checks your code. Use `safety` or `pip-audit` for dependency vulnerabilities.

## Contributing

Found a security pattern we missed? Contribute to the Security Auditor:

1. Add patterns to `src/security_auditor.py`
2. Test with real-world examples
3. Submit a pull request with examples

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [PEP 506 - Secrets Module](https://www.python.org/dev/peps/pep-0506/)
- [CWE Database](https://cwe.mitre.org/)

## Support

For issues or questions about the Security Auditor:
- Check this guide first
- Review the [main README](README.md)
- Open an issue on GitHub

---

**Remember:** Security is a journey, not a destination. Regular auditing is key to maintaining secure code! 🔒
