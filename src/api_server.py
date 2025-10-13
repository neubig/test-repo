#!/usr/bin/env python3
"""
REST API Server for py2to3 Migration Toolkit

Provides a RESTful API interface to the migration toolkit, enabling programmatic
access to all migration features. Perfect for CI/CD integration, web dashboards,
and third-party tool integration.

Usage:
    python api_server.py
    python api_server.py --port 5000 --host 0.0.0.0
    ./py2to3 api --port 8080
"""

import argparse
import json
import os
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
except ImportError:
    print("Error: Flask is required for the API server.")
    print("Install it with: pip install flask flask-cors")
    sys.exit(1)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from error_handlers import handle_api_errors

app = Flask(__name__)
CORS(app)  # Enable CORS for web dashboard integration

# API version
API_VERSION = "1.0.0"


def create_response(data: Any = None, error: str = None, status_code: int = 200) -> tuple:
    """Create a standardized API response."""
    response = {
        "success": error is None,
        "timestamp": datetime.utcnow().isoformat(),
        "api_version": API_VERSION
    }
    
    if error:
        response["error"] = error
    if data is not None:
        response["data"] = data
    
    return jsonify(response), status_code


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return create_response({
        "status": "healthy",
        "version": API_VERSION,
        "toolkit": "py2to3 Migration Toolkit"
    })


@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and available endpoints."""
    endpoints = {
        "/api/health": "Health check",
        "/api/info": "API information",
        "/api/check": "Run Python 3 compatibility check",
        "/api/fix": "Apply migration fixes",
        "/api/report": "Generate migration report",
        "/api/stats": "Get migration statistics",
        "/api/backup/list": "List backups",
        "/api/backup/create": "Create backup",
        "/api/backup/restore": "Restore from backup",
        "/api/config": "Get or set configuration",
        "/api/status": "Get migration status",
        "/api/deps": "Analyze dependencies",
        "/api/security": "Run security audit",
        "/api/quality": "Check code quality",
        "/api/risk": "Analyze migration risks"
    }
    
    return create_response({
        "version": API_VERSION,
        "endpoints": endpoints,
        "methods": ["GET", "POST"],
        "documentation": "See API_SERVER_GUIDE.md for full documentation"
    })


@app.route('/api/check', methods=['POST'])
@handle_api_errors
def check_compatibility():
    """Run Python 3 compatibility check."""
    data = request.get_json() or {}
    path = data.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from verifier import Python3CompatibilityVerifier
    
    verifier = Python3CompatibilityVerifier()
    if os.path.isdir(path):
        verifier.verify_directory(path)
    else:
        verifier.verify_file(path)
    
    issues = [
        {
            "file": issue.file_path,
            "line": issue.line_number,
            "severity": issue.severity,
            "category": issue.category,
            "description": issue.description
        }
        for issue in verifier.issues_found
    ]
    
    return create_response({
        "path": path,
        "issues_found": len(issues),
        "issues": issues,
        "summary": verifier.get_summary()
    })


@app.route('/api/fix', methods=['POST'])
@handle_api_errors
def apply_fixes():
    """Apply migration fixes to code."""
    data = request.get_json() or {}
    path = data.get('path', '.')
    backup = data.get('backup', True)
    dry_run = data.get('dry_run', False)
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from fixer import Python2to3Fixer
    
    backup_dir = None
    if backup:
        backup_dir = os.path.join(tempfile.gettempdir(), 'py2to3_backups')
        os.makedirs(backup_dir, exist_ok=True)
    
    fixer = Python2to3Fixer(backup_dir=backup_dir)
    
    if os.path.isdir(path):
        results = fixer.fix_directory(path)
    else:
        results = fixer.fix_file(path)
    
    return create_response({
        "path": path,
        "fixes_applied": len(fixer.fixes_applied) if not dry_run else 0,
        "dry_run": dry_run,
        "backup_location": backup_dir if backup else None,
        "results": results
    })


@app.route('/api/report', methods=['POST'])
@handle_api_errors
def generate_report():
    """Generate migration report."""
    data = request.get_json() or {}
    format_type = data.get('format', 'json')  # json, html, text
    path = data.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from report_generator import ReportGenerator
    
    generator = ReportGenerator(path)
    
    if format_type == 'html':
        output_file = os.path.join(tempfile.gettempdir(), 'migration_report.html')
        generator.generate_html_report(output_file)
        return send_file(output_file, mimetype='text/html')
    
    elif format_type == 'json':
        report_data = generator.collect_data()
        return create_response(report_data)
    
    else:
        report_text = generator.generate_text_report()
        return create_response({"report": report_text})
    


@app.route('/api/stats', methods=['GET'])
@handle_api_errors
def get_statistics():
    """Get migration statistics."""
    path = request.args.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from stats_tracker import StatsTracker
    
    tracker = StatsTracker(path)
    stats = tracker.collect_stats()
    
    return create_response(stats)
    


@app.route('/api/backup/list', methods=['GET'])
@handle_api_errors
def list_backups():
    """List all available backups."""
    from backup_manager import BackupManager
    
    manager = BackupManager()
    backups = manager.list_backups()
    
    return create_response({
        "backups": backups,
        "total": len(backups)
    })
    


@app.route('/api/backup/create', methods=['POST'])
@handle_api_errors
def create_backup():
    """Create a new backup."""
    data = request.get_json() or {}
    path = data.get('path', '.')
    description = data.get('description', 'API backup')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from backup_manager import BackupManager
    
    manager = BackupManager()
    backup_id = manager.create_backup(path, description)
    
    return create_response({
        "backup_id": backup_id,
        "path": path,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    })
    


@app.route('/api/backup/restore', methods=['POST'])
@handle_api_errors
def restore_backup():
    """Restore from a backup."""
    data = request.get_json() or {}
    backup_id = data.get('backup_id')
    
    if not backup_id:
        return create_response(error="backup_id is required", status_code=400)
    
    from backup_manager import BackupManager
    
    manager = BackupManager()
    result = manager.restore_backup(backup_id)
    
    return create_response(result)
    


@app.route('/api/config', methods=['GET', 'POST'])
@handle_api_errors
def manage_config():
    """Get or set configuration."""
    from config_manager import ConfigManager
    
    manager = ConfigManager()
    
    if request.method == 'GET':
        config = manager.get_config()
        return create_response(config)
    
    else:  # POST
        data = request.get_json() or {}
        for key, value in data.items():
            manager.set_config(key, value)
        
        return create_response({
            "message": "Configuration updated",
            "config": manager.get_config()
        })


@app.route('/api/status', methods=['GET'])
@handle_api_errors
def get_status():
    """Get overall migration status."""
    path = request.args.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from status_reporter import StatusReporter
    
    reporter = StatusReporter(path)
    status = reporter.get_status()
    
    return create_response(status)
    


@app.route('/api/deps', methods=['POST'])
@handle_api_errors
def analyze_dependencies():
    """Analyze dependencies for Python 3 compatibility."""
    data = request.get_json() or {}
    path = data.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from dependency_analyzer import DependencyAnalyzer
    
    analyzer = DependencyAnalyzer(path)
    analyzer.scan_requirements_txt()
    analyzer.scan_setup_py()
    analyzer.scan_imports()
    
    results = analyzer.analyze_compatibility()
    
    return create_response(results)
    


@app.route('/api/security', methods=['POST'])
@handle_api_errors
def security_audit():
    """Run security audit on code."""
    data = request.get_json() or {}
    path = data.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from security_auditor import SecurityAuditor
    
    auditor = SecurityAuditor()
    if os.path.isdir(path):
        auditor.audit_directory(path)
    else:
        auditor.audit_file(path)
    
    issues = [issue.to_dict() for issue in auditor.issues]
    
    return create_response({
        "issues_found": len(issues),
        "issues": issues,
        "stats": dict(auditor.stats)
    })
    


@app.route('/api/quality', methods=['POST'])
@handle_api_errors
def check_quality():
    """Check code quality."""
    data = request.get_json() or {}
    path = data.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from code_quality import CodeQualityChecker
    
    checker = CodeQualityChecker(path)
    results = checker.run_checks()
    
    return create_response(results)
    


@app.route('/api/risk', methods=['POST'])
@handle_api_errors
def analyze_risks():
    """Analyze migration risks."""
    data = request.get_json() or {}
    path = data.get('path', '.')
    
    if not os.path.exists(path):
        return create_response(error=f"Path not found: {path}", status_code=404)
    
    from risk_analyzer import RiskAnalyzer
    
    analyzer = RiskAnalyzer(path)
    risks = analyzer.analyze()
    
    return create_response(risks)
    


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return create_response(error="Endpoint not found", status_code=404)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return create_response(error="Internal server error", status_code=500)


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(
        description='REST API Server for py2to3 Migration Toolkit'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to listen on (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         py2to3 Migration Toolkit - API Server                  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

🚀 Server starting...
   Host: {args.host}
   Port: {args.port}
   API Version: {API_VERSION}

📚 API Documentation:
   Health Check:  http://{args.host}:{args.port}/api/health
   API Info:      http://{args.host}:{args.port}/api/info
   
🔧 Available Endpoints:
   POST /api/check      - Run compatibility check
   POST /api/fix        - Apply migration fixes
   POST /api/report     - Generate reports
   GET  /api/stats      - Get statistics
   POST /api/deps       - Analyze dependencies
   POST /api/security   - Security audit
   POST /api/quality    - Code quality check
   POST /api/risk       - Risk analysis
   GET  /api/backup/list      - List backups
   POST /api/backup/create    - Create backup
   POST /api/backup/restore   - Restore backup
   GET/POST /api/config       - Manage configuration
   GET  /api/status     - Get migration status

🌐 Ready for requests!
    """)
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()
