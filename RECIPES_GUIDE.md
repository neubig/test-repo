# Migration Recipes Guide

The **Migration Recipe System** provides reusable templates and best practices for migrating different types of Python projects from Python 2 to Python 3. Recipes encapsulate configuration, recommended fix order, ignore patterns, and important notes specific to different frameworks and project types.

## Table of Contents

- [What are Migration Recipes?](#what-are-migration-recipes)
- [Quick Start](#quick-start)
- [Built-in Recipes](#built-in-recipes)
- [Recipe Commands](#recipe-commands)
- [Creating Custom Recipes](#creating-custom-recipes)
- [Sharing Recipes](#sharing-recipes)
- [Recipe Structure](#recipe-structure)
- [Examples](#examples)
- [Best Practices](#best-practices)

## What are Migration Recipes?

Migration recipes are pre-configured templates that provide:

- **Tailored Configuration**: Framework-specific settings and fix rules
- **Recommended Fix Order**: Prioritized sequence of fixes for best results
- **Ignore Patterns**: Common files/directories to skip (migrations, static files, etc.)
- **Important Notes**: Framework-specific gotchas and things to watch out for
- **Best Practices**: Curated advice from successful migrations

Think of recipes as "quick-start guides" that save you from having to figure out the optimal migration strategy for your specific project type.

## Quick Start

### List Available Recipes

```bash
# See all available recipes
./py2to3 recipe list
```

This shows bundled recipes for:
- Django web applications
- Flask web applications
- Command-line tools
- Data science/ML projects
- Python libraries/packages

### View Recipe Details

```bash
# See detailed information about a recipe
./py2to3 recipe show django
./py2to3 recipe show flask
./py2to3 recipe show cli
```

### Apply a Recipe

```bash
# Apply a recipe to your current project
./py2to3 recipe apply django

# Apply to a different directory
./py2to3 recipe apply flask -t /path/to/project
```

This will:
1. Create/update `.py2to3.config.json` with recipe settings
2. Display important notes for your project type
3. Show recommended fix order
4. List configured ignore patterns
5. Suggest next steps

### Start Migration

After applying a recipe:

```bash
# Review the configuration
./py2to3 config show

# Run preflight checks
./py2to3 preflight .

# Start fixing
./py2to3 fix .
```

## Built-in Recipes

### Django Recipe

For Django web applications.

**Key Features:**
- Ignores migrations, static files, and media directories
- Focuses on unicode handling in templates and forms
- Includes URL pattern considerations
- Database configuration notes

**Best For:**
- Django 1.x → Django 2.x/3.x migrations
- Projects with complex ORM usage
- Applications with custom admin interfaces

**Important Notes:**
- Django 2.0+ requires Python 3.5+
- Check third-party package compatibility first
- Test admin customizations thoroughly
- Review URL patterns (url() deprecated in Django 3.1)

### Flask Recipe

For Flask web applications.

**Key Features:**
- Ignores static files and virtual environments
- Focuses on request/response handling
- JSON serialization considerations
- Cookie and session handling notes

**Best For:**
- Flask applications with REST APIs
- Projects using Flask extensions
- Applications with file upload/download

**Important Notes:**
- Flask 2.0+ requires Python 3.6+
- Check Flask extension compatibility
- Test file upload/download functionality
- Verify JSON serialization works correctly

### CLI Recipe

For command-line tools and utilities.

**Key Features:**
- Focuses on print statements (affects output)
- Input/output encoding considerations
- Shebang line updates
- Error message and exit code testing

**Best For:**
- Command-line applications
- System utilities
- Developer tools
- Automation scripts

**Important Notes:**
- Test all arguments and options
- Verify input/output encoding for non-ASCII
- Check file I/O with various file types
- Consider modern CLI frameworks (click, typer)

### Data Science Recipe

For data science and machine learning projects.

**Key Features:**
- Integer division changes (/ vs //)
- Iterator behavior changes (map, filter, zip)
- Pickle compatibility considerations
- NumPy/Pandas version notes

**Best For:**
- Jupyter notebooks
- ML model training code
- Data processing pipelines
- Scientific computing projects

**Important Notes:**
- Integer division behavior changed
- map, filter, zip return iterators (not lists)
- Pickle files may need regeneration
- Re-run experiments for reproducibility
- Check numpy, pandas, scikit-learn versions

### Library Recipe

For Python packages and libraries.

**Key Features:**
- setup.py configuration updates
- Multi-version testing considerations
- Type hints and documentation
- CI/CD configuration for multiple Python versions

**Best For:**
- Open source libraries
- Internal shared packages
- PyPI published packages
- Framework extensions

**Important Notes:**
- Update setup.py classifiers
- Specify python_requires='>=3.6'
- Add type hints for better IDE support
- Test with Python 3.7, 3.8, 3.9, 3.10, 3.11
- Consider tox for multi-version testing

## Recipe Commands

### List Recipes

```bash
# List all available recipes (bundled + custom)
./py2to3 recipe list
```

### Show Recipe Details

```bash
# View comprehensive information about a recipe
./py2to3 recipe show <recipe-name>

# Example
./py2to3 recipe show django
```

Shows:
- Description and tags
- Author and creation date
- Important notes
- Recommended fix order
- Ignore patterns
- Configuration settings

### Apply Recipe

```bash
# Apply recipe to current directory
./py2to3 recipe apply <recipe-name>

# Apply to specific directory
./py2to3 recipe apply <recipe-name> -t /path/to/project

# Examples
./py2to3 recipe apply django
./py2to3 recipe apply flask -t ~/projects/my-flask-app
```

### Create Custom Recipe

```bash
# Create from current configuration
./py2to3 recipe create <name> -d "Description" -c .py2to3.config.json

# Example
./py2to3 recipe create my-company-standard \
  -d "Our company's standard migration recipe" \
  -c .py2to3.config.json
```

### Export Recipe

```bash
# Export to share with team
./py2to3 recipe export <name> -o recipe-file.json

# Example
./py2to3 recipe export django -o django-recipe.json
```

### Import Recipe

```bash
# Import from file
./py2to3 recipe import recipe-file.json

# Force overwrite existing recipe
./py2to3 recipe import recipe-file.json --force
```

### Delete Recipe

```bash
# Delete a custom recipe
./py2to3 recipe delete <name>

# Example
./py2to3 recipe delete my-old-recipe
```

Note: You can only delete custom recipes, not bundled recipes.

## Creating Custom Recipes

### From Current Configuration

The easiest way to create a recipe is from your current project configuration:

```bash
# 1. Configure your project
./py2to3 config init
./py2to3 config set fix_rules.print_statements true
# ... more configuration ...

# 2. Create recipe from config
./py2to3 recipe create my-recipe \
  -d "My custom migration recipe" \
  -c .py2to3.config.json
```

### Manual Creation

Create a JSON file with the recipe structure:

```json
{
  "name": "my-custom-recipe",
  "description": "Custom recipe for my project type",
  "author": "Your Name",
  "tags": ["custom", "special"],
  "config": {
    "fix_rules": {
      "print_statements": true,
      "imports": true,
      "exceptions": true
    },
    "backup_enabled": true
  },
  "fix_order": [
    "print_statements",
    "imports",
    "exceptions"
  ],
  "ignore_patterns": [
    "*/tests/*",
    "*/build/*"
  ],
  "notes": [
    "Important note 1",
    "Important note 2"
  ]
}
```

Then import it:

```bash
./py2to3 recipe import my-custom-recipe.json
```

## Sharing Recipes

### With Your Team

**Option 1: Export/Import**

```bash
# Developer A exports recipe
./py2to3 recipe export team-standard -o team-standard.recipe.json

# Commit to version control
git add team-standard.recipe.json
git commit -m "Add team migration recipe"

# Developer B imports recipe
./py2to3 recipe import team-standard.recipe.json
```

**Option 2: Shared Recipes Directory**

```bash
# Set up shared directory
export SHARED_RECIPES=/shared/recipes

# Use shared directory
./py2to3 recipe --recipes-dir $SHARED_RECIPES list
./py2to3 recipe --recipes-dir $SHARED_RECIPES apply team-standard
```

### With the Community

Consider contributing your recipe to the py2to3 project:

1. Test your recipe on multiple projects
2. Document any special considerations
3. Submit a pull request with the recipe file

## Recipe Structure

A recipe consists of the following components:

### Metadata

- **name**: Unique identifier for the recipe
- **description**: Brief description of the recipe's purpose
- **author**: Recipe creator (person or organization)
- **tags**: Keywords for categorization
- **created_at**: ISO 8601 timestamp

### Configuration

- **config**: Dictionary of py2to3 configuration settings
- Applied to `.py2to3.config.json` when recipe is used

### Fix Order

- **fix_order**: Recommended sequence for applying fixes
- Helps prioritize which issues to tackle first
- Based on best practices and common dependencies

### Ignore Patterns

- **ignore_patterns**: Glob patterns for files/directories to skip
- Prevents wasting time on generated or vendor code
- Examples: migrations, static files, node_modules

### Notes

- **notes**: Important warnings, gotchas, and tips
- Framework-specific considerations
- Links to documentation
- Version compatibility information

## Examples

### Example 1: Applying Django Recipe

```bash
# Navigate to your Django project
cd ~/projects/my-django-app

# View Django recipe details
./py2to3 recipe show django

# Apply the recipe
./py2to3 recipe apply django

# Review configuration
./py2to3 config show

# Run preflight checks
./py2to3 preflight .

# Start migration
./py2to3 fix .
```

### Example 2: Creating Company Standard Recipe

```bash
# Start with a good base
./py2to3 recipe apply library

# Customize for your needs
./py2to3 config set backup_enabled true
./py2to3 config set fix_rules.division true

# Save as custom recipe
./py2to3 recipe create acme-standard \
  -d "ACME Corp standard Python 3 migration recipe" \
  -c .py2to3.config.json

# Export for team
./py2to3 recipe export acme-standard -o recipes/acme-standard.json

# Team members can import
./py2to3 recipe import recipes/acme-standard.json
```

### Example 3: Comparing Recipes

```bash
# View multiple recipes to find the best fit
./py2to3 recipe show django
./py2to3 recipe show flask

# Try different recipes on test branches
git checkout -b try-django-recipe
./py2to3 recipe apply django
./py2to3 fix .

git checkout main
git checkout -b try-flask-recipe
./py2to3 recipe apply flask
./py2to3 fix .

# Compare results
./py2to3 compare branches try-django-recipe try-flask-recipe
```

## Best Practices

### Choosing the Right Recipe

1. **Start with the closest match**: Use the recipe that most closely matches your project type
2. **Review the notes**: Pay attention to framework-specific considerations
3. **Customize as needed**: Recipes are starting points, not rigid requirements
4. **Test on a branch**: Try different recipes to see which works best

### Customizing Recipes

1. **Apply base recipe**: Start with a bundled recipe
2. **Test migration**: Run on a small subset of your code
3. **Refine configuration**: Adjust based on results
4. **Save custom recipe**: Create your own recipe for future use

### Creating Team Recipes

1. **Collaborate**: Get input from multiple team members
2. **Document decisions**: Explain why certain choices were made
3. **Version control**: Store recipe files in your repository
4. **Update regularly**: Refine recipes based on experience

### Recipe Maintenance

1. **Keep recipes updated**: As tools and best practices evolve
2. **Document changes**: Track why recipes were modified
3. **Test before sharing**: Ensure recipes work on real projects
4. **Gather feedback**: Learn from others' experiences

### Integration with Workflow

```bash
# 1. Choose recipe at project start
./py2to3 recipe list
./py2to3 recipe show django

# 2. Apply and review
./py2to3 recipe apply django
./py2to3 config show

# 3. Run preflight checks
./py2to3 preflight .

# 4. Follow recipe's recommended fix order
# (shown when recipe is applied)

# 5. Create branch and start migration
git checkout -b python3-migration
./py2to3 fix .

# 6. Save your experience as new recipe
./py2to3 recipe create my-project-type \
  -d "Recipe for projects like mine" \
  -c .py2to3.config.json
```

## Troubleshooting

### Recipe Not Found

```bash
# Check available recipes
./py2to3 recipe list

# Check custom recipes directory
ls ~/.py2to3/recipes/
```

### Recipe Application Failed

- Ensure target directory exists
- Check write permissions
- Verify Python 3 compatibility of existing config

### Recipe Doesn't Match Project

- Start with closest match
- Customize configuration after applying
- Create custom recipe for your specific needs

## Further Reading

- [CLI Guide](CLI_GUIDE.md) - Main CLI documentation
- [Configuration Guide](CONFIG.md) - Configuration system details
- [Migration Planning](PLANNER_GUIDE.md) - Strategic planning tools
- [Best Practices](README.md) - General migration best practices

---

## Quick Reference

```bash
# List all recipes
./py2to3 recipe list

# View recipe details
./py2to3 recipe show <name>

# Apply recipe
./py2to3 recipe apply <name>

# Create custom recipe
./py2to3 recipe create <name> -d "Description"

# Export recipe
./py2to3 recipe export <name> -o file.json

# Import recipe
./py2to3 recipe import file.json

# Delete recipe
./py2to3 recipe delete <name>
```

Recipes make migration easier by providing proven strategies for different project types. Start with a bundled recipe, customize as needed, and share your successes with your team!
