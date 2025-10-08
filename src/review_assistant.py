#!/usr/bin/env python3
"""
Code Review Assistant for Python 2→3 Migrations

Helps teams review migration changes by:
- Analyzing changes and identifying what needs manual review
- Generating code review checklists
- Creating annotated diffs with explanations
- Categorizing changes by risk and type
- Providing review guidelines
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class MigrationReviewAssistant:
    """Assistant for reviewing Python 2 to 3 migration changes."""
    
    # Patterns that indicate different types of changes
    CHANGE_PATTERNS = {
        'print_statement': {
            'pattern': r'print\s*\(',
            'risk': 'low',
            'review_notes': 'Verify print statements work correctly, especially with file arguments'
        },
        'import_changes': {
            'pattern': r'(from|import)\s+(urllib\.request|urllib\.parse|urllib\.error|configparser|queue|builtins)',
            'risk': 'medium',
            'review_notes': 'Check that imported modules are used correctly with Python 3 APIs'
        },
        'exception_handling': {
            'pattern': r'except\s+\w+\s+as\s+\w+',
            'risk': 'low',
            'review_notes': 'Verify exception handling logic is correct'
        },
        'dict_methods': {
            'pattern': r'\.(items|keys|values)\(\)',
            'risk': 'low',
            'review_notes': 'Ensure code handles iterators correctly (not lists)'
        },
        'string_types': {
            'pattern': r'\bstr\b',
            'risk': 'medium',
            'review_notes': 'Check string/bytes handling - may need explicit encode/decode'
        },
        'division': {
            'pattern': r'//|\s+/\s+',
            'risk': 'high',
            'review_notes': 'CRITICAL: Verify division behavior (/ vs //) is correct'
        },
        'range_xrange': {
            'pattern': r'\brange\(',
            'risk': 'low',
            'review_notes': 'Verify range usage (now returns iterator, not list)'
        },
        'unicode': {
            'pattern': r'\b(encode|decode)\(',
            'risk': 'high',
            'review_notes': 'CRITICAL: Check encoding/decoding logic carefully'
        },
        'file_operations': {
            'pattern': r'\bopen\(',
            'risk': 'medium',
            'review_notes': 'Check file operations handle text/binary modes correctly'
        },
        'metaclass': {
            'pattern': r'__metaclass__|\bmetaclass=',
            'risk': 'high',
            'review_notes': 'CRITICAL: Metaclass changes are complex - verify thoroughly'
        }
    }
    
    def __init__(self, backup_dir: Optional[str] = None):
        """Initialize the review assistant.
        
        Args:
            backup_dir: Directory containing backups for comparison
        """
        self.backup_dir = backup_dir or '.py2to3_backups'
        self.changes = []
        self.review_items = []
        
    def analyze_changes(self, path: str) -> Dict:
        """Analyze migration changes in the given path.
        
        Args:
            path: Path to file or directory to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if os.path.isfile(path):
            return self._analyze_file(path)
        elif os.path.isdir(path):
            return self._analyze_directory(path)
        else:
            raise ValueError(f"Invalid path: {path}")
    
    def _analyze_directory(self, directory: str) -> Dict:
        """Analyze all Python files in a directory."""
        results = {
            'files_analyzed': 0,
            'changes_found': 0,
            'high_risk_changes': 0,
            'medium_risk_changes': 0,
            'low_risk_changes': 0,
            'files': [],
            'review_checklist': [],
            'summary': {}
        }
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    file_result = self._analyze_file(filepath)
                    results['files_analyzed'] += 1
                    results['changes_found'] += len(file_result.get('changes', []))
                    results['high_risk_changes'] += file_result.get('high_risk_count', 0)
                    results['medium_risk_changes'] += file_result.get('medium_risk_count', 0)
                    results['low_risk_changes'] += file_result.get('low_risk_count', 0)
                    
                    if file_result.get('changes'):
                        results['files'].append(file_result)
        
        # Generate review checklist
        results['review_checklist'] = self._generate_checklist(results)
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _analyze_file(self, filepath: str) -> Dict:
        """Analyze a single file for migration changes."""
        result = {
            'file': filepath,
            'changes': [],
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0,
            'files_analyzed': 1,
            'changes_found': 0,
            'high_risk_changes': 0,
            'medium_risk_changes': 0,
            'low_risk_changes': 0,
            'files': [],
            'review_checklist': [],
            'summary': {}
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check for each change pattern
            for change_type, config in self.CHANGE_PATTERNS.items():
                pattern = config['pattern']
                matches = list(re.finditer(pattern, content))
                
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''
                    
                    change = {
                        'type': change_type,
                        'line': line_num,
                        'code': line_content,
                        'risk': config['risk'],
                        'review_notes': config['review_notes']
                    }
                    result['changes'].append(change)
                    
                    # Count by risk level
                    if config['risk'] == 'high':
                        result['high_risk_count'] += 1
                        result['high_risk_changes'] += 1
                    elif config['risk'] == 'medium':
                        result['medium_risk_count'] += 1
                        result['medium_risk_changes'] += 1
                    else:
                        result['low_risk_count'] += 1
                        result['low_risk_changes'] += 1
            
            result['changes_found'] = len(result['changes'])
            if result['changes']:
                result['files'].append({
                    'file': filepath,
                    'changes': result['changes'],
                    'high_risk_count': result['high_risk_count'],
                    'medium_risk_count': result['medium_risk_count'],
                    'low_risk_count': result['low_risk_count']
                })
            
            # Generate checklist and summary for single file
            result['review_checklist'] = self._generate_checklist(result)
            result['summary'] = self._generate_summary(result)
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _generate_checklist(self, analysis: Dict) -> List[Dict]:
        """Generate a code review checklist based on analysis."""
        checklist = []
        
        # Add general items
        checklist.append({
            'category': 'General',
            'item': 'All tests pass after migration',
            'priority': 'critical'
        })
        checklist.append({
            'category': 'General',
            'item': 'Code runs without warnings under Python 3',
            'priority': 'critical'
        })
        checklist.append({
            'category': 'General',
            'item': 'All imports work correctly',
            'priority': 'high'
        })
        
        # Add specific items based on what was found
        change_types = set()
        for file_info in analysis.get('files', []):
            for change in file_info.get('changes', []):
                change_types.add(change['type'])
        
        # Add relevant checklist items
        if 'division' in change_types:
            checklist.append({
                'category': 'Division',
                'item': 'Verify integer division behavior (/ vs //)',
                'priority': 'critical'
            })
        
        if 'unicode' in change_types or 'string_types' in change_types:
            checklist.append({
                'category': 'Strings',
                'item': 'Check all string/bytes conversions',
                'priority': 'critical'
            })
            checklist.append({
                'category': 'Strings',
                'item': 'Verify encode/decode operations use correct encodings',
                'priority': 'high'
            })
        
        if 'import_changes' in change_types:
            checklist.append({
                'category': 'Imports',
                'item': 'Verify renamed modules work with Python 3 APIs',
                'priority': 'high'
            })
        
        if 'dict_methods' in change_types:
            checklist.append({
                'category': 'Data Structures',
                'item': 'Check dict.keys()/values()/items() usage handles iterators',
                'priority': 'medium'
            })
        
        if 'file_operations' in change_types:
            checklist.append({
                'category': 'File I/O',
                'item': 'Verify file operations handle text/binary modes correctly',
                'priority': 'high'
            })
        
        if 'exception_handling' in change_types:
            checklist.append({
                'category': 'Exceptions',
                'item': 'Check exception handling logic',
                'priority': 'medium'
            })
        
        return checklist
    
    def _generate_summary(self, analysis: Dict) -> Dict:
        """Generate a summary of the analysis."""
        total_changes = analysis['changes_found']
        critical_changes = analysis['high_risk_changes']
        
        # Calculate review effort estimate
        # High risk: 5 min each, Medium: 2 min each, Low: 1 min each
        estimated_minutes = (
            analysis['high_risk_changes'] * 5 +
            analysis['medium_risk_changes'] * 2 +
            analysis['low_risk_changes'] * 1
        )
        
        return {
            'total_files': analysis['files_analyzed'],
            'files_with_changes': len(analysis['files']),
            'total_changes': total_changes,
            'critical_items': critical_changes,
            'estimated_review_time': f"{estimated_minutes} minutes",
            'recommendation': self._get_recommendation(total_changes, critical_changes)
        }
    
    def _get_recommendation(self, total_changes: int, critical_changes: int) -> str:
        """Get a review recommendation based on analysis."""
        if critical_changes > 10:
            return "⚠️  High number of critical changes - recommend thorough review by senior developer"
        elif critical_changes > 5:
            return "⚠️  Several critical changes - recommend careful review with testing"
        elif total_changes > 50:
            return "ℹ️  Large number of changes - consider reviewing in batches"
        elif total_changes > 20:
            return "✓ Moderate changes - standard review process recommended"
        elif total_changes > 0:
            return "✓ Few changes - quick review should suffice"
        else:
            return "✓ No significant changes detected"
    
    def generate_report(self, analysis: Dict, output_format: str = 'markdown') -> str:
        """Generate a formatted review report.
        
        Args:
            analysis: Analysis results
            output_format: 'markdown', 'text', or 'json'
            
        Returns:
            Formatted report string
        """
        if output_format == 'json':
            return json.dumps(analysis, indent=2)
        elif output_format == 'markdown':
            return self._generate_markdown_report(analysis)
        else:
            return self._generate_text_report(analysis)
    
    def _generate_markdown_report(self, analysis: Dict) -> str:
        """Generate a Markdown-formatted report."""
        summary = analysis['summary']
        
        report = f"""# Python 2→3 Migration Code Review

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Files Analyzed:** {summary['total_files']}
- **Files Changed:** {summary['files_with_changes']}
- **Total Changes:** {summary['total_changes']}
- **Critical Items:** {summary['critical_items']} ⚠️
- **Estimated Review Time:** {summary['estimated_review_time']}

**Recommendation:** {summary['recommendation']}

## Risk Breakdown

| Risk Level | Count |
|------------|-------|
| 🔴 High    | {analysis['high_risk_changes']} |
| 🟡 Medium  | {analysis['medium_risk_changes']} |
| 🟢 Low     | {analysis['low_risk_changes']} |

## Review Checklist

"""
        # Add checklist items
        for item in analysis['review_checklist']:
            priority_icon = {
                'critical': '🔴',
                'high': '🟡',
                'medium': '🔵',
                'low': '⚪'
            }.get(item['priority'], '⚪')
            
            report += f"- [ ] {priority_icon} **{item['category']}**: {item['item']}\n"
        
        report += "\n## Detailed Changes\n\n"
        
        # Add file-by-file breakdown
        for file_info in sorted(analysis['files'], 
                               key=lambda x: x['high_risk_count'], 
                               reverse=True):
            if not file_info.get('changes'):
                continue
                
            report += f"\n### {file_info['file']}\n\n"
            report += f"- High risk: {file_info['high_risk_count']}, "
            report += f"Medium risk: {file_info['medium_risk_count']}, "
            report += f"Low risk: {file_info['low_risk_count']}\n\n"
            
            # Group changes by type
            changes_by_type = {}
            for change in file_info['changes']:
                change_type = change['type']
                if change_type not in changes_by_type:
                    changes_by_type[change_type] = []
                changes_by_type[change_type].append(change)
            
            for change_type, changes in sorted(changes_by_type.items()):
                risk_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[changes[0]['risk']]
                report += f"**{risk_icon} {change_type.replace('_', ' ').title()}** "
                report += f"({len(changes)} occurrence{'s' if len(changes) > 1 else ''})\n"
                report += f"- Review: {changes[0]['review_notes']}\n"
                
                # Show first few examples
                for change in changes[:3]:
                    report += f"  - Line {change['line']}: `{change['code']}`\n"
                
                if len(changes) > 3:
                    report += f"  - ... and {len(changes) - 3} more\n"
                report += "\n"
        
        report += "\n## Review Guidelines\n\n"
        report += """### Critical Items (Must Review Thoroughly)
- **Division operations**: Verify integer division vs. float division
- **String/bytes handling**: Check all encode/decode operations
- **Metaclasses**: Complex changes requiring deep understanding

### Important Items (Should Review Carefully)
- **Import changes**: Verify APIs are used correctly
- **File operations**: Check text vs. binary mode handling
- **Dictionary methods**: Ensure iterator handling is correct

### Low Priority Items (Quick Verification)
- **Print statements**: Usually safe, verify arguments
- **Exception handling**: Syntax changes, logic should be same
- **Range usage**: Verify list conversion if needed

## Testing Recommendations

1. Run all existing tests and verify they pass
2. Add tests for any high-risk changes
3. Perform manual testing of critical paths
4. Check for any deprecation warnings
5. Verify behavior matches Python 2 version

---
*Generated by py2to3 Code Review Assistant*
"""
        return report
    
    def _generate_text_report(self, analysis: Dict) -> str:
        """Generate a plain text report."""
        summary = analysis['summary']
        
        report = "=" * 70 + "\n"
        report += "Python 2→3 Migration Code Review\n"
        report += "=" * 70 + "\n\n"
        
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "SUMMARY\n"
        report += "-" * 70 + "\n"
        report += f"Files Analyzed: {summary['total_files']}\n"
        report += f"Files Changed: {summary['files_with_changes']}\n"
        report += f"Total Changes: {summary['total_changes']}\n"
        report += f"Critical Items: {summary['critical_items']}\n"
        report += f"Estimated Review Time: {summary['estimated_review_time']}\n\n"
        report += f"Recommendation: {summary['recommendation']}\n\n"
        
        report += "RISK BREAKDOWN\n"
        report += "-" * 70 + "\n"
        report += f"High Risk:   {analysis['high_risk_changes']}\n"
        report += f"Medium Risk: {analysis['medium_risk_changes']}\n"
        report += f"Low Risk:    {analysis['low_risk_changes']}\n\n"
        
        report += "REVIEW CHECKLIST\n"
        report += "-" * 70 + "\n"
        for item in analysis['review_checklist']:
            report += f"[ ] {item['priority'].upper()}: {item['category']} - {item['item']}\n"
        
        return report
    
    def generate_pr_description(self, analysis: Dict) -> str:
        """Generate a pull request description."""
        summary = analysis['summary']
        
        description = f"""## Python 2 to 3 Migration

This PR contains automated migration changes from Python 2 to Python 3.

### Summary
- Files changed: {summary['files_with_changes']} / {summary['total_files']}
- Total changes: {summary['total_changes']}
- Critical changes requiring review: {summary['critical_items']}
- Estimated review time: {summary['estimated_review_time']}

### Review Priority
{summary['recommendation']}

### Changes by Risk Level
- 🔴 High Risk: {analysis['high_risk_changes']} (requires careful review)
- 🟡 Medium Risk: {analysis['medium_risk_changes']} (should review)
- 🟢 Low Risk: {analysis['low_risk_changes']} (quick verification)

### Testing
- [ ] All existing tests pass
- [ ] Manual testing completed
- [ ] No Python 3 warnings
- [ ] Behavior matches Python 2 version

### Reviewers Checklist
"""
        for item in analysis['review_checklist']:
            if item['priority'] in ['critical', 'high']:
                description += f"- [ ] {item['item']}\n"
        
        return description


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Code Review Assistant for Python 2→3 migrations'
    )
    parser.add_argument('path', help='Path to analyze')
    parser.add_argument(
        '-f', '--format',
        choices=['markdown', 'text', 'json'],
        default='markdown',
        help='Output format'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: print to stdout)'
    )
    parser.add_argument(
        '--pr',
        action='store_true',
        help='Generate PR description instead of full report'
    )
    
    args = parser.parse_args()
    
    assistant = MigrationReviewAssistant()
    analysis = assistant.analyze_changes(args.path)
    
    if args.pr:
        report = assistant.generate_pr_description(analysis)
    else:
        report = assistant.generate_report(analysis, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
