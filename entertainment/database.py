"""
database.py - Entertainment Module

Responsibilities (per project standards):
    - Create SQLite database
    - Store articles
    - Retrieve articles
    - Prevent duplicates

Table Name: news
Schema (identical across all category modules):
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
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

DB_PATH = Path(__file__).parent / "news.db"

CREATE_TABLE_SQL = """
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
);
"""

CHECK_URL_SQL = "SELECT * FROM news WHERE url = ?"

INSERT_SQL = """
INSERT INTO news (
    title, description, content, source, url,
    category, category_confidence, sentiment, sentiment_confidence,
    published_date
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

SELECT_ALL_SQL = "SELECT * FROM news ORDER BY id DESC"
SELECT_BY_ID_SQL = "SELECT * FROM news WHERE id = ?"
SELECT_BY_SENTIMENT_SQL = "SELECT * FROM news WHERE sentiment = ?"
SELECT_BY_CATEGORY_SQL = "SELECT * FROM news WHERE category = ?"

COLUMNS = [
    "id", "title", "description", "content", "source", "url",
    "category", "category_confidence", "sentiment", "sentiment_confidence",
    "published_date",
]


def get_connection() -> sqlite3.Connection:
    """Open a connection to the Entertainment module's SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the news table if it doesn't already exist."""
    with get_connection() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    logger.info("Database initialized at %s", DB_PATH)


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {col: row[col] for col in COLUMNS}


def url_exists(url: str) -> bool:
    """Check if an article with this URL already exists in the database."""
    with get_connection() as conn:
        cursor = conn.execute(CHECK_URL_SQL, (url,))
        return cursor.fetchone() is not None


def insert_article(article: dict) -> bool:
    """
    Insert a processed article into the database.

    Skips insertion (and returns False) if the URL already exists,
    preventing duplicate news entries.

    Expected article dict keys:
        title, description, content, source, url,
        category, category_confidence, sentiment, sentiment_confidence,
        published_date
    """
    if url_exists(article.get("url", "")):
        logger.info("Duplicate URL skipped: %s", article.get("url"))
        return False

    with get_connection() as conn:
        conn.execute(
            INSERT_SQL,
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
            ),
        )
        conn.commit()

    logger.info("Saved To Database: %s", article.get("url"))
    return True


def get_all_news() -> list[dict]:
    """Retrieve all stored articles."""
    with get_connection() as conn:
        rows = conn.execute(SELECT_ALL_SQL).fetchall()
        return [_row_to_dict(row) for row in rows]


def get_news_by_id(news_id: int) -> dict | None:
    """Retrieve a single article by its id."""
    with get_connection() as conn:
        row = conn.execute(SELECT_BY_ID_SQL, (news_id,)).fetchone()
        return _row_to_dict(row) if row else None


def get_news_by_sentiment(label: str) -> list[dict]:
    """Retrieve all articles matching a given sentiment label."""
    with get_connection() as conn:
        rows = conn.execute(SELECT_BY_SENTIMENT_SQL, (label,)).fetchall()
        return [_row_to_dict(row) for row in rows]


def get_news_by_category(category: str) -> list[dict]:
    """Retrieve all articles matching a given category."""
    with get_connection() as conn:
        rows = conn.execute(SELECT_BY_CATEGORY_SQL, (category,)).fetchall()
        return [_row_to_dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print(f"Entertainment database ready at {DB_PATH}")
    news = get_all_news()

    print("Total articles in database:", len(news))