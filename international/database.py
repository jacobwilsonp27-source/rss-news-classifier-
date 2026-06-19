"""
database.py

Category: International / World

Responsibility (per project standards document):
    - Create SQLite database
    - Store articles
    - Retrieve articles
    - Prevent duplicates

Table Name: news
Schema (exactly as specified in the standards document):
    id INTEGER PRIMARY KEY
    title TEXT
    description TEXT
    content TEXT
    source TEXT
    url TEXT UNIQUE
    category TEXT
    category_confidence REAL
    sentiment TEXT
    sentiment_confidence REAL
    published_date TEXT
"""

import logging
import sqlite3
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("database")

DB_NAME = "news.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the SQLite database and the 'news' table if they do not
    already exist, using the mandatory schema.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                content TEXT,
                source TEXT,
                url TEXT UNIQUE,
                category TEXT,
                category_confidence REAL,
                sentiment TEXT,
                sentiment_confidence REAL,
                published_date TEXT
            )
            """
        )
        conn.commit()
        logger.info("Database initialized. 'news' table is ready.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()


def article_exists(url: str) -> bool:
    """
    Check if an article with the given URL already exists in the database.

    Implements the mandatory duplicate-prevention rule from the standards
    document.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM news WHERE url = ?", (url,))
        return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Failed to check existing article for URL {url}: {e}")
        return False
    finally:
        conn.close()


def insert_article(article: Dict) -> bool:
    """
    Insert a processed article into the database.

    Skips insertion if the URL already exists (duplicate prevention rule).

    Args:
        article: Dictionary containing the standard article fields:
            title, description, content, source, url, category,
            category_confidence, sentiment, sentiment_confidence,
            published_date

    Returns:
        True if the article was inserted, False if it was skipped
        (duplicate) or insertion failed.
    """
    if article_exists(article.get("url", "")):
        logger.info(f"Duplicate skipped - URL already exists: {article.get('url')}")
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO news (
                title, description, content, source, url,
                category, category_confidence, sentiment,
                sentiment_confidence, published_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                article.get("title", ""),
                article.get("description", ""),
                article.get("content", ""),
                article.get("source", ""),
                article.get("url", ""),
                article.get("category", ""),
                article.get("category_confidence", 0.0),
                article.get("sentiment", ""),
                article.get("sentiment_confidence", 0.0),
                article.get("published_date", ""),
            )
        )
        conn.commit()
        logger.info(f"Saved To Database - URL: {article.get('url')}")
        return True
    except sqlite3.IntegrityError:
        logger.info(f"Duplicate skipped (integrity constraint) - URL: {article.get('url')}")
        return False
    except Exception as e:
        logger.error(f"Failed to insert article: {e}")
        return False
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> Dict:
    """Convert a database row into the standard news JSON format."""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "content": row["content"],
        "source": row["source"],
        "url": row["url"],
        "category": row["category"],
        "category_confidence": row["category_confidence"],
        "sentiment": row["sentiment"],
        "sentiment_confidence": row["sentiment_confidence"],
        "published_date": row["published_date"],
    }


def get_all_articles() -> List[Dict]:
    """Retrieve all articles from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM news ORDER BY id DESC")
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to retrieve articles: {e}")
        return []
    finally:
        conn.close()


def get_article_by_id(article_id: int) -> Optional[Dict]:
    """Retrieve a single article by its ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        return row_to_dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to retrieve article with id {article_id}: {e}")
        return None
    finally:
        conn.close()


def get_articles_by_sentiment(sentiment_label: str) -> List[Dict]:
    """Retrieve all articles matching the given sentiment label."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM news WHERE sentiment = ? ORDER BY id DESC",
            (sentiment_label.lower(),)
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to retrieve articles with sentiment {sentiment_label}: {e}")
        return []
    finally:
        conn.close()


def get_articles_by_category(category_name: str) -> List[Dict]:
    """Retrieve all articles matching the given category."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM news WHERE category = ? ORDER BY id DESC",
            (category_name,)
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to retrieve articles with category {category_name}: {e}")
        return []
    finally:
        conn.close()