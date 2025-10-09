# Smart Migration Wizard Guide

## Overview

The **Smart Migration Wizard** is an interactive, beginner-friendly tool that guides you through the entire Python 2 to Python 3 migration process step-by-step. Instead of running individual commands and piecing together a workflow, the wizard asks you questions about your project and automatically orchestrates the right sequence of operations tailored to your needs.

## Why Use the Wizard?

- **Perfect for beginners**: No need to learn all the commands - just answer questions
- **Intelligent recommendations**: Get personalized migration strategies based on your project
- **Automated workflow**: The wizard runs the right commands in the right order
- **Safety-first approach**: Automatic backups and checkpoints before making changes
- **Progress tracking**: Visual feedback at every step
- **Error handling**: Graceful error recovery with helpful suggestions
- **Educational**: Learn best practices while migrating

## Quick Start

### Basic Usage

Run the wizard in your project directory:

```bash
./py2to3 wizard
```

Or specify a project path:

```bash
./py2to3 wizard /path/to/your/project
```

That's it! The wizard will guide you through the rest.

## What the Wizard Does

### 1. Welcome & Introduction

The wizard starts by welcoming you and explaining what it will do.

### 2. Project Assessment

The wizard automatically analyzes your project:
- Counts Python files and lines of code
- Detects test files and test frameworks
- Checks for git repository
- Finds dependency files (requirements.txt, setup.py, etc.)
- Categorizes project size (small/medium/large)

### 3. Requirements Gathering

The wizard asks you questions to understand your needs:

**Experience Level:**
- Beginner: New to Python 3
- Intermediate: Familiar with Python 3 basics
- Advanced: Very comfortable with Python 3

**Migration Approach:**
- Safe and gradual: Review everything manually
- Balanced: Auto-fix safe issues, review complex ones (recommended)
- Fast and automated: Auto-fix as much as possible

**Additional Preferences:**
- Create backups (if no git repository)
- Run tests after migration
- Generate detailed HTML report

### 4. Strategy Recommendations

Based on your project and preferences, the wizard:
- Estimates migration effort (time needed)
- Assesses complexity level
- Provides specific recommendations
- Identifies potential issues early
- Suggests best practices

### 5. Migration Plan

The wizard shows you a detailed plan before executing:
- All steps that will be performed
- Commands that will be run
- Expected outcomes at each stage
- Warnings and important notes

You can review this plan and decide whether to proceed.

### 6. Execution

If you approve, the wizard executes the migration:
- Runs pre-flight safety checks
- Creates backups or git checkpoints
- Checks Python 3 compatibility
- Analyzes dependencies
- Applies automated fixes
- Verifies results
- Runs tests (if applicable)
- Generates reports

At each step, you can see progress and decide whether to continue if issues arise.

### 7. Results & Next Steps

Finally, the wizard:
- Shows a summary of what was accomplished
- Provides recommendations for next steps
- Offers to commit changes (if using git)
- Celebrates your successful migration! 🎉

## Workflow Example

Here's what a typical wizard session looks like:

```bash
$ ./py2to3 wizard

======================================================================
               🚀 Smart Migration Wizard 🚀
======================================================================

Welcome! This wizard will guide you through migrating your Python 2
project to Python 3. I'll analyze your project, recommend a strategy,
and help you execute the migration step-by-step.

📁 Project: /home/user/my-project
----------------------------------------------------------------------

Ready to start the migration wizard? [Y/n]: y

📊 Step 1: Assessing your project...
----------------------------------------------------------------------

✓ Found 45 Python files
✓ Total lines of code: ~3,245
✓ Test files: 12
✓ Git repository: Yes
✓ Dependency files: requirements.txt, setup.py

📏 Project size: MEDIUM

💬 Step 2: Understanding your requirements...
----------------------------------------------------------------------

1. What's your experience level with Python 3?
   a) Beginner - New to Python 3
   b) Intermediate - Familiar with Python 3 basics
   c) Advanced - Very comfortable with Python 3

Your choice [a/b/c] (default: b): b

2. What migration approach do you prefer?
   a) Safe and gradual - Review everything manually
   b) Balanced - Auto-fix safe issues, review complex ones
   c) Fast and automated - Auto-fix as much as possible

Your choice [a/b/c] (default: b): b

✓ Git detected - we'll track all changes through git

3. Would you like to run tests after migration? [Y/n]: y

4. Generate a detailed HTML report of the migration? [Y/n]: y

🎯 Step 3: Generating migration strategy...
----------------------------------------------------------------------

📊 Estimated effort: 4-8 hours
📊 Complexity: Medium

📋 Step 4: Migration Plan
======================================================================

Based on your project and preferences, here's the recommended plan:

1. Pre-flight Safety Checks
   → Validate environment and check for potential issues
   💻 Command: ./py2to3 preflight

2. Create Git Checkpoint
   → Create a git checkpoint before migration
   💻 Command: ./py2to3 git checkpoint "pre-migration"

3. Check Python 3 Compatibility
   → Scan code for Python 2 patterns and incompatibilities
   💻 Command: ./py2to3 check .

... (more steps)

Would you like to proceed with the migration? [Y/n]: y

🚀 Step 5: Executing Migration
======================================================================

[1/8] Pre-flight Safety Checks
----------------------------------------------------------------------
Running pre-flight safety checks...
✓ Pre-flight Safety Checks completed successfully

... (more steps executed)

======================================================================
                  🎉 Migration Complete! 🎉
======================================================================

✓ Completed 8/8 steps successfully

📝 Recommended Next Steps:
----------------------------------------------------------------------
1. Review the changes made to your code
2. Test your application thoroughly
3. Update your documentation and README
4. Consider adding type hints (run: ./py2to3 typehints)
5. Run code quality checks (run: ./py2to3 quality)
6. Update your CI/CD pipeline for Python 3

📊 View your migration report: migration_report.html

Would you like to commit these changes now? [Y/n]: y

✓ Changes committed to git

🎊 Congratulations on migrating to Python 3!
======================================================================
```

## Advanced Features

### Saving Migration Plans

If you're not ready to execute the migration immediately, the wizard can save your plan:

```bash
# When asked "Would you like to proceed with the migration?", answer "n"
# The wizard will save migration_plan.json with your configuration
```

You can review this plan and run the wizard again later.

### Pausing and Resuming

The wizard allows you to pause at any step if issues arise. You can:
- Review the issue
- Manually fix problems
- Re-run the wizard to continue

### Error Recovery

If a step fails:
- The wizard explains what went wrong
- You can choose to continue or stop
- Previous steps remain intact (thanks to backups/git)
- You can rollback if needed

## Tips for Best Results

### Before Running the Wizard

1. **Commit your changes**: Make sure you have no uncommitted work
2. **Create a branch**: Use `git checkout -b python3-migration`
3. **Backup important data**: Even though the wizard creates backups
4. **Read the migration guide**: Familiarize yourself with common issues

### During Migration

1. **Read each question carefully**: The wizard tailors the workflow to your answers
2. **Don't rush**: Take time to understand each step
3. **Review changes**: Look at what was changed before committing
4. **Test thoroughly**: Run your test suite and manual tests

### After Migration

1. **Review the report**: Check the HTML report for details
2. **Update documentation**: Document Python 3 requirements
3. **Update CI/CD**: Configure your pipeline for Python 3
4. **Consider modernization**: Use newer Python 3 features

## Comparison with Manual Approach

### Manual Approach

```bash
# Multiple commands to run in sequence
./py2to3 preflight
./py2to3 git checkpoint "pre-migration"
./py2to3 check .
./py2to3 deps .
./py2to3 fix .
./py2to3 check . --post-migration
pytest
./py2to3 report -o migration_report.html
git add .
git commit -m "Migrate to Python 3"
```

**Pros:**
- Full control over each step
- Can customize flags and options
- Good for experienced users

**Cons:**
- Need to know the right sequence
- Easy to miss important steps
- No personalized recommendations
- Manual coordination required

### Wizard Approach

```bash
# Single command with interactive guidance
./py2to3 wizard
```

**Pros:**
- One command does everything
- Personalized recommendations
- No prior knowledge needed
- Can't skip important steps
- Educational and guided
- Error recovery built-in

**Cons:**
- Less granular control
- Interactive (not suitable for scripting)
- Takes slightly longer due to questions

## Integration with Other Tools

The wizard integrates seamlessly with other py2to3 tools:

### After the Wizard

Run additional tools to enhance your migration:

```bash
# Add type hints
./py2to3 typehints .

# Run quality checks
./py2to3 quality .

# Modernize code patterns
./py2to3 modernize .

# Generate documentation
./py2to3 docs .
```

### Using Wizard for Initial Migration

```bash
# Use wizard for initial migration
./py2to3 wizard

# Then use specific tools for refinement
./py2to3 review .
./py2to3 optimize .
```

## Troubleshooting

### Wizard Won't Start

```bash
# Check if migration_wizard.py exists
ls src/migration_wizard.py

# Try running with verbose mode
./py2to3 wizard --verbose
```

### Wizard Stops Unexpectedly

- Check the error message
- Review logs if available
- Use git to see what was changed: `git diff`
- Can rollback: `./py2to3 rollback undo`

### Want to Restart

```bash
# If you have git checkpoint
git reset --hard

# Or restore from backup
./py2to3 backup restore
```

## FAQ

### Q: Can I run the wizard multiple times?

**A:** Yes! The wizard is idempotent. Running it multiple times is safe, especially if you've fixed issues between runs.

### Q: Can I use the wizard in CI/CD?

**A:** The wizard is interactive, so it's not suitable for CI/CD. For automated pipelines, use the individual commands or the `migrate` command with appropriate flags.

### Q: Does the wizard work with large projects?

**A:** Yes! The wizard adapts its strategy based on project size. For large projects, it recommends incremental migration approaches.

### Q: What if I disagree with the wizard's recommendations?

**A:** You can always exit the wizard and run individual commands manually for full control. The wizard is designed for convenience, not to replace expert judgment.

### Q: Can I customize the wizard's behavior?

**A:** The wizard respects your `.py2to3.config.json` settings. Configure your preferences there, and the wizard will use them.

## Examples

### Small Project (< 1000 lines)

Perfect for the wizard! Quick migration in 1-2 hours.

```bash
./py2to3 wizard
# Answer questions
# Let it run
# Done!
```

### Medium Project (1000-10000 lines)

Wizard provides balanced approach with automated fixes and selective review.

```bash
./py2to3 wizard
# Choose "Balanced" approach
# Review complex changes
# Run tests
# Commit
```

### Large Project (> 10000 lines)

Wizard recommends incremental migration with careful review.

```bash
./py2to3 wizard
# Choose "Safe and gradual" approach
# Wizard suggests breaking it down
# Follow the multi-phase plan
# Migrate module by module
```

## Best Practices

1. **Use a clean branch**: Start fresh for clarity
2. **One module at a time**: For large projects, migrate incrementally
3. **Test at every step**: Don't accumulate untested changes
4. **Review auto-fixes**: Even "safe" fixes deserve a look
5. **Keep the report**: Document what was changed
6. **Share with the team**: Use the report for code review
7. **Update documentation**: Don't forget README, requirements, etc.

## Getting Help

If you need help:

1. **Read the error message**: The wizard provides helpful messages
2. **Check the guide**: This document covers common scenarios
3. **View the report**: The HTML report has details
4. **Use verbose mode**: `./py2to3 wizard --verbose`
5. **Check individual tool docs**: Each tool has its own guide

## Conclusion

The Smart Migration Wizard is the easiest way to migrate to Python 3. It combines the power of all py2to3 tools with intelligent orchestration and beginner-friendly guidance.

**Remember**: The wizard is a guide, not a replacement for understanding. Take time to learn why changes are made, and you'll become proficient with both Python 3 and the py2to3 toolkit!

Happy migrating! 🚀
