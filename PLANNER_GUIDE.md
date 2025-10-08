# Migration Planner Guide

The Migration Planner is a strategic planning tool that analyzes your codebase and creates an optimized migration plan for converting Python 2 code to Python 3. It helps teams approach large migrations systematically by breaking them down into manageable phases based on dependencies, complexity, and risk.

## 🎯 Why Use the Migration Planner?

Large codebases can have hundreds or thousands of files with complex interdependencies. The Migration Planner helps you:

- **Understand the full scope** of migration work before starting
- **Break down large migrations** into manageable phases
- **Migrate in optimal order** (leaf nodes first, then dependencies)
- **Estimate effort** for planning and resource allocation
- **Track progress** against a clear plan
- **Communicate effectively** with stakeholders using professional reports

## 🚀 Quick Start

### Basic Usage

Create a migration plan for your codebase:

```bash
# Analyze and display plan in console
./py2to3 plan src/

# Save plan to a text file
./py2to3 plan src/ -o migration_plan.txt

# Generate a Markdown report
./py2to3 plan src/ -f markdown -o migration_plan.md

# Generate a JSON file for CI/CD integration
./py2to3 plan src/ -f json -o migration_plan.json
```

## 📊 What the Planner Analyzes

### 1. File Dependencies

The planner builds a complete dependency graph by analyzing:
- `import` statements
- `from ... import` statements
- Internal module dependencies
- External package dependencies

### 2. Complexity Assessment

Each file is scored based on:
- **Lines of code** (larger files = higher complexity)
- **Number of Python 2 patterns** detected
- **Syntax errors** (may indicate complex migration issues)

### 3. Risk Classification

Files are classified into three risk levels:
- 🔴 **HIGH**: Complex files with many issues (>50 complexity score)
- 🟡 **MEDIUM**: Moderate complexity (26-50 complexity score)
- 🟢 **LOW**: Simple files with few issues (<25 complexity score)

### 4. Effort Estimation

The planner estimates migration hours based on:
- Lines of code (approximately 100 LOC per hour)
- Number of issues (0.5 hours per issue)
- Historical migration data

## 📋 Understanding the Migration Plan

### Phase Structure

The planner creates a phased approach:

**Phase 1**: **Leaf nodes** - Files with no internal dependencies
- Safest to migrate first
- Won't break other files
- Good for learning and establishing patterns

**Phase 2-N**: **Dependency layers** - Files whose dependencies have been migrated
- Each phase builds on previous phases
- Ensures dependencies are Python 3 compatible before migrating dependent files

**Final Phase**: **Circular dependencies** (if any)
- Files with circular import relationships
- May require refactoring to break cycles
- Highest coordination needed

### Reading the Plan Output

#### Text Format

```
================================================================================
PYTHON 2 TO 3 MIGRATION PLAN
================================================================================

Generated: 2024-01-15 10:30:00
Root Path: /path/to/project
Total Files: 45
Total Phases: 5
Estimated Total Hours: 38.5

================================================================================
SUMMARY BY RISK LEVEL
================================================================================
HIGH    :  12 files,   15.5 hours
MEDIUM  :  18 files,   14.0 hours
LOW     :  15 files,    9.0 hours

================================================================================
MIGRATION PHASES
================================================================================

────────────────────────────────────────────────────────────────────────────────
Phase 1: 8 files, ~6.5 hours
────────────────────────────────────────────────────────────────────────────────

  📄 utils/validators.py
     Risk: HIGH   | LOC:  350 | Complexity:  65 | Est: 2.5h
     Issues: 8
       • print statement
       • basestring type
       • unicode function
       ...
     Used by: 5 file(s)
```

#### Markdown Format

Generates a beautiful Markdown document with:
- Tables with emoji indicators
- Expandable sections
- Easy sharing on GitHub, GitLab, etc.
- Great for documentation and team communication

#### JSON Format

Machine-readable format perfect for:
- CI/CD pipeline integration
- Custom reporting tools
- Progress tracking systems
- Data analysis

```json
{
  "metadata": {
    "generated": "2024-01-15T10:30:00",
    "root_path": "/path/to/project",
    "total_files": 45,
    "total_phases": 5,
    "estimated_total_hours": 38.5
  },
  "phases": [
    {
      "phase_number": 1,
      "file_count": 8,
      "estimated_hours": 6.5,
      "files": [...]
    }
  ]
}
```

## 💡 Best Practices

### 1. Plan Before You Start

Always create a migration plan before beginning work:
```bash
./py2to3 plan src/ -o migration_plan.txt
```

Review the plan with your team to:
- Understand the scope
- Allocate resources
- Set realistic timelines
- Identify potential challenges

### 2. Follow the Phases

Stick to the recommended phase order:
```bash
# Phase 1 files first
./py2to3 fix src/utils/validators.py
./py2to3 fix src/utils/helpers.py

# Test before moving to Phase 2
pytest tests/

# Then Phase 2 files
./py2to3 fix src/models/user.py
...
```

### 3. Track Progress

Re-run the planner periodically to track progress:
```bash
# Initial plan
./py2to3 plan src/ -o plan_initial.txt

# After Phase 1
./py2to3 plan src/ -o plan_phase1_complete.txt

# Compare progress
diff plan_initial.txt plan_phase1_complete.txt
```

### 4. Update the Plan

If you need to adjust priorities or discover new issues:
```bash
# Regenerate plan with current state
./py2to3 plan src/ -o migration_plan_updated.txt
```

### 5. Communicate with Reports

Share Markdown reports with stakeholders:
```bash
# Create shareable report
./py2to3 plan src/ -f markdown -o MIGRATION_PLAN.md

# Add to git for team visibility
git add MIGRATION_PLAN.md
git commit -m "Add migration plan"
```

## 🔄 Integration with Other Tools

### With Git Integration

```bash
# Create migration branch
./py2to3 git branch py3-migration

# Create initial plan
./py2to3 plan src/ -f markdown -o MIGRATION_PLAN.md
git add MIGRATION_PLAN.md
./py2to3 git checkpoint "Initial migration plan created"

# Migrate Phase 1
./py2to3 fix src/utils/validators.py
./py2to3 git commit "phase1-validators" -m "Migrate validators.py (Phase 1)"
```

### With Preflight Checks

```bash
# Run preflight before creating plan
./py2to3 preflight src/

# Create plan
./py2to3 plan src/ -o migration_plan.txt

# Address preflight issues first, then follow plan
```

### With Risk Analysis

```bash
# Create plan
./py2to3 plan src/ -o plan.txt

# Analyze risks for high-complexity files
./py2to3 risk src/ -o risk_assessment.txt

# Prioritize review of high-risk files from Phase 1
```

### With Stats Tracking

```bash
# Create baseline plan
./py2to3 plan src/ -f json -o plan_baseline.json

# Track progress
./py2to3 stats src/ -f json -o stats_week1.json
./py2to3 stats src/ -f json -o stats_week2.json

# Compare to see improvement
```

## 📈 Advanced Usage

### Custom Analysis

You can import and use the planner programmatically:

```python
from migration_planner import MigrationPlanner

planner = MigrationPlanner("src/")
planner.analyze_codebase()
planner.create_migration_plan()

# Access plan data
for phase_num, files in enumerate(planner.phases, 1):
    print(f"Phase {phase_num}: {len(files)} files")
    for filepath in files:
        analysis = planner.files[filepath]
        print(f"  - {filepath}: {analysis.risk_level}")

# Export in multiple formats
planner.export_text("plan.txt")
planner.export_json("plan.json")
planner.export_markdown("plan.md")
```

### CI/CD Integration

Include planning in your CI/CD pipeline:

```yaml
# .github/workflows/migration-progress.yml
- name: Generate Migration Plan
  run: |
    ./py2to3 plan src/ -f json -o migration_plan.json
    
- name: Upload Plan
  uses: actions/upload-artifact@v3
  with:
    name: migration-plan
    path: migration_plan.json
```

### Progress Dashboard

Create a dashboard using the JSON output:

```bash
# Generate plan data
./py2to3 plan src/ -f json -o plan.json

# Use with your favorite visualization tool
# (Grafana, custom web dashboard, etc.)
```

## 🎨 Output Examples

### Console Output (Quick View)

Perfect for quick checks and terminal-based workflows.

### Text File (Detailed Report)

Comprehensive report with all details, great for:
- Email attachments
- Project documentation
- Review meetings

### Markdown (Team Collaboration)

Beautiful formatted reports with:
- Emoji indicators for quick scanning
- Tables for structured data
- Great rendering on GitHub/GitLab
- Easy to read and share

### JSON (Automation)

Machine-readable format for:
- CI/CD pipelines
- Custom tooling
- Data analysis
- Progress tracking systems

## 🔍 Troubleshooting

### "No Python files found"

Make sure you're pointing to the correct directory:
```bash
./py2to3 plan src/  # Not just 'src' if you're in parent directory
```

### "Circular dependencies detected"

This is normal! The planner handles them by:
1. Grouping them in the final phase
2. Flagging them for review
3. Suggesting they may need refactoring

### Inaccurate Estimates

Time estimates are approximations based on:
- Industry averages
- Code complexity
- Issue counts

Actual time may vary based on:
- Developer experience
- Code quality
- Testing requirements
- Your specific patterns

Use estimates for planning, but track actual time for future projects.

## 📚 Related Commands

- `./py2to3 preflight` - Run before planning to ensure environment is ready
- `./py2to3 check` - Check specific files for compatibility
- `./py2to3 fix` - Apply fixes to files
- `./py2to3 risk` - Analyze risk levels
- `./py2to3 stats` - Track migration statistics
- `./py2to3 deps` - Analyze dependencies
- `./py2to3 git` - Git integration for tracking

## 🤝 Tips for Success

1. **Review the plan with your team** before starting
2. **Start small** - Migrate Phase 1 first to learn patterns
3. **Test thoroughly** after each phase
4. **Use git checkpoints** between phases
5. **Update the plan** if priorities change
6. **Share progress** using Markdown reports
7. **Learn from high-risk files** - they may reveal common issues
8. **Celebrate milestones** - each phase completed is progress!

## 📖 Example Workflow

Here's a complete example workflow using the planner:

```bash
# 1. Initial setup
./py2to3 preflight src/
./py2to3 git branch py3-migration

# 2. Create and review plan
./py2to3 plan src/ -f markdown -o MIGRATION_PLAN.md
cat MIGRATION_PLAN.md  # Review with team

# 3. Start Phase 1
for file in $(grep "Phase 1:" MIGRATION_PLAN.md | grep "📄" | awk '{print $2}'); do
    echo "Migrating $file..."
    ./py2to3 check "$file"
    ./py2to3 fix "$file"
    ./py2to3 test-gen "$file" -o tests/
    pytest tests/
    ./py2to3 git commit "phase1" -m "Migrate $file"
done

# 4. Update plan after Phase 1
./py2to3 plan src/ -f markdown -o MIGRATION_PLAN_UPDATED.md

# 5. Continue with remaining phases...
```

## 🎓 Learning Resources

- **[CLI_GUIDE.md](CLI_GUIDE.md)** - Complete CLI documentation
- **[GIT_INTEGRATION.md](GIT_INTEGRATION.md)** - Git workflow integration
- **[RISK_GUIDE.md](RISK_GUIDE.md)** - Understanding risk analysis
- **[TEST_GEN_GUIDE.md](TEST_GEN_GUIDE.md)** - Generating tests for migrated code

---

**Ready to plan your migration?**

```bash
./py2to3 plan src/ -o migration_plan.txt
```

Good luck with your migration! 🚀
