"""
database.py

Category: Health

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
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
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
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Use case-insensitive match and trim input to be resilient to user input
        normalized = category_name.strip()
        cursor.execute(
            "SELECT * FROM news WHERE category = ? COLLATE NOCASE ORDER BY id DESC",
            (normalized,)
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to retrieve articles with category {category_name}: {e}")
        return []
    finally:
        conn.close()