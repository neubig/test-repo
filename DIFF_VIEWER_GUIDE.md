# 🔍 Interactive Diff Viewer Guide

The **Interactive Diff Viewer** is a powerful tool that generates beautiful, interactive HTML pages showing side-by-side comparisons of your code before and after migration. Perfect for code review, training, and understanding the impact of migration changes!

## ✨ Features

- **📊 Visual Comparison**: See exactly what changed with side-by-side and unified diff views
- **🎨 Syntax Highlighting**: Beautiful color-coded diffs for easy reading
- **📈 Statistics Dashboard**: Track additions, deletions, and file changes at a glance
- **🔄 Toggle Views**: Switch between side-by-side and unified diff formats
- **🗂️ Easy Navigation**: Jump directly to any file with the built-in file navigator
- **📱 Responsive Design**: Works great on desktop and mobile browsers
- **🎯 Zero Dependencies**: Pure HTML, CSS, and JavaScript - no external libraries needed

## 🚀 Quick Start

### Basic Usage

Generate a diff viewer for your entire project:

```bash
./py2to3 diff-viewer
```

This will:
1. Scan all Python files in the current directory
2. Compare them with their backups in `.migration_backups/`
3. Generate `diff_viewer.html` with an interactive comparison

Then open the generated file in your browser:

```bash
# macOS
open diff_viewer.html

# Linux
xdg-open diff_viewer.html

# Windows
start diff_viewer.html
```

### Analyze a Specific Directory

```bash
./py2to3 diff-viewer src/
```

### Analyze a Single File

```bash
./py2to3 diff-viewer src/core/app.py
```

### Custom Output File

```bash
./py2to3 diff-viewer -o my_migration_review.html
```

### Custom Backup Directory

```bash
./py2to3 diff-viewer -b backups/
```

## 📖 Use Cases

### 1. Code Review

Perfect for reviewing migration changes before committing:

```bash
# After running the fixer
./py2to3 fix src/ --backup-dir .migration_backups

# Generate interactive diff viewer
./py2to3 diff-viewer src/ -o review.html

# Review changes in your browser
open review.html
```

### 2. Team Training

Create training materials showing common Python 2 to 3 changes:

```bash
# Generate diff for specific examples
./py2to3 diff-viewer examples/ -o training_examples.html
```

Share the HTML file with your team to help them understand:
- What patterns change during migration
- Why certain changes are necessary
- How to recognize Python 2 vs Python 3 code

### 3. Stakeholder Presentations

Generate professional reports for non-technical stakeholders:

```bash
# Create comprehensive diff viewer
./py2to3 diff-viewer -o migration_progress.html

# Present the HTML in meetings to show:
# - What has changed
# - How much work has been done
# - Code quality improvements
```

### 4. Documentation

Document your migration journey:

```bash
# Generate diffs at different stages
./py2to3 diff-viewer -o phase1_imports.html  # After import fixes
./py2to3 diff-viewer -o phase2_syntax.html   # After syntax fixes
./py2to3 diff-viewer -o phase3_final.html    # After final review
```

### 5. Quality Assurance

Verify that automated fixes are correct:

```bash
# Generate diff viewer
./py2to3 diff-viewer src/

# Review each file to ensure:
# - No unintended changes
# - All changes are appropriate
# - Code still functions correctly
```

## 🎯 Understanding the Output

### Summary Section

The summary section shows:
- **Total Files Analyzed**: How many Python files were compared
- **Files With Changes**: How many files actually have differences
- **Total Additions**: Lines added (shown in green)
- **Total Deletions**: Lines removed (shown in red)

### Navigation Panel

The navigation panel lists all files with changes, showing:
- 📄 File icon and path
- ➕ Number of additions (green)
- ➖ Number of deletions (red)

Click any file to jump directly to its diff section.

### Diff Sections

Each file has its own diff section with:

#### Side-by-Side View (Default)
- **Left pane**: Original code (backup)
- **Right pane**: Modified code (current)
- **Color coding**:
  - 🟥 Red: Deleted lines
  - 🟩 Green: Added lines
  - ⬜ White: Unchanged lines

#### Unified Diff View
- Traditional unified diff format
- Lines prefixed with `-` (removed)
- Lines prefixed with `+` (added)
- Context lines show surrounding code

### Interactive Controls

- **Side by Side button**: Show side-by-side comparison (default)
- **Unified Diff button**: Show traditional unified diff format
- **Smooth scrolling**: Click file names in navigation to scroll smoothly to that section

## 💡 Tips and Best Practices

### Before Using the Diff Viewer

1. **Run the fixer with backups enabled**:
   ```bash
   ./py2to3 fix src/ --backup-dir .migration_backups
   ```

2. **Verify backups exist**:
   ```bash
   ls -la .migration_backups/
   ```

### Effective Code Review

1. **Start with statistics**: Look at the summary to get a high-level overview
2. **Review navigation**: Scan the file list to identify which files changed most
3. **Prioritize review**: Focus on files with the most changes first
4. **Use side-by-side**: Side-by-side view is best for detailed review
5. **Switch to unified**: Use unified diff for a traditional review experience
6. **Check context**: Make sure changes make sense in context

### Integration with Workflow

```bash
# Step 1: Run migration with backups
./py2to3 fix src/ --backup-dir .migration_backups

# Step 2: Generate diff viewer for review
./py2to3 diff-viewer src/ -o review.html

# Step 3: Review changes in browser
open review.html

# Step 4: If changes look good, commit
git add src/
git commit -m "Apply Python 2 to 3 migration fixes"

# Step 5: Archive the diff viewer with your commit
git add review.html
git commit -m "Add migration diff viewer for documentation"
```

### Sharing with Team

The diff viewer is a single, self-contained HTML file that can be:
- ✉️ **Emailed**: Send as an attachment
- 📦 **Archived**: Commit to your repository for historical reference
- 🌐 **Hosted**: Upload to internal web server or wiki
- 💬 **Shared**: Upload to Slack, Teams, or other collaboration tools

No dependencies or external resources required!

## 🔧 Advanced Usage

### Multiple Diff Viewers for Different Stages

Track your migration progress by generating diffs at each stage:

```bash
# After fixing imports
./py2to3 diff-viewer -o stage1_imports.html

# After fixing syntax
./py2to3 diff-viewer -o stage2_syntax.html

# After manual review and fixes
./py2to3 diff-viewer -o stage3_final.html
```

### Combining with Other Tools

```bash
# Generate stats, then diff viewer
./py2to3 stats collect --save
./py2to3 diff-viewer -o review_$(date +%Y%m%d).html

# Generate report card, then diff viewer
./py2to3 report-card -o report_card.html
./py2to3 diff-viewer -o detailed_diffs.html
```

### Custom Workflows

```bash
# Review specific subsystems
./py2to3 diff-viewer src/core/ -o core_review.html
./py2to3 diff-viewer src/utils/ -o utils_review.html
./py2to3 diff-viewer src/web/ -o web_review.html

# Compare specific backup directories
./py2to3 diff-viewer -b backups/phase1/ -o phase1_review.html
./py2to3 diff-viewer -b backups/phase2/ -o phase2_review.html
```

## 🎨 Customization

The diff viewer generates a self-contained HTML file with embedded CSS and JavaScript. While it's designed to work out of the box, you can customize it by:

1. **Generating the file**:
   ```bash
   ./py2to3 diff-viewer -o my_diff.html
   ```

2. **Editing the HTML**: Open `my_diff.html` in a text editor and modify:
   - Colors in the `<style>` section
   - Layout and spacing
   - Interactive behavior in the `<script>` section

## 🐛 Troubleshooting

### "Backup directory not found"

**Problem**: The backup directory doesn't exist.

**Solution**: Run the fixer with backups first:
```bash
./py2to3 fix src/ --backup-dir .migration_backups
```

### "No Python files found to compare"

**Problem**: No Python files in the specified path, or no backups exist for them.

**Solution**: 
- Verify the path contains Python files: `find . -name "*.py"`
- Check if backups exist: `ls -la .migration_backups/`
- Make sure backups were created during fixing

### HTML file is very large

**Problem**: For large projects, the HTML file can be several MB.

**Solution**: Generate separate diff viewers for subsections:
```bash
./py2to3 diff-viewer src/core/ -o core_diff.html
./py2to3 diff-viewer src/utils/ -o utils_diff.html
```

### Browser performance issues

**Problem**: Large diffs can be slow to render in the browser.

**Solution**: 
- Use a modern browser (Chrome, Firefox, Edge, Safari)
- Close other browser tabs to free memory
- Split large projects into smaller sections

## 📚 Related Commands

- **`./py2to3 compare`**: Compare migration progress between branches/commits
- **`./py2to3 backup`**: Manage backup files
- **`./py2to3 report`**: Generate comprehensive HTML reports with charts
- **`./py2to3 review`**: Interactive code review assistance
- **`./py2to3 convert`**: Quick snippet converter with side-by-side view

## 🎯 Examples

### Example 1: Full Project Review

```bash
# Fix the entire project
./py2to3 fix . --backup-dir .migration_backups

# Generate comprehensive diff viewer
./py2to3 diff-viewer -o project_review.html

# Review and commit
open project_review.html
# After review...
git add .
git commit -m "Python 2 to 3 migration - reviewed via diff viewer"
```

### Example 2: Incremental Migration

```bash
# Fix module by module
./py2to3 fix src/core/ --backup-dir .migration_backups
./py2to3 diff-viewer src/core/ -o core_diff.html
open core_diff.html
# Review and test...

./py2to3 fix src/utils/ --backup-dir .migration_backups
./py2to3 diff-viewer src/utils/ -o utils_diff.html
open utils_diff.html
# Review and test...
```

### Example 3: Team Review Process

```bash
# Developer generates diff
./py2to3 diff-viewer -o migration_$(date +%Y%m%d)_$(whoami).html

# Upload to team wiki or share drive
cp migration_*.html /shared/migration_reviews/

# Team reviews and approves
# Proceed with merge
```

## 🆘 Getting Help

- Run `./py2to3 diff-viewer --help` for command-line options
- Check [README.md](README.md) for general toolkit information
- See [CLI_GUIDE.md](CLI_GUIDE.md) for all available commands
- Visit [BACKUP_GUIDE.md](BACKUP_GUIDE.md) for backup management

## 🎉 Summary

The Interactive Diff Viewer makes migration review easy and visual:

✅ **Generate** beautiful HTML diffs with one command  
✅ **Review** changes side-by-side or in unified format  
✅ **Navigate** easily between files  
✅ **Share** self-contained HTML with team members  
✅ **Track** additions, deletions, and modifications  
✅ **Learn** from real migration examples  

Perfect for code review, training, documentation, and quality assurance!

---

**Quick Reference**:
```bash
# Basic usage
./py2to3 diff-viewer

# Specific directory
./py2to3 diff-viewer src/

# Custom output
./py2to3 diff-viewer -o my_review.html

# Custom backup dir
./py2to3 diff-viewer -b backups/

# Get help
./py2to3 diff-viewer --help
```
