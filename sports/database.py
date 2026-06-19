"""
database.py
Module: Sports
Compatible with: Python 3.12.10 / 3.14.6

Responsibilities:
- Create SQLite database
- Store articles
- Retrieve articles
- Prevent duplicates
"""

import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("database")

DB_NAME = "news.db"



import os

def init_db():
    print("DATABASE PATH:", os.path.abspath(DB_NAME))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    """)

    conn.commit()
    conn.close()

def article_exists(url: str) -> bool:
    """Check whether an article with the given URL already exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def insert_article(article: dict) -> bool:
    """
    Insert an article into the database if it does not already exist.

    Args:
        article (dict): Must contain title, description, content, source,
            url, category, category_confidence, sentiment,
            sentiment_confidence, published_date.

    Returns:
        bool: True if inserted, False if skipped (duplicate URL).
    """
    if article_exists(article["url"]):
        logger.info(f"Skipped duplicate: {article['url']}")
        return False

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO news (
            title, description, content, source, url,
            category, category_confidence, sentiment, sentiment_confidence, published_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
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
        ),
    )
    conn.commit()
    conn.close()
    logger.info(f"Saved To Database: {article['title']}")
    return True


def get_all_news() -> list[dict]:
    """Return all stored articles, most recent first."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_news_by_id(news_id: int) -> dict | None:
    """Return a single article by its id, or None if not found."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE id = ?", (news_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_news_by_sentiment(label: str) -> list[dict]:
    """Return all articles matching the given sentiment label."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM news WHERE sentiment = ? ORDER BY id DESC", (label.lower(),)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_news_by_category(category: str) -> list[dict]:
    """Return all articles matching the given category."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM news WHERE category = ? ORDER BY id DESC", (category,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print("news.db initialized with the 'news' table.")
