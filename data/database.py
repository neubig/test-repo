"""
Database management module for Python 2 application.
Demonstrates various Python 2 database patterns.
"""

import threading

import cPickle as pickle
import MySQLdb
from models.models import Article, Comment
from Queue import Empty, Queue
from utils.utils import Logger


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, host, port, username, password, database="scraper_db"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection = None
        self.logger = Logger("database")

        # Thread-local storage for connections
        self._local = threading.local()
        self._connection_pool = Queue(maxsize=10)

        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool."""
        for _ in xrange(5):  # Python 2 xrange
            try:
                conn = self._create_connection()
                self._connection_pool.put(conn)
            except Exception as e:
                self.logger.error("Failed to create connection: %s" % str(e))

    def _create_connection(self):
        """Create a new database connection."""
        return MySQLdb.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            passwd=self.password,
            db=self.database,
            charset="utf8",
        )

    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self._connection_pool.get(timeout=5)
        except Empty:
            # Create new connection if pool is empty
            return self._create_connection()

    def return_connection(self, conn):
        """Return connection to pool."""
        try:
            self._connection_pool.put(conn, timeout=1)
        except:
            # Pool is full, close the connection
            conn.close()

    def save_article(self, article):
        """Save an article to the database."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Serialize complex data using pickle
            metadata_blob = pickle.dumps(article.metadata)

            query = """
                INSERT INTO articles (title, content, url, author, publish_date, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                content = VALUES(content),
                metadata = VALUES(metadata)
            """

            cursor.execute(
                query,
                (
                    article.title.encode("utf-8"),
                    article.content.encode("utf-8"),
                    article.url,
                    article.author.encode("utf-8") if article.author else None,
                    article.publish_date,
                    metadata_blob,
                ),
            )

            article_id = cursor.lastrowid or self._get_article_id(cursor, article.url)

            # Save comments
            for comment in article.comments:
                self._save_comment(cursor, comment, article_id)

            conn.commit()
            return article_id

        except Exception as e:
            conn.rollback()
            self.logger.error("Error saving article: %s" % str(e))
            raise
        finally:
            self.return_connection(conn)

    def _get_article_id(self, cursor, url):
        """Get article ID by URL."""
        cursor.execute("SELECT id FROM articles WHERE url = %s", (url,))
        result = cursor.fetchone()
        return result[0] if result else None

    def _save_comment(self, cursor, comment, article_id):
        """Save a comment to the database."""
        query = """
            INSERT INTO comments (article_id, author, content, post_date)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                article_id,
                comment.author.encode("utf-8"),
                comment.content.encode("utf-8"),
                comment.post_date,
            ),
        )

    def get_articles(self, limit=100, offset=0):
        """Retrieve articles from database."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)

            query = """
                SELECT id, title, content, url, author, publish_date, metadata
                FROM articles
                ORDER BY publish_date DESC
                LIMIT %s OFFSET %s
            """

            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()

            articles = []
            for row in rows:
                # Deserialize metadata
                metadata = pickle.loads(str(row["metadata"])) if row["metadata"] else {}

                article = Article(
                    title=row["title"].decode("utf-8"),
                    content=row["content"].decode("utf-8"),
                    url=row["url"],
                    author=row["author"].decode("utf-8") if row["author"] else None,
                    publish_date=row["publish_date"],
                    metadata=metadata,
                )
                article.id = row["id"]

                # Load comments
                article.comments = self._get_comments(cursor, article.id)
                articles.append(article)

            return articles

        finally:
            self.return_connection(conn)

    def _get_comments(self, cursor, article_id):
        """Get comments for an article."""
        query = """
            SELECT author, content, post_date
            FROM comments
            WHERE article_id = %s
            ORDER BY post_date ASC
        """

        cursor.execute(query, (article_id,))
        rows = cursor.fetchall()

        comments = []
        for row in rows:
            comment = Comment(
                author=row["author"].decode("utf-8"),
                content=row["content"].decode("utf-8"),
                post_date=row["post_date"],
            )
            comments.append(comment)

        return comments

    def execute_raw_query(self, query, params=None):
        """Execute a raw SQL query."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())

            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount

        finally:
            self.return_connection(conn)

    def close(self):
        """Close all connections in the pool."""
        while not self._connection_pool.empty():
            try:
                conn = self._connection_pool.get_nowait()
                conn.close()
            except Empty:
                break
