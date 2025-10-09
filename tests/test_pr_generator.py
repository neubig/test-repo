#!/usr/bin/env python3
"""
Unit tests for PR Generator module.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pr_generator import PRGenerator, PRGeneratorError


class TestPRGenerator(unittest.TestCase):
    """Test cases for PRGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = PRGenerator(repo_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test PRGenerator initialization."""
        self.assertEqual(self.generator.repo_path, self.temp_dir)
        self.assertIsNotNone(self.generator.stats_file)
        self.assertIsNotNone(self.generator.journal_file)
    
    def test_init_with_token(self):
        """Test PRGenerator initialization with GitHub token."""
        token = "ghp_test_token"
        generator = PRGenerator(github_token=token)
        self.assertEqual(generator.github_token, token)
    
    def test_analyze_diff_print_statement(self):
        """Test detection of print statement changes."""
        diff = '''
        -    print "Hello, World!"
        +    print("Hello, World!")
        '''
        changes = self.generator._analyze_diff(diff)
        self.assertIn('print_statement', changes)
        self.assertGreater(changes['print_statement'], 0)
    
    def test_analyze_diff_import_change(self):
        """Test detection of import changes."""
        diff = '''
        -import urllib2
        +import urllib.request
        '''
        changes = self.generator._analyze_diff(diff)
        self.assertIn('import_change', changes)
    
    def test_analyze_diff_exception_syntax(self):
        """Test detection of exception syntax changes."""
        diff = '''
        -except ValueError, e:
        +except ValueError as e:
        '''
        changes = self.generator._analyze_diff(diff)
        self.assertIn('exception_syntax', changes)
    
    def test_analyze_diff_iterator_method(self):
        """Test detection of iterator method changes."""
        diff = '''
        -for key, value in data.iteritems():
        +for key, value in data.items():
        '''
        changes = self.generator._analyze_diff(diff)
        self.assertIn('iterator_method', changes)
    
    def test_analyze_diff_string_type(self):
        """Test detection of string type changes."""
        diff = '''
        -if isinstance(x, basestring):
        +if isinstance(x, str):
        '''
        changes = self.generator._analyze_diff(diff)
        self.assertIn('string_type', changes)
    
    def test_analyze_diff_xrange(self):
        """Test detection of xrange changes."""
        diff = '''
        -for i in xrange(10):
        +for i in range(10):
        '''
        changes = self.generator._analyze_diff(diff)
        self.assertIn('xrange', changes)
    
    def test_analyze_changes(self):
        """Test analysis of multiple file changes."""
        files = ['src/module1.py', 'src/module2.py', 'utils/helper.py']
        
        with patch.object(self.generator, 'get_file_authors', return_value=['user@example.com']):
            with patch.object(self.generator, '_run_git_command') as mock_git:
                mock_git.return_value = (0, '-print "test"\n+print("test")', '')
                
                analysis = self.generator.analyze_changes(files)
                
                self.assertEqual(analysis['total_files'], 3)
                self.assertIn('src', analysis['files_by_module'])
                self.assertIn('utils', analysis['files_by_module'])
                self.assertGreater(len(analysis['files']), 0)
    
    def test_generate_pr_title_single_module(self):
        """Test PR title generation for single module."""
        analysis = {
            'total_files': 3,
            'files_by_module': {'auth': ['auth/login.py', 'auth/session.py', 'auth/utils.py']}
        }
        
        title = self.generator.generate_pr_title(analysis)
        self.assertIn('auth', title)
        self.assertIn('3 files', title)
    
    def test_generate_pr_title_multiple_modules(self):
        """Test PR title generation for multiple modules."""
        analysis = {
            'total_files': 5,
            'files_by_module': {
                'auth': ['auth/login.py'],
                'utils': ['utils/helper.py'],
                'core': ['core/main.py']
            }
        }
        
        title = self.generator.generate_pr_title(analysis)
        self.assertIn('5 files', title)
    
    def test_generate_pr_description(self):
        """Test PR description generation."""
        analysis = {
            'total_files': 2,
            'files_by_module': {'auth': ['auth/login.py']},
            'changes_by_type': {'print_statement': 5, 'import_change': 3},
            'suggested_reviewers': {'user1@example.com', 'user2@example.com'}
        }
        
        description = self.generator.generate_pr_description(
            title="Test Migration",
            analysis=analysis
        )
        
        self.assertIn('Test Migration', description)
        self.assertIn('Files Modified', description)
        self.assertIn('2', description)
        self.assertIn('print', description.lower())
        self.assertIn('Testing Checklist', description)
        self.assertIn('Suggested Reviewers', description)
    
    def test_generate_pr_description_no_stats(self):
        """Test PR description generation without statistics."""
        analysis = {
            'total_files': 1,
            'files_by_module': {'test': ['test.py']},
            'changes_by_type': {},
            'suggested_reviewers': set()
        }
        
        description = self.generator.generate_pr_description(
            title="Test",
            analysis=analysis,
            include_stats=False
        )
        
        self.assertNotIn('Migration Statistics', description)
    
    def test_generate_pr_description_no_checklist(self):
        """Test PR description generation without checklist."""
        analysis = {
            'total_files': 1,
            'files_by_module': {'test': ['test.py']},
            'changes_by_type': {},
            'suggested_reviewers': set()
        }
        
        description = self.generator.generate_pr_description(
            title="Test",
            analysis=analysis,
            include_checklist=False
        )
        
        self.assertNotIn('Testing Checklist', description)
    
    @patch('pr_generator.PRGenerator._run_git_command')
    def test_get_changed_files(self, mock_git):
        """Test getting list of changed files."""
        mock_git.return_value = (0, 'src/file1.py\nsrc/file2.py\nREADME.md', '')
        
        files = self.generator.get_changed_files()
        
        self.assertEqual(len(files), 2)
        self.assertIn('src/file1.py', files)
        self.assertIn('src/file2.py', files)
        self.assertNotIn('README.md', files)
    
    @patch('pr_generator.PRGenerator._run_git_command')
    def test_get_changed_files_fallback_to_master(self, mock_git):
        """Test fallback to master branch when main doesn't exist."""
        # First call fails (main doesn't exist), second succeeds (master exists)
        mock_git.side_effect = [
            (1, '', 'unknown revision'),
            (0, 'src/file1.py', '')
        ]
        
        files = self.generator.get_changed_files('main')
        
        self.assertEqual(len(files), 1)
        self.assertEqual(mock_git.call_count, 2)
    
    @patch('pr_generator.PRGenerator._run_git_command')
    def test_get_file_authors(self, mock_git):
        """Test getting file authors."""
        mock_git.return_value = (
            0,
            'user1@example.com\nuser2@example.com\nuser1@example.com\nuser1@example.com',
            ''
        )
        
        authors = self.generator.get_file_authors('test.py', limit=2)
        
        self.assertEqual(len(authors), 2)
        self.assertEqual(authors[0], 'user1@example.com')
    
    def test_get_github_repo_info_https(self):
        """Test parsing GitHub HTTPS URL."""
        with patch.object(self.generator, '_run_git_command') as mock_git:
            mock_git.return_value = (0, 'https://github.com/owner/repo.git', '')
            
            owner, repo = self.generator.get_github_repo_info()
            
            self.assertEqual(owner, 'owner')
            self.assertEqual(repo, 'repo')
    
    def test_get_github_repo_info_ssh(self):
        """Test parsing GitHub SSH URL."""
        with patch.object(self.generator, '_run_git_command') as mock_git:
            mock_git.return_value = (0, 'git@github.com:owner/repo.git', '')
            
            owner, repo = self.generator.get_github_repo_info()
            
            self.assertEqual(owner, 'owner')
            self.assertEqual(repo, 'repo')
    
    def test_get_github_repo_info_invalid(self):
        """Test handling of invalid GitHub URL."""
        with patch.object(self.generator, '_run_git_command') as mock_git:
            mock_git.return_value = (0, 'https://gitlab.com/owner/repo.git', '')
            
            result = self.generator.get_github_repo_info()
            
            self.assertIsNone(result)
    
    @patch('pr_generator.PRGenerator._run_git_command')
    def test_create_pr_draft(self, mock_git):
        """Test creating a PR draft file."""
        # Mock git commands
        mock_git.side_effect = [
            (0, 'src/file1.py\nsrc/file2.py', ''),  # get_changed_files
            (0, 'user@example.com', ''),  # get_file_authors for file1
            (0, '-print "test"\n+print("test")', ''),  # diff for file1
            (0, 'user@example.com', ''),  # get_file_authors for file2
            (0, '-import urllib2\n+import urllib.request', ''),  # diff for file2
        ]
        
        output_file = 'test_pr.md'
        result = self.generator.create_pr_draft(output_file)
        
        self.assertTrue(os.path.exists(result))
        
        with open(result, 'r') as f:
            content = f.read()
            self.assertIn('TITLE:', content)
            self.assertIn('Python 3 Migration', content)
    
    def test_create_pr_draft_no_files(self):
        """Test error when no files changed."""
        with patch.object(self.generator, 'get_changed_files', return_value=[]):
            with self.assertRaises(PRGeneratorError) as context:
                self.generator.create_pr_draft('test.md')
            
            self.assertIn('No changed Python files', str(context.exception))
    
    def test_issue_descriptions(self):
        """Test that all issue types have descriptions."""
        self.assertIn('print_statement', PRGenerator.ISSUE_DESCRIPTIONS)
        self.assertIn('import_change', PRGenerator.ISSUE_DESCRIPTIONS)
        self.assertIn('exception_syntax', PRGenerator.ISSUE_DESCRIPTIONS)
        self.assertGreater(len(PRGenerator.ISSUE_DESCRIPTIONS), 10)
    
    def test_create_github_pr_success(self):
        """Test successful GitHub PR creation."""
        try:
            import requests
            has_requests = True
        except ImportError:
            has_requests = False
        
        if not has_requests:
            self.skipTest("requests module not installed")
        
        with patch('requests.post') as mock_post:
            with patch('pr_generator.PRGenerator._run_git_command') as mock_git:
                with patch('pr_generator.PRGenerator.get_changed_files') as mock_files:
                    with patch('pr_generator.PRGenerator.analyze_changes') as mock_analyze:
                        # Setup mocks
                        self.generator.github_token = 'test_token'
                        mock_files.return_value = ['src/test.py']
                        mock_analyze.return_value = {
                            'total_files': 1,
                            'files_by_module': {'src': ['src/test.py']},
                            'changes_by_type': {'print_statement': 1},
                            'suggested_reviewers': set()
                        }
                        
                        # Mock git commands
                        mock_git.side_effect = [
                            (0, 'https://github.com/owner/repo.git', ''),  # get remote URL
                            (0, 'feature-branch', ''),  # get current branch
                        ]
                        
                        # Mock requests response
                        mock_response = Mock()
                        mock_response.status_code = 201
                        mock_response.json.return_value = {
                            'number': 123,
                            'html_url': 'https://github.com/owner/repo/pull/123'
                        }
                        mock_post.return_value = mock_response
                        
                        result = self.generator.create_github_pr()
                        
                        self.assertTrue(result['success'])
                        self.assertEqual(result['pr_number'], 123)
                        self.assertIn('pull/123', result['pr_url'])
    
    @patch('pr_generator.PRGenerator.analyze_changes')
    @patch('pr_generator.PRGenerator.get_changed_files')
    @patch('pr_generator.PRGenerator._run_git_command')
    def test_create_github_pr_no_token(self, mock_git, mock_files, mock_analyze):
        """Test error when GitHub token is missing."""
        # Clear environment before creating generator to ensure no token
        with patch.dict('os.environ', {}, clear=True):
            generator = PRGenerator(github_token=None)
            
            # Mock git commands to pass initial checks
            mock_git.side_effect = [
                (0, 'https://github.com/owner/repo.git', ''),  # get remote
                (0, 'feature-branch', ''),  # get current branch (not main)
            ]
            mock_files.return_value = ['src/test.py']
            mock_analyze.return_value = {
                'total_files': 1,
                'files_by_module': {'src': ['src/test.py']},
                'changes_by_type': {},
                'suggested_reviewers': set()
            }
            
            with self.assertRaises(PRGeneratorError) as context:
                generator.create_github_pr()
            
            self.assertIn('token not found', str(context.exception).lower())
    
    @patch('pr_generator.PRGenerator._run_git_command')
    def test_create_github_pr_no_repo_info(self, mock_git):
        """Test error when repository info cannot be determined."""
        self.generator.github_token = 'test_token'
        mock_git.return_value = (1, '', 'error')
        
        with self.assertRaises(PRGeneratorError) as context:
            self.generator.create_github_pr()
        
        self.assertIn('Could not determine GitHub repository', str(context.exception))
    
    @patch('pr_generator.PRGenerator._run_git_command')
    def test_create_github_pr_on_base_branch(self, mock_git):
        """Test error when on base branch."""
        self.generator.github_token = 'test_token'
        mock_git.side_effect = [
            (0, 'https://github.com/owner/repo.git', ''),  # get remote
            (0, 'main', ''),  # get current branch
        ]
        
        with self.assertRaises(PRGeneratorError) as context:
            self.generator.create_github_pr(base_branch='main')
        
        self.assertIn('Must be on a feature branch', str(context.exception))
    
    def test_create_github_pr_with_labels(self):
        """Test GitHub PR creation with labels."""
        try:
            import requests
            has_requests = True
        except ImportError:
            has_requests = False
        
        if not has_requests:
            self.skipTest("requests module not installed")
        
        with patch('requests.post') as mock_post:
            with patch('pr_generator.PRGenerator._run_git_command') as mock_git:
                with patch('pr_generator.PRGenerator.get_changed_files') as mock_files:
                    with patch('pr_generator.PRGenerator.analyze_changes') as mock_analyze:
                        self.generator.github_token = 'test_token'
                        mock_files.return_value = ['src/test.py']
                        mock_analyze.return_value = {
                            'total_files': 1,
                            'files_by_module': {'src': ['src/test.py']},
                            'changes_by_type': {},
                            'suggested_reviewers': set()
                        }
                        
                        mock_git.side_effect = [
                            (0, 'https://github.com/owner/repo.git', ''),
                            (0, 'feature-branch', ''),
                        ]
                        
                        # Mock requests response
                        mock_response = Mock()
                        mock_response.status_code = 201
                        mock_response.json.return_value = {
                            'number': 123,
                            'html_url': 'https://github.com/owner/repo/pull/123'
                        }
                        mock_post.return_value = mock_response
                        
                        result = self.generator.create_github_pr(labels=['migration', 'python3'])
                        
                        # Should call post twice: once for PR, once for labels
                        self.assertEqual(mock_post.call_count, 2)


class TestPRGeneratorIntegration(unittest.TestCase):
    """Integration tests for PRGenerator."""
    
    def test_full_workflow_draft(self):
        """Test complete workflow of generating a PR draft."""
        # This is more of a smoke test to ensure components work together
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = PRGenerator(repo_path=temp_dir)
            
            # Mock the git operations
            with patch.object(generator, 'get_changed_files', return_value=['src/test.py']):
                with patch.object(generator, 'get_file_authors', return_value=['user@example.com']):
                    with patch.object(generator, '_run_git_command') as mock_git:
                        mock_git.return_value = (0, '-print "test"\n+print("test")', '')
                        
                        output_path = generator.create_pr_draft('test_pr.md')
                        
                        self.assertTrue(os.path.exists(output_path))
                        
                        with open(output_path, 'r') as f:
                            content = f.read()
                            self.assertIn('Migration', content)
                            self.assertIn('Testing Checklist', content)


if __name__ == '__main__':
    unittest.main()
