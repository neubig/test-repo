#!/usr/bin/env python
"""
Python 2 to Python 3 Verifier
A programmatic tool to verify Python 3 compatibility and detect remaining Python 2 patterns.
"""

import ast
import datetime
import os
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict


class Python3CompatibilityVerifier:
    """Main class for verifying Python 3 compatibility."""

    def __init__(self):
        self.issues_found = []
        self.warnings = []
        self.files_checked = 0
        self.syntax_errors = []

        # Define patterns that indicate Python 2 compatibility issues
        self.issue_patterns = self._get_issue_patterns()

    def _get_issue_patterns(self):
        """Define patterns that indicate Python 2/3 compatibility issues."""
        return OrderedDict(
            [
                # Print statements (should be functions)
                (
                    "print_statements",
                    {
                        "pattern": r"\bprint\s+[^(]",
                        "severity": "error",
                        "description": "Print statement found (should be print() function)",
                        "suggestion": "Use print() function instead of print statement",
                    },
                ),
                # Old import patterns
                (
                    "urllib2_import",
                    {
                        "pattern": r"import urllib2",
                        "severity": "error",
                        "description": "urllib2 import found",
                        "suggestion": "Use urllib.request instead",
                    },
                ),
                (
                    "urlparse_import",
                    {
                        "pattern": r"from urlparse import",
                        "severity": "error",
                        "description": "urlparse import found",
                        "suggestion": "Use urllib.parse instead",
                    },
                ),
                (
                    "configparser_import",
                    {
                        "pattern": r"\bimport ConfigParser\b",
                        "severity": "error",
                        "description": "ConfigParser import found",
                        "suggestion": "Use configparser instead",
                    },
                ),
                (
                    "cpickle_import",
                    {
                        "pattern": r"\bimport cPickle\b",
                        "severity": "error",
                        "description": "cPickle import found",
                        "suggestion": "Use pickle instead",
                    },
                ),
                (
                    "stringio_import",
                    {
                        "pattern": r"from StringIO import",
                        "severity": "error",
                        "description": "StringIO import found",
                        "suggestion": "Use io.StringIO instead",
                    },
                ),
                (
                    "htmlparser_import",
                    {
                        "pattern": r"\bfrom HTMLParser import\b",
                        "severity": "error",
                        "description": "HTMLParser import found",
                        "suggestion": "Use html.parser instead",
                    },
                ),
                (
                    "queue_import",
                    {
                        "pattern": r"\bfrom Queue import\b",
                        "severity": "error",
                        "description": "Queue import found",
                        "suggestion": "Use queue instead",
                    },
                ),
                (
                    "thread_import",
                    {
                        "pattern": r"\bimport thread\b",
                        "severity": "error",
                        "description": "thread import found",
                        "suggestion": "Use _thread instead",
                    },
                ),
                # String and unicode issues
                (
                    "basestring_usage",
                    {
                        "pattern": r"\bbasestring\b",
                        "severity": "error",
                        "description": "basestring usage found",
                        "suggestion": "Use str instead of basestring",
                    },
                ),
                (
                    "unicode_function",
                    {
                        "pattern": r"\bunicode\(",
                        "severity": "error",
                        "description": "unicode() function found",
                        "suggestion": "Use str() instead of unicode()",
                    },
                ),
                # Iterator issues
                (
                    "xrange_usage",
                    {
                        "pattern": r"\bxrange\(",
                        "severity": "error",
                        "description": "xrange() usage found",
                        "suggestion": "Use range() instead of xrange()",
                    },
                ),
                (
                    "iteritems_usage",
                    {
                        "pattern": r"\.iteritems\(\)",
                        "severity": "error",
                        "description": "iteritems() usage found",
                        "suggestion": "Use items() instead of iteritems()",
                    },
                ),
                (
                    "iterkeys_usage",
                    {
                        "pattern": r"\.iterkeys\(\)",
                        "severity": "error",
                        "description": "iterkeys() usage found",
                        "suggestion": "Use keys() instead of iterkeys()",
                    },
                ),
                (
                    "itervalues_usage",
                    {
                        "pattern": r"\.itervalues\(\)",
                        "severity": "error",
                        "description": "itervalues() usage found",
                        "suggestion": "Use values() instead of itervalues()",
                    },
                ),
                # Exception handling
                (
                    "old_except_syntax",
                    {
                        "pattern": r"except\s+\w+\s*,\s*\w+:",
                        "severity": "error",
                        "description": "Old except syntax found",
                        "suggestion": 'Use "except Exception as e:" syntax',
                    },
                ),
                # Comparison issues
                (
                    "cmp_function",
                    {
                        "pattern": r"\bcmp\(",
                        "severity": "error",
                        "description": "cmp() function usage found",
                        "suggestion": "Use comparison operators or implement custom comparison",
                    },
                ),
                (
                    "cmp_method",
                    {
                        "pattern": r"def __cmp__\(",
                        "severity": "warning",
                        "description": "__cmp__ method found",
                        "suggestion": "Use __lt__, __eq__, etc. methods instead",
                    },
                ),
                # File handling issues
                (
                    "file_builtin",
                    {
                        "pattern": r"\bfile\(",
                        "severity": "error",
                        "description": "file() builtin usage found",
                        "suggestion": "Use open() instead of file()",
                    },
                ),
                # Class definition issues
                (
                    "old_style_class",
                    {
                        "pattern": r"^class\s+\w+\s*:",
                        "severity": "warning",
                        "description": "Old-style class definition found",
                        "suggestion": "Inherit from object for new-style class",
                    },
                ),
                # Division issues
                (
                    "integer_division",
                    {
                        "pattern": r"\b\d+\s*/\s*\d+\b",
                        "severity": "warning",
                        "description": "Potential integer division found",
                        "suggestion": "Use // for integer division or ensure float division",
                    },
                ),
                # Note: Encoding check is handled separately in _check_encoding method
            ]
        )

    def verify_file(self, filepath):
        """Verify a single Python file for Python 3 compatibility."""
        print("Verifying file: %s" % filepath)
        self.files_checked += 1

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, encoding="latin-1") as f:
                    content = f.read()
                self.warnings.append(
                    {
                        "file": filepath,
                        "line": 1,
                        "issue": "encoding_issue",
                        "description": "File encoding issue detected",
                        "suggestion": "Ensure file is saved with UTF-8 encoding",
                    }
                )
            except Exception as e:
                self.issues_found.append(
                    {
                        "file": filepath,
                        "line": 1,
                        "issue": "read_error",
                        "severity": "error",
                        "description": "Cannot read file: %s" % str(e),
                        "suggestion": "Check file encoding and permissions",
                    }
                )
                return False

        # Check for Python 2/3 compatibility issues first
        self._check_patterns(filepath, content)

        # Check syntax (but don't stop if invalid - Python 2 code may not parse in Python 3)
        syntax_valid, syntax_error = self._check_syntax(filepath, content)
        if not syntax_valid:
            self.syntax_errors.append({"file": filepath, "error": syntax_error})
            # Don't return False here - continue with other checks

        # Additional checks (only if syntax is valid for AST parsing)
        if syntax_valid:
            self._check_imports(filepath, content)
        self._check_encoding(filepath, content)

        return True

    def _check_syntax(self, filepath, content):
        """Check if the file has valid Python 3 syntax."""
        try:
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno or 'unknown'}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def _check_patterns(self, filepath, content):
        """Check content against known issue patterns."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for issue_name, issue_info in self.issue_patterns.items():
                if re.search(issue_info["pattern"], line):
                    self.issues_found.append(
                        {
                            "file": filepath,
                            "line": line_num,
                            "issue": issue_name,
                            "severity": issue_info["severity"],
                            "description": issue_info["description"],
                            "suggestion": issue_info["suggestion"],
                            "code": line.strip(),
                        }
                    )

    def _check_imports(self, filepath, content):
        """Check for problematic imports."""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._check_import_name(filepath, node.lineno, alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._check_import_name(filepath, node.lineno, node.module)

        except Exception:
            pass  # Syntax errors already caught

    def _check_import_name(self, filepath, line_num, import_name):
        """Check if an import name is problematic."""
        problematic_imports = {
            "urllib2": "Use urllib.request instead",
            "urlparse": "Use urllib.parse instead",
            "ConfigParser": "Use configparser instead",
            "cPickle": "Use pickle instead",
            "StringIO": "Use io instead",
            "HTMLParser": "Use html.parser instead",
            "Queue": "Use queue instead",
            "thread": "Use _thread instead",
            "commands": "Use subprocess instead",
            "md5": "Use hashlib instead",
            "sha": "Use hashlib instead",
        }

        if import_name in problematic_imports:
            self.issues_found.append(
                {
                    "file": filepath,
                    "line": line_num,
                    "issue": "problematic_import",
                    "severity": "error",
                    "description": "Problematic import: %s" % import_name,
                    "suggestion": problematic_imports[import_name],
                    "code": import_name,
                }
            )

    def _check_encoding(self, filepath, content):
        """Check for encoding declaration."""
        lines = content.split("\n")
        has_encoding = False

        # Check first two lines for encoding declaration
        for i in range(min(2, len(lines))):
            if "coding" in lines[i] or "encoding" in lines[i]:
                has_encoding = True
                break

        if not has_encoding and any(ord(c) > 127 for c in content):
            self.warnings.append(
                {
                    "file": filepath,
                    "line": 1,
                    "issue": "missing_encoding",
                    "description": "File contains non-ASCII characters but no encoding declaration",
                    "suggestion": "Add # -*- coding: utf-8 -*- at the top of the file",
                }
            )

    def verify_directory(self, directory, recursive=True):
        """Verify all Python files in a directory."""
        print("Verifying directory: %s" % directory)

        python_files = []

        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        python_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if file.endswith(".py"):
                    python_files.append(os.path.join(directory, file))

        print("Found %d Python files to verify" % len(python_files))

        success_count = 0
        for filepath in python_files:
            if self.verify_file(filepath):
                success_count += 1

        print("Successfully verified %d out of %d files" % (success_count, len(python_files)))
        return success_count == len(python_files)

    def run_2to3_tool(self, target_path):
        """Run the official 2to3 tool and capture output."""
        try:
            result = subprocess.run(
                ["2to3", "--print-function", "--no-diff", target_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, "2to3 tool timed out"
        except FileNotFoundError:
            return False, "2to3 tool not found (install python3-tools)"
        except Exception as e:
            return False, "Error running 2to3: %s" % str(e)

    def generate_report(self):
        """Generate a comprehensive verification report."""
        report = []
        report.append("Python 3 Compatibility Verification Report")
        report.append("=" * 50)
        report.append("Generated: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report.append("Files checked: %d" % self.files_checked)
        report.append("")

        # Summary
        error_count = len([i for i in self.issues_found if i["severity"] == "error"])
        warning_count = len([i for i in self.issues_found if i["severity"] == "warning"])

        report.append("Summary:")
        report.append("  Errors: %d" % error_count)
        report.append("  Warnings: %d" % warning_count)
        report.append("  Syntax errors: %d" % len(self.syntax_errors))
        report.append("")

        # Syntax errors
        if self.syntax_errors:
            report.append("Syntax Errors:")
            report.append("-" * 20)
            for error in self.syntax_errors:
                report.append(f"  {error['file']}: {error['error']}")
            report.append("")

        # Issues by severity
        if self.issues_found:
            # Group by severity
            errors = [i for i in self.issues_found if i["severity"] == "error"]
            warnings = [i for i in self.issues_found if i["severity"] == "warning"]

            if errors:
                report.append("Errors (must fix for Python 3):")
                report.append("-" * 35)
                self._add_issues_to_report(report, errors)
                report.append("")

            if warnings:
                report.append("Warnings (recommended fixes):")
                report.append("-" * 30)
                self._add_issues_to_report(report, warnings)
                report.append("")

        # Issue statistics
        if self.issues_found:
            report.append("Issue Statistics:")
            report.append("-" * 20)
            issue_counts: dict[str, int] = defaultdict(int)
            for issue in self.issues_found:
                issue_counts[issue["issue"]] += 1

            for issue_type, count in sorted(issue_counts.items()):
                report.append("  %s: %d" % (issue_type, count))
            report.append("")

        # Recommendations
        report.append("Recommendations:")
        report.append("-" * 15)
        if error_count == 0 and warning_count == 0:
            report.append("  ✓ Code appears to be Python 3 compatible!")
        else:
            if error_count > 0:
                report.append("  • Fix all errors before running with Python 3")
            if warning_count > 0:
                report.append("  • Review warnings for potential issues")
            report.append("  • Test thoroughly with Python 3")
            report.append("  • Consider using automated tools like 2to3")

        return "\n".join(report)

    def _add_issues_to_report(self, report, issues):
        """Add issues to the report."""
        # Group by file
        files_with_issues = defaultdict(list)
        for issue in issues:
            files_with_issues[issue["file"]].append(issue)

        for filepath, file_issues in files_with_issues.items():
            report.append("  File: %s" % filepath)
            for issue in file_issues:
                report.append("    Line %d: %s" % (issue["line"], issue["description"]))
                if "code" in issue and issue["code"]:
                    report.append("      Code: %s" % issue["code"])
                report.append("      Fix: %s" % issue["suggestion"])
                report.append("")

    def save_report(self, filename="verification_report.txt"):
        """Save the verification report to a file."""
        report = self.generate_report()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            print("Report saved to: %s" % filename)
            return True
        except Exception as e:
            print("Error saving report: %s" % str(e))
            return False

    def is_python3_compatible(self):
        """Check if the verified code is Python 3 compatible."""
        error_count = len([i for i in self.issues_found if i["severity"] == "error"])
        return error_count == 0 and len(self.syntax_errors) == 0


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python verifier.py <file_or_directory> [options]")
        print("Options:")
        print("  --no-recursive      Don't process directories recursively")
        print("  --report FILE       Save report to specified file")
        print("  --use-2to3          Also run official 2to3 tool")
        sys.exit(1)

    target = sys.argv[1]
    recursive = True
    report_file = None
    use_2to3 = False

    # Parse options
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--no-recursive":
            recursive = False
            i += 1
        elif sys.argv[i] == "--report" and i + 1 < len(sys.argv):
            report_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--use-2to3":
            use_2to3 = True
            i += 1
        else:
            print("Unknown option: %s" % sys.argv[i])
            sys.exit(1)

    # Create verifier
    verifier = Python3CompatibilityVerifier()

    # Process target
    if os.path.isfile(target):
        verifier.verify_file(target)
    elif os.path.isdir(target):
        verifier.verify_directory(target, recursive=recursive)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)

    # Run 2to3 tool if requested
    if use_2to3:
        print("\nRunning official 2to3 tool...")
        tool_success, tool_output = verifier.run_2to3_tool(target)
        if tool_success:
            print("2to3 tool completed successfully")
            if tool_output.strip():
                print("2to3 output:")
                print(tool_output)
        else:
            print("2to3 tool failed: %s" % tool_output)

    # Generate and display report
    print("\n" + verifier.generate_report())

    # Save report if requested
    if report_file:
        verifier.save_report(report_file)

    # Check compatibility
    if verifier.is_python3_compatible():
        print("\n✓ Code appears to be Python 3 compatible!")
        exit_code = 0
    else:
        print("\n✗ Code has Python 3 compatibility issues that need to be fixed.")
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
