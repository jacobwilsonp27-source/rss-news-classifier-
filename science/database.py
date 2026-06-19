import sqlite3

DB_NAME = "news.db"


def create_database():
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


def save_article(article):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO news
    (
        title,
        description,
        content,
        source,
        url,
        category,
        category_confidence,
        sentiment,
        sentiment_confidence,
        published_date
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        article["published_date"]
    ))

    conn.commit()
    conn.close()


def get_all_news():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM news")

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_news_by_id(news_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM news WHERE id = ?",
        (news_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def get_news_by_sentiment(label):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM news WHERE sentiment = ?",
        (label,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_news_by_category(category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM news WHERE category = ?",
        (category,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows