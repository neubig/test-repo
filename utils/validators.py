"""
Validation utilities for Python 2 application.
Demonstrates various validation patterns and string handling.
"""

import datetime
import re

from models.models import Article, Comment, User
from urlparse import urlparse


class URLValidator:
    """URL validation utilities."""

    # URL regex pattern
    URL_PATTERN = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    @classmethod
    def is_valid(cls, url):
        """Check if URL is valid."""
        if not isinstance(url, basestring):
            return False

        if not url:
            return False

        # Basic regex check
        if not cls.URL_PATTERN.match(url):
            return False

        # Additional checks using urlparse
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except:
            return False

    @classmethod
    def normalize_url(cls, url):
        """Normalize URL format."""
        if not cls.is_valid(url):
            return None

        # Add http:// if no scheme
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        # Parse and rebuild
        parsed = urlparse(url)

        # Normalize domain to lowercase
        netloc = parsed.netloc.lower()

        # Remove default ports
        if netloc.endswith(":80") and parsed.scheme == "http":
            netloc = netloc[:-3]
        elif netloc.endswith(":443") and parsed.scheme == "https":
            netloc = netloc[:-4]

        # Rebuild URL
        normalized = "%s://%s%s" % (parsed.scheme, netloc, parsed.path)

        if parsed.query:
            normalized += "?" + parsed.query
        if parsed.fragment:
            normalized += "#" + parsed.fragment

        return normalized

    @classmethod
    def get_domain(cls, url):
        """Extract domain from URL."""
        if not cls.is_valid(url):
            return None

        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return None


class EmailValidator:
    """Email validation utilities."""

    # Email regex pattern
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @classmethod
    def is_valid(cls, email):
        """Check if email is valid."""
        if not isinstance(email, basestring):
            return False

        if not email:
            return False

        # Basic regex check
        if not cls.EMAIL_PATTERN.match(email):
            return False

        # Additional checks
        if email.count("@") != 1:
            return False

        local, domain = email.split("@")

        # Check local part
        if len(local) > 64 or len(local) == 0:
            return False

        # Check domain part
        if len(domain) > 255 or len(domain) == 0:
            return False

        return True

    @classmethod
    def normalize_email(cls, email):
        """Normalize email format."""
        if not cls.is_valid(email):
            return None

        return email.lower().strip()


class DataValidator:
    """General data validation utilities."""

    @classmethod
    def validate_article(cls, article):
        """Validate Article object."""
        if not isinstance(article, Article):
            return False

        # Check required fields
        if not article.title or not isinstance(article.title, basestring):
            return False

        if not article.content or not isinstance(article.content, basestring):
            return False

        if not article.url or not URLValidator.is_valid(article.url):
            return False

        # Check title length
        if len(article.title.strip()) < 5:
            return False

        # Check content length
        if len(article.content.strip()) < 50:
            return False

        # Validate author if present
        if article.author and not isinstance(article.author, basestring):
            return False

        # Validate publish date
        if article.publish_date and not isinstance(article.publish_date, datetime.date):
            return False

        return True

    @classmethod
    def validate_comment(cls, comment):
        """Validate Comment object."""
        if not isinstance(comment, Comment):
            return False

        # Check required fields
        if not comment.author or not isinstance(comment.author, basestring):
            return False

        if not comment.content or not isinstance(comment.content, basestring):
            return False

        # Check content length
        if len(comment.content.strip()) < 5:
            return False

        # Check author length
        if len(comment.author.strip()) < 2:
            return False

        # Validate post date
        if comment.post_date and not isinstance(comment.post_date, datetime.date):
            return False

        return True

    @classmethod
    def validate_user(cls, user):
        """Validate User object."""
        if not isinstance(user, User):
            return False

        # Check required fields
        if not user.username or not isinstance(user.username, basestring):
            return False

        if not user.email or not EmailValidator.is_valid(user.email):
            return False

        # Check username format
        username_pattern = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
        if not username_pattern.match(user.username):
            return False

        # Check full name if present
        if user.full_name and not isinstance(user.full_name, basestring):
            return False

        return True

    @classmethod
    def sanitize_html(cls, html_content):
        """Basic HTML sanitization."""
        if not isinstance(html_content, basestring):
            return ""

        # Remove script tags
        html_content = re.sub(
            r"<script[^>]*>.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE
        )

        # Remove style tags
        html_content = re.sub(
            r"<style[^>]*>.*?</style>", "", html_content, flags=re.DOTALL | re.IGNORECASE
        )

        # Remove dangerous attributes
        dangerous_attrs = ["onclick", "onload", "onerror", "onmouseover", "onfocus"]
        for attr in dangerous_attrs:
            pattern = r'\s+%s\s*=\s*["\'][^"\']*["\']' % attr
            html_content = re.sub(pattern, "", html_content, flags=re.IGNORECASE)

        return html_content

    @classmethod
    def validate_date_string(cls, date_string, formats=None):
        """Validate and parse date string."""
        if not isinstance(date_string, basestring):
            return None

        if formats is None:
            formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S"]

        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_string, fmt).date()
            except ValueError:
                continue

        return None

    @classmethod
    def validate_integer(cls, value, min_value=None, max_value=None):
        """Validate integer value with optional range."""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False

        if min_value is not None and int_value < min_value:
            return False

        if max_value is not None and int_value > max_value:
            return False

        return True

    @classmethod
    def validate_string_length(cls, value, min_length=None, max_length=None):
        """Validate string length."""
        if not isinstance(value, basestring):
            return False

        length = len(value)

        if min_length is not None and length < min_length:
            return False

        if max_length is not None and length > max_length:
            return False

        return True

    @classmethod
    def clean_text(cls, text):
        """Clean and normalize text."""
        if not isinstance(text, basestring):
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove control characters
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        return text

    @classmethod
    def validate_phone_number(cls, phone):
        """Validate phone number format."""
        if not isinstance(phone, basestring):
            return False

        # Remove all non-digit characters
        digits_only = re.sub(r"\D", "", phone)

        # Check length (US format)
        if len(digits_only) == 10:
            return True
        elif len(digits_only) == 11 and digits_only.startswith("1"):
            return True

        return False

    @classmethod
    def validate_zip_code(cls, zip_code):
        """Validate US ZIP code format."""
        if not isinstance(zip_code, basestring):
            return False

        # 5-digit or 5+4 format
        zip_pattern = re.compile(r"^\d{5}(-\d{4})?$")
        return bool(zip_pattern.match(zip_code.strip()))
