#!/usr/bin/env python
"""
Migration Simulator
Preview complete migration outcomes without making changes.
Perfect for planning, demos, and stakeholder presentations.
"""

import os
import re
import sys
import json
from datetime import datetime
from collections import defaultdict, OrderedDict
from io import StringIO
from contextlib import redirect_stdout

from fixer import Python2to3Fixer
from verifier import Python3CompatibilityVerifier


class MigrationSimulator:
    """Simulate complete migration to preview outcomes without changes."""

    def __init__(self, target_path="."):
        self.target_path = target_path
        self.simulation_results = {
            "timestamp": datetime.now().isoformat(),
            "target_path": target_path,
            "files_analyzed": [],
            "total_changes": 0,
            "changes_by_type": defaultdict(int),
            "changes_by_file": defaultdict(list),
            "issues_before": [],
            "issues_after": [],
            "file_previews": {},
            "summary": {}
        }
        
    def simulate(self, verbose=False):
        """
        Simulate the complete migration process.
        
        Args:
            verbose: Show detailed progress
            
        Returns:
            Dictionary with simulation results
        """
        print("🔮 Starting Migration Simulation...")
        print(f"📁 Target: {self.target_path}")
        print("=" * 60)
        
        # Find all Python files
        python_files = self._find_python_files()
        print(f"\n📊 Found {len(python_files)} Python files to analyze\n")
        
        if not python_files:
            print("⚠️  No Python files found!")
            return self.simulation_results
        
        # Phase 1: Analyze current state
        print("Phase 1: Analyzing current state...")
        print("-" * 60)
        issues_before = self._analyze_current_state(python_files, verbose)
        self.simulation_results["issues_before"] = issues_before
        
        # Phase 2: Simulate fixes
        print(f"\nPhase 2: Simulating migration fixes...")
        print("-" * 60)
        self._simulate_fixes(python_files, verbose)
        
        # Phase 3: Analyze projected state
        print(f"\nPhase 3: Analyzing projected state...")
        print("-" * 60)
        issues_after = self._analyze_projected_state(python_files, verbose)
        self.simulation_results["issues_after"] = issues_after
        
        # Generate summary
        self._generate_summary()
        
        return self.simulation_results
    
    def _find_python_files(self):
        """Find all Python files in target path."""
        python_files = []
        
        if os.path.isfile(self.target_path):
            if self.target_path.endswith(".py"):
                python_files.append(self.target_path)
        else:
            for root, dirs, files in os.walk(self.target_path):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in [
                    '.git', '__pycache__', '.venv', 'venv', 'node_modules',
                    '.tox', '.pytest_cache', 'build', 'dist', '.eggs'
                ]]
                
                for filename in files:
                    if filename.endswith(".py"):
                        filepath = os.path.join(root, filename)
                        python_files.append(filepath)
        
        return sorted(python_files)
    
    def _analyze_current_state(self, python_files, verbose):
        """Analyze current state before migration."""
        verifier = Python3CompatibilityVerifier()
        
        for filepath in python_files:
            if verbose:
                print(f"  Checking: {filepath}")
            
            # Suppress verifier's print output
            with redirect_stdout(StringIO()):
                verifier.verify_file(filepath)
            
            if verbose and verifier.issues_found:
                print(f"    ⚠️  {len(verifier.issues_found)} issues found")
        
        all_issues = verifier.issues_found
        print(f"\n✓ Current state: {len(all_issues)} Python 2 issues detected")
        return all_issues
    
    def _simulate_fixes(self, python_files, verbose):
        """Simulate applying fixes without modifying files."""
        fixer = Python2to3Fixer(backup_dir=".simulation_tmp")
        
        for filepath in python_files:
            if verbose:
                print(f"  Simulating: {filepath}")
            
            try:
                # Read file
                with open(filepath, 'r') as f:
                    original_content = f.read()
                
                content = original_content
                file_changes = []
                
                # Apply each fix pattern
                for fix_name, fix_info in fixer.fix_patterns.items():
                    pattern = fix_info["pattern"]
                    replacement = fix_info["replacement"]
                    
                    matches = list(re.finditer(pattern, content, re.MULTILINE))
                    if matches:
                        count = len(matches)
                        file_changes.append({
                            "fix_type": fix_name,
                            "description": fix_info["description"],
                            "count": count,
                            "matches": [m.group(0) for m in matches[:3]]  # First 3 examples
                        })
                        
                        self.simulation_results["changes_by_type"][fix_name] += count
                        self.simulation_results["total_changes"] += count
                        
                        # Apply the fix to content for preview
                        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                if file_changes:
                    self.simulation_results["changes_by_file"][filepath] = file_changes
                    self.simulation_results["files_analyzed"].append({
                        "path": filepath,
                        "changes_count": sum(c["count"] for c in file_changes),
                        "changes": file_changes
                    })
                    
                    # Store preview
                    self.simulation_results["file_previews"][filepath] = {
                        "original": original_content[:500],  # First 500 chars
                        "modified": content[:500],
                        "size_change": len(content) - len(original_content)
                    }
                    
                    if verbose:
                        total_changes = sum(c["count"] for c in file_changes)
                        print(f"    ✓ {total_changes} changes simulated")
                        
            except Exception as e:
                if verbose:
                    print(f"    ⚠️  Error: {str(e)}")
        
        print(f"\n✓ Simulated {self.simulation_results['total_changes']} changes across {len(self.simulation_results['files_analyzed'])} files")
    
    def _analyze_projected_state(self, python_files, verbose):
        """Analyze projected state after simulated migration."""
        # For simplicity, we estimate remaining issues based on patterns
        # In a full implementation, we'd apply fixes to temp files and verify
        
        issues_before = len(self.simulation_results["issues_before"])
        changes_made = self.simulation_results["total_changes"]
        
        # Estimate: each change typically fixes 1-2 issues
        estimated_fixed = min(changes_made * 1.5, issues_before)
        estimated_remaining = max(0, issues_before - int(estimated_fixed))
        
        print(f"\n✓ Projected state: ~{estimated_remaining} issues remaining")
        print(f"  (Estimated {int(estimated_fixed)} issues would be resolved)")
        
        return [{"estimated": True, "count": estimated_remaining}]
    
    def _generate_summary(self):
        """Generate summary of simulation."""
        summary = {
            "files_total": len(self._find_python_files()),
            "files_affected": len(self.simulation_results["files_analyzed"]),
            "files_unchanged": len(self._find_python_files()) - len(self.simulation_results["files_analyzed"]),
            "total_changes": self.simulation_results["total_changes"],
            "issues_before": len(self.simulation_results["issues_before"]),
            "issues_after_estimated": len(self.simulation_results["issues_after"]),
            "fix_types_used": len(self.simulation_results["changes_by_type"]),
            "estimated_success_rate": 0
        }
        
        if summary["issues_before"] > 0:
            fixed = summary["issues_before"] - summary["issues_after_estimated"]
            summary["estimated_success_rate"] = (fixed / summary["issues_before"]) * 100
        
        self.simulation_results["summary"] = summary
        
    def print_report(self, detailed=False):
        """Print a human-readable simulation report."""
        summary = self.simulation_results["summary"]
        
        print("\n" + "=" * 60)
        print("🔮 MIGRATION SIMULATION REPORT")
        print("=" * 60)
        
        print(f"\n📊 Overview:")
        print(f"  Total files scanned:     {summary['files_total']}")
        print(f"  Files requiring changes: {summary['files_affected']}")
        print(f"  Files unchanged:         {summary['files_unchanged']}")
        
        print(f"\n🔧 Projected Changes:")
        print(f"  Total fixes to apply:    {summary['total_changes']}")
        print(f"  Fix types needed:        {summary['fix_types_used']}")
        
        print(f"\n📈 Impact Analysis:")
        print(f"  Issues before:           {summary['issues_before']}")
        print(f"  Issues after (est.):     {summary['issues_after_estimated']}")
        print(f"  Success rate (est.):     {summary['estimated_success_rate']:.1f}%")
        
        if detailed:
            print(f"\n🔍 Changes by Type:")
            for fix_type, count in sorted(
                self.simulation_results["changes_by_type"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:
                print(f"  {fix_type:.<35} {count:>4}")
            
            if len(self.simulation_results["changes_by_type"]) > 10:
                print(f"  ... and {len(self.simulation_results['changes_by_type']) - 10} more")
        
        print("\n" + "=" * 60)
        print("✅ Simulation Complete!")
        print("=" * 60)
        
        print("\n💡 Next Steps:")
        print("  1. Review the simulation results above")
        print("  2. Create a backup: ./py2to3 backup create")
        print("  3. Apply fixes: ./py2to3 fix src/")
        print("  4. Verify results: ./py2to3 check src/")
        print("\n⚠️  Note: This is a simulation. No files were modified.")
    
    def save_report(self, output_file="simulation_report.json"):
        """Save simulation report to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(self.simulation_results, f, indent=2, default=str)
        print(f"\n💾 Detailed report saved to: {output_file}")


def main():
    """Command-line interface for migration simulator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Simulate Python 2 to 3 migration without making changes"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )
    parser.add_argument(
        "-d", "--detailed",
        action="store_true",
        help="Show detailed report"
    )
    parser.add_argument(
        "-o", "--output",
        default="simulation_report.json",
        help="Output file for detailed JSON report"
    )
    
    args = parser.parse_args()
    
    # Run simulation
    simulator = MigrationSimulator(args.path)
    simulator.simulate(verbose=args.verbose)
    
    # Print report
    simulator.print_report(detailed=args.detailed)
    
    # Save detailed report
    simulator.save_report(args.output)


if __name__ == "__main__":
    main()
