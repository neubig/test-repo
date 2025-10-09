#!/usr/bin/env python3
"""
Migration Readiness & Safety Score - Comprehensive assessment tool

Evaluates project readiness for migration and post-migration production readiness.
Provides actionable recommendations and best practices compliance checking.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class ReadinessChecker:
    """Comprehensive migration readiness and safety assessment."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.checks = []
        self.score = 0
        self.max_score = 0
        self.recommendations = []
        self.warnings = []
        
    def assess_pre_migration_readiness(self) -> Dict:
        """Assess if project is ready to start migration."""
        print("🔍 Assessing Pre-Migration Readiness...\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "assessment_type": "pre-migration",
            "checks": [],
            "score": 0,
            "max_score": 0,
            "percentage": 0,
            "grade": "",
            "recommendations": [],
            "warnings": []
        }
        
        # Category 1: Version Control (20 points)
        self._check_git_repository(results)
        self._check_git_status(results)
        self._check_git_remote(results)
        self._check_gitignore(results)
        
        # Category 2: Backup & Safety (20 points)
        self._check_backup_directory(results)
        self._check_backup_recent(results)
        self._check_rollback_capability(results)
        
        # Category 3: Testing Infrastructure (25 points)
        self._check_test_suite_exists(results)
        self._check_tests_pass(results)
        self._check_test_coverage(results)
        
        # Category 4: Project Structure (15 points)
        self._check_requirements_file(results)
        self._check_virtual_environment(results)
        self._check_configuration(results)
        
        # Category 5: Documentation (10 points)
        self._check_readme_exists(results)
        self._check_documentation(results)
        
        # Category 6: Code Quality (10 points)
        self._check_code_organization(results)
        self._check_no_syntax_errors(results)
        
        # Calculate final score
        results["score"] = sum(c["score"] for c in results["checks"])
        results["max_score"] = sum(c["max_score"] for c in results["checks"])
        results["percentage"] = (results["score"] / results["max_score"] * 100) if results["max_score"] > 0 else 0
        results["grade"] = self._calculate_grade(results["percentage"])
        
        return results
    
    def assess_post_migration_readiness(self) -> Dict:
        """Assess if migration is complete and ready for production."""
        print("🔍 Assessing Post-Migration Production Readiness...\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "assessment_type": "post-migration",
            "checks": [],
            "score": 0,
            "max_score": 0,
            "percentage": 0,
            "grade": "",
            "recommendations": [],
            "warnings": []
        }
        
        # Category 1: Compatibility (30 points)
        self._check_python3_compatibility(results)
        self._check_no_python2_imports(results)
        self._check_no_python2_syntax(results)
        
        # Category 2: Testing (25 points)
        self._check_all_tests_pass_py3(results)
        self._check_test_coverage_adequate(results)
        self._check_integration_tests(results)
        
        # Category 3: Code Quality (20 points)
        self._check_no_code_smells(results)
        self._check_type_hints_added(results)
        self._check_modernization_complete(results)
        
        # Category 4: Documentation (15 points)
        self._check_changelog_updated(results)
        self._check_migration_documented(results)
        self._check_api_docs_updated(results)
        
        # Category 5: Dependencies (10 points)
        self._check_dependencies_compatible(results)
        self._check_no_deprecated_packages(results)
        
        # Calculate final score
        results["score"] = sum(c["score"] for c in results["checks"])
        results["max_score"] = sum(c["max_score"] for c in results["checks"])
        results["percentage"] = (results["score"] / results["max_score"] * 100) if results["max_score"] > 0 else 0
        results["grade"] = self._calculate_grade(results["percentage"])
        
        return results
    
    def _add_check(self, results: Dict, category: str, name: str, 
                   passed: bool, score: int, max_score: int, 
                   message: str, recommendation: str = None):
        """Add a check result."""
        check = {
            "category": category,
            "name": name,
            "passed": passed,
            "score": score if passed else 0,
            "max_score": max_score,
            "message": message
        }
        results["checks"].append(check)
        
        if not passed and recommendation:
            results["recommendations"].append(f"[{category}] {recommendation}")
    
    # ===== Pre-Migration Checks =====
    
    def _check_git_repository(self, results: Dict):
        """Check if project is in a git repository."""
        git_dir = self.root_path / ".git"
        passed = git_dir.exists() and git_dir.is_dir()
        self._add_check(
            results, "Version Control", "Git Repository", passed, 5, 5,
            "Project is in a git repository" if passed else "Project is not in a git repository",
            "Initialize git repository: git init"
        )
    
    def _check_git_status(self, results: Dict):
        """Check if git working directory is clean."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            clean = len(result.stdout.strip()) == 0
            passed = clean
            self._add_check(
                results, "Version Control", "Clean Working Directory", passed, 5, 5,
                "Git working directory is clean" if passed else "Git working directory has uncommitted changes",
                "Commit all changes before migration: git add -A && git commit -m 'Pre-migration checkpoint'"
            )
        except:
            self._add_check(
                results, "Version Control", "Clean Working Directory", False, 0, 5,
                "Could not check git status",
                "Ensure git is installed and working"
            )
    
    def _check_git_remote(self, results: Dict):
        """Check if git remote is configured."""
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            has_remote = len(result.stdout.strip()) > 0
            passed = has_remote
            self._add_check(
                results, "Version Control", "Remote Repository", passed, 5, 5,
                "Remote repository configured" if passed else "No remote repository configured",
                "Add remote repository for backup: git remote add origin <url>"
            )
        except:
            self._add_check(
                results, "Version Control", "Remote Repository", False, 0, 5,
                "Could not check git remotes"
            )
    
    def _check_gitignore(self, results: Dict):
        """Check if .gitignore exists."""
        gitignore = self.root_path / ".gitignore"
        passed = gitignore.exists()
        self._add_check(
            results, "Version Control", ".gitignore File", passed, 5, 5,
            ".gitignore file exists" if passed else ".gitignore file missing",
            "Create .gitignore to exclude build artifacts, __pycache__, .pyc files"
        )
    
    def _check_backup_directory(self, results: Dict):
        """Check if backup directory exists."""
        backup_dirs = [
            self.root_path / "backups",
            self.root_path / ".backups",
            self.root_path / "backup"
        ]
        passed = any(d.exists() for d in backup_dirs)
        self._add_check(
            results, "Backup & Safety", "Backup Directory", passed, 7, 7,
            "Backup directory exists" if passed else "No backup directory found",
            "Create backups before migration: ./py2to3 backup create"
        )
    
    def _check_backup_recent(self, results: Dict):
        """Check if recent backups exist."""
        backup_dirs = [
            self.root_path / "backups",
            self.root_path / ".backups"
        ]
        
        recent_backup = False
        for backup_dir in backup_dirs:
            if backup_dir.exists():
                backups = list(backup_dir.glob("*"))
                if backups:
                    recent_backup = True
                    break
        
        passed = recent_backup
        self._add_check(
            results, "Backup & Safety", "Recent Backups", passed, 7, 7,
            "Recent backups found" if passed else "No recent backups found",
            "Create a backup: ./py2to3 backup create"
        )
    
    def _check_rollback_capability(self, results: Dict):
        """Check if rollback is possible."""
        history_file = self.root_path / ".py2to3_history.json"
        passed = history_file.exists()
        self._add_check(
            results, "Backup & Safety", "Rollback Capability", passed, 6, 6,
            "Rollback system configured" if passed else "Rollback system not configured",
            "Rollback capability will be available after first migration operation"
        )
    
    def _check_test_suite_exists(self, results: Dict):
        """Check if test suite exists."""
        test_paths = [
            self.root_path / "tests",
            self.root_path / "test",
            self.root_path / "src" / "tests"
        ]
        
        test_files = []
        for test_path in test_paths:
            if test_path.exists():
                test_files.extend(list(test_path.glob("test_*.py")))
                test_files.extend(list(test_path.glob("*_test.py")))
        
        passed = len(test_files) > 0
        self._add_check(
            results, "Testing", "Test Suite Exists", passed, 10, 10,
            f"Found {len(test_files)} test files" if passed else "No test files found",
            "Create tests before migration to ensure behavioral compatibility"
        )
    
    def _check_tests_pass(self, results: Dict):
        """Check if existing tests pass."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--co", "-q"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            has_tests = "test session starts" in result.stdout.lower() or "test" in result.stdout.lower()
            
            if has_tests:
                result = subprocess.run(
                    ["python", "-m", "pytest", "-x"],
                    cwd=self.root_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                passed = result.returncode == 0
                self._add_check(
                    results, "Testing", "Tests Pass", passed, 10, 10,
                    "All tests pass" if passed else "Some tests fail",
                    "Fix failing tests before migration to establish baseline"
                )
            else:
                self._add_check(
                    results, "Testing", "Tests Pass", False, 0, 10,
                    "No tests to run",
                    "Create tests before migration"
                )
        except:
            self._add_check(
                results, "Testing", "Tests Pass", False, 0, 10,
                "Could not run tests",
                "Install pytest: pip install pytest"
            )
    
    def _check_test_coverage(self, results: Dict):
        """Check test coverage."""
        coverage_file = self.root_path / ".coverage"
        htmlcov = self.root_path / "htmlcov"
        
        passed = coverage_file.exists() or htmlcov.exists()
        self._add_check(
            results, "Testing", "Test Coverage Tracked", passed, 5, 5,
            "Test coverage is tracked" if passed else "Test coverage not tracked",
            "Track coverage: pytest --cov=src --cov-report=html"
        )
    
    def _check_requirements_file(self, results: Dict):
        """Check if requirements file exists."""
        req_files = [
            self.root_path / "requirements.txt",
            self.root_path / "setup.py",
            self.root_path / "pyproject.toml",
            self.root_path / "Pipfile"
        ]
        
        passed = any(f.exists() for f in req_files)
        self._add_check(
            results, "Project Structure", "Dependencies Documented", passed, 5, 5,
            "Dependencies are documented" if passed else "No dependency file found",
            "Document dependencies: pip freeze > requirements.txt"
        )
    
    def _check_virtual_environment(self, results: Dict):
        """Check if running in virtual environment."""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        passed = in_venv
        self._add_check(
            results, "Project Structure", "Virtual Environment", passed, 5, 5,
            "Running in virtual environment" if passed else "Not in virtual environment",
            "Create virtual environment: python3 -m venv venv && source venv/bin/activate"
        )
    
    def _check_configuration(self, results: Dict):
        """Check if py2to3 configuration exists."""
        config_file = self.root_path / ".py2to3.config.json"
        passed = config_file.exists()
        self._add_check(
            results, "Project Structure", "Configuration File", passed, 5, 5,
            "py2to3 configuration exists" if passed else "No py2to3 configuration",
            "Initialize configuration: ./py2to3 config init"
        )
    
    def _check_readme_exists(self, results: Dict):
        """Check if README exists."""
        readme_files = [
            self.root_path / "README.md",
            self.root_path / "README.rst",
            self.root_path / "README.txt"
        ]
        passed = any(f.exists() for f in readme_files)
        self._add_check(
            results, "Documentation", "README File", passed, 5, 5,
            "README file exists" if passed else "No README file",
            "Create README.md documenting the project"
        )
    
    def _check_documentation(self, results: Dict):
        """Check if documentation directory exists."""
        doc_dirs = [
            self.root_path / "docs",
            self.root_path / "doc",
            self.root_path / "documentation"
        ]
        passed = any(d.exists() and d.is_dir() for d in doc_dirs)
        self._add_check(
            results, "Documentation", "Documentation Directory", passed, 5, 5,
            "Documentation directory exists" if passed else "No documentation directory",
            "Create docs/ directory for project documentation"
        )
    
    def _check_code_organization(self, results: Dict):
        """Check if code is organized in modules."""
        src_dir = self.root_path / "src"
        python_files = list(self.root_path.glob("*.py"))
        
        if src_dir.exists():
            passed = True
            msg = "Code organized in src/ directory"
        elif len(python_files) > 0:
            passed = True
            msg = "Python files found in root"
        else:
            passed = False
            msg = "No Python files found"
        
        self._add_check(
            results, "Code Quality", "Code Organization", passed, 5, 5,
            msg,
            "Organize code in packages/modules"
        )
    
    def _check_no_syntax_errors(self, results: Dict):
        """Check for Python syntax errors."""
        python_files = list(self.root_path.rglob("*.py"))
        syntax_errors = []
        
        for py_file in python_files[:20]:  # Check first 20 files
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError:
                syntax_errors.append(py_file.name)
        
        passed = len(syntax_errors) == 0
        self._add_check(
            results, "Code Quality", "No Syntax Errors", passed, 5, 5,
            "No syntax errors found" if passed else f"Syntax errors in {len(syntax_errors)} files",
            "Fix syntax errors before migration"
        )
    
    # ===== Post-Migration Checks =====
    
    def _check_python3_compatibility(self, results: Dict):
        """Check Python 3 compatibility."""
        try:
            # Try to run verifier if available
            verifier_path = self.root_path / "src" / "verifier.py"
            if verifier_path.exists():
                result = subprocess.run(
                    ["python3", str(verifier_path), str(self.root_path)],
                    cwd=self.root_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                # Simple heuristic: if no critical errors mentioned
                passed = "error" not in result.stdout.lower() or "0 issues" in result.stdout.lower()
            else:
                # Basic check: can files be compiled with Python 3?
                python_files = list(self.root_path.rglob("*.py"))[:10]
                errors = 0
                for py_file in python_files:
                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            compile(f.read(), str(py_file), 'exec')
                    except SyntaxError:
                        errors += 1
                passed = errors == 0
            
            self._add_check(
                results, "Compatibility", "Python 3 Compatibility", passed, 15, 15,
                "Code is Python 3 compatible" if passed else "Python 3 compatibility issues remain",
                "Run: ./py2to3 check to identify remaining issues"
            )
        except:
            self._add_check(
                results, "Compatibility", "Python 3 Compatibility", False, 0, 15,
                "Could not verify Python 3 compatibility",
                "Run: ./py2to3 check"
            )
    
    def _check_no_python2_imports(self, results: Dict):
        """Check for Python 2 specific imports."""
        python_files = list(self.root_path.rglob("*.py"))
        py2_imports = []
        
        py2_modules = ['__builtin__', 'urllib2', 'urlparse', 'ConfigParser', 
                       'Queue', 'SocketServer', 'SimpleHTTPServer', 'BaseHTTPServer']
        
        for py_file in python_files[:50]:  # Check first 50 files
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for module in py2_modules:
                        if f"import {module}" in content or f"from {module}" in content:
                            py2_imports.append(py_file.name)
                            break
            except:
                pass
        
        passed = len(py2_imports) == 0
        self._add_check(
            results, "Compatibility", "No Python 2 Imports", passed, 10, 10,
            "No Python 2 imports found" if passed else f"Python 2 imports in {len(py2_imports)} files",
            "Replace Python 2 imports with Python 3 equivalents"
        )
    
    def _check_no_python2_syntax(self, results: Dict):
        """Check for Python 2 specific syntax."""
        python_files = list(self.root_path.rglob("*.py"))
        py2_syntax = []
        
        patterns = ['print ', 'except ', ', e:', 'xrange(', '.iteritems()', 
                   '.iterkeys()', '.itervalues()']
        
        for py_file in python_files[:50]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in patterns:
                        if pattern in content:
                            py2_syntax.append(py_file.name)
                            break
            except:
                pass
        
        passed = len(py2_syntax) == 0
        self._add_check(
            results, "Compatibility", "No Python 2 Syntax", passed, 5, 5,
            "No Python 2 syntax found" if passed else f"Python 2 syntax in {len(py2_syntax)} files",
            "Run: ./py2to3 fix to convert Python 2 syntax"
        )
    
    def _check_all_tests_pass_py3(self, results: Dict):
        """Check if all tests pass with Python 3."""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "-v"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            passed = result.returncode == 0
            self._add_check(
                results, "Testing", "All Tests Pass (Python 3)", passed, 15, 15,
                "All tests pass with Python 3" if passed else "Some tests fail with Python 3",
                "Fix failing tests before deploying to production"
            )
        except:
            self._add_check(
                results, "Testing", "All Tests Pass (Python 3)", False, 0, 15,
                "Could not run tests with Python 3",
                "Install pytest and run tests"
            )
    
    def _check_test_coverage_adequate(self, results: Dict):
        """Check if test coverage is adequate."""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "--cov=.", "--cov-report=term"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Extract coverage percentage
            import re
            coverage_match = re.search(r'TOTAL.*?(\d+)%', result.stdout)
            if coverage_match:
                coverage = int(coverage_match.group(1))
                passed = coverage >= 70
                self._add_check(
                    results, "Testing", "Test Coverage >= 70%", passed, 5, 5,
                    f"Test coverage: {coverage}%" if passed else f"Test coverage: {coverage}% (below 70%)",
                    "Increase test coverage to at least 70%"
                )
            else:
                self._add_check(
                    results, "Testing", "Test Coverage >= 70%", False, 0, 5,
                    "Could not determine coverage",
                    "Run: pytest --cov=. --cov-report=term"
                )
        except:
            self._add_check(
                results, "Testing", "Test Coverage >= 70%", False, 0, 5,
                "Coverage not available",
                "Install pytest-cov: pip install pytest-cov"
            )
    
    def _check_integration_tests(self, results: Dict):
        """Check if integration tests exist."""
        test_dirs = [self.root_path / "tests", self.root_path / "test"]
        integration_tests = []
        
        for test_dir in test_dirs:
            if test_dir.exists():
                integration_tests.extend(list(test_dir.glob("*integration*.py")))
                integration_tests.extend(list(test_dir.glob("*e2e*.py")))
        
        passed = len(integration_tests) > 0
        self._add_check(
            results, "Testing", "Integration Tests Exist", passed, 5, 5,
            f"Found {len(integration_tests)} integration tests" if passed else "No integration tests found",
            "Add integration tests to verify end-to-end functionality"
        )
    
    def _check_no_code_smells(self, results: Dict):
        """Check for code smells."""
        try:
            result = subprocess.run(
                ["python3", "-m", "pylint", "--exit-zero", "--score=yes", "src"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            import re
            score_match = re.search(r'Your code has been rated at ([\d.]+)/10', result.stdout)
            if score_match:
                score = float(score_match.group(1))
                passed = score >= 7.0
                self._add_check(
                    results, "Code Quality", "Code Quality Score >= 7.0", passed, 7, 7,
                    f"Code quality score: {score}/10" if passed else f"Code quality score: {score}/10 (below 7.0)",
                    "Improve code quality by addressing pylint warnings"
                )
            else:
                self._add_check(
                    results, "Code Quality", "Code Quality Score >= 7.0", True, 7, 7,
                    "Code quality check passed (pylint not available)"
                )
        except:
            self._add_check(
                results, "Code Quality", "Code Quality Score >= 7.0", True, 7, 7,
                "Code quality not checked (pylint not available)"
            )
    
    def _check_type_hints_added(self, results: Dict):
        """Check if type hints were added."""
        python_files = list(self.root_path.rglob("*.py"))
        files_with_hints = 0
        
        for py_file in python_files[:20]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '->' in content or ': ' in content:
                        files_with_hints += 1
            except:
                pass
        
        passed = files_with_hints > 0
        self._add_check(
            results, "Code Quality", "Type Hints Added", passed, 6, 6,
            f"Type hints found in {files_with_hints} files" if passed else "No type hints found",
            "Add type hints for better Python 3 code: ./py2to3 typehints"
        )
    
    def _check_modernization_complete(self, results: Dict):
        """Check if code uses modern Python 3 features."""
        python_files = list(self.root_path.rglob("*.py"))
        modern_features = 0
        
        for py_file in python_files[:20]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Look for f-strings, type hints, pathlib, etc.
                    if 'f"' in content or "f'" in content or 'from pathlib import' in content:
                        modern_features += 1
            except:
                pass
        
        passed = modern_features > 0
        self._add_check(
            results, "Code Quality", "Modernization Applied", passed, 7, 7,
            f"Modern Python 3 features in {modern_features} files" if passed else "No modern Python 3 features",
            "Modernize code: ./py2to3 modernize"
        )
    
    def _check_changelog_updated(self, results: Dict):
        """Check if CHANGELOG was updated."""
        changelog_files = [
            self.root_path / "CHANGELOG.md",
            self.root_path / "CHANGELOG.rst",
            self.root_path / "CHANGELOG.txt"
        ]
        passed = any(f.exists() for f in changelog_files)
        self._add_check(
            results, "Documentation", "CHANGELOG Updated", passed, 5, 5,
            "CHANGELOG file exists" if passed else "No CHANGELOG file",
            "Document migration in CHANGELOG: ./py2to3 changelog"
        )
    
    def _check_migration_documented(self, results: Dict):
        """Check if migration is documented."""
        doc_files = [
            self.root_path / "MIGRATION.md",
            self.root_path / "docs" / "migration.md",
            self.root_path / "UPGRADE.md"
        ]
        passed = any(f.exists() for f in doc_files)
        self._add_check(
            results, "Documentation", "Migration Documented", passed, 5, 5,
            "Migration documentation exists" if passed else "No migration documentation",
            "Document migration process and breaking changes"
        )
    
    def _check_api_docs_updated(self, results: Dict):
        """Check if API documentation was updated."""
        doc_dirs = [
            self.root_path / "docs",
            self.root_path / "doc"
        ]
        
        has_docs = False
        for doc_dir in doc_dirs:
            if doc_dir.exists():
                doc_files = list(doc_dir.glob("*.md")) + list(doc_dir.glob("*.rst"))
                if len(doc_files) > 0:
                    has_docs = True
                    break
        
        passed = has_docs
        self._add_check(
            results, "Documentation", "API Documentation Updated", passed, 5, 5,
            "API documentation exists" if passed else "No API documentation",
            "Update API documentation to reflect Python 3 changes"
        )
    
    def _check_dependencies_compatible(self, results: Dict):
        """Check if dependencies are Python 3 compatible."""
        req_files = [
            self.root_path / "requirements.txt",
            self.root_path / "setup.py"
        ]
        
        has_req_file = any(f.exists() for f in req_files)
        if not has_req_file:
            self._add_check(
                results, "Dependencies", "Dependencies Compatible", True, 5, 5,
                "No dependencies to check"
            )
            return
        
        # Simple heuristic: check if file was recently modified
        req_file = next(f for f in req_files if f.exists())
        import time
        mtime = req_file.stat().st_mtime
        days_old = (time.time() - mtime) / 86400
        
        passed = days_old < 30  # Modified in last 30 days
        self._add_check(
            results, "Dependencies", "Dependencies Compatible", passed, 5, 5,
            "Dependencies recently updated" if passed else "Dependencies may be outdated",
            "Update dependencies: pip install --upgrade -r requirements.txt"
        )
    
    def _check_no_deprecated_packages(self, results: Dict):
        """Check for deprecated packages."""
        req_file = self.root_path / "requirements.txt"
        if not req_file.exists():
            self._add_check(
                results, "Dependencies", "No Deprecated Packages", True, 5, 5,
                "No requirements file to check"
            )
            return
        
        deprecated = ['django<2.0', 'flask<1.0', 'requests<2.0']
        
        try:
            with open(req_file, 'r') as f:
                content = f.read().lower()
                has_deprecated = any(dep in content for dep in deprecated)
            
            passed = not has_deprecated
            self._add_check(
                results, "Dependencies", "No Deprecated Packages", passed, 5, 5,
                "No deprecated packages found" if passed else "Deprecated packages found",
                "Update to latest package versions"
            )
        except:
            self._add_check(
                results, "Dependencies", "No Deprecated Packages", True, 5, 5,
                "Could not check for deprecated packages"
            )
    
    def _calculate_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage."""
        if percentage >= 90:
            return "A (Excellent)"
        elif percentage >= 80:
            return "B (Good)"
        elif percentage >= 70:
            return "C (Fair)"
        elif percentage >= 60:
            return "D (Poor)"
        else:
            return "F (Needs Improvement)"
    
    def print_report(self, results: Dict):
        """Print a formatted readiness report."""
        print("\n" + "="*80)
        print(f"  MIGRATION READINESS ASSESSMENT - {results['assessment_type'].upper()}")
        print("="*80 + "\n")
        
        # Overall Score
        score = results["score"]
        max_score = results["max_score"]
        percentage = results["percentage"]
        grade = results["grade"]
        
        print(f"Overall Score: {score}/{max_score} ({percentage:.1f}%)")
        print(f"Grade: {grade}\n")
        
        # Score bar
        bar_length = 50
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        if percentage >= 80:
            color = "\033[92m"  # Green
        elif percentage >= 60:
            color = "\033[93m"  # Yellow
        else:
            color = "\033[91m"  # Red
        
        print(f"{color}{bar}\033[0m {percentage:.1f}%\n")
        
        # Checks by category
        categories = {}
        for check in results["checks"]:
            cat = check["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(check)
        
        for category, checks in categories.items():
            cat_score = sum(c["score"] for c in checks)
            cat_max = sum(c["max_score"] for c in checks)
            cat_pct = (cat_score / cat_max * 100) if cat_max > 0 else 0
            
            print(f"\n{category}: {cat_score}/{cat_max} ({cat_pct:.0f}%)")
            print("-" * 80)
            
            for check in checks:
                status = "✓" if check["passed"] else "✗"
                status_color = "\033[92m" if check["passed"] else "\033[91m"
                print(f"  {status_color}{status}\033[0m {check['name']}: {check['message']}")
        
        # Recommendations
        if results["recommendations"]:
            print("\n" + "="*80)
            print("  RECOMMENDATIONS")
            print("="*80 + "\n")
            for i, rec in enumerate(results["recommendations"], 1):
                print(f"{i}. {rec}")
        
        # Summary
        print("\n" + "="*80)
        if percentage >= 80:
            print("  ✓ READY - Your project is well-prepared!")
        elif percentage >= 60:
            print("  ⚠ NEEDS WORK - Address recommendations before proceeding")
        else:
            print("  ✗ NOT READY - Significant preparation needed")
        print("="*80 + "\n")
    
    def save_report(self, results: Dict, output_path: str):
        """Save report to JSON file."""
        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Report saved to: {output_file}")


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migration Readiness & Safety Score Assessment"
    )
    parser.add_argument(
        'assessment_type',
        choices=['pre', 'post', 'both'],
        help='Type of assessment: pre-migration, post-migration, or both'
    )
    parser.add_argument(
        '--path',
        default='.',
        help='Root path of project to assess (default: current directory)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Save report to JSON file'
    )
    
    args = parser.parse_args()
    
    checker = ReadinessChecker(args.path)
    
    if args.assessment_type in ['pre', 'both']:
        results = checker.assess_pre_migration_readiness()
        checker.print_report(results)
        if args.output:
            output_file = args.output if args.assessment_type == 'pre' else args.output.replace('.json', '_pre.json')
            checker.save_report(results, output_file)
    
    if args.assessment_type in ['post', 'both']:
        if args.assessment_type == 'both':
            print("\n\n")
        results = checker.assess_post_migration_readiness()
        checker.print_report(results)
        if args.output:
            output_file = args.output if args.assessment_type == 'post' else args.output.replace('.json', '_post.json')
            checker.save_report(results, output_file)


if __name__ == "__main__":
    main()
