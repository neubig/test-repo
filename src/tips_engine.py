#!/usr/bin/env python3
"""
Migration Tips Engine for Python 2 to 3

Provides quick, context-aware tips and solutions for common migration issues.
Complements comprehensive guides with instant answers and practical examples.
"""

import os
import re
from collections import defaultdict
from typing import List, Dict, Optional


class TipsEngine:
    """Engine for providing context-aware migration tips and solutions."""
    
    TIPS_DATABASE = {
        'print': {
            'title': 'Print Statement → Print Function',
            'category': 'Built-ins',
            'problem': 'Python 2 uses print as a statement, Python 3 uses it as a function',
            'examples': [
                {
                    'py2': 'print "Hello, World!"',
                    'py3': 'print("Hello, World!")',
                    'notes': 'Always use parentheses in Python 3'
                },
                {
                    'py2': 'print "Name:", name',
                    'py3': 'print("Name:", name)',
                    'notes': 'Comma-separated values work the same way'
                },
                {
                    'py2': 'print >>sys.stderr, "Error"',
                    'py3': 'print("Error", file=sys.stderr)',
                    'notes': 'Use file parameter for output redirection'
                }
            ],
            'quick_fix': 'Add parentheses around all print statements',
            'common_mistakes': [
                'Forgetting to import print_function from __future__',
                'Not updating print statements with file redirection'
            ],
            'related_guides': ['QUICK_START.md', 'PATTERNS_GUIDE.md']
        },
        
        'imports': {
            'title': 'Standard Library Module Renames',
            'category': 'Imports',
            'problem': 'Many standard library modules were renamed in Python 3',
            'examples': [
                {
                    'py2': 'import ConfigParser',
                    'py3': 'import configparser',
                    'notes': 'Module name is now lowercase'
                },
                {
                    'py2': 'import urllib2',
                    'py3': 'from urllib import request',
                    'notes': 'urllib2 split into urllib.request and urllib.error'
                },
                {
                    'py2': 'from Queue import Queue',
                    'py3': 'from queue import Queue',
                    'notes': 'Queue module renamed to queue'
                }
            ],
            'quick_fix': 'Use dependency analyzer to find all import changes needed',
            'common_mistakes': [
                'Missing urllib split (urllib.request, urllib.parse, urllib.error)',
                'Not updating from X import Y statements'
            ],
            'related_guides': ['DEPENDENCY_GUIDE.md', 'IMPORT_OPTIMIZER_GUIDE.md']
        },
        
        'unicode': {
            'title': 'String and Unicode Handling',
            'category': 'Strings',
            'problem': 'Python 3 treats all strings as unicode by default',
            'examples': [
                {
                    'py2': 'u"Unicode string"',
                    'py3': '"Unicode string"',
                    'notes': 'u prefix is allowed but not needed'
                },
                {
                    'py2': 'isinstance(s, basestring)',
                    'py3': 'isinstance(s, str)',
                    'notes': 'basestring removed, str covers all strings'
                },
                {
                    'py2': 'unicode(text, "utf-8")',
                    'py3': 'str(text)',
                    'notes': 'unicode() function removed'
                }
            ],
            'quick_fix': 'Replace basestring with str, remove unnecessary u prefixes',
            'common_mistakes': [
                'Mixing bytes and strings without proper encoding/decoding',
                'Not handling file encoding explicitly'
            ],
            'related_guides': ['ENCODING_GUIDE.md', 'MODERNIZER_GUIDE.md']
        },
        
        'iterators': {
            'title': 'Iterator Methods and Functions',
            'category': 'Iterators',
            'problem': 'Many methods return iterators instead of lists in Python 3',
            'examples': [
                {
                    'py2': 'dict.iteritems()',
                    'py3': 'dict.items()',
                    'notes': 'items() now returns an iterator by default'
                },
                {
                    'py2': 'xrange(10)',
                    'py3': 'range(10)',
                    'notes': 'range() now behaves like xrange()'
                },
                {
                    'py2': 'dict.keys()[0]',
                    'py3': 'list(dict.keys())[0]',
                    'notes': 'Wrap with list() if you need indexing'
                }
            ],
            'quick_fix': 'Replace iteritems/iterkeys/itervalues with items/keys/values',
            'common_mistakes': [
                'Trying to index dict.keys() or dict.values() directly',
                'Assuming map() and filter() return lists'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        },
        
        'exceptions': {
            'title': 'Exception Syntax',
            'category': 'Exceptions',
            'problem': 'Exception syntax changed from comma to "as" keyword',
            'examples': [
                {
                    'py2': 'except Exception, e:',
                    'py3': 'except Exception as e:',
                    'notes': 'Use "as" keyword instead of comma'
                },
                {
                    'py2': 'raise ValueError, "message"',
                    'py3': 'raise ValueError("message")',
                    'notes': 'Use function call syntax'
                }
            ],
            'quick_fix': 'Replace ", e:" with "as e:" in except clauses',
            'common_mistakes': [
                'Forgetting to update nested exception handlers',
                'Not updating raise statements'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        },
        
        'division': {
            'title': 'Integer Division Behavior',
            'category': 'Operators',
            'problem': 'Division operator / always returns float in Python 3',
            'examples': [
                {
                    'py2': '5 / 2  # Returns 2',
                    'py3': '5 // 2  # Returns 2 (use // for integer division)',
                    'notes': 'Use // for integer division, / for float division'
                },
                {
                    'py2': 'from __future__ import division',
                    'py3': '# Not needed, / is float division by default',
                    'notes': 'Future import no longer necessary'
                }
            ],
            'quick_fix': 'Review all division operations and use // where integer division is needed',
            'common_mistakes': [
                'Assuming / returns integer for integer operands',
                'Not testing calculations after migration'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        },
        
        'classes': {
            'title': 'New-Style Classes',
            'category': 'Classes',
            'problem': 'All classes should inherit from object in Python 3',
            'examples': [
                {
                    'py2': 'class MyClass:',
                    'py3': 'class MyClass(object):',
                    'notes': 'Explicitly inherit from object for compatibility'
                },
                {
                    'py2': 'class MyClass(object):',
                    'py3': 'class MyClass:',
                    'notes': 'In Python 3, all classes inherit from object by default'
                }
            ],
            'quick_fix': 'Add (object) to all class definitions for Python 2/3 compatibility',
            'common_mistakes': [
                'Not updating __cmp__ methods',
                'Assuming old-style class behavior'
            ],
            'related_guides': ['MODERNIZER_GUIDE.md']
        },
        
        'input': {
            'title': 'Input Function Changes',
            'category': 'Built-ins',
            'problem': 'raw_input() renamed to input(), old input() removed',
            'examples': [
                {
                    'py2': 'name = raw_input("Enter name: ")',
                    'py3': 'name = input("Enter name: ")',
                    'notes': 'raw_input() is now input()'
                },
                {
                    'py2': 'value = input("Enter number: ")  # Evaluates expression',
                    'py3': 'value = eval(input("Enter number: "))  # Need explicit eval',
                    'notes': 'Python 3 input() returns string, use eval() if needed'
                }
            ],
            'quick_fix': 'Replace raw_input() with input()',
            'common_mistakes': [
                'Using old input() for expression evaluation without eval()',
                'Not validating user input'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        },
        
        'dict_methods': {
            'title': 'Dictionary Method Changes',
            'category': 'Built-ins',
            'problem': 'Dictionary methods return views instead of lists',
            'examples': [
                {
                    'py2': 'keys = d.keys(); keys.sort()',
                    'py3': 'keys = sorted(d.keys())',
                    'notes': 'Use sorted() instead of .sort()'
                },
                {
                    'py2': 'if d.has_key("x"):',
                    'py3': 'if "x" in d:',
                    'notes': 'has_key() removed, use "in" operator'
                }
            ],
            'quick_fix': 'Replace has_key() with "in" operator',
            'common_mistakes': [
                'Trying to use list methods on dict_keys/dict_values',
                'Not wrapping with list() when needed'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        },
        
        'relative_imports': {
            'title': 'Relative Import Changes',
            'category': 'Imports',
            'problem': 'Implicit relative imports no longer work in Python 3',
            'examples': [
                {
                    'py2': 'import module  # From same package',
                    'py3': 'from . import module',
                    'notes': 'Use explicit relative import'
                },
                {
                    'py2': 'from module import function',
                    'py3': 'from .module import function',
                    'notes': 'Add dot for relative import'
                }
            ],
            'quick_fix': 'Use absolute imports or explicit relative imports with dots',
            'common_mistakes': [
                'Mixing absolute and relative imports inconsistently',
                'Not updating package __init__.py files'
            ],
            'related_guides': ['IMPORT_OPTIMIZER_GUIDE.md']
        },
        
        'metaclass': {
            'title': 'Metaclass Syntax',
            'category': 'Advanced',
            'problem': 'Metaclass syntax changed significantly',
            'examples': [
                {
                    'py2': 'class MyClass:\n    __metaclass__ = Meta',
                    'py3': 'class MyClass(metaclass=Meta):',
                    'notes': 'Use keyword argument in class definition'
                }
            ],
            'quick_fix': 'Move __metaclass__ to class definition arguments',
            'common_mistakes': [
                'Not updating metaclass in inheritance hierarchies',
                'Forgetting to update custom metaclasses'
            ],
            'related_guides': ['MODERNIZER_GUIDE.md']
        },
        
        'long': {
            'title': 'Long Integer Type',
            'category': 'Built-ins',
            'problem': 'long type merged with int in Python 3',
            'examples': [
                {
                    'py2': 'x = 10L',
                    'py3': 'x = 10',
                    'notes': 'Remove L suffix from integers'
                },
                {
                    'py2': 'isinstance(x, long)',
                    'py3': 'isinstance(x, int)',
                    'notes': 'long is now int'
                }
            ],
            'quick_fix': 'Replace long with int, remove L suffixes',
            'common_mistakes': [
                'Checking for both int and long separately',
                'Not removing L suffixes'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        },
        
        'octal': {
            'title': 'Octal Literal Syntax',
            'category': 'Syntax',
            'problem': 'Octal literals must use 0o prefix in Python 3',
            'examples': [
                {
                    'py2': 'mode = 0755',
                    'py3': 'mode = 0o755',
                    'notes': 'Use 0o prefix for octal numbers'
                }
            ],
            'quick_fix': 'Replace leading 0 with 0o in octal literals',
            'common_mistakes': [
                'Missing octal literals in file permission settings',
                'Not updating chmod and umask values'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        },
        
        'reduce': {
            'title': 'reduce() Function',
            'category': 'Built-ins',
            'problem': 'reduce() moved from built-ins to functools',
            'examples': [
                {
                    'py2': 'result = reduce(lambda x, y: x+y, items)',
                    'py3': 'from functools import reduce\nresult = reduce(lambda x, y: x+y, items)',
                    'notes': 'Import from functools module'
                }
            ],
            'quick_fix': 'Add "from functools import reduce" at top of file',
            'common_mistakes': [
                'Forgetting the import',
                'Not considering alternatives like sum() or list comprehensions'
            ],
            'related_guides': ['IMPORT_OPTIMIZER_GUIDE.md']
        },
        
        'exec': {
            'title': 'exec Statement',
            'category': 'Built-ins',
            'problem': 'exec changed from statement to function',
            'examples': [
                {
                    'py2': 'exec code',
                    'py3': 'exec(code)',
                    'notes': 'Use as function with parentheses'
                },
                {
                    'py2': 'exec code in globals, locals',
                    'py3': 'exec(code, globals, locals)',
                    'notes': 'Pass namespaces as arguments'
                }
            ],
            'quick_fix': 'Add parentheses to exec statements',
            'common_mistakes': [
                'Not updating namespace specification',
                'Security issues with exec (consider alternatives)'
            ],
            'related_guides': ['PATTERNS_GUIDE.md']
        }
    }
    
    CATEGORIES = {
        'built-ins': ['print', 'input', 'dict_methods', 'reduce', 'exec', 'long'],
        'strings': ['unicode'],
        'imports': ['imports', 'relative_imports'],
        'iterators': ['iterators'],
        'exceptions': ['exceptions'],
        'operators': ['division'],
        'classes': ['classes', 'metaclass'],
        'syntax': ['octal'],
        'advanced': ['metaclass']
    }
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path
        self.detected_issues = None
    
    def get_tip(self, topic: str) -> Optional[Dict]:
        """Get a specific tip by topic."""
        return self.TIPS_DATABASE.get(topic.lower())
    
    def get_all_tips(self) -> Dict:
        """Get all available tips."""
        return self.TIPS_DATABASE
    
    def get_tips_by_category(self, category: str) -> Dict:
        """Get all tips in a specific category."""
        topic_ids = self.CATEGORIES.get(category.lower(), [])
        return {tid: self.TIPS_DATABASE[tid] for tid in topic_ids if tid in self.TIPS_DATABASE}
    
    def search_tips(self, query: str) -> Dict:
        """Search for tips matching a query."""
        query = query.lower()
        results = {}
        
        for topic_id, tip in self.TIPS_DATABASE.items():
            if query in topic_id.lower():
                results[topic_id] = tip
                continue
            
            if query in tip['title'].lower():
                results[topic_id] = tip
                continue
            
            if query in tip['problem'].lower():
                results[topic_id] = tip
                continue
            
            if query in tip['category'].lower():
                results[topic_id] = tip
                continue
        
        return results
    
    def scan_codebase(self, path: str) -> Dict[str, int]:
        """Scan codebase and detect which issues are present."""
        if not os.path.exists(path):
            return {}
        
        issue_counts = defaultdict(int)
        
        patterns = {
            'print': [
                r'^\s*print\s+["\']',  # print "string"
                r'^\s*print\s+\w+\s*$',  # print variable
                r'>>\s*sys\.',  # print >>sys.stderr
            ],
            'imports': [
                r'import\s+(ConfigParser|Queue|urllib2|urlparse|httplib)',
                r'from\s+(ConfigParser|Queue|urllib2|urlparse|httplib)',
            ],
            'unicode': [
                r'basestring',
                r'unicode\(',
                r'u["\']',
            ],
            'iterators': [
                r'\.iteritems\(',
                r'\.iterkeys\(',
                r'\.itervalues\(',
                r'xrange\(',
            ],
            'exceptions': [
                r'except\s+\w+\s*,\s*\w+:',
                r'raise\s+\w+\s*,',
            ],
            'dict_methods': [
                r'\.has_key\(',
            ],
            'input': [
                r'raw_input\(',
            ],
            'long': [
                r'\d+L\b',
                r'\blong\(',
            ],
            'reduce': [
                r'\breduce\(',
            ],
            'exec': [
                r'^\s*exec\s+[^(]',
            ],
        }
        
        if os.path.isfile(path):
            files_to_scan = [path]
        else:
            files_to_scan = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.py'):
                        files_to_scan.append(os.path.join(root, file))
        
        for filepath in files_to_scan:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for issue_type, pattern_list in patterns.items():
                        for pattern in pattern_list:
                            for line in lines:
                                if re.search(pattern, line):
                                    issue_counts[issue_type] += 1
            except Exception:
                continue
        
        self.detected_issues = dict(issue_counts)
        return self.detected_issues
    
    def get_relevant_tips(self, max_tips: int = 5) -> Dict:
        """Get tips most relevant to the scanned codebase."""
        if self.detected_issues is None and self.project_path:
            self.scan_codebase(self.project_path)
        
        if not self.detected_issues:
            return {}
        
        sorted_issues = sorted(
            self.detected_issues.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        relevant_tips = {}
        for issue_type, count in sorted_issues[:max_tips]:
            if issue_type in self.TIPS_DATABASE:
                relevant_tips[issue_type] = self.TIPS_DATABASE[issue_type]
                relevant_tips[issue_type]['detected_count'] = count
        
        return relevant_tips
    
    def format_tip(self, topic_id: str, tip: Dict, show_examples: bool = True,
                   show_related: bool = True, color: bool = True) -> str:
        """Format a tip for display."""
        lines = []
        
        if color:
            BOLD = '\033[1m'
            GREEN = '\033[92m'
            CYAN = '\033[96m'
            YELLOW = '\033[93m'
            RED = '\033[91m'
            BLUE = '\033[94m'
            RESET = '\033[0m'
        else:
            BOLD = GREEN = CYAN = YELLOW = RED = BLUE = RESET = ''
        
        lines.append(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
        lines.append(f"{BOLD}{GREEN}📚 {tip['title']}{RESET}")
        lines.append(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")
        
        lines.append(f"{BOLD}Category:{RESET} {tip['category']}")
        lines.append(f"{BOLD}Topic ID:{RESET} {topic_id}\n")
        
        if 'detected_count' in tip:
            lines.append(f"{YELLOW}⚠ Found {tip['detected_count']} instance(s) in your code{RESET}\n")
        
        lines.append(f"{BOLD}Problem:{RESET}")
        lines.append(f"  {tip['problem']}\n")
        
        if show_examples and tip['examples']:
            lines.append(f"{BOLD}Examples:{RESET}")
            for i, example in enumerate(tip['examples'], 1):
                lines.append(f"\n  {BOLD}Example {i}:{RESET}")
                lines.append(f"    {RED}Python 2:{RESET} {example['py2']}")
                lines.append(f"    {GREEN}Python 3:{RESET} {example['py3']}")
                if example.get('notes'):
                    lines.append(f"    {CYAN}Note:{RESET} {example['notes']}")
            lines.append("")
        
        lines.append(f"{BOLD}{GREEN}✓ Quick Fix:{RESET}")
        lines.append(f"  {tip['quick_fix']}\n")
        
        if tip['common_mistakes']:
            lines.append(f"{BOLD}{YELLOW}⚠ Common Mistakes:{RESET}")
            for mistake in tip['common_mistakes']:
                lines.append(f"  • {mistake}")
            lines.append("")
        
        if show_related and tip['related_guides']:
            lines.append(f"{BOLD}{BLUE}📖 Related Guides:{RESET}")
            for guide in tip['related_guides']:
                lines.append(f"  • {guide}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def list_all_topics(self) -> List[str]:
        """List all available tip topics."""
        return sorted(self.TIPS_DATABASE.keys())
    
    def list_categories(self) -> List[str]:
        """List all available categories."""
        return sorted(self.CATEGORIES.keys())


def main():
    """CLI interface for tips engine (standalone mode)."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tips_engine.py <topic|--all|--scan path>")
        print("\nAvailable topics:")
        engine = TipsEngine()
        for topic in engine.list_all_topics():
            print(f"  - {topic}")
        sys.exit(0)
    
    engine = TipsEngine()
    
    if sys.argv[1] == '--all':
        for topic_id in engine.list_all_topics():
            tip = engine.get_tip(topic_id)
            print(engine.format_tip(topic_id, tip))
    elif sys.argv[1] == '--scan' and len(sys.argv) > 2:
        path = sys.argv[2]
        engine.project_path = path
        relevant = engine.get_relevant_tips()
        print(f"\n🔍 Scanned: {path}")
        print(f"Found {len(engine.detected_issues)} types of issues\n")
        for topic_id, tip in relevant.items():
            print(engine.format_tip(topic_id, tip))
    else:
        topic = sys.argv[1]
        tip = engine.get_tip(topic)
        if tip:
            print(engine.format_tip(topic, tip))
        else:
            print(f"❌ Tip not found: {topic}")
            print("\nDid you mean one of these?")
            results = engine.search_tips(topic)
            for tid in results:
                print(f"  - {tid}")


if __name__ == '__main__':
    main()
