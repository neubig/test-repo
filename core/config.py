"""
Configuration management for Python 2 application.
Demonstrates ConfigParser and various Python 2 configuration patterns.
"""

import os
import sys
from ConfigParser import ConfigParser, SafeConfigParser
import cPickle as pickle
from StringIO import StringIO


class ApplicationConfig(object):
    """Main application configuration manager."""
    
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = SafeConfigParser()
        self.defaults = self._get_defaults()
        
        # Set defaults
        for section, options in self.defaults.iteritems():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option, value in options.iteritems():
                self.config.set(section, option, str(value))
                
        # Load from file if exists
        if os.path.exists(config_file):
            self.load_config()
        else:
            self.save_config()
            
    def _get_defaults(self):
        """Get default configuration values."""
        return {
            'database': {
                'host': 'localhost',
                'port': 3306,
                'username': 'scraper_user',
                'password': 'scraper_pass',
                'database': 'scraper_db',
                'charset': 'utf8',
                'pool_size': 10,
                'timeout': 30
            },
            'scraper': {
                'user_agent': 'Python-Scraper/1.0',
                'timeout': 30,
                'max_retries': 3,
                'delay_between_requests': 1,
                'urls': 'http://example.com/news,http://example.com/articles',
                'max_pages_per_site': 100,
                'respect_robots_txt': 'true',
                'concurrent_requests': 5
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'scraper.log',
                'max_file_size': '10MB',
                'backup_count': 5
            },
            'processing': {
                'min_article_length': 100,
                'max_article_length': 50000,
                'extract_images': 'true',
                'extract_links': 'true',
                'clean_html': 'true',
                'language_detection': 'true'
            },
            'cache': {
                'enabled': 'true',
                'directory': 'cache',
                'max_size': 1000,
                'ttl_hours': 24,
                'cleanup_interval': 3600
            },
            'export': {
                'formats': 'json,csv,xml',
                'output_directory': 'output',
                'filename_template': 'articles_{date}_{format}',
                'include_metadata': 'true',
                'compress_output': 'false'
            }
        }
        
    def load_config(self):
        """Load configuration from file."""
        try:
            self.config.read(self.config_file)
            return True
        except Exception as e:
            print "Error loading config: %s" % str(e)
            return False
            
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'wb') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print "Error saving config: %s" % str(e)
            return False
            
    def get(self, section, option, fallback=None):
        """Get configuration value."""
        try:
            return self.config.get(section, option)
        except:
            return fallback
            
    def getint(self, section, option, fallback=0):
        """Get integer configuration value."""
        try:
            return self.config.getint(section, option)
        except:
            return fallback
            
    def getfloat(self, section, option, fallback=0.0):
        """Get float configuration value."""
        try:
            return self.config.getfloat(section, option)
        except:
            return fallback
            
    def getboolean(self, section, option, fallback=False):
        """Get boolean configuration value."""
        try:
            return self.config.getboolean(section, option)
        except:
            return fallback
            
    def set(self, section, option, value):
        """Set configuration value."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        
    def get_section(self, section):
        """Get all options in a section as dictionary."""
        if not self.config.has_section(section):
            return {}
            
        return dict(self.config.items(section))
        
    def get_database_config(self):
        """Get database configuration."""
        return {
            'host': self.get('database', 'host'),
            'port': self.getint('database', 'port'),
            'username': self.get('database', 'username'),
            'password': self.get('database', 'password'),
            'database': self.get('database', 'database'),
            'charset': self.get('database', 'charset'),
            'pool_size': self.getint('database', 'pool_size'),
            'timeout': self.getint('database', 'timeout')
        }
        
    def get_scraper_config(self):
        """Get scraper configuration."""
        urls_string = self.get('scraper', 'urls', '')
        urls = [url.strip() for url in urls_string.split(',') if url.strip()]
        
        return {
            'user_agent': self.get('scraper', 'user_agent'),
            'timeout': self.getint('scraper', 'timeout'),
            'max_retries': self.getint('scraper', 'max_retries'),
            'delay_between_requests': self.getfloat('scraper', 'delay_between_requests'),
            'urls': urls,
            'max_pages_per_site': self.getint('scraper', 'max_pages_per_site'),
            'respect_robots_txt': self.getboolean('scraper', 'respect_robots_txt'),
            'concurrent_requests': self.getint('scraper', 'concurrent_requests')
        }
        
    def get_logging_config(self):
        """Get logging configuration."""
        return {
            'level': self.get('logging', 'level'),
            'format': self.get('logging', 'format'),
            'file': self.get('logging', 'file'),
            'max_file_size': self.get('logging', 'max_file_size'),
            'backup_count': self.getint('logging', 'backup_count')
        }
        
    def validate_config(self):
        """Validate configuration values."""
        errors = []
        
        # Validate database config
        db_config = self.get_database_config()
        if not db_config['host']:
            errors.append("Database host is required")
        if db_config['port'] <= 0 or db_config['port'] > 65535:
            errors.append("Database port must be between 1 and 65535")
        if not db_config['username']:
            errors.append("Database username is required")
            
        # Validate scraper config
        scraper_config = self.get_scraper_config()
        if not scraper_config['urls']:
            errors.append("At least one URL is required for scraping")
        if scraper_config['timeout'] <= 0:
            errors.append("Scraper timeout must be positive")
        if scraper_config['max_retries'] < 0:
            errors.append("Max retries cannot be negative")
            
        # Validate logging config
        logging_config = self.get_logging_config()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if logging_config['level'] not in valid_levels:
            errors.append("Invalid logging level: %s" % logging_config['level'])
            
        return errors
        
    def to_dict(self):
        """Convert configuration to dictionary."""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
        return config_dict
        
    def from_dict(self, config_dict):
        """Load configuration from dictionary."""
        for section, options in config_dict.iteritems():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option, value in options.iteritems():
                self.config.set(section, option, str(value))


class EnvironmentConfig(object):
    """Environment-specific configuration manager."""
    
    def __init__(self, environment='development'):
        self.environment = environment
        self.env_configs = {
            'development': {
                'debug': True,
                'database_host': 'localhost',
                'database_name': 'scraper_dev',
                'log_level': 'DEBUG',
                'cache_enabled': False
            },
            'testing': {
                'debug': True,
                'database_host': 'localhost',
                'database_name': 'scraper_test',
                'log_level': 'DEBUG',
                'cache_enabled': False
            },
            'staging': {
                'debug': False,
                'database_host': 'staging-db.example.com',
                'database_name': 'scraper_staging',
                'log_level': 'INFO',
                'cache_enabled': True
            },
            'production': {
                'debug': False,
                'database_host': 'prod-db.example.com',
                'database_name': 'scraper_prod',
                'log_level': 'WARNING',
                'cache_enabled': True
            }
        }
        
    def get_config(self):
        """Get configuration for current environment."""
        return self.env_configs.get(self.environment, self.env_configs['development'])
        
    def is_debug(self):
        """Check if debug mode is enabled."""
        return self.get_config().get('debug', False)
        
    def get_database_host(self):
        """Get database host for current environment."""
        return self.get_config().get('database_host', 'localhost')
        
    def get_log_level(self):
        """Get log level for current environment."""
        return self.get_config().get('log_level', 'INFO')


def load_config_from_env():
    """Load configuration from environment variables."""
    config = {}
    
    # Database configuration
    config['database'] = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', '3306')),
        'username': os.environ.get('DB_USERNAME', 'scraper_user'),
        'password': os.environ.get('DB_PASSWORD', 'scraper_pass'),
        'database': os.environ.get('DB_NAME', 'scraper_db')
    }
    
    # Scraper configuration
    config['scraper'] = {
        'user_agent': os.environ.get('SCRAPER_USER_AGENT', 'Python-Scraper/1.0'),
        'timeout': int(os.environ.get('SCRAPER_TIMEOUT', '30')),
        'max_retries': int(os.environ.get('SCRAPER_MAX_RETRIES', '3'))
    }
    
    # Logging configuration
    config['logging'] = {
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
        'file': os.environ.get('LOG_FILE', 'scraper.log')
    }
    
    return config


def create_sample_config(filename='config.ini.sample'):
    """Create a sample configuration file."""
    config = ApplicationConfig()
    
    # Add comments to the configuration
    config_content = """# Sample configuration file for Python 2 Scraper Application
# Copy this file to config.ini and modify as needed

[database]
# Database connection settings
host = localhost
port = 3306
username = scraper_user
password = scraper_pass
database = scraper_db
charset = utf8
pool_size = 10
timeout = 30

[scraper]
# Web scraping settings
user_agent = Python-Scraper/1.0
timeout = 30
max_retries = 3
delay_between_requests = 1
urls = http://example.com/news,http://example.com/articles
max_pages_per_site = 100
respect_robots_txt = true
concurrent_requests = 5

[logging]
# Logging configuration
level = INFO
format = %%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s
file = scraper.log
max_file_size = 10MB
backup_count = 5

[processing]
# Data processing settings
min_article_length = 100
max_article_length = 50000
extract_images = true
extract_links = true
clean_html = true
language_detection = true

[cache]
# Caching settings
enabled = true
directory = cache
max_size = 1000
ttl_hours = 24
cleanup_interval = 3600

[export]
# Export settings
formats = json,csv,xml
output_directory = output
filename_template = articles_{date}_{format}
include_metadata = true
compress_output = false
"""
    
    try:
        with open(filename, 'w') as f:
            f.write(config_content)
        return True
    except IOError:
        return False