#!/usr/bin/env python3
"""
Security Auditor for Python 2 to Python 3 Migrations

Identifies security vulnerabilities that may be introduced during
Python 2 to Python 3 migration process, including:
- String encoding vulnerabilities
- Input validation issues
- Cryptographic concerns
- SQL injection risks
- Pickle/serialization security
- Path traversal vulnerabilities
"""

import ast
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class SecurityIssue:
    """Represents a security issue found in code"""
    
    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_HIGH = "HIGH"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_LOW = "LOW"
    SEVERITY_INFO = "INFO"
    
    def __init__(self, filename: str, line: int, severity: str, category: str, 
                 description: str, code_snippet: str = "", remediation: str = ""):
        self.filename = filename
        self.line = line
        self.severity = severity
        self.category = category
        self.description = description
        self.code_snippet = code_snippet
        self.remediation = remediation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'filename': self.filename,
            'line': self.line,
            'severity': self.severity,
            'category': self.category,
            'description': self.description,
            'code_snippet': self.code_snippet,
            'remediation': self.remediation
        }


class SecurityAuditor:
    """Audits Python code for security vulnerabilities during Py2->Py3 migration"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues: List[SecurityIssue] = []
        self.stats = defaultdict(int)
        
        # Security patterns to detect
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize security vulnerability patterns"""
        return {
            'encoding': [
                {
                    'pattern': r'\.decode\(\s*["\']latin-?1["\']\s*\)',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Latin-1 decoding can mask encoding errors and lead to vulnerabilities',
                    'remediation': 'Use UTF-8 encoding and proper error handling: .decode("utf-8", errors="strict")'
                },
                {
                    'pattern': r'\.encode\(\s*\)\.decode\(\s*\)',
                    'severity': SecurityIssue.SEVERITY_MEDIUM,
                    'description': 'Unnecessary encode/decode chain can introduce encoding vulnerabilities',
                    'remediation': 'Remove unnecessary encoding operations or use explicit encoding'
                },
                {
                    'pattern': r'str\s*\(\s*bytes',
                    'severity': SecurityIssue.SEVERITY_MEDIUM,
                    'description': 'Direct str() conversion of bytes can lead to incorrect data representation',
                    'remediation': 'Use explicit .decode() with proper encoding and error handling'
                }
            ],
            'injection': [
                {
                    'pattern': r'execute\s*\(\s*["\'].*%s.*["\']\s*%',
                    'severity': SecurityIssue.SEVERITY_CRITICAL,
                    'description': 'SQL injection vulnerability: String formatting in SQL queries',
                    'remediation': 'Use parameterized queries with placeholders: execute("SELECT * FROM table WHERE id = ?", (id,))'
                },
                {
                    'pattern': r'execute\s*\(\s*f["\']',
                    'severity': SecurityIssue.SEVERITY_CRITICAL,
                    'description': 'SQL injection vulnerability: f-string in SQL query',
                    'remediation': 'Use parameterized queries instead of f-strings for SQL'
                },
                {
                    'pattern': r'execute\s*\(\s*.*\+',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Possible SQL injection: String concatenation in query',
                    'remediation': 'Use parameterized queries instead of string concatenation'
                },
                {
                    'pattern': r'os\.system\s*\(\s*.*\+',
                    'severity': SecurityIssue.SEVERITY_CRITICAL,
                    'description': 'Command injection vulnerability: Unsanitized input in os.system()',
                    'remediation': 'Use subprocess with shell=False and a list of arguments'
                },
                {
                    'pattern': r'subprocess\..*shell\s*=\s*True',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Command injection risk: subprocess with shell=True',
                    'remediation': 'Use shell=False and pass command as a list'
                },
                {
                    'pattern': r'eval\s*\(',
                    'severity': SecurityIssue.SEVERITY_CRITICAL,
                    'description': 'Code injection vulnerability: Use of eval() with untrusted input',
                    'remediation': 'Avoid eval(). Use ast.literal_eval() for safe evaluation of literals'
                },
                {
                    'pattern': r'exec\s*\(',
                    'severity': SecurityIssue.SEVERITY_CRITICAL,
                    'description': 'Code injection vulnerability: Use of exec() with untrusted input',
                    'remediation': 'Avoid exec(). Redesign to avoid dynamic code execution'
                }
            ],
            'crypto': [
                {
                    'pattern': r'md5\s*\(',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Weak cryptographic hash: MD5 is cryptographically broken',
                    'remediation': 'Use SHA-256 or stronger: hashlib.sha256()'
                },
                {
                    'pattern': r'sha1\s*\(',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Weak cryptographic hash: SHA-1 is deprecated for security',
                    'remediation': 'Use SHA-256 or stronger: hashlib.sha256()'
                },
                {
                    'pattern': r'random\.random\s*\(',
                    'severity': SecurityIssue.SEVERITY_MEDIUM,
                    'description': 'Weak random number generation for security purposes',
                    'remediation': 'Use secrets module for cryptographic purposes: secrets.token_bytes()'
                },
                {
                    'pattern': r'pickle\.loads?\s*\(',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Pickle deserialization can execute arbitrary code',
                    'remediation': 'Never unpickle untrusted data. Use JSON or other safe serialization'
                }
            ],
            'files': [
                {
                    'pattern': r'open\s*\(\s*.*\+.*["\']w',
                    'severity': SecurityIssue.SEVERITY_MEDIUM,
                    'description': 'File path from user input without validation',
                    'remediation': 'Validate and sanitize file paths. Use Path().resolve() to prevent traversal'
                },
                {
                    'pattern': r'os\.path\.join\s*\([^)]*input',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Path traversal vulnerability: User input in path construction',
                    'remediation': 'Validate paths and use Path().resolve() to prevent directory traversal'
                }
            ],
            'web': [
                {
                    'pattern': r'\.format\s*\([^)]*request\.',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Potential XSS: Request data in string formatting',
                    'remediation': 'Always escape user input before rendering in HTML'
                },
                {
                    'pattern': r'input\s*\(\s*["\']',
                    'severity': SecurityIssue.SEVERITY_LOW,
                    'description': 'User input without validation',
                    'remediation': 'Always validate and sanitize user input'
                }
            ],
            'comparison': [
                {
                    'pattern': r'==\s*["\'].*password',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Timing attack vulnerability: String comparison for passwords',
                    'remediation': 'Use secrets.compare_digest() for constant-time comparison'
                },
                {
                    'pattern': r'==\s*["\'].*token',
                    'severity': SecurityIssue.SEVERITY_HIGH,
                    'description': 'Timing attack vulnerability: String comparison for tokens',
                    'remediation': 'Use secrets.compare_digest() for constant-time comparison'
                }
            ]
        }
    
    def audit_file(self, filepath: str) -> List[SecurityIssue]:
        """Audit a single Python file for security issues"""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Pattern-based checks
            for category, patterns in self.patterns.items():
                for pattern_info in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                            issue = SecurityIssue(
                                filename=filepath,
                                line=line_num,
                                severity=pattern_info['severity'],
                                category=category,
                                description=pattern_info['description'],
                                code_snippet=line.strip(),
                                remediation=pattern_info['remediation']
                            )
                            issues.append(issue)
                            self.stats[category] += 1
                            self.stats[f'severity_{pattern_info["severity"]}'] += 1
            
            # AST-based checks for more complex patterns
            try:
                tree = ast.parse(content, filename=filepath)
                issues.extend(self._ast_audit(tree, filepath, lines))
            except SyntaxError:
                if self.verbose:
                    print(f"Warning: Could not parse {filepath} for AST analysis")
        
        except Exception as e:
            if self.verbose:
                print(f"Error auditing {filepath}: {e}")
        
        return issues
    
    def _ast_audit(self, tree: ast.AST, filepath: str, lines: List[str]) -> List[SecurityIssue]:
        """Perform AST-based security analysis"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for hardcoded secrets
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id.lower()
                        if any(secret in name for secret in ['password', 'secret', 'token', 'api_key', 'apikey']):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                if len(node.value.value) > 8:  # Likely a real secret
                                    issue = SecurityIssue(
                                        filename=filepath,
                                        line=node.lineno,
                                        severity=SecurityIssue.SEVERITY_CRITICAL,
                                        category='secrets',
                                        description=f'Hardcoded secret in variable: {target.id}',
                                        code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else '',
                                        remediation='Use environment variables or a secrets management system'
                                    )
                                    issues.append(issue)
                                    self.stats['secrets'] += 1
                                    self.stats['severity_CRITICAL'] += 1
            
            # Check for unsafe deserialization
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['loads', 'load'] and hasattr(node.func.value, 'id'):
                        if node.func.value.id in ['pickle', 'yaml', 'marshal']:
                            issue = SecurityIssue(
                                filename=filepath,
                                line=node.lineno,
                                severity=SecurityIssue.SEVERITY_HIGH,
                                category='deserialization',
                                description=f'Unsafe deserialization using {node.func.value.id}.{node.func.attr}()',
                                code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else '',
                                remediation='Avoid deserializing untrusted data. Use JSON for safe data exchange'
                            )
                            issues.append(issue)
                            self.stats['deserialization'] += 1
                            self.stats['severity_HIGH'] += 1
        
        return issues
    
    def audit_directory(self, directory: str, exclude_patterns: List[str] = None) -> List[SecurityIssue]:
        """Audit all Python files in a directory"""
        if exclude_patterns is None:
            exclude_patterns = ['venv', '__pycache__', '.git', 'node_modules', 'tests']
        
        all_issues = []
        
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if self.verbose:
                        print(f"Auditing: {filepath}")
                    issues = self.audit_file(filepath)
                    all_issues.extend(issues)
        
        self.issues = all_issues
        return all_issues
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate security audit report"""
        if output_format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate text format report"""
        report = []
        report.append("=" * 80)
        report.append("SECURITY AUDIT REPORT - Python 2 to Python 3 Migration")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Issues Found: {len(self.issues)}")
        report.append(f"  • CRITICAL: {self.stats.get('severity_CRITICAL', 0)}")
        report.append(f"  • HIGH:     {self.stats.get('severity_HIGH', 0)}")
        report.append(f"  • MEDIUM:   {self.stats.get('severity_MEDIUM', 0)}")
        report.append(f"  • LOW:      {self.stats.get('severity_LOW', 0)}")
        report.append(f"  • INFO:     {self.stats.get('severity_INFO', 0)}")
        report.append("")
        
        # Issues by category
        report.append("ISSUES BY CATEGORY")
        report.append("-" * 80)
        categories = set(issue.category for issue in self.issues)
        for category in sorted(categories):
            count = sum(1 for issue in self.issues if issue.category == category)
            report.append(f"  • {category}: {count}")
        report.append("")
        
        # Detailed issues
        report.append("DETAILED FINDINGS")
        report.append("=" * 80)
        report.append("")
        
        # Group by severity
        for severity in [SecurityIssue.SEVERITY_CRITICAL, SecurityIssue.SEVERITY_HIGH,
                        SecurityIssue.SEVERITY_MEDIUM, SecurityIssue.SEVERITY_LOW,
                        SecurityIssue.SEVERITY_INFO]:
            severity_issues = [i for i in self.issues if i.severity == severity]
            if not severity_issues:
                continue
            
            report.append(f"{severity} SEVERITY ({len(severity_issues)} issues)")
            report.append("-" * 80)
            
            for issue in severity_issues:
                report.append(f"File: {issue.filename}:{issue.line}")
                report.append(f"Category: {issue.category}")
                report.append(f"Description: {issue.description}")
                if issue.code_snippet:
                    report.append(f"Code: {issue.code_snippet}")
                report.append(f"Remediation: {issue.remediation}")
                report.append("")
        
        # Recommendations
        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        report.append("")
        report.append("1. Address CRITICAL and HIGH severity issues immediately")
        report.append("2. Review encoding/decoding operations for proper UTF-8 handling")
        report.append("3. Replace weak cryptographic functions (MD5, SHA-1) with SHA-256+")
        report.append("4. Use parameterized queries to prevent SQL injection")
        report.append("5. Never deserialize untrusted data with pickle or similar")
        report.append("6. Validate and sanitize all user input")
        report.append("7. Use secrets module for cryptographic random numbers")
        report.append("8. Store secrets in environment variables, not in code")
        report.append("")
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generate JSON format report"""
        report = {
            'summary': {
                'total_issues': len(self.issues),
                'by_severity': {
                    'critical': self.stats.get('severity_CRITICAL', 0),
                    'high': self.stats.get('severity_HIGH', 0),
                    'medium': self.stats.get('severity_MEDIUM', 0),
                    'low': self.stats.get('severity_LOW', 0),
                    'info': self.stats.get('severity_INFO', 0)
                },
                'by_category': {
                    category: self.stats.get(category, 0)
                    for category in set(issue.category for issue in self.issues)
                }
            },
            'issues': [issue.to_dict() for issue in self.issues]
        }
        return json.dumps(report, indent=2)
    
    def save_report(self, output_file: str, output_format: str = 'text'):
        """Save report to file"""
        report = self.generate_report(output_format)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        if self.verbose:
            print(f"Security audit report saved to: {output_file}")


def main():
    """Main entry point for security auditor"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Security Auditor for Python 2 to Python 3 Migrations'
    )
    parser.add_argument('path', help='File or directory to audit')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('-f', '--format', choices=['text', 'json'], 
                       default='text', help='Report format')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--exclude', nargs='+', 
                       default=['venv', '__pycache__', '.git', 'node_modules', 'tests'],
                       help='Patterns to exclude from scanning')
    
    args = parser.parse_args()
    
    auditor = SecurityAuditor(verbose=args.verbose)
    
    path = Path(args.path)
    if path.is_file():
        auditor.audit_file(str(path))
    elif path.is_dir():
        auditor.audit_directory(str(path), exclude_patterns=args.exclude)
    else:
        print(f"Error: {args.path} is not a valid file or directory")
        return 1
    
    # Generate and display report
    report = auditor.generate_report(args.format)
    print(report)
    
    # Save to file if requested
    if args.output:
        auditor.save_report(args.output, args.format)
    
    # Return error code based on critical/high issues
    critical_high = (auditor.stats.get('severity_CRITICAL', 0) + 
                     auditor.stats.get('severity_HIGH', 0))
    return 1 if critical_high > 0 else 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
