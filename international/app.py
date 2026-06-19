"""
app.py

Category: International / World

Responsibility (per project standards document):
    - Create FastAPI server
    - Expose API endpoints
    - Connect all project components

Pipeline (per standards document):
    RSS Feed -> Fetch News -> Categorize News -> Analyze Sentiment ->
    Store in Database -> Provide API
"""

import logging

from fastapi import FastAPI, HTTPException

import database
from fetch_news import fetch_all_news
from categorize import categorize_article
from sentiment import analyze_sentiment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("app")

app = FastAPI(title="International / World News Module")


def run_pipeline() -> None:
    """
    Execute the full mandatory pipeline:
    Fetch -> Categorize -> Analyze Sentiment -> Store

    Connects fetch_news.py, categorize.py, sentiment.py, and database.py
    as required by app.py's responsibilities in the standards document.
    """
    articles = fetch_all_news()

    for article in articles:
        text_for_analysis = (
            f"{article.get('title', '')}. "
            f"{article.get('description', '')}"
        )

        category_result = categorize_article(text_for_analysis)

        # Store only International articles
        if category_result["category"] != "International":
            logger.info(
                f"Skipping article. Predicted category: "
                f"{category_result['category']}"
            )
            continue

        sentiment_result = analyze_sentiment(text_for_analysis)

        processed_article = {
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "content": article.get("content", ""),
            "source": article.get("source", ""),
            "url": article.get("url", ""),
            "category": category_result["category"],
            "category_confidence": category_result["confidence"],
            "sentiment": sentiment_result["sentiment"],
            "sentiment_confidence": sentiment_result["confidence"],
            "published_date": article.get("published_date", ""),
        }

        database.insert_article(processed_article)




import threading

@app.on_event("startup")
def startup_event():
    logger.info("API Started")
    database.init_db()

    threading.Thread(
        target=run_pipeline,
        daemon=True
    ).start()


@app.get("/news")
def get_all_news():
    """Get All News"""
    return database.get_all_articles()


@app.get("/news/{news_id}")
def get_news_by_id(news_id: int):
    """Get News By ID"""
    article = database.get_article_by_id(news_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/news/sentiment/{label}")
def get_news_by_sentiment(label: str):
    """Get News By Sentiment"""
    return database.get_articles_by_sentiment(label)


@app.get("/news/category/{category}")
def get_news_by_category(category: str):
    """Get News By Category"""
    return database.get_articles_by_category(category)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)