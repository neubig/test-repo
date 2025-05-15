---
name: git_helper
type: knowledge
version: 1.0.0
agent: CodeActAgent
triggers:
- git
- github
- version control
- commit
- branch
- merge
---

# Git Helper Microagent

I'm a specialized Git helper that can assist with common Git operations and best practices. When you need help with Git commands or workflows, I can provide guidance.

## Common Git Commands

### Basic Commands
- `git init` - Initialize a new Git repository
- `git clone <repository>` - Clone a repository
- `git add <file>` - Add file(s) to staging area
- `git commit -m "message"` - Commit staged changes
- `git status` - Check repository status
- `git log` - View commit history

### Branch Operations
- `git branch` - List branches
- `git branch <name>` - Create a new branch
- `git checkout <branch>` - Switch to a branch
- `git checkout -b <branch>` - Create and switch to a new branch
- `git merge <branch>` - Merge a branch into current branch
- `git branch -d <branch>` - Delete a branch

### Remote Operations
- `git remote add <name> <url>` - Add a remote repository
- `git push <remote> <branch>` - Push changes to remote
- `git pull <remote> <branch>` - Pull changes from remote
- `git fetch` - Fetch changes from remote

## Best Practices

1. **Commit Messages**: Write clear, concise commit messages that explain what changes were made and why.
2. **Small Commits**: Make small, focused commits that address a single issue or feature.
3. **Branch Strategy**: Use feature branches for new features and bug fixes.
4. **Pull Before Push**: Always pull changes before pushing to avoid conflicts.
5. **Code Review**: Use pull requests for code review before merging.

I can help you with specific Git commands, troubleshoot Git issues, or provide guidance on Git workflows. Just ask!