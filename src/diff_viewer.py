#!/usr/bin/env python3
"""
Interactive HTML Diff Viewer

Generates beautiful, interactive HTML pages showing side-by-side comparisons
of Python files before and after migration. Perfect for code review, training,
and understanding the impact of migration changes.
"""

import difflib
import html
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DiffViewer:
    """Generate interactive HTML diff views for migration changes."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """Initialize the diff viewer.
        
        Args:
            backup_dir: Directory containing backup files
        """
        self.backup_dir = backup_dir or ".migration_backups"
        self.diffs = []
        self.stats = {
            'total_files': 0,
            'files_with_changes': 0,
            'total_additions': 0,
            'total_deletions': 0,
            'total_modifications': 0
        }
    
    def compare_with_backup(self, current_path: str) -> Dict:
        """Compare current file with its backup.
        
        Args:
            current_path: Path to current file
            
        Returns:
            dict: Comparison results
        """
        if not os.path.exists(current_path):
            return {'error': f'Current file not found: {current_path}'}
        
        # Find corresponding backup
        rel_path = os.path.relpath(current_path)
        backup_path = os.path.join(self.backup_dir, rel_path)
        
        if not os.path.exists(backup_path):
            return {'error': f'Backup not found: {backup_path}'}
        
        # Read files
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.readlines()
        except Exception as e:
            return {'error': f'Failed to read backup: {e}'}
        
        try:
            with open(current_path, 'r', encoding='utf-8') as f:
                current_content = f.readlines()
        except Exception as e:
            return {'error': f'Failed to read current file: {e}'}
        
        # Generate diff
        diff = list(difflib.unified_diff(
            backup_content,
            current_content,
            fromfile=f'{rel_path} (backup)',
            tofile=f'{rel_path} (current)',
            lineterm=''
        ))
        
        # Calculate statistics
        additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        has_changes = len(diff) > 0
        
        return {
            'file': current_path,
            'backup_path': backup_path,
            'backup_content': backup_content,
            'current_content': current_content,
            'diff': diff,
            'additions': additions,
            'deletions': deletions,
            'has_changes': has_changes
        }
    
    def scan_directory(self, directory: str = '.') -> List[Dict]:
        """Scan directory and compare all Python files with backups.
        
        Args:
            directory: Directory to scan
            
        Returns:
            list: List of comparison results
        """
        results = []
        
        for root, _, files in os.walk(directory):
            # Skip backup directory
            if self.backup_dir in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    result = self.compare_with_backup(file_path)
                    
                    if 'error' not in result:
                        results.append(result)
                        self.stats['total_files'] += 1
                        
                        if result['has_changes']:
                            self.stats['files_with_changes'] += 1
                            self.stats['total_additions'] += result['additions']
                            self.stats['total_deletions'] += result['deletions']
        
        return results
    
    def generate_html(self, comparisons: List[Dict], output_file: str = 'diff_viewer.html') -> str:
        """Generate interactive HTML diff viewer.
        
        Args:
            comparisons: List of comparison results
            output_file: Output HTML file path
            
        Returns:
            str: Path to generated HTML file
        """
        html_parts = [self._generate_header()]
        
        # Add summary section
        html_parts.append(self._generate_summary(comparisons))
        
        # Add navigation
        html_parts.append(self._generate_navigation(comparisons))
        
        # Add diff sections
        for idx, comparison in enumerate(comparisons):
            if comparison.get('has_changes'):
                html_parts.append(self._generate_diff_section(comparison, idx))
        
        html_parts.append(self._generate_footer())
        
        # Write to file
        html_content = '\n'.join(html_parts)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_header(self) -> str:
        """Generate HTML header with styles and scripts."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Diff Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .summary {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .summary h2 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .stat-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 1rem;
            border-radius: 4px;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        .navigation {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .navigation h3 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .file-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .file-link {
            display: flex;
            align-items: center;
            padding: 0.75rem;
            background: #f8f9fa;
            border-radius: 4px;
            text-decoration: none;
            color: #333;
            transition: all 0.2s;
            border-left: 4px solid transparent;
        }
        
        .file-link:hover {
            background: #e9ecef;
            border-left-color: #667eea;
            transform: translateX(4px);
        }
        
        .file-link .icon {
            margin-right: 0.75rem;
            font-size: 1.2rem;
        }
        
        .file-link .stats {
            margin-left: auto;
            display: flex;
            gap: 1rem;
            font-size: 0.85rem;
        }
        
        .addition {
            color: #28a745;
        }
        
        .deletion {
            color: #dc3545;
        }
        
        .diff-section {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .diff-header {
            border-bottom: 2px solid #667eea;
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .diff-header h3 {
            color: #667eea;
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        
        .diff-header .meta {
            color: #666;
            font-size: 0.9rem;
        }
        
        .diff-controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .diff-container {
            background: #f8f9fa;
            border-radius: 4px;
            overflow-x: auto;
        }
        
        .side-by-side {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1px;
            background: #dee2e6;
        }
        
        .diff-pane {
            background: #fff;
            overflow-x: auto;
        }
        
        .diff-pane h4 {
            background: #667eea;
            color: white;
            padding: 0.75rem;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .code-line {
            display: flex;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .line-number {
            background: #f8f9fa;
            color: #999;
            padding: 0.25rem 0.75rem;
            text-align: right;
            min-width: 50px;
            user-select: none;
            border-right: 1px solid #dee2e6;
        }
        
        .line-content {
            padding: 0.25rem 0.75rem;
            flex: 1;
            white-space: pre;
            overflow-x: auto;
        }
        
        .line-added {
            background: #d4edda;
        }
        
        .line-deleted {
            background: #f8d7da;
        }
        
        .line-modified {
            background: #fff3cd;
        }
        
        .unified-diff {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            padding: 1rem;
            background: #fff;
            border-radius: 4px;
        }
        
        .unified-diff .diff-line {
            line-height: 1.5;
            padding: 0.1rem 0;
        }
        
        .unified-diff .diff-add {
            background: #d4edda;
            color: #155724;
        }
        
        .unified-diff .diff-remove {
            background: #f8d7da;
            color: #721c24;
        }
        
        .unified-diff .diff-context {
            color: #666;
        }
        
        .unified-diff .diff-header {
            background: #e9ecef;
            padding: 0.25rem;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .side-by-side {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🔍 Migration Diff Viewer</h1>
            <p>Interactive side-by-side comparison of migration changes</p>
        </div>
    </div>
'''
    
    def _generate_summary(self, comparisons: List[Dict]) -> str:
        """Generate summary section."""
        files_with_changes = sum(1 for c in comparisons if c.get('has_changes'))
        total_additions = sum(c.get('additions', 0) for c in comparisons)
        total_deletions = sum(c.get('deletions', 0) for c in comparisons)
        
        return f'''
    <div class="container">
        <div class="summary">
            <h2>📊 Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="value">{len(comparisons)}</div>
                    <div class="label">Total Files Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="value">{files_with_changes}</div>
                    <div class="label">Files With Changes</div>
                </div>
                <div class="stat-card">
                    <div class="value addition">+{total_additions}</div>
                    <div class="label">Total Additions</div>
                </div>
                <div class="stat-card">
                    <div class="value deletion">-{total_deletions}</div>
                    <div class="label">Total Deletions</div>
                </div>
            </div>
        </div>
'''
    
    def _generate_navigation(self, comparisons: List[Dict]) -> str:
        """Generate navigation section."""
        nav_items = []
        
        for idx, comparison in enumerate(comparisons):
            if comparison.get('has_changes'):
                file = comparison['file']
                additions = comparison['additions']
                deletions = comparison['deletions']
                
                nav_items.append(f'''
                <a href="#file-{idx}" class="file-link">
                    <span class="icon">📄</span>
                    <span>{html.escape(file)}</span>
                    <span class="stats">
                        <span class="addition">+{additions}</span>
                        <span class="deletion">-{deletions}</span>
                    </span>
                </a>
                ''')
        
        return f'''
        <div class="navigation">
            <h3>📁 Changed Files</h3>
            <div class="file-list">
                {"".join(nav_items) if nav_items else "<p>No changes detected.</p>"}
            </div>
        </div>
    </div>
'''
    
    def _generate_diff_section(self, comparison: Dict, idx: int) -> str:
        """Generate diff section for a file."""
        file = comparison['file']
        backup_content = comparison['backup_content']
        current_content = comparison['current_content']
        additions = comparison['additions']
        deletions = comparison['deletions']
        
        # Generate side-by-side view
        side_by_side = self._generate_side_by_side(backup_content, current_content)
        
        # Generate unified diff view
        unified = self._generate_unified_diff(comparison['diff'])
        
        return f'''
    <div class="container">
        <div class="diff-section" id="file-{idx}">
            <div class="diff-header">
                <h3>📄 {html.escape(file)}</h3>
                <div class="meta">
                    <span class="addition">+{additions} additions</span> | 
                    <span class="deletion">-{deletions} deletions</span>
                </div>
            </div>
            
            <div class="diff-controls">
                <button class="btn btn-primary" onclick="showSideBySide({idx})">Side by Side</button>
                <button class="btn btn-secondary" onclick="showUnified({idx})">Unified Diff</button>
            </div>
            
            <div class="diff-container side-by-side-view" id="side-by-side-{idx}">
                {side_by_side}
            </div>
            
            <div class="diff-container unified-diff-view" id="unified-{idx}" style="display: none;">
                {unified}
            </div>
        </div>
    </div>
'''
    
    def _generate_side_by_side(self, backup_lines: List[str], current_lines: List[str]) -> str:
        """Generate side-by-side diff view."""
        diff = difflib.ndiff(backup_lines, current_lines)
        
        backup_html = ['<div class="diff-pane"><h4>Before (Backup)</h4>']
        current_html = ['<div class="diff-pane"><h4>After (Current)</h4>']
        
        backup_line_num = 0
        current_line_num = 0
        
        for line in diff:
            if line.startswith('  '):  # Unchanged
                backup_line_num += 1
                current_line_num += 1
                content = html.escape(line[2:])
                
                backup_html.append(f'''
                <div class="code-line">
                    <div class="line-number">{backup_line_num}</div>
                    <div class="line-content">{content}</div>
                </div>
                ''')
                
                current_html.append(f'''
                <div class="code-line">
                    <div class="line-number">{current_line_num}</div>
                    <div class="line-content">{content}</div>
                </div>
                ''')
            
            elif line.startswith('- '):  # Deleted
                backup_line_num += 1
                content = html.escape(line[2:])
                
                backup_html.append(f'''
                <div class="code-line line-deleted">
                    <div class="line-number">{backup_line_num}</div>
                    <div class="line-content">{content}</div>
                </div>
                ''')
            
            elif line.startswith('+ '):  # Added
                current_line_num += 1
                content = html.escape(line[2:])
                
                current_html.append(f'''
                <div class="code-line line-added">
                    <div class="line-number">{current_line_num}</div>
                    <div class="line-content">{content}</div>
                </div>
                ''')
        
        backup_html.append('</div>')
        current_html.append('</div>')
        
        return f'''
        <div class="side-by-side">
            {''.join(backup_html)}
            {''.join(current_html)}
        </div>
        '''
    
    def _generate_unified_diff(self, diff_lines: List[str]) -> str:
        """Generate unified diff view."""
        html_lines = ['<div class="unified-diff">']
        
        for line in diff_lines:
            escaped = html.escape(line)
            
            if line.startswith('+++') or line.startswith('---'):
                html_lines.append(f'<div class="diff-line diff-header">{escaped}</div>')
            elif line.startswith('+'):
                html_lines.append(f'<div class="diff-line diff-add">{escaped}</div>')
            elif line.startswith('-'):
                html_lines.append(f'<div class="diff-line diff-remove">{escaped}</div>')
            elif line.startswith('@@'):
                html_lines.append(f'<div class="diff-line diff-context"><strong>{escaped}</strong></div>')
            else:
                html_lines.append(f'<div class="diff-line diff-context">{escaped}</div>')
        
        html_lines.append('</div>')
        return ''.join(html_lines)
    
    def _generate_footer(self) -> str:
        """Generate HTML footer."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f'''
    <div class="footer">
        <p>Generated by py2to3 Migration Toolkit - {timestamp}</p>
    </div>
    
    <script>
        function showSideBySide(idx) {{
            document.getElementById('side-by-side-' + idx).style.display = 'block';
            document.getElementById('unified-' + idx).style.display = 'none';
        }}
        
        function showUnified(idx) {{
            document.getElementById('side-by-side-' + idx).style.display = 'none';
            document.getElementById('unified-' + idx).style.display = 'block';
        }}
    </script>
</body>
</html>
'''


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate interactive HTML diff viewer for migration changes'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='File or directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '-b', '--backup-dir',
        default='.migration_backups',
        help='Backup directory (default: .migration_backups)'
    )
    parser.add_argument(
        '-o', '--output',
        default='diff_viewer.html',
        help='Output HTML file (default: diff_viewer.html)'
    )
    
    args = parser.parse_args()
    
    viewer = DiffViewer(backup_dir=args.backup_dir)
    
    if os.path.isfile(args.path):
        # Single file
        result = viewer.compare_with_backup(args.path)
        if 'error' in result:
            print(f"Error: {result['error']}")
            return 1
        comparisons = [result]
    else:
        # Directory
        comparisons = viewer.scan_directory(args.path)
    
    if not comparisons:
        print("No files found to compare.")
        return 1
    
    output_file = viewer.generate_html(comparisons, args.output)
    print(f"✓ Generated interactive diff viewer: {output_file}")
    print(f"  Total files: {len(comparisons)}")
    print(f"  Files with changes: {sum(1 for c in comparisons if c.get('has_changes'))}")
    
    return 0


if __name__ == '__main__':
    exit(main())
