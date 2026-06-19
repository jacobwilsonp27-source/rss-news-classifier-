import sqlite3

DB_NAME = "news.db"


def create_table():
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

    print("Table Created Successfully")


def save_news(article):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO news (
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
        print("Saved:", article["title"])

    except sqlite3.IntegrityError:
        print("Duplicate News Skipped")

    conn.close()


if __name__ == "__main__":
    create_table()
