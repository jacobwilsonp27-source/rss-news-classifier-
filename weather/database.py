import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "weather_news.db"


def get_connection():
    """Create and return a SQLite database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enables dict-like row access
    return conn


def create_table():
    """
    Create the news table if it does not already exist.
    Schema is mandatory and identical across all modules.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            title                TEXT,
            description          TEXT,
            content              TEXT,
            source               TEXT,
            url                  TEXT UNIQUE,
            category             TEXT,
            category_confidence  REAL,
            sentiment            TEXT,
            sentiment_confidence REAL,
            published_date       TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database table verified / created successfully")


def is_duplicate(url: str) -> bool:
    """
    Check if an article with the given URL already exists in the database.

    Args:
        url (str): The article URL to check.

    Returns:
        bool: True if duplicate exists, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def save_article(article: dict) -> bool:
    """
    Save a processed article to the database.
    Skips insertion if the URL already exists (duplicate prevention).

    Args:
        article (dict): Fully processed article with all required fields.

    Returns:
        bool: True if saved, False if duplicate/skipped.
    """
    if is_duplicate(article["url"]):
        logger.info(f"Duplicate skipped: {article['url']}")
        return False

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO news (
                title, description, content, source, url,
                category, category_confidence,
                sentiment, sentiment_confidence, published_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article["title"],
            article["description"],
            article["content"],
            article["source"],
            article["url"],
            article["category"],
            article["category_confidence"],
            article["sentiment"],
            article["sentiment_confidence"],
            article["published_date"],
        ))
        conn.commit()
        logger.info(f"Saved To Database: {article['title'][:60]}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"IntegrityError - Duplicate URL: {article['url']}")
        return False
    finally:
        conn.close()


def get_all_articles() -> list:
    """Retrieve all articles from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_article_by_id(article_id: int) -> dict | None:
    """Retrieve a single article by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_articles_by_sentiment(label: str) -> list:
    """Retrieve all articles matching a given sentiment label."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE sentiment = ? ORDER BY id DESC", (label.lower(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_articles_by_category(category: str) -> list:
    """Retrieve all articles matching a given category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE category = ? ORDER BY id DESC", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
