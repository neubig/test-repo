"""
Data processing module for Python 2 application.
Demonstrates text processing, regular expressions, and data transformation.
"""

import csv
import datetime
import json
import re
from collections import OrderedDict

from models.models import Article, Comment
from utils.utils import Logger


class DataProcessor:
    """Processes and transforms scraped data."""

    def __init__(self):
        self.logger = Logger("processor")

        # Compile regex patterns for better performance
        self.date_patterns = [
            re.compile(r"(\d{4})-(\d{2})-(\d{2})"),  # YYYY-MM-DD
            re.compile(r"(\d{2})/(\d{2})/(\d{4})"),  # MM/DD/YYYY
            re.compile(r"(\w+)\s+(\d{1,2}),\s+(\d{4})"),  # Month DD, YYYY
        ]

        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )

        # Month name mapping
        self.month_names = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }

    def extract_articles(self, scraped_data):
        """Extract and process articles from scraped data."""
        articles = []

        if isinstance(scraped_data, dict) and "content" in scraped_data:
            # Process single page
            page_articles = self._process_page_content(scraped_data)
            articles.extend(page_articles)
        elif isinstance(scraped_data, list):
            # Process multiple pages
            for page_data in scraped_data:
                page_articles = self._process_page_content(page_data)
                articles.extend(page_articles)

        return articles

    def _process_page_content(self, page_data):
        """Process content from a single page."""
        articles = []
        content = page_data.get("content", "")
        base_url = page_data.get("url", "")

        # Extract article blocks using various patterns
        article_blocks = self._extract_article_blocks(content)

        for block in article_blocks:
            try:
                article = self._parse_article_block(block, base_url)
                if article:
                    articles.append(article)
            except Exception as e:
                self.logger.warning("Failed to parse article block: %s" % str(e))

        return articles

    def _extract_article_blocks(self, html_content):
        """Extract potential article blocks from HTML."""
        # Look for common article containers
        patterns = [
            r"<article[^>]*>(.*?)</article>",
            r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*post[^"]*"[^>]*>(.*?)</div>',
            r'<section[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</section>',
        ]

        blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            blocks.extend(matches)

        return blocks

    def _parse_article_block(self, block_html, base_url):
        """Parse an individual article block."""
        # Extract title
        title = self._extract_title(block_html)
        if not title:
            return None

        # Extract content
        content = self._extract_content(block_html)

        # Extract metadata
        author = self._extract_author(block_html)
        publish_date = self._extract_date(block_html)

        # Extract comments
        comments = self._extract_comments(block_html)

        # Create article object
        article = Article(
            title=title, content=content, url=base_url, author=author, publish_date=publish_date
        )

        article.comments = comments
        article.metadata = {
            "word_count": len(content.split()),
            "extracted_emails": self.email_pattern.findall(content),
            "extracted_urls": self.url_pattern.findall(content),
            "processing_date": datetime.datetime.now(),
        }

        return article

    def _extract_title(self, html):
        """Extract title from HTML block."""
        patterns = [
            r"<h1[^>]*>(.*?)</h1>",
            r"<h2[^>]*>(.*?)</h2>",
            r"<title[^>]*>(.*?)</title>",
            r'<div[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</div>',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                title = re.sub(r"<[^>]+>", "", match.group(1))  # Strip HTML tags
                return title.strip()

        return None

    def _extract_content(self, html):
        """Extract main content from HTML block."""
        # Remove script and style tags
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)

        # Look for content containers
        patterns = [
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*body[^"]*"[^>]*>(.*?)</div>',
            r"<p[^>]*>(.*?)</p>",
        ]

        content_parts = []
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for match in matches:
                # Strip HTML tags but preserve structure
                clean_text = re.sub(r"<[^>]+>", " ", match)
                clean_text = re.sub(r"\s+", " ", clean_text).strip()
                if len(clean_text) > 50:  # Only include substantial content
                    content_parts.append(clean_text)

        return "\n\n".join(content_parts)

    def _extract_author(self, html):
        """Extract author from HTML block."""
        patterns = [
            r'<span[^>]*class="[^"]*author[^"]*"[^>]*>(.*?)</span>',
            r'<div[^>]*class="[^"]*byline[^"]*"[^>]*>(.*?)</div>',
            r'<p[^>]*class="[^"]*author[^"]*"[^>]*>(.*?)</p>',
            r"by\s+([A-Za-z\s]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                author = re.sub(r"<[^>]+>", "", match.group(1))
                author = re.sub(r"^by\s+", "", author, flags=re.IGNORECASE)
                return author.strip()

        return None

    def _extract_date(self, html):
        """Extract publication date from HTML block."""
        # Look for time tags first
        time_match = re.search(r'<time[^>]*datetime="([^"]+)"[^>]*>', html, re.IGNORECASE)
        if time_match:
            try:
                return datetime.datetime.strptime(time_match.group(1)[:10], "%Y-%m-%d").date()
            except ValueError:
                pass

        # Try various date patterns
        for pattern in self.date_patterns:
            match = pattern.search(html)
            if match:
                try:
                    if len(match.groups()) == 3:
                        if match.group(1).isdigit() and len(match.group(1)) == 4:
                            # YYYY-MM-DD format
                            year, month, day = (
                                int(match.group(1)),
                                int(match.group(2)),
                                int(match.group(3)),
                            )
                        elif match.group(3).isdigit() and len(match.group(3)) == 4:
                            # MM/DD/YYYY format
                            month, day, year = (
                                int(match.group(1)),
                                int(match.group(2)),
                                int(match.group(3)),
                            )
                        else:
                            # Month DD, YYYY format
                            month_name = match.group(1).lower()
                            if month_name in self.month_names:
                                month = self.month_names[month_name]
                                day = int(match.group(2))
                                year = int(match.group(3))
                            else:
                                continue

                        return datetime.date(year, month, day)
                except (ValueError, KeyError):
                    continue

        return None

    def _extract_comments(self, html):
        """Extract comments from HTML block."""
        comments = []

        # Look for comment sections
        comment_patterns = [
            r'<div[^>]*class="[^"]*comment[^"]*"[^>]*>(.*?)</div>',
            r'<li[^>]*class="[^"]*comment[^"]*"[^>]*>(.*?)</li>',
        ]

        for pattern in comment_patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for match in matches:
                comment = self._parse_comment(match)
                if comment:
                    comments.append(comment)

        return comments

    def _parse_comment(self, comment_html):
        """Parse individual comment."""
        author = self._extract_author(comment_html)
        content = self._extract_content(comment_html)
        date = self._extract_date(comment_html)

        if content and len(content.strip()) > 10:
            return Comment(
                author=author or "Anonymous",
                content=content,
                post_date=date or datetime.date.today(),
            )

        return None

    def export_to_csv(self, articles, filename):
        """Export articles to CSV format."""
        with open(filename, "wb") as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(["Title", "Author", "Date", "URL", "Content", "Comment Count"])

            # Write articles
            for article in articles:
                writer.writerow(
                    [
                        article.title.encode("utf-8"),
                        (article.author or "").encode("utf-8"),
                        str(article.publish_date) if article.publish_date else "",
                        article.url,
                        article.content[:500].encode("utf-8"),  # Truncate content
                        len(article.comments),
                    ]
                )

    def export_to_json(self, articles, filename):
        """Export articles to JSON format."""
        articles_data = []

        for article in articles:
            article_dict = OrderedDict(
                [
                    ("title", article.title),
                    ("author", article.author),
                    ("publish_date", str(article.publish_date) if article.publish_date else None),
                    ("url", article.url),
                    ("content", article.content),
                    (
                        "comments",
                        [
                            {
                                "author": comment.author,
                                "content": comment.content,
                                "post_date": str(comment.post_date),
                            }
                            for comment in article.comments
                        ],
                    ),
                    ("metadata", article.metadata),
                ]
            )
            articles_data.append(article_dict)

        with open(filename, "w") as jsonfile:
            json.dump(articles_data, jsonfile, indent=2, ensure_ascii=False)
