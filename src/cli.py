#!/usr/bin/env python3
"""
py2to3 - Unified CLI for Python 2 to Python 3 Migration Toolkit

A comprehensive command-line interface for managing Python 2 to 3 code migration.
Combines fixer, verifier, and report generator into a single, easy-to-use tool.
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}", file=sys.stderr)


def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def validate_path(path):
    """Validate that a path exists."""
    if not os.path.exists(path):
        print_error(f"Path does not exist: {path}")
        sys.exit(1)
    return path


def command_check(args):
    """Run the verifier to check Python 3 compatibility."""
    print_header("Python 3 Compatibility Check")
    
    validate_path(args.path)
    
    print_info(f"Checking path: {args.path}")
    print_info(f"Report file: {args.report or 'console output only'}\n")
    
    try:
        # Import verifier dynamically to avoid import errors if not available
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from verifier import Python3CompatibilityVerifier
        
        verifier = Python3CompatibilityVerifier()
        if os.path.isdir(args.path):
            verifier.verify_directory(args.path)
        else:
            verifier.verify_file(args.path)
        
        issues = verifier.issues_found
        
        # Print summary
        if issues:
            print_warning(f"Found {len(issues)} compatibility issue(s)")
            
            # Group issues by severity
            critical = [i for i in issues if i.get('severity') == 'critical']
            warnings = [i for i in issues if i.get('severity') == 'warning']
            
            if critical:
                print_error(f"Critical issues: {len(critical)}")
            if warnings:
                print_warning(f"Warnings: {len(warnings)}")
            
            # Show first few issues
            print("\nSample issues:")
            for issue in issues[:5]:
                severity_color = Colors.FAIL if issue.get('severity') == 'critical' else Colors.WARNING
                print(f"  {severity_color}• {issue.get('file', 'unknown')}:{issue.get('line', '?')}{Colors.ENDC}")
                print(f"    {issue.get('description', 'No description')}")
        else:
            print_success("No compatibility issues found!")
        
        # Save report if requested
        if args.report:
            verifier.save_report(args.report, issues)
            print_success(f"Report saved to: {args.report}")
        
        return 0 if not issues else 1
        
    except ImportError as e:
        print_error(f"Failed to import verifier: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during verification: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_fix(args):
    """Run the fixer to convert Python 2 code to Python 3."""
    print_header("Python 2 to Python 3 Auto-Fixer")
    
    validate_path(args.path)
    
    print_info(f"Fixing path: {args.path}")
    print_info(f"Backup directory: {args.backup_dir}")
    print_info(f"Dry run: {'Yes - no changes will be made' if args.dry_run else 'No'}\n")
    
    if args.dry_run:
        print_warning("DRY RUN MODE: No files will be modified")
    elif not args.yes:
        response = input(f"{Colors.WARNING}This will modify files. Continue? [y/N]: {Colors.ENDC}")
        if response.lower() not in ['y', 'yes']:
            print_info("Operation cancelled")
            return 0
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from fixer import Python2to3Fixer
        
        fixer = Python2to3Fixer(backup_dir=args.backup_dir)
        
        if os.path.isfile(args.path):
            results = fixer.fix_file(args.path, dry_run=args.dry_run)
        else:
            results = fixer.fix_directory(args.path, dry_run=args.dry_run)
        
        # Print summary
        fixes_count = len(results.get('fixes', []))
        errors_count = len(results.get('errors', []))
        
        if fixes_count > 0:
            print_success(f"Applied {fixes_count} fix(es)")
            
            # Show summary of fix types
            fix_types = {}
            for fix in results.get('fixes', []):
                fix_type = fix.get('type', 'unknown')
                fix_types[fix_type] = fix_types.get(fix_type, 0) + 1
            
            print("\nFixes by type:")
            for fix_type, count in sorted(fix_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {fix_type}: {count}")
        else:
            print_info("No fixes needed")
        
        if errors_count > 0:
            print_error(f"Encountered {errors_count} error(s)")
        
        # Save report if requested
        if args.report:
            with open(args.report, 'w') as f:
                f.write(f"Python 2 to 3 Fix Report\n")
                f.write(f"Generated: {datetime.datetime.now()}\n")
                f.write(f"Path: {args.path}\n\n")
                f.write(f"Fixes applied: {fixes_count}\n")
                f.write(f"Errors: {errors_count}\n\n")
                
                for fix in results.get('fixes', []):
                    f.write(f"- {fix.get('file')}: {fix.get('description')}\n")
            
            print_success(f"Report saved to: {args.report}")
        
        return 0 if errors_count == 0 else 1
        
    except ImportError as e:
        print_error(f"Failed to import fixer: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during fixing: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_stats(args):
    """Track and display migration statistics."""
    print_header("Migration Statistics")
    
    if hasattr(args, 'path') and args.path:
        validate_path(args.path)
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from stats_tracker import MigrationStatsTracker
        
        tracker = MigrationStatsTracker()
        
        if args.stats_action == 'collect':
            # Collect and display current stats
            print_info(f"Collecting statistics for: {args.path or 'current directory'}\n")
            
            stats = tracker.collect_stats(args.path)
            
            # Get previous snapshot for comparison if it exists
            previous = tracker.get_latest_snapshot()
            comparison = None
            
            if previous and not args.no_compare:
                comparison = tracker.compare_snapshots(previous, stats)
            
            # Save snapshot if requested
            if args.save:
                snapshot_path = tracker.save_snapshot(stats)
                print_success(f"Snapshot saved to: {snapshot_path}\n")
            
            # Display stats
            print(tracker.format_stats(stats, comparison))
            
            # Show recommendation
            if stats['summary']['progress_percentage'] < 100:
                remaining = stats['summary']['files_with_issues']
                print_info(f"Recommendation: Focus on fixing the {remaining} files with issues")
                print_info("Run 'py2to3 fix <path>' to automatically fix common patterns")
        
        elif args.stats_action == 'show':
            # Show latest snapshot
            latest = tracker.get_latest_snapshot()
            
            if not latest:
                print_warning("No statistics snapshots found")
                print_info("Run 'py2to3 stats collect --save' to create a snapshot")
                return 0
            
            print(tracker.format_stats(latest))
        
        elif args.stats_action == 'trend':
            # Show trend analysis
            trend = tracker.generate_trend_report()
            
            if not trend:
                print_warning("Not enough snapshots for trend analysis (minimum 2 required)")
                print_info("Run 'py2to3 stats collect --save' multiple times over your migration")
                return 0
            
            print_info(f"Trend Analysis ({trend['snapshots_count']} snapshots)\n")
            print(f"First Scan: {trend['first_scan']}")
            print(f"Latest Scan: {trend['latest_scan']}")
            print(f"Total Progress: {trend['total_progress']:+.2f}%")
            print(f"Issues Resolved: {trend['issues_resolved']}")
            print("\nProgress Timeline:")
            
            for i, point in enumerate(trend['timeline'], 1):
                print(f"  {i}. {point['timestamp']}")
                print(f"     Progress: {point['progress_percentage']:.2f}% | Issues: {point['total_issues']}")
        
        elif args.stats_action == 'clear':
            # Clear all snapshots
            if not args.yes:
                response = input(f"{Colors.WARNING}Clear all statistics snapshots? [y/N]: {Colors.ENDC}")
                if response.lower() not in ['y', 'yes']:
                    print_info("Operation cancelled")
                    return 0
            
            import shutil
            if tracker.stats_dir.exists():
                shutil.rmtree(tracker.stats_dir)
                print_success("All statistics snapshots cleared")
            else:
                print_info("No statistics snapshots to clear")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import stats tracker: {e}")
        return 1
    except Exception as e:
        print_error(f"Error tracking statistics: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_report(args):
    """Generate an HTML report of migration progress."""
    print_header("Migration Report Generator")
    
    print_info(f"Output file: {args.output}")
    print_info(f"Including fixes: {'Yes' if args.include_fixes else 'No'}")
    print_info(f"Including issues: {'Yes' if args.include_issues else 'No'}\n")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from report_generator import MigrationReportGenerator
        
        generator = MigrationReportGenerator()
        
        # If paths provided, scan them for data
        if args.scan_path:
            validate_path(args.scan_path)
            print_info(f"Scanning {args.scan_path} for migration data...")
            
            # This would ideally load existing fix/verification data
            # For now, we'll generate a basic report
        
        # Generate the report
        report_path = generator.generate_html_report(args.output)
        
        print_success(f"Report generated: {report_path}")
        print_info(f"Open in browser: file://{os.path.abspath(report_path)}")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import report generator: {e}")
        return 1
    except Exception as e:
        print_error(f"Error generating report: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_migrate(args):
    """Run the complete migration workflow: fix -> verify -> report."""
    print_header("Complete Migration Workflow")
    
    validate_path(args.path)
    
    print_info(f"Target path: {args.path}")
    print_info(f"Backup directory: {args.backup_dir}")
    print_info(f"Output report: {args.output}\n")
    
    if not args.yes:
        response = input(f"{Colors.WARNING}This will modify files and run the complete migration. Continue? [y/N]: {Colors.ENDC}")
        if response.lower() not in ['y', 'yes']:
            print_info("Operation cancelled")
            return 0
    
    # Step 1: Initial verification
    print_info("\n[Step 1/4] Running initial compatibility check...")
    args_check = argparse.Namespace(
        path=args.path,
        report=f"{args.output}.pre-fix-issues.txt",
        verbose=args.verbose
    )
    initial_issues = command_check(args_check)
    
    # Step 2: Apply fixes
    print_info("\n[Step 2/4] Applying automatic fixes...")
    args_fix = argparse.Namespace(
        path=args.path,
        backup_dir=args.backup_dir,
        dry_run=False,
        yes=True,
        report=f"{args.output}.fixes-applied.txt",
        verbose=args.verbose
    )
    fix_result = command_fix(args_fix)
    
    # Step 3: Post-fix verification
    print_info("\n[Step 3/4] Running post-fix verification...")
    args_check_post = argparse.Namespace(
        path=args.path,
        report=f"{args.output}.post-fix-issues.txt",
        verbose=args.verbose
    )
    final_issues = command_check(args_check_post)
    
    # Step 4: Generate report
    print_info("\n[Step 4/4] Generating comprehensive HTML report...")
    args_report = argparse.Namespace(
        output=args.output,
        include_fixes=True,
        include_issues=True,
        scan_path=args.path,
        verbose=args.verbose
    )
    command_report(args_report)
    
    # Final summary
    print_header("Migration Complete")
    print_success(f"Backup created in: {args.backup_dir}")
    print_success(f"Reports generated with prefix: {args.output}")
    
    if final_issues == 0:
        print_success("All compatibility issues resolved! ✨")
    else:
        print_warning("Some issues remain - check the reports for details")
    
    return final_issues


def command_config(args):
    """Manage configuration for py2to3 toolkit."""
    print_header("Configuration Management")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from config_manager import ConfigManager
        
        config_mgr = ConfigManager()
        
        if args.config_action == 'init':
            # Initialize a new config file
            if args.user:
                if config_mgr.has_user_config():
                    print_warning("User config already exists!")
                    print_info(f"Location: {config_mgr.USER_CONFIG_PATH}")
                    if not args.force:
                        print_error("Use --force to overwrite")
                        return 1
                
                if config_mgr.save_user_config():
                    print_success(f"User config created: {config_mgr.USER_CONFIG_PATH}")
                else:
                    print_error("Failed to create user config")
                    return 1
            else:
                # Project config
                config_path = args.path or Path.cwd() / ConfigManager.DEFAULT_CONFIG_NAME
                
                if Path(config_path).exists() and not args.force:
                    print_error(f"Config already exists: {config_path}")
                    print_info("Use --force to overwrite")
                    return 1
                
                if config_mgr.init_project_config(config_path):
                    print_success(f"Project config created: {config_path}")
                    print_info("Edit this file to customize your project settings")
                else:
                    print_error("Failed to create project config")
                    return 1
        
        elif args.config_action == 'show':
            # Show current configuration
            print_info("Active Configuration:\n")
            
            if config_mgr.has_user_config():
                print_success(f"User config: {config_mgr.USER_CONFIG_PATH}")
            
            if config_mgr.has_project_config():
                print_success(f"Project config: {config_mgr.get_config_path()}")
            
            if not config_mgr.has_user_config() and not config_mgr.has_project_config():
                print_info("No configuration files found (using defaults)")
            
            print("\nCurrent Settings:")
            print(json.dumps(config_mgr.to_dict(), indent=2))
        
        elif args.config_action == 'get':
            # Get a specific config value
            if not args.key:
                print_error("Please specify a key to get")
                return 1
            
            value = config_mgr.get(args.key)
            if value is not None:
                print_success(f"{args.key} = {json.dumps(value, indent=2)}")
            else:
                print_warning(f"Key not found: {args.key}")
                return 1
        
        elif args.config_action == 'set':
            # Set a config value
            if not args.key or args.value is None:
                print_error("Please specify both key and value")
                return 1
            
            # Try to parse value as JSON, fall back to string
            try:
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            
            config_mgr.set(args.key, value)
            
            # Save to appropriate config file
            if args.user:
                if config_mgr.save_user_config():
                    print_success(f"Updated user config: {args.key} = {value}")
                else:
                    return 1
            else:
                if not config_mgr.has_project_config():
                    print_error("No project config file found. Run 'py2to3 config init' first")
                    return 1
                
                if config_mgr.save_project_config():
                    print_success(f"Updated project config: {args.key} = {value}")
                else:
                    return 1
        
        elif args.config_action == 'path':
            # Show config file paths
            if args.user:
                print_info(f"User config path: {config_mgr.USER_CONFIG_PATH}")
                if config_mgr.has_user_config():
                    print_success("(exists)")
                else:
                    print_warning("(not created yet)")
            else:
                project_config = config_mgr.get_config_path()
                if project_config:
                    print_success(f"Project config: {project_config}")
                else:
                    print_warning("No project config found in current directory")
                    print_info(f"Default location: {Path.cwd() / ConfigManager.DEFAULT_CONFIG_NAME}")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import config manager: {e}")
        return 1
    except Exception as e:
        print_error(f"Error managing config: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='py2to3',
        description='Unified CLI for Python 2 to Python 3 migration toolkit',
        epilog='For detailed help on a command, run: py2to3 <command> --help'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    parser_check = subparsers.add_parser(
        'check',
        help='Check Python 3 compatibility',
        description='Verify code for Python 3 compatibility issues'
    )
    parser_check.add_argument('path', help='File or directory to check')
    parser_check.add_argument('-r', '--report', help='Save report to file')
    
    # Fix command
    parser_fix = subparsers.add_parser(
        'fix',
        help='Automatically fix Python 2 code',
        description='Convert Python 2 code to Python 3'
    )
    parser_fix.add_argument('path', help='File or directory to fix')
    parser_fix.add_argument('-b', '--backup-dir', default='backup', help='Backup directory (default: backup)')
    parser_fix.add_argument('-n', '--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser_fix.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    parser_fix.add_argument('-r', '--report', help='Save report to file')
    
    # Report command
    parser_report = subparsers.add_parser(
        'report',
        help='Generate HTML migration report',
        description='Create a comprehensive HTML report of migration progress'
    )
    parser_report.add_argument('-o', '--output', default='migration_report.html', help='Output HTML file (default: migration_report.html)')
    parser_report.add_argument('-s', '--scan-path', help='Path to scan for migration data')
    parser_report.add_argument('--include-fixes', action='store_true', default=True, help='Include fixes in report')
    parser_report.add_argument('--include-issues', action='store_true', default=True, help='Include issues in report')
    
    # Stats command
    parser_stats = subparsers.add_parser(
        'stats',
        help='Track migration progress statistics',
        description='Collect and analyze migration statistics over time'
    )
    stats_subparsers = parser_stats.add_subparsers(dest='stats_action', help='Statistics actions')
    
    # Stats collect
    parser_stats_collect = stats_subparsers.add_parser('collect', help='Collect current statistics')
    parser_stats_collect.add_argument('path', nargs='?', help='Path to analyze (defaults to current directory)')
    parser_stats_collect.add_argument('-s', '--save', action='store_true', help='Save statistics snapshot')
    parser_stats_collect.add_argument('--no-compare', action='store_true', help='Do not compare with previous snapshot')
    
    # Stats show
    parser_stats_show = stats_subparsers.add_parser('show', help='Show latest statistics snapshot')
    
    # Stats trend
    parser_stats_trend = stats_subparsers.add_parser('trend', help='Show progress trends over time')
    
    # Stats clear
    parser_stats_clear = stats_subparsers.add_parser('clear', help='Clear all statistics snapshots')
    parser_stats_clear.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    
    # Migrate command (complete workflow)
    parser_migrate = subparsers.add_parser(
        'migrate',
        help='Run complete migration workflow',
        description='Execute the complete migration: fix → verify → report'
    )
    parser_migrate.add_argument('path', help='File or directory to migrate')
    parser_migrate.add_argument('-b', '--backup-dir', default='backup', help='Backup directory (default: backup)')
    parser_migrate.add_argument('-o', '--output', default='migration_report.html', help='Output report base name (default: migration_report.html)')
    parser_migrate.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    
    # Config command
    parser_config = subparsers.add_parser(
        'config',
        help='Manage configuration',
        description='Manage py2to3 configuration files'
    )
    config_subparsers = parser_config.add_subparsers(dest='config_action', help='Config actions')
    
    # Config init
    parser_config_init = config_subparsers.add_parser('init', help='Initialize configuration file')
    parser_config_init.add_argument('-u', '--user', action='store_true', help='Create user-level config')
    parser_config_init.add_argument('-p', '--path', help='Config file path (for project config)')
    parser_config_init.add_argument('-f', '--force', action='store_true', help='Overwrite existing config')
    
    # Config show
    parser_config_show = config_subparsers.add_parser('show', help='Show current configuration')
    
    # Config get
    parser_config_get = config_subparsers.add_parser('get', help='Get a configuration value')
    parser_config_get.add_argument('key', nargs='?', help='Configuration key (dot notation supported)')
    
    # Config set
    parser_config_set = config_subparsers.add_parser('set', help='Set a configuration value')
    parser_config_set.add_argument('key', nargs='?', help='Configuration key (dot notation supported)')
    parser_config_set.add_argument('value', nargs='?', help='Value to set')
    parser_config_set.add_argument('-u', '--user', action='store_true', help='Save to user config instead of project config')
    
    # Config path
    parser_config_path = config_subparsers.add_parser('path', help='Show configuration file path')
    parser_config_path.add_argument('-u', '--user', action='store_true', help='Show user config path')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command provided
    if not args.command:
        parser.print_help()
        return 0
    
    # Disable colors if requested or if not in a TTY
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()
    
    # Load and apply configuration defaults (skip for config command)
    if args.command != 'config':
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from config_manager import ConfigManager
            
            config_mgr = ConfigManager()
            args = config_mgr.apply_to_args(args)
        except Exception:
            # If config loading fails, continue with defaults
            pass
    
    # Route to appropriate command handler
    if args.command == 'check':
        return command_check(args)
    elif args.command == 'fix':
        return command_fix(args)
    elif args.command == 'report':
        return command_report(args)
    elif args.command == 'stats':
        return command_stats(args)
    elif args.command == 'migrate':
        return command_migrate(args)
    elif args.command == 'config':
        return command_config(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
