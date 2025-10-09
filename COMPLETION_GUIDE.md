# Shell Completion Guide for py2to3 🎯

## Overview

The py2to3 toolkit now includes powerful shell completion support for **bash**, **zsh**, and **fish** shells! With 47 commands and hundreds of options, shell completions dramatically improve your workflow by:

- ✨ Auto-completing commands and subcommands
- 🎯 Suggesting available options with Tab
- 🚀 Reducing typos and increasing productivity
- 📚 Helping discover available commands
- ⚡ Making the toolkit easier to learn and use

## Quick Start

### Install Completions (Automatic)

The easiest way to enable completions is to use the automatic installer:

```bash
# Auto-detect your shell and install completions
./py2to3 completion install

# Or specify your shell explicitly
./py2to3 completion install bash
./py2to3 completion install zsh
./py2to3 completion install fish
```

After installation, restart your shell or source your configuration file:

```bash
# For bash
source ~/.bashrc

# For zsh
source ~/.zshrc

# For fish
# Fish automatically loads completions, just restart the shell
```

### Check Status

To see which shells have completions installed:

```bash
./py2to3 completion status
```

Example output:
```
Current shell: bash

Installation status:
  bash    : ✓ Installed
  zsh     : ✗ Not installed
  fish    : ✗ Not installed

✓ Completions are installed for your current shell (bash)
```

## Usage Examples

Once installed, you can use Tab completion for:

### Basic Command Completion

```bash
# Press Tab after typing partial command
./py2to3 ch<Tab>
# Completes to: ./py2to3 check

./py2to3 pre<Tab>
# Shows: preflight  precommit
```

### Subcommand Completion

```bash
# Complete subcommands
./py2to3 backup <Tab>
# Shows: list  restore  clean  diff  scan

./py2to3 git <Tab>
# Shows: status  info  branch  checkpoint  commit  log  rollback  diff

./py2to3 completion <Tab>
# Shows: generate  install  uninstall  status
```

### Option Completion

```bash
# Complete options
./py2to3 check --<Tab>
# Shows: --report  --json  --verbose  --help

./py2to3 fix --<Tab>
# Shows: --backup-dir  --report  --dry-run  --pattern  --help
```

### Format and Value Completion

```bash
# Complete format options
./py2to3 stats show --format <Tab>
# Shows: json  text  table

./py2to3 completion generate <Tab>
# Shows: bash  zsh  fish
```

## Advanced Features

### Manual Installation

If you prefer manual installation or need custom paths:

#### Bash

```bash
# Generate completion script
./py2to3 completion generate bash -o ~/.bash_completion.d/py2to3

# Add to your ~/.bashrc
echo "source ~/.bash_completion.d/py2to3" >> ~/.bashrc
source ~/.bashrc
```

#### Zsh

```bash
# Create completion directory if it doesn't exist
mkdir -p ~/.zsh/completion

# Generate completion script
./py2to3 completion generate zsh -o ~/.zsh/completion/_py2to3

# Add to your ~/.zshrc (if not already present)
echo "fpath=(~/.zsh/completion $fpath)" >> ~/.zshrc
echo "autoload -Uz compinit && compinit" >> ~/.zshrc
source ~/.zshrc
```

#### Fish

```bash
# Create completion directory if it doesn't exist
mkdir -p ~/.config/fish/completions

# Generate completion script
./py2to3 completion generate fish -o ~/.config/fish/completions/py2to3.fish

# Fish automatically loads completions, just restart
```

### Viewing Completion Scripts

You can view or save the generated completion scripts:

```bash
# View bash completion script
./py2to3 completion generate bash

# Save to a custom location
./py2to3 completion generate zsh -o /path/to/custom/_py2to3

# Generate and pipe to another command
./py2to3 completion generate fish | less
```

### Uninstalling Completions

If you need to remove completions:

```bash
# Auto-detect shell and uninstall
./py2to3 completion uninstall

# Or specify shell explicitly
./py2to3 completion uninstall bash
./py2to3 completion uninstall zsh
./py2to3 completion uninstall fish
```

## Supported Commands

Completions are available for all 47 py2to3 commands:

### Core Migration Commands
- `check` - Check Python 3 compatibility
- `fix` - Apply automated fixes
- `migrate` - Full migration workflow
- `preflight` - Pre-migration checks
- `review` - Review changes

### Analysis & Reporting
- `stats` - Migration statistics
- `report` - Generate reports
- `report-card` - Quality assessment
- `dashboard` - Interactive dashboard
- `status` - Project status
- `health` - Health monitoring

### Planning & Organization
- `plan` - Migration planning
- `estimate` - Effort estimation
- `risk` - Risk analysis
- `recipe` - Migration recipes
- `journal` - Migration journal
- `state` - State management

### Code Quality
- `quality` - Code quality checks
- `lint` - Linting integration
- `typehints` - Type hints generation
- `modernize` - Code modernization
- `imports` - Import optimization
- `encoding` - Encoding analysis
- `validate` - Runtime validation

### Development Tools
- `test-gen` - Test generation
- `bench` - Performance benchmarking
- `compare` - Compare versions
- `search` - Pattern search
- `docs` - Documentation generation

### Version Control
- `git` - Git integration
- `backup` - Backup management
- `rollback` - Rollback operations
- `changelog` - Changelog generation

### Configuration & Setup
- `config` - Configuration management
- `venv` - Virtual environment
- `deps` - Dependency analysis
- `metadata` - Metadata updates
- `freeze` - Freeze requirements
- `version-check` - Version checking

### Collaboration
- `export` - Export configuration
- `import` - Import configuration
- `precommit` - Pre-commit hooks

### Interactive Tools
- `wizard` - Interactive wizard
- `interactive` - Interactive fixer
- `watch` - Watch mode
- `convert` - Snippet converter

### Shell Integration
- `completion` - Shell completions (this feature!)

## Troubleshooting

### Completions Not Working

1. **Check Installation Status**
   ```bash
   ./py2to3 completion status
   ```

2. **Verify Shell Detection**
   ```bash
   echo $SHELL
   ```

3. **Reinstall Completions**
   ```bash
   ./py2to3 completion uninstall
   ./py2to3 completion install
   ```

4. **Restart Shell**
   ```bash
   exec $SHELL
   ```

### Bash Completions Not Loading

If bash completions aren't working:

1. Check if bash-completion is installed:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install bash-completion

   # On macOS
   brew install bash-completion@2
   ```

2. Ensure bash-completion is sourced in your ~/.bashrc:
   ```bash
   # Add this to ~/.bashrc if missing
   if [ -f /etc/bash_completion ]; then
       . /etc/bash_completion
   fi
   ```

### Zsh Completions Not Loading

If zsh completions aren't working:

1. Make sure compinit is called in your ~/.zshrc:
   ```bash
   autoload -Uz compinit && compinit
   ```

2. Clear the completion cache:
   ```bash
   rm ~/.zcompdump*
   exec zsh
   ```

### Fish Completions Not Loading

If fish completions aren't working:

1. Check completion directory exists:
   ```bash
   mkdir -p ~/.config/fish/completions
   ```

2. Verify the completion file is there:
   ```bash
   ls -la ~/.config/fish/completions/py2to3.fish
   ```

## Benefits

### Productivity Boost

With shell completions, you can:

- **Complete commands instantly**: Press Tab instead of typing full command names
- **Discover subcommands**: See all available options for any command
- **Avoid typos**: Tab completion ensures correct spelling
- **Learn faster**: Explore commands interactively without reading docs
- **Work efficiently**: Reduce keystrokes by 50% or more

### Example Workflow

Without completions:
```bash
./py2to3 backup list --path src/ --output backup-list.txt
# ^ Must type/remember everything ^
```

With completions:
```bash
./py2to3 ba<Tab> li<Tab> --p<Tab> src/ --o<Tab> backup-list.txt
# ^ Tab completes everything! ^
```

## Best Practices

1. **Install for Your Primary Shell**: Focus on the shell you use most
2. **Check Status Regularly**: Use `completion status` to verify installation
3. **Update After Upgrades**: Reinstall completions after major py2to3 updates
4. **Share with Team**: Include completion setup in team onboarding docs

## Integration with Other Tools

### With Terminal Multiplexers

Completions work seamlessly with:
- **tmux**: Completions work in all tmux panes
- **screen**: Full completion support
- **Terminal.app / iTerm2**: Works with all completion features

### With Development Environments

- **VS Code Terminal**: Full support
- **PyCharm Terminal**: Full support
- **Vim/Neovim Terminal**: Full support

## FAQs

### Q: Do I need to reinstall completions after updating py2to3?

A: Not usually, but if new commands are added, you should regenerate completions:
```bash
./py2to3 completion install --force
```

### Q: Can I have completions for multiple shells?

A: Yes! Install completions for each shell you use:
```bash
./py2to3 completion install bash
./py2to3 completion install zsh
```

### Q: Do completions work with the global installation?

A: Yes! If you installed py2to3 globally (`pip install .`), completions work with the `py2to3` command anywhere.

### Q: Can I customize completion behavior?

A: The completion scripts are standard shell scripts. You can modify them after generation, but changes will be overwritten on reinstall.

### Q: Do completions slow down my shell?

A: No, completions are loaded lazily and have negligible performance impact.

## Technical Details

### How It Works

The completion system:

1. **Generates shell-specific scripts** using native completion syntax
2. **Installs to standard locations** recognized by each shell
3. **Auto-detects shell** from `$SHELL` environment variable
4. **Provides context-aware suggestions** based on current command

### Completion Locations

Default installation paths:

- **Bash**: `~/.bash_completion.d/py2to3`
- **Zsh**: `~/.zsh/completion/_py2to3`
- **Fish**: `~/.config/fish/completions/py2to3.fish`

### Supported Features by Shell

| Feature | Bash | Zsh | Fish |
|---------|------|-----|------|
| Command completion | ✓ | ✓ | ✓ |
| Subcommand completion | ✓ | ✓ | ✓ |
| Option completion | ✓ | ✓ | ✓ |
| Value completion | ✓ | ✓ | ✓ |
| File completion | ✓ | ✓ | ✓ |
| Descriptions | ✗ | ✓ | ✓ |

## Contributing

Want to improve completions? We welcome contributions!

- Add more context-aware completions
- Improve completion descriptions
- Add support for more shells (PowerShell, etc.)
- Enhance file/path completion logic

## Summary

Shell completions make the py2to3 toolkit significantly more user-friendly. With Tab completion for all 47 commands and hundreds of options, you'll work faster and make fewer mistakes.

**Get started now:**
```bash
./py2to3 completion install
```

Happy migrating! 🚀
