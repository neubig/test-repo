# Migration Simulator Guide 🔮

The **Migration Simulator** allows you to preview the complete outcome of a Python 2 to Python 3 migration **without making any changes** to your code. This is perfect for planning, getting stakeholder approval, and understanding the scope of changes before committing to the migration.

## Why Use the Simulator?

- **🎯 Planning**: Understand the full scope of changes before starting
- **👔 Stakeholder Approval**: Generate reports for management buy-in
- **📊 Impact Analysis**: See exactly what will change and where
- **🎓 Training & Demos**: Show teams what to expect from migration
- **⚖️ Strategy Comparison**: Test different configurations safely
- **📈 Estimation**: Get accurate effort estimates with real data

## Quick Start

```bash
# Simulate migration of current directory
./py2to3 simulate

# Simulate specific directory with detailed output
./py2to3 simulate src/ --detailed --verbose

# Generate detailed JSON report
./py2to3 simulate src/ -o my_simulation.json
```

## How It Works

The simulator runs through three phases:

### Phase 1: Analyze Current State
- Scans all Python files in the target path
- Identifies Python 2 compatibility issues
- Counts problems by type and severity

### Phase 2: Simulate Migration
- Applies all fix patterns in memory (no files changed!)
- Tracks what changes would be made to each file
- Generates before/after previews
- Counts changes by type

### Phase 3: Project Outcomes
- Estimates remaining issues after migration
- Calculates expected success rate
- Identifies files that may need manual review

## Command Options

```bash
./py2to3 simulate [PATH] [OPTIONS]
```

### Arguments

- `PATH` - Directory or file to simulate (default: current directory)

### Options

- `-v, --verbose` - Show detailed progress for each file
- `-d, --detailed` - Include detailed breakdown in report
- `-o, --output FILE` - Save JSON report to file (default: simulation_report.json)

## Usage Examples

### Basic Simulation

Preview migration of your entire project:

```bash
./py2to3 simulate
```

Output:
```
🔮 Starting Migration Simulation...
📁 Target: .
============================================================

📊 Found 25 Python files to analyze

Phase 1: Analyzing current state...
------------------------------------------------------------
✓ Current state: 143 Python 2 issues detected

Phase 2: Simulating migration fixes...
------------------------------------------------------------
✓ Simulated 156 changes across 23 files

Phase 3: Analyzing projected state...
------------------------------------------------------------
✓ Projected state: ~9 issues remaining
  (Estimated 134 issues would be resolved)

============================================================
🔮 MIGRATION SIMULATION REPORT
============================================================

📊 Overview:
  Total files scanned:     25
  Files requiring changes: 23
  Files unchanged:         2

🔧 Projected Changes:
  Total fixes to apply:    156
  Fix types needed:        12

📈 Impact Analysis:
  Issues before:           143
  Issues after (est.):     9
  Success rate (est.):     93.7%

============================================================
✅ Simulation Complete!
============================================================

💡 Next Steps:
  1. Review the simulation results above
  2. Create a backup: ./py2to3 backup create
  3. Apply fixes: ./py2to3 fix src/
  4. Verify results: ./py2to3 check src/

⚠️  Note: This is a simulation. No files were modified.
```

### Detailed Simulation

Get a breakdown of changes by type:

```bash
./py2to3 simulate src/ --detailed
```

Additional output includes:
```
🔍 Changes by Type:
  print_statements........................  42
  iteritems_calls.........................  28
  urllib2_imports.........................  15
  except_syntax...........................  12
  xrange_calls............................  11
  ... and 7 more
```

### Verbose Simulation

See progress for each file:

```bash
./py2to3 simulate src/ --verbose
```

Shows:
```
Phase 2: Simulating migration fixes...
------------------------------------------------------------
  Simulating: src/web/scraper.py
    ✓ 15 changes simulated
  Simulating: src/core/processor.py
    ✓ 22 changes simulated
  Simulating: src/data/database.py
    ✓ 8 changes simulated
  ...
```

### Save Detailed Report

Generate a comprehensive JSON report for analysis:

```bash
./py2to3 simulate --output detailed_analysis.json
```

The JSON report includes:
- Complete list of files analyzed
- Detailed changes for each file
- Before/after code previews
- Issues breakdown
- Timestamp and metadata

## Understanding the Report

### Overview Section

- **Total files scanned**: All Python files found
- **Files requiring changes**: Files with Python 2 patterns
- **Files unchanged**: Already Python 3 compatible

### Projected Changes

- **Total fixes to apply**: Number of individual changes
- **Fix types needed**: Different types of fixes (imports, print, etc.)

### Impact Analysis

- **Issues before**: Python 2 compatibility issues detected
- **Issues after (est.)**: Estimated remaining issues
- **Success rate**: Percentage of issues that would be resolved

### Changes by Type

When using `--detailed`, see the breakdown:
- `print_statements`: Print statement conversions
- `iteritems_calls`: Dictionary iterator updates
- `urllib2_imports`: Import path changes
- `except_syntax`: Exception handling updates
- And more...

## Use Cases

### 1. Pre-Migration Planning

Before starting migration, understand the scope:

```bash
# Run simulation
./py2to3 simulate src/ --detailed -o planning_report.json

# Review the report
cat planning_report.json | python -m json.tool | less
```

Use the data to:
- Estimate time and resources needed
- Identify high-impact files
- Plan migration phases
- Set realistic timelines

### 2. Stakeholder Presentations

Generate professional reports for management:

```bash
# Create simulation report
./py2to3 simulate --detailed -o stakeholder_report.json

# Combine with other reports
./py2to3 estimate src/ -o effort_estimate.txt
./py2to3 risk src/ -o risk_analysis.txt
```

Present:
- Clear before/after metrics
- Estimated effort and timeline
- Risk assessment
- Projected success rate

### 3. Testing Migration Strategies

Compare different approaches:

```bash
# Strategy A: Default configuration
./py2to3 simulate src/ -o strategy_a.json

# Strategy B: Custom rules
./py2to3 config set aggressive_fixes true
./py2to3 simulate src/ -o strategy_b.json

# Compare results
diff strategy_a.json strategy_b.json
```

### 4. Training and Education

Help teams understand the migration:

```bash
# Show what will happen
./py2to3 simulate examples/ --verbose --detailed

# Let team members explore
./py2to3 patterns  # Show migration patterns
./py2to3 simulate --help  # Explain options
```

### 5. Pre-Flight Check

Final validation before starting:

```bash
# Full simulation with all details
./py2to3 simulate src/ --verbose --detailed -o preflight.json

# Review critical files
./py2to3 deps src/  # Check dependencies
./py2to3 risk src/  # Check risks

# If simulation looks good, proceed
./py2to3 backup create
./py2to3 fix src/
```

## Integration with Other Tools

The simulator works seamlessly with other py2to3 commands:

### Before Simulation

```bash
# Understand current state
./py2to3 status          # Quick status
./py2to3 stats src/      # Detailed statistics
./py2to3 deps src/       # Dependency analysis
```

### During Simulation

```bash
# Run simulation
./py2to3 simulate src/ --detailed -o sim.json

# Analyze results
python -m json.tool sim.json | less
```

### After Simulation

```bash
# If satisfied with simulation results
./py2to3 backup create         # Create safety backup
./py2to3 fix src/              # Apply actual fixes
./py2to3 check src/            # Verify results
./py2to3 compare sim.json      # Compare to simulation
```

## JSON Report Structure

The detailed JSON report contains:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "target_path": "src/",
  "files_analyzed": [
    {
      "path": "src/web/scraper.py",
      "changes_count": 15,
      "changes": [
        {
          "fix_type": "print_statements",
          "description": "Convert print statements to print() functions",
          "count": 8,
          "matches": ["print 'Starting...'", "print result"]
        }
      ]
    }
  ],
  "total_changes": 156,
  "changes_by_type": {
    "print_statements": 42,
    "iteritems_calls": 28,
    "urllib2_imports": 15
  },
  "file_previews": {
    "src/web/scraper.py": {
      "original": "#!/usr/bin/env python\nimport urllib2...",
      "modified": "#!/usr/bin/env python\nimport urllib.request...",
      "size_change": 12
    }
  },
  "summary": {
    "files_total": 25,
    "files_affected": 23,
    "files_unchanged": 2,
    "total_changes": 156,
    "issues_before": 143,
    "issues_after_estimated": 9,
    "estimated_success_rate": 93.7
  }
}
```

## Best Practices

### 1. Run Simulation First

Always simulate before applying fixes:

```bash
# ✅ Good
./py2to3 simulate src/ --detailed
# Review results, then:
./py2to3 fix src/

# ❌ Bad
./py2to3 fix src/  # No preview!
```

### 2. Save Simulation Reports

Keep records for comparison:

```bash
# Save with timestamp
./py2to3 simulate -o "simulation_$(date +%Y%m%d_%H%M%S).json"

# Compare before and after
./py2to3 simulate -o before_sim.json
./py2to3 fix src/
./py2to3 check src/ -o after_check.json
diff before_sim.json after_check.json
```

### 3. Use with Version Control

Track simulation results:

```bash
# Simulate and commit results
./py2to3 simulate -o simulation.json
git add simulation.json
git commit -m "Add migration simulation baseline"

# Later, compare
./py2to3 simulate -o simulation_new.json
diff simulation.json simulation_new.json
```

### 4. Combine with Other Reports

Build comprehensive picture:

```bash
# Full analysis
./py2to3 simulate src/ -o sim.json
./py2to3 estimate src/ -o estimate.txt
./py2to3 risk src/ -o risk.json
./py2to3 deps src/ -o deps.json

# Review all before starting
ls -lh *.json *.txt
```

## FAQ

### Q: Does simulation modify any files?

**A:** No! Simulation is completely safe and read-only. It analyzes your code and shows what *would* change, but doesn't modify anything.

### Q: How accurate is the simulation?

**A:** The simulation shows exact changes that would be made and accurately counts issues. The "remaining issues" estimate is conservative and typically accurate within 5-10%.

### Q: Can I simulate with custom rules?

**A:** Yes! Configure custom rules first, then run simulation:

```bash
./py2to3 rules add my_rules.json
./py2to3 simulate src/ -o with_custom_rules.json
```

### Q: How long does simulation take?

**A:** Very fast! Usually 1-5 seconds for small projects, 10-30 seconds for large ones. Much faster than actual migration since it doesn't create backups or modify files.

### Q: Can I simulate just one file?

**A:** Yes! Pass a file path instead of directory:

```bash
./py2to3 simulate src/specific_file.py
```

### Q: What if simulation shows issues?

**A:** Review the report carefully. Files with many changes or complex patterns may need manual review after automated fixes. Use:

```bash
./py2to3 risk src/      # Identify risky files
./py2to3 complexity src/  # Check complex files
```

## Troubleshooting

### "No Python files found"

- Check the path is correct
- Ensure you have .py files in the target directory
- Try: `find . -name "*.py"` to locate Python files

### "Permission denied"

- Ensure you have read access to the files
- Check directory permissions
- Try: `ls -la` to verify permissions

### Simulation is slow

- Large codebases (1000+ files) take longer
- Use verbose mode to see progress
- Consider simulating subdirectories separately

## Related Commands

- `./py2to3 preflight` - Safety checks before migration
- `./py2to3 fix` - Apply actual fixes
- `./py2to3 estimate` - Estimate migration effort
- `./py2to3 risk` - Analyze migration risks
- `./py2to3 compare` - Compare before/after
- `./py2to3 check` - Verify Python 3 compatibility

## Tips

💡 **Tip 1**: Run simulation regularly during migration to track progress

💡 **Tip 2**: Share simulation reports with team before starting

💡 **Tip 3**: Use JSON output for automated pipelines and analysis

💡 **Tip 4**: Combine with `--detailed` for stakeholder presentations

💡 **Tip 5**: Archive simulation reports for project documentation

## Summary

The Migration Simulator is your risk-free way to:
- ✅ Preview complete migration outcomes
- ✅ Understand scope and impact
- ✅ Generate accurate estimates
- ✅ Get stakeholder approval
- ✅ Plan migration strategy
- ✅ Train team members

Remember: **Simulate, Review, Then Migrate!** 🚀
