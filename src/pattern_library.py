#!/usr/bin/env python3
"""
Pattern Library Browser for Python 2 to 3 Migration

An interactive reference tool that provides searchable examples of common
Python 2 patterns and their Python 3 equivalents. Useful for learning
and as a quick reference during manual migration work.
"""

import re
import sys
from typing import List, Dict, Optional


class MigrationPattern:
    """Represents a single Python 2 to 3 migration pattern."""
    
    def __init__(self, name: str, category: str, python2: str, python3: str,
                 explanation: str, gotchas: Optional[str] = None,
                 difficulty: str = "medium"):
        self.name = name
        self.category = category
        self.python2 = python2
        self.python3 = python3
        self.explanation = explanation
        self.gotchas = gotchas
        self.difficulty = difficulty  # easy, medium, hard
    
    def matches_search(self, query: str) -> bool:
        """Check if this pattern matches the search query."""
        query_lower = query.lower()
        searchable = f"{self.name} {self.category} {self.explanation}".lower()
        return query_lower in searchable
    
    def format_display(self, show_details: bool = True) -> str:
        """Format pattern for display."""
        difficulty_emoji = {
            "easy": "🟢",
            "medium": "🟡",
            "hard": "🔴"
        }
        
        output = []
        output.append(f"\n{'=' * 70}")
        output.append(f"📘 {self.name}")
        output.append(f"   Category: {self.category} | Difficulty: {difficulty_emoji.get(self.difficulty, '⚪')} {self.difficulty.title()}")
        output.append(f"{'=' * 70}\n")
        
        if show_details:
            output.append("📝 EXPLANATION:")
            output.append(f"   {self.explanation}\n")
            
            output.append("🐍 PYTHON 2:")
            for line in self.python2.strip().split('\n'):
                output.append(f"   {line}")
            output.append("")
            
            output.append("✨ PYTHON 3:")
            for line in self.python3.strip().split('\n'):
                output.append(f"   {line}")
            output.append("")
            
            if self.gotchas:
                output.append("⚠️  GOTCHAS:")
                output.append(f"   {self.gotchas}\n")
        
        return '\n'.join(output)


class PatternLibrary:
    """Manages and provides access to Python 2 to 3 migration patterns."""
    
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[MigrationPattern]:
        """Load all migration patterns."""
        patterns = [
            MigrationPattern(
                name="Print Statement to Function",
                category="Built-ins",
                python2="print 'Hello, World!'",
                python3="print('Hello, World!')",
                explanation="Print changed from a statement to a function. Parentheses are now required.",
                gotchas="Multiple arguments need commas: print('a', 'b') instead of print 'a', 'b'",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Print with Separator",
                category="Built-ins",
                python2="print 'a', 'b', 'c'",
                python3="print('a', 'b', 'c', sep=' ')",
                explanation="Print arguments are separated by spaces by default. Use sep parameter to customize.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Print without Newline",
                category="Built-ins",
                python2="print 'text',  # trailing comma",
                python3="print('text', end='')",
                explanation="Use the end parameter to control line endings.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Exception Handling Syntax",
                category="Exceptions",
                python2="try:\n    risky_operation()\nexcept ValueError, e:\n    print e",
                python3="try:\n    risky_operation()\nexcept ValueError as e:\n    print(e)",
                explanation="Exception capture syntax changed from comma to 'as' keyword.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Raising Exceptions",
                category="Exceptions",
                python2="raise ValueError, 'error message'",
                python3="raise ValueError('error message')",
                explanation="Exceptions must be raised with parentheses-based constructor syntax.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Dictionary Iterator Methods",
                category="Iterators",
                python2="for key, value in d.iteritems():\n    process(key, value)",
                python3="for key, value in d.items():\n    process(key, value)",
                explanation="iteritems(), iterkeys(), and itervalues() removed. Use items(), keys(), values() which now return views.",
                gotchas="In Python 3, dict.keys(), values(), and items() return dictionary views, not lists. Convert with list() if needed.",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Dictionary Keys as List",
                category="Iterators",
                python2="keys = d.keys()  # returns list\nfirst_key = keys[0]",
                python3="keys = list(d.keys())  # explicit conversion\nfirst_key = keys[0]",
                explanation="dict.keys() returns a view object, not a list. Convert explicitly if list operations are needed.",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Range vs XRange",
                category="Iterators",
                python2="for i in xrange(1000000):\n    process(i)",
                python3="for i in range(1000000):\n    process(i)",
                explanation="xrange() was removed. range() now behaves like the old xrange() (returns an iterator, not a list).",
                gotchas="Old range() returned a list. New range() is lazy. Use list(range()) if you need a list.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Integer Division",
                category="Operators",
                python2="result = 5 / 2  # returns 2 (integer division)",
                python3="result = 5 // 2  # returns 2 (floor division)\nresult = 5 / 2   # returns 2.5 (true division)",
                explanation="Division operator / now always performs true division. Use // for floor division.",
                gotchas="This is a semantic change that can cause bugs. Review all division operations carefully.",
                difficulty="hard"
            ),
            MigrationPattern(
                name="String Types",
                category="Strings",
                python2="if isinstance(obj, basestring):\n    process_string(obj)",
                python3="if isinstance(obj, str):\n    process_string(obj)",
                explanation="basestring was removed. In Python 3, str is the only string type (unicode by default).",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Unicode Strings",
                category="Strings",
                python2="text = u'Hello, 世界'\ndata = 'binary data'",
                python3="text = 'Hello, 世界'  # str is unicode by default\ndata = b'binary data'  # bytes for binary",
                explanation="All strings are Unicode by default in Python 3. Use bytes for binary data.",
                gotchas="Mixing str and bytes operations will raise TypeError. Be explicit about encoding/decoding.",
                difficulty="hard"
            ),
            MigrationPattern(
                name="String Formatting",
                category="Strings",
                python2="msg = 'Hello, %s!' % name\nmsg = 'x=%d, y=%d' % (x, y)",
                python3="msg = 'Hello, {}!'.format(name)\nmsg = f'x={x}, y={y}'  # Python 3.6+",
                explanation="While % formatting still works, .format() and f-strings are preferred in Python 3.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Import urllib",
                category="Imports",
                python2="import urllib\nimport urllib2\nimport urlparse",
                python3="import urllib.request\nimport urllib.parse\nimport urllib.error",
                explanation="urllib, urllib2, and urlparse were reorganized into urllib.request, urllib.parse, and urllib.error.",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Import ConfigParser",
                category="Imports",
                python2="import ConfigParser\nconfig = ConfigParser.ConfigParser()",
                python3="import configparser\nconfig = configparser.ConfigParser()",
                explanation="ConfigParser renamed to configparser (lowercase) following PEP 8.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Import Queue",
                category="Imports",
                python2="import Queue\nq = Queue.Queue()",
                python3="import queue\nq = queue.Queue()",
                explanation="Queue renamed to queue (lowercase) following PEP 8.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Import SocketServer",
                category="Imports",
                python2="import SocketServer",
                python3="import socketserver",
                explanation="SocketServer renamed to socketserver (lowercase) following PEP 8.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Input Function",
                category="Built-ins",
                python2="name = raw_input('Name: ')  # returns string\nage = input('Age: ')  # evaluates input!",
                python3="name = input('Name: ')  # always returns string\nage = int(input('Age: '))  # convert explicitly",
                explanation="raw_input() renamed to input(). Old input() removed (was unsafe eval).",
                gotchas="Old input() evaluated code - security risk! New input() is safe (returns string).",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Map Function",
                category="Functional",
                python2="result = map(lambda x: x*2, [1,2,3])\nprint result  # [2, 4, 6]",
                python3="result = map(lambda x: x*2, [1,2,3])\nprint(list(result))  # [2, 4, 6]",
                explanation="map() returns an iterator instead of a list. Convert with list() if needed.",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Filter Function",
                category="Functional",
                python2="result = filter(lambda x: x > 0, numbers)\nprint result  # list of positive numbers",
                python3="result = filter(lambda x: x > 0, numbers)\nprint(list(result))  # list of positive numbers",
                explanation="filter() returns an iterator instead of a list. Convert with list() if needed.",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Zip Function",
                category="Functional",
                python2="result = zip([1,2], ['a','b'])\nprint result  # [(1,'a'), (2,'b')]",
                python3="result = zip([1,2], ['a','b'])\nprint(list(result))  # [(1,'a'), (2,'b')]",
                explanation="zip() returns an iterator instead of a list. Convert with list() if needed.",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Classic Classes",
                category="Classes",
                python2="class MyClass:\n    pass",
                python3="class MyClass:\n    pass  # OK\n# OR explicitly inherit from object:\nclass MyClass(object):\n    pass",
                explanation="All classes are new-style in Python 3. Explicit object inheritance is optional but clear.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Metaclasses",
                category="Classes",
                python2="class MyClass(object):\n    __metaclass__ = Meta",
                python3="class MyClass(metaclass=Meta):\n    pass",
                explanation="Metaclass syntax changed from __metaclass__ attribute to metaclass keyword argument.",
                difficulty="hard"
            ),
            MigrationPattern(
                name="Next Method",
                category="Iterators",
                python2="it = iter([1, 2, 3])\nvalue = it.next()",
                python3="it = iter([1, 2, 3])\nvalue = next(it)",
                explanation="Iterator .next() method replaced by next() built-in function.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Has Key Method",
                category="Dictionary",
                python2="if d.has_key('name'):\n    print d['name']",
                python3="if 'name' in d:\n    print(d['name'])",
                explanation="has_key() method removed. Use 'in' operator instead.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="File IO",
                category="Files",
                python2="f = file('data.txt', 'r')\ncontent = f.read()\nf.close()",
                python3="with open('data.txt', 'r') as f:\n    content = f.read()",
                explanation="file() removed, use open(). Context managers (with) are now the preferred approach.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Reduce Function",
                category="Functional",
                python2="from functools import reduce  # Python 2.6+\ntotal = reduce(lambda x,y: x+y, [1,2,3,4])",
                python3="from functools import reduce\ntotal = reduce(lambda x,y: x+y, [1,2,3,4])",
                explanation="reduce() moved from built-ins to functools module. Must be imported explicitly.",
                difficulty="medium"
            ),
            MigrationPattern(
                name="Octal Literals",
                category="Literals",
                python2="octal = 0755",
                python3="octal = 0o755",
                explanation="Octal literals now require 0o or 0O prefix instead of just 0.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Long Integer Type",
                category="Numbers",
                python2="big_num = 123456789L",
                python3="big_num = 123456789",
                explanation="Long and int were unified. The L suffix is no longer needed or allowed.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Comparison Functions",
                category="Sorting",
                python2="sorted_list = sorted(items, cmp=compare_func)",
                python3="from functools import cmp_to_key\nsorted_list = sorted(items, key=cmp_to_key(compare_func))",
                explanation="cmp parameter removed from sort functions. Use key parameter or cmp_to_key() converter.",
                gotchas="Writing key functions is more efficient. Only use cmp_to_key for complex comparisons.",
                difficulty="hard"
            ),
            MigrationPattern(
                name="Unicode Literals",
                category="Strings",
                python2="# -*- coding: utf-8 -*-\ntext = u'Ä, Ö, Ü'",
                python3="# Unicode by default, no prefix needed\ntext = 'Ä, Ö, Ü'",
                explanation="Strings are Unicode by default in Python 3. The u'' prefix is accepted but unnecessary.",
                difficulty="easy"
            ),
            MigrationPattern(
                name="Absolute vs Relative Imports",
                category="Imports",
                python2="# In package/module.py:\nimport util  # relative import",
                python3="# In package/module.py:\nfrom . import util  # explicit relative\nimport package.util  # absolute",
                explanation="Implicit relative imports removed. Use explicit relative (.) or absolute imports.",
                difficulty="medium"
            ),
        ]
        return patterns
    
    def get_categories(self) -> List[str]:
        """Get list of all pattern categories."""
        categories = sorted(set(p.category for p in self.patterns))
        return categories
    
    def get_patterns_by_category(self, category: str) -> List[MigrationPattern]:
        """Get all patterns in a specific category."""
        return [p for p in self.patterns if p.category.lower() == category.lower()]
    
    def search_patterns(self, query: str) -> List[MigrationPattern]:
        """Search patterns by keyword."""
        return [p for p in self.patterns if p.matches_search(query)]
    
    def get_patterns_by_difficulty(self, difficulty: str) -> List[MigrationPattern]:
        """Get patterns filtered by difficulty level."""
        return [p for p in self.patterns if p.difficulty == difficulty.lower()]
    
    def display_summary(self):
        """Display a summary of available patterns."""
        print("\n" + "=" * 70)
        print("📚 Python 2 to 3 Migration Pattern Library")
        print("=" * 70)
        print(f"\nTotal Patterns: {len(self.patterns)}")
        
        print("\n📂 Categories:")
        for category in self.get_categories():
            count = len(self.get_patterns_by_category(category))
            print(f"   • {category}: {count} pattern(s)")
        
        print("\n⚡ Difficulty Distribution:")
        for difficulty in ["easy", "medium", "hard"]:
            count = len(self.get_patterns_by_difficulty(difficulty))
            emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[difficulty]
            print(f"   {emoji} {difficulty.title()}: {count} pattern(s)")
        
        print("\n💡 Usage:")
        print("   • Browse by category: patterns --category <name>")
        print("   • Search patterns: patterns --search <query>")
        print("   • Filter by difficulty: patterns --difficulty <level>")
        print("   • List all patterns: patterns --list")
        print()
    
    def display_pattern_list(self, patterns: List[MigrationPattern] = None):
        """Display a condensed list of patterns."""
        if patterns is None:
            patterns = self.patterns
        
        if not patterns:
            print("\n⚠️  No patterns found matching your criteria.\n")
            return
        
        print(f"\n📋 Found {len(patterns)} pattern(s):\n")
        
        grouped = {}
        for pattern in patterns:
            if pattern.category not in grouped:
                grouped[pattern.category] = []
            grouped[pattern.category].append(pattern)
        
        for category in sorted(grouped.keys()):
            print(f"\n  📁 {category}:")
            for pattern in grouped[category]:
                difficulty_emoji = {
                    "easy": "🟢",
                    "medium": "🟡", 
                    "hard": "🔴"
                }[pattern.difficulty]
                print(f"     {difficulty_emoji} {pattern.name}")
        print()


def main():
    """Main entry point for pattern library CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Browse Python 2 to 3 migration patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --summary              Show pattern library overview
  %(prog)s --list                 List all patterns
  %(prog)s --category Strings     Show all string-related patterns
  %(prog)s --search print         Search for print-related patterns
  %(prog)s --difficulty easy      Show only easy patterns
        """
    )
    
    parser.add_argument('--summary', action='store_true',
                        help='Show pattern library summary')
    parser.add_argument('--list', action='store_true',
                        help='List all available patterns')
    parser.add_argument('--category', metavar='NAME',
                        help='Show patterns in a specific category')
    parser.add_argument('--search', metavar='QUERY',
                        help='Search patterns by keyword')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'],
                        help='Filter patterns by difficulty level')
    parser.add_argument('--show', metavar='INDEX', type=int,
                        help='Show detailed view of pattern by index')
    
    args = parser.parse_args()
    
    library = PatternLibrary()
    
    # Default to summary if no arguments
    if not any([args.summary, args.list, args.category, args.search, args.difficulty, args.show]):
        library.display_summary()
        return
    
    if args.summary:
        library.display_summary()
        return
    
    # Collect patterns based on filters
    patterns = library.patterns
    
    if args.category:
        patterns = library.get_patterns_by_category(args.category)
        if not patterns:
            print(f"\n⚠️  Category '{args.category}' not found.")
            print(f"Available categories: {', '.join(library.get_categories())}\n")
            return
    
    if args.search:
        patterns = library.search_patterns(args.search)
    
    if args.difficulty:
        patterns = [p for p in patterns if p.difficulty == args.difficulty]
    
    # Display results
    if args.list or args.category or args.search or args.difficulty:
        if patterns:
            library.display_pattern_list(patterns)
            print("💡 To see details, use --show <pattern_name> or browse one by one\n")
            # Show all details
            for i, pattern in enumerate(patterns, 1):
                print(pattern.format_display(show_details=True))
        else:
            print("\n⚠️  No patterns found matching your criteria.\n")


if __name__ == '__main__':
    main()
