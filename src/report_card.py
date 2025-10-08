#!/usr/bin/env python3
"""
Migration Report Card Generator

Generates a comprehensive quality assessment of Python 2 to 3 migration.
Provides letter grades and actionable recommendations for improvement.
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class MigrationReportCard:
    """Generate quality assessments for Python 2 to 3 migrations."""
    
    GRADE_THRESHOLDS = {
        'A': 90,
        'B': 80,
        'C': 70,
        'D': 60,
        'F': 0
    }
    
    def __init__(self, project_path='.'):
        """Initialize the report card generator.
        
        Args:
            project_path: Path to the project being assessed
        """
        self.project_path = Path(project_path).resolve()
        self.scores = {}
        self.recommendations = []
        self.metrics = {}
        
    def generate_report_card(self, output_format='text'):
        """Generate a comprehensive migration report card.
        
        Args:
            output_format: Output format ('text', 'html', 'json', 'markdown')
            
        Returns:
            str: Formatted report card
        """
        self._calculate_all_scores()
        
        if output_format == 'json':
            return self._format_json()
        elif output_format == 'html':
            return self._format_html()
        elif output_format == 'markdown':
            return self._format_markdown()
        else:
            return self._format_text()
    
    def _calculate_all_scores(self):
        """Calculate scores for all assessment categories."""
        self.scores['compatibility'] = self._assess_compatibility()
        self.scores['modernization'] = self._assess_modernization()
        self.scores['code_quality'] = self._assess_code_quality()
        self.scores['test_coverage'] = self._assess_test_coverage()
        self.scores['documentation'] = self._assess_documentation()
        self.scores['best_practices'] = self._assess_best_practices()
        
        # Calculate overall score
        weights = {
            'compatibility': 0.30,
            'modernization': 0.20,
            'code_quality': 0.20,
            'test_coverage': 0.15,
            'documentation': 0.10,
            'best_practices': 0.05
        }
        
        self.scores['overall'] = sum(
            self.scores[cat] * weight 
            for cat, weight in weights.items()
        )
    
    def _assess_compatibility(self):
        """Assess Python 3 compatibility.
        
        Returns:
            float: Score from 0-100
        """
        try:
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            
            # Count Python files
            py_files = list(self.project_path.rglob('*.py'))
            total_files = len([f for f in py_files if not self._should_skip(f)])
            
            if total_files == 0:
                self.recommendations.append({
                    'category': 'compatibility',
                    'severity': 'info',
                    'message': 'No Python files found to assess'
                })
                return 100.0
            
            # Verify directory
            for file in py_files:
                if not self._should_skip(file):
                    try:
                        verifier.verify_file(str(file))
                    except:
                        pass
            
            issues = verifier.issues_found
            
            # Calculate score based on issues
            critical_issues = sum(1 for i in issues if i.get('severity') == 'critical')
            high_issues = sum(1 for i in issues if i.get('severity') == 'high')
            medium_issues = sum(1 for i in issues if i.get('severity') == 'medium')
            low_issues = sum(1 for i in issues if i.get('severity') == 'low')
            
            # Weight issues by severity
            issue_score = (
                critical_issues * 10 +
                high_issues * 5 +
                medium_issues * 2 +
                low_issues * 1
            )
            
            # Calculate score (max deduction of 100 points)
            score = max(0, 100 - (issue_score * 2))
            
            self.metrics['compatibility'] = {
                'total_files': total_files,
                'issues': {
                    'critical': critical_issues,
                    'high': high_issues,
                    'medium': medium_issues,
                    'low': low_issues
                }
            }
            
            # Add recommendations
            if critical_issues > 0:
                self.recommendations.append({
                    'category': 'compatibility',
                    'severity': 'critical',
                    'message': f'Fix {critical_issues} critical compatibility issues immediately'
                })
            if high_issues > 5:
                self.recommendations.append({
                    'category': 'compatibility',
                    'severity': 'high',
                    'message': f'Address {high_issues} high-priority compatibility issues'
                })
            
            return score
            
        except Exception as e:
            self.recommendations.append({
                'category': 'compatibility',
                'severity': 'error',
                'message': f'Failed to assess compatibility: {str(e)}'
            })
            return 50.0
    
    def _assess_modernization(self):
        """Assess use of modern Python 3 features.
        
        Returns:
            float: Score from 0-100
        """
        py_files = list(self.project_path.rglob('*.py'))
        py_files = [f for f in py_files if not self._should_skip(f)]
        
        if not py_files:
            return 100.0
        
        modern_features = {
            'f-strings': 0,
            'type_hints': 0,
            'pathlib': 0,
            'dataclasses': 0,
            'async_await': 0,
            'walrus_operator': 0
        }
        
        for file in py_files:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for modern features
                if "f'" in content or 'f"' in content:
                    modern_features['f-strings'] += 1
                if '->' in content or ': ' in content and 'def ' in content:
                    modern_features['type_hints'] += 1
                if 'from pathlib import' in content or 'import pathlib' in content:
                    modern_features['pathlib'] += 1
                if '@dataclass' in content:
                    modern_features['dataclasses'] += 1
                if 'async def' in content or 'await ' in content:
                    modern_features['async_await'] += 1
                if ':=' in content:
                    modern_features['walrus_operator'] += 1
                    
            except:
                pass
        
        # Calculate score based on modern feature usage
        total_possible = len(modern_features) * len(py_files)
        total_used = sum(modern_features.values())
        
        score = (total_used / total_possible * 100) if total_possible > 0 else 50.0
        
        self.metrics['modernization'] = modern_features
        
        # Add recommendations
        if modern_features['f-strings'] < len(py_files) * 0.3:
            self.recommendations.append({
                'category': 'modernization',
                'severity': 'medium',
                'message': 'Consider using f-strings instead of .format() or % formatting'
            })
        if modern_features['type_hints'] < len(py_files) * 0.2:
            self.recommendations.append({
                'category': 'modernization',
                'severity': 'medium',
                'message': 'Add type hints to improve code quality and IDE support'
            })
        if modern_features['pathlib'] == 0:
            self.recommendations.append({
                'category': 'modernization',
                'severity': 'low',
                'message': 'Consider using pathlib.Path instead of os.path for path operations'
            })
        
        return min(100.0, score + 30)  # Boost score as these are nice-to-haves
    
    def _assess_code_quality(self):
        """Assess overall code quality.
        
        Returns:
            float: Score from 0-100
        """
        py_files = list(self.project_path.rglob('*.py'))
        py_files = [f for f in py_files if not self._should_skip(f)]
        
        if not py_files:
            return 100.0
        
        quality_metrics = {
            'has_docstrings': 0,
            'reasonable_length': 0,
            'no_todos': 0,
            'good_naming': 0
        }
        
        for file in py_files:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                # Check for docstrings
                if '"""' in content or "'''" in content:
                    quality_metrics['has_docstrings'] += 1
                
                # Check file length (not too long)
                if len(lines) < 500:
                    quality_metrics['reasonable_length'] += 1
                
                # Check for TODOs (fewer is better)
                if 'TODO' not in content.upper() and 'FIXME' not in content.upper():
                    quality_metrics['no_todos'] += 1
                
                # Check for good naming (no single letter vars in function names)
                if not any(f'def {c}(' in content for c in 'abcdefghijklmnopqrstuvwxyz'):
                    quality_metrics['good_naming'] += 1
                    
            except:
                pass
        
        # Calculate score
        total_checks = len(quality_metrics) * len(py_files)
        passed_checks = sum(quality_metrics.values())
        
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 75.0
        
        self.metrics['code_quality'] = quality_metrics
        
        # Add recommendations
        if quality_metrics['has_docstrings'] < len(py_files) * 0.5:
            self.recommendations.append({
                'category': 'code_quality',
                'severity': 'medium',
                'message': 'Add docstrings to modules, classes, and functions'
            })
        
        return score
    
    def _assess_test_coverage(self):
        """Assess test coverage.
        
        Returns:
            float: Score from 0-100
        """
        # Count source files
        src_files = []
        test_files = []
        
        for file in self.project_path.rglob('*.py'):
            if self._should_skip(file):
                continue
            
            if 'test' in file.name.lower() or 'test' in str(file.parent).lower():
                test_files.append(file)
            else:
                src_files.append(file)
        
        if not src_files:
            return 100.0
        
        # Simple heuristic: ratio of test files to source files
        test_ratio = len(test_files) / len(src_files) if src_files else 0
        
        # Score based on test ratio (ideal is 1:1 or better)
        score = min(100, test_ratio * 100)
        
        self.metrics['test_coverage'] = {
            'source_files': len(src_files),
            'test_files': len(test_files),
            'ratio': f"{test_ratio:.2f}"
        }
        
        # Add recommendations
        if test_ratio < 0.3:
            self.recommendations.append({
                'category': 'test_coverage',
                'severity': 'high',
                'message': f'Only {len(test_files)} test files for {len(src_files)} source files. Add more tests!'
            })
        elif test_ratio < 0.6:
            self.recommendations.append({
                'category': 'test_coverage',
                'severity': 'medium',
                'message': f'Test coverage could be improved ({len(test_files)}/{len(src_files)} ratio)'
            })
        
        return score
    
    def _assess_documentation(self):
        """Assess documentation quality.
        
        Returns:
            float: Score from 0-100
        """
        doc_files = []
        expected_docs = ['README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'LICENSE']
        
        found_docs = []
        for doc in expected_docs:
            if (self.project_path / doc).exists():
                found_docs.append(doc)
        
        # Check for other markdown files
        md_files = list(self.project_path.glob('*.md'))
        
        # Calculate score
        base_score = (len(found_docs) / len(expected_docs)) * 60  # 60% for essential docs
        bonus_score = min(40, len(md_files) * 5)  # Up to 40% for additional docs
        
        score = base_score + bonus_score
        
        self.metrics['documentation'] = {
            'essential_docs': found_docs,
            'total_markdown': len(md_files)
        }
        
        # Add recommendations
        missing_docs = [d for d in expected_docs if d not in found_docs]
        if missing_docs:
            self.recommendations.append({
                'category': 'documentation',
                'severity': 'medium',
                'message': f'Add missing documentation: {", ".join(missing_docs)}'
            })
        
        return score
    
    def _assess_best_practices(self):
        """Assess adherence to best practices.
        
        Returns:
            float: Score from 0-100
        """
        checks = {
            'has_gitignore': (self.project_path / '.gitignore').exists(),
            'has_requirements': (self.project_path / 'requirements.txt').exists() or 
                               (self.project_path / 'setup.py').exists() or
                               (self.project_path / 'pyproject.toml').exists(),
            'has_tests_dir': (self.project_path / 'tests').exists() or 
                            (self.project_path / 'test').exists(),
            'has_config': (self.project_path / '.py2to3.config.json').exists() or
                         (self.project_path / 'setup.cfg').exists(),
            'no_cache_files': not any(self.project_path.rglob('*.pyc'))
        }
        
        score = (sum(checks.values()) / len(checks)) * 100
        
        self.metrics['best_practices'] = checks
        
        # Add recommendations
        if not checks['has_gitignore']:
            self.recommendations.append({
                'category': 'best_practices',
                'severity': 'low',
                'message': 'Add a .gitignore file to exclude unnecessary files'
            })
        if not checks['has_requirements']:
            self.recommendations.append({
                'category': 'best_practices',
                'severity': 'medium',
                'message': 'Add requirements.txt or setup.py to track dependencies'
            })
        
        return score
    
    def _should_skip(self, path):
        """Check if path should be skipped.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if should skip
        """
        skip_patterns = [
            'venv', 'env', '.env', 'node_modules', '__pycache__',
            '.git', '.pytest_cache', '.tox', 'build', 'dist',
            '.eggs', '*.egg-info', 'my-vite-app'
        ]
        
        path_str = str(path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _get_letter_grade(self, score):
        """Convert numeric score to letter grade.
        
        Args:
            score: Numeric score (0-100)
            
        Returns:
            str: Letter grade
        """
        for grade, threshold in self.GRADE_THRESHOLDS.items():
            if score >= threshold:
                return grade
        return 'F'
    
    def _format_text(self):
        """Format report card as plain text.
        
        Returns:
            str: Formatted text report
        """
        lines = []
        lines.append("=" * 70)
        lines.append("PYTHON 2 TO 3 MIGRATION REPORT CARD")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Project: {self.project_path.name}")
        lines.append("")
        
        # Overall grade
        overall_grade = self._get_letter_grade(self.scores['overall'])
        lines.append(f"OVERALL GRADE: {overall_grade} ({self.scores['overall']:.1f}/100)")
        lines.append("")
        
        # Category scores
        lines.append("CATEGORY SCORES:")
        lines.append("-" * 70)
        
        categories = [
            ('compatibility', 'Python 3 Compatibility', 30),
            ('modernization', 'Modern Python 3 Features', 20),
            ('code_quality', 'Code Quality', 20),
            ('test_coverage', 'Test Coverage', 15),
            ('documentation', 'Documentation', 10),
            ('best_practices', 'Best Practices', 5)
        ]
        
        for key, name, weight in categories:
            score = self.scores[key]
            grade = self._get_letter_grade(score)
            lines.append(f"{name:.<40} {grade} ({score:.1f}/100) [{weight}% weight]")
        
        lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.append("RECOMMENDATIONS:")
            lines.append("-" * 70)
            
            # Group by severity
            by_severity = defaultdict(list)
            for rec in self.recommendations:
                by_severity[rec['severity']].append(rec)
            
            for severity in ['critical', 'high', 'medium', 'low', 'info', 'error']:
                if severity in by_severity:
                    lines.append(f"\n{severity.upper()}:")
                    for rec in by_severity[severity]:
                        lines.append(f"  • [{rec['category']}] {rec['message']}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_markdown(self):
        """Format report card as markdown.
        
        Returns:
            str: Formatted markdown report
        """
        lines = []
        lines.append("# Python 2 to 3 Migration Report Card")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Project:** {self.project_path.name}")
        lines.append("")
        
        # Overall grade
        overall_grade = self._get_letter_grade(self.scores['overall'])
        lines.append(f"## Overall Grade: {overall_grade}")
        lines.append(f"**Score:** {self.scores['overall']:.1f}/100")
        lines.append("")
        
        # Category scores
        lines.append("## Category Scores")
        lines.append("")
        lines.append("| Category | Grade | Score | Weight |")
        lines.append("|----------|-------|-------|--------|")
        
        categories = [
            ('compatibility', 'Python 3 Compatibility', 30),
            ('modernization', 'Modern Python 3 Features', 20),
            ('code_quality', 'Code Quality', 20),
            ('test_coverage', 'Test Coverage', 15),
            ('documentation', 'Documentation', 10),
            ('best_practices', 'Best Practices', 5)
        ]
        
        for key, name, weight in categories:
            score = self.scores[key]
            grade = self._get_letter_grade(score)
            lines.append(f"| {name} | {grade} | {score:.1f}/100 | {weight}% |")
        
        lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            
            # Group by severity
            by_severity = defaultdict(list)
            for rec in self.recommendations:
                by_severity[rec['severity']].append(rec)
            
            for severity in ['critical', 'high', 'medium', 'low', 'info', 'error']:
                if severity in by_severity:
                    emoji = {
                        'critical': '🔴',
                        'high': '🟠', 
                        'medium': '🟡',
                        'low': '🔵',
                        'info': 'ℹ️',
                        'error': '❌'
                    }.get(severity, '•')
                    
                    lines.append(f"### {emoji} {severity.upper()}")
                    lines.append("")
                    for rec in by_severity[severity]:
                        lines.append(f"- **[{rec['category']}]** {rec['message']}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _format_html(self):
        """Format report card as HTML.
        
        Returns:
            str: Formatted HTML report
        """
        overall_grade = self._get_letter_grade(self.scores['overall'])
        
        # Grade colors
        grade_colors = {
            'A': '#4CAF50',
            'B': '#8BC34A',
            'C': '#FFC107',
            'D': '#FF9800',
            'F': '#F44336'
        }
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Migration Report Card</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
        }}
        .overall-grade {{
            text-align: center;
            margin: 30px 0;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
        }}
        .grade-letter {{
            font-size: 72px;
            font-weight: bold;
            margin: 0;
        }}
        .grade-score {{
            font-size: 24px;
            margin: 10px 0 0 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #2196F3;
            color: white;
        }}
        .grade-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }}
        .recommendations {{
            margin-top: 30px;
        }}
        .rec-item {{
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .rec-critical {{ border-color: #F44336; }}
        .rec-high {{ border-color: #FF9800; }}
        .rec-medium {{ border-color: #FFC107; }}
        .rec-low {{ border-color: #2196F3; }}
        .rec-info {{ border-color: #9E9E9E; }}
        .rec-category {{
            font-weight: bold;
            color: #666;
        }}
        .meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Python 2 to 3 Migration Report Card</h1>
        <div class="meta">
            <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Project:</strong> {self.project_path.name}
        </div>
        
        <div class="overall-grade">
            <p class="grade-letter">{overall_grade}</p>
            <p class="grade-score">{self.scores['overall']:.1f} / 100</p>
        </div>
        
        <h2>📊 Category Scores</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Grade</th>
                <th>Score</th>
                <th>Weight</th>
            </tr>
"""
        
        categories = [
            ('compatibility', 'Python 3 Compatibility', 30),
            ('modernization', 'Modern Python 3 Features', 20),
            ('code_quality', 'Code Quality', 20),
            ('test_coverage', 'Test Coverage', 15),
            ('documentation', 'Documentation', 10),
            ('best_practices', 'Best Practices', 5)
        ]
        
        for key, name, weight in categories:
            score = self.scores[key]
            grade = self._get_letter_grade(score)
            color = grade_colors.get(grade, '#999')
            html += f"""
            <tr>
                <td>{name}</td>
                <td><span class="grade-badge" style="background: {color}">{grade}</span></td>
                <td>{score:.1f}/100</td>
                <td>{weight}%</td>
            </tr>
"""
        
        html += """
        </table>
"""
        
        # Recommendations
        if self.recommendations:
            html += """
        <h2>💡 Recommendations</h2>
        <div class="recommendations">
"""
            
            # Group by severity
            by_severity = defaultdict(list)
            for rec in self.recommendations:
                by_severity[rec['severity']].append(rec)
            
            severity_icons = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🔵',
                'info': 'ℹ️',
                'error': '❌'
            }
            
            for severity in ['critical', 'high', 'medium', 'low', 'info', 'error']:
                if severity in by_severity:
                    for rec in by_severity[severity]:
                        icon = severity_icons.get(severity, '•')
                        html += f"""
            <div class="rec-item rec-{severity}">
                {icon} <span class="rec-category">[{rec['category']}]</span> {rec['message']}
            </div>
"""
            
            html += """
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    def _format_json(self):
        """Format report card as JSON.
        
        Returns:
            str: Formatted JSON report
        """
        report = {
            'generated': datetime.now().isoformat(),
            'project': self.project_path.name,
            'overall': {
                'score': round(self.scores['overall'], 2),
                'grade': self._get_letter_grade(self.scores['overall'])
            },
            'categories': {},
            'metrics': self.metrics,
            'recommendations': self.recommendations
        }
        
        categories = [
            ('compatibility', 'Python 3 Compatibility', 30),
            ('modernization', 'Modern Python 3 Features', 20),
            ('code_quality', 'Code Quality', 20),
            ('test_coverage', 'Test Coverage', 15),
            ('documentation', 'Documentation', 10),
            ('best_practices', 'Best Practices', 5)
        ]
        
        for key, name, weight in categories:
            report['categories'][key] = {
                'name': name,
                'score': round(self.scores[key], 2),
                'grade': self._get_letter_grade(self.scores[key]),
                'weight': weight
            }
        
        return json.dumps(report, indent=2)
    
    def save_report(self, output_path, output_format='text'):
        """Generate and save report card to file.
        
        Args:
            output_path: Path to save report
            output_format: Format ('text', 'html', 'json', 'markdown')
        """
        report = self.generate_report_card(output_format)
        
        output_path = Path(output_path)
        output_path.write_text(report, encoding='utf-8')
        
        return output_path


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate a quality assessment report card for Python 2 to 3 migration'
    )
    parser.add_argument(
        'project_path',
        nargs='?',
        default='.',
        help='Path to project to assess (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'html', 'json', 'markdown'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Generate report card
    card = MigrationReportCard(args.project_path)
    
    if args.output:
        card.save_report(args.output, args.format)
        print(f"Report card saved to: {args.output}")
    else:
        report = card.generate_report_card(args.format)
        print(report)


if __name__ == '__main__':
    main()
