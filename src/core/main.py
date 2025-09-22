#!/usr/bin/env python
"""
Main application entry point for a Python 2 web scraper and data processor.
This application demonstrates various Python 2 patterns that need upgrading.
"""

import sys
import os
from urlparse import urlparse, urljoin
from urllib2 import urlopen, HTTPError
from ConfigParser import ConfigParser
import cPickle as pickle
from StringIO import StringIO

from data.database import DatabaseManager
from web.web_scraper import WebScraper
from data.data_processor import DataProcessor
from utils.utils import Logger, FileHandler
from models.models import User, Article, Comment
from utils.validators import URLValidator, DataValidator


class MainApplication(object):
    """Main application class that orchestrates the web scraping and data processing."""
    
    def __init__(self, config_file='config.ini'):
        self.config = ConfigParser()
        self.config.read(config_file)
        
        self.logger = Logger(self.config.get('logging', 'level'))
        self.db_manager = DatabaseManager(
            host=self.config.get('database', 'host'),
            port=self.config.getint('database', 'port'),
            username=self.config.get('database', 'username'),
            password=self.config.get('database', 'password')
        )
        
        self.scraper = WebScraper(
            user_agent=self.config.get('scraper', 'user_agent'),
            timeout=self.config.getint('scraper', 'timeout')
        )
        
        self.processor = DataProcessor()
        self.file_handler = FileHandler()
        
    def run(self):
        """Main execution method."""
        # TODO(openhands-completed): Add proper logging instead of print statements
        self.logger.info("Starting application...")
        
        try:
            # Get URLs to scrape from config
            urls = self.config.get('scraper', 'urls').split(',')
            
            for url in urls:
                url = url.strip()
                if not URLValidator.is_valid(url):
                    print "Invalid URL: %s" % url
                    continue
                    
                print "Processing URL: %s" % url
                
                # Scrape the URL
                try:
                    content = self.scraper.scrape(url)
                    if content:
                        # Process the scraped data
                        articles = self.processor.extract_articles(content)
                        
                        # Save to database
                        for article in articles:
                            if DataValidator.validate_article(article):
                                self.db_manager.save_article(article)
                                print "Saved article: %s" % article.title
                            else:
                                print "Invalid article data, skipping..."
                                # TODO(openhands): Add detailed validation error reporting
                                
                except Exception as e:
                    self.logger.error("Error processing URL %s: %s" % (url, str(e)))
                    
        except Exception as e:
            self.logger.error("Application error: %s" % str(e))
            return 1
            
        print "Application completed successfully"
        return 0
        
    def cleanup(self):
        """Cleanup resources."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()


if __name__ == '__main__':
    app = MainApplication()
    try:
        exit_code = app.run()
        sys.exit(exit_code)
    finally:
        app.cleanup()