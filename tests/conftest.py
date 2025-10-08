"""
Shared fixtures and configuration for pytest test suite.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add src directory to path for imports
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    # Cleanup
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)


@pytest.fixture
def sample_py2_file(temp_dir):
    """Create a sample Python 2 file for testing."""
    content = '''#!/usr/bin/env python
"""Sample Python 2 code for testing."""

import urllib2
from ConfigParser import ConfigParser
import cPickle as pickle
from StringIO import StringIO

class OldStyleClass:
    """Old-style class without object inheritance."""
    
    def __init__(self, value):
        self.value = value
    
    def __cmp__(self, other):
        return cmp(self.value, other.value)


def main():
    print "Hello, World!"
    
    # Using old exception syntax
    try:
        result = urllib2.urlopen("http://example.com")
        print "Success:", result.read()
    except Exception, e:
        print "Error:", e
    
    # Using old iteration methods
    data = {"key1": "value1", "key2": "value2"}
    for key, value in data.iteritems():
        print key, value
    
    # Using xrange
    for i in xrange(10):
        print i


if __name__ == "__main__":
    main()
'''
    file_path = temp_dir / "sample_py2.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_py3_file(temp_dir):
    """Create a sample Python 3 file for testing."""
    content = '''#!/usr/bin/env python3
"""Sample Python 3 code for testing."""

import urllib.request as urllib2
from configparser import ConfigParser
import pickle
from io import StringIO


class NewStyleClass:
    """New-style class."""
    
    def __init__(self, value):
        self.value = value


def main():
    print("Hello, World!")
    
    # Using new exception syntax
    try:
        result = urllib2.urlopen("http://example.com")
        print("Success:", result.read())
    except Exception as e:
        print("Error:", e)
    
    # Using new iteration methods
    data = {"key1": "value1", "key2": "value2"}
    for key, value in data.items():
        print(key, value)
    
    # Using range instead of xrange
    for i in range(10):
        print(i)


if __name__ == "__main__":
    main()
'''
    file_path = temp_dir / "sample_py3.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_directory(temp_dir):
    """Create a directory with multiple Python files for testing."""
    # Create directory structure
    module_dir = temp_dir / "test_module"
    module_dir.mkdir()
    
    # Create __init__.py
    (module_dir / "__init__.py").write_text('"""Test module."""\n')
    
    # Create a few Python files
    files = {
        "file1.py": '''print "File 1"
import urllib2
''',
        "file2.py": '''print "File 2"
from StringIO import StringIO
''',
        "file3.py": '''print "File 3"
for i in xrange(5):
    print i
''',
    }
    
    for filename, content in files.items():
        (module_dir / filename).write_text(content)
    
    return module_dir


@pytest.fixture
def backup_dir(temp_dir):
    """Create a backup directory for testing."""
    backup_path = temp_dir / "test_backups"
    backup_path.mkdir()
    return backup_path


@pytest.fixture
def config_file(temp_dir):
    """Create a sample configuration file for testing."""
    config_content = '''{
    "version": "1.0.0",
    "backup_dir": "test_backup",
    "report_output": "test_report.html",
    "auto_confirm": false,
    "verbose": true,
    "ignore_patterns": [
        "**/venv/**",
        "**/__pycache__/**"
    ],
    "fix_rules": {
        "fix_print_statements": true,
        "fix_imports": true
    }
}'''
    config_path = temp_dir / ".py2to3.config.json"
    config_path.write_text(config_content)
    return config_path
