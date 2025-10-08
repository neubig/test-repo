#!/usr/bin/env python
"""
Python 2 to 3 Migration Report Generator
Generates comprehensive HTML reports for code migration progress and results.
"""

import datetime
import json
import os
from collections import defaultdict
from html import escape


class MigrationReportGenerator:
    """Generates HTML reports for Python 2 to 3 migration progress."""

    def __init__(self):
        self.report_data = {
            'timestamp': datetime.datetime.now(),
            'files_processed': 0,
            'fixes_applied': [],
            'issues_found': [],
            'statistics': defaultdict(int),
            'errors': []
        }

    def add_fix(self, file_path, fix_type, description, line_number=None, 
                before_code=None, after_code=None):
        """Add a fix to the report."""
        self.report_data['fixes_applied'].append({
            'file': file_path,
            'type': fix_type,
            'description': description,
            'line': line_number,
            'before': before_code,
            'after': after_code,
            'timestamp': datetime.datetime.now()
        })
        self.report_data['statistics'][fix_type] += 1

    def add_issue(self, file_path, issue_type, description, severity='warning',
                  line_number=None, code_snippet=None, suggestion=None):
        """Add an issue to the report."""
        self.report_data['issues_found'].append({
            'file': file_path,
            'type': issue_type,
            'description': description,
            'severity': severity,
            'line': line_number,
            'code': code_snippet,
            'suggestion': suggestion
        })
        self.report_data['statistics'][f'{severity}_count'] += 1

    def add_error(self, file_path, error_message):
        """Add an error to the report."""
        self.report_data['errors'].append({
            'file': file_path,
            'message': error_message,
            'timestamp': datetime.datetime.now()
        })

    def set_files_processed(self, count):
        """Set the number of files processed."""
        self.report_data['files_processed'] = count

    def generate_html_report(self, output_path='migration_report.html'):
        """Generate a comprehensive HTML report."""
        html_content = self._build_html()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def _build_html(self):
        """Build the complete HTML report."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python 2 to 3 Migration Report</title>
    {self._get_styles()}
</head>
<body>
    <div class="container">
        {self._build_header()}
        {self._build_summary()}
        {self._build_statistics()}
        {self._build_fixes_section()}
        {self._build_issues_section()}
        {self._build_errors_section()}
        {self._build_footer()}
    </div>
    {self._get_scripts()}
</body>
</html>"""

    def _build_header(self):
        """Build the report header."""
        timestamp = self.report_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        return f"""
        <header class="header">
            <h1>🐍 Python 2 to 3 Migration Report</h1>
            <p class="subtitle">Generated on {timestamp}</p>
        </header>"""

    def _build_summary(self):
        """Build the summary section."""
        total_fixes = len(self.report_data['fixes_applied'])
        total_issues = len(self.report_data['issues_found'])
        total_errors = len(self.report_data['errors'])
        files_processed = self.report_data['files_processed']
        
        error_count = self.report_data['statistics'].get('error_count', 0)
        warning_count = self.report_data['statistics'].get('warning_count', 0)
        
        # Calculate progress percentage
        if total_issues > 0:
            progress = min(100, int((total_fixes / (total_fixes + total_issues)) * 100))
        else:
            progress = 100 if total_fixes > 0 else 0

        status_class = 'success' if progress >= 80 else 'warning' if progress >= 50 else 'error'
        status_text = 'Excellent Progress' if progress >= 80 else 'Good Progress' if progress >= 50 else 'Needs Attention'

        return f"""
        <section class="summary">
            <h2>📊 Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="card-icon">📁</div>
                    <div class="card-value">{files_processed}</div>
                    <div class="card-label">Files Processed</div>
                </div>
                <div class="summary-card success">
                    <div class="card-icon">✅</div>
                    <div class="card-value">{total_fixes}</div>
                    <div class="card-label">Fixes Applied</div>
                </div>
                <div class="summary-card warning">
                    <div class="card-icon">⚠️</div>
                    <div class="card-value">{total_issues}</div>
                    <div class="card-label">Issues Found</div>
                </div>
                <div class="summary-card error">
                    <div class="card-icon">❌</div>
                    <div class="card-value">{total_errors}</div>
                    <div class="card-label">Errors</div>
                </div>
            </div>
            <div class="progress-section">
                <div class="progress-header">
                    <h3>Migration Progress</h3>
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%"></div>
                </div>
                <p class="progress-text">{progress}% Complete</p>
            </div>
        </section>"""

    def _build_statistics(self):
        """Build the statistics section with charts."""
        stats = self.report_data['statistics']
        
        # Group fixes by type
        fix_types = defaultdict(int)
        for fix in self.report_data['fixes_applied']:
            fix_types[fix['type']] += 1
        
        # Create chart data
        chart_data = []
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', 
                  '#00BCD4', '#FFEB3B', '#795548', '#607D8B', '#E91E63']
        
        for i, (fix_type, count) in enumerate(sorted(fix_types.items(), 
                                                      key=lambda x: x[1], 
                                                      reverse=True)):
            chart_data.append({
                'type': fix_type,
                'count': count,
                'color': colors[i % len(colors)]
            })
        
        chart_items = '\n'.join([
            f'<div class="chart-item" style="flex-grow: {item["count"]}">'
            f'<div class="chart-bar" style="background-color: {item["color"]}"></div>'
            f'<div class="chart-label">{escape(item["type"])}: {item["count"]}</div>'
            f'</div>'
            for item in chart_data
        ])
        
        stats_table = '\n'.join([
            f'<tr><td class="stat-name">{escape(fix_type)}</td>'
            f'<td class="stat-value">{count}</td></tr>'
            for fix_type, count in sorted(fix_types.items(), 
                                          key=lambda x: x[1], 
                                          reverse=True)
        ])
        
        return f"""
        <section class="statistics">
            <h2>📈 Statistics</h2>
            <div class="chart-container">
                <h3>Fixes by Type</h3>
                <div class="chart">
                    {chart_items if chart_items else '<p class="empty-message">No fixes applied yet</p>'}
                </div>
            </div>
            <div class="stats-table-container">
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Fix Type</th>
                            <th>Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {stats_table if stats_table else '<tr><td colspan="2" class="empty-message">No statistics available</td></tr>'}
                    </tbody>
                </table>
            </div>
        </section>"""

    def _build_fixes_section(self):
        """Build the fixes section with code comparisons."""
        fixes = self.report_data['fixes_applied']
        
        if not fixes:
            return """
            <section class="fixes">
                <h2>✅ Fixes Applied</h2>
                <p class="empty-message">No fixes have been applied yet.</p>
            </section>"""
        
        # Group fixes by file
        fixes_by_file = defaultdict(list)
        for fix in fixes:
            fixes_by_file[fix['file']].append(fix)
        
        fixes_html = []
        for file_path, file_fixes in sorted(fixes_by_file.items()):
            fixes_html.append(f'<div class="file-section">')
            fixes_html.append(f'<h3 class="file-name">📄 {escape(file_path)}</h3>')
            fixes_html.append(f'<p class="fix-count">{len(file_fixes)} fix(es) applied</p>')
            
            for fix in file_fixes:
                line_info = f' (Line {fix["line"]})' if fix['line'] else ''
                fixes_html.append(f'<div class="fix-item">')
                fixes_html.append(f'<div class="fix-header">')
                fixes_html.append(f'<span class="fix-type">{escape(fix["type"])}</span>')
                fixes_html.append(f'<span class="fix-line">{line_info}</span>')
                fixes_html.append(f'</div>')
                fixes_html.append(f'<p class="fix-description">{escape(fix["description"])}</p>')
                
                if fix['before'] or fix['after']:
                    fixes_html.append(f'<div class="code-comparison">')
                    if fix['before']:
                        fixes_html.append(f'<div class="code-before">')
                        fixes_html.append(f'<div class="code-label">Before:</div>')
                        fixes_html.append(f'<pre><code>{escape(fix["before"])}</code></pre>')
                        fixes_html.append(f'</div>')
                    if fix['after']:
                        fixes_html.append(f'<div class="code-after">')
                        fixes_html.append(f'<div class="code-label">After:</div>')
                        fixes_html.append(f'<pre><code>{escape(fix["after"])}</code></pre>')
                        fixes_html.append(f'</div>')
                    fixes_html.append(f'</div>')
                
                fixes_html.append(f'</div>')
            
            fixes_html.append(f'</div>')
        
        return f"""
        <section class="fixes">
            <h2>✅ Fixes Applied</h2>
            {''.join(fixes_html)}
        </section>"""

    def _build_issues_section(self):
        """Build the issues section."""
        issues = self.report_data['issues_found']
        
        if not issues:
            return """
            <section class="issues">
                <h2>⚠️ Remaining Issues</h2>
                <p class="empty-message success-message">✨ Great! No issues found.</p>
            </section>"""
        
        # Group issues by severity
        errors = [i for i in issues if i['severity'] == 'error']
        warnings = [i for i in issues if i['severity'] == 'warning']
        
        issues_html = []
        
        if errors:
            issues_html.append('<h3 class="issue-category error">❌ Errors ({})'.format(len(errors)))
            issues_html.append('</h3>')
            for issue in errors:
                issues_html.append(self._format_issue(issue, 'error'))
        
        if warnings:
            issues_html.append('<h3 class="issue-category warning">⚠️ Warnings ({})'.format(len(warnings)))
            issues_html.append('</h3>')
            for issue in warnings:
                issues_html.append(self._format_issue(issue, 'warning'))
        
        return f"""
        <section class="issues">
            <h2>⚠️ Remaining Issues</h2>
            {''.join(issues_html)}
        </section>"""

    def _format_issue(self, issue, severity_class):
        """Format a single issue."""
        line_info = f' (Line {issue["line"]})' if issue['line'] else ''
        code_html = ''
        if issue['code']:
            code_html = f'''
            <div class="issue-code">
                <div class="code-label">Code:</div>
                <pre><code>{escape(issue["code"])}</code></pre>
            </div>'''
        
        suggestion_html = ''
        if issue['suggestion']:
            suggestion_html = f'''
            <div class="issue-suggestion">
                <div class="suggestion-label">💡 Suggestion:</div>
                <p>{escape(issue["suggestion"])}</p>
            </div>'''
        
        return f'''
        <div class="issue-item {severity_class}">
            <div class="issue-header">
                <span class="issue-file">📄 {escape(issue["file"])}{line_info}</span>
                <span class="issue-type">{escape(issue["type"])}</span>
            </div>
            <p class="issue-description">{escape(issue["description"])}</p>
            {code_html}
            {suggestion_html}
        </div>'''

    def _build_errors_section(self):
        """Build the errors section."""
        errors = self.report_data['errors']
        
        if not errors:
            return ''
        
        errors_html = []
        for error in errors:
            timestamp = error['timestamp'].strftime('%H:%M:%S')
            errors_html.append(f'''
            <div class="error-item">
                <div class="error-header">
                    <span class="error-file">📄 {escape(error["file"])}</span>
                    <span class="error-time">{timestamp}</span>
                </div>
                <pre class="error-message">{escape(error["message"])}</pre>
            </div>''')
        
        return f"""
        <section class="errors">
            <h2>❌ Errors</h2>
            {''.join(errors_html)}
        </section>"""

    def _build_footer(self):
        """Build the report footer."""
        return """
        <footer class="footer">
            <p>Generated by Python 2 to 3 Migration Report Generator</p>
            <p>For more information, see the project documentation</p>
        </footer>"""

    def _get_styles(self):
        """Get the CSS styles for the report."""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }

        section {
            padding: 40px;
            border-bottom: 1px solid #e0e0e0;
        }

        section:last-of-type {
            border-bottom: none;
        }

        h2 {
            font-size: 2em;
            margin-bottom: 20px;
            color: #333;
        }

        h3 {
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #555;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .summary-card {
            background: #f5f5f5;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            transition: transform 0.2s;
        }

        .summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .summary-card.success {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
        }

        .summary-card.warning {
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
            color: white;
        }

        .summary-card.error {
            background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
            color: white;
        }

        .card-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .card-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .card-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .progress-section {
            background: #f9f9f9;
            padding: 25px;
            border-radius: 8px;
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }

        .status-badge.success {
            background: #4CAF50;
            color: white;
        }

        .status-badge.warning {
            background: #FF9800;
            color: white;
        }

        .status-badge.error {
            background: #F44336;
            color: white;
        }

        .progress-bar {
            background: #e0e0e0;
            border-radius: 20px;
            height: 30px;
            overflow: hidden;
            margin-bottom: 10px;
        }

        .progress-fill {
            background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
            height: 100%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }

        .progress-text {
            text-align: center;
            font-weight: bold;
            color: #555;
        }

        .chart-container {
            margin-bottom: 30px;
        }

        .chart {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .chart-item {
            min-width: 150px;
            text-align: center;
        }

        .chart-bar {
            height: 100px;
            border-radius: 4px;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }

        .chart-bar:hover {
            transform: scaleY(1.1);
        }

        .chart-label {
            font-size: 0.9em;
            color: #666;
        }

        .stats-table-container {
            overflow-x: auto;
        }

        .stats-table {
            width: 100%;
            border-collapse: collapse;
        }

        .stats-table th,
        .stats-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }

        .stats-table th {
            background: #f5f5f5;
            font-weight: bold;
        }

        .stat-name {
            color: #555;
        }

        .stat-value {
            font-weight: bold;
            color: #667eea;
        }

        .file-section {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .file-name {
            color: #667eea;
            margin-bottom: 5px;
        }

        .fix-count {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }

        .fix-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #4CAF50;
        }

        .fix-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .fix-type {
            background: #4CAF50;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .fix-line {
            color: #666;
            font-size: 0.9em;
        }

        .fix-description {
            color: #555;
            margin-bottom: 10px;
        }

        .code-comparison {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }

        .code-before,
        .code-after {
            background: #f5f5f5;
            border-radius: 4px;
            overflow: hidden;
        }

        .code-label {
            background: #333;
            color: white;
            padding: 8px 12px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .code-before .code-label {
            background: #F44336;
        }

        .code-after .code-label {
            background: #4CAF50;
        }

        pre {
            margin: 0;
            padding: 12px;
            overflow-x: auto;
        }

        code {
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }

        .issue-category {
            margin-top: 20px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid currentColor;
        }

        .issue-category.error {
            color: #F44336;
        }

        .issue-category.warning {
            color: #FF9800;
        }

        .issue-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #FF9800;
        }

        .issue-item.error {
            border-left-color: #F44336;
            background: #ffebee;
        }

        .issue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }

        .issue-file {
            color: #333;
            font-weight: bold;
        }

        .issue-type {
            background: #FF9800;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .issue-item.error .issue-type {
            background: #F44336;
        }

        .issue-description {
            color: #555;
            margin-bottom: 10px;
        }

        .issue-code {
            margin-top: 10px;
        }

        .issue-code .code-label {
            background: #666;
            color: white;
            padding: 6px 10px;
            font-size: 0.85em;
            font-weight: bold;
            display: inline-block;
            border-radius: 4px 4px 0 0;
        }

        .issue-suggestion {
            margin-top: 10px;
            background: #e3f2fd;
            padding: 12px;
            border-radius: 4px;
            border-left: 3px solid #2196F3;
        }

        .suggestion-label {
            font-weight: bold;
            color: #1976D2;
            margin-bottom: 5px;
        }

        .error-item {
            background: #ffebee;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #F44336;
        }

        .error-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .error-file {
            font-weight: bold;
            color: #333;
        }

        .error-time {
            color: #666;
            font-size: 0.9em;
        }

        .error-message {
            background: white;
            padding: 12px;
            border-radius: 4px;
            color: #D32F2F;
            overflow-x: auto;
        }

        .empty-message {
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }

        .success-message {
            color: #4CAF50;
            font-weight: bold;
        }

        .footer {
            background: #f5f5f5;
            padding: 30px;
            text-align: center;
            color: #666;
        }

        .footer p {
            margin: 5px 0;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            section {
                padding: 20px;
            }

            .summary-grid {
                grid-template-columns: 1fr;
            }

            .code-comparison {
                grid-template-columns: 1fr;
            }
        }
    </style>"""

    def _get_scripts(self):
        """Get JavaScript for interactive features."""
        return """
    <script>
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Animate progress bar on load
        window.addEventListener('load', function() {
            const progressFill = document.querySelector('.progress-fill');
            if (progressFill) {
                const width = progressFill.style.width;
                progressFill.style.width = '0%';
                setTimeout(() => {
                    progressFill.style.width = width;
                }, 100);
            }
        });
    </script>"""

    def export_json(self, output_path='migration_report.json'):
        """Export report data as JSON."""
        # Convert datetime objects to strings
        data = {
            'timestamp': self.report_data['timestamp'].isoformat(),
            'files_processed': self.report_data['files_processed'],
            'total_fixes': len(self.report_data['fixes_applied']),
            'total_issues': len(self.report_data['issues_found']),
            'total_errors': len(self.report_data['errors']),
            'statistics': dict(self.report_data['statistics']),
            'fixes_applied': [
                {**fix, 'timestamp': fix['timestamp'].isoformat()}
                for fix in self.report_data['fixes_applied']
            ],
            'issues_found': self.report_data['issues_found'],
            'errors': [
                {**error, 'timestamp': error['timestamp'].isoformat()}
                for error in self.report_data['errors']
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path


def main():
    """Example usage of the report generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate HTML reports for Python 2 to 3 migration'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Input JSON file with migration data (optional)'
    )
    parser.add_argument(
        '-o', '--output',
        default='migration_report.html',
        help='Output HTML file path (default: migration_report.html)'
    )
    parser.add_argument(
        '--json',
        help='Also export data as JSON to specified file'
    )
    
    args = parser.parse_args()
    
    generator = MigrationReportGenerator()
    
    # If input file provided, load data from it
    if args.input and os.path.exists(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Load data into generator
            generator.report_data = data
    else:
        # Demo data
        generator.set_files_processed(10)
        generator.add_fix(
            'core/main.py', 
            'print_statements',
            'Converted print statement to print() function',
            line_number=42,
            before_code='print "Hello World"',
            after_code='print("Hello World")'
        )
        generator.add_fix(
            'web/scraper.py',
            'urllib2_imports',
            'Updated urllib2 import to urllib.request',
            line_number=3,
            before_code='import urllib2',
            after_code='import urllib.request as urllib2'
        )
        generator.add_issue(
            'data/processor.py',
            'basestring_usage',
            'basestring is not defined in Python 3',
            severity='error',
            line_number=67,
            code_snippet='if isinstance(value, basestring):',
            suggestion='Replace basestring with str'
        )
    
    # Generate HTML report
    output_file = generator.generate_html_report(args.output)
    print(f'✅ HTML report generated: {output_file}')
    
    # Export JSON if requested
    if args.json:
        json_file = generator.export_json(args.json)
        print(f'✅ JSON data exported: {json_file}')


if __name__ == '__main__':
    main()
