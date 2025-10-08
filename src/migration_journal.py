#!/usr/bin/env python3
"""
Migration Journal - Track notes, decisions, and insights during Python 2 to 3 migration

This module provides a comprehensive system for documenting the migration process,
including decisions made, issues encountered, and lessons learned.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
from collections import defaultdict


class JournalEntry:
    """Represents a single journal entry."""
    
    def __init__(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        category: str = "general",
        related_files: Optional[List[str]] = None,
        author: Optional[str] = None
    ):
        self.id = self._generate_id()
        self.timestamp = datetime.now().isoformat()
        self.content = content
        self.tags = tags or []
        self.category = category
        self.related_files = related_files or []
        self.author = author or os.environ.get('USER', 'unknown')
        
    def _generate_id(self) -> str:
        """Generate a unique ID for the entry."""
        return f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'content': self.content,
            'tags': self.tags,
            'category': self.category,
            'related_files': self.related_files,
            'author': self.author
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'JournalEntry':
        """Create entry from dictionary."""
        entry = cls(
            content=data['content'],
            tags=data.get('tags', []),
            category=data.get('category', 'general'),
            related_files=data.get('related_files', []),
            author=data.get('author', 'unknown')
        )
        entry.id = data['id']
        entry.timestamp = data['timestamp']
        return entry
    
    def matches_filter(
        self,
        search_term: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        author: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> bool:
        """Check if entry matches given filters."""
        if search_term and search_term.lower() not in self.content.lower():
            return False
        
        if tags and not any(tag in self.tags for tag in tags):
            return False
        
        if category and self.category != category:
            return False
        
        if author and self.author != author:
            return False
        
        if files and not any(f in self.related_files for f in files):
            return False
        
        return True


class MigrationJournal:
    """Manages migration journal entries."""
    
    CATEGORIES = [
        'decision',      # Architecture or implementation decisions
        'issue',         # Problems encountered
        'solution',      # How issues were resolved
        'insight',       # Lessons learned or discoveries
        'todo',          # Tasks to complete
        'question',      # Open questions
        'general',       # General notes
    ]
    
    def __init__(self, journal_path: str = ".migration_journal.json"):
        self.journal_path = Path(journal_path)
        self.entries: List[JournalEntry] = []
        self._load()
    
    def _load(self):
        """Load journal from file."""
        if self.journal_path.exists():
            try:
                with open(self.journal_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [JournalEntry.from_dict(e) for e in data.get('entries', [])]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load journal: {e}")
                self.entries = []
    
    def _save(self):
        """Save journal to file."""
        data = {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'entries': [e.to_dict() for e in self.entries]
        }
        with open(self.journal_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_entry(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        category: str = "general",
        related_files: Optional[List[str]] = None,
        author: Optional[str] = None
    ) -> JournalEntry:
        """Add a new journal entry."""
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(self.CATEGORIES)}")
        
        entry = JournalEntry(content, tags, category, related_files, author)
        self.entries.append(entry)
        self._save()
        return entry
    
    def get_entries(
        self,
        search_term: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        author: Optional[str] = None,
        files: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[JournalEntry]:
        """Get entries matching the given filters."""
        filtered = [
            e for e in self.entries
            if e.matches_filter(search_term, tags, category, author, files)
        ]
        
        # Sort by timestamp, newest first
        filtered.sort(key=lambda e: e.timestamp, reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_entry_by_id(self, entry_id: str) -> Optional[JournalEntry]:
        """Get a specific entry by ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def update_entry(
        self,
        entry_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        related_files: Optional[List[str]] = None
    ) -> bool:
        """Update an existing entry."""
        entry = self.get_entry_by_id(entry_id)
        if not entry:
            return False
        
        if content is not None:
            entry.content = content
        if tags is not None:
            entry.tags = tags
        if category is not None:
            if category not in self.CATEGORIES:
                raise ValueError(f"Invalid category. Must be one of: {', '.join(self.CATEGORIES)}")
            entry.category = category
        if related_files is not None:
            entry.related_files = related_files
        
        self._save()
        return True
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry by ID."""
        entry = self.get_entry_by_id(entry_id)
        if not entry:
            return False
        
        self.entries.remove(entry)
        self._save()
        return True
    
    def get_statistics(self) -> Dict:
        """Get journal statistics."""
        stats = {
            'total_entries': len(self.entries),
            'by_category': defaultdict(int),
            'by_author': defaultdict(int),
            'unique_tags': set(),
            'related_files': set(),
            'date_range': None
        }
        
        if not self.entries:
            return dict(stats)
        
        timestamps = []
        for entry in self.entries:
            stats['by_category'][entry.category] += 1
            stats['by_author'][entry.author] += 1
            stats['unique_tags'].update(entry.tags)
            stats['related_files'].update(entry.related_files)
            timestamps.append(entry.timestamp)
        
        stats['unique_tags'] = sorted(stats['unique_tags'])
        stats['related_files'] = sorted(stats['related_files'])
        stats['date_range'] = {
            'first': min(timestamps),
            'last': max(timestamps)
        }
        
        return dict(stats)
    
    def export_markdown(self, output_path: str, filters: Optional[Dict] = None):
        """Export journal entries as Markdown documentation."""
        filters = filters or {}
        entries = self.get_entries(**filters)
        
        lines = [
            "# Migration Journal",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Entries: {len(entries)}",
            "",
        ]
        
        # Group by category
        by_category = defaultdict(list)
        for entry in entries:
            by_category[entry.category].append(entry)
        
        for category in self.CATEGORIES:
            if category not in by_category:
                continue
            
            entries_in_cat = by_category[category]
            lines.extend([
                f"## {category.title()}",
                "",
                f"*{len(entries_in_cat)} entries*",
                ""
            ])
            
            for entry in entries_in_cat:
                timestamp = datetime.fromisoformat(entry.timestamp).strftime('%Y-%m-%d %H:%M')
                lines.extend([
                    f"### {entry.id}",
                    "",
                    f"**Date:** {timestamp}  ",
                    f"**Author:** {entry.author}  ",
                ])
                
                if entry.tags:
                    lines.append(f"**Tags:** {', '.join(entry.tags)}  ")
                
                if entry.related_files:
                    lines.append(f"**Related Files:** {', '.join(entry.related_files)}  ")
                
                lines.extend([
                    "",
                    entry.content,
                    "",
                    "---",
                    ""
                ])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def export_json(self, output_path: str, filters: Optional[Dict] = None):
        """Export journal entries as JSON."""
        filters = filters or {}
        entries = self.get_entries(**filters)
        
        data = {
            'exported': datetime.now().isoformat(),
            'total_entries': len(entries),
            'statistics': self.get_statistics(),
            'entries': [e.to_dict() for e in entries]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_entries(self, import_path: str):
        """Import entries from a JSON file."""
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        for entry_data in data.get('entries', []):
            # Check if entry already exists
            if not self.get_entry_by_id(entry_data['id']):
                entry = JournalEntry.from_dict(entry_data)
                self.entries.append(entry)
                imported_count += 1
        
        self._save()
        return imported_count
    
    def get_tag_cloud(self) -> Dict[str, int]:
        """Get tag usage frequency."""
        tag_counts = defaultdict(int)
        for entry in self.entries:
            for tag in entry.tags:
                tag_counts[tag] += 1
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
    
    def get_timeline(self, group_by: str = 'day') -> Dict[str, int]:
        """Get entry timeline grouped by day, week, or month."""
        timeline = defaultdict(int)
        
        for entry in self.entries:
            dt = datetime.fromisoformat(entry.timestamp)
            
            if group_by == 'day':
                key = dt.strftime('%Y-%m-%d')
            elif group_by == 'week':
                key = dt.strftime('%Y-W%W')
            elif group_by == 'month':
                key = dt.strftime('%Y-%m')
            else:
                raise ValueError("group_by must be 'day', 'week', or 'month'")
            
            timeline[key] += 1
        
        return dict(sorted(timeline.items()))


def format_entry_for_display(entry: JournalEntry, color: bool = True) -> str:
    """Format a journal entry for terminal display."""
    timestamp = datetime.fromisoformat(entry.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    if color:
        # ANSI color codes
        BOLD = '\033[1m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        CYAN = '\033[96m'
        RESET = '\033[0m'
        
        lines = [
            f"{BOLD}{BLUE}[{entry.id}]{RESET}",
            f"{CYAN}Category:{RESET} {entry.category}",
            f"{CYAN}Author:{RESET} {entry.author}",
            f"{CYAN}Date:{RESET} {timestamp}",
        ]
        
        if entry.tags:
            lines.append(f"{CYAN}Tags:{RESET} {', '.join(entry.tags)}")
        
        if entry.related_files:
            lines.append(f"{CYAN}Files:{RESET} {', '.join(entry.related_files)}")
        
        lines.extend([
            "",
            entry.content,
            ""
        ])
    else:
        lines = [
            f"[{entry.id}]",
            f"Category: {entry.category}",
            f"Author: {entry.author}",
            f"Date: {timestamp}",
        ]
        
        if entry.tags:
            lines.append(f"Tags: {', '.join(entry.tags)}")
        
        if entry.related_files:
            lines.append(f"Files: {', '.join(entry.related_files)}")
        
        lines.extend([
            "",
            entry.content,
            ""
        ])
    
    return '\n'.join(lines)


def main():
    """Command-line interface for migration journal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migration Journal - Track notes and decisions during migration"
    )
    parser.add_argument(
        '--journal-path',
        default='.migration_journal.json',
        help='Path to journal file (default: .migration_journal.json)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add entry command
    add_parser = subparsers.add_parser('add', help='Add a new journal entry')
    add_parser.add_argument('content', help='Entry content')
    add_parser.add_argument('--tags', nargs='+', help='Tags for the entry')
    add_parser.add_argument('--category', choices=MigrationJournal.CATEGORIES,
                           default='general', help='Entry category')
    add_parser.add_argument('--files', nargs='+', help='Related files')
    add_parser.add_argument('--author', help='Entry author')
    
    # List entries command
    list_parser = subparsers.add_parser('list', help='List journal entries')
    list_parser.add_argument('--search', help='Search term')
    list_parser.add_argument('--tags', nargs='+', help='Filter by tags')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--author', help='Filter by author')
    list_parser.add_argument('--files', nargs='+', help='Filter by related files')
    list_parser.add_argument('--limit', type=int, help='Limit number of results')
    list_parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    # Show entry command
    show_parser = subparsers.add_parser('show', help='Show a specific entry')
    show_parser.add_argument('entry_id', help='Entry ID')
    show_parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show journal statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export journal entries')
    export_parser.add_argument('output', help='Output file path')
    export_parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                              help='Export format')
    export_parser.add_argument('--category', help='Filter by category')
    export_parser.add_argument('--tags', nargs='+', help='Filter by tags')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import journal entries')
    import_parser.add_argument('input', help='Input JSON file path')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a journal entry')
    delete_parser.add_argument('entry_id', help='Entry ID to delete')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    journal = MigrationJournal(args.journal_path)
    
    if args.command == 'add':
        entry = journal.add_entry(
            content=args.content,
            tags=args.tags,
            category=args.category,
            related_files=args.files,
            author=args.author
        )
        print(f"✓ Added entry: {entry.id}")
    
    elif args.command == 'list':
        entries = journal.get_entries(
            search_term=args.search,
            tags=args.tags,
            category=args.category,
            author=args.author,
            files=args.files,
            limit=args.limit
        )
        
        if not entries:
            print("No entries found.")
        else:
            print(f"Found {len(entries)} entries:\n")
            for entry in entries:
                print(format_entry_for_display(entry, color=not args.no_color))
                print("-" * 80)
    
    elif args.command == 'show':
        entry = journal.get_entry_by_id(args.entry_id)
        if entry:
            print(format_entry_for_display(entry, color=not args.no_color))
        else:
            print(f"Entry not found: {args.entry_id}")
    
    elif args.command == 'stats':
        stats = journal.get_statistics()
        print("Journal Statistics")
        print("=" * 50)
        print(f"Total Entries: {stats['total_entries']}")
        print(f"\nBy Category:")
        for cat, count in sorted(stats['by_category'].items()):
            print(f"  {cat}: {count}")
        print(f"\nBy Author:")
        for author, count in sorted(stats['by_author'].items()):
            print(f"  {author}: {count}")
        print(f"\nUnique Tags: {len(stats['unique_tags'])}")
        if stats['unique_tags']:
            print(f"  {', '.join(stats['unique_tags'][:10])}")
        print(f"\nRelated Files: {len(stats['related_files'])}")
        if stats['date_range']:
            print(f"\nDate Range:")
            print(f"  First Entry: {stats['date_range']['first']}")
            print(f"  Last Entry: {stats['date_range']['last']}")
    
    elif args.command == 'export':
        filters = {}
        if args.category:
            filters['category'] = args.category
        if args.tags:
            filters['tags'] = args.tags
        
        if args.format == 'markdown':
            journal.export_markdown(args.output, filters)
        else:
            journal.export_json(args.output, filters)
        
        print(f"✓ Exported to: {args.output}")
    
    elif args.command == 'import':
        count = journal.import_entries(args.input)
        print(f"✓ Imported {count} entries")
    
    elif args.command == 'delete':
        if journal.delete_entry(args.entry_id):
            print(f"✓ Deleted entry: {args.entry_id}")
        else:
            print(f"Entry not found: {args.entry_id}")


if __name__ == '__main__':
    main()
