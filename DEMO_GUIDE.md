# 🎬 Interactive Demo Showcase Guide

## Overview

The **Demo Showcase** provides a quick, hands-on demonstration of the py2to3 migration toolkit. It's perfect for:

- **New users** learning how the tool works
- **Presentations and demos** to stakeholders or teams
- **Installation validation** to verify everything is set up correctly
- **Quick introduction** to the migration workflow

The demo creates a temporary Python 2 code sample, runs it through the complete migration workflow, and shows you exactly what the tool can do — all in just a few minutes!

## Features

✨ **Interactive Walkthrough**: Guides you step-by-step through the migration process  
🎯 **Hands-on Learning**: See actual code transformations in real-time  
📊 **Complete Workflow**: Demonstrates checking, fixing, and verifying  
🔒 **Safe & Isolated**: Uses temporary files, doesn't touch your code  
⚡ **Fast**: Complete demo runs in 2-3 minutes  
🎨 **Beautiful Output**: Colored, formatted, easy to follow  

## Quick Start

Run the interactive demo:

```bash
./py2to3 demo
```

That's it! The demo will guide you through the entire process.

## Usage

### Basic Usage

Run the default interactive demo:

```bash
./py2to3 demo
```

The demo will:
1. Create a sample Python 2 file with common patterns
2. Show the original Python 2 code
3. Run compatibility checks to detect issues
4. Apply automated fixes
5. Show the transformed Python 3 code
6. Verify the results
7. Provide next steps and resources

You'll be prompted to press Enter between each step.

### Automatic Mode

Run the demo without pauses (for presentations or automated testing):

```bash
./py2to3 demo --auto
```

This runs through the entire demo automatically with brief pauses between steps.

### Quiet Mode

Run with minimal output (just the essentials):

```bash
./py2to3 demo --quiet
```

### Combine Options

Run automatically with minimal output:

```bash
./py2to3 demo --auto --quiet
```

## What the Demo Shows

### Step 1: Setup
- Creates a temporary demo environment
- Generates a sample Python 2 file

### Step 2: Original Code
Shows Python 2 code containing:
- `print` statements without parentheses
- Old imports (`urllib2`, `ConfigParser`)
- Old-style classes
- Old exception syntax (`except Exception, e`)
- Iterator methods (`xrange`, `iteritems`)
- Old comparison methods (`__cmp__`)
- `basestring` type references

### Step 3: Compatibility Check
- Runs the verifier to detect Python 2 patterns
- Shows detected compatibility issues
- Provides summary of problems found

### Step 4: Apply Fixes
- Runs the automated fixer
- Creates backups
- Transforms Python 2 code to Python 3

### Step 5: Fixed Code
Shows the transformed code with:
- `print()` function calls
- Updated imports (`urllib.request`, `configparser`)
- New-style classes
- Modern exception syntax (`except Exception as e`)
- Updated methods (`range()`, `items()`)
- `str` instead of `basestring`

### Step 6: Verification
- Re-runs the verifier on fixed code
- Shows any remaining issues
- Confirms successful migration

### Step 7: Summary & Next Steps
Provides:
- Summary of what was accomplished
- Suggested commands to try next
- Links to relevant documentation
- Resources for learning more

## Example Output

```
======================================================================
            🚀 py2to3 Interactive Demo Showcase 🚀
======================================================================

Welcome to the py2to3 migration toolkit!
This demo will walk you through the complete migration workflow.
Interactive mode: ON

Press Enter to begin...

🔹🔹🔹 Step 1/7: Setting up demo environment

✓ Created temporary demo directory: /tmp/py2to3_demo_abc123/
✓ Created sample Python 2 file: demo_scraper.py

Press Enter to continue...

🔹🔹🔹 Step 2/7: Examining Original Python 2 Code

This sample demonstrates common Python 2 patterns:
  • Print statements (print "text")
  • Old imports (urllib2, ConfigParser)
  • Old-style classes
  • Old exception syntax (except Exception, e)
  • Iterator methods (xrange, iteritems)
  • Old comparison methods (__cmp__)
  • basestring type

Sample Python 2 Code:
----------------------------------------------------------------------
  1 | #!/usr/bin/env python
  2 | # -*- coding: utf-8 -*-
  3 | """
  4 | Sample Python 2 Web Scraper
  5 | Demonstrates common Python 2 patterns that need migration
  6 | """
  7 | 
  8 | import urllib2
  9 | import ConfigParser
 10 | from BaseHTTPServer import HTTPServer
...
----------------------------------------------------------------------

Press Enter to continue...

[Demo continues through all 7 steps...]
```

## Use Cases

### For New Users

Perfect first command to run after installing py2to3:

```bash
# After installation
./py2to3 demo

# Then follow the suggestions to try real commands
./py2to3 doctor
./py2to3 wizard
```

### For Presentations

Run in automatic mode for smooth demos:

```bash
# Presentation mode - automatic with full output
./py2to3 demo --auto

# Record it for async viewing
script -c "./py2to3 demo --auto" demo_recording.txt
```

### For Testing Installation

Verify that the tool is working correctly:

```bash
# Quick test that everything works
./py2to3 demo --auto --quiet

# Check exit code
./py2to3 demo --auto && echo "Installation verified!"
```

### For Learning

Study the transformations:

```bash
# Run interactively, take time to read each step
./py2to3 demo

# Pay attention to:
# - What issues are detected
# - How fixes are applied
# - What the transformed code looks like
```

## What's Demonstrated

The demo showcases these toolkit features:

1. **Verifier**: Detects Python 2 compatibility issues
2. **Fixer**: Applies automated transformations
3. **Backup System**: Creates safety backups
4. **Reporting**: Summarizes issues and fixes
5. **Workflow**: Shows the recommended migration process

## Next Steps After Demo

After running the demo, try these commands:

```bash
# Check your project health
./py2to3 doctor

# Get started with the wizard
./py2to3 wizard

# Create a migration checklist
./py2to3 checklist src/

# Check your actual code
./py2to3 check src/

# Browse migration patterns
./py2to3 patterns

# Get help on any command
./py2to3 --help
./py2to3 <command> --help
```

## Technical Details

### Temporary Files

- Demo creates files in a temporary directory
- All files are automatically cleaned up after demo
- No impact on your actual codebase
- Safe to run multiple times

### Sample Code

The demo uses realistic Python 2 code that includes:
- Web scraping patterns
- Configuration management
- Class definitions
- Error handling
- Data processing
- Common Python 2 idioms

### Dependencies

The demo requires:
- `verifier.py` module (for compatibility checking)
- `fixer.py` module (for applying fixes)
- Python 3.6+ (for running the demo)

If modules are not available, the demo will skip those steps gracefully.

## Tips

💡 **Take Your Time**: In interactive mode, read each step carefully  
💡 **Try Variations**: Run it multiple times with different options  
💡 **Show Others**: Great way to introduce the tool to your team  
💡 **Follow Up**: Use the suggested commands after the demo  
💡 **Share Feedback**: Let us know if the demo could be improved  

## Troubleshooting

### Demo Won't Start

```bash
# Check that py2to3 is executable
chmod +x py2to3

# Verify Python version
python3 --version

# Run with error details
./py2to3 demo
```

### Import Errors

If you see import errors:

```bash
# Check that you're in the repo root
pwd

# Verify src/ directory exists
ls src/

# Try installing dependencies
pip install -r requirements.txt
```

### Interrupted Demo

If you interrupt the demo (Ctrl+C), temporary files are automatically cleaned up.

## Command Reference

```
./py2to3 demo [OPTIONS]

Options:
  --auto          Run in automatic mode (no pauses)
  --quiet         Minimal output
  -h, --help      Show help message
```

## Related Features

- **Wizard**: `./py2to3 wizard` - Interactive migration workflow
- **Doctor**: `./py2to3 doctor` - Health diagnostics
- **Patterns**: `./py2to3 patterns` - Browse migration patterns
- **Simulator**: `./py2to3 simulate` - Preview migrations
- **Tutorial**: See `QUICK_START.md` for step-by-step guide

## FAQ

**Q: Does the demo modify my code?**  
A: No! The demo uses temporary files and doesn't touch your codebase.

**Q: How long does the demo take?**  
A: 2-3 minutes in interactive mode, ~30 seconds in auto mode.

**Q: Can I skip steps?**  
A: In interactive mode, just press Enter to continue. Or use `--auto` to run everything.

**Q: Can I run the demo multiple times?**  
A: Yes! It's safe to run as many times as you want.

**Q: Is internet required?**  
A: No, the demo runs completely offline.

**Q: Can I customize the demo code?**  
A: The demo uses built-in sample code. To try your own code, use the regular commands like `./py2to3 check your_file.py`.

## Contributing

Have ideas for improving the demo?

- Suggest additional patterns to showcase
- Improve the output formatting
- Add more detailed explanations
- Translate to other languages
- Create video walkthroughs

Submit issues or PRs on GitHub!

## See Also

- [Quick Start Guide](QUICK_START.md) - Get started guide
- [CLI Guide](CLI_GUIDE.md) - Complete command reference  
- [Wizard Guide](WIZARD_GUIDE.md) - Interactive migration tool
- [Patterns Guide](PATTERNS_GUIDE.md) - Python 2→3 patterns
- [README](README.md) - Main documentation

---

**Happy Migrating! 🚀**

For questions or feedback, please open an issue on GitHub.
