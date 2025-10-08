#!/usr/bin/env python3
"""
Tests for the dependency analyzer module.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dependency_analyzer import DependencyAnalyzer


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        yield project_dir


@pytest.fixture
def sample_requirements(temp_project_dir):
    """Create a sample requirements.txt file."""
    req_file = temp_project_dir / 'requirements.txt'
    req_file.write_text("""
# Sample requirements file
Django>=2.0
requests==2.28.0
flask>=1.0
# mysql-python==1.2.5  # Python 2 only
pillow>=8.0
""")
    return req_file


@pytest.fixture
def sample_setup_py(temp_project_dir):
    """Create a sample setup.py file."""
    setup_file = temp_project_dir / 'setup.py'
    setup_file.write_text("""
from setuptools import setup

setup(
    name='test-package',
    version='1.0',
    install_requires=[
        'numpy>=1.19',
        'pandas>=1.0',
    ]
)
""")
    return setup_file


@pytest.fixture
def sample_python_files(temp_project_dir):
    """Create sample Python files with imports."""
    # File with Python 2 imports
    py2_file = temp_project_dir / 'old_code.py'
    py2_file.write_text("""
import urllib2
import ConfigParser
from Queue import Queue
import urlparse
""")
    
    # File with Python 3 imports
    py3_file = temp_project_dir / 'new_code.py'
    py3_file.write_text("""
import urllib.request
import configparser
from queue import Queue
import json
""")
    
    return py2_file, py3_file


class TestDependencyAnalyzer:
    """Test cases for DependencyAnalyzer class."""
    
    def test_init(self, temp_project_dir):
        """Test initialization."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        assert analyzer.project_path == temp_project_dir
        assert len(analyzer.dependencies) == 0
        assert len(analyzer.import_locations) == 0
        assert len(analyzer.issues) == 0
    
    def test_scan_requirements_txt(self, temp_project_dir, sample_requirements):
        """Test scanning requirements.txt."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_requirements_txt()
        
        # Should find the packages
        req_deps = analyzer.dependencies['requirements.txt']
        assert 'django' in req_deps
        assert 'requests' in req_deps
        assert 'flask' in req_deps
        assert 'pillow' in req_deps
    
    def test_scan_setup_py(self, temp_project_dir, sample_setup_py):
        """Test scanning setup.py."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_setup_py()
        
        # Should find install_requires packages
        setup_deps = analyzer.dependencies['setup.py']
        assert 'numpy' in setup_deps
        assert 'pandas' in setup_deps
    
    def test_scan_imports(self, temp_project_dir, sample_python_files):
        """Test scanning Python imports."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_imports()
        
        import_deps = analyzer.dependencies['imports']
        
        # Should find Python 2 imports
        assert 'urllib2' in import_deps
        assert 'ConfigParser' in import_deps
        assert 'Queue' in import_deps
        assert 'urlparse' in import_deps
        
        # Should find Python 3 imports
        assert 'urllib' in import_deps
        assert 'configparser' in import_deps
        assert 'queue' in import_deps
        assert 'json' in import_deps
    
    def test_analyze_compatibility_stdlib_renames(self, temp_project_dir, sample_python_files):
        """Test detection of standard library renames."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_imports()
        results = analyzer.analyze_compatibility()
        
        # Should identify renamed stdlib modules
        stdlib_renames = {item['package'] for item in results['stdlib_renames']}
        assert 'urllib2' in stdlib_renames
        assert 'ConfigParser' in stdlib_renames
        assert 'Queue' in stdlib_renames
        assert 'urlparse' in stdlib_renames
        
        # Check Python 3 names are provided
        for item in results['stdlib_renames']:
            assert 'py3_name' in item
            assert item['py3_name']  # Not empty
    
    def test_analyze_compatibility_known_packages(self, temp_project_dir, sample_requirements):
        """Test analysis of known third-party packages."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_requirements_txt()
        results = analyzer.analyze_compatibility()
        
        # Django should be in needs_upgrade (has version requirements)
        package_names = {item['package'] for item in results['needs_upgrade']}
        assert 'django' in package_names
        
        # Find Django entry and check details
        django_entry = next(item for item in results['needs_upgrade'] if item['package'] == 'django')
        assert 'min_version' in django_entry
        assert 'recommended' in django_entry
    
    def test_generate_report_text(self, temp_project_dir, sample_python_files):
        """Test text report generation."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_imports()
        report = analyzer.generate_report('text')
        
        # Check report contains expected sections
        assert 'Python 3 Dependency Compatibility Report' in report
        assert 'STANDARD LIBRARY RENAMES' in report
        assert 'urllib2' in report
        assert 'ConfigParser' in report
        assert 'RECOMMENDATIONS' in report
    
    def test_generate_report_json(self, temp_project_dir, sample_python_files):
        """Test JSON report generation."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_imports()
        report_json = analyzer.generate_report('json')
        
        # Parse JSON
        data = json.loads(report_json)
        
        # Check structure
        assert 'stdlib_renames' in data
        assert 'incompatible' in data
        assert 'needs_upgrade' in data
        assert 'compatible' in data
        assert 'unknown' in data
        
        # Check data types
        assert isinstance(data['stdlib_renames'], list)
        assert len(data['stdlib_renames']) > 0
    
    def test_scan_all(self, temp_project_dir, sample_requirements, sample_setup_py, sample_python_files):
        """Test scanning all sources."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_all()
        
        # Should have dependencies from all sources
        assert 'requirements.txt' in analyzer.dependencies
        assert 'setup.py' in analyzer.dependencies
        assert 'imports' in analyzer.dependencies
        
        # Check some packages from each source
        assert 'django' in analyzer.dependencies['requirements.txt']
        assert 'numpy' in analyzer.dependencies['setup.py']
        assert 'urllib2' in analyzer.dependencies['imports']
    
    def test_import_locations_tracking(self, temp_project_dir, sample_python_files):
        """Test that import locations are tracked correctly."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_imports()
        
        # Check that locations are recorded
        assert 'urllib2' in analyzer.import_locations
        locations = analyzer.import_locations['urllib2']
        assert len(locations) > 0
        
        # Check location structure
        loc = locations[0]
        assert 'source' in loc
        assert 'line' in loc
        assert 'raw' in loc
    
    def test_empty_project(self, temp_project_dir):
        """Test analyzer on empty project."""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.scan_all()
        results = analyzer.analyze_compatibility()
        
        # Should return empty results
        assert len(results['stdlib_renames']) == 0
        assert len(results['incompatible']) == 0
        assert len(results['needs_upgrade']) == 0


@pytest.mark.integration
class TestDependencyAnalyzerIntegration:
    """Integration tests for dependency analyzer."""
    
    def test_real_project_analysis(self):
        """Test analysis on the actual project."""
        # Get the project root (parent of tests directory)
        project_root = Path(__file__).parent.parent
        src_dir = project_root / 'src'
        
        if not src_dir.exists():
            pytest.skip("Source directory not found")
        
        analyzer = DependencyAnalyzer(src_dir)
        analyzer.scan_all()
        results = analyzer.analyze_compatibility()
        
        # Should find some standard library renames in the example code
        assert len(results['stdlib_renames']) > 0
        
        # Should be able to generate report without errors
        text_report = analyzer.generate_report('text')
        assert len(text_report) > 0
        
        json_report = analyzer.generate_report('json')
        data = json.loads(json_report)
        assert 'stdlib_renames' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
