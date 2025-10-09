# 🕸️ Dependency Graph Guide

## Overview

The Dependency Graph Generator creates interactive visual representations of your Python codebase's module dependencies. This powerful tool helps you understand complex codebases, plan migration order, and identify potential issues before starting your Python 2 to 3 migration.

## Why Use Dependency Graphs?

Visual dependency graphs provide insights that text reports can't match:

- **📊 Understand Complex Codebases**: See at a glance how modules relate to each other
- **🎯 Plan Migration Order**: Identify modules with fewer dependencies to migrate first
- **⚠️ Spot Circular Dependencies**: Visually identify problematic dependency cycles
- **🎨 Assess Risk at a Glance**: Color-coded nodes show risk levels instantly
- **👥 Communicate with Teams**: Present migration strategy with clear visuals
- **📈 Track Progress**: Regenerate graphs to visualize migration progress over time

## Quick Start

Generate a dependency graph for your project:

```bash
# Basic usage - creates dependency_graph.html
./py2to3 graph src/

# Specify custom output file
./py2to3 graph src/ -o my_project_deps.html

# View text summary instead of generating graph
./py2to3 graph src/ --summary
```

Open the generated HTML file in your web browser to explore the interactive visualization.

## Features

### Interactive Visualization

The dependency graph provides a rich, interactive experience:

- **Drag and Drop**: Rearrange nodes by dragging them
- **Zoom**: Scroll to zoom in and out
- **Hover Details**: Hover over nodes to see detailed information:
  - Module name and file path
  - Lines of code
  - Risk level
  - Number of imports
  - Complexity rating

### Color-Coded Risk Levels

Nodes are color-coded to show migration risk at a glance:

- 🔴 **Red (High Risk)**: Heavy use of Python 2 patterns, needs careful migration
- 🟡 **Yellow (Medium Risk)**: Some Python 2 patterns, moderate attention needed
- 🟢 **Green (Low Risk)**: Minimal Python 2 code, easy to migrate

### Statistics Dashboard

At the top of the graph, you'll see:

- Total number of modules
- Total dependencies
- Count of high/medium/low risk modules

### Circular Dependency Detection

If circular dependencies are detected, they're highlighted with a warning banner showing the cycle chains. These should be refactored before migration when possible.

## Use Cases

### 1. Planning Migration Order

**Goal**: Determine which modules to migrate first

**Approach**:
1. Generate the dependency graph
2. Look for modules with no dependencies (they appear isolated or only have outgoing arrows)
3. These modules are safe to migrate first since nothing depends on them
4. Work your way up to heavily-depended-upon modules

```bash
# Generate graph
./py2to3 graph src/ -o migration_plan.html

# Or get text summary with migration suggestions
./py2to3 graph src/ --summary
```

The text summary specifically identifies modules with no dependencies as good starting points.

### 2. Understanding a New Codebase

**Goal**: Quickly understand module relationships in an unfamiliar project

**Approach**:
1. Generate the dependency graph
2. Explore the visualization by dragging nodes and hovering for details
3. Identify core modules (heavily depended upon - many incoming arrows)
4. Identify leaf modules (few or no dependencies - isolated nodes)
5. Spot subsystems (clusters of interconnected modules)

```bash
./py2to3 graph /path/to/project -o project_overview.html
```

### 3. Identifying Circular Dependencies

**Goal**: Find and resolve circular dependencies before migration

**Approach**:
1. Generate the dependency graph
2. Look for the circular dependency warning banner
3. Review the cycle chains listed
4. Refactor to break the cycles (extract interfaces, reorganize code)
5. Regenerate graph to verify cycles are resolved

```bash
# Check for circular dependencies
./py2to3 graph src/ --summary
```

If circular dependencies exist, the summary will show them clearly.

### 4. Presenting to Stakeholders

**Goal**: Communicate migration strategy to non-technical stakeholders

**Approach**:
1. Generate a clean dependency graph
2. Share the HTML file or present it in meetings
3. Use the visual representation to explain:
   - Project complexity (number of modules and connections)
   - Risk distribution (color coding)
   - Migration approach (which parts first, which last)
   - Potential challenges (circular dependencies, high-risk modules)

```bash
# Generate polished graph for presentation
./py2to3 graph src/ -o stakeholder_presentation.html
```

### 5. Tracking Migration Progress

**Goal**: Visualize how migration reduces risk over time

**Approach**:
1. Generate initial graph before migration
2. Save with timestamp: `graph_before.html`
3. After migrating some modules, regenerate
4. Compare graphs to see risk levels decreasing
5. Share progress visually with team

```bash
# Before migration
./py2to3 graph src/ -o graph_$(date +%Y%m%d).html

# After some migration
./py2to3 graph src/ -o graph_$(date +%Y%m%d).html
```

## Understanding the Visualization

### Node Size

Node size is proportional to the module's lines of code (LOC). Larger circles = more code = potentially more work to migrate.

### Node Color

- 🔴 **Red**: High risk - many Python 2 patterns detected
- 🟡 **Yellow**: Medium risk - some Python 2 patterns
- 🟢 **Green**: Low risk - minimal Python 2 code

### Arrows (Edges)

Arrows show import relationships:
- Arrow points from importing module to imported module
- More arrows pointing TO a module = more dependents (migrate later)
- Fewer arrows pointing FROM a module = fewer dependencies (migrate earlier)

### Layout

The force-directed layout automatically positions nodes to minimize crossing edges. Modules that depend on each other tend to cluster together.

## Integration with Other Tools

### With Migration Planner

The dependency graph complements the migration planner:

```bash
# Get structured migration plan
./py2to3 plan src/ -o plan.md

# Get visual representation
./py2to3 graph src/ -o deps.html
```

Use the planner for detailed phase-by-phase instructions, and the graph for visual understanding.

### With Stats Tracking

Track how the dependency graph evolves:

```bash
# Collect baseline stats
./py2to3 stats collect --save

# Generate baseline graph
./py2to3 graph src/ -o graph_baseline.html

# After migration work
./py2to3 stats collect --save
./py2to3 graph src/ -o graph_progress.html
```

### With Risk Analyzer

Combine risk analysis with visual representation:

```bash
# Detailed risk analysis
./py2to3 risk src/ -o risk_report.txt

# Visual risk distribution
./py2to3 graph src/ -o risk_graph.html
```

## Command Reference

### Basic Command

```bash
./py2to3 graph <path> [options]
```

### Options

- `<path>`: Directory to analyze (required)
- `-o, --output <file>`: Output HTML file (default: dependency_graph.html)
- `--summary`: Print text summary instead of generating graph

### Examples

```bash
# Analyze src directory
./py2to3 graph src/

# Custom output filename
./py2to3 graph src/ -o my_deps.html

# Text summary only
./py2to3 graph src/ --summary

# Analyze entire project
./py2to3 graph . -o full_project_graph.html
```

## Tips and Best Practices

### 1. Start with a Summary

Before generating the full graph, check the summary:

```bash
./py2to3 graph src/ --summary
```

This gives you quick insights without opening a browser.

### 2. Handle Large Codebases

For very large projects (100+ modules), the graph might be crowded:

- Use zoom to focus on specific areas
- Consider analyzing subsystems separately
- Rely on hover tooltips for details rather than node labels

### 3. Regular Regeneration

Regenerate graphs regularly during migration to:
- Track progress visually
- Verify risk levels are decreasing
- Ensure no new circular dependencies were introduced

### 4. Share with Team

The HTML files are self-contained and portable:
- Email them to team members
- Add them to project documentation
- Include in migration reports
- Present in team meetings

### 5. Combine with Other Tools

Don't rely solely on the graph. Use it alongside:
- `./py2to3 plan` for structured migration steps
- `./py2to3 stats` for numerical metrics
- `./py2to3 risk` for detailed risk analysis

## Troubleshooting

### Graph Looks Cluttered

**Problem**: Too many nodes to see clearly

**Solutions**:
- Zoom in on specific areas
- Drag nodes to organize manually
- Analyze subsystems separately
- Use `--summary` for text overview

### Some Modules Missing

**Problem**: Expected modules don't appear in graph

**Cause**: Graph only shows local project modules, not external packages

**Solution**: This is by design. External dependencies (like `requests`, `numpy`) are filtered out to focus on your codebase structure.

### Circular Dependencies Found

**Problem**: Warning banner shows circular dependency chains

**Solution**: This is actually good - you've identified an issue! Refactor to break the cycles:
1. Extract shared code to a new module
2. Use dependency injection
3. Reorganize module structure
4. Move imports inside functions (temporary workaround)

### Graph Won't Generate

**Problem**: Error when running the command

**Common causes**:
- Path doesn't exist: Verify the directory path
- Not a directory: Graph command requires a directory, not a single file
- No Python files found: Ensure the directory contains .py files

## Technical Details

### What Gets Analyzed

The tool analyzes:
- All `.py` files in the specified directory (recursively)
- Import statements (`import` and `from ... import`)
- Lines of code (excluding blanks and comments)
- Python 2 pattern usage for risk assessment
- Module interdependencies

### What Gets Filtered

The tool filters out:
- External package imports (e.g., `requests`, `numpy`)
- Standard library imports (e.g., `os`, `sys`)
- Hidden directories (`.git`, `__pycache__`, etc.)
- Virtual environment directories

### Technology Stack

The generated HTML uses:
- **D3.js**: For force-directed graph layout and visualization
- **Pure JavaScript**: No build step required
- **Self-contained**: All code embedded in a single HTML file
- **Responsive**: Works on various screen sizes

## See Also

- [PLANNER_GUIDE.md](PLANNER_GUIDE.md): Structured migration planning
- [RISK_GUIDE.md](RISK_GUIDE.md): Detailed risk analysis
- [STATS_GUIDE.md](STATUS_GUIDE.md): Statistics tracking
- [CLI_GUIDE.md](CLI_GUIDE.md): Complete CLI reference

## Feedback and Contributions

Have ideas for improving the dependency graph visualization? We'd love to hear from you! Consider:
- Additional layout algorithms
- Export to other formats (PNG, SVG, GraphViz DOT)
- Filtering options (show only high-risk modules)
- Timeline view showing graph evolution
- Integration with other visualization tools

---

*Happy visualizing! 🕸️*
