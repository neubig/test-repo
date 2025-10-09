#!/usr/bin/env python3
"""
Documentation Navigator - Search and browse py2to3 documentation

Provides powerful search and navigation capabilities across all toolkit documentation.
With 50+ guide files, this tool helps users quickly find relevant information.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


class DocNavigator:
    """Navigate and search through py2to3 documentation."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the documentation navigator.
        
        Args:
            project_root: Root directory of the project. If None, auto-detect.
        """
        if project_root is None:
            # Auto-detect project root by looking for project-specific markers
            current = Path(__file__).resolve()
            while current.parent != current:
                # Look for py2to3 script or setup.py as markers of project root
                if (current / 'py2to3').exists() or (current / 'setup.py').exists():
                    project_root = str(current)
                    break
                # Also check for the main README.md with multiple guide files
                if (current / 'README.md').exists() and len(list(current.glob('*_GUIDE.md'))) > 5:
                    project_root = str(current)
                    break
                current = current.parent
            else:
                project_root = '.'
        
        self.project_root = Path(project_root)
        self.docs = self._index_documentation()
        
    def _index_documentation(self) -> Dict[str, Dict]:
        """Index all markdown documentation files.
        
        Returns:
            Dictionary mapping file paths to document metadata.
        """
        docs = {}
        
        # Find all markdown files in the project root (non-recursive)
        for md_file in self.project_root.glob('*.md'):
            # Skip certain files
            if md_file.name in ['LICENSE.md', 'CONTRIBUTING.md']:
                continue
            
            rel_path = md_file.relative_to(self.project_root)
            docs[str(rel_path)] = self._parse_document(md_file)
        
        # Also search in docs/ subdirectory
        docs_dir = self.project_root / 'docs'
        if docs_dir.exists():
            for md_file in docs_dir.glob('*.md'):
                rel_path = md_file.relative_to(self.project_root)
                docs[str(rel_path)] = self._parse_document(md_file)
        
        return docs
    
    def _parse_document(self, file_path: Path) -> Dict:
        """Parse a markdown document and extract metadata.
        
        Args:
            file_path: Path to the markdown file.
            
        Returns:
            Dictionary with document metadata.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # Extract description (first paragraph after title)
        desc_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|\n#)', content, re.MULTILINE | re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        description = ' '.join(description.split())[:200]  # First 200 chars
        
        # Extract sections (all # headings)
        sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Determine category from filename
        category = self._categorize_document(file_path.stem)
        
        # Extract keywords from content
        keywords = self._extract_keywords(content, file_path.stem)
        
        return {
            'path': file_path,
            'title': title,
            'description': description,
            'sections': sections,
            'category': category,
            'keywords': keywords,
            'content': content,
            'size': len(content)
        }
    
    def _categorize_document(self, filename: str) -> str:
        """Categorize a document based on its filename.
        
        Args:
            filename: Document filename (without extension).
            
        Returns:
            Category name.
        """
        filename_lower = filename.lower()
        
        if filename == 'README':
            return 'Getting Started'
        elif filename == 'QUICK_START':
            return 'Getting Started'
        elif 'GUIDE' in filename:
            # Categorize by the guide type
            if any(x in filename_lower for x in ['wizard', 'cli', 'interactive']):
                return 'User Interface'
            elif any(x in filename_lower for x in ['check', 'verify', 'validate', 'quality', 'security']):
                return 'Validation & Quality'
            elif any(x in filename_lower for x in ['backup', 'rollback', 'freeze', 'git']):
                return 'Safety & Version Control'
            elif any(x in filename_lower for x in ['report', 'badge', 'dashboard', 'heatmap', 'timeline', 'story']):
                return 'Reporting & Visualization'
            elif any(x in filename_lower for x in ['config', 'setup', 'venv']):
                return 'Configuration'
            elif any(x in filename_lower for x in ['pattern', 'recipe', 'snippet', 'example']):
                return 'Examples & Patterns'
            elif any(x in filename_lower for x in ['ci_cd', 'precommit', 'watch']):
                return 'Automation'
            elif any(x in filename_lower for x in ['deps', 'dependency', 'import']):
                return 'Dependencies'
            elif any(x in filename_lower for x in ['api', 'export', 'format']):
                return 'Integration & Export'
            else:
                return 'Advanced Features'
        elif filename == 'CHANGELOG':
            return 'Project Info'
        else:
            return 'Other'
    
    def _extract_keywords(self, content: str, filename: str) -> List[str]:
        """Extract keywords from document content.
        
        Args:
            content: Document content.
            filename: Document filename.
            
        Returns:
            List of keywords.
        """
        keywords = set()
        
        # Add filename-based keywords
        keywords.update(filename.lower().replace('_', ' ').split())
        
        # Extract code blocks (these often contain important commands)
        code_blocks = re.findall(r'```(?:bash|python)?\n(.+?)\n```', content, re.DOTALL)
        for block in code_blocks[:10]:  # Limit to first 10 code blocks
            # Extract command names (first word after ./py2to3 or python)
            cmds = re.findall(r'(?:\.\/py2to3|python3?)\s+(\w+)', block)
            keywords.update(cmds)
        
        # Extract emphasized terms (bold/italic)
        emphasized = re.findall(r'\*\*(.+?)\*\*|__(.+?)__|`(.+?)`', content)
        for match in emphasized[:20]:  # Limit to first 20
            for group in match:
                if group:
                    keywords.add(group.lower())
        
        return list(keywords)[:20]  # Limit to 20 keywords
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search documentation for a query string.
        
        Args:
            query: Search query.
            max_results: Maximum number of results to return.
            
        Returns:
            List of matching documents with relevance scores and context.
        """
        query_lower = query.lower()
        results = []
        
        for doc_path, doc_info in self.docs.items():
            score = 0
            contexts = []
            
            # Check title match (highest weight)
            if query_lower in doc_info['title'].lower():
                score += 10
                contexts.append(('title', doc_info['title']))
            
            # Check description match
            if query_lower in doc_info['description'].lower():
                score += 5
                contexts.append(('description', doc_info['description']))
            
            # Check keywords match
            for keyword in doc_info['keywords']:
                if query_lower in keyword.lower():
                    score += 3
            
            # Check sections match
            for section in doc_info['sections']:
                if query_lower in section.lower():
                    score += 2
                    contexts.append(('section', section))
            
            # Check full content match with context extraction
            content_lower = doc_info['content'].lower()
            if query_lower in content_lower:
                score += 1
                # Extract context around matches
                for match in re.finditer(re.escape(query_lower), content_lower):
                    start = max(0, match.start() - 60)
                    end = min(len(doc_info['content']), match.end() + 60)
                    context = doc_info['content'][start:end].strip()
                    # Clean up the context
                    context = ' '.join(context.split())
                    if len(context) > 0:
                        contexts.append(('content', context))
                        if len(contexts) >= 3:  # Limit contexts per document
                            break
            
            if score > 0:
                results.append({
                    'path': doc_path,
                    'title': doc_info['title'],
                    'description': doc_info['description'],
                    'category': doc_info['category'],
                    'score': score,
                    'contexts': contexts[:3]  # Top 3 contexts
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def list_by_category(self) -> Dict[str, List[Dict]]:
        """List all documents grouped by category.
        
        Returns:
            Dictionary mapping categories to lists of documents.
        """
        categories = defaultdict(list)
        
        for doc_path, doc_info in self.docs.items():
            categories[doc_info['category']].append({
                'path': doc_path,
                'title': doc_info['title'],
                'description': doc_info['description']
            })
        
        # Sort documents within each category by title
        for category in categories:
            categories[category].sort(key=lambda x: x['title'])
        
        return dict(categories)
    
    def get_document(self, path: str) -> Optional[Dict]:
        """Get full information about a specific document.
        
        Args:
            path: Document path (can be partial).
            
        Returns:
            Document information or None if not found.
        """
        # Try exact match first
        if path in self.docs:
            info = self.docs[path].copy()
            info['rel_path'] = path
            return info
        
        # Try partial match
        for doc_path, doc_info in self.docs.items():
            if path.lower() in doc_path.lower():
                info = doc_info.copy()
                info['rel_path'] = doc_path
                return info
        
        return None
    
    def get_related(self, path: str, max_results: int = 5) -> List[Dict]:
        """Find documents related to the given document.
        
        Args:
            path: Document path.
            max_results: Maximum number of related documents to return.
            
        Returns:
            List of related documents.
        """
        doc_info = self.get_document(path)
        if not doc_info:
            return []
        
        related = []
        doc_keywords = set(doc_info['keywords'])
        
        for doc_path, other_info in self.docs.items():
            if doc_path == path:
                continue
            
            score = 0
            
            # Same category gets points
            if other_info['category'] == doc_info['category']:
                score += 5
            
            # Shared keywords get points
            other_keywords = set(other_info['keywords'])
            shared = doc_keywords & other_keywords
            score += len(shared)
            
            if score > 0:
                related.append({
                    'path': doc_path,
                    'title': other_info['title'],
                    'description': other_info['description'],
                    'category': other_info['category'],
                    'score': score
                })
        
        # Sort by score (descending)
        related.sort(key=lambda x: x['score'], reverse=True)
        
        return related[:max_results]
    
    def get_stats(self) -> Dict:
        """Get statistics about the documentation.
        
        Returns:
            Dictionary with documentation statistics.
        """
        categories = self.list_by_category()
        total_size = sum(doc['size'] for doc in self.docs.values())
        
        return {
            'total_documents': len(self.docs),
            'total_size': total_size,
            'total_size_kb': total_size / 1024,
            'categories': {cat: len(docs) for cat, docs in categories.items()},
            'avg_document_size': total_size / len(self.docs) if self.docs else 0
        }


def format_search_results(results: List[Dict], show_context: bool = True) -> str:
    """Format search results for display.
    
    Args:
        results: List of search results.
        show_context: Whether to show context snippets.
        
    Returns:
        Formatted string.
    """
    if not results:
        return "No results found."
    
    output = []
    
    for i, result in enumerate(results, 1):
        output.append(f"\n{i}. {result['title']}")
        output.append(f"   📄 {result['path']}")
        output.append(f"   📁 {result['category']}")
        
        if result['description']:
            output.append(f"   💡 {result['description']}")
        
        if show_context and result['contexts']:
            output.append(f"   🔍 Matches:")
            for ctx_type, ctx_text in result['contexts'][:2]:
                if ctx_type == 'title':
                    output.append(f"      • In title: {ctx_text}")
                elif ctx_type == 'section':
                    output.append(f"      • In section: {ctx_text}")
                elif ctx_type == 'content':
                    output.append(f"      • ...{ctx_text}...")
    
    return '\n'.join(output)


def format_category_list(categories: Dict[str, List[Dict]]) -> str:
    """Format category listing for display.
    
    Args:
        categories: Dictionary of categories and their documents.
        
    Returns:
        Formatted string.
    """
    output = []
    
    # Define category order for better organization
    category_order = [
        'Getting Started',
        'User Interface',
        'Configuration',
        'Validation & Quality',
        'Safety & Version Control',
        'Examples & Patterns',
        'Reporting & Visualization',
        'Automation',
        'Dependencies',
        'Integration & Export',
        'Advanced Features',
        'Project Info',
        'Other'
    ]
    
    # Sort categories by defined order
    sorted_categories = sorted(
        categories.items(),
        key=lambda x: category_order.index(x[0]) if x[0] in category_order else 999
    )
    
    for category, docs in sorted_categories:
        output.append(f"\n📚 {category} ({len(docs)} documents)")
        output.append("   " + "─" * 60)
        
        for doc in docs:
            output.append(f"   • {doc['title']}")
            output.append(f"     {doc['path']}")
            if doc['description']:
                desc = doc['description'][:80] + '...' if len(doc['description']) > 80 else doc['description']
                output.append(f"     {desc}")
    
    return '\n'.join(output)


def main():
    """Command-line interface for the documentation navigator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Search and navigate py2to3 documentation'
    )
    
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search documentation')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', '--max-results', type=int, default=10,
                              help='Maximum number of results (default: 10)')
    search_parser.add_argument('--no-context', action='store_true',
                              help='Hide context snippets')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all documentation')
    list_parser.add_argument('-c', '--category', help='Filter by category')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get info about a specific document')
    info_parser.add_argument('path', help='Document path (can be partial)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show documentation statistics')
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        return 1
    
    # Initialize navigator
    nav = DocNavigator()
    
    if args.action == 'search':
        results = nav.search(args.query, args.max_results)
        print(f"\n🔍 Found {len(results)} result(s) for '{args.query}':")
        print(format_search_results(results, not args.no_context))
        
    elif args.action == 'list':
        categories = nav.list_by_category()
        if args.category:
            # Filter by category
            filtered = {k: v for k, v in categories.items() 
                       if args.category.lower() in k.lower()}
            print(format_category_list(filtered))
        else:
            print(format_category_list(categories))
        
    elif args.action == 'info':
        doc = nav.get_document(args.path)
        if not doc:
            print(f"❌ Document not found: {args.path}")
            return 1
        
        print(f"\n📄 {doc['title']}")
        print(f"   Path: {doc['path']}")
        print(f"   Category: {doc['category']}")
        print(f"   Size: {doc['size']} bytes")
        
        if doc['description']:
            print(f"\n   Description:")
            print(f"   {doc['description']}")
        
        if doc['sections']:
            print(f"\n   Sections:")
            for section in doc['sections'][:10]:
                print(f"   • {section}")
            if len(doc['sections']) > 10:
                print(f"   ... and {len(doc['sections']) - 10} more")
        
        # Show related documents
        related = nav.get_related(str(doc['path']))
        if related:
            print(f"\n   Related Documents:")
            for rel in related:
                print(f"   • {rel['title']} ({rel['path']})")
        
    elif args.action == 'stats':
        stats = nav.get_stats()
        print(f"\n📊 Documentation Statistics:")
        print(f"   Total Documents: {stats['total_documents']}")
        print(f"   Total Size: {stats['total_size_kb']:.1f} KB")
        print(f"   Average Size: {stats['avg_document_size']:.0f} bytes")
        print(f"\n   Documents by Category:")
        for cat, count in sorted(stats['categories'].items(), 
                                key=lambda x: x[1], reverse=True):
            print(f"   • {cat}: {count}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
