#!/usr/bin/env python3
"""
Example API client for py2to3 Migration Toolkit REST API

This script demonstrates how to use the REST API to:
1. Check the server health
2. Perform a compatibility check
3. Get migration statistics
4. Apply fixes (with backup)
5. Generate a report

Usage:
    # Start the API server first
    ./py2to3 api

    # In another terminal, run this client
    python examples/api_client_example.py
"""

import requests
import json
import sys
from pathlib import Path

# API configuration
API_BASE = "http://localhost:5000/api"
TEST_PATH = "."  # Change this to your project path


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def health_check():
    """Check if the API server is running."""
    print_section("Health Check")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        result = response.json()
        
        if result.get('success'):
            print("✅ API Server is healthy!")
            print(f"   Version: {result.get('api_version')}")
            print(f"   Status: {result['data'].get('status')}")
            return True
        else:
            print("❌ API Server returned an error")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("   Make sure the server is running: ./py2to3 api")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_api_info():
    """Get API information and available endpoints."""
    print_section("API Information")
    
    try:
        response = requests.get(f"{API_BASE}/info", timeout=5)
        result = response.json()
        
        if result.get('success'):
            print(f"API Version: {result['data'].get('version')}")
            print("\nAvailable Endpoints:")
            for endpoint, description in result['data'].get('endpoints', {}).items():
                print(f"  {endpoint:30} - {description}")
            return True
        else:
            print(f"Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False


def check_compatibility(path):
    """Run a compatibility check."""
    print_section(f"Compatibility Check: {path}")
    
    try:
        response = requests.post(
            f"{API_BASE}/check",
            json={"path": path},
            timeout=30
        )
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            print(f"✅ Check completed successfully!")
            print(f"   Path: {data.get('path')}")
            print(f"   Issues Found: {data.get('issues_found', 0)}")
            
            if data.get('issues'):
                print(f"\n   Sample Issues:")
                for issue in data['issues'][:3]:  # Show first 3 issues
                    print(f"     - {issue.get('file')}:{issue.get('line')}")
                    print(f"       {issue.get('category')}: {issue.get('description')}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_statistics(path):
    """Get migration statistics."""
    print_section(f"Migration Statistics: {path}")
    
    try:
        response = requests.get(
            f"{API_BASE}/stats",
            params={"path": path},
            timeout=30
        )
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            print("✅ Statistics retrieved successfully!")
            print(f"   Total Files: {data.get('total_files', 0)}")
            print(f"   Total Lines: {data.get('total_lines', 0)}")
            print(f"   Issues Found: {data.get('issues_found', 0)}")
            
            if data.get('issues_by_severity'):
                print("\n   Issues by Severity:")
                for severity, count in data['issues_by_severity'].items():
                    print(f"     {severity}: {count}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def apply_fixes(path, backup=True, dry_run=True):
    """Apply migration fixes."""
    mode = "DRY RUN" if dry_run else "APPLY"
    print_section(f"Apply Fixes ({mode}): {path}")
    
    try:
        response = requests.post(
            f"{API_BASE}/fix",
            json={
                "path": path,
                "backup": backup,
                "dry_run": dry_run
            },
            timeout=60
        )
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            print(f"✅ Fix operation completed!")
            print(f"   Path: {data.get('path')}")
            print(f"   Fixes Applied: {data.get('fixes_applied', 0)}")
            print(f"   Dry Run: {data.get('dry_run')}")
            
            if data.get('backup_location'):
                print(f"   Backup Location: {data['backup_location']}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def generate_report(path, format_type='json'):
    """Generate a migration report."""
    print_section(f"Generate Report ({format_type.upper()}): {path}")
    
    try:
        response = requests.post(
            f"{API_BASE}/report",
            json={
                "path": path,
                "format": format_type
            },
            timeout=60
        )
        
        if format_type == 'html':
            # For HTML, save the file
            if response.status_code == 200:
                output_file = f"migration_report_{Path(path).name}.html"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"✅ HTML report saved to: {output_file}")
                return True
            else:
                print(f"❌ Error generating HTML report")
                return False
        else:
            # For JSON/text, parse the response
            result = response.json()
            
            if result.get('success'):
                print("✅ Report generated successfully!")
                
                # Save to file
                output_file = f"migration_report_{Path(path).name}.json"
                with open(output_file, 'w') as f:
                    json.dump(result['data'], f, indent=2)
                print(f"   Report saved to: {output_file}")
                
                return True
            else:
                print(f"❌ Error: {result.get('error')}")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run the example API client."""
    print("\n" + "=" * 60)
    print("  py2to3 Migration Toolkit - API Client Example")
    print("=" * 60)
    print(f"\nTarget: {TEST_PATH}")
    print(f"API Base: {API_BASE}")
    
    # 1. Health check
    if not health_check():
        print("\n❌ Cannot continue without a healthy API server")
        sys.exit(1)
    
    # 2. Get API info
    get_api_info()
    
    # 3. Check compatibility
    check_compatibility(TEST_PATH)
    
    # 4. Get statistics
    get_statistics(TEST_PATH)
    
    # 5. Apply fixes (dry run only for safety)
    apply_fixes(TEST_PATH, backup=True, dry_run=True)
    
    # 6. Generate report
    generate_report(TEST_PATH, format_type='json')
    
    print_section("Example Completed")
    print("✅ All API operations completed successfully!")
    print("\n💡 Tips:")
    print("   - Modify TEST_PATH to check your own project")
    print("   - Set dry_run=False in apply_fixes() to apply real changes")
    print("   - Use format_type='html' in generate_report() for HTML output")
    print("   - See API_SERVER_GUIDE.md for complete API documentation")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
