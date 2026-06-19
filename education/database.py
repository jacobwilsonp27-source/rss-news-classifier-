"""
database.py
-----------
Responsibility:
  - Create SQLite database (news.db)
  - Store articles with the mandatory schema
  - Retrieve articles
  - Prevent duplicate entries (URL uniqueness check)

Table  : news
Schema : matches the mandatory PDF specification exactly.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
DB_PATH: Path = Path(__file__).parent / "news.db"

CREATE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS news (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    title                TEXT    NOT NULL,
    description          TEXT,
    content              TEXT,
    source               TEXT,
    url                  TEXT    UNIQUE NOT NULL,
    category             TEXT,
    category_confidence  REAL,
    sentiment            TEXT,
    sentiment_confidence REAL,
    published_date       TEXT
);
"""

INSERT_SQL: str = """
INSERT OR IGNORE INTO news
    (title, description, content, source, url,
     category, category_confidence,
     sentiment, sentiment_confidence,
     published_date)
VALUES
    (:title, :description, :content, :source, :url,
     :category, :category_confidence,
     :sentiment, :sentiment_confidence,
     :published_date);
"""


# ── Connection helper ─────────────────────────────────────────────────────────
def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row          # dict-like rows
    conn.execute("PRAGMA journal_mode=WAL;") # better concurrency
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


# ── Initialisation ────────────────────────────────────────────────────────────
def init_db() -> None:
    """Create the database and the *news* table if they don't exist."""
    with _get_connection() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    logger.info("Database initialised at %s", DB_PATH)


# ── Write ─────────────────────────────────────────────────────────────────────
def save_article(article: dict) -> bool:
    """
    Insert one article.  Silently skips duplicates (same URL).

    Returns True if inserted, False if skipped.
    """
    # Mandatory fields guard
    if not article.get("url") or not article.get("title"):
        logger.warning("Skipping article with missing url/title.")
        return False

    record = {
        "title":                article.get("title",                ""),
        "description":          article.get("description",          ""),
        "content":              article.get("content",              ""),
        "source":               article.get("source",               ""),
        "url":                  article["url"],
        "category":             article.get("category",             ""),
        "category_confidence":  article.get("category_confidence",  0.0),
        "sentiment":            article.get("sentiment",            ""),
        "sentiment_confidence": article.get("sentiment_confidence", 0.0),
        "published_date":       article.get("published_date",       ""),
    }

    with _get_connection() as conn:
        cursor = conn.execute(INSERT_SQL, record)
        conn.commit()

    if cursor.rowcount > 0:
        logger.info("Saved To Database | url=%s", article["url"])
        return True
    else:
        logger.debug("Duplicate skipped  | url=%s", article["url"])
        return False


def save_articles(articles: list[dict]) -> dict[str, int]:
    """Bulk-save articles.  Returns {'saved': n, 'skipped': m}."""
    saved = skipped = 0
    for article in articles:
        if save_article(article):
            saved += 1
        else:
            skipped += 1
    logger.info("Bulk save complete | saved=%d | skipped=%d", saved, skipped)
    return {"saved": saved, "skipped": skipped}


# ── Read ──────────────────────────────────────────────────────────────────────
def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def get_all_news(limit: int = 100, offset: int = 0) -> list[dict]:
    """Return all articles ordered by newest first."""
    sql = """
        SELECT * FROM news
        ORDER BY published_date DESC
        LIMIT ? OFFSET ?
    """
    with _get_connection() as conn:
        rows = conn.execute(sql, (limit, offset)).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_news_by_id(news_id: int) -> Optional[dict]:
    """Return a single article by primary key."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM news WHERE id = ?", (news_id,)
        ).fetchone()
    return _row_to_dict(row) if row else None


def get_news_by_sentiment(label: str) -> list[dict]:
    """Return articles filtered by sentiment label."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM news WHERE LOWER(sentiment) = LOWER(?) ORDER BY published_date DESC",
            (label,),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_news_by_category(category: str) -> list[dict]:
    """Return articles filtered by category name (case-insensitive)."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM news WHERE LOWER(category) = LOWER(?) ORDER BY published_date DESC",
            (category,),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def url_exists(url: str) -> bool:
    """Check whether a URL already exists in the database."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM news WHERE url = ?", (url,)
        ).fetchone()
    return row is not None


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("DB ready at:", DB_PATH)
    print("Total rows:", len(get_all_news()))
