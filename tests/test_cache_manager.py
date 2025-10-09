#!/usr/bin/env python3
"""
Tests for the cache_manager module.
"""

import os
import sys
import tempfile
import shutil
import ast
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cache_manager import CacheManager


class TestCacheManager:
    """Test suite for CacheManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.test_dir, '.test_cache')
        self.cache = CacheManager(cache_dir=self.cache_dir)
        
        # Create test Python file
        self.test_file = os.path.join(self.test_dir, 'test.py')
        with open(self.test_file, 'w') as f:
            f.write('print("Hello, World!")\n')
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_cache_initialization(self):
        """Test cache manager initialization"""
        assert self.cache.cache_dir.exists()
        assert self.cache.ast_cache_dir.exists()
        assert self.cache.pattern_cache_dir.exists()
        assert self.cache.analysis_cache_dir.exists()
        assert self.cache.metadata_dir.exists()
    
    def test_ast_caching(self):
        """Test AST caching functionality"""
        # Parse file
        with open(self.test_file, 'r') as f:
            tree = ast.parse(f.read())
        
        # Cache AST
        self.cache.set_ast_cache(self.test_file, tree)
        
        # Retrieve from cache
        cached_tree = self.cache.get_ast_cache(self.test_file)
        assert cached_tree is not None
        assert isinstance(cached_tree, ast.Module)
        
        # Verify cache hit
        assert self.cache.stats['hits'] == 1
    
    def test_ast_cache_invalidation(self):
        """Test AST cache invalidation on file change"""
        # Parse and cache
        with open(self.test_file, 'r') as f:
            tree = ast.parse(f.read())
        self.cache.set_ast_cache(self.test_file, tree)
        
        # Modify file
        with open(self.test_file, 'w') as f:
            f.write('print("Modified!")\n')
        
        # Try to retrieve - should return None (invalidated)
        cached_tree = self.cache.get_ast_cache(self.test_file)
        assert cached_tree is None
    
    def test_pattern_caching(self):
        """Test pattern matching cache"""
        matches = [
            {'line': 1, 'pattern': 'print_statement'},
            {'line': 5, 'pattern': 'print_statement'}
        ]
        
        # Cache pattern matches
        self.cache.set_pattern_cache(self.test_file, 'print_statements', matches)
        
        # Retrieve from cache
        cached_matches = self.cache.get_pattern_cache(self.test_file, 'print_statements')
        assert cached_matches == matches
    
    def test_analysis_caching(self):
        """Test analysis results cache"""
        analysis = {
            'issues': 5,
            'complexity': 10,
            'lines': 100
        }
        
        # Cache analysis
        self.cache.set_analysis_cache(self.test_file, analysis)
        
        # Retrieve from cache
        cached_analysis = self.cache.get_analysis_cache(self.test_file)
        assert cached_analysis == analysis
    
    def test_file_invalidation(self):
        """Test invalidating specific file"""
        # Cache multiple types for same file
        with open(self.test_file, 'r') as f:
            tree = ast.parse(f.read())
        self.cache.set_ast_cache(self.test_file, tree)
        self.cache.set_pattern_cache(self.test_file, 'test', [])
        self.cache.set_analysis_cache(self.test_file, {})
        
        # Invalidate file
        removed = self.cache.invalidate_file(self.test_file)
        assert removed >= 1  # At least one entry removed
        
        # Verify cache is empty for this file
        assert self.cache.get_ast_cache(self.test_file) is None
    
    def test_cache_clearing(self):
        """Test clearing cache"""
        # Add some cache entries
        with open(self.test_file, 'r') as f:
            tree = ast.parse(f.read())
        self.cache.set_ast_cache(self.test_file, tree)
        
        # Clear cache
        removed = self.cache.clear_cache()
        assert removed >= 1
        
        # Verify cache is empty
        stats = self.cache.get_statistics()
        assert stats['total_entries'] == 0
    
    def test_cache_statistics(self):
        """Test cache statistics"""
        # Add cache entries
        with open(self.test_file, 'r') as f:
            tree = ast.parse(f.read())
        self.cache.set_ast_cache(self.test_file, tree)
        self.cache.get_ast_cache(self.test_file)  # Hit
        self.cache.get_pattern_cache(self.test_file, 'nonexistent')  # Miss
        
        stats = self.cache.get_statistics()
        assert stats['total_entries'] >= 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0
    
    def test_list_cached_files(self):
        """Test listing cached files"""
        # Cache a file
        with open(self.test_file, 'r') as f:
            tree = ast.parse(f.read())
        self.cache.set_ast_cache(self.test_file, tree)
        
        # List cached files
        cached_files = self.cache.list_cached_files()
        assert len(cached_files) == 1
        assert cached_files[0][0] == self.test_file
    
    def test_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        # Create multiple files
        file1 = os.path.join(self.test_dir, 'file1.py')
        file2 = os.path.join(self.test_dir, 'file2.py')
        
        for f in [file1, file2]:
            with open(f, 'w') as fp:
                fp.write('print("test")\n')
        
        # Cache and retrieve
        for f in [file1, file2]:
            with open(f, 'r') as fp:
                tree = ast.parse(fp.read())
            self.cache.set_ast_cache(f, tree)
            self.cache.get_ast_cache(f)  # Hit
        
        stats = self.cache.get_statistics()
        assert stats['hits'] == 2
        assert stats['hit_rate'] == 100.0


def test_cache_manager_default_directory():
    """Test cache manager with default directory"""
    cache = CacheManager()
    assert cache.cache_dir.name == '.py2to3_cache'


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
