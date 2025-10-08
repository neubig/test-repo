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


def command_preflight(args):
    """Run pre-migration safety checks."""
    print_header("Pre-Migration Safety Check")
    
    validate_path(args.path)
    
    print_info(f"Checking project: {args.path}")
    print_info(f"Backup directory: {args.backup_dir}\n")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from preflight_checker import PreflightChecker, PreflightCheck
        
        checker = PreflightChecker(args.path)
        checks = checker.run_all_checks(backup_dir=args.backup_dir)
        
        # Display results
        if args.json:
            import json
            summary = checker.get_summary()
            checks_data = [
                {
                    'name': c.name,
                    'status': c.status,
                    'message': c.message,
                    'details': c.details,
                    'fix_suggestion': c.fix_suggestion
                }
                for c in checks
            ]
            result = {
                'summary': summary,
                'checks': checks_data
            }
            print(json.dumps(result, indent=2))
        else:
            # Print individual checks with colors
            status_colors = {
                PreflightCheck.PASS: Colors.OKGREEN,
                PreflightCheck.WARN: Colors.WARNING,
                PreflightCheck.FAIL: Colors.FAIL,
                PreflightCheck.INFO: Colors.OKCYAN
            }
            
            status_symbols = {
                PreflightCheck.PASS: '✓',
                PreflightCheck.WARN: '⚠',
                PreflightCheck.FAIL: '✗',
                PreflightCheck.INFO: 'ℹ'
            }
            
            # Group by status
            status_order = [PreflightCheck.FAIL, PreflightCheck.WARN, PreflightCheck.PASS, PreflightCheck.INFO]
            
            for status in status_order:
                status_checks = [c for c in checks if c.status == status]
                if not status_checks:
                    continue
                
                print(f"\n{Colors.BOLD}{status}:{Colors.ENDC}")
                
                for check in status_checks:
                    color = status_colors.get(status, '')
                    symbol = status_symbols.get(status, '•')
                    print(f"{color}{symbol} {check.name}: {check.message}{Colors.ENDC}")
                    
                    if args.verbose and check.details:
                        for detail in check.details[:5]:
                            print(f"  {color}→ {detail}{Colors.ENDC}")
                    
                    if check.fix_suggestion:
                        print(f"  {Colors.OKCYAN}💡 {check.fix_suggestion}{Colors.ENDC}")
            
            # Print summary
            summary = checker.get_summary()
            if summary:
                print(f"\n{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
                print(f"{Colors.BOLD}SUMMARY{Colors.ENDC}")
                print(f"{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
                
                overall_color = Colors.OKGREEN if summary['overall_status'] == 'READY' else Colors.WARNING if summary['overall_status'] == 'WARNING' else Colors.FAIL
                print(f"Status: {overall_color}{Colors.BOLD}{summary['overall_status']}{Colors.ENDC}")
                print(f"Message: {summary['message']}")
                print(f"\nTotal Checks: {summary['total_checks']}")
                print(f"  {Colors.OKGREEN}✓ Passed: {summary['passed']}{Colors.ENDC}")
                print(f"  {Colors.WARNING}⚠ Warnings: {summary['warnings']}{Colors.ENDC}")
                print(f"  {Colors.FAIL}✗ Failed: {summary['failures']}{Colors.ENDC}")
                print(f"  {Colors.OKCYAN}ℹ Info: {summary['info']}{Colors.ENDC}")
                print(f"{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
        
        # Return appropriate exit code
        summary = checker.get_summary()
        if summary['overall_status'] == 'FAILED':
            return 1
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import preflight checker: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during preflight check: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_backup(args):
    """Manage backups created during migration."""
    print_header("Backup Management")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from backup_manager import BackupManager
        
        backup_dir = getattr(args, 'backup_dir', 'backup')
        manager = BackupManager(backup_dir=backup_dir)
        
        if args.backup_action == 'list':
            # List all backups
            backups = manager.list_backups(pattern=getattr(args, 'pattern', None))
            
            if not backups:
                print_info("No backups found")
                return 0
            
            print_success(f"Found {len(backups)} backup(s):\n")
            
            for i, backup in enumerate(backups, 1):
                timestamp = backup.get('timestamp', 'unknown')
                original = backup.get('original_path', 'unknown')
                backup_path = backup.get('backup_path', 'unknown')
                size_kb = backup.get('size', 0) / 1024
                
                print(f"{Colors.BOLD}{i}. {os.path.basename(original)}{Colors.ENDC}")
                print(f"   Original: {original}")
                print(f"   Backup:   {backup_path}")
                print(f"   Time:     {timestamp}")
                print(f"   Size:     {size_kb:.2f} KB")
                if backup.get('description'):
                    print(f"   Note:     {backup['description']}")
                print()
            
            # Show stats
            stats = manager.get_backup_stats()
            print(f"{Colors.OKCYAN}Summary:{Colors.ENDC}")
            print(f"  Total backups: {stats['total_count']}")
            print(f"  Total size:    {stats['total_size_mb']} MB")
            if stats['oldest']:
                print(f"  Oldest:        {stats['oldest']}")
            if stats['newest']:
                print(f"  Newest:        {stats['newest']}")
            
            return 0
        
        elif args.backup_action == 'restore':
            # Restore from backup
            if not args.backup_path:
                print_error("Backup path is required for restore")
                return 1
            
            print_info(f"Restoring from: {args.backup_path}")
            
            if not args.yes and not args.dry_run:
                response = input(f"{Colors.WARNING}This will overwrite existing files. Continue? [y/N]: {Colors.ENDC}")
                if response.lower() not in ['y', 'yes']:
                    print_info("Operation cancelled")
                    return 0
            
            if args.dry_run:
                print_warning("DRY RUN MODE: No files will be modified\n")
            
            result = manager.restore_file(
                args.backup_path,
                original_path=getattr(args, 'target', None),
                dry_run=args.dry_run
            )
            
            if result['status'] == 'success':
                print_success(f"Restored: {result['original_path']}")
            elif result['status'] == 'dry_run':
                print_info(f"Would restore to: {result['original_path']}")
            
            return 0
        
        elif args.backup_action == 'clean':
            # Clean up old backups
            print_info("Cleaning backups...")
            
            if args.all:
                print_warning("This will remove ALL backups")
            elif args.older_than:
                print_info(f"Removing backups older than {args.older_than} days")
            elif args.pattern:
                print_info(f"Removing backups matching pattern: {args.pattern}")
            
            if not args.yes and not args.dry_run:
                response = input(f"{Colors.WARNING}This will delete backup files. Continue? [y/N]: {Colors.ENDC}")
                if response.lower() not in ['y', 'yes']:
                    print_info("Operation cancelled")
                    return 0
            
            if args.dry_run:
                print_warning("DRY RUN MODE: No files will be deleted\n")
            
            result = manager.clean_backups(
                older_than_days=getattr(args, 'older_than', None),
                pattern=getattr(args, 'pattern', None),
                all_backups=args.all,
                dry_run=args.dry_run
            )
            
            if result['total_removed'] > 0:
                if args.dry_run:
                    print_info(f"Would remove {result['total_removed']} backup(s)")
                else:
                    print_success(f"Removed {result['total_removed']} backup(s)")
                
                # Show first few removed items
                for removed in result['removed'][:5]:
                    status = removed['status']
                    path = removed['backup_path']
                    if args.dry_run:
                        print(f"  Would remove: {path}")
                    else:
                        print(f"  Removed: {path}")
                
                if len(result['removed']) > 5:
                    print(f"  ... and {len(result['removed']) - 5} more")
            else:
                print_info("No backups matched the criteria")
            
            if result['total_errors'] > 0:
                print_error(f"Encountered {result['total_errors']} error(s)")
            
            return 0
        
        elif args.backup_action == 'diff':
            # Show differences
            if not args.backup_path:
                print_error("Backup path is required for diff")
                return 1
            
            print_info(f"Comparing backup with current file...\n")
            
            result = manager.diff_backup(
                args.backup_path,
                original_path=getattr(args, 'target', None),
                context_lines=getattr(args, 'context', 3)
            )
            
            if result['status'] == 'original_missing':
                print_warning(result['message'])
                return 0
            
            if not result['has_changes']:
                print_success("No differences found - files are identical")
                return 0
            
            print(f"{Colors.BOLD}Differences:{Colors.ENDC}\n")
            print(result['diff'])
            
            stats = result['stats']
            print(f"\n{Colors.OKCYAN}Summary:{Colors.ENDC}")
            print(f"  Backup lines:  {stats['backup_lines']}")
            print(f"  Current lines: {stats['current_lines']}")
            print(f"  Lines added:   {Colors.OKGREEN}+{stats['lines_added']}{Colors.ENDC}")
            print(f"  Lines removed: {Colors.FAIL}-{stats['lines_removed']}{Colors.ENDC}")
            
            return 0
        
        elif args.backup_action == 'info':
            # Show backup information
            if not args.backup_path:
                print_error("Backup path is required for info")
                return 1
            
            info = manager.get_backup_info(args.backup_path)
            
            print(f"{Colors.BOLD}Backup Information:{Colors.ENDC}\n")
            print(f"  Original path:  {info.get('original_path', 'unknown')}")
            print(f"  Backup path:    {info.get('backup_path', 'unknown')}")
            print(f"  Timestamp:      {info.get('timestamp', 'unknown')}")
            print(f"  Description:    {info.get('description', 'none')}")
            print(f"  Size:           {info.get('current_size_kb', 0)} KB")
            
            if info.get('age_days') is not None:
                print(f"  Age:            {info['age_days']} days ({info['age_hours']} hours)")
            
            print(f"\n{Colors.BOLD}Status:{Colors.ENDC}")
            backup_exists = "✓ exists" if info.get('exists') else "✗ missing"
            original_exists = "✓ exists" if info.get('original_exists') else "✗ missing"
            print(f"  Backup file:    {backup_exists}")
            print(f"  Original file:  {original_exists}")
            
            return 0
        
        elif args.backup_action == 'scan':
            # Scan and sync backup directory
            print_info("Scanning backup directory...\n")
            
            result = manager.scan_backup_directory()
            
            if result['status'] == 'no_backup_dir':
                print_warning(result['message'])
                return 0
            
            print_success(f"Backup directory scan complete")
            print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
            print(f"  Backups in filesystem: {result['total_fs_backups']}")
            print(f"  Backups in metadata:   {result['total_meta_backups']}")
            
            if result['orphaned_count'] > 0:
                print(f"\n{Colors.WARNING}Orphaned files (in filesystem, not in metadata):{Colors.ENDC}")
                for orphaned in result['orphaned_files'][:10]:
                    print(f"  • {orphaned}")
                if result['orphaned_count'] > 10:
                    print(f"  ... and {result['orphaned_count'] - 10} more")
            
            if result['missing_count'] > 0:
                print(f"\n{Colors.FAIL}Missing files (in metadata, not in filesystem):{Colors.ENDC}")
                for missing in result['missing_files'][:10]:
                    print(f"  • {missing}")
                if result['missing_count'] > 10:
                    print(f"  ... and {result['missing_count'] - 10} more")
            
            if result['orphaned_count'] == 0 and result['missing_count'] == 0:
                print_success("\n✓ All backups are properly tracked")
            
            return 0
        
        else:
            print_error(f"Unknown backup action: {args.backup_action}")
            return 1
        
    except FileNotFoundError as e:
        print_error(str(e))
        return 1
    except ValueError as e:
        print_error(str(e))
        return 1
    except ImportError as e:
        print_error(f"Failed to import backup manager: {e}")
        return 1
    except Exception as e:
        print_error(f"Error managing backups: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_compare(args):
    """Compare migration progress across different contexts."""
    print_header("Migration Comparison")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from comparison_tool import MigrationComparison
        
        comparator = MigrationComparison()
        
        if args.compare_mode == 'paths':
            print_info(f"Comparing paths: {args.path_a} vs {args.path_b}\n")
            result = comparator.compare_paths(
                args.path_a, args.path_b,
                args.label_a, args.label_b
            )
        
        elif args.compare_mode == 'branches':
            print_info(f"Comparing branches: {args.branch_a} vs {args.branch_b}\n")
            print_warning("This will temporarily switch git branches. Your working directory will be restored.")
            
            if not args.yes:
                confirm = input(f"{Colors.WARNING}Proceed with branch comparison? (y/N): {Colors.ENDC}")
                if confirm.lower() != 'y':
                    print_info("Comparison cancelled")
                    return 0
            
            result = comparator.compare_branches(
                args.branch_a, args.branch_b,
                args.scan_path
            )
        
        elif args.compare_mode == 'commits':
            print_info(f"Comparing commits: {args.commit_a} vs {args.commit_b}\n")
            print_warning("This will temporarily checkout commits. Your working directory will be restored.")
            
            if not args.yes:
                confirm = input(f"{Colors.WARNING}Proceed with commit comparison? (y/N): {Colors.ENDC}")
                if confirm.lower() != 'y':
                    print_info("Comparison cancelled")
                    return 0
            
            result = comparator.compare_commits(
                args.commit_a, args.commit_b,
                args.scan_path
            )
        
        else:
            print_error("Unknown comparison mode")
            return 1
        
        # Format and display results
        output = comparator.format_comparison(result, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print_success(f"\nComparison saved to: {args.output}")
        else:
            print(output)
        
        # Show actionable insights
        winner = result['winner']
        if winner['winner'] != 'tie' and args.format != 'json':
            print_info("\nRecommendations:")
            if winner['margin'] > 10:
                print(f"  • {winner['winner']} shows significantly better progress")
                print(f"  • Consider adopting strategies from {winner['winner']}")
            else:
                print(f"  • Both approaches are performing similarly")
                print(f"  • Review specific issue types for optimization opportunities")
        
        return 0
        
    except RuntimeError as e:
        print_error(f"Comparison failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Unexpected error during comparison: {e}")
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
            # Validate JSON output requirements
            if args.format == 'json' and not args.output:
                print_error("JSON format requires --output option")
                return 1
            
            # Collect and display current stats
            if args.format != 'json':
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
                if args.format != 'json':
                    print_success(f"Snapshot saved to: {snapshot_path}\n")
            
            # Output based on format
            if args.format == 'json':
                # Prepare JSON output
                output_data = {
                    'stats': stats,
                    'comparison': comparison,
                    'generated_at': datetime.datetime.now().isoformat()
                }
                
                # Write to file
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                
                print_success(f"Statistics exported to: {args.output}")
            else:
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


def command_interactive(args):
    """Run interactive fixer with manual review."""
    print_header("Interactive Python 2 to 3 Fixer")
    
    validate_path(args.path)
    
    print_info(f"Path: {args.path}")
    print_info(f"Context lines: {args.context}")
    print_info(f"Auto-backup: {'enabled' if not args.no_backup else 'disabled'}\n")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from interactive_fixer import InteractiveFixer
        
        fixer = InteractiveFixer(
            directory=args.path,
            context_lines=args.context,
            auto_backup=not args.no_backup
        )
        
        stats = fixer.run()
        
        if stats['accepted'] > 0:
            print_success(f"\nSuccessfully applied {stats['accepted']} fixes")
            return 0
        elif stats['total_fixes'] == 0:
            print_success("\nNo fixes needed - code is Python 3 compatible")
            return 0
        else:
            print_warning("\nNo fixes were applied")
            return 1
            
    except Exception as e:
        print_error(f"Error during interactive fixing: {e}")
        if hasattr(args, 'verbose') and args.verbose:
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


def command_git(args):
    """Handle git integration commands."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from git_integration import GitIntegration, GitIntegrationError
        
        git = GitIntegration(args.path)
        
        # Check if action is provided
        if not args.git_action:
            print_error("No git action specified")
            print_info("Available actions: status, init, branch, checkpoint, commit, log, rollback, diff, info")
            return 1
        
        # Git status
        if args.git_action == 'status':
            print_header("Git Status")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                print_info("Initialize with: ./py2to3 git init")
                return 1
            
            status = git.get_status()
            branch = git.get_current_branch()
            is_clean = git.is_clean()
            
            print_info(f"Current branch: {branch}")
            print_info(f"Working directory: {'clean' if is_clean else 'has changes'}\n")
            
            if not is_clean:
                if status['modified']:
                    print(f"{Colors.WARNING}Modified files:{Colors.ENDC}")
                    for f in status['modified']:
                        print(f"  {Colors.WARNING}M{Colors.ENDC} {f}")
                
                if status['added']:
                    print(f"\n{Colors.OKGREEN}Added files:{Colors.ENDC}")
                    for f in status['added']:
                        print(f"  {Colors.OKGREEN}A{Colors.ENDC} {f}")
                
                if status['deleted']:
                    print(f"\n{Colors.FAIL}Deleted files:{Colors.ENDC}")
                    for f in status['deleted']:
                        print(f"  {Colors.FAIL}D{Colors.ENDC} {f}")
                
                if status['untracked']:
                    print(f"\n{Colors.OKCYAN}Untracked files:{Colors.ENDC}")
                    for f in status['untracked']:
                        print(f"  {Colors.OKCYAN}?{Colors.ENDC} {f}")
            else:
                print_success("No changes to commit")
            
            return 0
        
        # Git init
        elif args.git_action == 'init':
            print_header("Initialize Git Repository")
            
            if git.is_git_repo():
                print_info("Already a git repository")
                return 0
            
            git.init_repo()
            print_success("Initialized git repository")
            return 0
        
        # Git branch
        elif args.git_action == 'branch':
            print_header("Create Migration Branch")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                return 1
            
            branch_name = git.create_migration_branch(args.name)
            print_success(f"Created and switched to branch: {branch_name}")
            return 0
        
        # Git checkpoint
        elif args.git_action == 'checkpoint':
            print_header("Create Migration Checkpoint")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                return 1
            
            if not args.message:
                print_error("Commit message is required")
                return 1
            
            try:
                commit_hash = git.create_checkpoint(args.message, args.tag)
                print_success(f"Created checkpoint: {commit_hash[:8]}")
                if args.tag:
                    print_info(f"Tagged as: {git.migration_tag_prefix}-{args.tag}")
                return 0
            except GitIntegrationError as e:
                print_error(str(e))
                return 1
        
        # Git commit (with migration stats)
        elif args.git_action == 'commit':
            print_header("Create Migration Commit")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                return 1
            
            # Load statistics if provided
            stats = {}
            if args.stats_file:
                if not os.path.exists(args.stats_file):
                    print_error(f"Statistics file not found: {args.stats_file}")
                    return 1
                
                with open(args.stats_file, 'r') as f:
                    stats = json.load(f)
            
            try:
                commit_hash = git.create_migration_commit(
                    args.phase,
                    stats=stats,
                    additional_info=args.message
                )
                print_success(f"Created migration commit: {commit_hash[:8]}")
                print_info(f"Phase: {args.phase}")
                return 0
            except GitIntegrationError as e:
                print_error(str(e))
                return 1
        
        # Git log
        elif args.git_action == 'log':
            print_header("Migration Commit History")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                return 1
            
            commits = git.get_migration_commits()
            
            if not commits:
                print_info("No migration commits found")
                return 0
            
            # Show first N commits
            for i, commit in enumerate(commits[:args.count], 1):
                print(f"{Colors.BOLD}{i}. {commit['hash'][:8]}{Colors.ENDC}")
                print(f"   {commit['message']}")
                print(f"   {Colors.OKCYAN}{commit['date']}{Colors.ENDC}\n")
            
            if len(commits) > args.count:
                print_info(f"Showing {args.count} of {len(commits)} migration commits")
            
            return 0
        
        # Git rollback
        elif args.git_action == 'rollback':
            print_header("Rollback Migration")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                return 1
            
            # If no commit specified, use last migration commit
            commit_hash = args.commit
            if not commit_hash:
                commits = git.get_migration_commits()
                if not commits:
                    print_error("No migration commits found")
                    return 1
                commit_hash = commits[0]['hash']
                print_info(f"Rolling back to last migration commit: {commit_hash[:8]}")
            
            # Confirm
            if not args.yes:
                reset_type = "HARD (discard all changes)" if args.hard else "MIXED (keep changes as unstaged)"
                response = input(f"{Colors.WARNING}Rollback to {commit_hash[:8]} ({reset_type})? [y/N]: {Colors.ENDC}")
                if response.lower() not in ['y', 'yes']:
                    print_info("Operation cancelled")
                    return 0
            
            try:
                git.rollback_to_commit(commit_hash, hard=args.hard)
                print_success(f"Rolled back to commit: {commit_hash[:8]}")
                if args.hard:
                    print_warning("All changes have been discarded")
                else:
                    print_info("Changes are preserved as unstaged")
                return 0
            except GitIntegrationError as e:
                print_error(str(e))
                return 1
        
        # Git diff
        elif args.git_action == 'diff':
            print_header("Git Diff")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                return 1
            
            diff = git.get_diff(args.commit1, args.commit2)
            
            if not diff:
                print_info("No differences found")
                return 0
            
            print(diff)
            return 0
        
        # Git info
        elif args.git_action == 'info':
            print_header("Repository Information")
            
            if not git.is_git_repo():
                print_error("Not a git repository")
                return 1
            
            info = git.get_repo_info()
            
            print(f"{Colors.BOLD}Repository:{Colors.ENDC}")
            print(f"  Branch:        {info['branch']}")
            print(f"  Status:        {'Clean' if info['is_clean'] else 'Modified'}")
            print(f"  Total commits: {info['commit_count']}")
            
            if info.get('remote_url'):
                print(f"  Remote:        {info['remote_url']}")
            
            if info.get('last_commit'):
                print(f"\n{Colors.BOLD}Last Commit:{Colors.ENDC}")
                print(f"  Hash:    {info['last_commit']['hash'][:8]}")
                print(f"  Message: {info['last_commit']['message']}")
                print(f"  Date:    {info['last_commit']['date']}")
            
            # Get migration commits count
            migration_commits = git.get_migration_commits()
            if migration_commits:
                print(f"\n{Colors.BOLD}Migration:{Colors.ENDC}")
                print(f"  Migration commits: {len(migration_commits)}")
                print(f"  Last migration:    {migration_commits[0]['message']}")
                print(f"  Migration date:    {migration_commits[0]['date']}")
            
            return 0
        
        else:
            print_error(f"Unknown git action: {args.git_action}")
            return 1
    
    except ImportError as e:
        print_error(f"Failed to import git integration module: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during git operation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_deps(args):
    """Analyze dependencies for Python 3 compatibility."""
    print_header("Python 3 Dependency Compatibility Analysis")
    
    validate_path(args.path)
    
    print_info(f"Analyzing dependencies in: {args.path}")
    print_info(f"Output format: {args.format}\n")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from dependency_analyzer import DependencyAnalyzer
        
        analyzer = DependencyAnalyzer(args.path)
        
        print_info("Scanning requirements.txt...")
        analyzer.scan_requirements_txt()
        
        print_info("Scanning setup.py...")
        analyzer.scan_setup_py()
        
        print_info("Scanning Python imports...")
        analyzer.scan_imports()
        
        print_info("Analyzing compatibility...\n")
        
        report = analyzer.generate_report(args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print_success(f"Report saved to: {args.output}")
        else:
            print(report)
        
        # Check if there are critical issues
        results = analyzer.analyze_compatibility()
        if results['incompatible'] or results['stdlib_renames']:
            print_warning("\nAction required: Some dependencies need attention!")
            return 1
        else:
            print_success("\nAll dependencies appear to be compatible!")
            return 0
        
    except ImportError as e:
        print_error(f"Failed to import dependency analyzer: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during dependency analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_test_gen(args):
    """Generate unit tests for migrated code."""
    print_header("Automated Test Generation")
    
    validate_path(args.path)
    
    print_info(f"Generating tests for: {args.path}")
    print_info(f"Output directory: {args.output}\n")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from test_generator import TestGenerator
        
        generator = TestGenerator(args.path, args.output)
        summary = generator.generate_tests(overwrite=args.overwrite)
        
        # Display summary
        print(f"{Colors.BOLD}Test Generation Summary{Colors.ENDC}")
        print("=" * 60)
        print(f"Files processed:      {summary['files_processed']}")
        print(f"Test files created:   {len(summary['test_files_created'])}")
        print(f"Tests generated:      {summary['tests_generated']}")
        print(f"  - Functions tested: {summary['functions_tested']}")
        print(f"  - Classes tested:   {summary['classes_tested']}")
        print(f"Skipped files:        {len(summary['skipped_files'])}")
        print()
        
        if summary['test_files_created']:
            print(f"{Colors.OKGREEN}Generated test files:{Colors.ENDC}")
            for test_file in summary['test_files_created']:
                print(f"  ✓ {test_file}")
            print()
        
        if args.verbose and summary['skipped_files']:
            print(f"{Colors.WARNING}Skipped files:{Colors.ENDC}")
            for skipped in summary['skipped_files']:
                print(f"  - {skipped}")
            print()
        
        if summary['test_files_created']:
            print_success(f"Successfully generated tests in {args.output}/")
            print()
            print(f"{Colors.BOLD}Next steps:{Colors.ENDC}")
            print("  1. Review generated tests and add specific assertions")
            print("  2. Provide appropriate test inputs and expected outputs")
            print("  3. Add edge cases and error handling tests")
            print(f"  4. Run tests: pytest {args.output}")
        else:
            print_warning("No tests were generated")
            print_info("Make sure the target path contains Python files with testable functions/classes")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import test generator: {e}")
        return 1
    except Exception as e:
        print_error(f"Error generating tests: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_risk(args):
    """Analyze migration risks for code review prioritization."""
    print_header("Migration Risk Analysis")
    
    validate_path(args.path)
    
    print_info(f"Analyzing path: {args.path}")
    print_info(f"Backup directory: {args.backup_dir}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from risk_analyzer import MigrationRiskAnalyzer
        
        analyzer = MigrationRiskAnalyzer(
            backup_dir=args.backup_dir,
            source_dir=args.path
        )
        
        print_info("Scanning for changes and analyzing risk patterns...")
        summary = analyzer.analyze_project(args.path)
        
        # Check for errors
        if 'error' in summary:
            print_error(summary['error'])
            return 1
        
        # Format output based on requested format
        if args.json:
            output = json.dumps(summary, indent=2)
        else:
            output = analyzer.format_report(summary, detailed=args.detailed)
        
        # Save or print
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print_success(f"Report saved to: {args.output}")
        else:
            print(output)
        
        # Show summary status
        high_risk_count = len(summary.get('high_risk_files', []))
        total_files = summary.get('total_files_analyzed', 0)
        
        if total_files == 0:
            print_warning("\n⚠️  No changes detected. Make sure backup directory contains file backups.")
            print_info("Run 'py2to3 fix' first to create backups before analyzing risks.")
            return 0
        
        if high_risk_count > 0:
            print_warning(f"\n⚠️  {high_risk_count} high-risk files require priority review")
            return 1
        else:
            print_success(f"\n✓ Risk analysis complete for {total_files} files")
            print_info("No high-risk changes detected - standard review process sufficient")
            return 0
            
    except ImportError as e:
        print_error(f"Could not import risk analyzer: {e}")
        return 1
    except Exception as e:
        print_error(f"Risk analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_plan(args):
    """Create a strategic migration plan for the codebase."""
    print_header("Migration Planning")
    
    validate_path(args.path)
    
    print_info(f"Analyzing codebase: {args.path}")
    print_info(f"Output format: {args.format}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from migration_planner import MigrationPlanner
        
        planner = MigrationPlanner(args.path)
        
        print_info("📊 Analyzing files and dependencies...")
        planner.analyze_codebase()
        
        print_info("📋 Creating phased migration plan...")
        planner.create_migration_plan()
        
        print()
        print_success(f"✓ Plan created: {len(planner.phases)} phases, ~{planner.total_estimated_hours:.1f} hours")
        print()
        
        # Export in requested format
        if args.format == "json":
            output_file = args.output or "migration_plan.json"
            planner.export_json(output_file)
        elif args.format == "markdown":
            output_file = args.output or "migration_plan.md"
            planner.export_markdown(output_file)
        else:
            text_output = planner.export_text(args.output)
            if not args.output:
                print(text_output)
        
        # Print quick summary
        if args.output:
            print()
            print_info("Quick Summary:")
            print(f"  📁 Total Files: {len(planner.files)}")
            print(f"  📊 Phases: {len(planner.phases)}")
            
            risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for f in planner.files.values():
                risk_counts[f.risk_level] += 1
            
            print(f"  🔴 High Risk: {risk_counts['HIGH']} files")
            print(f"  🟡 Medium Risk: {risk_counts['MEDIUM']} files")
            print(f"  🟢 Low Risk: {risk_counts['LOW']} files")
            print(f"  ⏱️  Estimated: {planner.total_estimated_hours:.1f} hours")
            print()
            print_info("💡 Tip: Start with Phase 1 files (minimal dependencies)")
            print_info("💡 Tip: Use './py2to3 fix <file>' to migrate individual files")
        
        return 0
        
    except ImportError as e:
        print_error(f"Could not import migration planner: {e}")
        return 1
    except Exception as e:
        print_error(f"Planning failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_quality(args):
    """Analyze code quality and complexity metrics."""
    print_header("Code Quality and Complexity Analysis")
    
    validate_path(args.path)
    
    print_info(f"Analyzing: {args.path}")
    if args.output:
        print_info(f"Output file: {args.output}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from code_quality import CodeQualityAnalyzer
        
        analyzer = CodeQualityAnalyzer()
        
        # Analyze path
        if os.path.isfile(args.path):
            result = analyzer.analyze_file(args.path)
            analyzer.metrics = [result]
            analyzer.summary = analyzer._calculate_summary([result])
        else:
            analyzer.analyze_directory(args.path)
        
        # Generate output
        if args.format == 'json':
            import json
            output = json.dumps(analyzer.export_json(), indent=2)
        else:
            output = analyzer.format_report(include_files=args.detailed)
        
        # Write or print output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print_success(f"Report saved to {args.output}")
        else:
            print(output)
        
        # Show summary message
        if analyzer.summary:
            avg_mi = analyzer.summary.get('avg_maintainability_index', 0)
            if avg_mi >= 70:
                print_success(f"Overall quality is good! (MI: {avg_mi:.2f}/100)")
            elif avg_mi >= 50:
                print_warning(f"Overall quality is moderate (MI: {avg_mi:.2f}/100)")
            else:
                print_warning(f"Overall quality needs improvement (MI: {avg_mi:.2f}/100)")
        
        return 0
        
    except ImportError as e:
        print_error(f"Could not import code quality analyzer: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    except Exception as e:
        print_error(f"Quality analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_bench(args):
    """Run performance benchmarks comparing Python 2 and Python 3."""
    print_header("Performance Benchmark")
    
    validate_path(args.path)
    
    print_info(f"Benchmarking: {args.path}")
    print_info(f"Iterations: {args.iterations}")
    print_info(f"Timeout: {args.timeout}s per file")
    if args.output:
        print_info(f"Output file: {args.output}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from performance_benchmark import PerformanceBenchmark
        
        # Create benchmark instance
        benchmark = PerformanceBenchmark(
            python2_cmd=args.python2,
            python3_cmd=args.python3
        )
        
        # Check environment
        print_info("Checking environment...")
        env_info = benchmark.check_environment()
        
        if env_info['python2_available']:
            print_success(f"Python 2: {env_info['python2_version']}")
        else:
            print_warning(f"Python 2 not found (command: {args.python2})")
        
        if env_info['python3_available']:
            print_success(f"Python 3: {env_info['python3_version']}")
        else:
            print_warning(f"Python 3 not found (command: {args.python3})")
        
        if not env_info['python2_available'] and not env_info['python3_available']:
            print_error("Neither Python 2 nor Python 3 found")
            print_info("Specify Python commands with --python2 and --python3 flags")
            return 1
        
        print()
        print_info("Running benchmarks... (this may take a while)")
        print()
        
        # Run benchmark
        if os.path.isfile(args.path):
            results = [benchmark.benchmark_file(args.path, args.iterations, args.timeout)]
        elif os.path.isdir(args.path):
            results = benchmark.benchmark_directory(args.path, args.iterations, args.timeout)
        else:
            print_error(f"Invalid path: {args.path}")
            return 1
        
        # Generate report
        report = benchmark.generate_report(results, args.format)
        
        # Write or print output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print_success(f"Benchmark report saved to {args.output}")
        else:
            print(report)
        
        # Show summary
        summary = benchmark._generate_summary(results)
        if summary['completed'] > 0 and summary['avg_speedup'] > 0:
            if summary['avg_speedup'] > 1.05:
                print_success(f"Python 3 is {summary['avg_speedup']:.2f}x faster on average!")
            elif summary['avg_speedup'] < 0.95:
                print_warning(f"Python 3 is {1/summary['avg_speedup']:.2f}x slower on average")
            else:
                print_info("Python 3 has similar performance (within 5%)")
        
        return 0
        
    except ImportError as e:
        print_error(f"Could not import performance benchmark tool: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    except Exception as e:
        print_error(f"Benchmark failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_watch(args):
    """Monitor files for changes and automatically check compatibility."""
    # Check if watchdog is available
    try:
        import watchdog
    except ImportError:
        print_error("Watch mode requires the 'watchdog' package")
        print_info("Install it with: pip install watchdog")
        return 1
    
    validate_path(args.path)
    
    print_info(f"Starting watch mode on: {args.path}")
    print_info(f"Mode: {args.mode}")
    print_info(f"Debounce: {args.debounce}s")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from watch_mode import WatchMode
        
        config = {
            'debounce_seconds': args.debounce
        }
        
        watch = WatchMode(args.path, mode=args.mode, config=config)
        watch.start()
        
        return 0
        
    except ImportError as e:
        print_error(f"Could not import watch mode: {e}")
        return 1
    except KeyboardInterrupt:
        print()
        print_info("Watch mode stopped by user")
        return 0
    except Exception as e:
        print_error(f"Watch mode failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_dashboard(args):
    """Generate interactive progress dashboard."""
    print_header("Progress Dashboard Generator")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from progress_dashboard import ProgressDashboard
        
        print_info("Generating interactive progress dashboard...\n")
        
        dashboard = ProgressDashboard(args.project_path)
        output_file = dashboard.generate_dashboard(args.output)
        
        print_success(f"Dashboard generated: {output_file}")
        print_info(f"Open in browser: file://{output_file}\n")
        
        print(f"{Colors.BOLD}Dashboard Features:{Colors.ENDC}")
        print(f"  📉 Burndown chart - Issues over time")
        print(f"  📈 Progress chart - Migration completion")
        print(f"  📊 Issue distribution - By type and severity")
        print(f"  ⚡ Velocity tracking - Progress rate analysis")
        print(f"  🎯 ETA prediction - Estimated completion date\n")
        
        print(f"{Colors.BOLD}Update Dashboard:{Colors.ENDC}")
        print(f"  1. Run fixes: {Colors.OKCYAN}py2to3 fix <path>{Colors.ENDC}")
        print(f"  2. Collect stats: {Colors.OKCYAN}py2to3 stats collect --save{Colors.ENDC}")
        print(f"  3. Refresh dashboard: {Colors.OKCYAN}py2to3 dashboard{Colors.ENDC}")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import dashboard generator: {e}")
        return 1
    except Exception as e:
        print_error(f"Error generating dashboard: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_docs(args):
    """Generate migration documentation in Markdown format."""
    print_header("Migration Documentation Generator")
    
    if hasattr(args, 'path') and args.path:
        validate_path(args.path)
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from doc_generator import MigrationDocGenerator
        
        print_info(f"Generating documentation for: {args.path or 'current directory'}")
        
        generator = MigrationDocGenerator(args.path or '.')
        
        # Set custom output directory if provided
        if args.output_dir:
            generator.docs_dir = Path(args.output_dir)
            generator.docs_dir.mkdir(exist_ok=True)
        
        print_info(f"Output directory: {generator.docs_dir}\n")
        
        # Generate documentation
        saved_paths = generator.generate_full_documentation(
            backup_dir=args.backup_dir
        )
        
        # Display success message
        print_success("Documentation generated successfully!\n")
        
        print(f"{Colors.BOLD}Generated Documents:{Colors.ENDC}")
        for doc_type, path in saved_paths.items():
            emoji = {
                'summary': '📊',
                'guide': '📘',
                'changelog': '📝',
                'best_practices': '✨',
                'index': '📖'
            }.get(doc_type, '📄')
            print(f"  {emoji} {doc_type.title()}: {Colors.OKCYAN}{path}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print(f"  1. Review the generated documentation")
        print(f"  2. Commit to version control: {Colors.OKCYAN}git add {generator.docs_dir}{Colors.ENDC}")
        print(f"  3. Share with your team")
        print(f"  4. Update as migration progresses")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import documentation generator: {e}")
        return 1
    except Exception as e:
        print_error(f"Error generating documentation: {e}")
        if hasattr(args, 'verbose') and args.verbose:
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
    
    # Preflight command
    parser_preflight = subparsers.add_parser(
        'preflight',
        help='Run pre-migration safety checks',
        description='Verify environment and project readiness before migration'
    )
    parser_preflight.add_argument('path', nargs='?', default='.', help='Project path to check (default: current directory)')
    parser_preflight.add_argument('-b', '--backup-dir', default='backup', help='Backup directory to validate (default: backup)')
    parser_preflight.add_argument('-v', '--verbose', action='store_true', help='Show detailed check information')
    parser_preflight.add_argument('--json', action='store_true', help='Output results as JSON')
    
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
    
    # Interactive command
    parser_interactive = subparsers.add_parser(
        'interactive',
        help='Review and approve fixes interactively',
        description='Review each proposed fix and decide whether to apply it'
    )
    parser_interactive.add_argument('path', help='Directory to analyze and fix')
    parser_interactive.add_argument('-c', '--context', type=int, default=3, 
                                   help='Number of context lines to show (default: 3)')
    parser_interactive.add_argument('--no-backup', action='store_true', 
                                   help='Disable automatic backups')
    
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
    parser_stats_collect.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='Output format (default: text)')
    parser_stats_collect.add_argument('-o', '--output', help='Output file for statistics (required for JSON format)')
    
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
    
    # Backup command
    parser_backup = subparsers.add_parser(
        'backup',
        help='Manage migration backups',
        description='Manage backups created during Python 2 to 3 migration'
    )
    parser_backup.add_argument('-b', '--backup-dir', default='backup', help='Backup directory (default: backup)')
    backup_subparsers = parser_backup.add_subparsers(dest='backup_action', help='Backup actions')
    
    # Backup list
    parser_backup_list = backup_subparsers.add_parser('list', help='List all available backups')
    parser_backup_list.add_argument('-p', '--pattern', help='Filter backups by pattern')
    
    # Backup restore
    parser_backup_restore = backup_subparsers.add_parser('restore', help='Restore files from backup')
    parser_backup_restore.add_argument('backup_path', nargs='?', help='Path to backup file')
    parser_backup_restore.add_argument('-t', '--target', help='Target path to restore to (defaults to original location)')
    parser_backup_restore.add_argument('-n', '--dry-run', action='store_true', help='Show what would be restored without actually restoring')
    parser_backup_restore.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    
    # Backup clean
    parser_backup_clean = backup_subparsers.add_parser('clean', help='Clean up old backups')
    parser_backup_clean.add_argument('-o', '--older-than', type=int, help='Remove backups older than N days')
    parser_backup_clean.add_argument('-p', '--pattern', help='Remove backups matching pattern')
    parser_backup_clean.add_argument('-a', '--all', action='store_true', help='Remove all backups')
    parser_backup_clean.add_argument('-n', '--dry-run', action='store_true', help='Show what would be removed without actually removing')
    parser_backup_clean.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    
    # Backup diff
    parser_backup_diff = backup_subparsers.add_parser('diff', help='Show differences between backup and current file')
    parser_backup_diff.add_argument('backup_path', nargs='?', help='Path to backup file')
    parser_backup_diff.add_argument('-t', '--target', help='Target file to compare with (defaults to original location)')
    parser_backup_diff.add_argument('-c', '--context', type=int, default=3, help='Number of context lines in diff (default: 3)')
    
    # Backup info
    parser_backup_info = backup_subparsers.add_parser('info', help='Show detailed information about a backup')
    parser_backup_info.add_argument('backup_path', nargs='?', help='Path to backup file')
    
    # Backup scan
    parser_backup_scan = backup_subparsers.add_parser('scan', help='Scan backup directory and check for inconsistencies')
    
    # Deps command
    parser_deps = subparsers.add_parser(
        'deps',
        help='Analyze dependencies for Python 3 compatibility',
        description='Scan and analyze project dependencies for Python 3 compatibility'
    )
    parser_deps.add_argument('path', nargs='?', default='.', help='Project path to analyze (default: current directory)')
    parser_deps.add_argument('-o', '--output', help='Save report to file (default: print to console)')
    parser_deps.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='Output format (default: text)')
    
    # Git command
    parser_git = subparsers.add_parser(
        'git',
        help='Git integration for migration tracking',
        description='Integrate migration workflow with git version control'
    )
    parser_git.add_argument('-p', '--path', default='.', help='Repository path (default: current directory)')
    git_subparsers = parser_git.add_subparsers(dest='git_action', help='Git actions')
    
    # Git status
    parser_git_status = git_subparsers.add_parser('status', help='Show git status of migration files')
    
    # Git init
    parser_git_init = git_subparsers.add_parser('init', help='Initialize git repository (if not already initialized)')
    
    # Git branch
    parser_git_branch = git_subparsers.add_parser('branch', help='Create a migration branch')
    parser_git_branch.add_argument('name', nargs='?', help='Branch name (default: auto-generated)')
    
    # Git checkpoint
    parser_git_checkpoint = git_subparsers.add_parser('checkpoint', help='Create a migration checkpoint (commit)')
    parser_git_checkpoint.add_argument('message', nargs='?', help='Commit message')
    parser_git_checkpoint.add_argument('-t', '--tag', help='Tag name for this checkpoint')
    
    # Git commit (alias for checkpoint with migration stats)
    parser_git_commit = git_subparsers.add_parser('commit', help='Create a migration commit with statistics')
    parser_git_commit.add_argument('phase', help='Migration phase (e.g., pre-migration, fixes-applied, verified)')
    parser_git_commit.add_argument('-s', '--stats-file', help='JSON file with migration statistics')
    parser_git_commit.add_argument('-m', '--message', help='Additional commit message')
    
    # Git log
    parser_git_log = git_subparsers.add_parser('log', help='Show migration commit history')
    parser_git_log.add_argument('-n', '--count', type=int, default=10, help='Number of commits to show (default: 10)')
    
    # Git rollback
    parser_git_rollback = git_subparsers.add_parser('rollback', help='Rollback to a previous migration state')
    parser_git_rollback.add_argument('commit', nargs='?', help='Commit hash to rollback to (default: last migration commit)')
    parser_git_rollback.add_argument('--hard', action='store_true', help='Discard all changes (hard reset)')
    parser_git_rollback.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    
    # Git diff
    parser_git_diff = git_subparsers.add_parser('diff', help='Show changes between commits')
    parser_git_diff.add_argument('commit1', nargs='?', default='HEAD', help='First commit (default: HEAD)')
    parser_git_diff.add_argument('commit2', nargs='?', help='Second commit (default: working directory)')
    
    # Git info
    parser_git_info = git_subparsers.add_parser('info', help='Show repository information')
    
    # Compare command
    parser_compare = subparsers.add_parser(
        'compare',
        help='Compare migration progress',
        description='Compare migration progress between branches, commits, or paths'
    )
    compare_subparsers = parser_compare.add_subparsers(dest='compare_mode', help='Comparison mode')
    
    # Compare paths
    parser_compare_paths = compare_subparsers.add_parser('paths', help='Compare two file system paths')
    parser_compare_paths.add_argument('path_a', help='First path to compare')
    parser_compare_paths.add_argument('path_b', help='Second path to compare')
    parser_compare_paths.add_argument('--label-a', default='Path A', help='Label for first path (default: Path A)')
    parser_compare_paths.add_argument('--label-b', default='Path B', help='Label for second path (default: Path B)')
    parser_compare_paths.add_argument('-o', '--output', help='Save comparison to file')
    parser_compare_paths.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='Output format (default: text)')
    parser_compare_paths.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompts')
    
    # Compare branches
    parser_compare_branches = compare_subparsers.add_parser('branches', help='Compare two git branches')
    parser_compare_branches.add_argument('branch_a', help='First branch to compare')
    parser_compare_branches.add_argument('branch_b', help='Second branch to compare')
    parser_compare_branches.add_argument('-s', '--scan-path', default='.', help='Path to scan in branches (default: current directory)')
    parser_compare_branches.add_argument('-o', '--output', help='Save comparison to file')
    parser_compare_branches.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='Output format (default: text)')
    parser_compare_branches.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompts')
    
    # Compare commits
    parser_compare_commits = compare_subparsers.add_parser('commits', help='Compare two git commits')
    parser_compare_commits.add_argument('commit_a', help='First commit hash/reference')
    parser_compare_commits.add_argument('commit_b', help='Second commit hash/reference')
    parser_compare_commits.add_argument('-s', '--scan-path', default='.', help='Path to scan in commits (default: current directory)')
    parser_compare_commits.add_argument('-o', '--output', help='Save comparison to file')
    parser_compare_commits.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='Output format (default: text)')
    parser_compare_commits.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompts')
    
    # Risk command
    parser_risk = subparsers.add_parser(
        'risk',
        help='Analyze migration risks for code review',
        description='Identify high-risk changes that require careful manual review after migration'
    )
    parser_risk.add_argument('path', nargs='?', default='src', help='Path to analyze (default: src)')
    parser_risk.add_argument('-b', '--backup-dir', default='backup', help='Backup directory path (default: backup)')
    parser_risk.add_argument('-o', '--output', help='Save report to file')
    parser_risk.add_argument('--json', action='store_true', help='Output in JSON format')
    parser_risk.add_argument('-d', '--detailed', action='store_true', help='Include detailed per-file analysis')
    
    # Test-gen command
    parser_test_gen = subparsers.add_parser(
        'test-gen',
        help='Generate unit tests for migrated code',
        description='Automatically generate unit tests to verify migration correctness'
    )
    parser_test_gen.add_argument('path', help='File or directory to generate tests for')
    parser_test_gen.add_argument('-o', '--output', default='generated_tests', 
                                 help='Output directory for generated tests (default: generated_tests)')
    parser_test_gen.add_argument('--overwrite', action='store_true', 
                                 help='Overwrite existing test files')
    
    # Plan command
    parser_plan = subparsers.add_parser(
        'plan',
        help='Create a strategic migration plan',
        description='Analyze codebase and create a phased migration plan based on dependencies'
    )
    parser_plan.add_argument('path', help='Directory to analyze')
    parser_plan.add_argument('-o', '--output', help='Output file (default: print to console)')
    parser_plan.add_argument('-f', '--format', choices=['text', 'json', 'markdown'],
                            default='text', help='Output format (default: text)')
    
    # Watch command
    parser_watch = subparsers.add_parser(
        'watch',
        help='Watch files and auto-check for compatibility',
        description='Monitor Python files for changes and automatically run compatibility checks'
    )
    parser_watch.add_argument('path', nargs='?', default='.',
                             help='Path to watch (default: current directory)')
    parser_watch.add_argument('-m', '--mode', choices=['check', 'stats', 'report'],
                             default='check', help='Watch mode (default: check)')
    parser_watch.add_argument('--debounce', type=float, default=1.0,
                             help='Debounce delay in seconds (default: 1.0)')
    
    # Quality command
    parser_quality = subparsers.add_parser(
        'quality',
        help='Analyze code quality and complexity',
        description='Analyze code quality metrics including complexity, maintainability, and code statistics'
    )
    parser_quality.add_argument('path', nargs='?', default='src',
                               help='File or directory to analyze (default: src)')
    parser_quality.add_argument('-o', '--output', help='Save report to file')
    parser_quality.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                               help='Output format (default: text)')
    parser_quality.add_argument('-d', '--detailed', action='store_true',
                               help='Include detailed per-file metrics in report')
    
    # Bench command
    parser_bench = subparsers.add_parser(
        'bench',
        help='Benchmark Python 2 vs Python 3 performance',
        description='Compare execution time and performance between Python 2 and Python 3 code'
    )
    parser_bench.add_argument('path', nargs='?', default='src',
                             help='File or directory to benchmark (default: src)')
    parser_bench.add_argument('-i', '--iterations', type=int, default=100,
                             help='Number of iterations per benchmark (default: 100)')
    parser_bench.add_argument('-t', '--timeout', type=int, default=30,
                             help='Timeout per file in seconds (default: 30)')
    parser_bench.add_argument('-o', '--output', help='Save report to file')
    parser_bench.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                             help='Output format (default: text)')
    parser_bench.add_argument('--python2', default='python2',
                             help='Python 2 command (default: python2)')
    parser_bench.add_argument('--python3', default='python3',
                             help='Python 3 command (default: python3)')
    
    # Docs command
    parser_docs = subparsers.add_parser(
        'docs',
        help='Generate migration documentation',
        description='Generate comprehensive Markdown documentation for the migration project'
    )
    parser_docs.add_argument('path', nargs='?', default='.',
                            help='Project path to document (default: current directory)')
    parser_docs.add_argument('-o', '--output-dir',
                            help='Output directory for documentation (default: .migration_docs)')
    parser_docs.add_argument('-b', '--backup-dir',
                            help='Backup directory path to include in changelog')
    
    # Dashboard command
    parser_dashboard = subparsers.add_parser(
        'dashboard',
        help='Generate interactive progress dashboard',
        description='Generate an interactive HTML dashboard with charts, trends, velocity, and ETA'
    )
    parser_dashboard.add_argument('-o', '--output', 
                                 default='migration_dashboard.html',
                                 help='Output HTML file (default: migration_dashboard.html)')
    parser_dashboard.add_argument('--project-path', 
                                 default='.',
                                 help='Project path (default: current directory)')
    
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
    elif args.command == 'preflight':
        return command_preflight(args)
    elif args.command == 'fix':
        return command_fix(args)
    elif args.command == 'interactive':
        return command_interactive(args)
    elif args.command == 'report':
        return command_report(args)
    elif args.command == 'stats':
        return command_stats(args)
    elif args.command == 'migrate':
        return command_migrate(args)
    elif args.command == 'config':
        return command_config(args)
    elif args.command == 'backup':
        return command_backup(args)
    elif args.command == 'deps':
        return command_deps(args)
    elif args.command == 'git':
        return command_git(args)
    elif args.command == 'compare':
        return command_compare(args)
    elif args.command == 'risk':
        return command_risk(args)
    elif args.command == 'test-gen':
        return command_test_gen(args)
    elif args.command == 'plan':
        return command_plan(args)
    elif args.command == 'watch':
        return command_watch(args)
    elif args.command == 'quality':
        return command_quality(args)
    elif args.command == 'bench':
        return command_bench(args)
    elif args.command == 'docs':
        return command_docs(args)
    elif args.command == 'dashboard':
        return command_dashboard(args)
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
