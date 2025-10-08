#!/usr/bin/env python3
"""
Migration Health Monitor for Python 2 to 3 Migration

Provides a comprehensive health score and monitoring dashboard for tracking
migration progress, identifying issues, and ensuring migration quality.
"""

import ast
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class HealthDimension:
    """Represents a single health dimension with score and details."""
    
    def __init__(self, name: str, score: float, weight: float, status: str, 
                 details: str, recommendations: List[str]):
        self.name = name
        self.score = max(0.0, min(100.0, score))  # Clamp between 0-100
        self.weight = weight
        self.status = status  # 'excellent', 'good', 'warning', 'critical'
        self.details = details
        self.recommendations = recommendations
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'score': round(self.score, 1),
            'weight': self.weight,
            'status': self.status,
            'details': self.details,
            'recommendations': self.recommendations
        }


class MigrationHealthMonitor:
    """Monitors and reports on Python 2 to 3 migration health."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.dimensions = []
        self.overall_score = 0.0
        self.overall_status = 'unknown'
        self.history_file = self.project_path / '.py2to3_health_history.json'
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load historical health data."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_history(self):
        """Save current health data to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': round(self.overall_score, 1),
            'overall_status': self.overall_status,
            'dimensions': [d.to_dict() for d in self.dimensions]
        }
        self.history.append(entry)
        
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}", file=sys.stderr)
    
    def analyze(self, save_history: bool = True) -> Dict:
        """
        Analyze project health across all dimensions.
        
        Returns:
            Dictionary containing health report
        """
        self.dimensions = []
        
        # Analyze each dimension
        self.dimensions.append(self._analyze_compatibility())
        self.dimensions.append(self._analyze_code_quality())
        self.dimensions.append(self._analyze_test_coverage())
        self.dimensions.append(self._analyze_risk_level())
        self.dimensions.append(self._analyze_progress())
        self.dimensions.append(self._analyze_backup_safety())
        
        # Calculate weighted overall score
        total_weight = sum(d.weight for d in self.dimensions)
        if total_weight > 0:
            self.overall_score = sum(d.score * d.weight for d in self.dimensions) / total_weight
        else:
            self.overall_score = 0.0
        
        # Determine overall status
        if self.overall_score >= 90:
            self.overall_status = 'excellent'
        elif self.overall_score >= 75:
            self.overall_status = 'good'
        elif self.overall_score >= 50:
            self.overall_status = 'warning'
        else:
            self.overall_status = 'critical'
        
        # Save to history
        if save_history:
            self._save_history()
        
        return self._generate_report()
    
    def _analyze_compatibility(self) -> HealthDimension:
        """Analyze Python 3 compatibility."""
        try:
            # Try to import and use verifier
            sys.path.insert(0, str(Path(__file__).parent))
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            
            # Count Python files and issues
            python_files = list(self.project_path.rglob('*.py'))
            if not python_files:
                return HealthDimension(
                    name='Compatibility',
                    score=100.0,
                    weight=0.30,
                    status='excellent',
                    details='No Python files found',
                    recommendations=[]
                )
            
            # Check for issues (simplified - check for common patterns)
            total_issues = 0
            critical_issues = 0
            
            for py_file in python_files:
                if any(skip in str(py_file) for skip in ['test', '__pycache__', '.git', 'venv']):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Check for Python 2 patterns
                    if 'print ' in content and 'print(' not in content:
                        total_issues += 1
                        critical_issues += 1
                    if 'import urllib2' in content:
                        total_issues += 1
                    if '.iteritems()' in content:
                        total_issues += 1
                    if 'except ' in content and ' as ' not in content and ':' in content:
                        if 'except:' not in content:  # Basic check for old-style exceptions
                            pass  # More complex to detect reliably
                    if 'xrange(' in content:
                        total_issues += 1
                        
                except Exception:
                    pass
            
            # Calculate score based on issues
            if len(python_files) > 0:
                issues_per_file = total_issues / len(python_files)
                # Score decreases as issues per file increases
                score = max(0, 100 - (issues_per_file * 20))
            else:
                score = 100
            
            # Determine status and recommendations
            if score >= 90:
                status = 'excellent'
                details = f'Found {total_issues} compatibility issues in {len(python_files)} files'
                recommendations = ['Continue monitoring for new issues']
            elif score >= 70:
                status = 'good'
                details = f'Found {total_issues} compatibility issues in {len(python_files)} files'
                recommendations = [
                    'Run: ./py2to3 fix to automatically fix common issues',
                    'Review remaining issues with: ./py2to3 check'
                ]
            elif score >= 40:
                status = 'warning'
                details = f'Found {total_issues} compatibility issues ({critical_issues} critical)'
                recommendations = [
                    'PRIORITY: Run ./py2to3 preflight before fixing',
                    'Apply fixes with: ./py2to3 fix --backup-dir backups',
                    'Review high-risk changes with: ./py2to3 risk'
                ]
            else:
                status = 'critical'
                details = f'Found {total_issues} compatibility issues ({critical_issues} critical)'
                recommendations = [
                    'URGENT: Create backup with: ./py2to3 backup create',
                    'Run preflight check: ./py2to3 preflight',
                    'Plan migration with: ./py2to3 plan',
                    'Consider incremental migration approach'
                ]
            
            return HealthDimension(
                name='Compatibility',
                score=score,
                weight=0.30,
                status=status,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthDimension(
                name='Compatibility',
                score=50.0,
                weight=0.30,
                status='warning',
                details=f'Could not analyze compatibility: {str(e)}',
                recommendations=['Ensure verifier module is available']
            )
    
    def _analyze_code_quality(self) -> HealthDimension:
        """Analyze code quality metrics."""
        try:
            python_files = list(self.project_path.rglob('*.py'))
            if not python_files:
                return HealthDimension(
                    name='Code Quality',
                    score=100.0,
                    weight=0.20,
                    status='excellent',
                    details='No Python files to analyze',
                    recommendations=[]
                )
            
            total_lines = 0
            total_functions = 0
            total_classes = 0
            complex_functions = 0
            long_files = 0
            
            for py_file in python_files:
                if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'venv']):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        total_lines += len(lines)
                        
                        if len(lines) > 500:
                            long_files += 1
                        
                        # Try to parse AST
                        try:
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    total_functions += 1
                                    # Check complexity (rough estimate by number of statements)
                                    if len(node.body) > 20:
                                        complex_functions += 1
                                elif isinstance(node, ast.ClassDef):
                                    total_classes += 1
                        except:
                            pass
                            
                except Exception:
                    pass
            
            # Calculate quality score
            score = 100.0
            issues = []
            
            if long_files > 0:
                score -= min(20, long_files * 5)
                issues.append(f'{long_files} files exceed 500 lines')
            
            if total_functions > 0 and complex_functions / total_functions > 0.2:
                score -= 15
                issues.append(f'{complex_functions} functions are complex')
            
            avg_file_size = total_lines / len(python_files) if python_files else 0
            if avg_file_size > 300:
                score -= 10
                issues.append(f'Average file size is {int(avg_file_size)} lines')
            
            score = max(0, score)
            
            # Determine status
            if score >= 85:
                status = 'excellent'
            elif score >= 70:
                status = 'good'
            elif score >= 50:
                status = 'warning'
            else:
                status = 'critical'
            
            details = f'{len(python_files)} files, {total_functions} functions, {total_classes} classes'
            if issues:
                details += f' - Issues: {", ".join(issues)}'
            
            recommendations = []
            if long_files > 0:
                recommendations.append('Consider splitting large files into smaller modules')
            if complex_functions > 0:
                recommendations.append('Refactor complex functions into smaller units')
            if not recommendations:
                recommendations.append('Code quality is good - maintain current standards')
            
            return HealthDimension(
                name='Code Quality',
                score=score,
                weight=0.20,
                status=status,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthDimension(
                name='Code Quality',
                score=50.0,
                weight=0.20,
                status='warning',
                details=f'Could not analyze quality: {str(e)}',
                recommendations=['Check file permissions and syntax']
            )
    
    def _analyze_test_coverage(self) -> HealthDimension:
        """Analyze test coverage and presence."""
        try:
            # Look for test files
            test_files = []
            test_patterns = ['test_*.py', '*_test.py', 'tests.py']
            
            for pattern in test_patterns:
                test_files.extend(self.project_path.rglob(pattern))
            
            # Count source files
            source_files = [
                f for f in self.project_path.rglob('*.py')
                if not any(skip in str(f) for skip in ['test', '__pycache__', '.git', 'venv'])
            ]
            
            if not source_files:
                return HealthDimension(
                    name='Test Coverage',
                    score=100.0,
                    weight=0.15,
                    status='excellent',
                    details='No source files to test',
                    recommendations=[]
                )
            
            # Calculate coverage ratio (rough estimate)
            coverage_ratio = len(test_files) / len(source_files) if source_files else 0
            
            # Score based on coverage
            if coverage_ratio >= 0.8:
                score = 100.0
                status = 'excellent'
                details = f'{len(test_files)} test files for {len(source_files)} source files'
                recommendations = ['Excellent test coverage - keep it up!']
            elif coverage_ratio >= 0.5:
                score = 80.0
                status = 'good'
                details = f'{len(test_files)} test files for {len(source_files)} source files'
                recommendations = [
                    'Good coverage - consider adding tests for uncovered modules',
                    'Run: pytest --cov to measure actual coverage'
                ]
            elif coverage_ratio >= 0.2:
                score = 60.0
                status = 'warning'
                details = f'{len(test_files)} test files for {len(source_files)} source files'
                recommendations = [
                    'Test coverage needs improvement',
                    'Generate tests with: ./py2to3 test-gen',
                    'Prioritize testing critical modules first'
                ]
            else:
                score = 30.0
                status = 'critical'
                details = f'Only {len(test_files)} test files for {len(source_files)} source files'
                recommendations = [
                    'CRITICAL: Very low test coverage',
                    'Generate baseline tests: ./py2to3 test-gen',
                    'Set up pytest framework if not present',
                    'Create tests before migration to ensure behavior parity'
                ]
            
            return HealthDimension(
                name='Test Coverage',
                score=score,
                weight=0.15,
                status=status,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthDimension(
                name='Test Coverage',
                score=50.0,
                weight=0.15,
                status='warning',
                details=f'Could not analyze tests: {str(e)}',
                recommendations=['Check test directory structure']
            )
    
    def _analyze_risk_level(self) -> HealthDimension:
        """Analyze migration risk level."""
        try:
            # Check for high-risk indicators
            risk_score = 100.0
            risks = []
            
            # Check for backup directory
            backup_dirs = [
                self.project_path / '.py2to3_backups',
                self.project_path / 'backups',
                self.project_path / '.backups'
            ]
            has_backups = any(d.exists() for d in backup_dirs)
            
            if not has_backups:
                risk_score -= 30
                risks.append('No backup directory found')
            
            # Check for git repository
            git_dir = self.project_path / '.git'
            if not git_dir.exists():
                risk_score -= 20
                risks.append('No git repository')
            else:
                # Check for uncommitted changes (basic check)
                try:
                    import subprocess
                    result = subprocess.run(
                        ['git', 'status', '--porcelain'],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.stdout.strip():
                        risk_score -= 15
                        risks.append('Uncommitted changes detected')
                except:
                    pass
            
            # Check for configuration file
            config_file = self.project_path / '.py2to3.config.json'
            if not config_file.exists():
                risk_score -= 10
                risks.append('No configuration file')
            
            # Check for documentation
            doc_files = ['README.md', 'MIGRATION.md', 'CHANGELOG.md']
            has_docs = any((self.project_path / doc).exists() for doc in doc_files)
            if not has_docs:
                risk_score -= 10
                risks.append('Limited documentation')
            
            risk_score = max(0, risk_score)
            
            # Determine status
            if risk_score >= 85:
                status = 'excellent'
                details = 'Migration environment is well-prepared'
            elif risk_score >= 70:
                status = 'good'
                details = f'Some risk factors: {", ".join(risks)}'
            elif risk_score >= 50:
                status = 'warning'
                details = f'Multiple risk factors: {", ".join(risks)}'
            else:
                status = 'critical'
                details = f'High risk: {", ".join(risks)}'
            
            # Generate recommendations
            recommendations = []
            if 'No backup' in str(risks):
                recommendations.append('Create backup: ./py2to3 backup create')
            if 'No git' in str(risks):
                recommendations.append('Initialize git repository: git init')
            if 'Uncommitted changes' in str(risks):
                recommendations.append('Commit changes before migration: git commit -am "Pre-migration state"')
            if 'No configuration' in str(risks):
                recommendations.append('Create config: ./py2to3 config init')
            if not recommendations:
                recommendations.append('Risk level is acceptable')
            
            return HealthDimension(
                name='Risk Level',
                score=risk_score,
                weight=0.20,
                status=status,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthDimension(
                name='Risk Level',
                score=50.0,
                weight=0.20,
                status='warning',
                details=f'Could not analyze risk: {str(e)}',
                recommendations=['Review migration preparation manually']
            )
    
    def _analyze_progress(self) -> HealthDimension:
        """Analyze migration progress."""
        try:
            # Check for migration state/journal files
            state_file = self.project_path / '.migration_state.json'
            journal_file = self.project_path / '.migration_journal.json'
            
            progress_score = 0.0
            completed_items = 0
            total_items = 0
            
            if state_file.exists():
                try:
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                        if 'files' in state:
                            total_items = len(state['files'])
                            completed_items = sum(
                                1 for f in state['files'].values() 
                                if f.get('status') == 'completed'
                            )
                except:
                    pass
            
            if total_items > 0:
                progress_score = (completed_items / total_items) * 100
            else:
                # No state file - estimate from Python 2 patterns
                python_files = list(self.project_path.rglob('*.py'))
                py2_patterns = 0
                
                for py_file in python_files:
                    if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'venv']):
                        continue
                    
                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if any(pattern in content for pattern in [
                                'print ', 'urllib2', '.iteritems()', 'xrange('
                            ]):
                                py2_patterns += 1
                    except:
                        pass
                
                if python_files:
                    migrated_ratio = 1 - (py2_patterns / len(python_files))
                    progress_score = max(0, min(100, migrated_ratio * 100))
                else:
                    progress_score = 100
            
            # Determine status
            if progress_score >= 90:
                status = 'excellent'
                details = f'Migration {int(progress_score)}% complete'
                recommendations = [
                    'Almost done! Review final issues',
                    'Run final verification: ./py2to3 check',
                    'Prepare for release'
                ]
            elif progress_score >= 70:
                status = 'good'
                details = f'Migration {int(progress_score)}% complete'
                recommendations = [
                    'Good progress - keep going!',
                    'Review migration state: ./py2to3 state show',
                    'Update journal: ./py2to3 journal add'
                ]
            elif progress_score >= 40:
                status = 'warning'
                details = f'Migration {int(progress_score)}% complete'
                recommendations = [
                    'Migration is underway - maintain momentum',
                    'Use planner to organize remaining work: ./py2to3 plan',
                    'Track progress with: ./py2to3 stats collect'
                ]
            elif progress_score > 0:
                status = 'warning'
                details = f'Migration {int(progress_score)}% complete'
                recommendations = [
                    'Migration just started',
                    'Create a plan: ./py2to3 plan',
                    'Start with high-priority files',
                    'Track progress regularly'
                ]
            else:
                status = 'critical'
                details = 'Migration not started'
                recommendations = [
                    'URGENT: Begin migration',
                    'Run preflight: ./py2to3 preflight',
                    'Create plan: ./py2to3 plan',
                    'Start with: ./py2to3 migrate'
                ]
            
            return HealthDimension(
                name='Progress',
                score=progress_score,
                weight=0.10,
                status=status,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthDimension(
                name='Progress',
                score=50.0,
                weight=0.10,
                status='warning',
                details=f'Could not analyze progress: {str(e)}',
                recommendations=['Check migration state files']
            )
    
    def _analyze_backup_safety(self) -> HealthDimension:
        """Analyze backup and safety measures."""
        try:
            score = 100.0
            issues = []
            
            # Check for backup directory
            backup_dir = self.project_path / '.py2to3_backups'
            if not backup_dir.exists():
                score -= 40
                issues.append('No backup directory')
            else:
                # Count backups
                backups = list(backup_dir.glob('*'))
                if len(backups) == 0:
                    score -= 30
                    issues.append('No backups created')
                elif len(backups) < 5:
                    score -= 10
                    issues.append('Limited backup history')
            
            # Check for rollback history
            rollback_file = self.project_path / '.py2to3_rollback_history.json'
            if rollback_file.exists():
                score += 0  # Neutral, but good to have
            else:
                score -= 10
                issues.append('No rollback history')
            
            # Check for git
            if (self.project_path / '.git').exists():
                score += 0  # Already counted in risk
            else:
                score -= 20
                issues.append('No version control')
            
            score = max(0, min(100, score))
            
            # Determine status
            if score >= 85:
                status = 'excellent'
                details = 'Strong safety measures in place'
            elif score >= 70:
                status = 'good'
                details = 'Good safety measures'
                if issues:
                    details += f' - Minor issues: {", ".join(issues)}'
            elif score >= 50:
                status = 'warning'
                details = f'Safety concerns: {", ".join(issues)}'
            else:
                status = 'critical'
                details = f'Critical safety issues: {", ".join(issues)}'
            
            # Recommendations
            recommendations = []
            if 'No backup' in str(issues):
                recommendations.append('Create backup: ./py2to3 backup create')
            if 'No backups created' in str(issues):
                recommendations.append('Create initial backup before proceeding')
            if 'No version control' in str(issues):
                recommendations.append('Initialize git: git init && git add . && git commit -m "Initial"')
            if not recommendations:
                recommendations.append('Safety measures are adequate')
            
            return HealthDimension(
                name='Backup & Safety',
                score=score,
                weight=0.05,
                status=status,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthDimension(
                name='Backup & Safety',
                score=50.0,
                weight=0.05,
                status='warning',
                details=f'Could not analyze safety: {str(e)}',
                recommendations=['Review backup procedures manually']
            )
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive health report."""
        # Get trend if we have history
        trend = 'stable'
        trend_value = 0.0
        
        if len(self.history) >= 2:
            prev_score = self.history[-2]['overall_score']
            current_score = self.overall_score
            diff = current_score - prev_score
            
            if diff > 5:
                trend = 'improving'
                trend_value = diff
            elif diff < -5:
                trend = 'declining'
                trend_value = diff
            else:
                trend = 'stable'
                trend_value = diff
        
        # Collect all recommendations by priority
        all_recommendations = []
        for dim in self.dimensions:
            for rec in dim.recommendations:
                if 'URGENT' in rec or 'CRITICAL' in rec:
                    priority = 'critical'
                elif 'PRIORITY' in rec:
                    priority = 'high'
                else:
                    priority = 'normal'
                
                all_recommendations.append({
                    'dimension': dim.name,
                    'priority': priority,
                    'recommendation': rec
                })
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'normal': 2}
        all_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return {
            'overall_score': round(self.overall_score, 1),
            'overall_status': self.overall_status,
            'trend': trend,
            'trend_value': round(trend_value, 1),
            'timestamp': datetime.now().isoformat(),
            'dimensions': [d.to_dict() for d in self.dimensions],
            'recommendations': all_recommendations,
            'health_history': self.history[-10:] if len(self.history) > 10 else self.history
        }
    
    def get_trend_analysis(self, days: int = 7) -> Dict:
        """Analyze health trends over specified days."""
        if not self.history:
            return {
                'available': False,
                'message': 'No historical data available'
            }
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = [
            h for h in self.history
            if datetime.fromisoformat(h['timestamp']) >= cutoff_date
        ]
        
        if len(recent_history) < 2:
            return {
                'available': False,
                'message': f'Not enough data in last {days} days'
            }
        
        scores = [h['overall_score'] for h in recent_history]
        timestamps = [h['timestamp'] for h in recent_history]
        
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        improvement = scores[-1] - scores[0]
        
        return {
            'available': True,
            'days': days,
            'measurements': len(recent_history),
            'average_score': round(avg_score, 1),
            'min_score': round(min_score, 1),
            'max_score': round(max_score, 1),
            'improvement': round(improvement, 1),
            'trend': 'improving' if improvement > 5 else 'declining' if improvement < -5 else 'stable',
            'first_measurement': timestamps[0],
            'last_measurement': timestamps[-1]
        }


def format_health_report(report: Dict, verbose: bool = False) -> str:
    """Format health report for console output."""
    lines = []
    
    # Header
    lines.append("\n" + "=" * 70)
    lines.append("MIGRATION HEALTH REPORT".center(70))
    lines.append("=" * 70)
    
    # Overall score with visual indicator
    score = report['overall_score']
    status = report['overall_status']
    
    # Create score bar
    bar_length = 50
    filled = int((score / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # Status emoji
    status_emoji = {
        'excellent': '🟢',
        'good': '🟡',
        'warning': '🟠',
        'critical': '🔴'
    }
    
    lines.append(f"\n{status_emoji.get(status, '⚪')} Overall Health Score: {score}/100 ({status.upper()})")
    lines.append(f"[{bar}]")
    
    # Trend
    trend = report.get('trend', 'stable')
    trend_value = report.get('trend_value', 0)
    trend_emoji = {'improving': '📈', 'declining': '📉', 'stable': '➡️'}
    if trend != 'stable':
        lines.append(f"\n{trend_emoji[trend]} Trend: {trend.upper()} ({trend_value:+.1f} points)")
    else:
        lines.append(f"\n{trend_emoji[trend]} Trend: STABLE")
    
    lines.append(f"\nTimestamp: {report['timestamp']}")
    
    # Dimensions
    lines.append("\n" + "-" * 70)
    lines.append("HEALTH DIMENSIONS")
    lines.append("-" * 70)
    
    for dim in report['dimensions']:
        dim_status = status_emoji.get(dim['status'], '⚪')
        lines.append(f"\n{dim_status} {dim['name']}: {dim['score']}/100 (weight: {dim['weight']*100:.0f}%)")
        lines.append(f"   {dim['details']}")
        
        if verbose and dim['recommendations']:
            lines.append("   Recommendations:")
            for rec in dim['recommendations']:
                lines.append(f"   • {rec}")
    
    # Priority recommendations
    lines.append("\n" + "-" * 70)
    lines.append("RECOMMENDED ACTIONS")
    lines.append("-" * 70)
    
    recommendations = report.get('recommendations', [])
    
    # Group by priority
    critical = [r for r in recommendations if r['priority'] == 'critical']
    high = [r for r in recommendations if r['priority'] == 'high']
    normal = [r for r in recommendations if r['priority'] == 'normal']
    
    if critical:
        lines.append("\n🔴 CRITICAL:")
        for rec in critical[:3]:  # Show top 3
            lines.append(f"   • [{rec['dimension']}] {rec['recommendation']}")
    
    if high:
        lines.append("\n🟠 HIGH PRIORITY:")
        for rec in high[:3]:
            lines.append(f"   • [{rec['dimension']}] {rec['recommendation']}")
    
    if not critical and not high:
        if normal:
            lines.append("\n🟢 Suggestions:")
            for rec in normal[:5]:
                lines.append(f"   • [{rec['dimension']}] {rec['recommendation']}")
        else:
            lines.append("\n✅ No immediate actions required - health is good!")
    
    lines.append("\n" + "=" * 70 + "\n")
    
    return "\n".join(lines)


def main():
    """Main entry point for health monitor CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Monitor Python 2 to 3 migration health'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to project directory (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for JSON report'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed recommendations for each dimension'
    )
    parser.add_argument(
        '--no-history',
        action='store_true',
        help='Do not save to history'
    )
    parser.add_argument(
        '--trend',
        type=int,
        metavar='DAYS',
        help='Show trend analysis for last N days'
    )
    
    args = parser.parse_args()
    
    # Create monitor and analyze
    monitor = MigrationHealthMonitor(args.path)
    report = monitor.analyze(save_history=not args.no_history)
    
    # Print report
    print(format_health_report(report, verbose=args.verbose))
    
    # Show trend analysis if requested
    if args.trend:
        trend = monitor.get_trend_analysis(days=args.trend)
        if trend['available']:
            print(f"\n📊 Trend Analysis (Last {trend['days']} days):")
            print(f"   Measurements: {trend['measurements']}")
            print(f"   Average Score: {trend['average_score']}/100")
            print(f"   Range: {trend['min_score']}-{trend['max_score']}")
            print(f"   Change: {trend['improvement']:+.1f} points")
            print(f"   Trend: {trend['trend'].upper()}")
        else:
            print(f"\n⚠️  {trend['message']}")
    
    # Save JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✓ JSON report saved to: {args.output}")
    
    # Exit with status code based on health
    if report['overall_score'] >= 70:
        sys.exit(0)
    elif report['overall_score'] >= 50:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
