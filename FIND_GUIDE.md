# 🔍 Documentation Navigator Guide

**Instantly find, search, and explore py2to3's extensive documentation library with intelligent search and categorization.**

## Overview

The `find` command provides a powerful interface for navigating py2to3's 50+ documentation guides. Instead of manually searching through files, use the documentation navigator to:

- 🔍 **Search** by keyword across all documentation
- 📚 **Browse** guides organized by category
- 📄 **View** detailed information about any guide
- 📊 **Analyze** documentation statistics

## Quick Start

```bash
# Search for specific topics
./py2to3 find search "wizard"

# List all documentation by category
./py2to3 find list

# Get detailed information about a guide
./py2to3 find info WIZARD_GUIDE

# View documentation statistics
./py2to3 find stats
```

## Commands

### 1. Search Documentation

Search across all documentation by keyword, title, or content:

```bash
./py2to3 find search <query>
```

**Examples:**

```bash
# Find guides about the wizard
./py2to3 find search "wizard"

# Search for dependency-related guides
./py2to3 find search "dependencies"

# Find guides about testing
./py2to3 find search "test"
```

**Options:**

- `-n, --max-results N` - Limit results (default: 10)
- `--no-context` - Hide context snippets

**Search Features:**

- Searches in document titles, sections, descriptions, and content
- Smart keyword matching with relevance scoring
- Context snippets show where matches were found
- Results ranked by relevance

### 2. List All Documentation

Browse all available guides organized by category:

```bash
./py2to3 find list
```

**Categories include:**

- 📚 Getting Started
- 📚 User Interface
- 📚 Configuration
- 📚 Validation & Quality
- 📚 Safety & Version Control
- 📚 Examples & Patterns
- 📚 Reporting & Visualization
- 📚 Advanced Features
- 📚 Integration & Export
- 📚 Dependencies
- 📚 Automation
- And more...

### 3. Document Information

Get detailed information about a specific guide:

```bash
./py2to3 find info <document>
```

**Examples:**

```bash
# Full path
./py2to3 find info WIZARD_GUIDE.md

# Partial name match
./py2to3 find info wizard

# Case insensitive
./py2to3 find info CLI_GUIDE
```

**Shows:**

- 📄 Document title and path
- 📁 Category
- 📏 File size
- 📝 Description
- 📑 Table of contents (sections)
- 🏷️ Keywords
- 🔗 Related documents

### 4. Documentation Statistics

View statistics about the documentation library:

```bash
./py2to3 find stats
```

**Displays:**

- Total number of documents
- Total size of documentation
- Average document size
- Documents per category (with bar chart)

## Workflow Examples

### New User Getting Started

```bash
# See all available guides
./py2to3 find list

# Find beginner-friendly guides
./py2to3 find search "quick start"

# Learn about the wizard
./py2to3 find info WIZARD_GUIDE
```

### Finding Specific Feature Documentation

```bash
# Search for a feature
./py2to3 find search "backup"

# Get details about the backup guide
./py2to3 find info BACKUP_GUIDE

# Find related guides
# (shown automatically in info command)
```

### Exploring Advanced Features

```bash
# See documentation statistics
./py2to3 find stats

# Browse advanced features category
./py2to3 find list

# Search for specific advanced feature
./py2to3 find search "api server"
```

## Tips & Tricks

### Effective Searching

- **Be specific**: Search for unique terms like "heatmap" or "badges"
- **Use related terms**: Try synonyms if first search doesn't find what you need
- **Check related docs**: The `info` command shows related documents
- **Browse categories**: Use `list` to discover guides by topic

### Quick Navigation

- **Partial names work**: `find info wizard` finds `WIZARD_GUIDE.md`
- **Case insensitive**: `CLI_GUIDE` and `cli_guide` both work
- **Tab completion**: If you have completion installed, tab completes document names

### Discovery

- **Start with list**: Get an overview of all available documentation
- **Follow related docs**: Each guide shows related documentation
- **Check categories**: Find guides by browsing categories
- **Search broadly**: Try general terms to discover related guides

## Integration with Other Commands

The `find` command complements other py2to3 commands:

```bash
# Find guide for a command
./py2to3 find search "wizard"

# Read the guide, then run the command
./py2to3 wizard

# Find guides about a feature
./py2to3 find search "badges"

# Run the command
./py2to3 badges
```

## Common Use Cases

### "How do I...?"

Instead of searching through files manually:

```bash
# How do I create a backup?
./py2to3 find search "backup"

# How do I check my progress?
./py2to3 find search "progress"

# How do I validate my migration?
./py2to3 find search "validate"
```

### Learning py2to3

```bash
# Start with getting started guides
./py2to3 find list

# Search for tutorials
./py2to3 find search "tutorial"

# Explore by category
./py2to3 find list  # Browse categories
```

### Reference Documentation

```bash
# Find CLI reference
./py2to3 find info CLI_GUIDE

# Look up command syntax
./py2to3 find search "command"

# Find configuration options
./py2to3 find search "config"
```

## Documentation Categories Explained

- **Getting Started**: Installation, quick start, and basic usage
- **User Interface**: CLI guides, wizard, and interactive tools
- **Configuration**: Setup and configuration options
- **Validation & Quality**: Testing, quality checks, and security
- **Safety & Version Control**: Backups, rollback, and git integration
- **Examples & Patterns**: Code examples, recipes, and patterns
- **Reporting & Visualization**: Reports, charts, and progress tracking
- **Advanced Features**: API server, plugins, and advanced tools
- **Integration & Export**: Exporting results and integrations
- **Dependencies**: Dependency management and analysis
- **Automation**: CI/CD, pre-commit hooks, and automation

## Technical Details

### Auto-detection

The documentation navigator automatically finds the project root by looking for:

1. The `py2to3` script
2. The `setup.py` file
3. Multiple `*_GUIDE.md` files

No configuration needed!

### Search Algorithm

The search function uses a smart scoring system:

- **Title matches**: Highest priority (20 points)
- **Section matches**: High priority (10 points)
- **Keyword matches**: Medium priority (5 points)
- **Content matches**: Lower priority (2 points)
- **Description matches**: Medium priority (5 points)

Results are ranked by total score, with context snippets showing where matches were found.

### Related Documents

The `info` command shows related documents based on:

- **Category similarity**: Documents in the same category
- **Keyword overlap**: Documents sharing keywords
- **Topic relatedness**: Documents covering related topics

## Troubleshooting

### "Document not found"

- Check spelling with `./py2to3 find list`
- Try partial name: `wizard` instead of `WIZARD_GUIDE.md`
- Search instead: `./py2to3 find search "wizard"`

### No search results

- Try different keywords or synonyms
- Use broader terms
- Browse categories with `./py2to3 find list`

### Incomplete results

- Increase max results: `--max-results 20`
- Try multiple related searches
- Browse the category containing your topic

## See Also

- [CLI_GUIDE.md](CLI_GUIDE.md) - Complete CLI reference
- [QUICK_START.md](QUICK_START.md) - Getting started with py2to3
- [WIZARD_GUIDE.md](WIZARD_GUIDE.md) - Interactive migration wizard
- [README.md](README.md) - Project overview

---

**Start exploring the documentation now:**

```bash
./py2to3 find list
```

**Need help?** Use the built-in help:

```bash
./py2to3 find --help
./py2to3 find search --help
```
