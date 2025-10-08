#!/usr/bin/env python3
"""
Risk Analyzer for Python 2 to 3 Migration

Analyzes migration changes to identify high-risk modifications that require
careful manual review. Helps teams prioritize code review efforts by scoring
changes based on potential impact, complexity, and criticality.
"""

import ast
import os
import difflib
import json
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for migration changes."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ChangeCategory(Enum):
    """Categories of changes that affect risk assessment."""
    ERROR_HANDLING = "error_handling"
    IO_OPERATIONS = "io_operations"
    DATABASE = "database"
    NETWORK = "network"
    ENCODING = "encoding"
    TYPE_CONVERSION = "type_conversion"
    ITERATOR = "iterator"
    IMPORTS = "imports"
    SYNTAX = "syntax"
    LOGIC = "logic"


@dataclass
class RiskFactor:
    """A factor contributing to risk assessment."""
    category: str
    description: str
    weight: float
    location: str


@dataclass
class FileRiskAssessment:
    """Risk assessment for a single file."""
    file_path: str
    risk_level: str
    risk_score: float
    risk_factors: List[Dict]
    change_count: int
    function_changes: List[str]
    critical_areas: List[str]
    recommendations: List[str]


class MigrationRiskAnalyzer:
    """Analyze migration risks and prioritize changes for review."""
    
    # Risk weights for different change categories
    CATEGORY_WEIGHTS = {
        ChangeCategory.ERROR_HANDLING: 10.0,
        ChangeCategory.IO_OPERATIONS: 9.0,
        ChangeCategory.DATABASE: 9.0,
        ChangeCategory.NETWORK: 8.0,
        ChangeCategory.ENCODING: 7.0,
        ChangeCategory.TYPE_CONVERSION: 6.0,
        ChangeCategory.ITERATOR: 5.0,
        ChangeCategory.IMPORTS: 3.0,
        ChangeCategory.SYNTAX: 2.0,
        ChangeCategory.LOGIC: 8.0,
    }
    
    # Critical function patterns
    CRITICAL_PATTERNS = {
        'exception': ChangeCategory.ERROR_HANDLING,
        'error': ChangeCategory.ERROR_HANDLING,
        'raise': ChangeCategory.ERROR_HANDLING,
        'try': ChangeCategory.ERROR_HANDLING,
        'open': ChangeCategory.IO_OPERATIONS,
        'read': ChangeCategory.IO_OPERATIONS,
        'write': ChangeCategory.IO_OPERATIONS,
        'file': ChangeCategory.IO_OPERATIONS,
        'sql': ChangeCategory.DATABASE,
        'query': ChangeCategory.DATABASE,
        'database': ChangeCategory.DATABASE,
        'db': ChangeCategory.DATABASE,
        'request': ChangeCategory.NETWORK,
        'response': ChangeCategory.NETWORK,
        'http': ChangeCategory.NETWORK,
        'socket': ChangeCategory.NETWORK,
        'encode': ChangeCategory.ENCODING,
        'decode': ChangeCategory.ENCODING,
        'unicode': ChangeCategory.ENCODING,
        'utf': ChangeCategory.ENCODING,
    }
    
    def __init__(self, backup_dir: str = 'backups', source_dir: str = 'src'):
        """Initialize the risk analyzer.
        
        Args:
            backup_dir: Directory containing backup files
            source_dir: Directory containing current (fixed) files
        """
        self.backup_dir = Path(backup_dir)
        self.source_dir = Path(source_dir)
        self.assessments: List[FileRiskAssessment] = []
        
    def analyze_project(self, scan_path: Optional[str] = None) -> Dict:
        """Analyze risk across the entire project.
        
        Args:
            scan_path: Path to analyze (defaults to source_dir)
            
        Returns:
            dict: Overall risk analysis
        """
        scan_path = Path(scan_path) if scan_path else self.source_dir
        
        if not scan_path.exists():
            return {
                'error': f"Path does not exist: {scan_path}",
                'assessments': []
            }
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(scan_path):
            # Skip hidden and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['venv', 'env', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Analyze each file
        self.assessments = []
        for file_path in python_files:
            assessment = self._analyze_file(file_path)
            if assessment:
                self.assessments.append(assessment)
        
        # Generate overall analysis
        return self._generate_summary()
    
    def _analyze_file(self, file_path: str) -> Optional[FileRiskAssessment]:
        """Analyze risk for a single file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            FileRiskAssessment or None if no backup exists
        """
        current_file = Path(file_path)
        
        # Try to find the backup file
        backup_file = self._find_backup(current_file)
        if not backup_file or not backup_file.exists():
            # No backup means no changes, minimal risk
            return None
        
        # Read both versions
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                old_content = f.read()
            with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
                new_content = f.read()
        except Exception as e:
            return None
        
        # If files are identical, no risk
        if old_content == new_content:
            return None
        
        # Analyze changes
        risk_factors = []
        function_changes = []
        critical_areas = []
        
        # Detect change types
        changes = list(difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            lineterm=''
        ))
        
        change_count = sum(1 for line in changes if line.startswith(('+', '-')) 
                          and not line.startswith(('+++', '---')))
        
        # Analyze AST if possible
        try:
            old_tree = ast.parse(old_content)
            new_tree = ast.parse(new_content)
            
            # Find function changes
            old_functions = self._extract_function_names(old_tree)
            new_functions = self._extract_function_names(new_tree)
            function_changes = list(old_functions & new_functions)
            
            # Analyze critical patterns
            critical_areas = self._find_critical_areas(new_content, new_tree)
            
        except SyntaxError:
            # If we can't parse, it's likely a significant change
            risk_factors.append(RiskFactor(
                category=ChangeCategory.SYNTAX.value,
                description="Syntax errors or unparseable code detected",
                weight=10.0,
                location=str(current_file)
            ))
        
        # Analyze change content for risk patterns
        risk_factors.extend(self._analyze_change_patterns(changes, str(current_file)))
        
        # Add weight for volume of changes
        if change_count > 50:
            risk_factors.append(RiskFactor(
                category="volume",
                description=f"Large number of changes ({change_count} lines)",
                weight=5.0,
                location=str(current_file)
            ))
        elif change_count > 20:
            risk_factors.append(RiskFactor(
                category="volume",
                description=f"Moderate number of changes ({change_count} lines)",
                weight=2.0,
                location=str(current_file)
            ))
        
        # Add weight for critical function changes
        if function_changes:
            for func in function_changes:
                if any(pattern in func.lower() for pattern in self.CRITICAL_PATTERNS):
                    risk_factors.append(RiskFactor(
                        category=ChangeCategory.LOGIC.value,
                        description=f"Changes in critical function: {func}",
                        weight=7.0,
                        location=str(current_file)
                    ))
        
        # Calculate overall risk score
        risk_score = sum(rf.weight for rf in risk_factors)
        risk_level = self._calculate_risk_level(risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, risk_factors, critical_areas
        )
        
        return FileRiskAssessment(
            file_path=str(current_file),
            risk_level=risk_level.value,
            risk_score=round(risk_score, 2),
            risk_factors=[asdict(rf) for rf in risk_factors],
            change_count=change_count,
            function_changes=function_changes[:10],  # Limit to top 10
            critical_areas=critical_areas,
            recommendations=recommendations
        )
    
    def _find_backup(self, current_file: Path) -> Optional[Path]:
        """Find the backup file for a given current file.
        
        Args:
            current_file: Path to current file
            
        Returns:
            Path to backup file or None
        """
        # Check if backup_dir exists
        if not self.backup_dir.exists():
            return None
        
        # Try to find matching backup
        relative_path = current_file.relative_to(Path.cwd()) if current_file.is_absolute() else current_file
        
        # Common backup patterns
        possible_backups = [
            self.backup_dir / relative_path,
            self.backup_dir / current_file.name,
        ]
        
        for backup in possible_backups:
            if backup.exists():
                return backup
        
        return None
    
    def _extract_function_names(self, tree: ast.AST) -> Set[str]:
        """Extract function and method names from AST.
        
        Args:
            tree: AST tree
            
        Returns:
            Set of function names
        """
        functions = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.add(node.name)
        return functions
    
    def _find_critical_areas(self, content: str, tree: ast.AST) -> List[str]:
        """Identify critical areas in the code.
        
        Args:
            content: Source code content
            tree: AST tree
            
        Returns:
            List of critical area descriptions
        """
        critical = []
        content_lower = content.lower()
        
        for pattern, category in self.CRITICAL_PATTERNS.items():
            if pattern in content_lower:
                critical.append(f"{category.value}: {pattern}")
        
        # Check for specific AST patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                critical.append(f"{ChangeCategory.ERROR_HANDLING.value}: exception handler")
            elif isinstance(node, ast.Try):
                critical.append(f"{ChangeCategory.ERROR_HANDLING.value}: try-except block")
        
        return list(set(critical))[:10]  # Return unique, limited to 10
    
    def _analyze_change_patterns(self, changes: List[str], location: str) -> List[RiskFactor]:
        """Analyze diff changes for risk patterns.
        
        Args:
            changes: Diff changes
            location: File location
            
        Returns:
            List of risk factors
        """
        risk_factors = []
        change_text = ''.join(changes).lower()
        
        # Check for critical change patterns
        patterns = {
            'except': (ChangeCategory.ERROR_HANDLING, "Exception handling modified"),
            'raise': (ChangeCategory.ERROR_HANDLING, "Exception raising modified"),
            'import': (ChangeCategory.IMPORTS, "Import statements changed"),
            'open(': (ChangeCategory.IO_OPERATIONS, "File operations changed"),
            'encode': (ChangeCategory.ENCODING, "Encoding operations changed"),
            'decode': (ChangeCategory.ENCODING, "Decoding operations changed"),
            '.items()': (ChangeCategory.ITERATOR, "Dictionary iteration changed"),
            '.keys()': (ChangeCategory.ITERATOR, "Dictionary keys iteration changed"),
            '.values()': (ChangeCategory.ITERATOR, "Dictionary values iteration changed"),
            'range(': (ChangeCategory.ITERATOR, "Range usage changed"),
            'unicode': (ChangeCategory.ENCODING, "Unicode handling changed"),
            'basestring': (ChangeCategory.TYPE_CONVERSION, "String type checking changed"),
            'print': (ChangeCategory.SYNTAX, "Print statements changed"),
        }
        
        for pattern, (category, description) in patterns.items():
            if pattern in change_text:
                weight = self.CATEGORY_WEIGHTS.get(category, 3.0)
                risk_factors.append(RiskFactor(
                    category=category.value,
                    description=description,
                    weight=weight,
                    location=location
                ))
        
        return risk_factors
    
    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Calculate risk level from score.
        
        Args:
            score: Numeric risk score
            
        Returns:
            RiskLevel enum
        """
        if score >= 30:
            return RiskLevel.CRITICAL
        elif score >= 20:
            return RiskLevel.HIGH
        elif score >= 10:
            return RiskLevel.MEDIUM
        elif score >= 5:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _generate_recommendations(
        self, 
        risk_level: RiskLevel, 
        risk_factors: List[RiskFactor],
        critical_areas: List[str]
    ) -> List[str]:
        """Generate recommendations based on risk assessment.
        
        Args:
            risk_level: Calculated risk level
            risk_factors: List of identified risk factors
            critical_areas: List of critical areas
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH):
            recommendations.append("⚠️  PRIORITY: Requires thorough manual code review")
            recommendations.append("⚠️  Add comprehensive unit tests before deploying")
            recommendations.append("⚠️  Consider peer review by senior developer")
        
        # Category-specific recommendations
        categories = {rf.category for rf in risk_factors}
        
        if ChangeCategory.ERROR_HANDLING.value in categories:
            recommendations.append("🔍 Review exception handling logic carefully")
            recommendations.append("🧪 Test error paths and edge cases")
        
        if ChangeCategory.ENCODING.value in categories:
            recommendations.append("🔤 Test with various character encodings (UTF-8, ASCII, etc.)")
            recommendations.append("🌍 Verify handling of non-ASCII characters")
        
        if ChangeCategory.IO_OPERATIONS.value in categories:
            recommendations.append("📁 Test file operations with different file types and sizes")
            recommendations.append("🔒 Verify file handling and resource cleanup")
        
        if ChangeCategory.DATABASE.value in categories:
            recommendations.append("🗄️  Review database queries and connection handling")
            recommendations.append("🧪 Test with actual database operations")
        
        if ChangeCategory.ITERATOR.value in categories:
            recommendations.append("🔄 Verify iterator behavior matches Python 2 expectations")
            recommendations.append("📊 Test with large datasets if applicable")
        
        if not recommendations:
            recommendations.append("✅ Standard code review recommended")
            recommendations.append("✅ Run existing test suite")
        
        return recommendations
    
    def _generate_summary(self) -> Dict:
        """Generate summary of risk analysis.
        
        Returns:
            dict: Summary data
        """
        if not self.assessments:
            return {
                'total_files_analyzed': 0,
                'risk_distribution': {},
                'high_risk_files': [],
                'recommendations': ['No changes detected or no backups available'],
                'assessments': []
            }
        
        # Calculate distributions
        risk_distribution = defaultdict(int)
        for assessment in self.assessments:
            risk_distribution[assessment.risk_level] += 1
        
        # Sort by risk score
        sorted_assessments = sorted(
            self.assessments, 
            key=lambda x: x.risk_score, 
            reverse=True
        )
        
        # Identify high-risk files
        high_risk = [
            {
                'file': a.file_path,
                'risk_level': a.risk_level,
                'risk_score': a.risk_score,
                'change_count': a.change_count
            }
            for a in sorted_assessments 
            if a.risk_level in ('critical', 'high')
        ]
        
        # Overall recommendations
        overall_recommendations = []
        if high_risk:
            overall_recommendations.append(
                f"⚠️  {len(high_risk)} high-risk files require priority review"
            )
            overall_recommendations.append(
                "🔍 Focus code review efforts on critical and high-risk files first"
            )
        
        critical_count = risk_distribution.get('critical', 0)
        if critical_count > 0:
            overall_recommendations.append(
                f"🚨 {critical_count} CRITICAL risk files need immediate attention"
            )
        
        if not high_risk:
            overall_recommendations.append(
                "✅ No high-risk changes detected - standard review process sufficient"
            )
        
        return {
            'total_files_analyzed': len(self.assessments),
            'total_changes': sum(a.change_count for a in self.assessments),
            'average_risk_score': round(
                sum(a.risk_score for a in self.assessments) / len(self.assessments), 2
            ),
            'risk_distribution': dict(risk_distribution),
            'high_risk_files': high_risk,
            'top_risk_files': [
                {
                    'file': a.file_path,
                    'risk_level': a.risk_level,
                    'risk_score': a.risk_score,
                    'top_factors': [rf['description'] for rf in a.risk_factors[:3]]
                }
                for a in sorted_assessments[:10]
            ],
            'recommendations': overall_recommendations,
            'assessments': [asdict(a) for a in sorted_assessments]
        }
    
    def format_report(self, summary: Dict, detailed: bool = False) -> str:
        """Format risk analysis as a readable report.
        
        Args:
            summary: Summary data from analyze_project
            detailed: Include detailed per-file analysis
            
        Returns:
            str: Formatted report
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("MIGRATION RISK ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary statistics
        lines.append("📊 OVERALL STATISTICS")
        lines.append("-" * 70)
        lines.append(f"Files Analyzed: {summary['total_files_analyzed']}")
        lines.append(f"Total Changes: {summary.get('total_changes', 0)} lines")
        if summary['total_files_analyzed'] > 0:
            lines.append(f"Average Risk Score: {summary.get('average_risk_score', 0)}")
        lines.append("")
        
        # Risk distribution
        if summary['risk_distribution']:
            lines.append("📈 RISK DISTRIBUTION")
            lines.append("-" * 70)
            risk_order = ['critical', 'high', 'medium', 'low', 'minimal']
            for level in risk_order:
                count = summary['risk_distribution'].get(level, 0)
                if count > 0:
                    emoji = {
                        'critical': '🚨',
                        'high': '⚠️ ',
                        'medium': '⚡',
                        'low': '📝',
                        'minimal': '✅'
                    }.get(level, '•')
                    lines.append(f"{emoji} {level.upper()}: {count} files")
            lines.append("")
        
        # High-risk files
        if summary['high_risk_files']:
            lines.append("🎯 HIGH-RISK FILES (PRIORITY REVIEW)")
            lines.append("-" * 70)
            for item in summary['high_risk_files'][:15]:
                file_name = Path(item['file']).name
                lines.append(
                    f"  {item['risk_level'].upper():10} | "
                    f"Score: {item['risk_score']:5.1f} | "
                    f"Changes: {item['change_count']:3} | "
                    f"{file_name}"
                )
            lines.append("")
        
        # Top risk files
        if summary.get('top_risk_files'):
            lines.append("📋 TOP 10 FILES BY RISK SCORE")
            lines.append("-" * 70)
            for i, item in enumerate(summary['top_risk_files'][:10], 1):
                file_name = Path(item['file']).name
                lines.append(f"{i:2}. {file_name} (Score: {item['risk_score']})")
                if item.get('top_factors'):
                    for factor in item['top_factors'][:2]:
                        lines.append(f"     • {factor}")
            lines.append("")
        
        # Recommendations
        if summary['recommendations']:
            lines.append("💡 RECOMMENDATIONS")
            lines.append("-" * 70)
            for rec in summary['recommendations']:
                lines.append(f"  {rec}")
            lines.append("")
        
        # Detailed per-file analysis
        if detailed and summary.get('assessments'):
            lines.append("=" * 70)
            lines.append("DETAILED FILE ANALYSIS")
            lines.append("=" * 70)
            lines.append("")
            
            for assessment in summary['assessments'][:20]:  # Limit to 20 files
                lines.append(f"File: {assessment['file_path']}")
                lines.append(f"Risk Level: {assessment['risk_level'].upper()}")
                lines.append(f"Risk Score: {assessment['risk_score']}")
                lines.append(f"Changes: {assessment['change_count']} lines")
                
                if assessment['critical_areas']:
                    lines.append("Critical Areas:")
                    for area in assessment['critical_areas'][:5]:
                        lines.append(f"  • {area}")
                
                if assessment['recommendations']:
                    lines.append("Recommendations:")
                    for rec in assessment['recommendations'][:3]:
                        lines.append(f"  • {rec}")
                
                lines.append("-" * 70)
                lines.append("")
        
        return "\n".join(lines)
    
    def export_json(self, summary: Dict, output_file: str):
        """Export analysis results to JSON file.
        
        Args:
            summary: Summary data from analyze_project
            output_file: Path to output JSON file
        """
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)


def main():
    """Command-line interface for risk analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze migration risks and prioritize code review'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='src',
        help='Path to analyze (default: src)'
    )
    parser.add_argument(
        '--backup-dir',
        default='backups',
        help='Backup directory path (default: backups)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for report'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    parser.add_argument(
        '-d', '--detailed',
        action='store_true',
        help='Include detailed per-file analysis'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = MigrationRiskAnalyzer(
        backup_dir=args.backup_dir,
        source_dir=args.path
    )
    
    print(f"Analyzing migration risks in: {args.path}")
    print(f"Using backups from: {args.backup_dir}")
    print()
    
    summary = analyzer.analyze_project(args.path)
    
    # Output results
    if args.json:
        if args.output:
            analyzer.export_json(summary, args.output)
            print(f"✅ JSON report saved to: {args.output}")
        else:
            print(json.dumps(summary, indent=2))
    else:
        report = analyzer.format_report(summary, detailed=args.detailed)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"✅ Report saved to: {args.output}")
        else:
            print(report)


if __name__ == '__main__':
    main()
