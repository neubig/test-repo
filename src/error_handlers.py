"""
Common error handling utilities for the py2to3 toolkit.

This module provides reusable error handling patterns to reduce code duplication
across the CLI and API server components.
"""

import functools
import sys
import traceback


def handle_api_errors(func):
    """
    Decorator for Flask route handlers to automatically catch and format exceptions.
    
    This eliminates the need for repetitive try-except blocks in API routes.
    
    Usage:
        @app.route('/api/endpoint')
        @handle_api_errors
        def my_endpoint():
            # Your code here
            return create_response(data)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            from api_server import create_response
            return create_response(error=str(e), status_code=500)
    return wrapper


def handle_cli_error(error, message, args=None, exit_code=None):
    """
    Handle CLI errors with consistent formatting and optional verbose output.
    
    Args:
        error: The exception that was caught
        message: The error message to display to the user
        args: Optional argparse Namespace object with verbose flag
        exit_code: Optional exit code (if provided, will exit the program)
    
    Usage:
        try:
            # Your code here
        except Exception as e:
            handle_cli_error(e, "Operation failed", args)
            return 1
    """
    from cli import print_error
    
    print_error(f"{message}: {error}")
    
    if args and hasattr(args, 'verbose') and args.verbose:
        traceback.print_exc()
    
    if exit_code is not None:
        sys.exit(exit_code)


def print_verbose_error(args):
    """
    Print traceback if verbose mode is enabled.
    
    Args:
        args: argparse Namespace object with verbose flag
    
    Usage:
        try:
            # Your code here
        except Exception as e:
            from cli import print_error
            print_error(f"Operation failed: {e}")
            print_verbose_error(args)
    """
    if args and hasattr(args, 'verbose') and args.verbose:
        traceback.print_exc()
