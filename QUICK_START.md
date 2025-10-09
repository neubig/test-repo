# Quick Start Guide

Get started with the Python 2 to 3 Migration Toolkit in just a few minutes!

## 🚀 Installation (Easy Way)

We've made it super easy to get started. Just run the automated setup script:

```bash
./setup.sh
```

This will:
- ✅ Check your Python version
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Validate the installation
- ✅ Run a quick demo
- ✅ Show you what to do next

### Setup Options

```bash
# Standard installation (recommended)
./setup.sh

# Install without virtual environment
./setup.sh --no-venv

# Install with development tools
./setup.sh --dev

# Use a custom venv directory
./setup.sh --venv-dir .venv

# Get help
./setup.sh --help
```

## 📦 Manual Installation

If you prefer to install manually:

```bash
# 1. Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Make py2to3 executable
chmod +x py2to3

# 4. Verify installation
./py2to3 --help
```

### Development Installation

For development with testing and linting tools:

```bash
pip install -r requirements-dev.txt
```

## 🎯 Your First Migration

Once installed, you can start migrating in three easy ways:

### Option 1: Wizard Mode (Recommended for Beginners)

The wizard guides you through the entire process:

```bash
./py2to3 wizard
```

The wizard will:
- Ask about your project and experience level
- Recommend a migration strategy
- Run all necessary checks
- Apply fixes with your approval
- Generate reports
- Track progress

### Option 2: Step-by-Step

Run commands manually for more control:

```bash
# Step 1: Check what needs to be migrated
./py2to3 check src/

# Step 2: Run safety checks
./py2to3 preflight src/

# Step 3: Apply fixes (with backup)
./py2to3 fix src/ --backup

# Step 4: Check what's left
./py2to3 check src/

# Step 5: Generate a report
./py2to3 report
```

### Option 3: One Command

For quick migrations:

```bash
./py2to3 migrate src/ --backup --report
```

## 🛠️ Using Make Commands

We've included a Makefile for common tasks:

```bash
# Show all available commands
make help

# Run the setup script
make setup

# Run tests
make test

# Run tests with coverage
make test-cov

# Run a quick demo
make demo

# Format code
make format

# Run linters
make lint

# Clean generated files
make clean

# Install dependencies
make install

# Install dev dependencies
make install-dev
```

## 📚 Common Commands

Here are the most useful commands to get started:

```bash
# Get help
./py2to3 --help
./py2to3 <command> --help

# Check compatibility
./py2to3 check <path>

# Apply fixes
./py2to3 fix <path> --backup

# See migration status
./py2to3 status

# Search for specific patterns
./py2to3 search <path> --pattern print_statement

# Convert a code snippet
./py2to3 convert --code 'print "hello"'

# Generate visual dashboard
./py2to3 dashboard

# Run preflight checks
./py2to3 preflight <path>

# Manage backups
./py2to3 backup list
./py2to3 backup restore <backup_id>

# Track coverage
./py2to3 coverage track

# Manage configuration
./py2to3 config show
./py2to3 config set <key> <value>

# Generate reports
./py2to3 report --output report.html
```

## 🎓 Learning Path

### For Beginners

1. **Start here**: Run `./py2to3 wizard` and follow the prompts
2. **Read**: [WIZARD_GUIDE.md](WIZARD_GUIDE.md) for wizard details
3. **Explore**: Run `./py2to3 --help` to see all commands
4. **Practice**: Try `./py2to3 convert` to convert code snippets

### For Experienced Users

1. **Configure**: Set up your preferences with `./py2to3 config init`
2. **Plan**: Use `./py2to3 plan <path>` to create a migration plan
3. **Execute**: Run fixes, checks, and reports as needed
4. **Track**: Monitor progress with `./py2to3 status` and `./py2to3 dashboard`

### For Teams

1. **Setup**: Install pre-commit hooks with `./py2to3 precommit install`
2. **CI/CD**: Enable automated checks (see [CI_CD_GUIDE.md](CI_CD_GUIDE.md))
3. **Share**: Export configurations with `./py2to3 export create`
4. **Collaborate**: Use git integration for tracking

## 📖 Documentation

We have comprehensive guides for every feature:

**Getting Started**
- [README.md](README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - This guide
- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI reference

**Workflows**
- [WIZARD_GUIDE.md](WIZARD_GUIDE.md) - Guided migration
- [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md) - Interactive fixes
- [WATCH_MODE.md](WATCH_MODE.md) - Continuous monitoring

**Core Features**
- [CONFIG.md](CONFIG.md) - Configuration management
- [BACKUP_GUIDE.md](BACKUP_GUIDE.md) - Backup management
- [ROLLBACK_GUIDE.md](ROLLBACK_GUIDE.md) - Rollback operations

**Advanced Features**
- [COVERAGE_GUIDE.md](COVERAGE_GUIDE.md) - Test coverage tracking
- [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) - Performance analysis
- [DEPENDENCY_GUIDE.md](DEPENDENCY_GUIDE.md) - Dependency management
- [CI_CD_GUIDE.md](CI_CD_GUIDE.md) - CI/CD integration

**And many more!** Check the main [README.md](README.md) for the complete list.

## ⚡ Quick Tips

1. **Always backup**: Use `--backup` flag when applying fixes
2. **Start small**: Test on a single file or module first
3. **Use preflight**: Run `./py2to3 preflight` before starting
4. **Track progress**: Use `./py2to3 status` regularly
5. **Read reports**: Generate HTML reports for detailed insights
6. **Commit often**: Use git to track your migration progress
7. **Use wizard**: When in doubt, run `./py2to3 wizard`

## 🆘 Troubleshooting

### Import Errors

If you get import errors, make sure dependencies are installed:

```bash
pip install -r requirements.txt
```

### Permission Errors

Make sure the py2to3 script is executable:

```bash
chmod +x py2to3
```

### Python Version Issues

Check your Python version (requires 3.6+):

```bash
python3 --version
```

### Virtual Environment Issues

If you have issues with the virtual environment:

```bash
# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

## 🎉 Success!

You're now ready to migrate Python 2 code to Python 3! Here's a suggested workflow:

```bash
# 1. Run the wizard (easiest way)
./py2to3 wizard

# 2. Or do it step by step
./py2to3 preflight src/     # Check if ready
./py2to3 check src/         # Find issues
./py2to3 fix src/ --backup  # Apply fixes
./py2to3 status             # Check progress
./py2to3 report             # Generate report

# 3. Track and iterate
./py2to3 dashboard          # Visual progress
./py2to3 check src/         # Find remaining issues
./py2to3 test-gen           # Generate tests
```

## 📞 Getting Help

- Run `./py2to3 --help` for command overview
- Run `./py2to3 <command> --help` for specific command help
- Check the guide files for detailed documentation
- Use `make help` for Makefile commands

## 🎯 Next Steps

1. ✅ Installation complete
2. 📝 Read [CLI_GUIDE.md](CLI_GUIDE.md) for detailed command reference
3. 🧙 Run `./py2to3 wizard` to start your first migration
4. 📊 Generate reports with `./py2to3 report`
5. 🎉 Celebrate when you reach 100% compatibility!

Happy migrating! 🚀
