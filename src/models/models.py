"""
Data models for Python 2 application.
Demonstrates old-style classes and Python 2 patterns.
"""

import datetime
from collections import OrderedDict


class User:
    """User model - old-style class without object inheritance."""

    def __init__(self, username, email, full_name=None):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.created_date = datetime.datetime.now()
        self.last_login = None
        self.is_active = True
        self.preferences = {}

    def __str__(self):
        return "User: %s (%s)" % (self.username, self.email)

    def __repr__(self):
        return "User(username='%s', email='%s')" % (self.username, self.email)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.datetime.now()

    def set_preference(self, key, value):
        """Set a user preference."""
        self.preferences[key] = value

    def get_preference(self, key, default=None):
        """Get a user preference."""
        return self.preferences.get(key, default)

    def to_dict(self):
        """Convert user to dictionary."""
        return OrderedDict(
            [
                ("username", self.username),
                ("email", self.email),
                ("full_name", self.full_name),
                ("created_date", str(self.created_date)),
                ("last_login", str(self.last_login) if self.last_login else None),
                ("is_active", self.is_active),
                ("preferences", self.preferences),
            ]
        )


class Article:
    """Article model - new-style class."""

    def __init__(self, title, content, url, author=None, publish_date=None):
        self.id = None
        self.title = title
        self.content = content
        self.url = url
        self.author = author
        self.publish_date = publish_date or datetime.date.today()
        self.created_date = datetime.datetime.now()
        self.updated_date = None
        self.comments = []
        self.tags = []
        self.metadata = {}
        self.view_count = 0

    def __str__(self):
        return "Article: %s" % self.title

    def __repr__(self):
        return "Article(title='%s', url='%s')" % (self.title, self.url)

    def __cmp__(self, other):
        """Python 2 comparison method."""
        if not isinstance(other, Article):
            return NotImplemented

        # Compare by publish date, then by title
        if self.publish_date != other.publish_date:
            return cmp(self.publish_date, other.publish_date)
        return cmp(self.title, other.title)

    def add_comment(self, comment):
        """Add a comment to the article."""
        if isinstance(comment, Comment):
            self.comments.append(comment)
        else:
            raise TypeError("Expected Comment object")

    def add_tag(self, tag):
        """Add a tag to the article."""
        if isinstance(tag, basestring) and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """Remove a tag from the article."""
        if tag in self.tags:
            self.tags.remove(tag)

    def get_word_count(self):
        """Get the word count of the article content."""
        return len(self.content.split())

    def get_reading_time(self, words_per_minute=200):
        """Estimate reading time in minutes."""
        word_count = self.get_word_count()
        return max(1, word_count / words_per_minute)

    def update_content(self, new_content):
        """Update article content and timestamp."""
        self.content = new_content
        self.updated_date = datetime.datetime.now()

    def increment_view_count(self):
        """Increment the view count."""
        self.view_count += 1

    def to_dict(self):
        """Convert article to dictionary."""
        return OrderedDict(
            [
                ("id", self.id),
                ("title", self.title),
                ("content", self.content),
                ("url", self.url),
                ("author", self.author),
                ("publish_date", str(self.publish_date)),
                ("created_date", str(self.created_date)),
                ("updated_date", str(self.updated_date) if self.updated_date else None),
                ("tags", self.tags),
                ("view_count", self.view_count),
                ("comment_count", len(self.comments)),
                ("word_count", self.get_word_count()),
                ("reading_time", self.get_reading_time()),
                ("metadata", self.metadata),
            ]
        )


class Comment:
    """Comment model - old-style class."""

    def __init__(self, author, content, post_date=None):
        self.id = None
        self.author = author
        self.content = content
        self.post_date = post_date or datetime.date.today()
        self.created_date = datetime.datetime.now()
        self.is_approved = False
        self.parent_comment_id = None
        self.replies = []

    def __str__(self):
        return "Comment by %s: %s..." % (self.author, self.content[:50])

    def __repr__(self):
        return "Comment(author='%s', content='%s...')" % (self.author, self.content[:30])

    def approve(self):
        """Approve the comment."""
        self.is_approved = True

    def add_reply(self, reply_comment):
        """Add a reply to this comment."""
        if isinstance(reply_comment, Comment):
            reply_comment.parent_comment_id = self.id
            self.replies.append(reply_comment)
        else:
            raise TypeError("Expected Comment object")

    def get_reply_count(self):
        """Get the number of replies."""
        return len(self.replies)

    def to_dict(self):
        """Convert comment to dictionary."""
        return OrderedDict(
            [
                ("id", self.id),
                ("author", self.author),
                ("content", self.content),
                ("post_date", str(self.post_date)),
                ("created_date", str(self.created_date)),
                ("is_approved", self.is_approved),
                ("parent_comment_id", self.parent_comment_id),
                ("reply_count", self.get_reply_count()),
            ]
        )


class Category:
    """Category model for organizing articles."""

    def __init__(self, name, description=None, parent_category=None):
        self.id = None
        self.name = name
        self.description = description
        self.parent_category = parent_category
        self.subcategories = []
        self.article_count = 0
        self.created_date = datetime.datetime.now()

    def __str__(self):
        return "Category: %s" % self.name

    def __repr__(self):
        return "Category(name='%s')" % self.name

    def add_subcategory(self, subcategory):
        """Add a subcategory."""
        if isinstance(subcategory, Category):
            subcategory.parent_category = self
            self.subcategories.append(subcategory)
        else:
            raise TypeError("Expected Category object")

    def get_full_path(self):
        """Get the full category path."""
        if self.parent_category:
            return "%s > %s" % (self.parent_category.get_full_path(), self.name)
        return self.name

    def to_dict(self):
        """Convert category to dictionary."""
        return OrderedDict(
            [
                ("id", self.id),
                ("name", self.name),
                ("description", self.description),
                ("parent_category", self.parent_category.name if self.parent_category else None),
                ("subcategory_count", len(self.subcategories)),
                ("article_count", self.article_count),
                ("full_path", self.get_full_path()),
                ("created_date", str(self.created_date)),
            ]
        )


class SearchResult:
    """Search result model - old-style class."""

    def __init__(self, query, results, total_count, page=1, per_page=10):
        self.query = query
        self.results = results
        self.total_count = total_count
        self.page = page
        self.per_page = per_page
        self.search_date = datetime.datetime.now()

    def __str__(self):
        return "SearchResult: %d results for '%s'" % (self.total_count, self.query)

    def get_total_pages(self):
        """Calculate total number of pages."""
        return (self.total_count + self.per_page - 1) / self.per_page

    def has_next_page(self):
        """Check if there's a next page."""
        return self.page < self.get_total_pages()

    def has_previous_page(self):
        """Check if there's a previous page."""
        return self.page > 1

    def get_result_range(self):
        """Get the range of results on current page."""
        start = (self.page - 1) * self.per_page + 1
        end = min(self.page * self.per_page, self.total_count)
        return start, end

    def to_dict(self):
        """Convert search result to dictionary."""
        start, end = self.get_result_range()
        return OrderedDict(
            [
                ("query", self.query),
                ("total_count", self.total_count),
                ("page", self.page),
                ("per_page", self.per_page),
                ("total_pages", self.get_total_pages()),
                ("result_range", "%d-%d" % (start, end)),
                ("has_next_page", self.has_next_page()),
                ("has_previous_page", self.has_previous_page()),
                ("search_date", str(self.search_date)),
                (
                    "results",
                    [
                        result.to_dict() if hasattr(result, "to_dict") else str(result)
                        for result in self.results
                    ],
                ),
            ]
        )
