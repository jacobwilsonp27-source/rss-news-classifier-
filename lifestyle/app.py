from fastapi import FastAPI
import sqlite3

app = FastAPI()

DB_NAME = "news.db"


@app.get("/")
def home():
    return {"message": "Lifestyle News API Running"}


@app.get("/news")
def get_all_news():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news")

    news = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return news
@app.get("/news/{news_id}")
def get_news_by_id(news_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE id=?", (news_id,))

    news = cursor.fetchone()

    conn.close()

    return dict(news) if news else {"message": "News not found"}


@app.get("/news/category/{category}")
def get_news_by_category(category: str):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE category=?", (category,))

    news = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return news


@app.get("/news/sentiment/{label}")
def get_news_by_sentiment(label: str):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE sentiment=?", (label,))

    news = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return news