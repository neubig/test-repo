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


def command_recipe(args):
    """Manage migration recipes/templates."""
    print_header("Migration Recipe Manager")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from recipe_manager import RecipeManager
        
        recipe_mgr = RecipeManager(args.recipes_dir if hasattr(args, 'recipes_dir') else None)
        
        if args.recipe_action == 'list':
            # List all available recipes
            recipes = recipe_mgr.list_recipes()
            
            if not recipes:
                print_warning("No recipes found")
                return 0
            
            print_info(f"Found {len(recipes)} recipe(s):\n")
            
            for recipe in recipes:
                print(f"{Colors.BOLD}{Colors.OKGREEN}📋 {recipe.name}{Colors.ENDC}")
                print(f"   {recipe.description}")
                if recipe.tags:
                    print(f"   Tags: {', '.join(recipe.tags)}")
                print(f"   Author: {recipe.author}")
                print()
        
        elif args.recipe_action == 'show':
            # Show detailed information about a recipe
            if not args.name:
                print_error("Please specify a recipe name")
                return 1
            
            recipe = recipe_mgr.load_recipe(args.name)
            if not recipe:
                return 1
            
            print(f"{Colors.BOLD}{Colors.OKGREEN}📋 {recipe.name}{Colors.ENDC}")
            print(f"   {recipe.description}\n")
            
            if recipe.tags:
                print(f"{Colors.BOLD}Tags:{Colors.ENDC} {', '.join(recipe.tags)}")
            print(f"{Colors.BOLD}Author:{Colors.ENDC} {recipe.author}")
            print(f"{Colors.BOLD}Created:{Colors.ENDC} {recipe.created_at}\n")
            
            if recipe.notes:
                print(f"{Colors.BOLD}📝 Important Notes:{Colors.ENDC}")
                for i, note in enumerate(recipe.notes, 1):
                    print(f"   {i}. {note}")
                print()
            
            if recipe.fix_order:
                print(f"{Colors.BOLD}🔧 Recommended Fix Order:{Colors.ENDC}")
                for i, fix_type in enumerate(recipe.fix_order, 1):
                    print(f"   {i}. {fix_type}")
                print()
            
            if recipe.ignore_patterns:
                print(f"{Colors.BOLD}🚫 Ignore Patterns:{Colors.ENDC}")
                for pattern in recipe.ignore_patterns:
                    print(f"   - {pattern}")
                print()
            
            if recipe.config:
                print(f"{Colors.BOLD}⚙️  Configuration:{Colors.ENDC}")
                print(json.dumps(recipe.config, indent=2))
        
        elif args.recipe_action == 'apply':
            # Apply a recipe to the current project
            if not args.name:
                print_error("Please specify a recipe name")
                return 1
            
            return 0 if recipe_mgr.apply_recipe(args.name, args.target) else 1
        
        elif args.recipe_action == 'create':
            # Create a new recipe from current configuration
            if not args.name:
                print_error("Please specify a recipe name")
                return 1
            
            if not args.description:
                print_error("Please provide a description with --description")
                return 1
            
            return 0 if recipe_mgr.create_from_current(
                args.name, 
                args.description,
                args.config_file
            ) else 1
        
        elif args.recipe_action == 'export':
            # Export a recipe to a file
            if not args.name:
                print_error("Please specify a recipe name")
                return 1
            
            output_path = args.output or f"{args.name}.recipe.json"
            return 0 if recipe_mgr.export_recipe(args.name, output_path) else 1
        
        elif args.recipe_action == 'import':
            # Import a recipe from a file
            if not args.file:
                print_error("Please specify a recipe file to import")
                return 1
            
            return 0 if recipe_mgr.import_recipe(args.file, args.force) else 1
        
        elif args.recipe_action == 'delete':
            # Delete a recipe
            if not args.name:
                print_error("Please specify a recipe name to delete")
                return 1
            
            return 0 if recipe_mgr.delete_recipe(args.name) else 1
        
        else:
            print_error(f"Unknown recipe action: {args.recipe_action}")
            return 1
            
    except Exception as e:
        print_error(f"Recipe management failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


def command_state(args):
    """Manage migration state tracking for individual files."""
    print_header("Migration State Tracker")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from migration_state import MigrationStateTracker, MigrationState
        
        project_root = args.project_root if hasattr(args, 'project_root') and args.project_root else '.'
        tracker = MigrationStateTracker(project_root)
        
        if args.state_action == 'init':
            # Initialize state tracking
            scan_dir = args.scan_dir if hasattr(args, 'scan_dir') and args.scan_dir else None
            result = tracker.initialize(
                scan_directory=scan_dir,
                force=args.force if hasattr(args, 'force') else False
            )
            
            if result['status'] == 'already_initialized':
                print_warning(f"State tracking already initialized")
                print_info(f"State file: {result['state_file']}")
                print_info(f"Tracking {result['file_count']} files")
                print_info("Use --force to reinitialize")
            else:
                print_success(f"Initialized migration state tracking")
                print_info(f"State file: {result['state_file']}")
                print_info(f"Found {result['files_found']} Python files")
                print_info(f"Added {result['files_added']} new files to tracking")
                print_info(f"Total tracked files: {result['total_tracked']}")
            
            return 0
        
        elif args.state_action == 'list':
            # List files with optional filtering
            state_filter = None
            if hasattr(args, 'filter_state') and args.filter_state:
                try:
                    state_filter = MigrationState(args.filter_state)
                except ValueError:
                    print_error(f"Invalid state: {args.filter_state}")
                    print_info(f"Valid states: {', '.join([s.value for s in MigrationState])}")
                    return 1
            
            files = tracker.list_files(
                state=state_filter,
                locked=args.locked if hasattr(args, 'locked') else None,
                owner=args.owner if hasattr(args, 'owner') else None
            )
            
            if not files:
                print_warning("No files found matching criteria")
                return 0
            
            print_info(f"Found {len(files)} file(s):\n")
            
            for file_data in files:
                # Color code based on state
                state = file_data['state']
                if state == MigrationState.DONE.value:
                    color = Colors.OKGREEN
                elif state == MigrationState.PENDING.value:
                    color = Colors.WARNING
                elif state in [MigrationState.IN_PROGRESS.value, MigrationState.MIGRATED.value]:
                    color = Colors.OKCYAN
                else:
                    color = Colors.OKBLUE
                
                lock_indicator = "🔒" if file_data.get('locked') else "  "
                print(f"{lock_indicator} {color}{state:12}{Colors.ENDC} {file_data['path']}", end='')
                if file_data.get('locked'):
                    print(f" (locked by {file_data.get('owner', 'unknown')})", end='')
                print()
            
            return 0
        
        elif args.state_action == 'set':
            # Set state for a file
            if not args.file:
                print_error("Please specify a file path")
                return 1
            
            if not args.state:
                print_error("Please specify a state")
                return 1
            
            try:
                new_state = MigrationState(args.state)
            except ValueError:
                print_error(f"Invalid state: {args.state}")
                print_info(f"Valid states: {', '.join([s.value for s in MigrationState])}")
                return 1
            
            try:
                tracker.set_state(
                    args.file, 
                    new_state,
                    notes=args.notes if hasattr(args, 'notes') else None,
                    user=args.user if hasattr(args, 'user') else None
                )
                print_success(f"Set {args.file} to state: {new_state.value}")
                return 0
            except ValueError as e:
                print_error(str(e))
                return 1
        
        elif args.state_action == 'lock':
            # Lock a file
            if not args.file:
                print_error("Please specify a file path")
                return 1
            
            try:
                tracker.lock_file(
                    args.file,
                    owner=args.owner if hasattr(args, 'owner') else None
                )
                print_success(f"Locked file: {args.file}")
                return 0
            except ValueError as e:
                print_error(str(e))
                return 1
        
        elif args.state_action == 'unlock':
            # Unlock a file
            if not args.file:
                print_error("Please specify a file path")
                return 1
            
            try:
                tracker.unlock_file(
                    args.file,
                    owner=args.owner if hasattr(args, 'owner') else None,
                    force=args.force if hasattr(args, 'force') else False
                )
                print_success(f"Unlocked file: {args.file}")
                return 0
            except ValueError as e:
                print_error(str(e))
                return 1
        
        elif args.state_action == 'stats':
            # Show statistics
            stats = tracker.get_statistics()
            
            print(f"{Colors.BOLD}Migration State Statistics{Colors.ENDC}\n")
            
            print(f"Total Files: {stats['total_files']}")
            print(f"Completion: {stats['completion_percentage']:.1f}%\n")
            
            print(f"{Colors.BOLD}By State:{Colors.ENDC}")
            for state in MigrationState:
                count = stats['by_state'].get(state.value, 0)
                if count > 0:
                    percentage = (count / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
                    print(f"  {state.value:12} : {count:4} ({percentage:.1f}%)")
            
            print(f"\n{Colors.BOLD}Activity:{Colors.ENDC}")
            print(f"  In Progress  : {stats['in_progress_files']}")
            print(f"  Locked Files : {stats['locked_files']}")
            
            return 0
        
        elif args.state_action == 'reset':
            # Reset a file to pending
            if not args.file:
                print_error("Please specify a file path")
                return 1
            
            if tracker.reset_file(args.file):
                print_success(f"Reset {args.file} to pending state")
                return 0
            else:
                print_error(f"File not found in state tracking: {args.file}")
                return 1
        
        elif args.state_action == 'export':
            # Export state
            output_file = args.output if hasattr(args, 'output') else None
            result = tracker.export_state(output_file)
            
            if output_file:
                print_success(f"Exported state to: {output_file}")
            else:
                print(json.dumps(result, indent=2))
            
            return 0
        
        elif args.state_action == 'import':
            # Import state
            if not args.file:
                print_error("Please specify a file to import from")
                return 1
            
            result = tracker.import_state(
                args.file,
                merge=args.merge if hasattr(args, 'merge') else False
            )
            
            print_success(f"Imported state: {result['status']}")
            if 'files_imported' in result:
                print_info(f"Files imported: {result['files_imported']}")
            if 'files_updated' in result:
                print_info(f"Files updated: {result['files_updated']}")
            
            return 0
        
        else:
            print_error(f"Unknown state action: {args.state_action}")
            return 1
            
    except Exception as e:
        print_error(f"State tracking failed: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


def command_journal(args):
    """Manage migration journal entries."""
    print_header("Migration Journal")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from migration_journal import MigrationJournal, format_entry_for_display
        
        journal_path = args.journal_path if hasattr(args, 'journal_path') and args.journal_path else '.migration_journal.json'
        journal = MigrationJournal(journal_path)
        
        if not hasattr(args, 'journal_action') or not args.journal_action:
            print_error("Please specify a journal action (add, list, show, stats, export, import, delete)")
            print_info("Use 'py2to3 journal --help' for more information")
            return 1
        
        if args.journal_action == 'add':
            # Add a new entry
            entry = journal.add_entry(
                content=args.content,
                tags=args.tags if hasattr(args, 'tags') and args.tags else None,
                category=args.category if hasattr(args, 'category') else 'general',
                related_files=args.files if hasattr(args, 'files') and args.files else None,
                author=args.author if hasattr(args, 'author') and args.author else None
            )
            print_success(f"Added journal entry: {entry.id}")
            if entry.tags:
                print_info(f"Tags: {', '.join(entry.tags)}")
            if entry.related_files:
                print_info(f"Related files: {', '.join(entry.related_files)}")
            return 0
        
        elif args.journal_action == 'list':
            # List entries with optional filtering
            entries = journal.get_entries(
                search_term=args.search if hasattr(args, 'search') and args.search else None,
                tags=args.tags if hasattr(args, 'tags') and args.tags else None,
                category=args.category if hasattr(args, 'category') and args.category else None,
                author=args.author if hasattr(args, 'author') and args.author else None,
                files=args.files if hasattr(args, 'files') and args.files else None,
                limit=args.limit if hasattr(args, 'limit') and args.limit else None
            )
            
            if not entries:
                print_warning("No entries found matching your criteria")
                return 0
            
            print_info(f"Found {len(entries)} entries:\n")
            for entry in entries:
                print(format_entry_for_display(entry, color=not args.no_color))
                print("-" * 80)
            
            return 0
        
        elif args.journal_action == 'show':
            # Show a specific entry
            entry = journal.get_entry_by_id(args.entry_id)
            if not entry:
                print_error(f"Entry not found: {args.entry_id}")
                return 1
            
            print(format_entry_for_display(entry, color=not args.no_color))
            return 0
        
        elif args.journal_action == 'stats':
            # Show statistics
            stats = journal.get_statistics()
            
            print_info(f"Total Entries: {stats['total_entries']}")
            
            if stats['by_category']:
                print("\nEntries by Category:")
                for category, count in sorted(stats['by_category'].items()):
                    print(f"  {category:12} {count:3} entries")
            
            if stats['by_author']:
                print("\nEntries by Author:")
                for author, count in sorted(stats['by_author'].items()):
                    print(f"  {author:20} {count:3} entries")
            
            if stats['unique_tags']:
                print(f"\nUnique Tags: {len(stats['unique_tags'])}")
                tag_cloud = journal.get_tag_cloud()
                top_tags = list(tag_cloud.items())[:15]
                if top_tags:
                    print("  Top tags:")
                    for tag, count in top_tags:
                        print(f"    {tag:20} {count:3} times")
            
            if stats['related_files']:
                print(f"\nRelated Files: {len(stats['related_files'])}")
            
            if stats['date_range']:
                print(f"\nDate Range:")
                print(f"  First: {stats['date_range']['first']}")
                print(f"  Last:  {stats['date_range']['last']}")
            
            return 0
        
        elif args.journal_action == 'export':
            # Export entries
            filters = {}
            if hasattr(args, 'category') and args.category:
                filters['category'] = args.category
            if hasattr(args, 'tags') and args.tags:
                filters['tags'] = args.tags
            
            if args.format == 'markdown':
                journal.export_markdown(args.output, filters)
            else:
                journal.export_json(args.output, filters)
            
            print_success(f"Exported journal to: {args.output}")
            return 0
        
        elif args.journal_action == 'import':
            # Import entries
            count = journal.import_entries(args.input)
            print_success(f"Imported {count} entries from: {args.input}")
            return 0
        
        elif args.journal_action == 'delete':
            # Delete an entry
            entry = journal.get_entry_by_id(args.entry_id)
            if not entry:
                print_error(f"Entry not found: {args.entry_id}")
                return 1
            
            # Show entry before deletion
            print_info("Entry to delete:")
            print(format_entry_for_display(entry, color=not args.no_color))
            
            # Confirm deletion
            if not (hasattr(args, 'confirm') and args.confirm):
                response = input("\nAre you sure you want to delete this entry? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print_info("Deletion cancelled")
                    return 0
            
            if journal.delete_entry(args.entry_id):
                print_success(f"Deleted entry: {args.entry_id}")
                return 0
            else:
                print_error(f"Failed to delete entry: {args.entry_id}")
                return 1
        
        else:
            print_error(f"Unknown journal action: {args.journal_action}")
            return 1
    
    except Exception as e:
        print_error(f"Journal operation failed: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


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


def command_graph(args):
    """Generate visual dependency graph."""
    print_header("Dependency Graph Generation")
    
    validate_path(args.path)
    
    if not os.path.isdir(args.path):
        print_error("Graph generation requires a directory path")
        return 1
    
    print_info(f"Analyzing codebase: {args.path}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from dependency_graph import DependencyGraphGenerator
        
        generator = DependencyGraphGenerator(args.path)
        generator.analyze()
        
        if args.summary:
            print()
            print(generator.generate_summary())
        else:
            print()
            generator.generate_html(args.output)
            print()
            print_success("Dependency graph generated successfully!")
            print()
            print_info("💡 Tips:")
            print_info("  • Open the graph in your web browser")
            print_info("  • Drag nodes to rearrange the layout")
            print_info("  • Hover over nodes to see details")
            print_info("  • Scroll to zoom in/out")
            print_info("  • Colors indicate risk levels (red=high, yellow=medium, green=low)")
            print()
            print_info("💡 Use the graph to:")
            print_info("  • Understand module relationships")
            print_info("  • Identify which modules to migrate first")
            print_info("  • Spot circular dependencies")
            print_info("  • Present migration strategy to your team")
        
        return 0
    
    except ImportError as e:
        print_error(f"Could not import dependency graph generator: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except Exception as e:
        print_error(f"Graph generation failed: {e}")
        if hasattr(args, 'verbose') and args.verbose:
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


def command_health(args):
    """Monitor migration health and generate health report."""
    print_header("Migration Health Monitor")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from health_monitor import MigrationHealthMonitor, format_health_report
        
        path = args.path if hasattr(args, 'path') else '.'
        
        print_info(f"Analyzing migration health for: {path}\n")
        
        # Create monitor and analyze
        monitor = MigrationHealthMonitor(path)
        report = monitor.analyze(save_history=not args.no_history)
        
        # Print report
        print(format_health_report(report, verbose=args.verbose))
        
        # Show trend analysis if requested
        if args.trend:
            trend = monitor.get_trend_analysis(days=args.trend)
            if trend['available']:
                print(f"📊 Trend Analysis (Last {trend['days']} days):")
                print(f"   Measurements: {trend['measurements']}")
                print(f"   Average Score: {trend['average_score']}/100")
                print(f"   Range: {trend['min_score']}-{trend['max_score']}")
                print(f"   Change: {trend['improvement']:+.1f} points")
                print(f"   Trend: {trend['trend'].upper()}")
                print()
            else:
                print(f"⚠️  {trend['message']}\n")
        
        # Save JSON if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✓ JSON report saved to: {args.output}\n")
        
        # Show quick tips
        if report['overall_score'] < 70:
            print(f"{Colors.BOLD}Quick Start:{Colors.ENDC}")
            print(f"  1. Review recommendations above")
            print(f"  2. Run suggested commands to improve health")
            print(f"  3. Re-run health check: {Colors.OKCYAN}py2to3 health{Colors.ENDC}")
            print(f"  4. Track progress: {Colors.OKCYAN}py2to3 health --trend 7{Colors.ENDC}")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import health monitor: {e}")
        return 1
    except Exception as e:
        print_error(f"Error analyzing health: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_lint(args):
    """Run Python linters on migrated code."""
    print_header("Linting Integration")
    
    if hasattr(args, 'target') and args.target and args.target != '.':
        validate_path(args.target)
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from lint_integration import LintingIntegration
        
        print_info(f"Running linters on: {args.target}\n")
        
        # Create linter instance
        linter = LintingIntegration()
        
        # Run linters
        results = linter.run_all_linters(
            target=args.target,
            enabled_linters=args.linters
        )
        
        # Display results
        print()
        report = linter.generate_report(format=args.format)
        print(report)
        
        # Save to file if requested
        if args.output:
            linter.save_report(args.output, format=args.format)
            print_success(f"\nReport saved to: {args.output}")
        
        # Return error code if issues found (for CI/CD)
        total_issues = results['summary']['total_issues']
        if total_issues > 0:
            print_warning(f"\n⚠ Found {total_issues} issues")
            return 1
        else:
            print_success("\n✓ No issues found!")
            return 0
        
    except ImportError as e:
        print_error(f"Failed to import linting integration: {e}")
        return 1
    except Exception as e:
        print_error(f"Error running linters: {e}")
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


def command_status(args):
    """Show quick status summary of migration progress."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from status_reporter import MigrationStatusReporter
        
        path = args.path if hasattr(args, 'path') else '.'
        stats_dir = args.stats_dir if hasattr(args, 'stats_dir') else '.migration_stats'
        
        reporter = MigrationStatusReporter(path, stats_dir)
        
        if args.json:
            # Export as JSON
            output = reporter.export_json(args.output if hasattr(args, 'output') else None)
            if hasattr(args, 'output') and args.output:
                print_success(f"Status report exported to: {args.output}")
            else:
                print(output)
        else:
            # Print colorful terminal report
            reporter.print_status(color=not args.no_color)
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import status reporter: {e}")
        return 1
    except Exception as e:
        print_error(f"Error generating status report: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_search(args):
    """Search for specific Python 2 patterns in codebase."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from pattern_search import PatternSearcher
        
        # List patterns if requested
        if args.list_patterns:
            print_header("Available Python 2 Patterns")
            print(f"\n{Colors.BOLD}Pattern Name{' ' * 8}Description{' ' * 30}Example{Colors.ENDC}\n")
            print(f"{Colors.BOLD}{'-' * 100}{Colors.ENDC}")
            
            for name, description, example in PatternSearcher.list_patterns():
                print(f"{Colors.OKCYAN}{name:20}{Colors.ENDC} {description:40} {Colors.WARNING}{example}{Colors.ENDC}")
            
            print(f"\n{Colors.BOLD}Usage:{Colors.ENDC}")
            print(f"  py2to3 search <path> -p <pattern_name>")
            print(f"  py2to3 search <path>                    # Search all patterns")
            print(f"  py2to3 search <path> -p print_statement xrange  # Search specific patterns\n")
            return 0
        
        # Create searcher
        path = args.path if hasattr(args, 'path') and args.path else '.'
        validate_path(path)
        
        print_header("Python 2 Pattern Search")
        print_info(f"Searching path: {path}")
        
        if hasattr(args, 'patterns') and args.patterns:
            print_info(f"Patterns: {', '.join(args.patterns)}\n")
        else:
            print_info("Patterns: all\n")
        
        searcher = PatternSearcher(path, context_lines=args.context)
        
        # Run search
        results = searcher.search(patterns=args.patterns if hasattr(args, 'patterns') else None)
        
        # Output results
        if args.json or args.output:
            json_output = searcher.export_json(args.output if args.output else None)
            if args.output:
                print_success(f"Results exported to: {args.output}")
            else:
                print(json_output)
        else:
            output = searcher.format_results_text(colorize=not args.no_color)
            print(output)
        
        summary = searcher.get_summary()
        
        if summary['total_matches'] > 0:
            print_warning(f"Found {summary['total_matches']} Python 2 pattern(s) to address")
            return 1  # Non-zero exit for CI/CD integration
        else:
            print_success("No Python 2 patterns found!")
            return 0
        
    except ImportError as e:
        print_error(f"Failed to import pattern searcher: {e}")
        return 1
    except ValueError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error searching patterns: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_security(args):
    """Audit code for security vulnerabilities."""
    print_header("Security Audit")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from security_auditor import SecurityAuditor
        
        path = args.path if hasattr(args, 'path') and args.path else '.'
        validate_path(path)
        
        print_info(f"Auditing path: {path}")
        if args.exclude:
            print_info(f"Excluding: {', '.join(args.exclude)}")
        print()
        
        # Create auditor
        auditor = SecurityAuditor(verbose=args.verbose if hasattr(args, 'verbose') else False)
        
        # Run audit
        from pathlib import Path
        if Path(path).is_file():
            issues = auditor.audit_file(path)
            auditor.issues = issues
        else:
            auditor.audit_directory(path, exclude_patterns=args.exclude)
        
        # Generate report
        print_info("Generating security report...\n")
        report = auditor.generate_report(args.format)
        
        # Display report
        if args.format == 'text':
            print(report)
        elif args.format == 'json' and not args.output:
            print(report)
        
        # Save to file if requested
        if args.output:
            auditor.save_report(args.output, args.format)
            print_success(f"Report saved to: {args.output}")
        
        # Summary
        total_issues = len(auditor.issues)
        critical_high = (auditor.stats.get('severity_CRITICAL', 0) + 
                        auditor.stats.get('severity_HIGH', 0))
        
        print()
        if total_issues == 0:
            print_success("✓ No security issues found!")
            return 0
        elif critical_high > 0:
            print_error(f"⚠ Found {critical_high} CRITICAL/HIGH severity security issues!")
            if args.fail_on_high:
                return 1
        else:
            print_warning(f"Found {total_issues} security issues (no critical/high)")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import security auditor: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during security audit: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_venv(args):
    """Manage virtual environments for Python 3 testing."""
    print_header("Virtual Environment Manager")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from venv_manager import VirtualEnvironmentManager
        
        manager = VirtualEnvironmentManager()
        
        # Handle subcommands
        if args.venv_action == 'create':
            print_info(f"Creating virtual environment '{args.name}'...")
            if args.python:
                print_info(f"Using Python {args.python}")
            
            success = manager.create(
                args.name,
                python_version=args.python,
                system_site_packages=args.system_site_packages
            )
            
            if success:
                manager.print_activation_command(args.name)
                return 0
            return 1
            
        elif args.venv_action == 'list':
            envs = manager.list_environments()
            
            if not envs:
                print_info("No virtual environments found")
                print_info(f"Create one with: py2to3 venv create <name>")
                return 0
            
            print(f"\n{Colors.BOLD}Virtual Environments:{Colors.ENDC}\n")
            for env in envs:
                status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if env["exists"] else f"{Colors.FAIL}✗{Colors.ENDC}"
                print(f"  {status} {Colors.BOLD}{env['name']}{Colors.ENDC}")
                print(f"      Path: {env['path']}")
                print(f"      Python: {env['python_version']}")
                print(f"      Packages: {env['package_count']}")
                print()
            
            return 0
            
        elif args.venv_action == 'remove':
            success = manager.remove(args.name, args.force)
            return 0 if success else 1
            
        elif args.venv_action == 'install':
            if args.requirements:
                success = manager.install_requirements(args.name, args.requirements)
            elif args.package:
                success = manager.install_package(args.name, args.package)
            else:
                print_error("Specify --requirements or --package")
                return 1
            
            return 0 if success else 1
            
        elif args.venv_action == 'run':
            success = manager.run_command(args.name, args.command)
            return 0 if success else 1
            
        elif args.venv_action == 'test':
            success = manager.run_tests(args.name, args.test_path)
            return 0 if success else 1
            
        elif args.venv_action == 'info':
            info = manager.get_info(args.name)
            
            if not info:
                print_error(f"Virtual environment '{args.name}' not found")
                return 1
            
            exists_text = f"{Colors.OKGREEN}Yes{Colors.ENDC}" if info['exists'] else f"{Colors.FAIL}No{Colors.ENDC}"
            
            print(f"\n{Colors.BOLD}Virtual Environment: {args.name}{Colors.ENDC}\n")
            print(f"  Path: {info['path']}")
            print(f"  Exists: {exists_text}")
            print(f"  Created: {info.get('created', 'Unknown')}")
            print(f"  Python: {info.get('python_version', 'Unknown')}")
            print(f"  System site-packages: {info.get('system_site_packages', False)}")
            print(f"  Packages installed: {len(info.get('packages_installed', []))}")
            
            if info.get('packages_installed'):
                print(f"\n  {Colors.BOLD}Installed packages:{Colors.ENDC}")
                for pkg in info['packages_installed'][:20]:
                    print(f"    - {pkg}")
                if len(info['packages_installed']) > 20:
                    print(f"    ... and {len(info['packages_installed']) - 20} more")
            
            print()
            manager.print_activation_command(args.name)
            
            return 0
            
        elif args.venv_action == 'activate':
            manager.print_activation_command(args.name)
            return 0
            
        else:
            print_error("No action specified")
            return 1
            
    except ImportError as e:
        print_error(f"Failed to import virtual environment manager: {e}")
        return 1
    except Exception as e:
        print_error(f"Error managing virtual environment: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_imports(args):
    """Optimize Python imports after migration."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from import_optimizer import ImportOptimizer
        
        print_header("Import Optimizer")
        
        path = args.path
        
        if not os.path.exists(path):
            print_error(f"Path does not exist: {path}")
            return 1
        
        optimizer = ImportOptimizer()
        
        if args.fix:
            print_info(f"{'Analyzing and optimizing' if args.fix else 'Analyzing'} imports in: {path}\n")
            
            if os.path.isfile(path):
                success = optimizer.optimize_file(path, backup=not args.no_backup)
                if success:
                    print_success(f"Optimized: {path}")
                    analysis = optimizer.analyze_file(path)
                    print_info(f"Applied {len(analysis['issues'])} optimization(s)")
                else:
                    print_info(f"No optimization needed: {path}")
            else:
                # Analyze first to show what will be done
                results = optimizer.analyze_directory(path, recursive=args.recursive)
                
                if not results:
                    print_success("No import issues found!")
                    return 0
                
                print_info(f"Found issues in {len(results)} file(s)\n")
                
                # Optimize files
                for result in results:
                    if 'error' not in result:
                        success = optimizer.optimize_file(
                            result['filepath'],
                            backup=not args.no_backup
                        )
                        if success:
                            print_success(f"Optimized: {result['filepath']}")
                
                print()
                print_info(f"Unused imports removed: {optimizer.stats['unused_imports']}")
                print_info(f"Duplicate imports removed: {optimizer.stats['duplicate_imports']}")
                print_info(f"Imports sorted: {optimizer.stats['unsorted_imports']}")
                print_success(f"Total optimizations applied: {optimizer.stats['total_optimizations']}")
            
            return 0
        
        else:
            # Analysis mode only
            print_info(f"Analyzing imports in: {path}\n")
            
            if os.path.isfile(path):
                results = [optimizer.analyze_file(path)]
            else:
                results = optimizer.analyze_directory(path, recursive=args.recursive)
            
            # Generate report
            optimizer.generate_report(results, args.output)
            
            if optimizer.stats['total_optimizations'] > 0:
                print()
                print_warning(f"Found {optimizer.stats['total_optimizations']} optimization opportunity/opportunities")
                print_info("Run with --fix to apply optimizations")
                return 1  # Non-zero for CI/CD
            else:
                print_success("All imports are well-organized!")
                return 0
    
    except ImportError as e:
        print_error(f"Failed to import optimizer: {e}")
        return 1
    except Exception as e:
        print_error(f"Error optimizing imports: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_modernize(args):
    """Modernize Python 3 code to use modern idioms and features."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from code_modernizer import CodeModernizer
        
        print_header("Code Modernizer")
        
        path = args.path
        
        if not os.path.exists(path):
            print_error(f"Path does not exist: {path}")
            return 1
        
        modernizer = CodeModernizer()
        
        # Analyze the code
        print_info(f"Analyzing: {path}\n")
        
        if os.path.isdir(path):
            modernizer.analyze_directory(path, recursive=not args.no_recursive)
        else:
            suggestions = modernizer.analyze_file(path)
            modernizer.suggestions.extend(suggestions)
            # Update stats for single file analysis
            for suggestion in suggestions:
                modernizer.stats[suggestion.category] = modernizer.stats.get(suggestion.category, 0) + 1
        
        # Filter by categories if specified
        if args.categories:
            modernizer.suggestions = [s for s in modernizer.suggestions if s.category in args.categories]
            # Recalculate stats after filtering
            modernizer.stats = {}
            for suggestion in modernizer.suggestions:
                modernizer.stats[suggestion.category] = modernizer.stats.get(suggestion.category, 0) + 1
        
        if not modernizer.suggestions:
            print_success("Code is already modern! No suggestions found.")
            return 0
        
        # Generate and display report
        if args.format == 'json':
            report = modernizer.generate_report(args.output, format='json')
            if not args.output:
                print(report)
        else:
            report = modernizer.generate_report(args.output, format='text')
            if not args.output:
                print(report)
        
        # Show summary
        print()
        print_success(f"Found {len(modernizer.suggestions)} modernization opportunity/opportunities")
        
        # Show category breakdown
        print()
        print_info("Suggestions by category:")
        for category, count in sorted(modernizer.stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {category:20s}: {count:3d}")
        
        print()
        print_info("💡 These suggestions can help make your code more:")
        print("  • Readable and concise (f-strings, comprehensions)")
        print("  • Type-safe (type hints)")
        print("  • Modern and idiomatic (pathlib, dataclasses)")
        print("  • Maintainable (context managers)")
        
        if args.output:
            print()
            print_success(f"Detailed report saved to: {args.output}")
        
        # Apply suggestions if requested
        if args.apply:
            print()
            print_warning("Auto-apply is experimental and only supports limited transformations")
            
            if args.dry_run or not args.apply:
                print_info("Running in DRY-RUN mode (no files will be modified)")
            
            stats = modernizer.apply_suggestions(
                categories=args.categories,
                dry_run=args.dry_run
            )
            
            print()
            print_success(f"Applied {stats['succeeded']} suggestion(s)")
            if stats['failed'] > 0:
                print_warning(f"Failed to apply {stats['failed']} suggestion(s)")
        
        return 0 if len(modernizer.suggestions) == 0 else 1
    
    except ImportError as e:
        print_error(f"Failed to import modernizer: {e}")
        return 1
    except Exception as e:
        print_error(f"Error modernizing code: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_convert(args):
    """Convert Python 2 code snippets to Python 3."""
    print_header("Code Snippet Converter")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from snippet_converter import SnippetConverter, format_diff, format_side_by_side
        
        # Get input code
        if args.code:
            code = args.code
            source_desc = "inline code"
        elif args.input == '-' or not args.input:
            print_info("Reading from stdin (press Ctrl+D when done)...")
            code = sys.stdin.read()
            source_desc = "stdin"
        else:
            validate_path(args.input)
            with open(args.input, 'r') as f:
                code = f.read()
            source_desc = args.input
        
        print_info(f"Converting {source_desc}...")
        print()
        
        # Convert
        converter = SnippetConverter()
        converted, changes = converter.convert(code)
        
        # Display results
        if args.quiet:
            print(converted)
        else:
            if args.side_by_side:
                print(format_side_by_side(code, converted))
            elif args.diff:
                diff = format_diff(code, converted)
                print(diff if diff else "No changes needed")
            else:
                print(f"{Colors.BOLD}=== Python 2 (Original) ==={Colors.ENDC}")
                print(code)
                print(f"\n{Colors.BOLD}=== Python 3 (Converted) ==={Colors.ENDC}")
                print(converted)
            
            if changes and not args.no_explanation:
                print(f"\n{Colors.BOLD}=== Changes Made ==={Colors.ENDC}\n")
                for i, change in enumerate(changes, 1):
                    print(f"{Colors.OKCYAN}{i}. {change['type']}{Colors.ENDC}")
                    if change['line'] > 0:
                        print(f"   Line {change['line']}")
                    print(f"   {Colors.FAIL}- {change['old']}{Colors.ENDC}")
                    print(f"   {Colors.OKGREEN}+ {change['new']}{Colors.ENDC}")
                    print(f"   {Colors.WARNING}ℹ {change['explanation']}{Colors.ENDC}")
                    print()
            
            if not changes:
                print()
                print_success("No changes needed - code is already Python 3 compatible!")
            else:
                print()
                print_success(f"Made {len(changes)} change(s) to convert code to Python 3")
        
        # Save output if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(converted)
            print()
            print_success(f"Converted code saved to: {args.output}")
        
        return 0
    
    except ImportError as e:
        print_error(f"Failed to import snippet converter: {e}")
        return 1
    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        return 1
    except Exception as e:
        print_error(f"Error converting code: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_version_check(args):
    """Check Python version compatibility of migrated code."""
    print_header("Python Version Compatibility Check")
    
    validate_path(args.path)
    
    print_info(f"Analyzing path: {args.path}")
    if args.target:
        print_info(f"Target version: Python {args.target}")
    print_info(f"Format: {args.format}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from version_checker import VersionChecker
        
        checker = VersionChecker()
        
        print_info("Scanning for version-specific features...")
        if os.path.isfile(args.path):
            checker.analyze_file(args.path)
        else:
            checker.analyze_directory(args.path)
        
        # Generate report
        report = checker.generate_report(args.format)
        
        # Print or save report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print_success(f"Report saved to: {args.output}")
            print()
        else:
            print(report)
            print()
        
        # Show summary
        min_version = checker.get_minimum_version()
        print_success(f"Analysis complete: {checker.analyzed_files} file(s) analyzed")
        print_info(f"Minimum Python version required: {min_version}")
        
        # Check target compatibility if specified
        if args.target:
            print()
            incompatible = checker.check_compatibility(args.target)
            if incompatible:
                print_warning(f"Found {len(incompatible)} incompatibility(ies) with Python {args.target}:")
                for issue, details in list(incompatible.items())[:5]:
                    print(f"  • {details['description']}")
                    print(f"    Requires: Python {details['required_version']}")
                if len(incompatible) > 5:
                    print(f"  ... and {len(incompatible) - 5} more issues")
                return 1
            else:
                print_success(f"✓ Code is compatible with Python {args.target}")
        
        if checker.errors:
            print()
            print_warning(f"Encountered {len(checker.errors)} error(s) during analysis")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import version checker: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during version check: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_review(args):
    """Generate code review assistance for migration changes."""
    print_header("Code Review Assistant")
    
    validate_path(args.path)
    
    print_info(f"Analyzing path: {args.path}")
    print_info(f"Format: {args.format}")
    
    if args.pr:
        print_info("Generating PR description")
    
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from review_assistant import MigrationReviewAssistant
        
        assistant = MigrationReviewAssistant()
        
        print_info("Analyzing migration changes...")
        analysis = assistant.analyze_changes(args.path)
        
        # Generate report
        if args.pr:
            report = assistant.generate_pr_description(analysis)
        else:
            report = assistant.generate_report(analysis, args.format)
        
        # Print summary
        summary = analysis['summary']
        print_success(f"Analyzed {summary['total_files']} file(s)")
        print_info(f"Found {summary['total_changes']} change(s)")
        
        if analysis['high_risk_changes'] > 0:
            print_warning(f"{analysis['high_risk_changes']} high-risk change(s) require careful review")
        
        print()
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print_success(f"Review report saved to: {args.output}")
        else:
            print(report)
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import review assistant: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during review analysis: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_typehints(args):
    """Generate type hints for Python 3 code."""
    print_header("Type Hints Generator")
    
    validate_path(args.path)
    
    print_info(f"Analyzing path: {args.path}")
    
    if args.dry_run:
        print_warning("DRY RUN MODE: No files will be modified")
    
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from type_hints_generator import TypeHintsGenerator
        
        generator = TypeHintsGenerator(dry_run=args.dry_run)
        
        # Process path
        if os.path.isfile(args.path):
            print_info("Processing single file...")
            results = [generator.process_file(args.path)]
        else:
            print_info("Processing directory...")
            results = generator.process_directory(args.path)
        
        print()
        
        # Print summary
        stats = generator.stats
        print_success(f"Processed {stats['files_processed']} file(s)")
        print_info(f"Functions annotated: {stats['functions_annotated']}")
        print_info(f"Parameters annotated: {stats['parameters_annotated']}")
        print_info(f"Return types added: {stats['returns_annotated']}")
        print_info(f"Typing imports added: {stats['imports_added']}")
        
        print()
        
        # Generate reports
        if args.report:
            generator.generate_report(results, args.report)
            print_success(f"Detailed report saved to: {args.report}")
        else:
            generator.generate_report(results)
        
        if args.json:
            generator.generate_json_report(results, args.json)
            print_success(f"JSON report saved to: {args.json}")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import type hints generator: {e}")
        return 1
    except Exception as e:
        print_error(f"Error generating type hints: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_estimate(args):
    """Estimate effort required for Python 2 to 3 migration."""
    print_header("Migration Effort Estimator")
    
    validate_path(args.path)
    
    print_info(f"Analyzing codebase: {args.path}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from effort_estimator import EffortEstimator
        
        estimator = EffortEstimator()
        
        print_info("Scanning files and detecting issues...")
        estimator.analyze_codebase(args.path)
        
        print_success(f"Found {estimator.file_count} Python files with {len(estimator.issues)} issues")
        print_info("Calculating estimates...")
        print()
        
        # Calculate estimates
        estimate = estimator.estimate_effort()
        team_recommendation = estimator.recommend_team_size(estimate)
        timeline = estimator.generate_timeline(estimate, team_recommendation)
        
        # Generate report
        report = estimator.format_report(estimate, team_recommendation, timeline, args.format)
        
        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print_success(f"Report saved to: {args.output}")
        else:
            print(report)
        
        print()
        print_success("Estimation complete!")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import effort estimator: {e}")
        return 1
    except Exception as e:
        print_error(f"Error estimating effort: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_export(args):
    """Export migration package."""
    print_header("Migration Package Export")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from export_manager import MigrationExporter, list_packages
        
        if not hasattr(args, 'export_action') or not args.export_action:
            print_error("No export action specified. Use 'create' or 'list'")
            print_info("Run: py2to3 export --help")
            return 1
        
        if args.export_action == 'create':
            # Create export package
            print_info("Creating migration export package...")
            print()
            
            exporter = MigrationExporter(args.path)
            
            # Show what will be included
            print_info("Package contents:")
            if args.config:
                print("  ✓ Configuration files")
            if args.recipes:
                print("  ✓ Custom recipes")
            if args.state:
                print("  ✓ Migration state")
            if args.journal:
                print("  ✓ Journal entries")
            if args.stats:
                print("  ✓ Statistics snapshots")
            if args.backups:
                print("  ✓ Backup files")
                if args.backup_pattern:
                    print(f"    Pattern: {args.backup_pattern}")
            print()
            
            # Create package
            package_path = exporter.export_package(
                output_path=args.output,
                include_config=args.config,
                include_recipes=args.recipes,
                include_state=args.state,
                include_journal=args.journal,
                include_stats=args.stats,
                include_backups=args.backups,
                backup_pattern=args.backup_pattern,
                description=args.description,
                tags=args.tags.split(',') if args.tags else None
            )
            
            print_success(f"Package created: {package_path}")
            
            # Show package info
            from pathlib import Path as PathLib
            size = PathLib(package_path).stat().st_size
            size_mb = size / (1024 * 1024)
            print_info(f"Package size: {size_mb:.2f} MB")
            print()
            print_info("To import this package in another project:")
            print(f"  py2to3 import {PathLib(package_path).name}")
            
        elif args.export_action == 'list':
            # List available packages
            print_info(f"Searching for packages in: {args.directory or '.'}")
            print()
            
            packages = list_packages(args.directory or '.')
            
            if not packages:
                print_warning("No migration packages found")
                return 0
            
            print_success(f"Found {len(packages)} package(s):\n")
            
            from pathlib import Path as PathLib
            for i, pkg in enumerate(packages, 1):
                print(f"{Colors.BOLD}{i}. {PathLib(pkg['file']).name}{Colors.ENDC}")
                print(f"   Created: {pkg['created_at']}")
                print(f"   Size: {pkg['size'] / (1024 * 1024):.2f} MB")
                print(f"   Files: {pkg['file_count']}")
                if pkg.get('description'):
                    print(f"   Description: {pkg['description']}")
                if pkg.get('tags'):
                    print(f"   Tags: {', '.join(pkg['tags'])}")
                
                # Show components
                components = pkg.get('components', {})
                included = [k for k, v in components.items() if v]
                if included:
                    print(f"   Components: {', '.join(included)}")
                print()
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import export manager: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during export: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_import(args):
    """Import migration package."""
    print_header("Migration Package Import")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from export_manager import MigrationImporter
        
        print_info(f"Importing package: {args.package}")
        print_info(f"Target path: {args.path}")
        print()
        
        # Show what will be imported
        print_info("Import options:")
        print(f"  Configuration: {'Yes' if args.config else 'No'}")
        print(f"  Recipes: {'Yes' if args.recipes else 'No'}")
        print(f"  State: {'Yes' if args.state else 'No'}")
        print(f"  Journal: {'Yes' if args.journal else 'No'}")
        print(f"  Statistics: {'Yes' if args.stats else 'No'}")
        print(f"  Backups: {'Yes' if args.backups else 'No'}")
        print(f"  Merge mode: {'Yes' if args.merge else 'No (overwrite)'}")
        print()
        
        if args.dry_run:
            print_warning("DRY RUN MODE - No changes will be made")
            print()
        
        importer = MigrationImporter(args.path)
        
        report = importer.import_package(
            package_path=args.package,
            import_config=args.config,
            import_recipes=args.recipes,
            import_state=args.state,
            import_journal=args.journal,
            import_stats=args.stats,
            import_backups=args.backups,
            merge=args.merge,
            dry_run=args.dry_run
        )
        
        # Show results
        if report['files_imported']:
            print_success(f"Imported {len(report['files_imported'])} file(s):")
            for file in report['files_imported']:
                print(f"  ✓ {file}")
        
        if report['files_skipped']:
            print()
            print_warning(f"Skipped {len(report['files_skipped'])} file(s):")
            for file in report['files_skipped'][:5]:
                print(f"  - {file}")
            if len(report['files_skipped']) > 5:
                print(f"  ... and {len(report['files_skipped']) - 5} more")
        
        if report['errors']:
            print()
            print_error(f"Encountered {len(report['errors'])} error(s):")
            for error in report['errors'][:5]:
                print(f"  ✗ {error}")
            if len(report['errors']) > 5:
                print(f"  ... and {len(report['errors']) - 5} more")
        
        if not args.dry_run:
            print()
            print_success("Import complete!")
        else:
            print()
            print_info("Dry run complete. Run without --dry-run to apply changes.")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import migration importer: {e}")
        return 1
    except FileNotFoundError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error during import: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_rollback(args):
    """Rollback migration operations."""
    print_header("Rollback Manager")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from rollback_manager import RollbackManager
        
        manager = RollbackManager()
        
        if not hasattr(args, 'rollback_action') or not args.rollback_action:
            print_error("Please specify a rollback action (undo, list, preview, stats, clear)")
            print_info("Use 'py2to3 rollback --help' for more information")
            return 1
        
        if args.rollback_action == 'undo':
            # Rollback an operation
            operation_id = args.id if hasattr(args, 'id') and args.id else None
            
            if operation_id:
                print_info(f"Rolling back operation: {operation_id}")
            else:
                print_info("Rolling back last operation...")
            
            # Preview first
            preview = manager.preview_rollback(operation_id)
            
            if not preview["success"]:
                print_error(preview.get("error", "Failed to preview rollback"))
                return 1
            
            # Show preview
            op = preview["operation"]
            print()
            print_info(f"Operation ID: {op['id']}")
            print_info(f"Type: {op['type']}")
            print_info(f"Timestamp: {op['timestamp']}")
            if op.get('description'):
                print_info(f"Description: {op['description']}")
            print()
            print_info(f"Files to restore: {preview['restorable_files']}/{preview['total_files']}")
            
            if preview['files_missing_backups']:
                print_warning(f"Missing backups: {len(preview['files_missing_backups'])}")
                if args.verbose:
                    for f in preview['files_missing_backups']:
                        print(f"  - {f['path']}")
            
            # Check if dry run
            if args.dry_run:
                print()
                print_info("Dry run - showing what would be restored:")
                for file_info in preview['files_to_restore']:
                    print(f"  ✓ {file_info['path']}")
                return 0
            
            # Ask for confirmation unless --yes is specified
            if not args.yes:
                print()
                response = input(f"{Colors.WARNING}Proceed with rollback? (y/N): {Colors.ENDC}")
                if response.lower() != 'y':
                    print_info("Rollback cancelled")
                    return 0
            
            # Perform rollback
            print()
            result = manager.rollback(operation_id, force=args.force)
            
            if result["success"]:
                print_success(f"Successfully rolled back operation {result['operation_id']}")
                print_info(f"Restored {result['total_restored']} file(s)")
                
                if result['total_failed'] > 0:
                    print_warning(f"Failed to restore {result['total_failed']} file(s)")
                    if args.verbose:
                        for f in result['failed_files']:
                            print(f"  ✗ {f['path']}: {f['error']}")
                
                return 0 if result['total_failed'] == 0 else 1
            else:
                print_error(f"Rollback failed: {result.get('error', 'Unknown error')}")
                return 1
        
        elif args.rollback_action == 'list':
            # List all operations
            operations = manager.get_operations(include_rolled_back=args.all)
            
            if not operations:
                print_warning("No operations found in history")
                print_info("Operations are tracked automatically when you use 'fix', 'modernize', etc.")
                return 0
            
            print_info(f"Found {len(operations)} operation(s):\n")
            
            for op in reversed(operations):  # Show most recent first
                rolled_back = op.get('rolled_back', False)
                status_icon = "↩" if rolled_back else "✓"
                status_color = Colors.WARNING if rolled_back else Colors.OKGREEN
                
                print(f"{status_color}{status_icon}{Colors.ENDC} {op['id']}")
                print(f"  Type: {op['type']}")
                print(f"  Time: {op['timestamp']}")
                if op.get('description'):
                    print(f"  Description: {op['description']}")
                print(f"  Files: {len(op.get('files', []))}")
                if rolled_back:
                    print(f"  {Colors.WARNING}Rolled back: {op.get('rollback_timestamp', 'Unknown')}{Colors.ENDC}")
                print()
            
            return 0
        
        elif args.rollback_action == 'preview':
            # Preview rollback without doing it
            operation_id = args.id if hasattr(args, 'id') and args.id else None
            
            preview = manager.preview_rollback(operation_id)
            
            if not preview["success"]:
                print_error(preview.get("error", "Failed to preview rollback"))
                return 1
            
            op = preview["operation"]
            print_info(f"Operation ID: {op['id']}")
            print_info(f"Type: {op['type']}")
            print_info(f"Timestamp: {op['timestamp']}")
            if op.get('description'):
                print_info(f"Description: {op['description']}")
            print()
            
            print_success(f"Files that can be restored: {preview['restorable_files']}")
            for file_info in preview['files_to_restore'][:10]:  # Show first 10
                print(f"  ✓ {file_info['path']}")
            if len(preview['files_to_restore']) > 10:
                print(f"  ... and {len(preview['files_to_restore']) - 10} more")
            
            if preview['files_missing_backups']:
                print()
                print_warning(f"Files with missing backups: {len(preview['files_missing_backups'])}")
                for file_info in preview['files_missing_backups'][:5]:
                    print(f"  ✗ {file_info['path']}")
                if len(preview['files_missing_backups']) > 5:
                    print(f"  ... and {len(preview['files_missing_backups']) - 5} more")
            
            return 0
        
        elif args.rollback_action == 'stats':
            # Show rollback statistics
            stats = manager.get_statistics()
            
            if args.json:
                import json
                print(json.dumps(stats, indent=2))
            else:
                print_info("Rollback Statistics:\n")
                print(f"Total operations: {stats['total_operations']}")
                print(f"Active operations: {stats['active_operations']}")
                print(f"Rolled back: {stats['rolled_back_operations']}")
                print(f"Total files tracked: {stats['total_files_tracked']}")
                
                if stats['operations_by_type']:
                    print("\nOperations by type:")
                    for op_type, count in stats['operations_by_type'].items():
                        print(f"  {op_type}: {count}")
            
            return 0
        
        elif args.rollback_action == 'clear':
            # Clear operation history
            if not args.yes:
                print_warning("This will clear the operation history.")
                response = input(f"{Colors.WARNING}Are you sure? (y/N): {Colors.ENDC}")
                if response.lower() != 'y':
                    print_info("Clear cancelled")
                    return 0
            
            keep_recent = args.keep if hasattr(args, 'keep') and args.keep else 0
            result = manager.clear_history(keep_recent=keep_recent)
            
            print_success(f"Cleared {result['cleared']} operation(s)")
            if result['remaining'] > 0:
                print_info(f"Kept {result['remaining']} recent operation(s)")
            
            return 0
        
        else:
            print_error(f"Unknown rollback action: {args.rollback_action}")
            return 1
        
    except ImportError as e:
        print_error(f"Failed to import rollback manager: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during rollback: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_freeze(args):
    """Freeze Guard - Prevent Python 2 code from being re-introduced."""
    print_header("Freeze Guard - Python 2 Prevention")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from freeze_guard import FreezeGuard
        
        config_path = args.config if hasattr(args, 'config') and args.config else '.freeze-guard.json'
        guard = FreezeGuard(config_path)
        
        if not hasattr(args, 'freeze_action') or not args.freeze_action:
            print_error("Please specify a freeze action (check, mark, unmark, status, install-hook)")
            print_info("Use 'py2to3 freeze --help' for more information")
            return 1
        
        if args.freeze_action == 'check':
            # Check files for Python 2 patterns
            if args.staged:
                print_info("Checking git staged files for Python 2 patterns...")
                violations, files = guard.check_git_staged()
                if not violations:
                    checked_frozen = [f for f in files if guard.config.is_frozen(f)]
                    if checked_frozen:
                        print_success(f"Checked {len(checked_frozen)} frozen file(s) - all clear!")
                    else:
                        print_success("No frozen files in staged changes")
                    return 0
            else:
                paths = args.paths if args.paths else ['.']
                print_info(f"Checking paths: {', '.join(paths)}")
                for path in paths:
                    if os.path.isfile(path):
                        violations = guard.check_files([path], only_frozen=args.frozen_only)
                    else:
                        violations = guard.check_directory(path)
            
            # Generate and print report
            report = guard.generate_report(format=args.format)
            print(report)
            return 1 if violations else 0
        
        elif args.freeze_action == 'mark':
            # Mark paths as frozen
            for path in args.paths:
                if not os.path.exists(path):
                    print_warning(f"Path does not exist: {path}")
                    continue
                guard.config.add_frozen_path(path)
                print_success(f"Marked as frozen: {path}")
            print_info(f"Frozen paths now tracked in: {config_path}")
            return 0
        
        elif args.freeze_action == 'unmark':
            # Unmark frozen paths
            for path in args.paths:
                guard.config.remove_frozen_path(path)
                print_success(f"Unmarked: {path}")
            return 0
        
        elif args.freeze_action == 'status':
            # Show frozen paths status
            frozen_paths = guard.config.get_frozen_paths()
            
            if args.json:
                import json
                print(json.dumps({
                    "frozen_paths": frozen_paths,
                    "total": len(frozen_paths)
                }, indent=2))
            else:
                if not frozen_paths:
                    print_warning("No frozen paths configured")
                    print_info(f"Use 'py2to3 freeze mark <path>' to freeze migrated code")
                else:
                    print_info(f"🔒 Frozen Paths ({len(frozen_paths)}):")
                    print()
                    for path in frozen_paths:
                        exists = "✓" if os.path.exists(path) else "✗"
                        status = f"{Colors.OKGREEN}exists{Colors.ENDC}" if exists == "✓" else f"{Colors.FAIL}not found{Colors.ENDC}"
                        print(f"  [{exists}] {path:50} ({status})")
                    print()
                    print_info(f"Config file: {config_path}")
            return 0
        
        elif args.freeze_action == 'install-hook':
            # Install pre-commit hook
            print_info("Installing git pre-commit hook for freeze guard...")
            success = guard.install_pre_commit_hook()
            if success:
                print()
                print_success("Pre-commit hook installed successfully!")
                print_info("The hook will check frozen files on every commit")
                print_info("To bypass (not recommended): git commit --no-verify")
            return 0 if success else 1
        
        else:
            print_error(f"Unknown freeze action: {args.freeze_action}")
            return 1
    
    except ImportError as e:
        print_error(f"Failed to import freeze guard: {e}")
        return 1
    except Exception as e:
        print_error(f"Error in freeze guard: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_validate(args):
    """Validate Python 3 code by attempting to import all modules."""
    print_header("Runtime Validation")
    
    validate_path(args.path)
    
    print_info(f"Validating: {args.path}")
    print_info(f"Verbose mode: {'enabled' if args.verbose else 'disabled'}\n")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from runtime_validator import RuntimeValidator
        
        validator = RuntimeValidator(args.path, verbose=args.verbose)
        
        print_info("Discovering Python files...")
        validator.validate()
        
        report = validator.generate_report(format=args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print_success(f"Report saved to: {args.output}")
        else:
            print(report)
        
        results = validator._generate_summary()
        
        if results['summary']['failed'] == 0:
            print()
            print_success("All modules validated successfully!")
            return 0
        else:
            print()
            print_error(f"Validation failed: {results['summary']['failed']} module(s) have errors")
            return 1
        
    except ImportError as e:
        print_error(f"Failed to import runtime_validator: {e}")
        print_info("This feature requires the runtime_validator module")
        return 1
    except Exception as e:
        print_error(f"Validation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_encoding(args):
    """Analyze and fix encoding issues in Python files."""
    print_header("Encoding Analysis")
    
    validate_path(args.path)
    
    print_info(f"Analyzing: {args.path}")
    print_info(f"Recursive: {args.recursive}")
    if args.add_declarations:
        print_info(f"{'[DRY RUN] ' if args.dry_run else ''}Will add missing encoding declarations")
    if args.convert_to_utf8:
        print_info(f"{'[DRY RUN] ' if args.dry_run else ''}Will convert non-UTF-8 files to UTF-8")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from encoding_analyzer import EncodingAnalyzer
        
        analyzer = EncodingAnalyzer(target_encoding='utf-8')
        
        # Analyze files
        if os.path.isdir(args.path):
            results = analyzer.analyze_directory(args.path, recursive=args.recursive)
        else:
            result = analyzer.detect_encoding(args.path)
            analyzer.results = [result]
            results = [result]
        
        print_info(f"Analyzed {len(results)} file(s)\n")
        
        # Apply fixes if requested
        if args.add_declarations:
            print(f"{Colors.BOLD}Adding encoding declarations...{Colors.ENDC}\n")
            added_count = 0
            for result in results:
                if not result['has_declaration'] and result['status'] != 'error':
                    fix_result = analyzer.add_encoding_declaration(
                        result['file'],
                        dry_run=args.dry_run
                    )
                    if fix_result['success'] and fix_result['action'] != 'skipped':
                        print_success(f"{fix_result['file']}: {fix_result['message']}")
                        added_count += 1
            
            if added_count > 0:
                print()
                print_success(f"Added encoding declarations to {added_count} file(s)")
            else:
                print_info("No files needed encoding declarations")
            print()
        
        if args.convert_to_utf8:
            print(f"{Colors.BOLD}Converting files to UTF-8...{Colors.ENDC}\n")
            converted_count = 0
            for result in results:
                if result['detected_encoding'] and \
                   result['detected_encoding'].lower() not in ['utf-8', 'utf8', 'ascii']:
                    convert_result = analyzer.convert_to_utf8(
                        result['file'],
                        backup=not args.no_backup,
                        dry_run=args.dry_run
                    )
                    if convert_result['converted']:
                        print_success(f"{convert_result['file']}: {convert_result['message']}")
                        if convert_result['backup_created']:
                            print_info(f"  Backup created: {convert_result['file']}.bak")
                        converted_count += 1
            
            if converted_count > 0:
                print()
                print_success(f"Converted {converted_count} file(s) to UTF-8")
            else:
                print_info("No files needed conversion")
            print()
        
        # Generate and display report
        if args.format or args.output:
            report_format = args.format or 'text'
            report = analyzer.generate_report(output_format=report_format)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(report)
                print_success(f"Report saved to: {args.output}")
            else:
                print(report)
        else:
            # Show summary statistics
            stats = analyzer.get_statistics()
            print(f"{Colors.BOLD}Summary Statistics{Colors.ENDC}")
            print("=" * 60)
            print(f"Total files:                 {stats['total_files']}")
            print(f"Files with issues:           {stats['files_with_issues']}")
            print(f"Files without declaration:   {stats['files_without_declaration']}")
            print(f"Files with non-UTF-8:        {stats['files_non_utf8']}")
            print()
            
            if stats['encoding_distribution']:
                print(f"{Colors.BOLD}Encoding Distribution:{Colors.ENDC}")
                for encoding, count in sorted(stats['encoding_distribution'].items(), 
                                             key=lambda x: x[1], reverse=True):
                    print(f"  {encoding}: {count}")
                print()
            
            print(f"{Colors.BOLD}Status Distribution:{Colors.ENDC}")
            for status, count in stats['status_distribution'].items():
                if count > 0:
                    symbol = {
                        'ok': '✓',
                        'info': 'ℹ',
                        'warning': '⚠',
                        'error': '✗'
                    }.get(status, '?')
                    print(f"  {symbol} {status}: {count}")
            print()
        
        # Provide recommendations
        stats = analyzer.get_statistics()
        if stats['files_with_issues'] > 0 or stats['files_without_declaration'] > 0:
            print(f"{Colors.BOLD}Recommendations:{Colors.ENDC}")
            
            if stats['files_without_declaration'] > 0:
                print_warning(f"{stats['files_without_declaration']} file(s) lack encoding declarations")
                print_info("Run with --add-declarations to fix automatically")
            
            if stats['files_non_utf8'] > 0:
                print_warning(f"{stats['files_non_utf8']} file(s) use non-UTF-8 encoding")
                print_info("Run with --convert-to-utf8 to convert to UTF-8")
            
            print()
        else:
            print_success("All files have proper encoding declarations!")
        
        # Exit with error code if issues found
        return 1 if stats['files_with_issues'] > 0 else 0
        
    except ImportError as e:
        print_error(f"Failed to import encoding analyzer: {e}")
        print_info("Make sure the 'chardet' package is installed: pip install chardet")
        return 1
    except Exception as e:
        print_error(f"Error analyzing encodings: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_report_card(args):
    """Generate a comprehensive migration quality report card."""
    print_header("Migration Report Card")
    
    validate_path(args.path)
    
    print_info(f"Analyzing project: {args.path}")
    print_info(f"Output format: {args.format}")
    if args.output:
        print_info(f"Output file: {args.output}\n")
    else:
        print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from report_card import MigrationReportCard
        
        # Generate report card
        card = MigrationReportCard(args.path)
        
        if args.output:
            # Save to file
            card.save_report(args.output, args.format)
            print_success(f"Report card saved to: {args.output}")
            
            # If HTML, provide helpful info about opening it
            if args.format == 'html':
                print_info("Open the HTML file in your browser to view the report card")
            
            return 0
        else:
            # Print to stdout
            report = card.generate_report_card(args.format)
            print(report)
            return 0
            
    except ImportError as e:
        print_error(f"Failed to import report card generator: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except Exception as e:
        print_error(f"Error generating report card: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_metadata(args):
    """Update project metadata files for Python 3 compatibility."""
    print_header("Project Metadata Updater")
    
    validate_path(args.path)
    
    print_info(f"Project directory: {args.path}")
    print_info(f"Python version range: {args.min_version} - {args.max_version}")
    if args.dry_run:
        print_warning("DRY RUN MODE - No files will be modified\n")
    else:
        print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from metadata_updater import MetadataUpdater
        
        updater = MetadataUpdater(args.path, args.min_version, args.max_version)
        results = updater.update_all(dry_run=args.dry_run)
        
        if args.json:
            print(json.dumps(results, indent=2))
            return 0
        
        # Display results
        if results["updated_files"]:
            print_success(f"Updated {len(results['updated_files'])} file(s):")
            for item in results["updated_files"]:
                print(f"\n  📄 {Colors.BOLD}{item['file']}{Colors.ENDC}")
                for change in item['changes']:
                    print(f"     {Colors.OKGREEN}•{Colors.ENDC} {change}")
        
        if results["skipped_files"]:
            print(f"\n{Colors.OKCYAN}⊘ Skipped {len(results['skipped_files'])} file(s) (no changes needed){Colors.ENDC}")
            if args.verbose:
                for file in results["skipped_files"]:
                    print(f"  • {file}")
        
        if results["errors"]:
            print()
            print_warning(f"Encountered {len(results['errors'])} error(s):")
            for error in results["errors"]:
                print(f"  • {error}")
        
        if not args.dry_run and results["updated_files"]:
            backup_dir = os.path.join(args.path, ".metadata_backups")
            if os.path.exists(backup_dir):
                print()
                print_info(f"💾 Backups saved to: {backup_dir}")
        
        print()
        
        if results["updated_files"] and not args.dry_run:
            print_success("✓ Project metadata successfully updated for Python 3!")
            print_info("Review the changes and commit them to your repository.")
            return 0
        elif args.dry_run and results["updated_files"]:
            print_info("Run without --dry-run to apply these changes.")
            return 0
        else:
            print_info("No metadata updates needed - your project is already configured for Python 3!")
            return 0
            
    except ImportError as e:
        print_error(f"Failed to import metadata updater: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except Exception as e:
        print_error(f"Error updating metadata: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_changelog(args):
    """Generate changelog from migration activities."""
    print_header("Changelog Generator")
    
    validate_path(args.path)
    
    print_info(f"Project directory: {args.path}")
    if args.since:
        print_info(f"Since: {args.since}")
    if args.until:
        print_info(f"Until: {args.until}")
    print_info(f"Version: {args.version}")
    print_info(f"Format: {args.format}")
    if args.output:
        print_info(f"Output: {args.output} ({'append' if args.append else 'overwrite'})")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from changelog_generator import ChangelogGenerator
        
        generator = ChangelogGenerator(args.path)
        changelog = generator.generate_changelog(
            output_file=args.output,
            since=args.since,
            until=args.until,
            version=args.version,
            format_style=args.format,
            append=args.append,
        )
        
        if args.output:
            print_success(f"Changelog {'appended to' if args.append else 'written to'}: {args.output}")
            print_info(f"Generated {len(changelog.splitlines())} lines")
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import changelog generator: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except Exception as e:
        print_error(f"Error generating changelog: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_coverage(args):
    """Track test coverage during migration."""
    print_header("Coverage Tracker")
    
    if not hasattr(args, 'coverage_action') or not args.coverage_action:
        print_error("No coverage action specified")
        print_info("Available actions: collect, report, trend, risky, clear")
        print_info("Run: py2to3 coverage --help")
        return 1
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from coverage_tracker import CoverageTracker
        
        tracker = CoverageTracker(args.path)
        
        if args.coverage_action == 'collect':
            print_info(f"Project directory: {args.path}")
            if args.test_command:
                print_info(f"Test command: {args.test_command}")
            else:
                print_info("Test command: auto-detect")
            print()
            
            print_info("Running tests with coverage...")
            success, message = tracker.run_coverage(args.test_command)
            
            if success:
                print_success(message)
                print()
                
                print_info("Parsing coverage data...")
                coverage_data = tracker.parse_coverage_json()
                
                if coverage_data:
                    analysis = tracker.analyze_coverage(coverage_data)
                    snapshot = tracker.save_snapshot(
                        analysis,
                        args.description or f"Coverage snapshot"
                    )
                    
                    print_success("Coverage snapshot saved")
                    print()
                    print_info(f"Overall Coverage: {analysis['overall_coverage']:.2f}%")
                    print_info(f"Total Files: {analysis['total_files']}")
                    print_info(f"Total Statements: {analysis['total_statements']}")
                    print_info(f"Covered: {analysis['covered_statements']}")
                    print_info(f"Missing: {analysis['missing_statements']}")
                    
                    if analysis.get('uncovered_files'):
                        print_warning(f"Uncovered files: {len(analysis['uncovered_files'])}")
                    if analysis.get('low_coverage_files'):
                        print_warning(f"Low coverage files: {len(analysis['low_coverage_files'])}")
                    
                    return 0
                else:
                    print_error("Could not parse coverage data")
                    print_info("Make sure coverage.json was generated")
                    return 1
            else:
                print_error(message)
                print_info("Try installing: pip install pytest pytest-cov")
                return 1
        
        elif args.coverage_action == 'report':
            print_info(f"Project directory: {args.path}")
            if args.output:
                print_info(f"Output file: {args.output}")
            print()
            
            report = tracker.generate_report(args.output)
            
            if "No coverage data" in report:
                print_warning(report.strip())
                print_info("Run 'py2to3 coverage collect' first")
                return 1
            
            print(report)
            
            if args.output:
                print_success(f"Report saved to: {args.output}")
            
            return 0
        
        elif args.coverage_action == 'trend':
            print_info(f"Project directory: {args.path}")
            print()
            
            trend = tracker.get_coverage_trend()
            
            if not trend:
                print_warning("No coverage snapshots available")
                print_info("Run 'py2to3 coverage collect' first")
                return 1
            
            print_info("Coverage Trend:")
            print("-" * 70)
            
            for entry in trend:
                timestamp = entry["timestamp"][:19]
                coverage = entry["coverage"]
                files = entry["files"]
                description = entry.get("description", "")
                
                # Color code based on coverage
                if coverage >= 80:
                    color = Colors.OKGREEN
                elif coverage >= 50:
                    color = Colors.WARNING
                else:
                    color = Colors.FAIL
                
                print(
                    f"{timestamp}  {color}{coverage:5.1f}%{Colors.ENDC}  "
                    f"({files} files)  {description}"
                )
            
            # Show trend direction
            if len(trend) >= 2:
                recent = trend[-1]["coverage"]
                previous = trend[-2]["coverage"]
                change = recent - previous
                
                print()
                if change > 0:
                    print_success(f"Coverage improved by {change:.2f}%")
                elif change < 0:
                    print_warning(f"Coverage decreased by {abs(change):.2f}%")
                else:
                    print_info("Coverage unchanged")
            
            return 0
        
        elif args.coverage_action == 'risky':
            print_info(f"Project directory: {args.path}")
            print_info(f"Coverage threshold: {args.threshold}%")
            print()
            
            risky = tracker.identify_risky_migrations()
            
            if not risky:
                print_success("No risky migrations identified!")
                print_info("All files have adequate test coverage")
                return 0
            
            # Filter by threshold
            risky_filtered = [f for f in risky if f["coverage"] < args.threshold]
            
            if not risky_filtered:
                print_success(f"No files below {args.threshold}% coverage threshold")
                return 0
            
            print_warning(f"Found {len(risky_filtered)} files with coverage below {args.threshold}%:")
            print()
            print("-" * 70)
            
            for file_info in risky_filtered[:20]:
                coverage = file_info["coverage"]
                path = file_info["path"]
                
                # Color code based on severity
                if coverage == 0:
                    color = Colors.FAIL
                elif coverage < 25:
                    color = Colors.WARNING
                else:
                    color = Colors.OKCYAN
                
                print(f"  {color}{coverage:5.1f}%{Colors.ENDC}  {path}")
            
            if len(risky_filtered) > 20:
                print(f"  ... and {len(risky_filtered) - 20} more")
            
            print()
            print_info("Consider adding tests to these files before migration")
            print_info("Run 'py2to3 test-gen' to auto-generate test templates")
            
            return 0
        
        elif args.coverage_action == 'clear':
            print_info(f"Project directory: {args.path}")
            print()
            
            tracker.clear_snapshots()
            print_success("Coverage snapshots cleared")
            
            return 0
        
        else:
            print_error(f"Unknown coverage action: {args.coverage_action}")
            return 1
    
    except ImportError as e:
        print_error(f"Failed to import coverage tracker: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except Exception as e:
        print_error(f"Error running coverage tracker: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_wizard(args):
    """Launch the interactive Smart Migration Wizard."""
    print_header("Smart Migration Wizard")
    
    print_info(f"Starting wizard for: {args.path}")
    print()
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from migration_wizard import MigrationWizard
        
        wizard = MigrationWizard(args.path)
        wizard.run()
        
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import migration wizard: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except KeyboardInterrupt:
        print()
        print_warning("Wizard cancelled by user")
        return 130
    except Exception as e:
        print_error(f"Error running wizard: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_precommit(args):
    """Manage pre-commit hooks for Python 3 compatibility."""
    action = args.precommit_action
    
    print_header(f"Pre-commit Hook Management: {action.title()}")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from precommit_generator import PreCommitGenerator
        
        generator = PreCommitGenerator(args.repo_root)
        
        if action == 'install':
            print_info(f"Installing pre-commit hooks in {generator.repo_root}")
            print_info(f"Mode: {args.mode}")
            print_info(f"Files pattern: {args.files_pattern}")
            if args.exclude_pattern:
                print_info(f"Exclude pattern: {args.exclude_pattern}")
            print()
            
            results = generator.install_hooks(
                mode=args.mode,
                files_pattern=args.files_pattern,
                exclude_pattern=args.exclude_pattern,
                force=args.force
            )
            
            if results['config_created']:
                print_success("Created .pre-commit-config.yaml")
            
            if results['hook_created']:
                print_success("Created custom validator hook")
            
            if results['precommit_installed']:
                print_success("Installed pre-commit hooks")
            else:
                print_warning("Pre-commit framework not installed")
                print_info("Install it with: pip install pre-commit")
                print_info("Then run: pre-commit install")
            
            if results['errors']:
                print()
                for error in results['errors']:
                    print_warning(error)
                return 1
            
            print()
            print_success("Pre-commit hooks installed successfully!")
            print_info("Hooks will run automatically before each commit")
            print_info(f"To test: git commit --dry-run or use './py2to3 precommit test'")
            return 0
        
        elif action == 'uninstall':
            print_info(f"Uninstalling pre-commit hooks from {generator.repo_root}")
            print()
            
            results = generator.uninstall_hooks()
            
            if results['config_removed']:
                print_success("Removed .pre-commit-config.yaml")
            
            if results['hook_removed']:
                print_success("Removed custom validator hook")
            
            if results['precommit_uninstalled']:
                print_success("Uninstalled pre-commit hooks")
            
            print()
            print_success("Pre-commit hooks uninstalled successfully!")
            return 0
        
        elif action == 'status':
            print_info(f"Checking pre-commit hook status in {generator.repo_root}")
            print()
            
            status = generator.check_status()
            
            print(f"Git repository: {Colors.OKGREEN if status['git_repo'] else Colors.FAIL}{'Yes' if status['git_repo'] else 'No'}{Colors.ENDC}")
            print(f"Config exists: {Colors.OKGREEN if status['config_exists'] else Colors.FAIL}{'Yes' if status['config_exists'] else 'No'}{Colors.ENDC}")
            print(f"Custom hook exists: {Colors.OKGREEN if status['hook_exists'] else Colors.FAIL}{'Yes' if status['hook_exists'] else 'No'}{Colors.ENDC}")
            print(f"Pre-commit available: {Colors.OKGREEN if status['precommit_available'] else Colors.FAIL}{'Yes' if status['precommit_available'] else 'No'}{Colors.ENDC}")
            
            if status.get('precommit_version'):
                print(f"Pre-commit version: {status['precommit_version']}")
            
            print(f"Pre-commit installed: {Colors.OKGREEN if status['precommit_installed'] else Colors.FAIL}{'Yes' if status['precommit_installed'] else 'No'}{Colors.ENDC}")
            
            if status.get('mode'):
                print(f"Configuration mode: {status['mode']}")
            
            print()
            if status['config_exists'] and status['hook_exists'] and status['precommit_installed']:
                print_success("Pre-commit hooks are fully configured and active")
            elif status['config_exists'] and status['hook_exists']:
                print_warning("Hooks configured but pre-commit not installed")
                print_info("Run: pre-commit install")
            else:
                print_warning("Pre-commit hooks not configured")
                print_info("Run: ./py2to3 precommit install")
            
            return 0
        
        elif action == 'test':
            print_info(f"Testing pre-commit hooks in {generator.repo_root}")
            if args.test_file:
                print_info(f"Testing file: {args.test_file}")
            else:
                print_info("Testing all staged files")
            print()
            
            results = generator.test_hooks(args.test_file)
            
            if results['output']:
                print(results['output'])
            
            if results['errors']:
                print()
                for error in results['errors']:
                    print_error(error)
                return 1
            
            if results['success']:
                print()
                print_success("All pre-commit hooks passed!")
                return 0
            else:
                print()
                print_warning("Some pre-commit hooks failed")
                return 1
        
        else:
            print_error(f"Unknown action: {action}")
            return 1
    
    except ImportError as e:
        print_error(f"Failed to import precommit generator: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled by user")
        return 130
    except Exception as e:
        print_error(f"Error managing pre-commit hooks: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_completion(args):
    """Manage shell completions for py2to3 CLI."""
    action = args.completion_action
    
    print_header(f"Shell Completion Management: {action.title() if action else 'Help'}")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from completion_generator import CompletionGenerator
        
        generator = CompletionGenerator()
        
        if action == 'generate':
            shell = args.shell if hasattr(args, 'shell') and args.shell else generator.detect_shell()
            
            if not shell:
                print_error("Could not detect shell. Please specify: bash, zsh, or fish")
                print_info("Usage: py2to3 completion generate <shell>")
                return 1
            
            if shell not in ['bash', 'zsh', 'fish']:
                print_error(f"Unsupported shell: {shell}")
                print_info("Supported shells: bash, zsh, fish")
                return 1
            
            print_info(f"Generating {shell} completion script...")
            print()
            
            # Generate and print the script
            if shell == 'bash':
                script = generator.generate_bash_completion()
            elif shell == 'zsh':
                script = generator.generate_zsh_completion()
            else:  # fish
                script = generator.generate_fish_completion()
            
            if hasattr(args, 'output') and args.output:
                # Write to file
                try:
                    with open(args.output, 'w') as f:
                        f.write(script)
                    print_success(f"Completion script written to {args.output}")
                    print_info(f"To use: source {args.output}")
                except Exception as e:
                    print_error(f"Failed to write completion script: {e}")
                    return 1
            else:
                # Print to stdout
                print(script)
            
            return 0
        
        elif action == 'install':
            shell = args.shell if hasattr(args, 'shell') and args.shell else generator.detect_shell()
            
            if not shell:
                print_error("Could not detect shell. Please specify: bash, zsh, or fish")
                print_info("Usage: py2to3 completion install <shell>")
                return 1
            
            print_info(f"Installing {shell} completions...")
            print()
            
            success, message = generator.install_completion(shell)
            
            if success:
                print_success("Installation successful!")
                print()
                print(message)
                return 0
            else:
                print_error("Installation failed!")
                print_error(message)
                return 1
        
        elif action == 'uninstall':
            shell = args.shell if hasattr(args, 'shell') and args.shell else generator.detect_shell()
            
            if not shell:
                print_error("Could not detect shell. Please specify: bash, zsh, or fish")
                print_info("Usage: py2to3 completion uninstall <shell>")
                return 1
            
            print_info(f"Uninstalling {shell} completions...")
            print()
            
            success, message = generator.uninstall_completion(shell)
            
            if success:
                print_success("Uninstallation successful!")
                print()
                print(message)
                return 0
            else:
                print_error("Uninstallation failed!")
                print_error(message)
                return 1
        
        elif action == 'status':
            print_info("Checking completion installation status...")
            print()
            
            status = generator.check_completion_status()
            current_shell = generator.detect_shell()
            
            if current_shell:
                print(f"Current shell: {Colors.OKCYAN}{current_shell}{Colors.ENDC}")
                print()
            
            print("Installation status:")
            for shell, installed in status.items():
                status_str = f"{Colors.OKGREEN}✓ Installed{Colors.ENDC}" if installed else f"{Colors.FAIL}✗ Not installed{Colors.ENDC}"
                print(f"  {shell:8s}: {status_str}")
            
            print()
            
            if not any(status.values()):
                print_warning("No completions are installed")
                print_info("Run: py2to3 completion install")
            elif current_shell and status.get(current_shell):
                print_success(f"Completions are installed for your current shell ({current_shell})")
            elif current_shell:
                print_warning(f"Completions are not installed for your current shell ({current_shell})")
                print_info(f"Run: py2to3 completion install {current_shell}")
            
            return 0
        
        else:
            print_error("No action specified")
            print_info("Available actions: generate, install, uninstall, status")
            print_info("Example: py2to3 completion install")
            return 1
    
    except ImportError as e:
        print_error(f"Failed to import completion generator: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled by user")
        return 130
    except Exception as e:
        print_error(f"Error managing completions: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def command_readiness(args):
    """Assess migration readiness and safety score."""
    assessment_type = args.readiness_type
    
    print_header(f"Migration Readiness Assessment: {assessment_type.upper()}")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from readiness_checker import ReadinessChecker
        
        checker = ReadinessChecker(args.path)
        
        if assessment_type in ['pre', 'both']:
            print_info(f"Analyzing project at: {args.path}")
            print_info("Running pre-migration readiness assessment...\n")
            
            results = checker.assess_pre_migration_readiness()
            checker.print_report(results)
            
            if args.output:
                output_file = args.output if assessment_type == 'pre' else args.output.replace('.json', '_pre.json')
                checker.save_report(results, output_file)
        
        if assessment_type in ['post', 'both']:
            if assessment_type == 'both':
                print("\n\n")
            
            print_info(f"Analyzing project at: {args.path}")
            print_info("Running post-migration production readiness assessment...\n")
            
            results = checker.assess_post_migration_readiness()
            checker.print_report(results)
            
            if args.output:
                output_file = args.output if assessment_type == 'post' else args.output.replace('.json', '_post.json')
                checker.save_report(results, output_file)
        
        print_success("Assessment complete!")
        return 0
        
    except ImportError as e:
        print_error(f"Failed to import readiness checker: {e}")
        print_info("Make sure all required dependencies are installed")
        return 1
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled by user")
        return 130
    except Exception as e:
        print_error(f"Error during readiness assessment: {e}")
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
    
    # Wizard command (featured first as it's the beginner-friendly entry point)
    parser_wizard = subparsers.add_parser(
        'wizard',
        help='🚀 Interactive migration wizard (recommended for beginners)',
        description='Smart Migration Wizard - Interactive guided workflow for Python 2 to 3 migration'
    )
    parser_wizard.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the project to migrate (default: current directory)'
    )
    
    # Check command
    parser_check = subparsers.add_parser(
        'check',
        help='Check Python 3 compatibility',
        description='Verify code for Python 3 compatibility issues'
    )
    parser_check.add_argument('path', help='File or directory to check')
    parser_check.add_argument('-r', '--report', help='Save report to file')
    
    # Version-check command
    parser_version_check = subparsers.add_parser(
        'version-check',
        help='Check Python version compatibility',
        description='Analyze code to determine Python 3.x version requirements and compatibility'
    )
    parser_version_check.add_argument('path', help='File or directory to analyze')
    parser_version_check.add_argument('-o', '--output', help='Save report to file')
    parser_version_check.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                                     help='Output format (default: text)')
    parser_version_check.add_argument('-t', '--target', help='Target Python version to check compatibility (e.g., 3.8, 3.9, 3.10)')
    
    # Convert command
    parser_convert = subparsers.add_parser(
        'convert',
        help='Convert Python 2 code snippets to Python 3',
        description='Quick converter for Python 2 code snippets - perfect for learning and testing'
    )
    parser_convert.add_argument('input', nargs='?', help='Input file (use - or omit for stdin)')
    parser_convert.add_argument('-c', '--code', help='Code string to convert (alternative to file input)')
    parser_convert.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser_convert.add_argument('--side-by-side', action='store_true', help='Show side-by-side comparison')
    parser_convert.add_argument('--diff', action='store_true', help='Show unified diff')
    parser_convert.add_argument('--no-explanation', action='store_true', help='Skip change explanations')
    parser_convert.add_argument('--quiet', action='store_true', help='Only output converted code (no formatting)')
    
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
    
    # Review command
    parser_review = subparsers.add_parser(
        'review',
        help='Generate code review assistance for migrations',
        description='Analyze migration changes and generate review checklists, risk assessments, and PR descriptions'
    )
    parser_review.add_argument('path', help='File or directory to analyze')
    parser_review.add_argument('-f', '--format', choices=['markdown', 'text', 'json'], 
                              default='markdown', help='Output format (default: markdown)')
    parser_review.add_argument('-o', '--output', help='Output file (default: print to stdout)')
    parser_review.add_argument('--pr', action='store_true', 
                              help='Generate PR description instead of full report')
    
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
    
    # Graph command
    parser_graph = subparsers.add_parser(
        'graph',
        help='Generate visual dependency graph',
        description='Create interactive visualization of module dependencies for migration planning'
    )
    parser_graph.add_argument('path', help='Directory to analyze')
    parser_graph.add_argument('-o', '--output', default='dependency_graph.html',
                             help='Output HTML file (default: dependency_graph.html)')
    parser_graph.add_argument('--summary', action='store_true',
                             help='Print text summary instead of generating graph')
    
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
    
    # Status command
    parser_status = subparsers.add_parser(
        'status',
        help='Show quick migration status summary',
        description='Display an at-a-glance status report of migration progress in the terminal'
    )
    parser_status.add_argument('path', nargs='?', default='.',
                              help='Project path to analyze (default: current directory)')
    parser_status.add_argument('--stats-dir', default='.migration_stats',
                              help='Stats directory (default: .migration_stats)')
    parser_status.add_argument('--json', action='store_true',
                              help='Output in JSON format')
    parser_status.add_argument('-o', '--output',
                              help='Export JSON report to file (requires --json)')
    
    # Search command
    parser_search = subparsers.add_parser(
        'search',
        help='Search for Python 2 patterns',
        description='Search for specific Python 2 patterns in your codebase with context and highlighting'
    )
    parser_search.add_argument('path', nargs='?', default='.',
                              help='Path to search (default: current directory)')
    parser_search.add_argument('-p', '--patterns', nargs='+',
                              help='Specific patterns to search for (e.g., print_statement xrange)')
    parser_search.add_argument('-l', '--list-patterns', action='store_true',
                              help='List all available patterns and exit')
    parser_search.add_argument('-c', '--context', type=int, default=2,
                              help='Number of context lines to show (default: 2)')
    parser_search.add_argument('-o', '--output',
                              help='Output file for JSON export')
    parser_search.add_argument('--json', action='store_true',
                              help='Output in JSON format')
    
    # Security command
    parser_security = subparsers.add_parser(
        'security',
        help='🔒 Audit code for security vulnerabilities',
        description='Security Auditor - Scan for security issues introduced during Python 2->3 migration'
    )
    parser_security.add_argument('path', nargs='?', default='.',
                                help='File or directory to audit (default: current directory)')
    parser_security.add_argument('-o', '--output',
                                help='Save report to file')
    parser_security.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                                help='Report format (default: text)')
    parser_security.add_argument('--exclude', nargs='+',
                                default=['venv', '__pycache__', '.git', 'node_modules', 'tests'],
                                help='Patterns to exclude from scanning')
    parser_security.add_argument('--fail-on-high', action='store_true',
                                help='Exit with error if high/critical issues found')
    
    # Imports command
    parser_imports = subparsers.add_parser(
        'imports',
        help='Optimize and clean up Python imports',
        description='Analyze and optimize Python imports: remove unused imports, sort by PEP 8, remove duplicates'
    )
    parser_imports.add_argument('path', nargs='?', default='.',
                               help='File or directory to analyze (default: current directory)')
    parser_imports.add_argument('--fix', action='store_true',
                               help='Apply import optimizations to files')
    parser_imports.add_argument('--no-backup', action='store_true',
                               help='Do not create backup files when fixing')
    parser_imports.add_argument('--recursive', action='store_true', default=True,
                               help='Recursively process directories (default: True)')
    parser_imports.add_argument('-o', '--output',
                               help='Save report to file')
    
    # Modernize command
    parser_modernize = subparsers.add_parser(
        'modernize',
        help='Upgrade Python 3 code to use modern idioms',
        description='Analyze Python 3 code and suggest modern features like f-strings, type hints, pathlib, dataclasses, etc.'
    )
    parser_modernize.add_argument('path', nargs='?', default='.',
                                 help='File or directory to analyze (default: current directory)')
    parser_modernize.add_argument('--no-recursive', action='store_true',
                                 help='Do not recursively process directories')
    parser_modernize.add_argument('-o', '--output',
                                 help='Save detailed report to file')
    parser_modernize.add_argument('--format', choices=['text', 'json'], default='text',
                                 help='Report format (default: text)')
    parser_modernize.add_argument('--apply', action='store_true',
                                 help='Apply suggested modernizations (experimental)')
    parser_modernize.add_argument('--dry-run', action='store_true', default=True,
                                 help='Preview changes without modifying files (default: True)')
    parser_modernize.add_argument('--categories', nargs='+',
                                 choices=['f-strings', 'pathlib', 'dict-merge', 'type-hints', 
                                         'dataclass', 'context-manager', 'comprehension'],
                                 help='Only analyze specific categories')
    
    # Type Hints command
    parser_typehints = subparsers.add_parser(
        'typehints',
        help='Add type hints to Python 3 code',
        description='Automatically generate and add type hints to Python 3 code by analyzing function signatures, return values, and usage patterns'
    )
    parser_typehints.add_argument('path', help='File or directory to process')
    parser_typehints.add_argument('--dry-run', action='store_true',
                                 help='Preview changes without modifying files')
    parser_typehints.add_argument('-r', '--report',
                                 help='Save detailed report to file')
    parser_typehints.add_argument('--json',
                                 help='Save JSON report to file')
    
    # Validate command
    parser_validate = subparsers.add_parser(
        'validate',
        help='Validate Python 3 code by attempting imports',
        description='Perform runtime validation by attempting to import all modules and checking for runtime errors. This complements static analysis by verifying code actually works.'
    )
    parser_validate.add_argument('path', help='File or directory to validate')
    parser_validate.add_argument('-v', '--verbose', action='store_true',
                                help='Show detailed error tracebacks')
    parser_validate.add_argument('-o', '--output',
                                help='Save validation report to file')
    parser_validate.add_argument('-f', '--format', choices=['text', 'json'], 
                                default='text',
                                help='Report format (default: text)')
    
    # Encoding command
    parser_encoding = subparsers.add_parser(
        'encoding',
        help='Analyze and fix file encoding issues',
        description='Detect file encodings, identify encoding issues, and fix encoding declarations for Python 3 compatibility'
    )
    parser_encoding.add_argument('path', help='File or directory to analyze')
    parser_encoding.add_argument('-r', '--recursive', action='store_true',
                                help='Recursively analyze subdirectories')
    parser_encoding.add_argument('-o', '--output',
                                help='Save report to file')
    parser_encoding.add_argument('-f', '--format', choices=['text', 'json', 'markdown'],
                                help='Report format')
    parser_encoding.add_argument('--add-declarations', action='store_true',
                                help='Add encoding declarations to files without them')
    parser_encoding.add_argument('--convert-to-utf8', action='store_true',
                                help='Convert files to UTF-8 encoding')
    parser_encoding.add_argument('--dry-run', action='store_true',
                                help='Preview changes without modifying files')
    parser_encoding.add_argument('--no-backup', action='store_true',
                                help='Do not create backups when converting files')
    
    # Estimate command
    parser_estimate = subparsers.add_parser(
        'estimate',
        help='Estimate effort required for migration',
        description='Analyze codebase and provide detailed estimates for time, cost, and resources needed for Python 2 to 3 migration'
    )
    parser_estimate.add_argument('path', help='File or directory to analyze')
    parser_estimate.add_argument('--format', choices=['text', 'json', 'csv'], 
                                default='text',
                                help='Output format (default: text)')
    parser_estimate.add_argument('-o', '--output',
                                help='Save report to file (default: print to console)')
    
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
    
    # Health command
    parser_health = subparsers.add_parser(
        'health',
        help='Monitor migration health',
        description='Analyze and report on overall migration health with actionable recommendations'
    )
    parser_health.add_argument('path', nargs='?', default='.',
                              help='Project path (default: current directory)')
    parser_health.add_argument('-o', '--output',
                              help='Save JSON report to file')
    parser_health.add_argument('-v', '--verbose', action='store_true',
                              help='Show detailed recommendations for each dimension')
    parser_health.add_argument('--no-history', action='store_true',
                              help='Do not save to history')
    parser_health.add_argument('--trend', type=int, metavar='DAYS',
                              help='Show trend analysis for last N days')
    
    # Lint command
    parser_lint = subparsers.add_parser(
        'lint',
        help='Run Python linters on migrated code',
        description='Integrate popular linters (pylint, flake8, mypy, black) for comprehensive code quality checking'
    )
    parser_lint.add_argument('target', nargs='?', default='.',
                            help='Path to lint (file or directory, default: current directory)')
    parser_lint.add_argument('--linters', nargs='+',
                            choices=['pylint', 'flake8', 'mypy', 'black'],
                            help='Specific linters to run (default: all available)')
    parser_lint.add_argument('-o', '--output',
                            help='Save report to file')
    parser_lint.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                            help='Output format (default: text)')
    
    # Recipe command
    parser_recipe = subparsers.add_parser(
        'recipe',
        help='Manage migration recipes/templates',
        description='Save, load, and share migration recipes for different project types (Django, Flask, CLI, etc.)'
    )
    parser_recipe.add_argument('--recipes-dir', help='Custom recipes directory')
    
    recipe_subparsers = parser_recipe.add_subparsers(dest='recipe_action', help='Recipe actions')
    
    # Recipe list
    parser_recipe_list = recipe_subparsers.add_parser('list', help='List all available recipes')
    
    # Recipe show
    parser_recipe_show = recipe_subparsers.add_parser('show', help='Show detailed information about a recipe')
    parser_recipe_show.add_argument('name', help='Recipe name')
    
    # Recipe apply
    parser_recipe_apply = recipe_subparsers.add_parser('apply', help='Apply a recipe to a project')
    parser_recipe_apply.add_argument('name', help='Recipe name')
    parser_recipe_apply.add_argument('-t', '--target', default='.', help='Target directory (default: current directory)')
    
    # Recipe create
    parser_recipe_create = recipe_subparsers.add_parser('create', help='Create a new recipe from current config')
    parser_recipe_create.add_argument('name', help='Recipe name')
    parser_recipe_create.add_argument('-d', '--description', required=True, help='Recipe description')
    parser_recipe_create.add_argument('-c', '--config-file', help='Configuration file to include in recipe')
    
    # Recipe export
    parser_recipe_export = recipe_subparsers.add_parser('export', help='Export a recipe to a file')
    parser_recipe_export.add_argument('name', help='Recipe name')
    parser_recipe_export.add_argument('-o', '--output', help='Output file path')
    
    # Recipe import
    parser_recipe_import = recipe_subparsers.add_parser('import', help='Import a recipe from a file')
    parser_recipe_import.add_argument('file', help='Recipe file to import')
    parser_recipe_import.add_argument('--force', action='store_true', help='Overwrite existing recipe')
    
    # Recipe delete
    parser_recipe_delete = recipe_subparsers.add_parser('delete', help='Delete a recipe')
    parser_recipe_delete.add_argument('name', help='Recipe name')
    
    # State tracking command
    parser_state = subparsers.add_parser(
        'state',
        help='Track migration state of individual files',
        description='Manage migration state tracking for coordinating team work and tracking file-level progress'
    )
    parser_state.add_argument('--project-root', help='Project root directory (default: current directory)')
    
    state_subparsers = parser_state.add_subparsers(dest='state_action', help='State tracking actions')
    
    # State init
    parser_state_init = state_subparsers.add_parser('init', help='Initialize state tracking for the project')
    parser_state_init.add_argument('--scan-dir', help='Directory to scan for Python files (default: project root)')
    parser_state_init.add_argument('--force', action='store_true', help='Reinitialize even if already initialized')
    
    # State list
    parser_state_list = state_subparsers.add_parser('list', help='List files and their migration states')
    parser_state_list.add_argument('--filter-state', help='Filter by state (pending, in_progress, migrated, verified, tested, done)')
    parser_state_list.add_argument('--locked', action='store_true', help='Show only locked files')
    parser_state_list.add_argument('--owner', help='Filter by owner')
    
    # State set
    parser_state_set = state_subparsers.add_parser('set', help='Set the migration state for a file')
    parser_state_set.add_argument('file', help='File path')
    parser_state_set.add_argument('state', help='New state (pending, in_progress, migrated, verified, tested, done, skipped)')
    parser_state_set.add_argument('--notes', help='Notes about the state change')
    parser_state_set.add_argument('--user', help='User making the change')
    
    # State lock
    parser_state_lock = state_subparsers.add_parser('lock', help='Lock a file for exclusive editing')
    parser_state_lock.add_argument('file', help='File path')
    parser_state_lock.add_argument('--owner', help='Owner of the lock (default: current user@hostname)')
    
    # State unlock
    parser_state_unlock = state_subparsers.add_parser('unlock', help='Unlock a file')
    parser_state_unlock.add_argument('file', help='File path')
    parser_state_unlock.add_argument('--owner', help='Owner requesting unlock')
    parser_state_unlock.add_argument('--force', action='store_true', help='Force unlock regardless of owner')
    
    # State stats
    parser_state_stats = state_subparsers.add_parser('stats', help='Show migration state statistics')
    
    # State reset
    parser_state_reset = state_subparsers.add_parser('reset', help='Reset a file to pending state')
    parser_state_reset.add_argument('file', help='File path')
    
    # State export
    parser_state_export = state_subparsers.add_parser('export', help='Export state to a file')
    parser_state_export.add_argument('-o', '--output', help='Output file path')
    
    # State import
    parser_state_import = state_subparsers.add_parser('import', help='Import state from a file')
    parser_state_import.add_argument('file', help='File to import from')
    parser_state_import.add_argument('--merge', action='store_true', help='Merge with existing state instead of replacing')
    
    # Venv command
    parser_venv = subparsers.add_parser(
        'venv',
        help='Manage Python 3 virtual environments',
        description='Create and manage isolated Python 3 environments for testing migrated code'
    )
    
    venv_subparsers = parser_venv.add_subparsers(dest='venv_action', help='Virtual environment actions')
    
    # Venv create
    parser_venv_create = venv_subparsers.add_parser('create', help='Create a new virtual environment')
    parser_venv_create.add_argument('name', help='Name of the virtual environment')
    parser_venv_create.add_argument('--python', help='Python version to use (e.g., 3.8, 3.9, 3.10)')
    parser_venv_create.add_argument('--system-site-packages', action='store_true',
                                   help='Give access to system site-packages')
    
    # Venv list
    parser_venv_list = venv_subparsers.add_parser('list', help='List all virtual environments')
    
    # Venv remove
    parser_venv_remove = venv_subparsers.add_parser('remove', help='Remove a virtual environment')
    parser_venv_remove.add_argument('name', help='Name of the virtual environment')
    parser_venv_remove.add_argument('--force', action='store_true', help='Force removal without confirmation')
    
    # Venv install
    parser_venv_install = venv_subparsers.add_parser('install', help='Install packages into a virtual environment')
    parser_venv_install.add_argument('name', help='Name of the virtual environment')
    parser_venv_install.add_argument('-r', '--requirements', help='Requirements file to install')
    parser_venv_install.add_argument('-p', '--package', help='Single package to install')
    
    # Venv run
    parser_venv_run = venv_subparsers.add_parser('run', help='Run a command in a virtual environment')
    parser_venv_run.add_argument('name', help='Name of the virtual environment')
    parser_venv_run.add_argument('command', nargs='+', help='Command to run')
    
    # Venv test
    parser_venv_test = venv_subparsers.add_parser('test', help='Run tests in a virtual environment')
    parser_venv_test.add_argument('name', help='Name of the virtual environment')
    parser_venv_test.add_argument('--test-path', help='Path to tests (default: tests)')
    
    # Venv info
    parser_venv_info = venv_subparsers.add_parser('info', help='Show detailed information about a virtual environment')
    parser_venv_info.add_argument('name', help='Name of the virtual environment')
    
    # Venv activate
    parser_venv_activate = venv_subparsers.add_parser('activate', help='Show activation command for a virtual environment')
    parser_venv_activate.add_argument('name', help='Name of the virtual environment')
    
    # Journal command
    parser_journal = subparsers.add_parser(
        'journal',
        help='Track notes and decisions during migration',
        description='Document migration decisions, track issues, and create a knowledge base for your team'
    )
    parser_journal.add_argument('--journal-path', default='.migration_journal.json',
                               help='Path to journal file (default: .migration_journal.json)')
    
    journal_subparsers = parser_journal.add_subparsers(dest='journal_action', help='Journal actions')
    
    # Journal add
    parser_journal_add = journal_subparsers.add_parser('add', help='Add a new journal entry')
    parser_journal_add.add_argument('content', help='Entry content')
    parser_journal_add.add_argument('--tags', nargs='+', help='Tags for the entry')
    parser_journal_add.add_argument('--category', 
                                   choices=['decision', 'issue', 'solution', 'insight', 'todo', 'question', 'general'],
                                   default='general', help='Entry category')
    parser_journal_add.add_argument('--files', nargs='+', help='Related files')
    parser_journal_add.add_argument('--author', help='Entry author')
    
    # Journal list
    parser_journal_list = journal_subparsers.add_parser('list', help='List journal entries')
    parser_journal_list.add_argument('--search', help='Search term')
    parser_journal_list.add_argument('--tags', nargs='+', help='Filter by tags')
    parser_journal_list.add_argument('--category', help='Filter by category')
    parser_journal_list.add_argument('--author', help='Filter by author')
    parser_journal_list.add_argument('--files', nargs='+', help='Filter by related files')
    parser_journal_list.add_argument('--limit', type=int, help='Limit number of results')
    
    # Journal show
    parser_journal_show = journal_subparsers.add_parser('show', help='Show a specific entry')
    parser_journal_show.add_argument('entry_id', help='Entry ID')
    
    # Journal stats
    parser_journal_stats = journal_subparsers.add_parser('stats', help='Show journal statistics')
    
    # Journal export
    parser_journal_export = journal_subparsers.add_parser('export', help='Export journal entries')
    parser_journal_export.add_argument('output', help='Output file path')
    parser_journal_export.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                                      help='Export format')
    parser_journal_export.add_argument('--category', help='Filter by category')
    parser_journal_export.add_argument('--tags', nargs='+', help='Filter by tags')
    
    # Journal import
    parser_journal_import = journal_subparsers.add_parser('import', help='Import journal entries')
    parser_journal_import.add_argument('input', help='Input JSON file path')
    
    # Journal delete
    parser_journal_delete = journal_subparsers.add_parser('delete', help='Delete a journal entry')
    parser_journal_delete.add_argument('entry_id', help='Entry ID to delete')
    parser_journal_delete.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # Freeze command
    parser_freeze = subparsers.add_parser(
        'freeze',
        help='Prevent Python 2 code from being re-introduced',
        description='Freeze Guard - Mark migrated code as Python 3 only and prevent Python 2 patterns from being re-introduced'
    )
    parser_freeze.add_argument('--config', default='.freeze-guard.json',
                               help='Path to freeze guard config file (default: .freeze-guard.json)')
    
    freeze_subparsers = parser_freeze.add_subparsers(dest='freeze_action', help='Freeze guard actions')
    
    # Freeze check
    parser_freeze_check = freeze_subparsers.add_parser('check', help='Check files for Python 2 patterns')
    parser_freeze_check.add_argument('paths', nargs='*', help='Files or directories to check')
    parser_freeze_check.add_argument('--staged', action='store_true', help='Check git staged files only')
    parser_freeze_check.add_argument('--frozen-only', action='store_true', help='Check frozen files only')
    parser_freeze_check.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    # Freeze mark
    parser_freeze_mark = freeze_subparsers.add_parser('mark', help='Mark paths as frozen (Python 3 only)')
    parser_freeze_mark.add_argument('paths', nargs='+', help='Paths to mark as frozen')
    
    # Freeze unmark
    parser_freeze_unmark = freeze_subparsers.add_parser('unmark', help='Unmark frozen paths')
    parser_freeze_unmark.add_argument('paths', nargs='+', help='Paths to unmark')
    
    # Freeze status
    parser_freeze_status = freeze_subparsers.add_parser('status', help='Show frozen paths status')
    parser_freeze_status.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Freeze install-hook
    parser_freeze_hook = freeze_subparsers.add_parser('install-hook', help='Install git pre-commit hook')
    
    # Pre-commit hooks command
    parser_precommit = subparsers.add_parser(
        'precommit',
        help='Manage pre-commit hooks for Python 3 validation',
        description='Install and manage pre-commit hooks that prevent Python 2 code from being committed'
    )
    parser_precommit.add_argument('--repo-root', help='Repository root directory (default: current directory)')
    
    precommit_subparsers = parser_precommit.add_subparsers(dest='precommit_action', help='Pre-commit actions')
    
    # Precommit install
    parser_precommit_install = precommit_subparsers.add_parser('install', help='Install pre-commit hooks')
    parser_precommit_install.add_argument('--mode', choices=['strict', 'normal', 'lenient'], default='normal',
                                         help='Validation strictness (default: normal)')
    parser_precommit_install.add_argument('--files-pattern', default='\\.py$',
                                         help='Regex pattern for files to check (default: \\.py$)')
    parser_precommit_install.add_argument('--exclude-pattern', default='',
                                         help='Regex pattern for files to exclude')
    parser_precommit_install.add_argument('--force', action='store_true',
                                         help='Overwrite existing configuration')
    
    # Precommit uninstall
    parser_precommit_uninstall = precommit_subparsers.add_parser('uninstall', help='Uninstall pre-commit hooks')
    
    # Precommit status
    parser_precommit_status = precommit_subparsers.add_parser('status', help='Check pre-commit hook status')
    
    # Precommit test
    parser_precommit_test = precommit_subparsers.add_parser('test', help='Test pre-commit hooks')
    parser_precommit_test.add_argument('--test-file', help='Specific file to test')
    
    # Completion command
    parser_completion = subparsers.add_parser(
        'completion',
        help='Manage shell completions for py2to3',
        description='Generate, install, and manage shell completions for bash, zsh, and fish'
    )
    
    completion_subparsers = parser_completion.add_subparsers(dest='completion_action', help='Completion actions')
    
    # Completion generate
    parser_completion_generate = completion_subparsers.add_parser('generate', help='Generate completion script')
    parser_completion_generate.add_argument('shell', nargs='?', choices=['bash', 'zsh', 'fish'], 
                                           help='Shell type (auto-detected if not specified)')
    parser_completion_generate.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    # Completion install
    parser_completion_install = completion_subparsers.add_parser('install', help='Install completions')
    parser_completion_install.add_argument('shell', nargs='?', choices=['bash', 'zsh', 'fish'],
                                          help='Shell type (auto-detected if not specified)')
    
    # Completion uninstall
    parser_completion_uninstall = completion_subparsers.add_parser('uninstall', help='Uninstall completions')
    parser_completion_uninstall.add_argument('shell', nargs='?', choices=['bash', 'zsh', 'fish'],
                                            help='Shell type (auto-detected if not specified)')
    
    # Completion status
    parser_completion_status = completion_subparsers.add_parser('status', help='Check completion status')
    
    # Rollback command
    parser_rollback = subparsers.add_parser(
        'rollback',
        help='Rollback migration operations',
        description='Quickly undo migration operations using operation history and backups'
    )
    
    rollback_subparsers = parser_rollback.add_subparsers(dest='rollback_action', help='Rollback actions')
    
    # Rollback undo
    parser_rollback_undo = rollback_subparsers.add_parser('undo', help='Rollback the last operation or a specific operation')
    parser_rollback_undo.add_argument('--id', help='Specific operation ID to rollback (default: last operation)')
    parser_rollback_undo.add_argument('-n', '--dry-run', action='store_true', help='Preview rollback without making changes')
    parser_rollback_undo.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    parser_rollback_undo.add_argument('--force', action='store_true', help='Force rollback even if some backups are missing')
    parser_rollback_undo.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
    
    # Rollback list
    parser_rollback_list = rollback_subparsers.add_parser('list', help='List all operations in history')
    parser_rollback_list.add_argument('--all', action='store_true', help='Include rolled back operations')
    parser_rollback_list.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
    
    # Rollback preview
    parser_rollback_preview = rollback_subparsers.add_parser('preview', help='Preview what would be rolled back')
    parser_rollback_preview.add_argument('--id', help='Specific operation ID to preview (default: last operation)')
    
    # Rollback stats
    parser_rollback_stats = rollback_subparsers.add_parser('stats', help='Show rollback statistics')
    parser_rollback_stats.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Rollback clear
    parser_rollback_clear = rollback_subparsers.add_parser('clear', help='Clear operation history')
    parser_rollback_clear.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')
    parser_rollback_clear.add_argument('--keep', type=int, help='Number of recent operations to keep')
    
    # Export command
    parser_export = subparsers.add_parser(
        'export',
        help='Export migration package',
        description='Package migration configuration, state, and learnings for sharing across teams and projects'
    )
    
    export_subparsers = parser_export.add_subparsers(dest='export_action', help='Export actions')
    
    # Export create
    parser_export_create = export_subparsers.add_parser('create', help='Create a migration package')
    parser_export_create.add_argument('path', nargs='?', default='.', help='Project path to export (default: current directory)')
    parser_export_create.add_argument('-o', '--output', help='Output file path (default: migration_export_TIMESTAMP.tar.gz)')
    parser_export_create.add_argument('--config', action='store_true', default=True, help='Include configuration files (default: True)')
    parser_export_create.add_argument('--no-config', action='store_false', dest='config', help='Exclude configuration files')
    parser_export_create.add_argument('--recipes', action='store_true', default=True, help='Include custom recipes (default: True)')
    parser_export_create.add_argument('--no-recipes', action='store_false', dest='recipes', help='Exclude custom recipes')
    parser_export_create.add_argument('--state', action='store_true', default=True, help='Include migration state (default: True)')
    parser_export_create.add_argument('--no-state', action='store_false', dest='state', help='Exclude migration state')
    parser_export_create.add_argument('--journal', action='store_true', default=True, help='Include journal entries (default: True)')
    parser_export_create.add_argument('--no-journal', action='store_false', dest='journal', help='Exclude journal entries')
    parser_export_create.add_argument('--stats', action='store_true', default=True, help='Include statistics (default: True)')
    parser_export_create.add_argument('--no-stats', action='store_false', dest='stats', help='Exclude statistics')
    parser_export_create.add_argument('--backups', action='store_true', help='Include backup files (default: False)')
    parser_export_create.add_argument('--backup-pattern', help='Pattern to filter backups (if including backups)')
    parser_export_create.add_argument('-d', '--description', help='Package description')
    parser_export_create.add_argument('-t', '--tags', help='Comma-separated tags for the package')
    
    # Export list
    parser_export_list = export_subparsers.add_parser('list', help='List available migration packages')
    parser_export_list.add_argument('-d', '--directory', help='Directory to search for packages (default: current directory)')
    
    # Import command
    parser_import = subparsers.add_parser(
        'import',
        help='Import migration package',
        description='Import migration configuration and state from a shared package'
    )
    parser_import.add_argument('package', help='Path to migration package file')
    parser_import.add_argument('path', nargs='?', default='.', help='Target project path (default: current directory)')
    parser_import.add_argument('--config', action='store_true', default=True, help='Import configuration files (default: True)')
    parser_import.add_argument('--no-config', action='store_false', dest='config', help='Skip configuration files')
    parser_import.add_argument('--recipes', action='store_true', default=True, help='Import custom recipes (default: True)')
    parser_import.add_argument('--no-recipes', action='store_false', dest='recipes', help='Skip custom recipes')
    parser_import.add_argument('--state', action='store_true', default=True, help='Import migration state (default: True)')
    parser_import.add_argument('--no-state', action='store_false', dest='state', help='Skip migration state')
    parser_import.add_argument('--journal', action='store_true', default=True, help='Import journal entries (default: True)')
    parser_import.add_argument('--no-journal', action='store_false', dest='journal', help='Skip journal entries')
    parser_import.add_argument('--stats', action='store_true', default=True, help='Import statistics (default: True)')
    parser_import.add_argument('--no-stats', action='store_false', dest='stats', help='Skip statistics')
    parser_import.add_argument('--backups', action='store_true', help='Import backup files (default: False)')
    parser_import.add_argument('--merge', action='store_true', default=True, help='Merge with existing data (default: True)')
    parser_import.add_argument('--overwrite', action='store_false', dest='merge', help='Overwrite existing data')
    parser_import.add_argument('-n', '--dry-run', action='store_true', help='Preview import without making changes')
    
    # Report Card command
    parser_report_card = subparsers.add_parser(
        'report-card',
        help='Generate migration quality assessment',
        description='Generate a comprehensive quality report card with grades and recommendations'
    )
    parser_report_card.add_argument('path', nargs='?', default='.', help='Project path to assess (default: current directory)')
    parser_report_card.add_argument('-o', '--output', help='Output file path (default: print to stdout)')
    parser_report_card.add_argument('-f', '--format', 
                                    choices=['text', 'html', 'json', 'markdown'],
                                    default='text',
                                    help='Output format (default: text)')
    
    # Metadata command
    parser_metadata = subparsers.add_parser(
        'metadata',
        help='Update project metadata for Python 3',
        description='Automatically update setup.py, pyproject.toml, tox.ini, CI configs, and other metadata files'
    )
    parser_metadata.add_argument('path', nargs='?', default='.', help='Project directory to update (default: current directory)')
    parser_metadata.add_argument('--min-version', default='3.6', help='Minimum Python 3 version to support (default: 3.6)')
    parser_metadata.add_argument('--max-version', default='3.12', help='Maximum Python 3 version to support (default: 3.12)')
    parser_metadata.add_argument('-n', '--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser_metadata.add_argument('--json', action='store_true', help='Output results as JSON')
    
    # Changelog command
    parser_changelog = subparsers.add_parser(
        'changelog',
        help='Generate migration changelog',
        description='Automatically generate a changelog from migration activities including git commits, journal entries, and statistics'
    )
    parser_changelog.add_argument('path', nargs='?', default='.', help='Project directory (default: current directory)')
    parser_changelog.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser_changelog.add_argument('--since', help='Start date (ISO format or relative like "30 days ago")')
    parser_changelog.add_argument('--until', help='End date (ISO format or "now")')
    parser_changelog.add_argument('--version', default='Unreleased', help='Version string for changelog entry (default: Unreleased)')
    parser_changelog.add_argument('--format', choices=['keepachangelog', 'simple'], default='keepachangelog', help='Changelog format style (default: keepachangelog)')
    parser_changelog.add_argument('--append', action='store_true', help='Append to existing changelog file')
    
    # Coverage command
    parser_coverage = subparsers.add_parser(
        'coverage',
        help='Track test coverage during migration',
        description='Monitor test coverage for migrated code to identify risky changes and track coverage trends'
    )
    coverage_subparsers = parser_coverage.add_subparsers(dest='coverage_action', help='Coverage actions')
    
    parser_coverage_collect = coverage_subparsers.add_parser('collect', help='Collect coverage data by running tests')
    parser_coverage_collect.add_argument('--path', default='.', help='Project directory (default: current directory)')
    parser_coverage_collect.add_argument('--description', help='Description for this coverage snapshot')
    parser_coverage_collect.add_argument('--test-command', help='Custom test command (default: auto-detect)')
    
    parser_coverage_report = coverage_subparsers.add_parser('report', help='Generate coverage report')
    parser_coverage_report.add_argument('--path', default='.', help='Project directory (default: current directory)')
    parser_coverage_report.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    parser_coverage_trend = coverage_subparsers.add_parser('trend', help='Show coverage trends over time')
    parser_coverage_trend.add_argument('--path', default='.', help='Project directory (default: current directory)')
    
    parser_coverage_risky = coverage_subparsers.add_parser('risky', help='Identify risky migrations (low coverage)')
    parser_coverage_risky.add_argument('--path', default='.', help='Project directory (default: current directory)')
    parser_coverage_risky.add_argument('--threshold', type=float, default=50.0, help='Coverage threshold for risk (default: 50%%)')
    
    parser_coverage_clear = coverage_subparsers.add_parser('clear', help='Clear coverage snapshots')
    parser_coverage_clear.add_argument('--path', default='.', help='Project directory (default: current directory)')
    
    # Readiness command
    parser_readiness = subparsers.add_parser(
        'readiness',
        help='🎯 Assess migration readiness and safety score',
        description='Comprehensive assessment tool that evaluates project readiness for migration and production deployment'
    )
    parser_readiness.add_argument(
        'readiness_type',
        choices=['pre', 'post', 'both'],
        help='Assessment type: pre-migration readiness, post-migration production readiness, or both'
    )
    parser_readiness.add_argument(
        '--path',
        default='.',
        help='Root path of project to assess (default: current directory)'
    )
    parser_readiness.add_argument(
        '-o', '--output',
        help='Save report to JSON file'
    )
    
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
    if args.command == 'wizard':
        return command_wizard(args)
    elif args.command == 'check':
        return command_check(args)
    elif args.command == 'version-check':
        return command_version_check(args)
    elif args.command == 'convert':
        return command_convert(args)
    elif args.command == 'preflight':
        return command_preflight(args)
    elif args.command == 'fix':
        return command_fix(args)
    elif args.command == 'interactive':
        return command_interactive(args)
    elif args.command == 'report':
        return command_report(args)
    elif args.command == 'review':
        return command_review(args)
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
    elif args.command == 'graph':
        return command_graph(args)
    elif args.command == 'watch':
        return command_watch(args)
    elif args.command == 'quality':
        return command_quality(args)
    elif args.command == 'bench':
        return command_bench(args)
    elif args.command == 'docs':
        return command_docs(args)
    elif args.command == 'status':
        return command_status(args)
    elif args.command == 'search':
        return command_search(args)
    elif args.command == 'security':
        return command_security(args)
    elif args.command == 'imports':
        return command_imports(args)
    elif args.command == 'modernize':
        return command_modernize(args)
    elif args.command == 'typehints':
        return command_typehints(args)
    elif args.command == 'validate':
        return command_validate(args)
    elif args.command == 'encoding':
        return command_encoding(args)
    elif args.command == 'estimate':
        return command_estimate(args)
    elif args.command == 'dashboard':
        return command_dashboard(args)
    elif args.command == 'health':
        return command_health(args)
    elif args.command == 'lint':
        return command_lint(args)
    elif args.command == 'recipe':
        return command_recipe(args)
    elif args.command == 'state':
        return command_state(args)
    elif args.command == 'journal':
        return command_journal(args)
    elif args.command == 'venv':
        return command_venv(args)
    elif args.command == 'freeze':
        return command_freeze(args)
    elif args.command == 'precommit':
        return command_precommit(args)
    elif args.command == 'completion':
        return command_completion(args)
    elif args.command == 'rollback':
        return command_rollback(args)
    elif args.command == 'export':
        return command_export(args)
    elif args.command == 'import':
        return command_import(args)
    elif args.command == 'report-card':
        return command_report_card(args)
    elif args.command == 'metadata':
        return command_metadata(args)
    elif args.command == 'changelog':
        return command_changelog(args)
    elif args.command == 'coverage':
        return command_coverage(args)
    elif args.command == 'readiness':
        return command_readiness(args)
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
