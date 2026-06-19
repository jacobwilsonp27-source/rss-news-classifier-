"""
database.py
------------
Handles all SQLite database operations for the Technology news module.

Responsibilities (per project standards):
    - Create the SQLite database and the 'news' table if they don't exist yet
    - Insert new articles while preventing duplicate entries (based on URL)
    - Retrieve all articles
    - Retrieve a single article by ID
    - Retrieve articles filtered by sentiment label
    - Retrieve articles filtered by category

This file does NOT know anything about RSS feeds, AI models, or FastAPI.
It only knows how to talk to the SQLite database. This separation of
concerns means database.py can be reused almost unchanged by every other
category module (sports, politics, health, etc.) - only the data that
flows through it differs.
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("technology_module.database")

DB_NAME = "news.db"


def get_connection() -> sqlite3.Connection:
    """
    Opens a new connection to the news.db SQLite file.

    We open a fresh connection per operation rather than keeping one
    global connection open for the whole app's lifetime. SQLite
    connections are cheap to create, and this avoids threading issues
    since FastAPI can handle multiple requests at the same time.
    """
    conn = sqlite3.connect(DB_NAME)
    # row_factory lets us access columns by name (row["title"]) instead
    # of only by index (row[1]), which makes the rest of the code far
    # more readable and far less fragile to column reordering.
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Creates the 'news' table if it does not already exist.

    The schema matches the mandatory project standard exactly, so every
    category module's database is structurally identical and can later
    be merged or queried the same way.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
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
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized (news.db ready, 'news' table present).")


def article_exists(url: str) -> bool:
    """
    Checks whether an article with this URL is already stored.

    Per the project's database rules, the URL is the unique key used to
    prevent the same article being inserted twice - for example if the
    RSS feed is fetched again and still contains an article we already saved.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM news WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def insert_article(article: Dict[str, Any]) -> bool:
    """
    Inserts a single processed article into the database.

    `article` is expected to be a dict containing all of:
        title, description, content, source, url,
        category, category_confidence,
        sentiment, sentiment_confidence,
        published_date

    Returns True if the article was inserted, and False if it was
    skipped because a row with the same URL already exists.
    """
    if article_exists(article["url"]):
        logger.info(f"Skipped duplicate article: {article['url']}")
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO news (
            title, description, content, source, url,
            category, category_confidence,
            sentiment, sentiment_confidence,
            published_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article.get("title"),
            article.get("description"),
            article.get("content"),
            article.get("source"),
            article.get("url"),
            article.get("category"),
            article.get("category_confidence"),
            article.get("sentiment"),
            article.get("sentiment_confidence"),
            article.get("published_date"),
        ),
    )
    conn.commit()
    conn.close()
    logger.info(f"Saved To Database: {article.get('title')}")
    return True


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Converts a sqlite3.Row into the mandatory standard JSON dict shape."""
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


def get_all_news() -> List[Dict[str, Any]]:
    """Returns every article in the database, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_news_by_id(news_id: int) -> Optional[Dict[str, Any]]:
    """Returns one article by its database ID, or None if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE id = ?", (news_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_news_by_sentiment(label: str) -> List[Dict[str, Any]]:
    """Returns all articles with a given sentiment label (positive/negative/neutral)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM news WHERE sentiment = ? ORDER BY id DESC",
        (label.lower(),),
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_news_by_category(category: str) -> List[Dict[str, Any]]:
    """Returns all articles in a given category (case-insensitive match)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM news WHERE category = ? COLLATE NOCASE ORDER BY id DESC",
        (category,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


if __name__ == "__main__":
    # Independent test block - lets you verify database.py works correctly
    # by running `python database.py` directly, with no other files involved.
    logging.basicConfig(level=logging.INFO)

    init_db()

    test_article = {
        "title": "Test Article: New Chip Unveiled",
        "description": "A short fictional description used only to test database.py.",
        "content": "Full fictional content about a new chip launch, used only to test database.py in isolation.",
        "source": "Manual Test",
        "url": "https://example.com/test-article-1",
        "category": "Technology",
        "category_confidence": 0.99,
        "sentiment": "positive",
        "sentiment_confidence": 0.95,
        "published_date": "2026-06-17T00:00:00",
    }

    print("Inserting test article ->", insert_article(test_article))
    print("Inserting the same article again (should be skipped) ->", insert_article(test_article))
    print()
    print("All news in database:")
    for row in get_all_news():
        print(row)
