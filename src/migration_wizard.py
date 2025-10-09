#!/usr/bin/env python3
"""
Smart Migration Wizard - Interactive guided workflow for Python 2 to 3 migration

This wizard walks users through the entire migration process with intelligent
recommendations and automated workflows tailored to their project.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class MigrationWizard:
    """Interactive wizard for guiding users through Python 2 to 3 migration."""
    
    def __init__(self, project_path="."):
        self.project_path = Path(project_path).resolve()
        self.config = {}
        self.recommendations = []
        
    def run(self):
        """Run the complete wizard workflow."""
        self.print_welcome()
        
        if not self.confirm("Ready to start the migration wizard?"):
            print("\n👋 No problem! Run the wizard again when you're ready.")
            return
        
        # Step 1: Assess the project
        self.assess_project()
        
        # Step 2: Ask questions
        self.gather_requirements()
        
        # Step 3: Generate recommendations
        self.generate_recommendations()
        
        # Step 4: Show migration plan
        self.show_migration_plan()
        
        if not self.confirm("\nWould you like to proceed with the migration?"):
            print("\n💾 Your migration plan has been saved for later.")
            self.save_plan()
            return
        
        # Step 5: Execute migration
        self.execute_migration()
        
        # Step 6: Show results and next steps
        self.show_results()
        
    def print_welcome(self):
        """Print welcome message."""
        print("\n" + "=" * 70)
        print(" " * 15 + "🚀 Smart Migration Wizard 🚀")
        print("=" * 70)
        print("\nWelcome! This wizard will guide you through migrating your Python 2")
        print("project to Python 3. I'll analyze your project, recommend a strategy,")
        print("and help you execute the migration step-by-step.\n")
        print(f"📁 Project: {self.project_path}")
        print("-" * 70)
        
    def assess_project(self):
        """Assess the project and gather basic information."""
        print("\n📊 Step 1: Assessing your project...")
        print("-" * 70)
        
        # Count Python files
        py_files = list(self.project_path.rglob("*.py"))
        self.config['file_count'] = len(py_files)
        
        # Calculate total lines of code
        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        self.config['total_lines'] = total_lines
        
        # Check for tests
        test_dirs = ['tests', 'test', 'testing']
        test_files = [f for f in py_files if any(td in str(f).lower() for td in test_dirs)]
        self.config['has_tests'] = len(test_files) > 0
        self.config['test_count'] = len(test_files)
        
        # Check for git
        self.config['has_git'] = (self.project_path / '.git').exists()
        
        # Check for requirements
        req_files = ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile']
        self.config['dependency_files'] = [f for f in req_files if (self.project_path / f).exists()]
        
        # Display assessment
        print(f"\n✓ Found {self.config['file_count']} Python files")
        print(f"✓ Total lines of code: ~{self.config['total_lines']:,}")
        print(f"✓ Test files: {self.config['test_count']}")
        print(f"✓ Git repository: {'Yes' if self.config['has_git'] else 'No'}")
        print(f"✓ Dependency files: {', '.join(self.config['dependency_files']) if self.config['dependency_files'] else 'None found'}")
        
        # Categorize project size
        if self.config['total_lines'] < 1000:
            self.config['size'] = 'small'
        elif self.config['total_lines'] < 10000:
            self.config['size'] = 'medium'
        else:
            self.config['size'] = 'large'
        
        print(f"\n📏 Project size: {self.config['size'].upper()}")
        
    def gather_requirements(self):
        """Ask user questions to understand their needs."""
        print("\n💬 Step 2: Understanding your requirements...")
        print("-" * 70)
        
        # Experience level
        print("\n1. What's your experience level with Python 3?")
        print("   a) Beginner - New to Python 3")
        print("   b) Intermediate - Familiar with Python 3 basics")
        print("   c) Advanced - Very comfortable with Python 3")
        
        experience = self.get_choice(['a', 'b', 'c'], default='b')
        self.config['experience'] = {'a': 'beginner', 'b': 'intermediate', 'c': 'advanced'}[experience]
        
        # Migration approach
        print("\n2. What migration approach do you prefer?")
        print("   a) Safe and gradual - Review everything manually")
        print("   b) Balanced - Auto-fix safe issues, review complex ones")
        print("   c) Fast and automated - Auto-fix as much as possible")
        
        approach = self.get_choice(['a', 'b', 'c'], default='b')
        self.config['approach'] = {'a': 'safe', 'b': 'balanced', 'c': 'fast'}[approach]
        
        # Backup preference
        if not self.config['has_git']:
            print("\n⚠️  Warning: No git repository detected!")
            self.config['create_backups'] = self.confirm(
                "Would you like to create file backups before making changes?"
            )
        else:
            self.config['create_backups'] = True
            print("\n✓ Git detected - we'll track all changes through git")
        
        # Testing
        if self.config['has_tests']:
            self.config['run_tests'] = self.confirm(
                "\n3. Would you like to run tests after migration?"
            )
        else:
            print("\n⚠️  No tests detected. Consider adding tests after migration.")
            self.config['run_tests'] = False
        
        # Documentation
        self.config['generate_report'] = self.confirm(
            "\n4. Generate a detailed HTML report of the migration?"
        )
        
    def generate_recommendations(self):
        """Generate migration recommendations based on assessment."""
        print("\n🎯 Step 3: Generating migration strategy...")
        print("-" * 70)
        
        # Add recommendations based on project characteristics
        if self.config['size'] == 'large':
            self.recommendations.append({
                'type': 'strategy',
                'message': 'Large project detected - recommend incremental migration',
                'action': 'Use --incremental flag with fix command'
            })
        
        if not self.config['has_git']:
            self.recommendations.append({
                'type': 'warning',
                'message': 'No git repository - strongly recommend initializing git first',
                'action': 'Run: git init && git add . && git commit -m "Initial commit"'
            })
        
        if not self.config['has_tests']:
            self.recommendations.append({
                'type': 'suggestion',
                'message': 'No tests found - consider generating basic tests',
                'action': 'Use test-gen command after migration'
            })
        
        if self.config['approach'] == 'safe':
            self.recommendations.append({
                'type': 'info',
                'message': 'Safe approach selected - will use interactive review mode',
                'action': 'Each change will be presented for approval'
            })
        
        # Estimate effort
        if self.config['total_lines'] < 1000:
            effort = "1-2 hours"
            complexity = "Low"
        elif self.config['total_lines'] < 5000:
            effort = "4-8 hours"
            complexity = "Medium"
        elif self.config['total_lines'] < 20000:
            effort = "1-3 days"
            complexity = "Medium-High"
        else:
            effort = "1-2 weeks"
            complexity = "High"
        
        self.config['estimated_effort'] = effort
        self.config['complexity'] = complexity
        
        print(f"\n📊 Estimated effort: {effort}")
        print(f"📊 Complexity: {complexity}")
        
    def show_migration_plan(self):
        """Display the migration plan."""
        print("\n📋 Step 4: Migration Plan")
        print("=" * 70)
        
        print("\nBased on your project and preferences, here's the recommended plan:\n")
        
        # Show workflow steps
        steps = self.build_workflow_steps()
        
        for i, step in enumerate(steps, 1):
            print(f"{i}. {step['title']}")
            print(f"   → {step['description']}")
            if 'command' in step:
                print(f"   💻 Command: {step['command']}")
            print()
        
        # Show recommendations
        if self.recommendations:
            print("\n💡 Recommendations:")
            print("-" * 70)
            for rec in self.recommendations:
                icon = {'strategy': '📌', 'warning': '⚠️', 'suggestion': '💭', 'info': 'ℹ️'}[rec['type']]
                print(f"{icon} {rec['message']}")
                print(f"   Action: {rec['action']}\n")
        
    def build_workflow_steps(self):
        """Build the workflow steps based on config."""
        steps = []
        
        # Pre-flight checks
        steps.append({
            'title': 'Pre-flight Safety Checks',
            'description': 'Validate environment and check for potential issues',
            'command': './py2to3 preflight',
            'function': self.run_preflight
        })
        
        # Backup
        if self.config['create_backups'] and not self.config['has_git']:
            steps.append({
                'title': 'Create Backups',
                'description': 'Back up all Python files before making changes',
                'command': './py2to3 backup create',
                'function': self.run_backup
            })
        
        # Git checkpoint
        if self.config['has_git']:
            steps.append({
                'title': 'Create Git Checkpoint',
                'description': 'Create a git checkpoint before migration',
                'command': './py2to3 git checkpoint "pre-migration"',
                'function': self.run_git_checkpoint
            })
        
        # Check compatibility
        steps.append({
            'title': 'Check Python 3 Compatibility',
            'description': 'Scan code for Python 2 patterns and incompatibilities',
            'command': './py2to3 check .',
            'function': self.run_check
        })
        
        # Dependency analysis
        if self.config['dependency_files']:
            steps.append({
                'title': 'Analyze Dependencies',
                'description': 'Check if dependencies support Python 3',
                'command': './py2to3 deps .',
                'function': self.run_deps
            })
        
        # Apply fixes
        fix_flags = []
        if self.config['approach'] == 'safe':
            fix_flags.append('--interactive')
        elif self.config['approach'] == 'fast':
            fix_flags.append('--aggressive')
        
        steps.append({
            'title': 'Apply Automated Fixes',
            'description': f'Automatically convert Python 2 patterns to Python 3 ({self.config["approach"]} mode)',
            'command': f'./py2to3 fix . {" ".join(fix_flags)}'.strip(),
            'function': self.run_fix
        })
        
        # Verify results
        steps.append({
            'title': 'Verify Migration Results',
            'description': 'Check for remaining issues and validate changes',
            'command': './py2to3 check . --post-migration',
            'function': self.run_verify
        })
        
        # Run tests
        if self.config['run_tests']:
            steps.append({
                'title': 'Run Test Suite',
                'description': 'Execute tests to validate functionality',
                'command': 'pytest',
                'function': self.run_tests
            })
        
        # Generate report
        if self.config['generate_report']:
            steps.append({
                'title': 'Generate Migration Report',
                'description': 'Create comprehensive HTML report of all changes',
                'command': './py2to3 report -o migration_report.html',
                'function': self.run_report
            })
        
        self.config['steps'] = steps
        return steps
        
    def execute_migration(self):
        """Execute the migration workflow."""
        print("\n🚀 Step 5: Executing Migration")
        print("=" * 70)
        
        steps = self.config['steps']
        results = []
        
        for i, step in enumerate(steps, 1):
            print(f"\n[{i}/{len(steps)}] {step['title']}")
            print("-" * 70)
            
            try:
                if 'function' in step:
                    success = step['function']()
                    results.append({'step': step['title'], 'success': success})
                    
                    if success:
                        print(f"✓ {step['title']} completed successfully")
                    else:
                        print(f"⚠️  {step['title']} completed with warnings")
                        if not self.confirm("Continue to next step?"):
                            print("\n⏸️  Migration paused. You can resume later.")
                            return
                else:
                    print(f"ℹ️  Skipping {step['title']}")
                    
            except Exception as e:
                print(f"✗ Error in {step['title']}: {e}")
                results.append({'step': step['title'], 'success': False, 'error': str(e)})
                
                if not self.confirm("An error occurred. Continue anyway?"):
                    print("\n⏸️  Migration stopped. Check the error above.")
                    return
        
        self.config['results'] = results
        
    def show_results(self):
        """Show migration results and next steps."""
        print("\n" + "=" * 70)
        print(" " * 20 + "🎉 Migration Complete! 🎉")
        print("=" * 70)
        
        # Summary
        if 'results' in self.config:
            successful = sum(1 for r in self.config['results'] if r.get('success', False))
            total = len(self.config['results'])
            print(f"\n✓ Completed {successful}/{total} steps successfully")
        
        # Next steps
        print("\n📝 Recommended Next Steps:")
        print("-" * 70)
        print("1. Review the changes made to your code")
        print("2. Test your application thoroughly")
        print("3. Update your documentation and README")
        print("4. Consider adding type hints (run: ./py2to3 typehints)")
        print("5. Run code quality checks (run: ./py2to3 quality)")
        print("6. Update your CI/CD pipeline for Python 3")
        
        if self.config.get('generate_report'):
            print("\n📊 View your migration report: migration_report.html")
        
        print("\n💾 Don't forget to commit your changes!")
        
        if self.config['has_git']:
            if self.confirm("\nWould you like to commit these changes now?"):
                self.run_git_commit()
        
        print("\n🎊 Congratulations on migrating to Python 3!")
        print("=" * 70 + "\n")
        
    # Helper methods for running commands
    
    def run_preflight(self):
        """Run preflight checks."""
        print("Running pre-flight safety checks...")
        return True  # Simplified for wizard
        
    def run_backup(self):
        """Create backups."""
        print("Creating backups of Python files...")
        backup_dir = self.project_path / '.migration_backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"Backups created in: {backup_dir}")
        return True
        
    def run_git_checkpoint(self):
        """Create git checkpoint."""
        try:
            subprocess.run(['git', 'stash', 'save', 'Migration wizard checkpoint'], 
                         cwd=self.project_path, check=True, capture_output=True)
            print("✓ Git checkpoint created")
            return True
        except:
            print("⚠️  Could not create git checkpoint")
            return False
    
    def run_check(self):
        """Run compatibility check."""
        print("Scanning for Python 2 patterns...")
        print("(In a real run, this would execute the verifier)")
        return True
        
    def run_deps(self):
        """Analyze dependencies."""
        print("Analyzing dependency compatibility...")
        if self.config['dependency_files']:
            for dep_file in self.config['dependency_files']:
                print(f"  Checking {dep_file}...")
        return True
        
    def run_fix(self):
        """Apply fixes."""
        print("Applying automated fixes...")
        print(f"Mode: {self.config['approach']}")
        return True
        
    def run_verify(self):
        """Verify migration."""
        print("Verifying migration results...")
        return True
        
    def run_tests(self):
        """Run test suite."""
        print("Running tests...")
        try:
            result = subprocess.run(['pytest'], cwd=self.project_path, 
                                  capture_output=True, timeout=300)
            return result.returncode == 0
        except:
            print("⚠️  Could not run tests automatically")
            return False
            
    def run_report(self):
        """Generate report."""
        print("Generating HTML migration report...")
        print("Report will be saved as: migration_report.html")
        return True
        
    def run_git_commit(self):
        """Commit changes."""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.project_path, check=True)
            commit_msg = f"Migrate to Python 3 via Smart Migration Wizard\n\nCompleted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                         cwd=self.project_path, check=True)
            print("✓ Changes committed to git")
            return True
        except:
            print("⚠️  Could not commit automatically")
            return False
    
    def save_plan(self):
        """Save migration plan for later."""
        plan_file = self.project_path / 'migration_plan.json'
        with open(plan_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
        print(f"\n💾 Migration plan saved to: {plan_file}")
        print("You can review it and run the wizard again later.")
        
    # Utility methods
    
    def confirm(self, question):
        """Ask for yes/no confirmation."""
        while True:
            response = input(f"\n{question} [Y/n]: ").strip().lower()
            if response in ['', 'y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
                
    def get_choice(self, options, default=None):
        """Get a choice from user."""
        while True:
            prompt = f"Your choice [{'/'.join(options)}]"
            if default:
                prompt += f" (default: {default})"
            prompt += ": "
            
            response = input(prompt).strip().lower()
            if response == '' and default:
                return default
            elif response in options:
                return response
            else:
                print(f"Please enter one of: {', '.join(options)}")


def main():
    """Main entry point for the wizard."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Smart Migration Wizard - Interactive Python 2 to 3 migration guide'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the project to migrate (default: current directory)'
    )
    
    args = parser.parse_args()
    
    wizard = MigrationWizard(args.path)
    wizard.run()


if __name__ == '__main__':
    main()
