#!/usr/bin/env python3
"""
Dependency Graph Generator for Python 2 to 3 Migration

Generates visual dependency graphs to help understand codebase structure
and plan migration order. Produces interactive HTML visualizations showing:
- Module dependencies as a network graph
- Risk levels with color coding
- Migration phases
- Circular dependencies
- Complexity metrics
"""

import ast
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class DependencyGraphGenerator:
    """Generates visual dependency graphs for Python codebases."""

    def __init__(self, root_path: str):
        """
        Initialize the dependency graph generator.

        Args:
            root_path: Root directory of the Python project
        """
        self.root_path = Path(root_path).resolve()
        self.modules: Dict[str, Dict] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.circular_deps: List[List[str]] = []
        
    def analyze(self):
        """Analyze the codebase and build dependency graph."""
        print("📊 Analyzing codebase structure...")
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(self.root_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in {
                '__pycache__', '.git', '.tox', 'venv', 'env',
                '.venv', 'node_modules', 'dist', 'build', '.pytest_cache'
            }]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        print(f"  Found {len(python_files)} Python files")
        
        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)
        
        # Detect circular dependencies
        self._detect_circular_dependencies()
        
        print(f"  Analyzed {len(self.modules)} modules")
        print(f"  Found {sum(len(deps) for deps in self.dependencies.values())} dependencies")
        if self.circular_deps:
            print(f"  ⚠️  Detected {len(self.circular_deps)} circular dependency chain(s)")
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file."""
        module_name = self._get_module_name(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Count lines of code (excluding blanks and comments)
            lines = [l.strip() for l in content.split('\n')]
            loc = sum(1 for l in lines if l and not l.startswith('#'))
            
            # Extract imports
            imports = self._extract_imports(tree, file_path)
            
            # Assess complexity (simple heuristic based on node types)
            complexity = self._assess_complexity(tree)
            
            # Detect Python 2 patterns for risk assessment
            risk_level = self._assess_risk(content, tree)
            
            # Store module information
            self.modules[module_name] = {
                'path': str(file_path.relative_to(self.root_path)),
                'loc': loc,
                'complexity': complexity,
                'risk': risk_level,
                'imports': list(imports)
            }
            
            # Store dependencies
            self.dependencies[module_name] = imports
            
        except Exception as e:
            print(f"  ⚠️  Warning: Could not analyze {file_path}: {e}")
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        rel_path = file_path.relative_to(self.root_path)
        parts = list(rel_path.parts)
        
        # Remove .py extension
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        
        # Handle __init__.py
        if parts[-1] == '__init__':
            parts = parts[:-1]
        
        return '.'.join(parts) if parts else '__main__'
    
    def _extract_imports(self, tree: ast.AST, file_path: Path) -> Set[str]:
        """Extract local module imports from AST."""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    imports.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    imports.add(module)
        
        # Filter to only local modules (ones we're tracking)
        local_imports = set()
        for imp in imports:
            # Check if this matches any module we know about
            for mod_name in self.modules.keys():
                if mod_name == imp or mod_name.startswith(imp + '.'):
                    local_imports.add(imp)
                    break
        
        return local_imports
    
    def _assess_complexity(self, tree: ast.AST) -> str:
        """Assess code complexity."""
        # Count various AST nodes as a complexity metric
        node_counts = defaultdict(int)
        for node in ast.walk(tree):
            node_counts[type(node).__name__] += 1
        
        # Simple heuristic: functions + classes + loops + conditions
        complexity_score = (
            node_counts.get('FunctionDef', 0) +
            node_counts.get('ClassDef', 0) +
            node_counts.get('For', 0) +
            node_counts.get('While', 0) +
            node_counts.get('If', 0)
        )
        
        if complexity_score > 50:
            return 'high'
        elif complexity_score > 20:
            return 'medium'
        else:
            return 'low'
    
    def _assess_risk(self, content: str, tree: ast.AST) -> str:
        """Assess migration risk level."""
        risk_score = 0
        
        # Python 2 patterns that indicate risk
        py2_patterns = [
            'print ', 'xrange(', 'iteritems(', 'iterkeys(', 'itervalues(',
            'unicode(', 'basestring', 'raw_input(', '.next()',
            'urllib2', 'ConfigParser', 'except.*,.*:', 'long(',
        ]
        
        for pattern in py2_patterns:
            risk_score += content.count(pattern)
        
        # Check for old-style string formatting
        risk_score += content.count('%s') + content.count('%d')
        
        # Check for division operator (might be integer division in Py2)
        risk_score += content.count(' / ')
        
        if risk_score > 20:
            return 'high'
        elif risk_score > 5:
            return 'medium'
        else:
            return 'low'
    
    def _detect_circular_dependencies(self):
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in self.modules:
                    continue
                    
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in self.circular_deps:
                        self.circular_deps.append(cycle)
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for module in self.modules:
            if module not in visited:
                dfs(module)
    
    def generate_html(self, output_file: str = "dependency_graph.html"):
        """Generate interactive HTML visualization."""
        print(f"\n📊 Generating interactive dependency graph...")
        
        # Prepare data for visualization
        nodes = []
        links = []
        node_ids = {name: idx for idx, name in enumerate(self.modules.keys())}
        
        # Create nodes
        for name, info in self.modules.items():
            nodes.append({
                'id': node_ids[name],
                'name': name,
                'path': info['path'],
                'loc': info['loc'],
                'complexity': info['complexity'],
                'risk': info['risk'],
                'imports': len(info['imports'])
            })
        
        # Create links
        for source, targets in self.dependencies.items():
            if source not in node_ids:
                continue
            for target in targets:
                if target in node_ids:
                    links.append({
                        'source': node_ids[source],
                        'target': node_ids[target]
                    })
        
        # Generate HTML
        html_content = self._generate_html_template(nodes, links)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Graph saved to: {output_file}")
        print(f"  Nodes: {len(nodes)}")
        print(f"  Edges: {len(links)}")
    
    def _generate_html_template(self, nodes: List[Dict], links: List[Dict]) -> str:
        """Generate HTML template with embedded D3.js visualization."""
        nodes_json = json.dumps(nodes, indent=2)
        links_json = json.dumps(links, indent=2)
        circular_deps_json = json.dumps(self.circular_deps, indent=2)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dependency Graph - Python 2 to 3 Migration</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card .label {{
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .stat-card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .graph-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 1rem;
            margin-bottom: 2rem;
        }}
        
        .legend {{
            display: flex;
            gap: 2rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
        
        .risk-high {{ background: #e74c3c; }}
        .risk-medium {{ background: #f39c12; }}
        .risk-low {{ background: #2ecc71; }}
        
        #graph {{
            width: 100%;
            height: 700px;
            border: 1px solid #ecf0f1;
            border-radius: 8px;
        }}
        
        .tooltip {{
            position: absolute;
            padding: 12px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            border-radius: 6px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            font-size: 0.9rem;
            max-width: 300px;
            z-index: 1000;
        }}
        
        .tooltip .module-name {{
            font-weight: bold;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }}
        
        .tooltip .detail {{
            margin: 0.25rem 0;
        }}
        
        .controls {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        .controls h3 {{
            margin-bottom: 1rem;
        }}
        
        .control-group {{
            margin-bottom: 1rem;
        }}
        
        .control-group label {{
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }}
        
        select, input[type="range"] {{
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        
        .circular-deps {{
            background: #fff3cd;
            border-left: 4px solid #f39c12;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 2rem;
        }}
        
        .circular-deps h3 {{
            color: #f39c12;
            margin-bottom: 0.5rem;
        }}
        
        .circular-deps ul {{
            list-style: none;
            padding-left: 1rem;
        }}
        
        .circular-deps li {{
            margin: 0.25rem 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🕸️ Dependency Graph Visualization</h1>
        <p>Interactive module dependency analysis for Python 2 to 3 migration</p>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Modules</div>
                <div class="value" id="total-modules">0</div>
            </div>
            <div class="stat-card">
                <div class="label">Dependencies</div>
                <div class="value" id="total-deps">0</div>
            </div>
            <div class="stat-card">
                <div class="label">High Risk</div>
                <div class="value" id="high-risk" style="color: #e74c3c;">0</div>
            </div>
            <div class="stat-card">
                <div class="label">Medium Risk</div>
                <div class="value" id="medium-risk" style="color: #f39c12;">0</div>
            </div>
            <div class="stat-card">
                <div class="label">Low Risk</div>
                <div class="value" id="low-risk" style="color: #2ecc71;">0</div>
            </div>
        </div>
        
        <div id="circular-deps-container"></div>
        
        <div class="graph-container">
            <div class="legend">
                <h3 style="width: 100%; margin-bottom: 0.5rem;">Legend</h3>
                <div class="legend-item">
                    <div class="legend-color risk-high"></div>
                    <span>High Risk</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color risk-medium"></div>
                    <span>Medium Risk</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color risk-low"></div>
                    <span>Low Risk</span>
                </div>
                <div class="legend-item" style="margin-left: auto;">
                    <span style="color: #7f8c8d;">💡 Tip: Drag nodes to rearrange, scroll to zoom</span>
                </div>
            </div>
            <svg id="graph"></svg>
        </div>
    </div>
    
    <div class="tooltip"></div>
    
    <script>
        const nodes = {nodes_json};
        const links = {links_json};
        const circularDeps = {circular_deps_json};
        
        // Update statistics
        document.getElementById('total-modules').textContent = nodes.length;
        document.getElementById('total-deps').textContent = links.length;
        
        const riskCounts = {{ high: 0, medium: 0, low: 0 }};
        nodes.forEach(node => {{
            if (node.risk === 'high') riskCounts.high++;
            else if (node.risk === 'medium') riskCounts.medium++;
            else riskCounts.low++;
        }});
        
        document.getElementById('high-risk').textContent = riskCounts.high;
        document.getElementById('medium-risk').textContent = riskCounts.medium;
        document.getElementById('low-risk').textContent = riskCounts.low;
        
        // Show circular dependencies warning
        if (circularDeps.length > 0) {{
            const container = document.getElementById('circular-deps-container');
            let html = '<div class="circular-deps">';
            html += '<h3>⚠️ Circular Dependencies Detected</h3>';
            html += '<p>The following circular dependency chains were found:</p>';
            html += '<ul>';
            circularDeps.forEach(cycle => {{
                html += '<li>→ ' + cycle.join(' → ') + '</li>';
            }});
            html += '</ul>';
            html += '<p style="margin-top: 0.5rem;"><em>Consider refactoring to break these cycles before migration.</em></p>';
            html += '</div>';
            container.innerHTML = html;
        }}
        
        // Set up SVG
        const svg = d3.select('#graph');
        const container = document.querySelector('#graph');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        svg.attr('viewBox', [0, 0, width, height]);
        
        // Create simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));
        
        // Create arrow marker for directed edges
        svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 25)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#95a5a6');
        
        // Create links
        const link = svg.append('g')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke', '#95a5a6')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 1.5)
            .attr('marker-end', 'url(#arrowhead)');
        
        // Color scale for risk
        const colorScale = d3.scaleOrdinal()
            .domain(['high', 'medium', 'low'])
            .range(['#e74c3c', '#f39c12', '#2ecc71']);
        
        // Create nodes
        const node = svg.append('g')
            .selectAll('g')
            .data(nodes)
            .join('g')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        node.append('circle')
            .attr('r', d => Math.max(8, Math.min(20, d.loc / 10)))
            .attr('fill', d => colorScale(d.risk))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);
        
        node.append('text')
            .text(d => d.name.split('.').pop())
            .attr('x', 0)
            .attr('y', -20)
            .attr('text-anchor', 'middle')
            .attr('font-size', '10px')
            .attr('fill', '#2c3e50')
            .attr('font-weight', '500');
        
        // Tooltip
        const tooltip = d3.select('.tooltip');
        
        node.on('mouseover', function(event, d) {{
            tooltip
                .style('opacity', 1)
                .html(`
                    <div class="module-name">${{d.name}}</div>
                    <div class="detail">📁 Path: ${{d.path}}</div>
                    <div class="detail">📊 Lines of Code: ${{d.loc}}</div>
                    <div class="detail">⚠️ Risk: ${{d.risk}}</div>
                    <div class="detail">🔗 Imports: ${{d.imports}}</div>
                    <div class="detail">🔧 Complexity: ${{d.complexity}}</div>
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px');
            
            d3.select(this).select('circle')
                .attr('stroke', '#3498db')
                .attr('stroke-width', 3);
        }})
        .on('mouseout', function() {{
            tooltip.style('opacity', 0);
            d3.select(this).select('circle')
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);
        }});
        
        // Update positions
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {{
                svg.selectAll('g').attr('transform', event.transform);
            }});
        
        svg.call(zoom);
    </script>
</body>
</html>
"""
    
    def generate_summary(self) -> str:
        """Generate a text summary of the dependency analysis."""
        lines = []
        lines.append("=" * 70)
        lines.append("DEPENDENCY ANALYSIS SUMMARY")
        lines.append("=" * 70)
        lines.append("")
        
        lines.append(f"Total Modules: {len(self.modules)}")
        lines.append(f"Total Dependencies: {sum(len(deps) for deps in self.dependencies.values())}")
        lines.append("")
        
        # Risk breakdown
        risk_counts = {'high': 0, 'medium': 0, 'low': 0}
        for info in self.modules.values():
            risk_counts[info['risk']] += 1
        
        lines.append("Risk Distribution:")
        lines.append(f"  🔴 High Risk: {risk_counts['high']} modules")
        lines.append(f"  🟡 Medium Risk: {risk_counts['medium']} modules")
        lines.append(f"  🟢 Low Risk: {risk_counts['low']} modules")
        lines.append("")
        
        # Circular dependencies
        if self.circular_deps:
            lines.append(f"⚠️  Circular Dependencies: {len(self.circular_deps)} cycle(s)")
            for i, cycle in enumerate(self.circular_deps, 1):
                lines.append(f"  {i}. {' → '.join(cycle)}")
            lines.append("")
        
        # Top modules by dependencies (most depended upon)
        reverse_deps = defaultdict(int)
        for source, targets in self.dependencies.items():
            for target in targets:
                reverse_deps[target] += 1
        
        if reverse_deps:
            lines.append("Most Depended Upon Modules (migrate these last):")
            sorted_deps = sorted(reverse_deps.items(), key=lambda x: x[1], reverse=True)[:5]
            for module, count in sorted_deps:
                lines.append(f"  • {module}: {count} dependents")
            lines.append("")
        
        # Modules with no dependencies (good starting points)
        no_deps = [name for name, deps in self.dependencies.items() if not deps]
        if no_deps:
            lines.append(f"Modules with No Dependencies (migrate these first): {len(no_deps)}")
            for module in no_deps[:10]:
                lines.append(f"  • {module}")
            if len(no_deps) > 10:
                lines.append(f"  ... and {len(no_deps) - 10} more")
            lines.append("")
        
        lines.append("=" * 70)
        return '\n'.join(lines)


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate visual dependency graphs for Python 2 to 3 migration'
    )
    parser.add_argument(
        'path',
        help='Path to Python project directory'
    )
    parser.add_argument(
        '-o', '--output',
        default='dependency_graph.html',
        help='Output HTML file (default: dependency_graph.html)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print text summary instead of generating graph'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    generator = DependencyGraphGenerator(args.path)
    generator.analyze()
    
    if args.summary:
        print(generator.generate_summary())
    else:
        generator.generate_html(args.output)
        print(f"\n✓ Open {args.output} in your browser to view the interactive graph")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
