# Pull Request Generator Guide 🔀

The Pull Request Generator is an intelligent tool that automatically creates comprehensive pull requests for your Python 2 to 3 migration changes. It analyzes your changes, generates rich PR descriptions with statistics, suggests reviewers based on code ownership, and can even create PRs automatically on GitHub.

## 🌟 Features

- **Automated PR Creation**: Create PRs directly on GitHub via API
- **Rich Descriptions**: Generate detailed PR descriptions with migration statistics
- **Smart Analysis**: Detect and categorize migration patterns automatically
- **Code Ownership**: Suggest reviewers based on git blame analysis
- **Module Grouping**: Group changes by module for better organization
- **Testing Checklists**: Include comprehensive testing checklists
- **Draft Mode**: Create draft PRs for review before publishing
- **Custom Labels**: Add migration-specific labels automatically

## 🚀 Quick Start

### Generate a PR Draft

The simplest way to get started is to generate a PR draft file:

```bash
./py2to3 pr --output MY_PR.md
```

This creates a markdown file with a complete PR title and description that you can:
- Review and edit before creating the PR
- Copy and paste into GitHub's PR creation interface
- Use as a template for manual PR creation

### Create a PR on GitHub Automatically

If you have a GitHub token set up, you can create PRs directly:

```bash
# Set your GitHub token (one time setup)
export GITHUB_TOKEN="your_github_personal_access_token"

# Create a PR automatically
./py2to3 pr --create
```

## 📋 Prerequisites

### For Draft Generation
- Git repository with committed changes
- Changes on a feature branch (not main/master)
- Python files with migration changes

### For Automatic PR Creation
- All of the above, plus:
- GitHub personal access token with `repo` scope
- `requests` library installed (`pip install requests`)
- Git remote pointing to a GitHub repository

## 🎯 Usage Examples

### Basic Draft Generation

Generate a simple PR draft:

```bash
./py2to3 pr
```

This creates `PR_DRAFT.md` in your repository root with:
- Auto-generated title based on changed files
- Migration statistics
- Files organized by module
- Testing checklist
- Suggested reviewers

### Custom Title and Output

Specify a custom title and output file:

```bash
./py2to3 pr --title "Fix: Migrate authentication module to Python 3" --output auth_pr.md
```

### Create Draft PR on GitHub

Create a draft PR for review before publishing:

```bash
./py2to3 pr --create --draft
```

Draft PRs are perfect for:
- Getting early feedback from teammates
- Running CI/CD checks before official review
- Iterating on changes before formal submission

### Add Labels to PR

Add migration-specific labels automatically:

```bash
./py2to3 pr --create --labels migration python3 automated
```

### Specify Base Branch

If your main branch is named differently:

```bash
./py2to3 pr --create --base-branch master
```

Or for feature branch merges:

```bash
./py2to3 pr --create --base-branch develop
```

## 📊 Generated PR Content

### PR Title

Automatically generated based on changed files:

- **Single module**: `Python 3 Migration: auth module (5 files)`
- **Multiple modules**: `Python 3 Migration: auth, utils, core (12 files)`

### PR Description Sections

#### 1. Overview
Brief explanation that this is an automated migration PR.

#### 2. Migration Statistics
- Total files modified
- Total changes made
- Changes broken down by type:
  - Print statements
  - Import changes
  - Exception syntax
  - Iterator methods
  - String types
  - And more...

#### 3. Modified Files by Module
Files organized by their module/package for easy navigation:

```
### auth (5 files)
- `src/auth/login.py`
- `src/auth/session.py`
...

### utils (3 files)
- `src/utils/validators.py`
...
```

#### 4. Testing Checklist
Comprehensive checklist including:
- [ ] All unit tests pass
- [ ] Manual testing completed
- [ ] No Python 2 syntax remains
- [ ] Imports work correctly
- [ ] String handling verified
- [ ] Exception handling verified
- [ ] Performance acceptable

#### 5. Review Notes
Key areas to focus on during code review:
- Automated vs manual changes
- String/unicode handling
- Iterator performance implications
- Import correctness

#### 6. Suggested Reviewers
Based on git blame analysis, suggests the top contributors to the modified files.

## 🔧 Advanced Features

### Smart Change Detection

The generator analyzes your diffs and detects specific migration patterns:

- **Print Statements**: `print "x"` → `print("x")`
- **Import Changes**: `import urllib2` → `import urllib.request`
- **Exception Syntax**: `except E, e:` → `except E as e:`
- **Iterator Methods**: `.iteritems()` → `.items()`
- **String Types**: `basestring` → `str`
- **Range Functions**: `xrange()` → `range()`

### Code Ownership Analysis

Uses `git log` to identify the main contributors to each file:

```bash
# For each modified file, analyzes commit history
# Suggests top 3 contributors as reviewers
# Helps ensure proper domain expertise in reviews
```

### Module Grouping

Intelligently groups files by their top-level module or package:

```
src/
├── auth/           → "auth" group
├── utils/          → "utils" group
├── core/           → "core" group
└── standalone.py   → "root" group
```

This helps reviewers focus on related changes together.

## 🔐 GitHub Token Setup

To create PRs automatically, you need a GitHub personal access token:

### Create a Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "py2to3 PR Generator"
4. Select scopes: check **`repo`** (full control of private repositories)
5. Click "Generate token"
6. Copy the token immediately (you won't see it again!)

### Set the Token

**Option 1: Environment Variable (Recommended)**

```bash
# In your ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Or for current session only
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

**Option 2: Pass to Constructor (Programmatic Use)**

```python
from pr_generator import PRGenerator

generator = PRGenerator(github_token="ghp_xxxxxxxxxxxxxxxxxxxx")
result = generator.create_github_pr()
```

### Security Best Practices

- **Never commit tokens** to version control
- Store in environment variables or secure secrets manager
- Use repository-specific tokens when possible
- Revoke tokens when no longer needed
- Use fine-grained tokens for additional security

## 📝 Programmatic Usage

Use the PR generator in your own scripts:

```python
from pr_generator import PRGenerator

# Initialize generator
generator = PRGenerator(repo_path=".", github_token="your_token")

# Get changed files
files = generator.get_changed_files(base_branch="main")
print(f"Changed files: {files}")

# Analyze changes
analysis = generator.analyze_changes(files)
print(f"Total changes: {sum(analysis['changes_by_type'].values())}")

# Generate PR description
description = generator.generate_pr_description(
    title="My Migration PR",
    analysis=analysis,
    include_stats=True,
    include_checklist=True
)
print(description)

# Create PR on GitHub
result = generator.create_github_pr(
    base_branch="main",
    title="Custom PR Title",
    draft=False,
    labels=["migration", "python3"]
)
print(f"Created PR #{result['pr_number']}: {result['pr_url']}")
```

## 🔄 Workflow Integration

### Integration with Migration Workflow

Combine PR generation with your migration workflow:

```bash
# 1. Create a feature branch
git checkout -b migration/auth-module

# 2. Run the migration
./py2to3 fix src/auth/

# 3. Commit the changes
git add src/auth/
git commit -m "Migrate auth module to Python 3"

# 4. Push to remote
git push origin migration/auth-module

# 5. Create the PR
./py2to3 pr --create --labels migration python3

# 6. Address review feedback
# ... make changes ...

# 7. Update the PR
git push origin migration/auth-module
```

### Integration with CI/CD

Include PR generation in your CI pipeline:

```yaml
# .github/workflows/migration.yml
name: Migration PR Generator

on:
  push:
    branches:
      - 'migration/**'

jobs:
  generate-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Generate PR draft
        run: ./py2to3 pr --output pr_draft_${{ github.run_number }}.md
      
      - name: Upload PR draft as artifact
        uses: actions/upload-artifact@v2
        with:
          name: pr-draft
          path: pr_draft_*.md
```

### Team Workflow

For teams working on migration:

1. **Lead creates migration plan**:
   ```bash
   ./py2to3 checklist --format markdown > MIGRATION_PLAN.md
   ```

2. **Team members pick modules** from the plan

3. **Each member creates a branch** for their module:
   ```bash
   git checkout -b migration/my-module
   ```

4. **Run migration on their module**:
   ```bash
   ./py2to3 fix src/my-module/
   ```

5. **Test the changes**:
   ```bash
   pytest tests/test_my_module.py
   ```

6. **Create PR automatically**:
   ```bash
   ./py2to3 pr --create --labels migration my-module
   ```

7. **Reviewers suggested automatically** based on code ownership

8. **Merge after approval** and move to next module

## ❓ Troubleshooting

### "No changed Python files found"

**Cause**: No Python files modified in your branch compared to base branch.

**Solution**:
```bash
# Check what files changed
git diff main...HEAD --name-only

# Make sure you're on a feature branch
git branch

# Make sure you have commits
git log
```

### "Must be on a feature branch"

**Cause**: Trying to create PR from main/master branch.

**Solution**:
```bash
# Create a feature branch first
git checkout -b migration/my-changes
```

### "GitHub token not found"

**Cause**: GITHUB_TOKEN environment variable not set.

**Solution**:
```bash
# Set the token
export GITHUB_TOKEN="your_token_here"

# Verify it's set
echo $GITHUB_TOKEN
```

### "Failed to create PR: 401"

**Cause**: Invalid or expired GitHub token.

**Solution**:
1. Generate a new token on GitHub
2. Make sure it has `repo` scope
3. Update your GITHUB_TOKEN variable

### "requests library not found"

**Cause**: Missing dependency for GitHub API calls.

**Solution**:
```bash
pip install requests
```

### "Could not determine GitHub repository"

**Cause**: Git remote doesn't point to GitHub.

**Solution**:
```bash
# Check your remote
git remote -v

# Should show something like:
# origin  https://github.com/user/repo.git (fetch)
# origin  https://github.com/user/repo.git (push)

# If not, add GitHub remote
git remote add origin https://github.com/user/repo.git
```

## 💡 Best Practices

### 1. Create Small, Focused PRs

Instead of one giant PR:
```bash
# Create separate PRs for each module
git checkout -b migration/auth
./py2to3 fix src/auth/
./py2to3 pr --create --title "Migrate auth module"

git checkout main
git checkout -b migration/utils
./py2to3 fix src/utils/
./py2to3 pr --create --title "Migrate utils module"
```

### 2. Use Draft PRs for Early Feedback

```bash
# Create as draft while still working
./py2to3 pr --create --draft

# Later, mark as ready for review via GitHub UI
```

### 3. Add Descriptive Labels

```bash
./py2to3 pr --create --labels migration python3 breaking-changes needs-testing
```

### 4. Review Before Creating

```bash
# Generate draft first
./py2to3 pr --output review.md

# Review the draft
cat review.md

# Edit if needed
vim review.md

# Then create manually or with --create
```

### 5. Include Tests in PR

```bash
# Generate tests for migrated code
./py2to3 test-gen src/my_module/

# Commit tests too
git add tests/
git commit -m "Add tests for migrated code"

# Then create PR
./py2to3 pr --create
```

## 🎓 Examples

### Example 1: Simple Module Migration

```bash
# Start with a clean branch
git checkout -b migration/auth-module

# Run the migration
./py2to3 fix src/auth/

# Review changes
./py2to3 diff-viewer src/auth/

# Test the changes
pytest tests/test_auth.py

# Commit
git add src/auth/
git commit -m "Migrate auth module to Python 3"

# Create PR
./py2to3 pr --create \
  --title "Python 3 Migration: Authentication Module" \
  --labels migration auth high-priority
```

### Example 2: Large Project with Multiple PRs

```bash
# Generate migration plan
./py2to3 checklist --format markdown > PLAN.md

# For each module in the plan:
for module in auth utils core api; do
  echo "Migrating $module..."
  
  # Create branch
  git checkout main
  git checkout -b migration/$module
  
  # Migrate
  ./py2to3 fix src/$module/
  
  # Test
  pytest tests/test_$module.py
  
  # Commit
  git add .
  git commit -m "Migrate $module to Python 3"
  
  # Push and create PR
  git push origin migration/$module
  ./py2to3 pr --create --labels migration $module
done
```

### Example 3: Review and Edit Before Creating

```bash
# Generate draft
./py2to3 pr --output MY_PR.md

# Review and customize
cat MY_PR.md
vim MY_PR.md  # Edit as needed

# Create PR manually using the draft:
# 1. Go to GitHub
# 2. Click "New Pull Request"
# 3. Copy content from MY_PR.md
# 4. Submit
```

## 🔗 Related Commands

- **`./py2to3 fix`** - Apply migration fixes before creating PR
- **`./py2to3 diff-viewer`** - Review changes visually
- **`./py2to3 git commit`** - Commit changes with migration stats
- **`./py2to3 checklist`** - Plan your migration PRs
- **`./py2to3 review`** - Get code review assistance
- **`./py2to3 stats`** - Check migration statistics

## 📚 Learn More

- [Git Integration Guide](GIT_INTEGRATION.md) - More on git workflow
- [Migration Workflow](CLI_GUIDE.md) - Complete migration process
- [Checklist Generator](CHECKLIST_GUIDE.md) - Planning migrations
- [Review Assistant](REVIEW_GUIDE.md) - Code review tips

## 🤝 Contributing

Have ideas for improving the PR generator? We'd love to hear them!

- Add more migration pattern detection
- Improve reviewer suggestions
- Better PR title generation
- Integration with other platforms (GitLab, Bitbucket)
- More customization options

## 📄 License

This tool is part of the py2to3 migration toolkit, available under the MIT License.

---

**Happy PR Creating! 🚀** Let the toolkit handle the documentation while you focus on the code.
