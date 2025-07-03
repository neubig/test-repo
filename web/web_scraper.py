"""
Web scraping module for Python 2 application.
Demonstrates urllib2, HTMLParser, and other Python 2 web patterns.
"""

import gzip
import re
import time

import cookielib
import urllib2
from HTMLParser import HTMLParser
from StringIO import StringIO
from urlparse import urljoin
from utils.utils import Logger


class ArticleHTMLParser(HTMLParser):
    """Custom HTML parser to extract article content."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_article = False
        self.in_title = False
        self.in_content = False
        self.in_author = False
        self.in_date = False

        self.title = ""
        self.content = ""
        self.author = ""
        self.date = ""
        self.links = []

        self.current_data = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "article" or ("class" in attrs_dict and "article" in attrs_dict["class"]):
            self.in_article = True
        elif self.in_article:
            if tag in ["h1", "h2"] and ("class" in attrs_dict and "title" in attrs_dict["class"]):
                self.in_title = True
            elif tag == "div" and ("class" in attrs_dict and "content" in attrs_dict["class"]):
                self.in_content = True
            elif tag == "span" and ("class" in attrs_dict and "author" in attrs_dict["class"]):
                self.in_author = True
            elif tag == "time" or ("class" in attrs_dict and "date" in attrs_dict["class"]):
                self.in_date = True
            elif tag == "a" and "href" in attrs_dict:
                self.links.append(attrs_dict["href"])

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False
        elif self.in_article:
            if tag in ["h1", "h2"] and self.in_title:
                self.title = self.current_data.strip()
                self.in_title = False
                self.current_data = ""
            elif tag == "div" and self.in_content:
                self.content += self.current_data.strip() + "\n"
                self.in_content = False
                self.current_data = ""
            elif tag == "span" and self.in_author:
                self.author = self.current_data.strip()
                self.in_author = False
                self.current_data = ""
            elif tag in ["time", "span"] and self.in_date:
                self.date = self.current_data.strip()
                self.in_date = False
                self.current_data = ""

    def handle_data(self, data):
        if self.in_title or self.in_content or self.in_author or self.in_date:
            self.current_data += data


class WebScraper:
    """Web scraper that handles HTTP requests and HTML parsing."""

    def __init__(self, user_agent="Python-Scraper/1.0", timeout=30):
        self.user_agent = user_agent
        self.timeout = timeout
        self.logger = Logger("scraper")

        # Set up cookie handling
        self.cookie_jar = cookielib.CookieJar()

        # Create URL opener with cookie support
        cookie_processor = urllib2.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib2.build_opener(cookie_processor)

        # Set default headers
        self.opener.addheaders = [
            ("User-Agent", self.user_agent),
            ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
            ("Accept-Language", "en-US,en;q=0.5"),
            ("Accept-Encoding", "gzip, deflate"),
            ("Connection", "keep-alive"),
        ]

        # Install the opener
        urllib2.install_opener(self.opener)

    def scrape(self, url, max_retries=3):
        """Scrape content from a URL with retry logic."""
        for attempt in xrange(max_retries):
            try:
                return self._fetch_content(url)
            except (OSError, urllib2.HTTPError, urllib2.URLError) as e:
                self.logger.warning("Attempt %d failed for %s: %s" % (attempt + 1, url, str(e)))
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    self.logger.error("All attempts failed for %s" % url)
                    raise

    def _fetch_content(self, url):
        """Fetch content from URL."""
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request, timeout=self.timeout)

            # Handle gzip encoding
            content = response.read()
            if response.info().get("Content-Encoding") == "gzip":
                content = gzip.GzipFile(fileobj=StringIO(content)).read()

            # Decode content
            encoding = self._get_encoding(response, content)
            if encoding:
                try:
                    content = content.decode(encoding)
                except UnicodeDecodeError:
                    # Fallback to utf-8 with error handling
                    content = content.decode("utf-8", "replace")
            else:
                content = content.decode("utf-8", "replace")

            return {
                "url": url,
                "content": content,
                "status_code": response.getcode(),
                "headers": dict(response.info()),
                "final_url": response.geturl(),
            }

        except urllib2.HTTPError as e:
            if e.code == 404:
                self.logger.warning("Page not found: %s" % url)
                return None
            else:
                raise

    def _get_encoding(self, response, content):
        """Determine content encoding."""
        # Check Content-Type header
        content_type = response.info().get("Content-Type", "")
        charset_match = re.search(r"charset=([^;\s]+)", content_type)
        if charset_match:
            return charset_match.group(1)

        # Check HTML meta tag
        meta_match = re.search(r'<meta[^>]+charset=([^"\'>]+)', content[:1024])
        if meta_match:
            return meta_match.group(1)

        return None

    def parse_articles(self, html_content, base_url):
        """Parse articles from HTML content."""
        parser = ArticleHTMLParser()
        parser.feed(html_content)

        articles = []
        if parser.title:
            # Convert relative URLs to absolute
            absolute_links = []
            for link in parser.links:
                absolute_link = urljoin(base_url, link)
                absolute_links.append(absolute_link)

            article_data = {
                "title": parser.title,
                "content": parser.content,
                "author": parser.author,
                "date": parser.date,
                "links": absolute_links,
                "source_url": base_url,
            }
            articles.append(article_data)

        return articles

    def get_links(self, url, filter_pattern=None):
        """Extract all links from a page."""
        content_data = self.scrape(url)
        if not content_data:
            return []

        # Simple regex to find links
        link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
        links = re.findall(link_pattern, content_data["content"], re.IGNORECASE)

        # Convert to absolute URLs
        absolute_links = []
        for link in links:
            absolute_link = urljoin(url, link)
            if filter_pattern is None or re.search(filter_pattern, absolute_link):
                absolute_links.append(absolute_link)

        return list(set(absolute_links))  # Remove duplicates

    def download_file(self, url, filename):
        """Download a file from URL."""
        try:
            response = urllib2.urlopen(url, timeout=self.timeout)

            with open(filename, "wb") as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

            return True

        except Exception as e:
            self.logger.error("Failed to download %s: %s" % (url, str(e)))
            return False
