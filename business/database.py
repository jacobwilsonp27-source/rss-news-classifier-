import sqlite3

DB_NAME = "news.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
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
    ''')
    conn.commit()
    conn.close()
    print("LOG: Database Initialization Completed")

def check_url_exists(url: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM news WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def insert_news_article(article_data: dict) -> bool:
    target_url = article_data.get("url")
    if target_url is None or check_url_exists(target_url):
        return False
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news (
            title, description, content, source, url, 
            category, category_confidence, sentiment, sentiment_confidence, published_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        article_data.get("title"),
        article_data.get("description"),
        article_data.get("content"),
        article_data.get("source"),
        target_url,
        article_data.get("category"),
        article_data.get("category_confidence"),
        article_data.get("sentiment"),
        article_data.get("sentiment_confidence"),
        article_data.get("published_date")
    ))
    conn.commit()
    conn.close()
    print("LOG: Saved To Database")
    return True