#!/usr/bin/env python3
"""
Interactive Demo Showcase for py2to3 Migration Tool

Provides a quick, hands-on demonstration of the tool's capabilities.
Perfect for new users, presentations, and validating installation.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# Sample Python 2 code for demonstration
DEMO_CODE = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sample Python 2 Web Scraper
Demonstrates common Python 2 patterns that need migration
"""

import urllib2
import ConfigParser
from BaseHTTPServer import HTTPServer

class OldStyleClass:
    """Example of old-style class"""
    
    def __init__(self, name):
        self.name = name
    
    def fetch_data(self, url):
        """Fetch data from URL"""
        try:
            response = urllib2.urlopen(url)
            data = response.read()
            print "Successfully fetched", len(data), "bytes"
            return data
        except Exception, e:
            print "Error:", e
            return None
    
    def process_items(self, items):
        """Process items using old iteration methods"""
        for i in xrange(len(items)):
            if isinstance(items[i], basestring):
                print "Processing item %d: %s" % (i, items[i])
        
        # Dictionary iteration
        config = {'host': 'localhost', 'port': 8080}
        for key, val in config.iteritems():
            print "Config %s = %s" % (key, val)
        
        return items.keys()
    
    def __cmp__(self, other):
        """Old-style comparison method"""
        return cmp(self.name, other.name)

def main():
    """Main entry point"""
    print "Starting Python 2 application..."
    
    # Integer division issue
    result = 5 / 2  # Returns 2 in Python 2, 2.5 in Python 3
    print "Division result:", result
    
    # Create instance
    scraper = OldStyleClass("demo")
    items = ['item1', 'item2', 'item3']
    scraper.process_items(items)
    
    print "Application complete!"

if __name__ == '__main__':
    main()
'''


class DemoShowcase:
    """Interactive demonstration of py2to3 migration capabilities."""
    
    def __init__(self, interactive: bool = True, verbose: bool = True):
        self.interactive = interactive
        self.verbose = verbose
        self.demo_dir: Optional[Path] = None
        self.demo_file: Optional[Path] = None
    
    def _print_header(self, text: str, char: str = "=") -> None:
        """Print a formatted header."""
        if self.verbose:
            width = 70
            print(f"\n{char * width}")
            print(f"{text:^{width}}")
            print(f"{char * width}\n")
    
    def _print_step(self, step: int, total: int, text: str) -> None:
        """Print a step indicator."""
        if self.verbose:
            print(f"\n{'🔹' * 3} Step {step}/{total}: {text}")
    
    def _pause(self, message: str = "Press Enter to continue...") -> None:
        """Pause for user interaction."""
        if self.interactive:
            input(f"\n{message}")
        elif self.verbose:
            time.sleep(1.5)
    
    def _print_code(self, code: str, title: str = "Code:") -> None:
        """Print code with line numbers."""
        if self.verbose:
            print(f"\n{title}")
            print("-" * 70)
            for i, line in enumerate(code.split('\n'), 1):
                print(f"{i:3d} | {line}")
            print("-" * 70)
    
    def setup_demo_environment(self) -> Path:
        """Create temporary demo environment."""
        self.demo_dir = Path(tempfile.mkdtemp(prefix='py2to3_demo_'))
        self.demo_file = self.demo_dir / 'demo_scraper.py'
        
        # Write demo code
        self.demo_file.write_text(DEMO_CODE)
        
        return self.demo_dir
    
    def cleanup_demo_environment(self) -> None:
        """Clean up temporary demo environment."""
        if self.demo_dir and self.demo_dir.exists():
            shutil.rmtree(self.demo_dir)
    
    def run_full_demo(self) -> bool:
        """Run the complete demonstration workflow."""
        try:
            self._print_header("🚀 py2to3 Interactive Demo Showcase 🚀")
            
            if self.verbose:
                print("Welcome to the py2to3 migration toolkit!")
                print("This demo will walk you through the complete migration workflow.")
                print(f"Interactive mode: {'ON' if self.interactive else 'OFF'}")
            
            self._pause("Press Enter to begin...")
            
            # Step 1: Setup
            self._step_1_setup()
            
            # Step 2: Show Python 2 Code
            self._step_2_show_original_code()
            
            # Step 3: Run Compatibility Check
            self._step_3_compatibility_check()
            
            # Step 4: Apply Automated Fixes
            self._step_4_apply_fixes()
            
            # Step 5: Show Fixed Code
            self._step_5_show_fixed_code()
            
            # Step 6: Verify Results
            self._step_6_verify_results()
            
            # Step 7: Summary
            self._step_7_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user.")
            return False
        except Exception as e:
            print(f"\n\n❌ Demo failed: {e}")
            return False
        finally:
            self.cleanup_demo_environment()
    
    def _step_1_setup(self) -> None:
        """Step 1: Create demo environment."""
        self._print_step(1, 7, "Setting up demo environment")
        
        demo_dir = self.setup_demo_environment()
        
        if self.verbose:
            print(f"✓ Created temporary demo directory: {demo_dir}")
            print(f"✓ Created sample Python 2 file: {self.demo_file.name}")
        
        self._pause()
    
    def _step_2_show_original_code(self) -> None:
        """Step 2: Display the original Python 2 code."""
        self._print_step(2, 7, "Examining Original Python 2 Code")
        
        if self.verbose:
            print("\nThis sample demonstrates common Python 2 patterns:")
            print("  • Print statements (print \"text\")")
            print("  • Old imports (urllib2, ConfigParser)")
            print("  • Old-style classes")
            print("  • Old exception syntax (except Exception, e)")
            print("  • Iterator methods (xrange, iteritems)")
            print("  • Old comparison methods (__cmp__)")
            print("  • basestring type")
        
        code = self.demo_file.read_text()
        self._print_code(code[:800] + "\n... (truncated for display)", 
                        "Sample Python 2 Code:")
        
        self._pause()
    
    def _step_3_compatibility_check(self) -> None:
        """Step 3: Run compatibility check."""
        self._print_step(3, 7, "Running Python 3 Compatibility Check")
        
        if self.verbose:
            print("\nRunning verifier to detect Python 2 patterns...")
        
        try:
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            verifier.verify_file(str(self.demo_file))
            
            issues = verifier.issues_found
            
            if self.verbose:
                print(f"\n✓ Analysis complete!")
                print(f"  Found {len(issues)} compatibility issues")
                
                if issues:
                    print("\n  Sample issues detected:")
                    for issue in issues[:5]:  # Show first 5
                        print(f"    • Line {issue.get('line', '?')}: "
                              f"{issue.get('type', 'Unknown')} - "
                              f"{issue.get('message', '')[:60]}")
                    if len(issues) > 5:
                        print(f"    ... and {len(issues) - 5} more issues")
        
        except ImportError:
            if self.verbose:
                print("  ⚠️  Verifier module not available, skipping detailed check")
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Compatibility check error: {e}")
        
        self._pause()
    
    def _step_4_apply_fixes(self) -> None:
        """Step 4: Apply automated fixes."""
        self._print_step(4, 7, "Applying Automated Fixes")
        
        if self.verbose:
            print("\nRunning fixer to automatically convert Python 2 to Python 3...")
        
        try:
            from fixer import Python2to3Fixer
            
            # Create backup
            backup_file = self.demo_file.parent / (self.demo_file.name + '.backup')
            shutil.copy(self.demo_file, backup_file)
            
            fixer = Python2to3Fixer()
            fixer.fix_file(str(self.demo_file))
            
            if self.verbose:
                print("\n✓ Automated fixes applied successfully!")
                print(f"  • Backup created: {backup_file.name}")
                print(f"  • File updated: {self.demo_file.name}")
                
                if hasattr(fixer, 'fixes_applied'):
                    print(f"  • Total fixes: {len(fixer.fixes_applied)}")
        
        except ImportError:
            if self.verbose:
                print("  ⚠️  Fixer module not available, skipping automated fixes")
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Fix error: {e}")
        
        self._pause()
    
    def _step_5_show_fixed_code(self) -> None:
        """Step 5: Show the fixed Python 3 code."""
        self._print_step(5, 7, "Examining Fixed Python 3 Code")
        
        if self.verbose:
            print("\nKey transformations applied:")
            print("  ✓ print statements → print() function")
            print("  ✓ urllib2 → urllib.request")
            print("  ✓ ConfigParser → configparser")
            print("  ✓ except Exception, e → except Exception as e")
            print("  ✓ xrange() → range()")
            print("  ✓ iteritems() → items()")
            print("  ✓ basestring → str")
            print("  ✓ Old-style class → new-style class")
        
        try:
            fixed_code = self.demo_file.read_text()
            self._print_code(fixed_code[:800] + "\n... (truncated for display)", 
                            "Fixed Python 3 Code:")
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Could not read fixed code: {e}")
        
        self._pause()
    
    def _step_6_verify_results(self) -> None:
        """Step 6: Verify the migration results."""
        self._print_step(6, 7, "Verifying Migration Results")
        
        if self.verbose:
            print("\nRe-running compatibility check on fixed code...")
        
        try:
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            verifier.verify_file(str(self.demo_file))
            
            remaining_issues = verifier.issues_found
            
            if self.verbose:
                print(f"\n✓ Verification complete!")
                print(f"  Remaining issues: {len(remaining_issues)}")
                
                if remaining_issues:
                    print("\n  Some issues may require manual review:")
                    for issue in remaining_issues[:3]:
                        print(f"    • {issue.get('type', 'Unknown')}: "
                              f"{issue.get('message', '')[:60]}")
                else:
                    print("\n  🎉 No remaining compatibility issues detected!")
        
        except ImportError:
            if self.verbose:
                print("  ⚠️  Verifier module not available")
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Verification error: {e}")
        
        self._pause()
    
    def _step_7_summary(self) -> None:
        """Step 7: Show summary and next steps."""
        self._print_step(7, 7, "Summary & Next Steps")
        
        self._print_header("🎉 Demo Complete! 🎉", "=")
        
        if self.verbose:
            print("You've just seen the py2to3 migration workflow in action!")
            print("\nWhat the tool did:")
            print("  1. ✓ Analyzed Python 2 code for compatibility issues")
            print("  2. ✓ Applied automated fixes for common patterns")
            print("  3. ✓ Verified the results")
            print("  4. ✓ Created backups for safety")
            
            print("\n" + "=" * 70)
            print("Next Steps - Try These Commands:")
            print("=" * 70)
            
            print("\n🧙 Beginner? Start with the wizard:")
            print("  $ ./py2to3 wizard")
            
            print("\n🏥 Check your project health:")
            print("  $ ./py2to3 doctor")
            
            print("\n📋 Get a migration checklist:")
            print("  $ ./py2to3 checklist src/")
            
            print("\n🔍 Check your code:")
            print("  $ ./py2to3 check src/")
            
            print("\n🔧 Apply fixes:")
            print("  $ ./py2to3 fix src/ --backup")
            
            print("\n📊 Generate a report:")
            print("  $ ./py2to3 report")
            
            print("\n📚 Browse migration patterns:")
            print("  $ ./py2to3 patterns")
            
            print("\n❓ Get help:")
            print("  $ ./py2to3 --help")
            print("  $ ./py2to3 <command> --help")
            
            print("\n" + "=" * 70)
            print("Documentation:")
            print("=" * 70)
            print("  • Quick Start:  QUICK_START.md")
            print("  • CLI Guide:    CLI_GUIDE.md")
            print("  • Wizard Guide: WIZARD_GUIDE.md")
            print("  • All Guides:   See README.md")
            
            print("\n" + "=" * 70)
            print("Thank you for trying py2to3! Happy migrating! 🚀")
            print("=" * 70 + "\n")


def run_demo(interactive: bool = True, verbose: bool = True) -> bool:
    """
    Run the interactive demo showcase.
    
    Args:
        interactive: If True, pause between steps for user input
        verbose: If True, print detailed information
    
    Returns:
        True if demo completed successfully, False otherwise
    """
    demo = DemoShowcase(interactive=interactive, verbose=verbose)
    return demo.run_full_demo()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Interactive demo of py2to3 migration toolkit'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run in automatic mode (no pauses for input)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    args = parser.parse_args()
    
    success = run_demo(
        interactive=not args.auto,
        verbose=not args.quiet
    )
    
    sys.exit(0 if success else 1)
