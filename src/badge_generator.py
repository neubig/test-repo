#!/usr/bin/env python3
"""
Badge Generator for Python 2 to 3 Migration Progress

Generates beautiful SVG badges showing migration progress that can be embedded
in README files, documentation, and project dashboards.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class BadgeGenerator:
    """Generate SVG badges for migration progress visualization."""
    
    # Color schemes for different progress levels
    COLORS = {
        'red': '#e05d44',
        'orange': '#fe7d37',
        'yellow': '#dfb317',
        'yellowgreen': '#a4a61d',
        'green': '#97ca00',
        'brightgreen': '#4c1',
        'blue': '#007ec6',
        'lightgrey': '#9f9f9f',
        'grey': '#555',
    }
    
    def __init__(self, output_dir: str = "badges"):
        """
        Initialize badge generator.
        
        Args:
            output_dir: Directory to save generated badges
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load migration statistics from stats tracker."""
        stats_file = Path(".migration_stats.json")
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    # Get the most recent snapshot
                    if 'snapshots' in data and data['snapshots']:
                        return data['snapshots'][-1]
                    return data
            except (json.JSONDecodeError, KeyError):
                pass
        return self._collect_current_stats()
    
    def _collect_current_stats(self) -> Dict:
        """Collect current statistics by running verifier."""
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from verifier import Python3CompatibilityVerifier
            
            verifier = Python3CompatibilityVerifier()
            verifier.verify_directory('.')
            
            total_files = len(verifier.files_checked)
            issues = verifier.issues_found
            files_with_issues = len(set(issue.get('file', '') for issue in issues))
            
            return {
                'total_files': total_files,
                'files_with_issues': files_with_issues,
                'files_clean': total_files - files_with_issues,
                'total_issues': len(issues),
                'timestamp': None
            }
        except Exception as e:
            print(f"Warning: Could not collect stats: {e}", file=sys.stderr)
            return {
                'total_files': 0,
                'files_with_issues': 0,
                'files_clean': 0,
                'total_issues': 0,
                'timestamp': None
            }
    
    def _get_color_for_percentage(self, percentage: float) -> str:
        """Get appropriate color based on completion percentage."""
        if percentage >= 95:
            return self.COLORS['brightgreen']
        elif percentage >= 80:
            return self.COLORS['green']
        elif percentage >= 60:
            return self.COLORS['yellowgreen']
        elif percentage >= 40:
            return self.COLORS['yellow']
        elif percentage >= 20:
            return self.COLORS['orange']
        else:
            return self.COLORS['red']
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status badge."""
        status_colors = {
            'not started': self.COLORS['red'],
            'in progress': self.COLORS['yellow'],
            'nearly complete': self.COLORS['yellowgreen'],
            'complete': self.COLORS['brightgreen'],
            'compatible': self.COLORS['brightgreen'],
            'issues found': self.COLORS['orange'],
        }
        return status_colors.get(status.lower(), self.COLORS['blue'])
    
    def _calculate_text_width(self, text: str) -> int:
        """Calculate approximate pixel width of text (simplified)."""
        # Approximate character widths for Verdana 11px
        return len(text) * 7 + 10
    
    def _generate_svg_badge(self, label: str, value: str, color: str) -> str:
        """
        Generate SVG badge markup.
        
        Args:
            label: Left side label text
            value: Right side value text
            color: Color for the value side (hex or color name)
            
        Returns:
            SVG markup as string
        """
        # Calculate dimensions
        label_width = self._calculate_text_width(label)
        value_width = self._calculate_text_width(value)
        total_width = label_width + value_width
        
        label_x = label_width / 2
        value_x = label_width + (value_width / 2)
        
        # Resolve color name to hex if needed
        badge_color = self.COLORS.get(color, color)
        
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
    <title>{label}: {value}</title>
    <linearGradient id="s" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="r">
        <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#r)">
        <rect width="{label_width}" height="20" fill="#555"/>
        <rect x="{label_width}" width="{value_width}" height="20" fill="{badge_color}"/>
        <rect width="{total_width}" height="20" fill="url(#s)"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
        <text aria-hidden="true" x="{label_x * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(label_width - 10) * 10}">{label}</text>
        <text x="{label_x * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(label_width - 10) * 10}">{label}</text>
        <text aria-hidden="true" x="{value_x * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(value_width - 10) * 10}">{value}</text>
        <text x="{value_x * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(value_width - 10) * 10}">{value}</text>
    </g>
</svg>'''
        return svg
    
    def generate_progress_badge(self) -> Tuple[str, str]:
        """Generate migration progress percentage badge."""
        total_files = self.stats.get('total_files', 0)
        files_clean = self.stats.get('files_clean', 0)
        
        if total_files == 0:
            percentage = 0
            value = "no files"
        else:
            percentage = (files_clean / total_files) * 100
            value = f"{percentage:.0f}%"
        
        color = self._get_color_for_percentage(percentage)
        svg = self._generate_svg_badge("migration progress", value, color)
        
        filename = "migration-progress.svg"
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(svg)
        
        return str(filepath), f"![Migration Progress](badges/{filename})"
    
    def generate_files_badge(self) -> Tuple[str, str]:
        """Generate files migrated count badge."""
        total_files = self.stats.get('total_files', 0)
        files_clean = self.stats.get('files_clean', 0)
        
        value = f"{files_clean}/{total_files}"
        
        if total_files == 0:
            percentage = 0
        else:
            percentage = (files_clean / total_files) * 100
        
        color = self._get_color_for_percentage(percentage)
        svg = self._generate_svg_badge("files migrated", value, color)
        
        filename = "files-migrated.svg"
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(svg)
        
        return str(filepath), f"![Files Migrated](badges/{filename})"
    
    def generate_issues_badge(self) -> Tuple[str, str]:
        """Generate issues remaining badge."""
        total_issues = self.stats.get('total_issues', 0)
        
        if total_issues == 0:
            value = "none"
            color = self.COLORS['brightgreen']
        elif total_issues <= 5:
            value = str(total_issues)
            color = self.COLORS['yellowgreen']
        elif total_issues <= 20:
            value = str(total_issues)
            color = self.COLORS['yellow']
        elif total_issues <= 50:
            value = str(total_issues)
            color = self.COLORS['orange']
        else:
            value = str(total_issues)
            color = self.COLORS['red']
        
        svg = self._generate_svg_badge("issues remaining", value, color)
        
        filename = "issues-remaining.svg"
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(svg)
        
        return str(filepath), f"![Issues Remaining](badges/{filename})"
    
    def generate_status_badge(self) -> Tuple[str, str]:
        """Generate overall migration status badge."""
        total_files = self.stats.get('total_files', 0)
        files_clean = self.stats.get('files_clean', 0)
        
        if total_files == 0:
            status = "unknown"
            color = self.COLORS['lightgrey']
        else:
            percentage = (files_clean / total_files) * 100
            if percentage >= 100:
                status = "complete"
            elif percentage >= 90:
                status = "nearly complete"
            elif percentage > 0:
                status = "in progress"
            else:
                status = "not started"
            color = self._get_status_color(status)
        
        svg = self._generate_svg_badge("migration", status, color)
        
        filename = "migration-status.svg"
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(svg)
        
        return str(filepath), f"![Migration Status](badges/{filename})"
    
    def generate_python_version_badge(self) -> Tuple[str, str]:
        """Generate Python version compatibility badge."""
        total_issues = self.stats.get('total_issues', 0)
        
        if total_issues == 0:
            value = "3.x ready"
            color = self.COLORS['brightgreen']
        else:
            value = "2.x only"
            color = self.COLORS['red']
        
        svg = self._generate_svg_badge("python", value, color)
        
        filename = "python-version.svg"
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(svg)
        
        return str(filepath), f"![Python Version](badges/{filename})"
    
    def generate_all_badges(self, verbose: bool = True) -> Dict[str, Tuple[str, str]]:
        """
        Generate all badges.
        
        Args:
            verbose: Print progress information
            
        Returns:
            Dictionary mapping badge names to (filepath, markdown) tuples
        """
        badges = {}
        
        if verbose:
            print("Generating migration progress badges...")
            print()
        
        # Generate each badge type
        badge_generators = [
            ('status', 'Migration Status', self.generate_status_badge),
            ('progress', 'Progress Percentage', self.generate_progress_badge),
            ('files', 'Files Migrated', self.generate_files_badge),
            ('issues', 'Issues Remaining', self.generate_issues_badge),
            ('python', 'Python Version', self.generate_python_version_badge),
        ]
        
        for key, name, generator in badge_generators:
            try:
                filepath, markdown = generator()
                badges[key] = (filepath, markdown)
                if verbose:
                    print(f"✓ Generated {name} badge: {filepath}")
            except Exception as e:
                if verbose:
                    print(f"✗ Failed to generate {name} badge: {e}", file=sys.stderr)
        
        if verbose:
            print()
            print(f"All badges saved to: {self.output_dir}/")
        
        return badges
    
    def generate_markdown_snippet(self, badges: Dict[str, Tuple[str, str]]) -> str:
        """
        Generate markdown snippet for embedding badges.
        
        Args:
            badges: Dictionary of badge information
            
        Returns:
            Markdown snippet
        """
        lines = [
            "<!-- Migration Progress Badges -->",
            ""
        ]
        
        # Add each badge's markdown
        for key, (filepath, markdown) in badges.items():
            lines.append(markdown)
        
        lines.append("")
        lines.append("<!-- Generated by py2to3 badge generator -->")
        
        return "\n".join(lines)
    
    def save_markdown_snippet(self, badges: Dict[str, Tuple[str, str]], 
                             output_file: str = "badges/README_SNIPPET.md") -> str:
        """
        Save markdown snippet to file.
        
        Args:
            badges: Dictionary of badge information
            output_file: Path to save snippet
            
        Returns:
            Path to saved file
        """
        snippet = self.generate_markdown_snippet(badges)
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(snippet)
        
        return str(output_path)


def main():
    """Main entry point for badge generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate migration progress badges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all badges
  python badge_generator.py
  
  # Generate badges to custom directory
  python badge_generator.py --output custom_badges/
  
  # Generate silently
  python badge_generator.py --quiet
  
  # Generate specific badge types
  python badge_generator.py --types progress,files,status
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        default='badges',
        help='Output directory for badges (default: badges/)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    parser.add_argument(
        '--types',
        help='Comma-separated list of badge types (status,progress,files,issues,python)'
    )
    
    parser.add_argument(
        '--no-snippet',
        action='store_true',
        help='Do not generate markdown snippet file'
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = BadgeGenerator(output_dir=args.output)
    
    # Generate badges
    if args.types:
        # Generate specific types
        badge_types = [t.strip() for t in args.types.split(',')]
        badges = {}
        
        type_map = {
            'status': ('Migration Status', generator.generate_status_badge),
            'progress': ('Progress Percentage', generator.generate_progress_badge),
            'files': ('Files Migrated', generator.generate_files_badge),
            'issues': ('Issues Remaining', generator.generate_issues_badge),
            'python': ('Python Version', generator.generate_python_version_badge),
        }
        
        for badge_type in badge_types:
            if badge_type in type_map:
                name, gen_func = type_map[badge_type]
                try:
                    filepath, markdown = gen_func()
                    badges[badge_type] = (filepath, markdown)
                    if not args.quiet:
                        print(f"✓ Generated {name} badge: {filepath}")
                except Exception as e:
                    print(f"✗ Failed to generate {name} badge: {e}", file=sys.stderr)
            else:
                print(f"✗ Unknown badge type: {badge_type}", file=sys.stderr)
    else:
        # Generate all badges
        badges = generator.generate_all_badges(verbose=not args.quiet)
    
    # Generate markdown snippet
    if not args.no_snippet and badges:
        snippet_file = generator.save_markdown_snippet(
            badges, 
            output_file=f"{args.output}/README_SNIPPET.md"
        )
        if not args.quiet:
            print()
            print(f"Markdown snippet saved to: {snippet_file}")
            print()
            print("Add these badges to your README.md:")
            print("-" * 50)
            with open(snippet_file, 'r') as f:
                print(f.read())


if __name__ == "__main__":
    main()
