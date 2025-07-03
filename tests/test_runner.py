"""
Test runner for Python 2 application.
Demonstrates unittest patterns and Python 2 testing approaches.
"""

import unittest
import sys
import os
import datetime
from StringIO import StringIO
import cPickle as pickle

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.models import Article, Comment, User, Category
from utils.validators import URLValidator, EmailValidator, DataValidator
from utils.utils import Logger, FileHandler, CacheManager
from core.config import ApplicationConfig


class TestModels(unittest.TestCase):
    """Test cases for model classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.article = Article(
            title="Test Article",
            content="This is a test article with enough content to pass validation.",
            url="http://example.com/test-article",
            author="Test Author"
        )
        
        self.comment = Comment(
            author="Test Commenter",
            content="This is a test comment with sufficient content."
        )
        
        self.user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        
    def test_article_creation(self):
        """Test article creation and basic properties."""
        self.assertEqual(self.article.title, "Test Article")
        self.assertEqual(self.article.author, "Test Author")
        self.assertTrue(isinstance(self.article.publish_date, datetime.date))
        self.assertEqual(len(self.article.comments), 0)
        
    def test_article_add_comment(self):
        """Test adding comments to articles."""
        self.article.add_comment(self.comment)
        self.assertEqual(len(self.article.comments), 1)
        self.assertEqual(self.article.comments[0], self.comment)
        
    def test_article_word_count(self):
        """Test article word count calculation."""
        word_count = self.article.get_word_count()
        self.assertTrue(isinstance(word_count, int))
        self.assertGreater(word_count, 0)
        
    def test_article_comparison(self):
        """Test article comparison using __cmp__."""
        article2 = Article(
            title="Another Article",
            content="Another test article content.",
            url="http://example.com/another-article"
        )
        
        # Test comparison
        result = cmp(self.article, article2)
        self.assertTrue(isinstance(result, int))
        
    def test_comment_creation(self):
        """Test comment creation."""
        self.assertEqual(self.comment.author, "Test Commenter")
        self.assertFalse(self.comment.is_approved)
        self.assertEqual(len(self.comment.replies), 0)
        
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.is_active)
        
    def test_user_preferences(self):
        """Test user preferences functionality."""
        self.user.set_preference("theme", "dark")
        self.assertEqual(self.user.get_preference("theme"), "dark")
        self.assertIsNone(self.user.get_preference("nonexistent"))


class TestValidators(unittest.TestCase):
    """Test cases for validator classes."""
    
    def test_url_validation(self):
        """Test URL validation."""
        valid_urls = [
            "http://example.com",
            "https://www.example.com",
            "http://example.com/path",
            "https://example.com:8080/path?query=value"
        ]
        
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "",
            None,
            123
        ]
        
        for url in valid_urls:
            self.assertTrue(URLValidator.is_valid(url), "URL should be valid: %s" % url)
            
        for url in invalid_urls:
            self.assertFalse(URLValidator.is_valid(url), "URL should be invalid: %s" % url)
            
    def test_url_normalization(self):
        """Test URL normalization."""
        test_cases = [
            ("example.com", "http://example.com"),
            ("HTTP://EXAMPLE.COM", "http://example.com"),
            ("http://example.com:80", "http://example.com"),
            ("https://example.com:443", "https://example.com")
        ]
        
        for input_url, expected in test_cases:
            result = URLValidator.normalize_url(input_url)
            self.assertEqual(result, expected)
            
    def test_email_validation(self):
        """Test email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk"
        ]
        
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "test@",
            "",
            None,
            123
        ]
        
        for email in valid_emails:
            self.assertTrue(EmailValidator.is_valid(email))
            
        for email in invalid_emails:
            self.assertFalse(EmailValidator.is_valid(email))
            
    def test_article_validation(self):
        """Test article validation."""
        valid_article = Article(
            title="Valid Article Title",
            content="This is a valid article with sufficient content to pass validation checks.",
            url="http://example.com/valid-article"
        )
        
        self.assertTrue(DataValidator.validate_article(valid_article))
        
        # Test invalid cases
        invalid_article = Article(
            title="",  # Empty title
            content="Short",  # Too short content
            url="invalid-url"  # Invalid URL
        )
        
        self.assertFalse(DataValidator.validate_article(invalid_article))


class TestUtils(unittest.TestCase):
    """Test cases for utility classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_file = "test_file.txt"
        self.test_content = "Test content with unicode: café"
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            
    def test_logger_creation(self):
        """Test logger creation."""
        logger = Logger("test_logger", "DEBUG")
        self.assertEqual(logger.name, "test_logger")
        
    def test_file_handler_write_read(self):
        """Test file writing and reading."""
        handler = FileHandler()
        
        # Test writing
        success = handler.write_file(self.test_file, self.test_content)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Test reading
        content = handler.read_file(self.test_file)
        self.assertEqual(content, self.test_content)
        
    def test_cache_manager(self):
        """Test cache manager functionality."""
        cache = CacheManager(cache_dir="test_cache", max_size=5)
        
        # Test setting and getting
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        # Test default value
        self.assertEqual(cache.get("nonexistent", "default"), "default")
        
        # Clean up
        cache.clear()
        import shutil
        if os.path.exists("test_cache"):
            shutil.rmtree("test_cache")


class TestConfig(unittest.TestCase):
    """Test cases for configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config_file = "test_config.ini"
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
            
    def test_config_creation(self):
        """Test configuration creation with defaults."""
        config = ApplicationConfig(self.test_config_file)
        
        # Test default values
        self.assertEqual(config.get('database', 'host'), 'localhost')
        self.assertEqual(config.getint('database', 'port'), 3306)
        self.assertTrue(config.getboolean('cache', 'enabled'))
        
    def test_config_validation(self):
        """Test configuration validation."""
        config = ApplicationConfig(self.test_config_file)
        errors = config.validate_config()
        
        # Should have no errors with defaults
        self.assertEqual(len(errors), 0)
        
        # Test invalid configuration
        config.set('database', 'port', '-1')
        errors = config.validate_config()
        self.assertGreater(len(errors), 0)


class TestIntegration(unittest.TestCase):
    """Integration test cases."""
    
    def test_article_with_comments_validation(self):
        """Test article with comments validation."""
        article = Article(
            title="Integration Test Article",
            content="This is an integration test article with sufficient content.",
            url="http://example.com/integration-test"
        )
        
        comment1 = Comment(
            author="Commenter 1",
            content="This is the first comment on the article."
        )
        
        comment2 = Comment(
            author="Commenter 2",
            content="This is the second comment on the article."
        )
        
        article.add_comment(comment1)
        article.add_comment(comment2)
        
        # Validate article
        self.assertTrue(DataValidator.validate_article(article))
        
        # Validate comments
        for comment in article.comments:
            self.assertTrue(DataValidator.validate_comment(comment))
            
    def test_data_serialization(self):
        """Test data serialization with pickle."""
        article = Article(
            title="Serialization Test",
            content="Testing serialization of article data.",
            url="http://example.com/serialization-test"
        )
        
        # Serialize
        serialized = pickle.dumps(article)
        self.assertTrue(isinstance(serialized, str))
        
        # Deserialize
        deserialized = pickle.loads(serialized)
        self.assertEqual(deserialized.title, article.title)
        self.assertEqual(deserialized.content, article.content)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestModels,
        TestValidators,
        TestUtils,
        TestConfig,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        
    # Run tests
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print stream.getvalue()
    
    # Return summary
    return {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success': result.wasSuccessful()
    }


if __name__ == '__main__':
    print "Running Python 2 Application Tests..."
    print "=" * 50
    
    results = run_tests()
    
    print "\n" + "=" * 50
    print "Test Results Summary:"
    print "Tests run: %d" % results['tests_run']
    print "Failures: %d" % results['failures']
    print "Errors: %d" % results['errors']
    print "Success: %s" % ("Yes" if results['success'] else "No")
    
    if not results['success']:
        sys.exit(1)
    else:
        print "\nAll tests passed!"
        sys.exit(0)