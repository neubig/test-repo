#!/usr/bin/env python3
"""
Migration Planner - Strategic planning tool for Python 2 to 3 migration

This module analyzes the codebase structure, dependencies, and complexity to create
an optimal migration plan broken down into manageable phases.
"""

import ast
import os
import json
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional


class FileAnalysis:
    """Analysis results for a single Python file."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.imports = set()
        self.imported_by = set()
        self.lines_of_code = 0
        self.complexity_score = 0
        self.issues = []
        self.risk_level = "LOW"
        self.estimated_hours = 0.0
        self.phase = 0
        self.status = "pending"
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "filepath": self.filepath,
            "imports": list(self.imports),
            "imported_by": list(self.imported_by),
            "lines_of_code": self.lines_of_code,
            "complexity_score": self.complexity_score,
            "issues": self.issues,
            "risk_level": self.risk_level,
            "estimated_hours": self.estimated_hours,
            "phase": self.phase,
            "status": self.status
        }


class MigrationPlanner:
    """Creates and manages migration plans for Python 2 to 3 conversion."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.files: Dict[str, FileAnalysis] = {}
        self.phases: List[List[str]] = []
        self.total_estimated_hours = 0.0
        self.plan_created = None
        
    def analyze_codebase(self):
        """Analyze all Python files in the codebase."""
        print(f"Analyzing codebase at: {self.root_path}")
        
        python_files = list(self.root_path.rglob("*.py"))
        print(f"Found {len(python_files)} Python files")
        
        for filepath in python_files:
            rel_path = str(filepath.relative_to(self.root_path))
            
            # Skip certain directories
            if any(skip in rel_path for skip in ['__pycache__', '.git', 'venv', 'env', '.tox']):
                continue
                
            self._analyze_file(filepath)
        
        self._build_dependency_graph()
        print(f"Analyzed {len(self.files)} files")
    
    def _analyze_file(self, filepath: Path):
        """Analyze a single Python file."""
        rel_path = str(filepath.relative_to(self.root_path))
        analysis = FileAnalysis(rel_path)
        
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            analysis.lines_of_code = len([line for line in content.split('\n') if line.strip()])
            
            # Parse imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis.imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            analysis.imports.add(node.module.split('.')[0])
            except SyntaxError:
                analysis.issues.append("Syntax error - may need Python 2 to 3 conversion")
                analysis.complexity_score += 20
            
            # Detect Python 2 patterns
            py2_patterns = [
                ('print ', 'print statement'),
                ('urllib2', 'urllib2 module'),
                ('ConfigParser', 'ConfigParser module'),
                ('iteritems()', 'dict.iteritems()'),
                ('xrange(', 'xrange function'),
                ('basestring', 'basestring type'),
                ('unicode(', 'unicode function'),
                ('except ', 'exception syntax'),
                ('.next()', '.next() method'),
                ('__cmp__', '__cmp__ method'),
            ]
            
            for pattern, description in py2_patterns:
                if pattern in content:
                    analysis.issues.append(description)
                    analysis.complexity_score += 5
            
            # Estimate complexity
            if analysis.lines_of_code > 500:
                analysis.complexity_score += 30
            elif analysis.lines_of_code > 200:
                analysis.complexity_score += 15
            elif analysis.lines_of_code > 100:
                analysis.complexity_score += 5
            
            # Calculate risk level
            if analysis.complexity_score > 50:
                analysis.risk_level = "HIGH"
            elif analysis.complexity_score > 25:
                analysis.risk_level = "MEDIUM"
            else:
                analysis.risk_level = "LOW"
            
            # Estimate hours (rough approximation)
            base_hours = analysis.lines_of_code / 100.0
            issue_hours = len(analysis.issues) * 0.5
            analysis.estimated_hours = round(base_hours + issue_hours, 1)
            
        except Exception as e:
            analysis.issues.append(f"Analysis error: {str(e)}")
            analysis.complexity_score = 50
            analysis.risk_level = "HIGH"
        
        self.files[rel_path] = analysis
    
    def _build_dependency_graph(self):
        """Build the dependency graph between files."""
        # Map module names to file paths
        module_to_file = {}
        for filepath in self.files.keys():
            module_name = filepath.replace('/', '.').replace('.py', '')
            module_to_file[module_name] = filepath
            # Also add shortened versions
            parts = module_name.split('.')
            for i in range(len(parts)):
                partial = '.'.join(parts[i:])
                if partial not in module_to_file:
                    module_to_file[partial] = filepath
        
        # Build reverse dependencies
        for filepath, analysis in self.files.items():
            for import_name in analysis.imports:
                # Try to find the imported file in our codebase
                if import_name in module_to_file:
                    imported_file = module_to_file[import_name]
                    if imported_file in self.files:
                        self.files[imported_file].imported_by.add(filepath)
    
    def create_migration_plan(self):
        """Create a phased migration plan based on dependencies."""
        print("\nCreating migration plan...")
        
        # Track which files are assigned to phases
        assigned = set()
        phase_num = 1
        
        # Phase 1: Leaf nodes (files with no dependencies on other project files)
        leaf_nodes = []
        for filepath, analysis in self.files.items():
            # Check if any imports are from our codebase
            has_internal_deps = any(
                imp in [f.replace('/', '.').replace('.py', '').split('.')[-1] 
                       for f in self.files.keys()]
                for imp in analysis.imports
            )
            if not has_internal_deps:
                leaf_nodes.append(filepath)
                analysis.phase = phase_num
        
        if leaf_nodes:
            self.phases.append(sorted(leaf_nodes, key=lambda f: self.files[f].complexity_score))
            assigned.update(leaf_nodes)
            print(f"Phase {phase_num}: {len(leaf_nodes)} leaf files")
            phase_num += 1
        
        # Subsequent phases: Files whose dependencies are all satisfied
        max_phases = 20  # Safety limit
        while len(assigned) < len(self.files) and phase_num <= max_phases:
            phase_files = []
            
            for filepath, analysis in self.files.items():
                if filepath in assigned:
                    continue
                
                # Check if all dependencies are satisfied
                deps_satisfied = True
                for imported_file in self.files.keys():
                    if imported_file == filepath:
                        continue
                    if filepath in self.files[imported_file].imported_by:
                        if imported_file not in assigned:
                            deps_satisfied = False
                            break
                
                if deps_satisfied:
                    phase_files.append(filepath)
                    analysis.phase = phase_num
            
            if phase_files:
                self.phases.append(sorted(phase_files, key=lambda f: self.files[f].complexity_score))
                assigned.update(phase_files)
                print(f"Phase {phase_num}: {len(phase_files)} files")
                phase_num += 1
            else:
                # No progress made, assign remaining files to final phase
                remaining = [f for f in self.files.keys() if f not in assigned]
                if remaining:
                    for filepath in remaining:
                        self.files[filepath].phase = phase_num
                    self.phases.append(remaining)
                    print(f"Phase {phase_num}: {len(remaining)} files (circular dependencies)")
                break
        
        self.total_estimated_hours = sum(f.estimated_hours for f in self.files.values())
        self.plan_created = datetime.now().isoformat()
        
        print(f"\nPlan created: {len(self.phases)} phases, ~{self.total_estimated_hours:.1f} hours estimated")
    
    def export_text(self, output_file: Optional[str] = None):
        """Export the migration plan as formatted text."""
        lines = []
        lines.append("=" * 80)
        lines.append("PYTHON 2 TO 3 MIGRATION PLAN")
        lines.append("=" * 80)
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Root Path: {self.root_path}")
        lines.append(f"Total Files: {len(self.files)}")
        lines.append(f"Total Phases: {len(self.phases)}")
        lines.append(f"Estimated Total Hours: {self.total_estimated_hours:.1f}")
        lines.append("\n" + "=" * 80)
        lines.append("SUMMARY BY RISK LEVEL")
        lines.append("=" * 80)
        
        risk_counts = defaultdict(int)
        risk_hours = defaultdict(float)
        for analysis in self.files.values():
            risk_counts[analysis.risk_level] += 1
            risk_hours[analysis.risk_level] += analysis.estimated_hours
        
        for risk in ["HIGH", "MEDIUM", "LOW"]:
            if risk in risk_counts:
                lines.append(f"{risk:8s}: {risk_counts[risk]:3d} files, {risk_hours[risk]:6.1f} hours")
        
        lines.append("\n" + "=" * 80)
        lines.append("MIGRATION PHASES")
        lines.append("=" * 80)
        
        for phase_num, phase_files in enumerate(self.phases, 1):
            phase_hours = sum(self.files[f].estimated_hours for f in phase_files)
            lines.append(f"\n{'─' * 80}")
            lines.append(f"Phase {phase_num}: {len(phase_files)} files, ~{phase_hours:.1f} hours")
            lines.append(f"{'─' * 80}")
            
            # Sort by complexity (highest first) within phase
            sorted_files = sorted(phase_files, 
                                key=lambda f: self.files[f].complexity_score, 
                                reverse=True)
            
            for filepath in sorted_files:
                analysis = self.files[filepath]
                lines.append(f"\n  📄 {filepath}")
                lines.append(f"     Risk: {analysis.risk_level:6s} | "
                           f"LOC: {analysis.lines_of_code:4d} | "
                           f"Complexity: {analysis.complexity_score:3d} | "
                           f"Est: {analysis.estimated_hours:.1f}h")
                if analysis.issues:
                    lines.append(f"     Issues: {len(analysis.issues)}")
                    for issue in analysis.issues[:3]:
                        lines.append(f"       • {issue}")
                    if len(analysis.issues) > 3:
                        lines.append(f"       • ... and {len(analysis.issues) - 3} more")
                if analysis.imported_by:
                    lines.append(f"     Used by: {len(analysis.imported_by)} file(s)")
        
        lines.append("\n" + "=" * 80)
        lines.append("RECOMMENDED APPROACH")
        lines.append("=" * 80)
        lines.append("\n1. Review this plan and adjust priorities as needed")
        lines.append("2. Start with Phase 1 (leaf nodes with minimal dependencies)")
        lines.append("3. Test thoroughly after each phase before proceeding")
        lines.append("4. Use the py2to3 toolkit commands:")
        lines.append("   - Run preflight checks: ./py2to3 preflight")
        lines.append("   - Check compatibility: ./py2to3 check <file>")
        lines.append("   - Apply fixes: ./py2to3 fix <file>")
        lines.append("   - Generate tests: ./py2to3 test-gen <file>")
        lines.append("   - Create git checkpoints: ./py2to3 git checkpoint")
        lines.append("5. Track progress with: ./py2to3 stats")
        lines.append("\n" + "=" * 80)
        
        result = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(result)
            print(f"\nPlan exported to: {output_file}")
        
        return result
    
    def export_json(self, output_file: str):
        """Export the migration plan as JSON."""
        plan_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "root_path": str(self.root_path),
                "total_files": len(self.files),
                "total_phases": len(self.phases),
                "estimated_total_hours": self.total_estimated_hours,
                "plan_created": self.plan_created
            },
            "phases": [
                {
                    "phase_number": i + 1,
                    "file_count": len(phase),
                    "estimated_hours": sum(self.files[f].estimated_hours for f in phase),
                    "files": [self.files[f].to_dict() for f in phase]
                }
                for i, phase in enumerate(self.phases)
            ],
            "risk_summary": self._get_risk_summary()
        }
        
        with open(output_file, 'w') as f:
            json.dump(plan_data, f, indent=2)
        
        print(f"\nJSON plan exported to: {output_file}")
    
    def export_markdown(self, output_file: str):
        """Export the migration plan as Markdown."""
        lines = []
        lines.append("# Python 2 to 3 Migration Plan\n")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        lines.append(f"**Root Path:** `{self.root_path}`  ")
        lines.append(f"**Total Files:** {len(self.files)}  ")
        lines.append(f"**Total Phases:** {len(self.phases)}  ")
        lines.append(f"**Estimated Total Hours:** {self.total_estimated_hours:.1f}\n")
        
        lines.append("## Summary by Risk Level\n")
        risk_counts = defaultdict(int)
        risk_hours = defaultdict(float)
        for analysis in self.files.values():
            risk_counts[analysis.risk_level] += 1
            risk_hours[analysis.risk_level] += analysis.estimated_hours
        
        lines.append("| Risk Level | Files | Estimated Hours |")
        lines.append("|------------|-------|-----------------|")
        for risk in ["HIGH", "MEDIUM", "LOW"]:
            if risk in risk_counts:
                emoji = "🔴" if risk == "HIGH" else "🟡" if risk == "MEDIUM" else "🟢"
                lines.append(f"| {emoji} {risk} | {risk_counts[risk]} | {risk_hours[risk]:.1f} |")
        
        lines.append("\n## Migration Phases\n")
        
        for phase_num, phase_files in enumerate(self.phases, 1):
            phase_hours = sum(self.files[f].estimated_hours for f in phase_files)
            lines.append(f"### Phase {phase_num}\n")
            lines.append(f"**Files:** {len(phase_files)} | **Estimated Hours:** {phase_hours:.1f}\n")
            
            sorted_files = sorted(phase_files, 
                                key=lambda f: self.files[f].complexity_score, 
                                reverse=True)
            
            for filepath in sorted_files:
                analysis = self.files[filepath]
                risk_emoji = "🔴" if analysis.risk_level == "HIGH" else "🟡" if analysis.risk_level == "MEDIUM" else "🟢"
                lines.append(f"#### {risk_emoji} `{filepath}`\n")
                lines.append(f"- **Risk:** {analysis.risk_level}")
                lines.append(f"- **Lines of Code:** {analysis.lines_of_code}")
                lines.append(f"- **Complexity Score:** {analysis.complexity_score}")
                lines.append(f"- **Estimated Hours:** {analysis.estimated_hours}")
                
                if analysis.issues:
                    lines.append(f"- **Issues Found:** {len(analysis.issues)}")
                    for issue in analysis.issues[:5]:
                        lines.append(f"  - {issue}")
                    if len(analysis.issues) > 5:
                        lines.append(f"  - *... and {len(analysis.issues) - 5} more*")
                
                if analysis.imported_by:
                    lines.append(f"- **Used by:** {len(analysis.imported_by)} file(s)")
                
                lines.append("")
        
        lines.append("## Recommended Approach\n")
        lines.append("1. ✅ Review this plan and adjust priorities as needed")
        lines.append("2. 🌱 Start with Phase 1 (leaf nodes with minimal dependencies)")
        lines.append("3. 🧪 Test thoroughly after each phase before proceeding")
        lines.append("4. 🔧 Use the py2to3 toolkit commands:")
        lines.append("   - `./py2to3 preflight` - Run preflight checks")
        lines.append("   - `./py2to3 check <file>` - Check compatibility")
        lines.append("   - `./py2to3 fix <file>` - Apply fixes")
        lines.append("   - `./py2to3 test-gen <file>` - Generate tests")
        lines.append("   - `./py2to3 git checkpoint` - Create git checkpoints")
        lines.append("5. 📊 Track progress with `./py2to3 stats`")
        
        result = "\n".join(lines)
        
        with open(output_file, 'w') as f:
            f.write(result)
        
        print(f"\nMarkdown plan exported to: {output_file}")
    
    def _get_risk_summary(self):
        """Get risk summary statistics."""
        risk_counts = defaultdict(int)
        risk_hours = defaultdict(float)
        for analysis in self.files.values():
            risk_counts[analysis.risk_level] += 1
            risk_hours[analysis.risk_level] += analysis.estimated_hours
        
        return {
            "HIGH": {"files": risk_counts["HIGH"], "hours": risk_hours["HIGH"]},
            "MEDIUM": {"files": risk_counts["MEDIUM"], "hours": risk_hours["MEDIUM"]},
            "LOW": {"files": risk_counts["LOW"], "hours": risk_hours["LOW"]}
        }


def main():
    """Main entry point for standalone usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create a strategic migration plan for Python 2 to 3 conversion"
    )
    parser.add_argument("path", help="Path to analyze")
    parser.add_argument("-o", "--output", help="Output file (default: print to console)")
    parser.add_argument("-f", "--format", choices=["text", "json", "markdown"], 
                       default="text", help="Output format")
    
    args = parser.parse_args()
    
    planner = MigrationPlanner(args.path)
    planner.analyze_codebase()
    planner.create_migration_plan()
    
    if args.format == "json":
        if not args.output:
            args.output = "migration_plan.json"
        planner.export_json(args.output)
    elif args.format == "markdown":
        if not args.output:
            args.output = "migration_plan.md"
        planner.export_markdown(args.output)
    else:
        text_output = planner.export_text(args.output)
        if not args.output:
            print(text_output)


if __name__ == "__main__":
    main()
