#!/usr/bin/env python3
"""
Migration Checklist Generator

Generates personalized, prioritized migration checklists based on codebase analysis.
Creates actionable roadmaps with quick wins, dependencies, and effort estimates.
"""

import ast
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional


class ChecklistGenerator:
    """Generate personalized migration checklists."""
    
    ISSUE_PRIORITIES = {
        'print_statement': 1,  # Easy fix
        'import_change': 2,
        'exception_syntax': 1,
        'iterator_method': 2,
        'string_type': 3,
        'division': 3,
        'long_type': 2,
        'unicode': 4,
        'basestring': 3,
        'xrange': 1,
        'dict_methods': 2,
        'old_style_class': 3,
        'cmp_function': 4,
        'encoding': 4,
        'file_function': 3,
    }
    
    def __init__(self, project_path: str):
        """Initialize checklist generator.
        
        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = Path(project_path)
        self.files_data = {}
        self.dependencies = defaultdict(set)
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: File analysis data
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e), 'issues': [], 'complexity': 0}
        
        issues = []
        complexity = 0
        
        # Detect Python 2 patterns
        if re.search(r'\bprint\s+["\']', content):
            issues.append({'type': 'print_statement', 'priority': 1, 'effort': 1})
        
        if re.search(r'\bimport\s+(urllib2|urlparse|ConfigParser|Queue)\b', content):
            issues.append({'type': 'import_change', 'priority': 2, 'effort': 2})
        
        if re.search(r'except\s+\w+\s*,\s*\w+:', content):
            issues.append({'type': 'exception_syntax', 'priority': 1, 'effort': 1})
        
        if re.search(r'\.(iteritems|iterkeys|itervalues)\(\)', content):
            issues.append({'type': 'iterator_method', 'priority': 2, 'effort': 2})
        
        if re.search(r'\bxrange\b', content):
            issues.append({'type': 'xrange', 'priority': 1, 'effort': 1})
        
        if re.search(r'\bbasestring\b', content):
            issues.append({'type': 'basestring', 'priority': 3, 'effort': 3})
        
        if re.search(r'\bunicode\s*\(', content):
            issues.append({'type': 'unicode', 'priority': 4, 'effort': 4})
        
        if re.search(r'\blong\s*\(', content):
            issues.append({'type': 'long_type', 'priority': 2, 'effort': 2})
        
        if re.search(r'\bfile\s*\(', content):
            issues.append({'type': 'file_function', 'priority': 3, 'effort': 3})
        
        # Calculate complexity score
        complexity = len(issues) * 10
        complexity += content.count('\n')  # Lines of code
        complexity += content.count('class ') * 20  # Classes
        complexity += content.count('def ') * 10  # Functions
        
        # Find imports to determine dependencies
        imports = re.findall(r'from\s+([\w.]+)\s+import|import\s+([\w.]+)', content)
        local_imports = []
        for imp in imports:
            module = imp[0] or imp[1]
            # Check if it's a local import
            if not module.split('.')[0] in ['os', 'sys', 're', 'json', 'ast', 'pathlib']:
                local_imports.append(module)
        
        return {
            'path': str(file_path.relative_to(self.project_path)),
            'issues': issues,
            'complexity': complexity,
            'dependencies': local_imports,
            'lines': content.count('\n') + 1,
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze the entire project.
        
        Returns:
            dict: Project analysis data
        """
        python_files = list(self.project_path.rglob('*.py'))
        
        # Filter out common non-source directories
        exclude_patterns = ['venv', 'env', '.venv', 'node_modules', '__pycache__', '.git']
        python_files = [
            f for f in python_files 
            if not any(pattern in str(f) for pattern in exclude_patterns)
        ]
        
        for file_path in python_files:
            file_data = self.analyze_file(file_path)
            self.files_data[str(file_path.relative_to(self.project_path))] = file_data
            
            # Build dependency graph
            for dep in file_data.get('dependencies', []):
                self.dependencies[file_data['path']].add(dep)
        
        return self.files_data
    
    def calculate_priority_score(self, file_data: Dict[str, Any]) -> float:
        """Calculate priority score for a file.
        
        Higher score = should be done sooner
        
        Args:
            file_data: File analysis data
            
        Returns:
            float: Priority score
        """
        score = 0.0
        
        # Fewer issues = higher priority (quick wins)
        issue_count = len(file_data['issues'])
        if issue_count == 0:
            return 0.0
        
        # Low complexity = higher priority
        complexity = file_data['complexity']
        if complexity < 100:
            score += 50
        elif complexity < 300:
            score += 30
        else:
            score += 10
        
        # Easy issues = higher priority
        avg_effort = sum(i['effort'] for i in file_data['issues']) / issue_count
        if avg_effort < 2:
            score += 40
        elif avg_effort < 3:
            score += 20
        else:
            score += 5
        
        # Files with no dependencies on other local files = higher priority
        if len(file_data.get('dependencies', [])) == 0:
            score += 30
        
        # Number of issues (normalized)
        score += max(0, 20 - issue_count * 2)
        
        return score
    
    def identify_quick_wins(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Identify files that are quick wins (easy to migrate).
        
        Args:
            top_n: Number of quick wins to return
            
        Returns:
            list: Quick win files
        """
        files_with_issues = [
            (path, data) for path, data in self.files_data.items()
            if len(data.get('issues', [])) > 0
        ]
        
        # Sort by priority score (highest first)
        sorted_files = sorted(
            files_with_issues,
            key=lambda x: self.calculate_priority_score(x[1]),
            reverse=True
        )
        
        return [
            {
                'path': path,
                'issues': len(data['issues']),
                'complexity': data['complexity'],
                'priority_score': self.calculate_priority_score(data)
            }
            for path, data in sorted_files[:top_n]
        ]
    
    def identify_blockers(self) -> List[Dict[str, Any]]:
        """Identify files that are blockers (many dependencies).
        
        Returns:
            list: Blocker files
        """
        # Count how many files depend on each file
        depended_on = defaultdict(int)
        for file_path, deps in self.dependencies.items():
            for dep in deps:
                # Try to map module name to file path
                dep_path = dep.replace('.', '/') + '.py'
                depended_on[dep_path] += 1
        
        blockers = []
        for file_path, count in depended_on.items():
            if count >= 2 and file_path in self.files_data:
                file_data = self.files_data[file_path]
                if len(file_data.get('issues', [])) > 0:
                    blockers.append({
                        'path': file_path,
                        'dependent_count': count,
                        'issues': len(file_data['issues']),
                        'complexity': file_data['complexity']
                    })
        
        return sorted(blockers, key=lambda x: x['dependent_count'], reverse=True)
    
    def generate_checklist(self, format: str = 'text') -> str:
        """Generate the migration checklist.
        
        Args:
            format: Output format ('text', 'markdown', 'json')
            
        Returns:
            str: Formatted checklist
        """
        # Analyze if not already done
        if not self.files_data:
            self.analyze_project()
        
        quick_wins = self.identify_quick_wins(5)
        blockers = self.identify_blockers()
        
        # Calculate statistics
        total_files = len(self.files_data)
        files_with_issues = sum(1 for d in self.files_data.values() if len(d.get('issues', [])) > 0)
        total_issues = sum(len(d.get('issues', [])) for d in self.files_data.values())
        
        if format == 'json':
            return json.dumps({
                'generated_at': datetime.now().isoformat(),
                'statistics': {
                    'total_files': total_files,
                    'files_with_issues': files_with_issues,
                    'total_issues': total_issues,
                },
                'quick_wins': quick_wins,
                'blockers': blockers,
                'all_files': [
                    {
                        'path': path,
                        'issues': len(data['issues']),
                        'complexity': data['complexity'],
                        'priority_score': self.calculate_priority_score(data)
                    }
                    for path, data in self.files_data.items()
                    if len(data.get('issues', [])) > 0
                ]
            }, indent=2)
        
        elif format == 'markdown':
            return self._generate_markdown_checklist(
                quick_wins, blockers, total_files, files_with_issues, total_issues
            )
        
        else:  # text format
            return self._generate_text_checklist(
                quick_wins, blockers, total_files, files_with_issues, total_issues
            )
    
    def _generate_text_checklist(
        self, quick_wins, blockers, total_files, files_with_issues, total_issues
    ) -> str:
        """Generate text format checklist."""
        lines = []
        lines.append("=" * 80)
        lines.append("PYTHON 2 TO 3 MIGRATION CHECKLIST")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("PROJECT OVERVIEW")
        lines.append("-" * 80)
        lines.append(f"Total Python files:        {total_files}")
        lines.append(f"Files needing migration:   {files_with_issues}")
        lines.append(f"Total issues found:        {total_issues}")
        lines.append(f"Completion:                {((total_files - files_with_issues) / total_files * 100):.1f}%")
        lines.append("")
        
        lines.append("RECOMMENDED MIGRATION STRATEGY")
        lines.append("-" * 80)
        lines.append("1. Start with Quick Wins (easy files)")
        lines.append("2. Address Blockers (files that other files depend on)")
        lines.append("3. Work through remaining files by priority")
        lines.append("4. Run tests after each phase")
        lines.append("")
        
        if quick_wins:
            lines.append("PHASE 1: QUICK WINS (Start Here!)")
            lines.append("-" * 80)
            lines.append("These files are the easiest to migrate. Start here to build momentum!")
            lines.append("")
            for i, item in enumerate(quick_wins, 1):
                lines.append(f"  [{' ' if i > 1 else 'X'}] {item['path']}")
                lines.append(f"      Issues: {item['issues']} | "
                           f"Complexity: {item['complexity']} | "
                           f"Priority Score: {item['priority_score']:.0f}")
                lines.append("")
        
        if blockers:
            lines.append("PHASE 2: BLOCKERS (High Priority)")
            lines.append("-" * 80)
            lines.append("These files are depended on by other files. Migrate them early!")
            lines.append("")
            for i, item in enumerate(blockers, 1):
                lines.append(f"  [ ] {item['path']}")
                lines.append(f"      Used by {item['dependent_count']} other files | "
                           f"Issues: {item['issues']} | "
                           f"Complexity: {item['complexity']}")
                lines.append("")
        
        lines.append("PHASE 3: REMAINING FILES")
        lines.append("-" * 80)
        lines.append("Work through these files in order of priority score.")
        lines.append("")
        
        # Get all remaining files sorted by priority
        quick_win_paths = {item['path'] for item in quick_wins}
        blocker_paths = {item['path'] for item in blockers}
        
        remaining = [
            (path, data) for path, data in self.files_data.items()
            if len(data.get('issues', [])) > 0 
            and path not in quick_win_paths 
            and path not in blocker_paths
        ]
        
        remaining.sort(key=lambda x: self.calculate_priority_score(x[1]), reverse=True)
        
        for i, (path, data) in enumerate(remaining[:10], 1):  # Show top 10
            lines.append(f"  [ ] {path}")
            lines.append(f"      Issues: {len(data['issues'])} | "
                       f"Complexity: {data['complexity']} | "
                       f"Priority: {self.calculate_priority_score(data):.0f}")
            lines.append("")
        
        if len(remaining) > 10:
            lines.append(f"  ... and {len(remaining) - 10} more files")
            lines.append("")
        
        lines.append("NEXT STEPS")
        lines.append("-" * 80)
        lines.append("1. Review this checklist with your team")
        lines.append("2. Start with Phase 1 (Quick Wins)")
        lines.append("3. Run: ./py2to3 fix <file> --backup-dir backups")
        lines.append("4. Run: ./py2to3 check <file> to verify")
        lines.append("5. Run tests to ensure functionality")
        lines.append("6. Move to next file in the checklist")
        lines.append("7. Re-generate checklist to see progress")
        lines.append("")
        
        lines.append("TIP: Run './py2to3 checklist --format markdown > MIGRATION_PLAN.md'")
        lines.append("     to save this checklist to a file for tracking!")
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def _generate_markdown_checklist(
        self, quick_wins, blockers, total_files, files_with_issues, total_issues
    ) -> str:
        """Generate markdown format checklist."""
        lines = []
        lines.append("# Python 2 to 3 Migration Checklist")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")
        
        lines.append("## 📊 Project Overview")
        lines.append("")
        lines.append(f"- **Total Python files:** {total_files}")
        lines.append(f"- **Files needing migration:** {files_with_issues}")
        lines.append(f"- **Total issues found:** {total_issues}")
        lines.append(f"- **Completion:** {((total_files - files_with_issues) / total_files * 100):.1f}%")
        lines.append("")
        
        lines.append("## 🎯 Recommended Migration Strategy")
        lines.append("")
        lines.append("1. **Start with Quick Wins** (easy files to build momentum)")
        lines.append("2. **Address Blockers** (files that other files depend on)")
        lines.append("3. **Work through remaining files** by priority score")
        lines.append("4. **Run tests** after each phase")
        lines.append("")
        
        if quick_wins:
            lines.append("## ⚡ Phase 1: Quick Wins (Start Here!)")
            lines.append("")
            lines.append("These files are the easiest to migrate. Start here to build momentum!")
            lines.append("")
            for i, item in enumerate(quick_wins, 1):
                checkbox = "- [x]" if i == 1 else "- [ ]"
                lines.append(f"{checkbox} **{item['path']}**")
                lines.append(f"  - Issues: {item['issues']}")
                lines.append(f"  - Complexity: {item['complexity']}")
                lines.append(f"  - Priority Score: {item['priority_score']:.0f}")
                lines.append("")
        
        if blockers:
            lines.append("## 🚧 Phase 2: Blockers (High Priority)")
            lines.append("")
            lines.append("These files are depended on by other files. Migrate them early!")
            lines.append("")
            for item in blockers:
                lines.append(f"- [ ] **{item['path']}**")
                lines.append(f"  - Used by **{item['dependent_count']}** other files")
                lines.append(f"  - Issues: {item['issues']}")
                lines.append(f"  - Complexity: {item['complexity']}")
                lines.append("")
        
        lines.append("## 📋 Phase 3: Remaining Files")
        lines.append("")
        lines.append("Work through these files in order of priority score.")
        lines.append("")
        
        # Get remaining files
        quick_win_paths = {item['path'] for item in quick_wins}
        blocker_paths = {item['path'] for item in blockers}
        
        remaining = [
            (path, data) for path, data in self.files_data.items()
            if len(data.get('issues', [])) > 0 
            and path not in quick_win_paths 
            and path not in blocker_paths
        ]
        
        remaining.sort(key=lambda x: self.calculate_priority_score(x[1]), reverse=True)
        
        for path, data in remaining[:10]:  # Show top 10
            lines.append(f"- [ ] **{path}**")
            lines.append(f"  - Issues: {len(data['issues'])}")
            lines.append(f"  - Complexity: {data['complexity']}")
            lines.append(f"  - Priority: {self.calculate_priority_score(data):.0f}")
            lines.append("")
        
        if len(remaining) > 10:
            lines.append(f"*... and {len(remaining) - 10} more files*")
            lines.append("")
        
        lines.append("## 🚀 Next Steps")
        lines.append("")
        lines.append("1. Review this checklist with your team")
        lines.append("2. Start with Phase 1 (Quick Wins)")
        lines.append("3. For each file:")
        lines.append("   ```bash")
        lines.append("   ./py2to3 fix <file> --backup-dir backups")
        lines.append("   ./py2to3 check <file>")
        lines.append("   # Run your tests")
        lines.append("   ```")
        lines.append("4. Move to next file in the checklist")
        lines.append("5. Re-generate checklist to see progress")
        lines.append("")
        lines.append("---")
        lines.append("*Run `./py2to3 checklist` to regenerate this checklist and track progress*")
        
        return '\n'.join(lines)


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate personalized migration checklists"
    )
    parser.add_argument(
        'path',
        help='Path to Python project'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'markdown', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: print to console)'
    )
    
    args = parser.parse_args()
    
    generator = ChecklistGenerator(args.path)
    checklist = generator.generate_checklist(format=args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(checklist)
        print(f"Checklist saved to {args.output}")
    else:
        print(checklist)


if __name__ == '__main__':
    main()
