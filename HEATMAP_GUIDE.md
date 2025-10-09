# Migration Heatmap Guide 🗺️

The **Migration Heatmap Generator** creates interactive visual treemaps that show the migration status, risk levels, and complexity of all Python files in your project at a glance. This powerful visualization tool helps teams quickly identify problem areas, prioritize work, and present progress to stakeholders.

## Overview

The heatmap provides a **spatial/structural view** of your codebase (vs. temporal views like dashboards), making it easy to:
- 🎯 **Identify hotspots** - See which files need the most attention
- 📊 **Prioritize work** - Focus on high-risk, high-complexity areas first
- 👥 **Present progress** - Beautiful visuals for stakeholder presentations
- 🗺️ **Understand structure** - See your codebase layout at a glance
- 🔍 **Spot patterns** - Identify directories or modules that need work

## Quick Start

Generate a heatmap for your project:

```bash
# Basic usage - analyze current directory
./py2to3 heatmap

# Analyze specific directory
./py2to3 heatmap src/

# With text report and custom output file
./py2to3 heatmap src/ --report -o my_heatmap.html

# Then open in browser
open my_heatmap.html
```

## Command Options

```
./py2to3 heatmap [directory] [options]

Positional Arguments:
  directory          Directory to analyze (default: current directory)

Options:
  -o, --output FILE  Output HTML file (default: migration_heatmap.html)
  --report          Print detailed text report to console
  -h, --help        Show help message
```

## Features

### Interactive Treemap Visualization

The heatmap generates a beautiful HTML file with:

#### 1. **Two View Modes**
- **Status View** - Color-coded by migration status:
  - 🟢 **Green** - Completed (no Python 2 patterns detected)
  - 🟡 **Amber** - In Progress (few Python 2 patterns)
  - 🔴 **Red** - Not Started (many Python 2 patterns)

- **Risk View** - Color-coded by migration risk:
  - 🟢 **Green** - Low Risk (simple migration)
  - 🟡 **Amber** - Medium Risk (moderate complexity)
  - 🔴 **Red** - High Risk (high complexity or many issues)

#### 2. **Proportional Sizing**
Files are sized proportionally to their line count, making it easy to see which files are largest and most impactful.

#### 3. **Interactive Tooltips**
Hover over any file to see detailed information:
- File name and path
- Number of lines
- Python 2 issues count
- Cyclomatic complexity
- Migration status
- Risk level

#### 4. **Summary Statistics**
Top-level stats showing:
- Total files analyzed
- Total lines of code
- Completed, in progress, and not started counts
- Risk distribution (high, medium, low)

#### 5. **Hierarchical Layout**
Files are organized by directory structure, making it easy to see which parts of your codebase need attention.

### Text Report

With `--report` flag, get a detailed console report including:

```
OVERALL STATISTICS:
  Total Files: 68
  Total Lines: 37,953
  Completed: 0 (0.0%)
  In Progress: 40 (58.8%)
  Not Started: 28 (41.2%)

RISK DISTRIBUTION:
  High Risk: 58 files
  Medium Risk: 4 files
  Low Risk: 6 files

TOP 10 FILES BY ISSUES:
  [Ranked list of files with most Python 2 issues]

TOP 10 FILES BY COMPLEXITY:
  [Ranked list of most complex files]
```

## Use Cases

### 1. Daily Standup Meetings

Show the heatmap during team meetings to visualize progress:

```bash
./py2to3 heatmap src/ -o daily_progress.html
# Share the HTML file or present it on screen
```

### 2. Sprint Planning

Identify which files to tackle in the next sprint:

```bash
./py2to3 heatmap . --report | grep "High Risk"
# Focus on high-risk files first
```

### 3. Stakeholder Presentations

Generate a clean, professional visualization for management:

```bash
./py2to3 heatmap src/ -o stakeholder_report.html
# Beautiful interactive charts that anyone can understand
```

### 4. Code Review Prioritization

Find files that need the most careful review:

```bash
./py2to3 heatmap . --report
# Review files with high complexity + high issues first
```

### 5. Team Workload Distribution

Use the heatmap to assign work to team members:

```bash
./py2to3 heatmap src/
# Assign different colored/sized areas to different developers
```

## Understanding the Analysis

### Python 2 Pattern Detection

The heatmap detects these Python 2 patterns:
- ✓ Print statements (`print "msg"` vs `print("msg")`)
- ✓ Old imports (`urllib2`, `ConfigParser`, `Queue`, `cPickle`)
- ✓ Unicode literals (`unicode()` calls)
- ✓ Iterator methods (`.iteritems()`, `xrange()`)
- ✓ Old exception syntax (`except Exception, e:`)
- ✓ Deprecated types (`basestring`, `long`)
- ✓ Old methods (`.has_key()`)
- ✓ Division behavior (missing `from __future__ import division`)

### Migration Status Classification

**Completed** (Green):
- Zero Python 2 patterns detected
- File appears to be Python 3 compatible

**In Progress** (Amber):
- 1-2 Python 2 patterns detected
- Partially migrated

**Not Started** (Red):
- 3+ Python 2 patterns detected
- Significant migration work needed

### Risk Level Calculation

Risk is based on two factors:

1. **Issue Count** - Number of Python 2 patterns
2. **Complexity** - Cyclomatic complexity (branches, loops, conditions)

**High Risk**:
- More than 5 Python 2 issues, OR
- Cyclomatic complexity > 20

**Medium Risk**:
- More than 2 Python 2 issues, OR
- Cyclomatic complexity > 10

**Low Risk**:
- Few Python 2 issues AND
- Low complexity

## Integration with Other Tools

### With Migration Workflow

```bash
# 1. Generate initial heatmap
./py2to3 heatmap src/ -o before.html

# 2. Run migration
./py2to3 migrate src/ --auto-yes

# 3. Generate after heatmap
./py2to3 heatmap src/ -o after.html

# 4. Compare before and after
open before.html after.html
```

### With Dashboard

```bash
# Collect stats regularly
./py2to3 stats collect --save

# Generate temporal dashboard
./py2to3 dashboard

# Generate spatial heatmap
./py2to3 heatmap src/

# Use both for comprehensive view:
# - Dashboard shows progress over time
# - Heatmap shows current structure/status
```

### With Report Card

```bash
# Generate comprehensive analysis
./py2to3 report-card src/

# Generate visual heatmap
./py2to3 heatmap src/

# Use together for presentations
```

## Advanced Usage

### Analyze Multiple Directories

```bash
# Analyze different parts separately
./py2to3 heatmap src/core -o core_heatmap.html
./py2to3 heatmap src/web -o web_heatmap.html
./py2to3 heatmap src/utils -o utils_heatmap.html
```

### Track Progress Over Time

```bash
# Weekly snapshots
./py2to3 heatmap src/ -o heatmap_week1.html
# ... do migration work ...
./py2to3 heatmap src/ -o heatmap_week2.html
# ... do more work ...
./py2to3 heatmap src/ -o heatmap_week3.html

# Watch colors change from red → amber → green!
```

### Identify Bottlenecks

```bash
# Find files blocking progress
./py2to3 heatmap . --report | grep "High Risk" > bottlenecks.txt

# Focus migration efforts on these files
cat bottlenecks.txt
```

## Tips and Best Practices

### 1. **Generate Regularly**
Create heatmaps weekly or after major migration sessions to track progress.

### 2. **Focus on Large Red Blocks**
Prioritize large, red (not started) files - they have the most impact.

### 3. **Celebrate Green**
Share heatmaps with team to celebrate when red areas turn green!

### 4. **Use Both Views**
- **Status View** - For tracking migration progress
- **Risk View** - For identifying challenging areas

### 5. **Export for Presentations**
The HTML files are self-contained - email them or upload to shared drives.

### 6. **Combine with Text Report**
Use `--report` to get actionable lists of specific files to work on.

### 7. **Directory-Level Analysis**
If heatmap is overwhelming, analyze subdirectories separately.

### 8. **Version Control Friendly**
Add heatmap generation to your CI/CD for automatic progress tracking.

## Troubleshooting

### Issue: Heatmap shows all files as "Not Started"

**Solution**: This might be normal if starting a fresh migration. Check the text report to see actual issue counts.

### Issue: Large files dominate the view

**Solution**: This is intentional - large files have more impact. Consider analyzing subdirectories separately for detail.

### Issue: HTML file won't open

**Solution**: Ensure you have a modern browser. The heatmap uses D3.js which requires JavaScript support.

### Issue: Analysis is slow

**Solution**: The tool analyzes AST for complexity calculation. For very large codebases, consider analyzing subdirectories separately.

## Example Workflow

Here's a complete workflow using the heatmap:

```bash
# 1. Initial assessment
./py2to3 heatmap src/ --report -o assessment.html
# Review the report, identify high-priority files

# 2. Run preflight checks
./py2to3 preflight src/
# Understand the scope

# 3. Start migration on high-priority files
./py2to3 fix src/high_priority_file.py
./py2to3 fix src/another_priority_file.py

# 4. Check progress
./py2to3 heatmap src/ -o progress.html
# See files turn from red to amber to green!

# 5. Continue migration
./py2to3 migrate src/ --interactive

# 6. Final validation
./py2to3 heatmap src/ --report -o final.html
# Celebrate when everything is green!
```

## Comparison with Other Tools

| Feature | Heatmap | Dashboard | Report Card |
|---------|---------|-----------|-------------|
| **Visual** | ✅ Interactive treemap | ✅ Charts | ❌ Text-based |
| **Spatial view** | ✅ By file/directory | ❌ | ❌ |
| **Temporal view** | ❌ | ✅ Over time | ❌ |
| **File-level detail** | ✅ Per file | ❌ Project-wide | ✅ Per file |
| **Risk analysis** | ✅ Visual + calculated | ❌ | ✅ Detailed |
| **Stakeholder-friendly** | ✅✅ Very visual | ✅ Good charts | ❌ Technical |
| **Quick overview** | ✅✅ At a glance | ✅ | ❌ Detailed |
| **Prioritization** | ✅✅ Visual | ❌ | ✅ Lists |

**Use Heatmap when you want:**
- Quick visual overview of current state
- To present to non-technical stakeholders
- To identify problem areas spatially
- To prioritize work visually

**Use Dashboard when you want:**
- Track progress over time
- See trends and velocity
- Predict completion dates

**Use Report Card when you want:**
- Detailed technical analysis
- File-by-file assessment
- Comprehensive quality metrics

## Best Use: Combine All Three!

```bash
# For complete insight:
./py2to3 report-card src/ -o detailed.json  # Technical depth
./py2to3 dashboard -o trends.html           # Temporal view
./py2to3 heatmap src/ -o structure.html     # Spatial view

# Now you have:
# - Detailed technical data (report-card)
# - Progress over time (dashboard)  
# - Current structure view (heatmap)
```

## Summary

The Migration Heatmap Generator is your **visual command center** for understanding migration status at a glance. It complements other tools by providing spatial/structural insights that help teams prioritize work and communicate progress effectively.

**Key Benefits:**
- 🎯 Instant identification of problem areas
- 📊 Beautiful visualizations for any audience  
- 🗺️ Spatial understanding of codebase
- 🚀 Helps prioritize migration work
- 👥 Perfect for team communication
- 📈 Tracks progress visually over time

Start using the heatmap today to gain instant visual insight into your Python 2 to 3 migration!

```bash
./py2to3 heatmap src/ -o heatmap.html
open heatmap.html
```

Happy migrating! 🚀
