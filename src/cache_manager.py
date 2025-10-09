#!/usr/bin/env python3
"""
Smart Cache Manager for Python 2 to 3 Migration Tool

Speeds up repeated operations by caching:
- AST parsing results
- Pattern matching results
- File analysis results
- Dependency graphs

Automatically invalidates cache when files change.
"""

import os
import json
import pickle
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Dict, List, Tuple
from collections import defaultdict


class CacheManager:
    """Smart caching system for migration tool operations"""
    
    CACHE_VERSION = "1.0.0"
    DEFAULT_CACHE_DIR = ".py2to3_cache"
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files (default: .py2to3_cache)
        """
        self.cache_dir = Path(cache_dir or self.DEFAULT_CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache subdirectories
        self.ast_cache_dir = self.cache_dir / "ast"
        self.pattern_cache_dir = self.cache_dir / "patterns"
        self.analysis_cache_dir = self.cache_dir / "analysis"
        self.metadata_dir = self.cache_dir / "metadata"
        
        for d in [self.ast_cache_dir, self.pattern_cache_dir, 
                  self.analysis_cache_dir, self.metadata_dir]:
            d.mkdir(exist_ok=True)
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'total_size': 0
        }
        
        self._load_metadata()
    
    def _load_metadata(self):
        """Load cache metadata"""
        self.metadata_file = self.metadata_dir / "cache_metadata.json"
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                'version': self.CACHE_VERSION,
                'created': time.time(),
                'file_hashes': {},
                'stats': self.stats
            }
    
    def _save_metadata(self):
        """Save cache metadata"""
        self.metadata['stats'] = self.stats
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of file content"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _has_file_changed(self, filepath: str) -> bool:
        """Check if file has changed since last cache"""
        current_hash = self._get_file_hash(filepath)
        cached_hash = self.metadata['file_hashes'].get(filepath)
        return current_hash != cached_hash
    
    def _update_file_hash(self, filepath: str):
        """Update stored hash for file"""
        self.metadata['file_hashes'][filepath] = self._get_file_hash(filepath)
    
    def _get_cache_key(self, filepath: str, cache_type: str) -> str:
        """Generate cache key for filepath and type"""
        # Use relative path if possible for portability
        try:
            rel_path = os.path.relpath(filepath)
        except ValueError:
            rel_path = filepath
        
        # Create safe filename from path
        safe_name = rel_path.replace(os.sep, '_').replace('/', '_')
        file_hash = self._get_file_hash(filepath)[:8]
        return f"{safe_name}_{file_hash}"
    
    def get_ast_cache(self, filepath: str) -> Optional[Any]:
        """
        Retrieve cached AST for file
        
        Args:
            filepath: Path to Python file
            
        Returns:
            Cached AST or None if not cached or invalidated
        """
        if self._has_file_changed(filepath):
            self.stats['misses'] += 1
            return None
        
        cache_key = self._get_cache_key(filepath, 'ast')
        cache_file = self.ast_cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self.stats['hits'] += 1
                    return pickle.load(f)
            except Exception:
                self.stats['misses'] += 1
                return None
        
        self.stats['misses'] += 1
        return None
    
    def set_ast_cache(self, filepath: str, ast_tree: Any):
        """
        Cache AST for file
        
        Args:
            filepath: Path to Python file
            ast_tree: AST tree object
        """
        cache_key = self._get_cache_key(filepath, 'ast')
        cache_file = self.ast_cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(ast_tree, f)
            self._update_file_hash(filepath)
            self._save_metadata()
        except Exception:
            pass
    
    def get_pattern_cache(self, filepath: str, pattern_name: str) -> Optional[List]:
        """
        Retrieve cached pattern matching results
        
        Args:
            filepath: Path to Python file
            pattern_name: Name of pattern being matched
            
        Returns:
            List of matches or None if not cached
        """
        if self._has_file_changed(filepath):
            self.stats['misses'] += 1
            return None
        
        cache_key = self._get_cache_key(filepath, f'pattern_{pattern_name}')
        cache_file = self.pattern_cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.stats['hits'] += 1
                    return json.load(f)
            except Exception:
                self.stats['misses'] += 1
                return None
        
        self.stats['misses'] += 1
        return None
    
    def set_pattern_cache(self, filepath: str, pattern_name: str, matches: List):
        """
        Cache pattern matching results
        
        Args:
            filepath: Path to Python file
            pattern_name: Name of pattern being matched
            matches: List of pattern matches
        """
        cache_key = self._get_cache_key(filepath, f'pattern_{pattern_name}')
        cache_file = self.pattern_cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(matches, f)
            self._update_file_hash(filepath)
            self._save_metadata()
        except Exception:
            pass
    
    def get_analysis_cache(self, filepath: str) -> Optional[Dict]:
        """
        Retrieve cached file analysis results
        
        Args:
            filepath: Path to Python file
            
        Returns:
            Analysis results dict or None if not cached
        """
        if self._has_file_changed(filepath):
            self.stats['misses'] += 1
            return None
        
        cache_key = self._get_cache_key(filepath, 'analysis')
        cache_file = self.analysis_cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.stats['hits'] += 1
                    return json.load(f)
            except Exception:
                self.stats['misses'] += 1
                return None
        
        self.stats['misses'] += 1
        return None
    
    def set_analysis_cache(self, filepath: str, analysis: Dict):
        """
        Cache file analysis results
        
        Args:
            filepath: Path to Python file
            analysis: Analysis results dictionary
        """
        cache_key = self._get_cache_key(filepath, 'analysis')
        cache_file = self.analysis_cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            self._update_file_hash(filepath)
            self._save_metadata()
        except Exception:
            pass
    
    def invalidate_file(self, filepath: str) -> int:
        """
        Invalidate all cache entries for a specific file
        
        Args:
            filepath: Path to file to invalidate
            
        Returns:
            Number of cache entries removed
        """
        removed = 0
        cache_key_prefix = self._get_cache_key(filepath, '')
        
        for cache_dir in [self.ast_cache_dir, self.pattern_cache_dir, 
                          self.analysis_cache_dir]:
            for cache_file in cache_dir.glob(f"{cache_key_prefix}*"):
                try:
                    cache_file.unlink()
                    removed += 1
                except Exception:
                    pass
        
        # Remove from metadata
        if filepath in self.metadata['file_hashes']:
            del self.metadata['file_hashes'][filepath]
        
        self.stats['invalidations'] += removed
        self._save_metadata()
        return removed
    
    def clear_cache(self, cache_type: Optional[str] = None) -> int:
        """
        Clear cache entries
        
        Args:
            cache_type: Type of cache to clear (ast/patterns/analysis/all)
            
        Returns:
            Number of cache entries removed
        """
        removed = 0
        
        if cache_type == 'ast' or cache_type is None:
            removed += self._clear_directory(self.ast_cache_dir)
        
        if cache_type == 'patterns' or cache_type is None:
            removed += self._clear_directory(self.pattern_cache_dir)
        
        if cache_type == 'analysis' or cache_type is None:
            removed += self._clear_directory(self.analysis_cache_dir)
        
        if cache_type is None:
            self.metadata['file_hashes'] = {}
            self.stats = {
                'hits': 0,
                'misses': 0,
                'invalidations': 0,
                'total_size': 0
            }
        
        self._save_metadata()
        return removed
    
    def _clear_directory(self, directory: Path) -> int:
        """Clear all files in directory"""
        removed = 0
        for cache_file in directory.glob("*"):
            try:
                cache_file.unlink()
                removed += 1
            except Exception:
                pass
        return removed
    
    def get_statistics(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        total_entries = sum([
            len(list(self.ast_cache_dir.glob("*"))),
            len(list(self.pattern_cache_dir.glob("*"))),
            len(list(self.analysis_cache_dir.glob("*")))
        ])
        
        total_size = sum([
            sum(f.stat().st_size for f in self.ast_cache_dir.glob("*")),
            sum(f.stat().st_size for f in self.pattern_cache_dir.glob("*")),
            sum(f.stat().st_size for f in self.analysis_cache_dir.glob("*"))
        ])
        
        hit_rate = 0.0
        total_requests = self.stats['hits'] + self.stats['misses']
        if total_requests > 0:
            hit_rate = (self.stats['hits'] / total_requests) * 100
        
        return {
            'total_entries': total_entries,
            'ast_entries': len(list(self.ast_cache_dir.glob("*"))),
            'pattern_entries': len(list(self.pattern_cache_dir.glob("*"))),
            'analysis_entries': len(list(self.analysis_cache_dir.glob("*"))),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cached_files': len(self.metadata['file_hashes']),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'invalidations': self.stats['invalidations'],
            'cache_version': self.CACHE_VERSION
        }
    
    def print_statistics(self):
        """Print formatted cache statistics"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("  CACHE STATISTICS")
        print("="*60)
        print(f"\nCache Location: {self.cache_dir}")
        print(f"Cache Version: {stats['cache_version']}")
        print(f"\n📦 Cache Entries:")
        print(f"  Total Entries: {stats['total_entries']}")
        print(f"  ├─ AST Cache: {stats['ast_entries']}")
        print(f"  ├─ Pattern Cache: {stats['pattern_entries']}")
        print(f"  └─ Analysis Cache: {stats['analysis_entries']}")
        print(f"\n💾 Storage:")
        print(f"  Total Size: {stats['total_size_mb']} MB ({stats['total_size_bytes']:,} bytes)")
        print(f"  Cached Files: {stats['cached_files']}")
        print(f"\n📊 Performance:")
        print(f"  Cache Hits: {stats['hits']}")
        print(f"  Cache Misses: {stats['misses']}")
        print(f"  Hit Rate: {stats['hit_rate']}%")
        print(f"  Invalidations: {stats['invalidations']}")
        print("\n" + "="*60 + "\n")
    
    def list_cached_files(self) -> List[Tuple[str, str]]:
        """
        List all files currently in cache
        
        Returns:
            List of (filepath, hash) tuples
        """
        return [(fp, h) for fp, h in self.metadata['file_hashes'].items()]
    
    def optimize_cache(self, max_age_days: int = 7) -> int:
        """
        Remove old cache entries
        
        Args:
            max_age_days: Remove entries older than this many days
            
        Returns:
            Number of entries removed
        """
        removed = 0
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        
        for cache_dir in [self.ast_cache_dir, self.pattern_cache_dir, 
                          self.analysis_cache_dir]:
            for cache_file in cache_dir.glob("*"):
                try:
                    if cache_file.stat().st_mtime < cutoff_time:
                        cache_file.unlink()
                        removed += 1
                except Exception:
                    pass
        
        return removed


def main():
    """CLI interface for cache manager"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Smart Cache Manager for Python 2 to 3 Migration Tool'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Cache commands')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show cache statistics')
    stats_parser.add_argument('--json', action='store_true',
                             help='Output as JSON')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear cache')
    clear_parser.add_argument('--type', choices=['ast', 'patterns', 'analysis', 'all'],
                             default='all', help='Type of cache to clear')
    clear_parser.add_argument('--confirm', action='store_true',
                             help='Skip confirmation prompt')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List cached files')
    
    # Invalidate command
    inv_parser = subparsers.add_parser('invalidate', help='Invalidate specific file')
    inv_parser.add_argument('filepath', help='File to invalidate')
    
    # Optimize command
    opt_parser = subparsers.add_parser('optimize', help='Remove old cache entries')
    opt_parser.add_argument('--max-age', type=int, default=7,
                           help='Remove entries older than N days (default: 7)')
    
    args = parser.parse_args()
    
    cache = CacheManager()
    
    if args.command == 'stats':
        if args.json:
            print(json.dumps(cache.get_statistics(), indent=2))
        else:
            cache.print_statistics()
    
    elif args.command == 'clear':
        if not args.confirm:
            cache_type = args.type if args.type != 'all' else 'entire'
            response = input(f"Clear {cache_type} cache? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        removed = cache.clear_cache(None if args.type == 'all' else args.type)
        print(f"✓ Cleared {removed} cache entries")
    
    elif args.command == 'list':
        cached_files = cache.list_cached_files()
        if cached_files:
            print(f"\n📁 Cached Files ({len(cached_files)}):\n")
            for filepath, file_hash in cached_files:
                print(f"  {filepath} [{file_hash[:8]}]")
            print()
        else:
            print("No files in cache")
    
    elif args.command == 'invalidate':
        removed = cache.invalidate_file(args.filepath)
        print(f"✓ Invalidated {removed} cache entries for {args.filepath}")
    
    elif args.command == 'optimize':
        removed = cache.optimize_cache(args.max_age)
        print(f"✓ Removed {removed} old cache entries")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
