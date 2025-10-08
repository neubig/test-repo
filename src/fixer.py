#!/usr/bin/env python
"""
Python 2 to Python 3 Fixer
A programmatic tool to automatically fix Python 2 code for Python 3 compatibility.
"""

import ast
import datetime
import os
import re
import shutil
import sys
from collections import OrderedDict


class Python2to3Fixer:
    """Main class for fixing Python 2 code to be Python 3 compatible."""

    def __init__(self, backup_dir="backup"):
        self.backup_dir = backup_dir
        self.fixes_applied = []
        self.errors = []

        # Ensure backup directory exists
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Define fix patterns
        self.fix_patterns = self._get_fix_patterns()

    def _get_fix_patterns(self):
        """Define patterns for common Python 2 to 3 fixes."""
        return OrderedDict(
            [
                # Print statements to print functions
                (
                    "print_statements",
                    {
                        "pattern": r"\bprint\s+([^(].*?)(?=\n|$)",
                        "replacement": r"print(\1)",
                        "description": "Convert print statements to print() functions",
                    },
                ),
                # Import fixes
                (
                    "urllib2_imports",
                    {
                        "pattern": r"import urllib2",
                        "replacement": "import urllib.request as urllib2",
                        "description": "Fix urllib2 imports",
                    },
                ),
                (
                    "urlparse_imports",
                    {
                        "pattern": r"from urlparse import",
                        "replacement": "from urllib.parse import",
                        "description": "Fix urlparse imports",
                    },
                ),
                (
                    "configparser_imports",
                    {
                        "pattern": r"from ConfigParser import",
                        "replacement": "from configparser import",
                        "description": "Fix ConfigParser imports",
                    },
                ),
                (
                    "configparser_direct",
                    {
                        "pattern": r"import ConfigParser",
                        "replacement": "import configparser as ConfigParser",
                        "description": "Fix ConfigParser direct imports",
                    },
                ),
                (
                    "pickle_imports",
                    {
                        "pattern": r"import cPickle as pickle",
                        "replacement": "import pickle",
                        "description": "Fix cPickle imports",
                    },
                ),
                (
                    "stringio_imports",
                    {
                        "pattern": r"from StringIO import StringIO",
                        "replacement": "from io import StringIO",
                        "description": "Fix StringIO imports",
                    },
                ),
                (
                    "htmlparser_imports",
                    {
                        "pattern": r"from HTMLParser import HTMLParser",
                        "replacement": "from html.parser import HTMLParser",
                        "description": "Fix HTMLParser imports",
                    },
                ),
                (
                    "queue_imports",
                    {
                        "pattern": r"from Queue import",
                        "replacement": "from queue import",
                        "description": "Fix Queue imports",
                    },
                ),
                (
                    "thread_imports",
                    {
                        "pattern": r"import thread",
                        "replacement": "import _thread as thread",
                        "description": "Fix thread imports",
                    },
                ),
                # String and unicode fixes
                (
                    "basestring_checks",
                    {
                        "pattern": r"\bisinstance\(([^,]+),\s*basestring\)",
                        "replacement": r"isinstance(\1, str)",
                        "description": "Replace basestring with str",
                    },
                ),
                (
                    "unicode_literals",
                    {
                        "pattern": r"\bunicode\(",
                        "replacement": "str(",
                        "description": "Replace unicode() with str()",
                    },
                ),
                # Iterator fixes
                (
                    "xrange_calls",
                    {
                        "pattern": r"\bxrange\(",
                        "replacement": "range(",
                        "description": "Replace xrange with range",
                    },
                ),
                (
                    "iteritems_calls",
                    {
                        "pattern": r"\.iteritems\(\)",
                        "replacement": ".items()",
                        "description": "Replace iteritems() with items()",
                    },
                ),
                (
                    "iterkeys_calls",
                    {
                        "pattern": r"\.iterkeys\(\)",
                        "replacement": ".keys()",
                        "description": "Replace iterkeys() with keys()",
                    },
                ),
                (
                    "itervalues_calls",
                    {
                        "pattern": r"\.itervalues\(\)",
                        "replacement": ".values()",
                        "description": "Replace itervalues() with values()",
                    },
                ),
                # Exception handling
                (
                    "except_syntax",
                    {
                        "pattern": r"except\s+(\w+),\s*(\w+):",
                        "replacement": r"except \1 as \2:",
                        "description": "Fix except syntax",
                    },
                ),
                # Comparison fixes
                (
                    "cmp_function",
                    {
                        "pattern": r"\bcmp\(",
                        "replacement": "(lambda a, b: (a > b) - (a < b))(",
                        "description": "Replace cmp() function",
                    },
                ),
                # File handling
                (
                    "file_open_mode",
                    {
                        "pattern": r"open\(([^,]+),\s*['\"]rb?['\"]",
                        "replacement": r"open(\1, 'r', encoding='utf-8'",
                        "description": "Fix file open modes for text files",
                    },
                ),
                # Class definitions
                (
                    "old_style_classes",
                    {
                        "pattern": r"^class\s+(\w+):",
                        "replacement": r"class \1(object):",
                        "description": "Convert old-style classes to new-style",
                    },
                ),
            ]
        )

    def fix_file(self, filepath, dry_run=False):
        """Fix a single Python file.
        
        Args:
            filepath: Path to the file to fix
            dry_run: If True, only analyze without modifying files
            
        Returns:
            Dictionary with 'fixes', 'errors', and 'success' keys
        """
        if dry_run:
            print("Analyzing file (dry run): %s" % filepath)
        else:
            print("Fixing file: %s" % filepath)

        backup_path = None
        # Create backup only if not in dry-run mode
        if not dry_run:
            backup_path = self._create_backup(filepath)
            if not backup_path:
                error_msg = "Failed to create backup for %s" % filepath
                self.errors.append(error_msg)
                return {
                    'fixes': self.fixes_applied,
                    'errors': self.errors,
                    'success': False
                }

        try:
            # Read file content
            with open(filepath) as f:
                content = f.read()

            original_content = content
            file_fixes = []

            # Apply fixes
            for fix_name, fix_info in self.fix_patterns.items():
                content, count = self._apply_fix(content, fix_info)
                if count > 0:
                    fix_entry = {
                        "file": filepath,
                        "fix": fix_name,
                        "type": fix_name,
                        "description": fix_info["description"],
                        "count": count,
                    }
                    self.fixes_applied.append(fix_entry)
                    file_fixes.append(fix_entry)

            # Add Python 3 compatibility imports at the top if needed
            content = self._add_compatibility_imports(content)

            # Write fixed content back to file (only if not dry run)
            if content != original_content:
                if dry_run:
                    print(
                        "  Would apply %d types of fixes (DRY RUN)"
                        % len(file_fixes)
                    )
                    # In dry run, show what changes would be made
                    for fix in file_fixes:
                        print(f"    - {fix['description']} ({fix['count']} occurrence(s))")
                else:
                    with open(filepath, "w") as f:
                        f.write(content)
                    print(
                        "  Applied %d types of fixes"
                        % len(file_fixes)
                    )
            else:
                if dry_run:
                    print("  No fixes needed")
                else:
                    print("  No fixes needed")

            return {
                'fixes': self.fixes_applied,
                'errors': self.errors,
                'success': True
            }

        except Exception as e:
            error_msg = f"Error fixing {filepath}: {str(e)}"
            self.errors.append(error_msg)
            # Restore from backup (only if we created one)
            if not dry_run and backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, filepath)
            return {
                'fixes': self.fixes_applied,
                'errors': self.errors,
                'success': False
            }

    def _create_backup(self, filepath):
        """Create a backup of the file."""
        try:
            filename = os.path.basename(filepath)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{filename}.{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            shutil.copy2(filepath, backup_path)
            return backup_path

        except Exception as e:
            print(f"Warning: Failed to create backup for {filepath}: {str(e)}")
            return None

    def _apply_fix(self, content, fix_info):
        """Apply a single fix to content."""
        pattern = fix_info["pattern"]
        replacement = fix_info["replacement"]

        # Use multiline flag for patterns that might span lines
        flags = re.MULTILINE
        if "flags" in fix_info:
            flags |= fix_info["flags"]

        new_content, count = re.subn(pattern, replacement, content, flags=flags)
        return new_content, count

    def _add_compatibility_imports(self, content):
        """Add Python 3 compatibility imports if needed."""
        imports_to_add = []

        # Check if we need future imports
        if "print(" in content and "from __future__ import print_function" not in content:
            imports_to_add.append("from __future__ import print_function")

        if (
            "unicode_literals" in content
            and "from __future__ import unicode_literals" not in content
        ):
            imports_to_add.append("from __future__ import unicode_literals")

        if imports_to_add:
            # Find the position to insert imports (after encoding declaration)
            lines = content.split("\n")
            insert_pos = 0

            # Skip shebang and encoding lines
            for i, line in enumerate(lines):
                if line.startswith("#!") or "coding:" in line or "coding=" in line:
                    insert_pos = i + 1
                elif line.strip() == "":
                    continue
                else:
                    break

            # Insert imports
            for import_line in reversed(imports_to_add):
                lines.insert(insert_pos, import_line)

            content = "\n".join(lines)

        return content

    def fix_directory(self, directory, recursive=True, dry_run=False):
        """Fix all Python files in a directory.
        
        Args:
            directory: Path to the directory to fix
            recursive: If True, process subdirectories recursively
            dry_run: If True, only analyze without modifying files
            
        Returns:
            Dictionary with 'fixes' and 'errors' lists
        """
        if dry_run:
            print("Analyzing directory (dry run): %s" % directory)
        else:
            print("Fixing directory: %s" % directory)

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

        print("Found %d Python files to %s" % (len(python_files), "analyze" if dry_run else "fix"))

        success_count = 0
        for filepath in python_files:
            result = self.fix_file(filepath, dry_run=dry_run)
            if result.get('success', False):
                success_count += 1

        if dry_run:
            print("Successfully analyzed %d out of %d files" % (success_count, len(python_files)))
        else:
            print("Successfully fixed %d out of %d files" % (success_count, len(python_files)))
        
        # Return results in expected format for CLI
        return {
            'fixes': self.fixes_applied,
            'errors': self.errors,
            'success': success_count == len(python_files)
        }

    def validate_syntax(self, filepath):
        """Validate Python syntax of a file."""
        try:
            with open(filepath) as f:
                content = f.read()

            # Try to parse with ast
            ast.parse(content)
            return True, None

        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, "Error reading file: %s" % str(e)

    def generate_report(self):
        """Generate a report of all fixes applied."""
        report = []
        report.append("Python 2 to 3 Conversion Report")
        report.append("=" * 40)
        report.append("Generated: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report.append("")

        if self.fixes_applied:
            report.append("Fixes Applied:")
            report.append("-" * 20)

            # Group fixes by file
            files_fixed: dict[str, list[dict[str, str]]] = {}
            for fix in self.fixes_applied:
                filepath = fix["file"]
                if filepath not in files_fixed:
                    files_fixed[filepath] = []
                files_fixed[filepath].append(fix)

            for filepath, fixes in files_fixed.items():
                report.append("\nFile: %s" % filepath)
                for fix in fixes:
                    report.append("  - %s (%d occurrences)" % (fix["description"], fix["count"]))

            # Summary
            report.append("\nSummary:")
            report.append("Files modified: %d" % len(files_fixed))
            report.append("Total fixes applied: %d" % len(self.fixes_applied))

        else:
            report.append("No fixes were needed or applied.")

        if self.errors:
            report.append("\nErrors:")
            report.append("-" * 10)
            for error in self.errors:
                report.append("  - %s" % error)

        return "\n".join(report)

    def save_report(self, filename="conversion_report.txt"):
        """Save the conversion report to a file."""
        report = self.generate_report()
        try:
            with open(filename, "w") as f:
                f.write(report)
            print("Report saved to: %s" % filename)
            return True
        except Exception as e:
            print("Error saving report: %s" % str(e))
            return False


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python fixer.py <input_file> [output_file] [options]")
        print("       python fixer.py <directory> [options]")
        print("Options:")
        print("  --backup-dir DIR    Specify backup directory (default: backup)")
        print("  --no-recursive      Don't process directories recursively")
        print("  --report FILE       Save report to specified file")
        print("")
        print("If output_file is provided, input_file will be copied to output_file and fixed.")
        print("Otherwise, input_file will be modified in-place.")
        sys.exit(1)

    target = sys.argv[1]
    output_file = None

    # Check if second argument is an output file (not an option)
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("--"):
        output_file = sys.argv[2]
        start_options = 3
    else:
        start_options = 2
    backup_dir = "backup"
    recursive = True
    report_file = None

    # Parse options
    i = start_options
    while i < len(sys.argv):
        if sys.argv[i] == "--backup-dir" and i + 1 < len(sys.argv):
            backup_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--no-recursive":
            recursive = False
            i += 1
        elif sys.argv[i] == "--report" and i + 1 < len(sys.argv):
            report_file = sys.argv[i + 1]
            i += 2
        else:
            print("Unknown option: %s" % sys.argv[i])
            sys.exit(1)

    # Create fixer
    fixer = Python2to3Fixer(backup_dir=backup_dir)

    # Process target
    if os.path.isfile(target):
        if output_file:
            # Copy input to output and fix the output file
            import shutil

            try:
                shutil.copy2(target, output_file)
                success = fixer.fix_file(output_file)
            except Exception as e:
                print("Error copying file: %s" % e)
                sys.exit(1)
        else:
            # Fix in-place
            success = fixer.fix_file(target)
    elif os.path.isdir(target):
        if output_file:
            print("Error: Output file cannot be specified when processing a directory")
            sys.exit(1)
        success = fixer.fix_directory(target, recursive=recursive)
    else:
        print("Error: %s is not a valid file or directory" % target)
        sys.exit(1)

    # Generate and display report
    print("\n" + fixer.generate_report())

    # Save report if requested
    if report_file:
        fixer.save_report(report_file)

    # Exit with appropriate code
    sys.exit(0 if success and not fixer.errors else 1)


if __name__ == "__main__":
    main()
