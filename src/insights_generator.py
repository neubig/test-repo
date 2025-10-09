#!/usr/bin/env python3
"""
Migration Insights Generator

Analyzes migration data to provide actionable insights, identify patterns,
suggest optimizations, and generate strategic recommendations for improving
the migration process.
"""

import os
import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import re


class MigrationInsightsGenerator:
    """Generate actionable insights from migration data."""
    
    def __init__(self, project_dir="."):
        self.project_dir = Path(project_dir)
        self.insights = {
            "summary": {},
            "patterns": {},
            "recommendations": [],
            "automation_opportunities": [],
            "risk_factors": [],
            "efficiency_metrics": {},
            "learning_opportunities": []
        }
        
    def analyze(self):
        """Run comprehensive analysis and generate insights."""
        print("🔍 Analyzing migration data...")
        
        self._load_migration_data()
        self._analyze_patterns()
        self._identify_automation_opportunities()
        self._analyze_efficiency()
        self._generate_recommendations()
        self._identify_learning_opportunities()
        
        print("✅ Analysis complete!")
        return self.insights
    
    def _load_migration_data(self):
        """Load data from various migration tools."""
        # Load stats
        stats_file = self.project_dir / ".migration_stats" / "stats.json"
        if stats_file.exists():
            with open(stats_file) as f:
                self.stats = json.load(f)
        else:
            self.stats = {}
            
        # Load migration state
        state_file = self.project_dir / ".migration_state.json"
        if state_file.exists():
            with open(state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {}
            
        # Load journal entries
        journal_file = self.project_dir / ".migration_journal.json"
        if journal_file.exists():
            with open(journal_file) as f:
                self.journal = json.load(f)
        else:
            self.journal = {"entries": []}
            
        # Load session data
        session_file = self.project_dir / ".migration_sessions.json"
        if session_file.exists():
            with open(session_file) as f:
                self.sessions = json.load(f)
        else:
            self.sessions = {"sessions": []}
    
    def _analyze_patterns(self):
        """Analyze common patterns in the migration."""
        pattern_counts = Counter()
        pattern_complexity = defaultdict(list)
        
        # Analyze from state data
        for file_path, data in self.state.get("files", {}).items():
            issues = data.get("issues", [])
            for issue in issues:
                issue_type = issue.get("type", "unknown")
                pattern_counts[issue_type] += 1
                pattern_complexity[issue_type].append(issue.get("severity", "medium"))
        
        # Calculate pattern statistics
        total_patterns = sum(pattern_counts.values())
        self.insights["patterns"] = {
            "total_unique_patterns": len(pattern_counts),
            "total_occurrences": total_patterns,
            "most_common": pattern_counts.most_common(10),
            "pattern_distribution": dict(pattern_counts)
        }
        
        # Identify high-impact patterns (frequent + high severity)
        high_impact = []
        for pattern, count in pattern_counts.items():
            severity_list = pattern_complexity[pattern]
            high_severity_count = sum(1 for s in severity_list if s == "high")
            if count > total_patterns * 0.1 or high_severity_count > count * 0.5:
                high_impact.append({
                    "pattern": pattern,
                    "count": count,
                    "severity": "high" if high_severity_count > count * 0.5 else "medium"
                })
        
        self.insights["patterns"]["high_impact"] = high_impact
    
    def _identify_automation_opportunities(self):
        """Identify patterns that could be automated."""
        opportunities = []
        
        # Look for repetitive patterns
        if self.insights["patterns"].get("most_common"):
            for pattern, count in self.insights["patterns"]["most_common"][:5]:
                if count >= 10:  # Threshold for automation
                    opportunities.append({
                        "pattern": pattern,
                        "occurrences": count,
                        "recommendation": f"Create custom rule for '{pattern}' (appears {count} times)",
                        "estimated_time_saved": f"{count * 2} minutes",
                        "priority": "high" if count >= 50 else "medium"
                    })
        
        # Analyze journal for manual work
        manual_patterns = []
        for entry in self.journal.get("entries", []):
            if "manual" in entry.get("notes", "").lower():
                manual_patterns.append(entry.get("notes", ""))
        
        if manual_patterns:
            opportunities.append({
                "pattern": "manual_fixes",
                "occurrences": len(manual_patterns),
                "recommendation": "Review manual fixes for automation potential",
                "priority": "medium"
            })
        
        self.insights["automation_opportunities"] = opportunities
    
    def _analyze_efficiency(self):
        """Analyze migration efficiency and velocity."""
        efficiency = {}
        
        # Calculate velocity from sessions
        sessions = self.sessions.get("sessions", [])
        if sessions:
            total_time = sum(s.get("duration", 0) for s in sessions)
            total_files = sum(len(s.get("files_modified", [])) for s in sessions)
            
            if total_time > 0:
                efficiency["avg_time_per_file"] = total_time / max(total_files, 1)
                efficiency["files_per_hour"] = (total_files / total_time) * 3600 if total_time > 0 else 0
                efficiency["total_sessions"] = len(sessions)
                efficiency["total_hours"] = total_time / 3600
        
        # Calculate progress rate
        if self.stats:
            total_issues = self.stats.get("total_issues", 0)
            resolved_issues = self.stats.get("resolved_issues", 0)
            if total_issues > 0:
                efficiency["completion_rate"] = (resolved_issues / total_issues) * 100
                efficiency["remaining_issues"] = total_issues - resolved_issues
        
        # Estimate time to completion
        if efficiency.get("files_per_hour") and self.state:
            remaining_files = sum(1 for f, d in self.state.get("files", {}).items() 
                                if d.get("status") != "completed")
            if efficiency["files_per_hour"] > 0:
                efficiency["estimated_hours_remaining"] = remaining_files / efficiency["files_per_hour"]
        
        self.insights["efficiency_metrics"] = efficiency
    
    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        recommendations = []
        
        # Efficiency recommendations
        efficiency = self.insights.get("efficiency_metrics", {})
        if efficiency.get("avg_time_per_file", 0) > 1800:  # > 30 minutes per file
            recommendations.append({
                "category": "efficiency",
                "priority": "high",
                "title": "Optimize migration workflow",
                "description": "Average time per file is high. Consider using automated tools more extensively.",
                "action": "Run './py2to3 fix' to automate common patterns"
            })
        
        # Pattern-based recommendations
        high_impact = self.insights.get("patterns", {}).get("high_impact", [])
        if high_impact:
            top_pattern = high_impact[0]
            recommendations.append({
                "category": "patterns",
                "priority": "high",
                "title": f"Focus on '{top_pattern['pattern']}' pattern",
                "description": f"This pattern appears frequently ({top_pattern['count']} times) and should be prioritized.",
                "action": f"Use './py2to3 search {top_pattern['pattern']}' to locate all instances"
            })
        
        # Automation recommendations
        auto_opps = self.insights.get("automation_opportunities", [])
        high_priority_auto = [o for o in auto_opps if o.get("priority") == "high"]
        if high_priority_auto:
            recommendations.append({
                "category": "automation",
                "priority": "high",
                "title": "Create custom automation rules",
                "description": f"Found {len(high_priority_auto)} patterns suitable for automation.",
                "action": "Use './py2to3 rules create' to define custom rules"
            })
        
        # Testing recommendations
        if not self._has_test_coverage():
            recommendations.append({
                "category": "testing",
                "priority": "high",
                "title": "Increase test coverage",
                "description": "Limited test coverage detected. Tests are crucial for safe migration.",
                "action": "Use './py2to3 test-gen' to generate test cases"
            })
        
        # Documentation recommendations
        if not self._has_migration_docs():
            recommendations.append({
                "category": "documentation",
                "priority": "medium",
                "title": "Document migration decisions",
                "description": "Keep a record of migration decisions and rationale.",
                "action": "Use './py2to3 journal add' to document decisions"
            })
        
        # Progress tracking recommendations
        completion_rate = efficiency.get("completion_rate", 0)
        if completion_rate > 50 and not self._has_precommit_hooks():
            recommendations.append({
                "category": "quality",
                "priority": "medium",
                "title": "Install pre-commit hooks",
                "description": "Prevent Python 2 code from being reintroduced.",
                "action": "Run './py2to3 precommit install'"
            })
        
        self.insights["recommendations"] = recommendations
    
    def _identify_learning_opportunities(self):
        """Identify learning opportunities for the team."""
        opportunities = []
        
        # Identify complex patterns
        patterns = self.insights.get("patterns", {})
        if patterns.get("high_impact"):
            opportunities.append({
                "topic": "Common Migration Patterns",
                "description": "Your codebase has several high-impact patterns worth understanding deeply.",
                "resource": "Run './py2to3 patterns' to learn about migration patterns"
            })
        
        # Suggest pattern library if many different patterns
        if patterns.get("total_unique_patterns", 0) > 10:
            opportunities.append({
                "topic": "Pattern Library",
                "description": "With many unique patterns, the pattern library can be a valuable reference.",
                "resource": "Browse with './py2to3 patterns'"
            })
        
        # Suggest wizard for beginners
        if not self.sessions.get("sessions"):
            opportunities.append({
                "topic": "Migration Wizard",
                "description": "New to migration? Try the interactive wizard for guided workflow.",
                "resource": "Start with './py2to3 wizard'"
            })
        
        self.insights["learning_opportunities"] = opportunities
    
    def _has_test_coverage(self):
        """Check if project has test coverage tracking."""
        coverage_file = self.project_dir / ".migration_coverage.json"
        return coverage_file.exists()
    
    def _has_migration_docs(self):
        """Check if migration is documented."""
        journal_entries = len(self.journal.get("entries", []))
        return journal_entries > 5
    
    def _has_precommit_hooks(self):
        """Check if pre-commit hooks are installed."""
        precommit_file = self.project_dir / ".pre-commit-config.yaml"
        return precommit_file.exists()
    
    def generate_report(self, output_format="text"):
        """Generate insights report in specified format."""
        if output_format == "text":
            return self._generate_text_report()
        elif output_format == "json":
            return json.dumps(self.insights, indent=2)
        elif output_format == "markdown":
            return self._generate_markdown_report()
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _generate_text_report(self):
        """Generate human-readable text report."""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("  🔍 MIGRATION INSIGHTS REPORT")
        lines.append("=" * 70)
        lines.append(f"\n📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary
        lines.append("\n📊 EFFICIENCY METRICS")
        lines.append("-" * 70)
        efficiency = self.insights.get("efficiency_metrics", {})
        if efficiency:
            if "total_sessions" in efficiency:
                lines.append(f"  • Total Sessions: {efficiency['total_sessions']}")
                lines.append(f"  • Total Hours: {efficiency.get('total_hours', 0):.1f}")
            if "completion_rate" in efficiency:
                lines.append(f"  • Completion Rate: {efficiency['completion_rate']:.1f}%")
            if "files_per_hour" in efficiency:
                lines.append(f"  • Files per Hour: {efficiency['files_per_hour']:.2f}")
            if "estimated_hours_remaining" in efficiency:
                lines.append(f"  • Estimated Hours Remaining: {efficiency['estimated_hours_remaining']:.1f}")
        else:
            lines.append("  No efficiency data available yet.")
        
        # Patterns
        lines.append("\n\n🔍 PATTERN ANALYSIS")
        lines.append("-" * 70)
        patterns = self.insights.get("patterns", {})
        if patterns.get("total_unique_patterns"):
            lines.append(f"  • Total Unique Patterns: {patterns['total_unique_patterns']}")
            lines.append(f"  • Total Occurrences: {patterns['total_occurrences']}")
            lines.append("\n  Most Common Patterns:")
            for pattern, count in patterns.get("most_common", [])[:5]:
                lines.append(f"    - {pattern}: {count} occurrences")
        else:
            lines.append("  No pattern data available yet.")
        
        # Automation Opportunities
        lines.append("\n\n⚡ AUTOMATION OPPORTUNITIES")
        lines.append("-" * 70)
        auto_opps = self.insights.get("automation_opportunities", [])
        if auto_opps:
            for opp in auto_opps[:5]:
                lines.append(f"\n  [{opp['priority'].upper()}] {opp['recommendation']}")
                if "estimated_time_saved" in opp:
                    lines.append(f"  💰 Potential time saved: {opp['estimated_time_saved']}")
        else:
            lines.append("  No automation opportunities identified yet.")
        
        # Recommendations
        lines.append("\n\n💡 RECOMMENDATIONS")
        lines.append("-" * 70)
        recommendations = self.insights.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"\n  {i}. [{rec['priority'].upper()}] {rec['title']}")
                lines.append(f"     {rec['description']}")
                lines.append(f"     ➡️  {rec['action']}")
        else:
            lines.append("  No recommendations at this time.")
        
        # Learning Opportunities
        lines.append("\n\n📚 LEARNING OPPORTUNITIES")
        lines.append("-" * 70)
        learning = self.insights.get("learning_opportunities", [])
        if learning:
            for opp in learning:
                lines.append(f"\n  • {opp['topic']}")
                lines.append(f"    {opp['description']}")
                lines.append(f"    💡 {opp['resource']}")
        else:
            lines.append("  Keep up the great work!")
        
        lines.append("\n" + "=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self):
        """Generate markdown formatted report."""
        lines = []
        lines.append("# 🔍 Migration Insights Report\n")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")
        
        # Efficiency Metrics
        lines.append("## 📊 Efficiency Metrics\n")
        efficiency = self.insights.get("efficiency_metrics", {})
        if efficiency:
            for key, value in efficiency.items():
                formatted_key = key.replace("_", " ").title()
                if isinstance(value, float):
                    lines.append(f"- **{formatted_key}:** {value:.2f}")
                else:
                    lines.append(f"- **{formatted_key}:** {value}")
        else:
            lines.append("No efficiency data available yet.\n")
        
        # Pattern Analysis
        lines.append("\n## 🔍 Pattern Analysis\n")
        patterns = self.insights.get("patterns", {})
        if patterns.get("most_common"):
            lines.append("### Most Common Patterns\n")
            lines.append("| Pattern | Occurrences |")
            lines.append("|---------|-------------|")
            for pattern, count in patterns.get("most_common", [])[:10]:
                lines.append(f"| `{pattern}` | {count} |")
        
        # Automation Opportunities
        lines.append("\n## ⚡ Automation Opportunities\n")
        auto_opps = self.insights.get("automation_opportunities", [])
        if auto_opps:
            for opp in auto_opps:
                priority_emoji = "🔴" if opp['priority'] == "high" else "🟡"
                lines.append(f"### {priority_emoji} {opp['recommendation']}\n")
                if "estimated_time_saved" in opp:
                    lines.append(f"**Potential time saved:** {opp['estimated_time_saved']}\n")
        
        # Recommendations
        lines.append("\n## 💡 Recommendations\n")
        recommendations = self.insights.get("recommendations", [])
        for rec in recommendations:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec['priority'], "⚪")
            lines.append(f"### {priority_emoji} {rec['title']}\n")
            lines.append(f"**Category:** {rec['category'].title()}\n")
            lines.append(f"{rec['description']}\n")
            lines.append(f"**Action:** `{rec['action']}`\n")
        
        # Learning Opportunities
        lines.append("\n## 📚 Learning Opportunities\n")
        learning = self.insights.get("learning_opportunities", [])
        for opp in learning:
            lines.append(f"### {opp['topic']}\n")
            lines.append(f"{opp['description']}\n")
            lines.append(f"💡 {opp['resource']}\n")
        
        return "\n".join(lines)
    
    def save_report(self, filename, output_format="text"):
        """Save insights report to file."""
        report = self.generate_report(output_format)
        output_path = self.project_dir / filename
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        return output_path


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate migration insights and recommendations"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save report to file"
    )
    
    args = parser.parse_args()
    
    generator = MigrationInsightsGenerator(args.project_dir)
    generator.analyze()
    
    if args.output:
        output_path = generator.save_report(args.output, args.format)
        print(f"\n✅ Report saved to: {output_path}")
    else:
        report = generator.generate_report(args.format)
        print(report)


if __name__ == "__main__":
    main()
