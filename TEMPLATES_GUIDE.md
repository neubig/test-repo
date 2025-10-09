# Configuration Templates Guide 🎨

The **Configuration Templates** feature helps you quickly set up optimal migration configurations for your specific project type. Instead of manually configuring dozens of options, simply apply a template tailored to your framework or use case.

## Why Use Templates?

- **🚀 Fast Setup**: Get started in seconds with pre-configured settings
- **✅ Best Practices**: Templates encode proven migration strategies
- **🎯 Project-Specific**: Optimized for Django, Flask, data science, CLI tools, and more
- **🤝 Shareable**: Create and share templates with your team
- **🔧 Customizable**: Start with a template, then fine-tune to your needs

## Quick Start

```bash
# List all available templates
./py2to3 templates list

# View details of a specific template
./py2to3 templates show django

# Apply a template to your project
./py2to3 templates apply django

# Apply without merging (replace existing config)
./py2to3 templates apply django --replace
```

## Available Built-in Templates

### Web Frameworks

#### 🌐 Django (`django`)
**Perfect for:** Django web applications

**What it configures:**
- Skips migrations, static files, media, and locale directories
- High priority for models, views, and forms
- Critical priority for settings.py
- Custom rule to remove unnecessary `unicode_literals` imports
- Thorough verification with import and syntax checking

**Special tips:**
- Start with models and forms first
- Test database migrations after conversion
- Check middleware compatibility
- Update settings.py last

```bash
./py2to3 templates apply django
```

#### ⚡ Flask (`flask`)
**Perfect for:** Flask web applications

**What it configures:**
- Skips static files and templates
- High priority for routes, models, and views
- Critical priority for config files
- Optimized for Flask's simpler structure

```bash
./py2to3 templates apply flask
```

#### 🚀 FastAPI (`fastapi`)
**Perfect for:** FastAPI applications (Python 3.6+ only)

**What it configures:**
- Enables type hints checking (FastAPI relies on them)
- Suggests async/await patterns
- Enables f-string modernization
- Strict verification mode

```bash
./py2to3 templates apply fastapi
```

### Data & Science

#### 📊 Data Science (`data-science`)
**Perfect for:** Data science and machine learning projects

**What it configures:**
- Skips data directories, datasets, models, notebooks, CSV, and pickle files
- Safe mode enabled (data workflows are sensitive)
- High priority for preprocessing and model code
- Checks compatibility of NumPy, Pandas, scikit-learn, TensorFlow, PyTorch

**Special tips:**
- Watch for integer division changes
- Test pickle compatibility
- Verify random number generator results
- Jupyter notebooks may need separate conversion

```bash
./py2to3 templates apply data-science
```

### Tools & Libraries

#### 🔧 CLI Tool (`cli-tool`)
**Perfect for:** Command-line applications and tools

**What it configures:**
- High priority for CLI and command modules
- Strict verification
- Focus on input/output encoding

```bash
./py2to3 templates apply cli-tool
```

#### 📦 Library/Package (`library`)
**Perfect for:** Python libraries and packages

**What it configures:**
- Safe mode (API stability matters)
- Critical priority for public API
- Runs tests after fixes
- Requires code coverage
- API compatibility checking

**Special tips:**
- Maintain backward compatibility where possible
- Update setup.py for Python 3
- Test all public APIs thoroughly
- Consider using `python_requires` in setup.py

```bash
./py2to3 templates apply library
```

#### 🧪 Test Automation (`test-automation`)
**Perfect for:** Test automation frameworks

**What it configures:**
- Skips test data, fixtures, and reports
- Critical priority for test runner
- Safe mode enabled
- High priority for test cases

```bash
./py2to3 templates apply test-automation
```

### General Templates

#### 🛡️ Minimal (`minimal`)
**Perfect for:** Conservative approach, any project type

**What it configures:**
- Safe mode enabled
- Backups enabled
- Verification after fixes
- Non-strict mode (fewer false positives)

**When to use:**
- First-time users
- Uncertain about project structure
- Want maximum control
- Legacy codebase with many edge cases

```bash
./py2to3 templates apply minimal
```

#### ⚡ Aggressive (`aggressive`)
**Perfect for:** Well-tested codebases, fast migration

**What it configures:**
- Safe mode disabled for speed
- Auto-fix enabled
- Strict verification
- Modernization options (f-strings, pathlib)
- Runs tests after fixes

**When to use:**
- Excellent test coverage (80%+)
- Need fast migration
- Willing to fix edge cases manually
- Have rollback plan ready

**⚠️ WARNING:** Only use with comprehensive test coverage!

```bash
./py2to3 templates apply aggressive
```

## Template Management

### Listing Templates

```bash
# List all templates
./py2to3 templates list

# List by category
./py2to3 templates list --category web
./py2to3 templates list --category data
./py2to3 templates list --category tool
```

**Output format:**
```
django               - Django Web Application (web)
                       Configuration optimized for Django web applications

flask                - Flask Web Application (web)
                       Configuration optimized for Flask web applications
...
```

### Viewing Template Details

```bash
# Show complete template configuration
./py2to3 templates show django

# Show with tips and all settings
./py2to3 templates show data-science
```

**Shows:**
- Full configuration JSON
- Priority settings
- Skip patterns
- Custom rules
- Migration tips

### Applying Templates

```bash
# Apply template (merges with existing config)
./py2to3 templates apply django

# Apply to specific config file
./py2to3 templates apply django --config my-config.json

# Replace existing config entirely
./py2to3 templates apply django --replace

# Apply and customize further
./py2to3 templates apply flask
./py2to3 config set fixer.safe_mode true
```

**Merge vs Replace:**
- **Merge (default)**: Combines template with your existing settings
- **Replace**: Completely replaces your config with template

## Creating Custom Templates

Create templates from your current configuration to share with your team or reuse across projects.

### From Current Configuration

```bash
# Create template from current config
./py2to3 templates create "My Django Template" \
    --description "Our company's Django migration settings" \
    --config .py2to3config.json \
    --category web

# Verify it was created
./py2to3 templates list
```

### Template Structure

Custom templates are JSON files with this structure:

```json
{
  "name": "My Template",
  "description": "Template description",
  "category": "web",
  "config": {
    "backup": {
      "enabled": true,
      "dir": "backups"
    },
    "fixer": {
      "safe_mode": false,
      "verify_after_fix": true
    },
    "priorities": {
      "models": "high",
      "views": "high"
    }
  },
  "tips": [
    "Tip 1: Start with models",
    "Tip 2: Test thoroughly"
  ]
}
```

### Sharing Templates

#### Export Template
```bash
# Export built-in template
./py2to3 templates export django django-template.json

# Export custom template
./py2to3 templates export my-company-django company-template.json

# Share file with team
git add company-template.json
git commit -m "Add company Django migration template"
```

#### Import Template
```bash
# Import from file
./py2to3 templates import company-template.json

# Now available for use
./py2to3 templates list
./py2to3 templates apply my-company-django
```

### Deleting Custom Templates

```bash
# Delete a custom template
./py2to3 templates delete my-template

# Note: Cannot delete built-in templates
```

## Template Categories

Templates are organized into categories:

- **web**: Web frameworks (Django, Flask, FastAPI)
- **data**: Data science and ML projects
- **tool**: CLI tools and utilities
- **library**: Python packages and libraries
- **testing**: Test automation frameworks
- **general**: General-purpose templates

```bash
# Show all categories
./py2to3 templates categories

# Filter by category
./py2to3 templates list --category web
```

## Common Workflows

### Starting a New Migration

```bash
# 1. Choose the right template
./py2to3 templates list

# 2. Apply template
./py2to3 templates apply django

# 3. Review and customize
./py2to3 config show

# 4. Start migration
./py2to3 wizard
```

### Team Collaboration

```bash
# Team lead creates template
./py2to3 config set fixer.safe_mode false
./py2to3 config set backup.max_backups 5
# ... configure everything ...
./py2to3 templates create "Team Django Config" \
    --description "Standard config for our Django projects" \
    --config .py2to3config.json \
    --category web

# Export and commit
./py2to3 templates export team-django-config team-config.json
git add team-config.json
git commit -m "Add team migration template"
git push

# Team members use it
git pull
./py2to3 templates import team-config.json
./py2to3 templates apply team-django-config
```

### Multiple Project Types

```bash
# Project has both web app and data science code
./py2to3 templates apply django --config webapp.config.json
./py2to3 templates apply data-science --config datascience.config.json

# Migrate separately
./py2to3 migrate webapp/ --config webapp.config.json
./py2to3 migrate datascience/ --config datascience.config.json
```

### Experimentation

```bash
# Try aggressive template
./py2to3 templates apply aggressive --config aggressive.json

# Run simulation
./py2to3 simulate src/ --config aggressive.json

# Compare with conservative approach
./py2to3 templates apply minimal --config conservative.json
./py2to3 simulate src/ --config conservative.json

# Choose the better approach
./py2to3 templates apply [chosen-template]
```

## Template Best Practices

### Choosing the Right Template

1. **Start with your framework**: Use framework-specific templates when available
2. **Consider your test coverage**: High coverage → aggressive, Low coverage → minimal
3. **Think about your timeline**: Tight deadline → aggressive, Flexible → minimal
4. **Account for complexity**: Simple codebase → aggressive, Complex → minimal

### Customizing Templates

After applying a template, customize for your specific needs:

```bash
# Apply base template
./py2to3 templates apply django

# Customize skip patterns
./py2to3 config set fixer.skip_patterns "*/migrations/*,*/vendor/*,*/legacy/*"

# Adjust priorities
./py2to3 config set priorities.api high
./py2to3 config set priorities.legacy low

# Add custom rules
./py2to3 rules add my-custom-rule "old_pattern" "new_pattern"
```

### Creating Reusable Templates

When creating templates for your team:

1. **Document everything**: Add comprehensive tips
2. **Test thoroughly**: Apply to sample projects first
3. **Start conservative**: Easier to loosen than tighten
4. **Include context**: Explain why settings are chosen
5. **Version control**: Track template changes over time

## Advanced Usage

### Programmatic Access

```python
from template_manager import TemplateManager

manager = TemplateManager()

# List templates
templates = manager.list_templates(category='web')
for t in templates:
    print(f"{t['id']}: {t['name']}")

# Apply template
manager.apply_template('django', '.py2to3config.json')

# Create custom template
manager.create_template(
    name='My Template',
    description='Custom config',
    config_file='current.json',
    category='web'
)
```

### Template Inheritance

Create specialized templates based on existing ones:

```bash
# Start with Django template
./py2to3 templates apply django

# Customize for your needs
./py2to3 config set fixer.skip_patterns "*/migrations/*,*/my_custom_dir/*"
./py2to3 config set priorities.apis critical

# Save as new template
./py2to3 templates create "Django REST API" \
    --description "Django + DRF migration config" \
    --config .py2to3config.json \
    --category web
```

### Template Validation

```bash
# Apply template and validate project
./py2to3 templates apply django
./py2to3 doctor
./py2to3 readiness

# Fix any issues
./py2to3 config set [setting] [value]

# Re-validate
./py2to3 doctor
```

## Troubleshooting

### Template Not Found

```bash
# Make sure you have the latest version
git pull

# Check template ID spelling
./py2to3 templates list

# Check if it's a custom template
ls ~/.py2to3/templates/
```

### Configuration Conflicts

If template conflicts with existing config:

```bash
# View current config
./py2to3 config show

# Backup current config
cp .py2to3config.json .py2to3config.backup.json

# Apply template with replace
./py2to3 templates apply django --replace

# Or merge carefully
./py2to3 templates apply django  # Default is merge
```

### Template Not Working as Expected

```bash
# View applied configuration
./py2to3 config show

# Check if settings were applied
cat .py2to3config.json

# Review template details
./py2to3 templates show django

# Re-apply if needed
./py2to3 templates apply django --replace
```

## FAQ

**Q: Can I modify built-in templates?**
A: No, but you can create a custom template based on a built-in one, then modify it.

**Q: Where are custom templates stored?**
A: In `~/.py2to3/templates/` as JSON files.

**Q: Can templates be shared across teams?**
A: Yes! Export templates to JSON files and commit them to your repository.

**Q: What happens if I apply a template twice?**
A: By default, it merges with existing config. Use `--replace` to overwrite.

**Q: Can I use multiple templates?**
A: Apply them sequentially. Later templates will merge with earlier ones.

**Q: Do templates work with all commands?**
A: Yes, templates just configure settings. All commands respect the configuration.

**Q: Can I see what a template will change before applying?**
A: Yes, use `./py2to3 templates show <template-id>` to preview.

## See Also

- [CONFIG.md](CONFIG.md) - Configuration system details
- [WIZARD_GUIDE.md](WIZARD_GUIDE.md) - Interactive migration wizard
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [DOCTOR_GUIDE.md](DOCTOR_GUIDE.md) - Environment diagnostics
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI reference

## Examples

### Django Project Migration

```bash
# 1. Apply Django template
./py2to3 templates apply django

# 2. Run diagnostics
./py2to3 doctor

# 3. Start wizard
./py2to3 wizard

# 4. Review results
./py2to3 report
```

### Data Science Project

```bash
# 1. Apply data science template
./py2to3 templates apply data-science

# 2. Check package compatibility
./py2to3 packages check

# 3. Run careful migration
./py2to3 migrate --safe

# 4. Test notebooks separately
# (Manual Jupyter notebook conversion)
```

### Multi-Framework Project

```bash
# Web API part
./py2to3 templates apply flask --config api.json
./py2to3 migrate api/ --config api.json

# CLI tool part
./py2to3 templates apply cli-tool --config cli.json
./py2to3 migrate cli/ --config cli.json

# Shared library part
./py2to3 templates apply library --config lib.json
./py2to3 migrate lib/ --config lib.json
```

---

**Need help?** Run `./py2to3 templates --help` or check other guides in the repository!
