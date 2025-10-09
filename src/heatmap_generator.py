"""
Migration Heatmap Generator

Creates interactive visual heatmaps of the codebase showing:
- Migration status by file
- Risk levels and complexity
- File sizes and issue counts
- Interactive HTML treemap visualization

Perfect for:
- Quickly identifying problem areas
- Prioritizing migration work
- Presenting progress to stakeholders
- Understanding codebase structure at a glance
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class HeatmapGenerator:
    """Generate interactive heatmap visualizations of migration status."""
    
    def __init__(self, target_dir: str = "."):
        self.target_dir = Path(target_dir).resolve()
        self.file_data = []
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'migrated': 0,
            'in_progress': 0,
            'not_started': 0,
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0
        }
    
    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a Python file for migration status and complexity."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.count('\n') + 1
            file_size = len(content)
            
            # Check for Python 2 patterns
            py2_patterns = {
                'print_statement': content.count('print ') - content.count('print('),
                'old_imports': any(imp in content for imp in ['urllib2', 'ConfigParser', 'Queue', 'cPickle']),
                'unicode_literals': 'unicode' in content and 'unicode(' in content,
                'iteritems': '.iteritems()' in content,
                'xrange': 'xrange(' in content,
                'old_exception': 'except Exception, ' in content,
                'basestring': 'basestring' in content,
                'long_type': ' long(' in content or ' long ' in content,
                'has_key': '.has_key(' in content,
                'old_division': 'from __future__ import division' not in content
            }
            
            issues_count = sum(1 for v in py2_patterns.values() if v)
            
            # Determine migration status
            if issues_count == 0:
                status = 'completed'
                color = '#10b981'  # green
            elif issues_count <= 2:
                status = 'in_progress'
                color = '#f59e0b'  # amber
            else:
                status = 'not_started'
                color = '#ef4444'  # red
            
            # Calculate complexity score
            try:
                tree = ast.parse(content)
                complexity = self._calculate_complexity(tree)
            except:
                complexity = lines // 10  # Rough estimate
            
            # Determine risk level
            if issues_count > 5 or complexity > 20:
                risk = 'high'
                risk_color = '#dc2626'
            elif issues_count > 2 or complexity > 10:
                risk = 'medium'
                risk_color = '#f59e0b'
            else:
                risk = 'low'
                risk_color = '#10b981'
            
            return {
                'path': str(filepath.relative_to(self.target_dir)),
                'name': filepath.name,
                'lines': lines,
                'size': file_size,
                'issues': issues_count,
                'complexity': complexity,
                'status': status,
                'color': color,
                'risk': risk,
                'risk_color': risk_color,
                'patterns': py2_patterns
            }
        
        except Exception as e:
            return None
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity approximation."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    def scan_directory(self, exclude_dirs: Optional[List[str]] = None) -> List[Dict]:
        """Scan directory for Python files and analyze them."""
        if exclude_dirs is None:
            exclude_dirs = ['venv', '.venv', 'node_modules', '__pycache__', '.git', 'dist', 'build']
        
        self.file_data = []
        
        for root, dirs, files in os.walk(self.target_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    file_info = self.analyze_file(filepath)
                    if file_info:
                        self.file_data.append(file_info)
                        self.stats['total_files'] += 1
                        self.stats['total_lines'] += file_info['lines']
                        
                        # Update status count
                        if file_info['status'] == 'completed':
                            self.stats['migrated'] += 1
                        elif file_info['status'] == 'in_progress':
                            self.stats['in_progress'] += 1
                        elif file_info['status'] == 'not_started':
                            self.stats['not_started'] += 1
                        
                        # Update risk count
                        if file_info['risk'] == 'high':
                            self.stats['high_risk'] += 1
                        elif file_info['risk'] == 'medium':
                            self.stats['medium_risk'] += 1
                        elif file_info['risk'] == 'low':
                            self.stats['low_risk'] += 1
        
        return self.file_data
    
    def generate_treemap_data(self) -> Dict:
        """Generate data structure for treemap visualization."""
        # Group files by directory
        tree = {'name': 'root', 'children': []}
        dir_map = {}
        
        for file_info in self.file_data:
            parts = Path(file_info['path']).parts
            current = tree
            
            # Navigate/create directory structure
            for i, part in enumerate(parts[:-1]):
                path_key = '/'.join(parts[:i+1])
                if path_key not in dir_map:
                    new_dir = {
                        'name': part,
                        'children': [],
                        'type': 'directory'
                    }
                    current['children'].append(new_dir)
                    dir_map[path_key] = new_dir
                    current = new_dir
                else:
                    current = dir_map[path_key]
            
            # Add file
            current['children'].append({
                'name': file_info['name'],
                'value': file_info['lines'],
                'size': file_info['size'],
                'issues': file_info['issues'],
                'complexity': file_info['complexity'],
                'status': file_info['status'],
                'color': file_info['color'],
                'risk': file_info['risk'],
                'risk_color': file_info['risk_color'],
                'type': 'file'
            })
        
        return tree
    
    def generate_html(self, output_file: str = "migration_heatmap.html") -> str:
        """Generate interactive HTML heatmap."""
        treemap_data = self.generate_treemap_data()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Heatmap</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .stat {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .legend {{
            padding: 20px 40px;
            background: white;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
        }}
        
        .legend-label {{
            font-size: 0.9em;
            color: #374151;
        }}
        
        #treemap {{
            padding: 40px;
        }}
        
        .node {{
            stroke: white;
            stroke-width: 2px;
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        
        .node:hover {{
            opacity: 0.8;
        }}
        
        .label {{
            fill: white;
            font-size: 12px;
            font-weight: 500;
            pointer-events: none;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            font-size: 14px;
            line-height: 1.6;
            max-width: 300px;
            z-index: 1000;
        }}
        
        .tooltip.show {{
            opacity: 1;
        }}
        
        .view-mode {{
            padding: 20px 40px;
            display: flex;
            justify-content: center;
            gap: 10px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .view-btn {{
            padding: 10px 24px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .view-btn:hover {{
            background: #667eea;
            color: white;
        }}
        
        .view-btn.active {{
            background: #667eea;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🗺️ Migration Heatmap</h1>
            <div class="subtitle">Visual Overview of Python 2 to 3 Migration Status</div>
        </header>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{self.stats['total_files']}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat">
                <div class="stat-value">{self.stats['total_lines']:,}</div>
                <div class="stat-label">Lines of Code</div>
            </div>
            <div class="stat">
                <div class="stat-value">{self.stats['migrated']}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat">
                <div class="stat-value">{self.stats['in_progress']}</div>
                <div class="stat-label">In Progress</div>
            </div>
            <div class="stat">
                <div class="stat-value">{self.stats['not_started']}</div>
                <div class="stat-label">Not Started</div>
            </div>
            <div class="stat">
                <div class="stat-value">{self.stats['high_risk']}</div>
                <div class="stat-label">High Risk</div>
            </div>
        </div>
        
        <div class="view-mode">
            <button class="view-btn active" onclick="changeView('status')">Status View</button>
            <button class="view-btn" onclick="changeView('risk')">Risk View</button>
        </div>
        
        <div class="legend" id="legend-status">
            <div class="legend-item">
                <div class="legend-color" style="background: #10b981;"></div>
                <div class="legend-label">Completed (No Python 2 patterns)</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f59e0b;"></div>
                <div class="legend-label">In Progress (Few Python 2 patterns)</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ef4444;"></div>
                <div class="legend-label">Not Started (Many Python 2 patterns)</div>
            </div>
        </div>
        
        <div class="legend" id="legend-risk" style="display: none;">
            <div class="legend-item">
                <div class="legend-color" style="background: #10b981;"></div>
                <div class="legend-label">Low Risk (Simple migration)</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f59e0b;"></div>
                <div class="legend-label">Medium Risk (Moderate complexity)</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #dc2626;"></div>
                <div class="legend-label">High Risk (High complexity/issues)</div>
            </div>
        </div>
        
        <div id="treemap"></div>
    </div>
    
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        const data = {json.dumps(treemap_data)};
        let currentView = 'status';
        
        function changeView(view) {{
            currentView = view;
            
            // Update button states
            document.querySelectorAll('.view-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Update legend
            document.getElementById('legend-status').style.display = view === 'status' ? 'flex' : 'none';
            document.getElementById('legend-risk').style.display = view === 'risk' ? 'flex' : 'none';
            
            // Redraw treemap
            drawTreemap();
        }}
        
        function drawTreemap() {{
            // Clear existing
            d3.select('#treemap').html('');
            
            const width = 1320;
            const height = 800;
            
            const svg = d3.select('#treemap')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const root = d3.hierarchy(data)
                .sum(d => d.type === 'file' ? d.value : 0)
                .sort((a, b) => b.value - a.value);
            
            d3.treemap()
                .size([width, height])
                .padding(2)
                .round(true)(root);
            
            const tooltip = d3.select('#tooltip');
            
            const nodes = svg.selectAll('g')
                .data(root.leaves())
                .join('g')
                .attr('transform', d => `translate(${{d.x0}},${{d.y0}})`);
            
            nodes.append('rect')
                .attr('class', 'node')
                .attr('width', d => d.x1 - d.x0)
                .attr('height', d => d.y1 - d.y0)
                .attr('fill', d => currentView === 'status' ? d.data.color : d.data.risk_color)
                .on('mouseover', function(event, d) {{
                    tooltip
                        .html(`
                            <strong>${{d.data.name}}</strong><br>
                            Lines: ${{d.data.value}}<br>
                            Issues: ${{d.data.issues}}<br>
                            Complexity: ${{d.data.complexity}}<br>
                            Status: ${{d.data.status}}<br>
                            Risk: ${{d.data.risk}}
                        `)
                        .classed('show', true)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY + 10) + 'px');
                }})
                .on('mouseout', function() {{
                    tooltip.classed('show', false);
                }});
            
            nodes.append('text')
                .attr('class', 'label')
                .selectAll('tspan')
                .data(d => {{
                    const width = d.x1 - d.x0;
                    const height = d.y1 - d.y0;
                    if (width > 60 && height > 30) {{
                        return [d.data.name];
                    }}
                    return [];
                }})
                .join('tspan')
                .attr('x', 4)
                .attr('y', 16)
                .text(d => d);
        }}
        
        // Initial draw
        drawTreemap();
    </script>
</body>
</html>
"""
        
        output_path = Path(output_file)
        output_path.write_text(html)
        return str(output_path.resolve())
    
    def generate_report(self) -> str:
        """Generate a text report of the heatmap analysis."""
        report = []
        report.append("=" * 70)
        report.append("MIGRATION HEATMAP ANALYSIS")
        report.append("=" * 70)
        report.append("")
        
        report.append("OVERALL STATISTICS:")
        report.append(f"  Total Files: {self.stats['total_files']}")
        report.append(f"  Total Lines: {self.stats['total_lines']:,}")
        report.append(f"  Completed: {self.stats['migrated']} ({self.stats['migrated']/max(self.stats['total_files'],1)*100:.1f}%)")
        report.append(f"  In Progress: {self.stats['in_progress']} ({self.stats['in_progress']/max(self.stats['total_files'],1)*100:.1f}%)")
        report.append(f"  Not Started: {self.stats['not_started']} ({self.stats['not_started']/max(self.stats['total_files'],1)*100:.1f}%)")
        report.append("")
        
        report.append("RISK DISTRIBUTION:")
        report.append(f"  High Risk: {self.stats['high_risk']} files")
        report.append(f"  Medium Risk: {self.stats['medium_risk']} files")
        report.append(f"  Low Risk: {self.stats['low_risk']} files")
        report.append("")
        
        # Top issues
        report.append("TOP 10 FILES BY ISSUES:")
        sorted_files = sorted(self.file_data, key=lambda x: x['issues'], reverse=True)[:10]
        for i, file_info in enumerate(sorted_files, 1):
            report.append(f"  {i:2d}. {file_info['path']}")
            report.append(f"      Issues: {file_info['issues']}, Complexity: {file_info['complexity']}, Risk: {file_info['risk']}")
        report.append("")
        
        # High complexity files
        report.append("TOP 10 FILES BY COMPLEXITY:")
        sorted_complex = sorted(self.file_data, key=lambda x: x['complexity'], reverse=True)[:10]
        for i, file_info in enumerate(sorted_complex, 1):
            report.append(f"  {i:2d}. {file_info['path']}")
            report.append(f"      Complexity: {file_info['complexity']}, Issues: {file_info['issues']}, Lines: {file_info['lines']}")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """CLI interface for heatmap generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate interactive heatmap visualization of migration status"
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='migration_heatmap.html',
        help='Output HTML file (default: migration_heatmap.html)'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Print text report to console'
    )
    
    args = parser.parse_args()
    
    print("🗺️  Generating Migration Heatmap...")
    print(f"📂 Scanning: {args.directory}")
    print()
    
    generator = HeatmapGenerator(args.directory)
    generator.scan_directory()
    
    if args.report:
        print(generator.generate_report())
    
    output_file = generator.generate_html(args.output)
    
    print("✅ Heatmap generated successfully!")
    print(f"📄 Output: {output_file}")
    print()
    print("💡 Open the HTML file in your browser to view the interactive heatmap.")
    print("   The heatmap shows files sized by lines of code, colored by status/risk.")


if __name__ == '__main__':
    main()
