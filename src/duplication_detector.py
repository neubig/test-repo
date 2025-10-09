#!/usr/bin/env python3
"""
Code Duplication Detector

Identifies duplicated and similar code blocks across the codebase.
Helps reduce migration work by finding consolidation opportunities.
"""

import ast
import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class CodeBlock:
    """Represents a block of code with metadata."""
    
    def __init__(self, file_path: str, start_line: int, end_line: int, content: str, hash_value: str):
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.content = content
        self.hash = hash_value
        self.lines_count = end_line - start_line + 1
    
    def __repr__(self):
        return f"CodeBlock({self.file_path}:{self.start_line}-{self.end_line})"


class DuplicationDetector:
    """Detects code duplication and similarity in Python codebases."""
    
    def __init__(self, min_lines: int = 5, similarity_threshold: float = 0.8):
        """
        Initialize the duplication detector.
        
        Args:
            min_lines: Minimum number of lines to consider as a block
            similarity_threshold: Threshold for considering blocks similar (0.0-1.0)
        """
        self.min_lines = min_lines
        self.similarity_threshold = similarity_threshold
        self.blocks = []
        self.exact_duplicates = defaultdict(list)
        self.similar_groups = []
        self.stats = {
            'files_analyzed': 0,
            'total_lines': 0,
            'duplicate_lines': 0,
            'duplicate_blocks': 0,
        }
    
    def analyze_directory(self, directory: str, exclude_patterns: List[str] = None) -> None:
        """
        Analyze all Python files in a directory for duplication.
        
        Args:
            directory: Path to directory to analyze
            exclude_patterns: List of patterns to exclude (e.g., ['test_', '__pycache__'])
        """
        if exclude_patterns is None:
            exclude_patterns = ['test_', '__pycache__', '.venv', 'venv', '.git', 'build', 'dist']
        
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        self.analyze_file(file_path)
                    except Exception as e:
                        print(f"Warning: Could not analyze {file_path}: {e}")
    
    def analyze_file(self, file_path: str) -> None:
        """Analyze a single Python file for code blocks."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        self.stats['files_analyzed'] += 1
        self.stats['total_lines'] += len(lines)
        
        # Extract code blocks using a sliding window
        for i in range(len(lines) - self.min_lines + 1):
            block_lines = lines[i:i + self.min_lines]
            
            # Skip blocks that are mostly empty or comments
            significant_lines = [
                line for line in block_lines 
                if line.strip() and not line.strip().startswith('#')
            ]
            if len(significant_lines) < self.min_lines // 2:
                continue
            
            # Normalize the code block for comparison
            normalized = self._normalize_code('\n'.join(block_lines))
            if len(normalized.strip()) < 10:  # Skip trivial blocks
                continue
            
            block_hash = self._hash_code(normalized)
            
            block = CodeBlock(
                file_path=file_path,
                start_line=i + 1,
                end_line=i + self.min_lines,
                content='\n'.join(block_lines),
                hash_value=block_hash
            )
            
            self.blocks.append(block)
            self.exact_duplicates[block_hash].append(block)
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison by removing variable names and whitespace."""
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in code.split('\n')]
        
        # Remove empty lines
        lines = [line for line in lines if line]
        
        # Join back together
        normalized = '\n'.join(lines)
        
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def _hash_code(self, code: str) -> str:
        """Generate a hash for a code block."""
        return hashlib.md5(code.encode()).hexdigest()
    
    def find_duplicates(self) -> Dict[str, List[CodeBlock]]:
        """
        Find exact duplicate code blocks.
        
        Returns:
            Dictionary mapping hash to list of duplicate blocks
        """
        # Filter to only hashes with more than one block
        duplicates = {
            hash_val: blocks 
            for hash_val, blocks in self.exact_duplicates.items() 
            if len(blocks) > 1
        }
        
        # Calculate statistics
        duplicate_blocks_set = set()
        for blocks in duplicates.values():
            for block in blocks:
                duplicate_blocks_set.add((block.file_path, block.start_line))
        
        self.stats['duplicate_blocks'] = len(duplicate_blocks_set)
        self.stats['duplicate_lines'] = sum(
            block.lines_count for blocks in duplicates.values() for block in blocks
        )
        
        return duplicates
    
    def calculate_similarity(self, block1: CodeBlock, block2: CodeBlock) -> float:
        """
        Calculate similarity between two code blocks using a simple metric.
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        lines1 = set(block1.content.split('\n'))
        lines2 = set(block2.content.split('\n'))
        
        if not lines1 or not lines2:
            return 0.0
        
        intersection = len(lines1 & lines2)
        union = len(lines1 | lines2)
        
        return intersection / union if union > 0 else 0.0
    
    def generate_report(self, format: str = 'text') -> str:
        """
        Generate a duplication report.
        
        Args:
            format: Output format ('text', 'json', or 'html')
        
        Returns:
            Formatted report string
        """
        duplicates = self.find_duplicates()
        
        if format == 'json':
            return self._generate_json_report(duplicates)
        elif format == 'html':
            return self._generate_html_report(duplicates)
        else:
            return self._generate_text_report(duplicates)
    
    def _generate_text_report(self, duplicates: Dict[str, List[CodeBlock]]) -> str:
        """Generate a text report."""
        report = []
        report.append("=" * 80)
        report.append("CODE DUPLICATION ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Files analyzed:           {self.stats['files_analyzed']}")
        report.append(f"Total lines:              {self.stats['total_lines']}")
        report.append(f"Duplicate blocks found:   {len(duplicates)}")
        report.append(f"Duplicate locations:      {self.stats['duplicate_blocks']}")
        report.append(f"Duplicate lines:          {self.stats['duplicate_lines']}")
        
        if self.stats['total_lines'] > 0:
            duplication_rate = (self.stats['duplicate_lines'] / self.stats['total_lines']) * 100
            report.append(f"Duplication rate:         {duplication_rate:.2f}%")
        
        report.append("")
        
        # Detailed duplicates
        if duplicates:
            report.append("DUPLICATE CODE BLOCKS")
            report.append("-" * 80)
            report.append("")
            
            # Sort by number of duplicates (most duplicated first)
            sorted_duplicates = sorted(
                duplicates.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )
            
            for idx, (hash_val, blocks) in enumerate(sorted_duplicates[:20], 1):
                report.append(f"Duplicate Group #{idx} ({len(blocks)} instances, {blocks[0].lines_count} lines each)")
                report.append("")
                
                for block in blocks:
                    rel_path = os.path.relpath(block.file_path)
                    report.append(f"  📄 {rel_path}:{block.start_line}-{block.end_line}")
                
                report.append("")
                report.append("  Code Preview:")
                preview_lines = blocks[0].content.split('\n')[:3]
                for line in preview_lines:
                    report.append(f"    {line}")
                if len(blocks[0].content.split('\n')) > 3:
                    report.append("    ...")
                
                report.append("")
                report.append("-" * 80)
                report.append("")
            
            if len(sorted_duplicates) > 20:
                report.append(f"... and {len(sorted_duplicates) - 20} more duplicate groups")
                report.append("")
        else:
            report.append("No significant code duplication found! 🎉")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 80)
        
        if duplicates:
            report.append("Consider the following actions:")
            report.append("")
            report.append("1. Extract duplicated code into reusable functions or classes")
            report.append("2. Create utility modules for commonly repeated patterns")
            report.append("3. Use inheritance or composition to reduce duplication")
            report.append("4. Review duplicated code before migration to reduce work")
            report.append("")
            
            potential_savings = self.stats['duplicate_lines'] - (len(duplicates) * 5)
            if potential_savings > 0:
                report.append(f"💡 Potential lines saved by refactoring: ~{potential_savings}")
                report.append("")
        else:
            report.append("✅ Your codebase has minimal duplication!")
            report.append("")
        
        report.append("=" * 80)
        
        return '\n'.join(report)
    
    def _generate_json_report(self, duplicates: Dict[str, List[CodeBlock]]) -> str:
        """Generate a JSON report."""
        import json
        
        data = {
            'summary': self.stats,
            'duplicates': []
        }
        
        for hash_val, blocks in duplicates.items():
            group = {
                'hash': hash_val,
                'instances': len(blocks),
                'lines_per_instance': blocks[0].lines_count,
                'locations': [
                    {
                        'file': block.file_path,
                        'start_line': block.start_line,
                        'end_line': block.end_line
                    }
                    for block in blocks
                ],
                'code_preview': blocks[0].content[:200]
            }
            data['duplicates'].append(group)
        
        return json.dumps(data, indent=2)
    
    def _generate_html_report(self, duplicates: Dict[str, List[CodeBlock]]) -> str:
        """Generate an HTML report."""
        duplication_rate = 0
        if self.stats['total_lines'] > 0:
            duplication_rate = (self.stats['duplicate_lines'] / self.stats['total_lines']) * 100
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Duplication Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.warning {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.success {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .stat-value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ font-size: 14px; opacity: 0.9; }}
        .duplicate-group {{ background: #f9f9f9; border-left: 4px solid #ff6b6b; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .duplicate-group h3 {{ margin-top: 0; color: #ff6b6b; }}
        .location {{ background: white; padding: 10px; margin: 5px 0; border-radius: 3px; font-family: monospace; }}
        .code-preview {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Courier New', monospace; margin-top: 10px; }}
        .recommendations {{ background: #e3f2fd; padding: 20px; border-radius: 5px; border-left: 4px solid #2196F3; }}
        .recommendations ul {{ margin: 10px 0; }}
        .emoji {{ font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="emoji">🔍</span> Code Duplication Analysis Report</h1>
        
        <h2>Summary Statistics</h2>
        <div class="stats">
            <div class="stat-card success">
                <div class="stat-label">Files Analyzed</div>
                <div class="stat-value">{self.stats['files_analyzed']}</div>
            </div>
            <div class="stat-card success">
                <div class="stat-label">Total Lines</div>
                <div class="stat-value">{self.stats['total_lines']:,}</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-label">Duplicate Blocks</div>
                <div class="stat-value">{len(duplicates)}</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-label">Duplication Rate</div>
                <div class="stat-value">{duplication_rate:.1f}%</div>
            </div>
        </div>
        
        <h2>Duplicate Code Blocks</h2>
"""
        
        if duplicates:
            sorted_duplicates = sorted(
                duplicates.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )
            
            for idx, (hash_val, blocks) in enumerate(sorted_duplicates[:15], 1):
                html += f"""
        <div class="duplicate-group">
            <h3>Duplicate Group #{idx}</h3>
            <p><strong>{len(blocks)} instances</strong> of <strong>{blocks[0].lines_count} lines</strong> each</p>
"""
                for block in blocks:
                    rel_path = os.path.relpath(block.file_path)
                    html += f'            <div class="location">📄 {rel_path}:{block.start_line}-{block.end_line}</div>\n'
                
                preview = blocks[0].content.split('\n')[:5]
                preview_text = '\n'.join(preview)
                if len(blocks[0].content.split('\n')) > 5:
                    preview_text += '\n...'
                
                html += f"""
            <div class="code-preview">{self._escape_html(preview_text)}</div>
        </div>
"""
        else:
            html += '        <p><strong>No significant code duplication found! 🎉</strong></p>\n'
        
        html += """
        <h2>Recommendations</h2>
        <div class="recommendations">
"""
        
        if duplicates:
            potential_savings = self.stats['duplicate_lines'] - (len(duplicates) * 5)
            html += f"""
            <p><strong>Consider the following actions:</strong></p>
            <ul>
                <li>Extract duplicated code into reusable functions or classes</li>
                <li>Create utility modules for commonly repeated patterns</li>
                <li>Use inheritance or composition to reduce duplication</li>
                <li>Review duplicated code before migration to reduce work</li>
            </ul>
            <p><strong>💡 Potential lines saved by refactoring: ~{potential_savings}</strong></p>
"""
        else:
            html += """
            <p><strong>✅ Your codebase has minimal duplication!</strong></p>
            <p>Keep up the good work maintaining clean, DRY (Don't Repeat Yourself) code.</p>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Detect code duplication in Python projects'
    )
    parser.add_argument(
        'path',
        help='Path to Python file or directory to analyze'
    )
    parser.add_argument(
        '-m', '--min-lines',
        type=int,
        default=5,
        help='Minimum lines for a code block (default: 5)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path for the report'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'html'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '-e', '--exclude',
        action='append',
        help='Patterns to exclude (can be used multiple times)'
    )
    
    args = parser.parse_args()
    
    detector = DuplicationDetector(min_lines=args.min_lines)
    
    if os.path.isdir(args.path):
        detector.analyze_directory(args.path, exclude_patterns=args.exclude)
    else:
        detector.analyze_file(args.path)
    
    report = detector.generate_report(format=args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
