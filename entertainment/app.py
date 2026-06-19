"""
app.py - Entertainment Module

Responsibilities (per project standards):
    - Create FastAPI server
    - Expose API endpoints
    - Connect all project components (fetch -> categorize -> sentiment -> store)

Pipeline:
    RSS Feed -> Fetch News -> Categorize News -> Analyze Sentiment
             -> Store in Database -> Provide API
"""

import logging

from fastapi import FastAPI, HTTPException

import database
import categorize
import sentiment
from fetch_news import fetch_all_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI(
    title="Entertainment News Categorization Module",
    description="AI-powered news categorization and sentiment analysis for the Entertainment category.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    """Initialize database and warm up models when the API starts."""
    database.init_db()
    logger.info("API Started")


def run_pipeline() -> dict:
    """
    Run the full news processing pipeline for the Entertainment category:
        1. Fetch RSS news
        2. Categorize each article (BART zero-shot)
        3. Analyze sentiment (RoBERTa)
        4. Store new articles in SQLite (duplicates skipped via URL check)

    Returns a summary of how many articles were fetched, stored, and skipped.
    """
    raw_articles = fetch_all_news()

    stored_count = 0
    skipped_count = 0

    for article in raw_articles:
        # Use title + description for richer context for both models.
        text_for_models = f"{article.get('title', '')}. {article.get('description', '')}".strip()

        category_result = categorize.categorize_article(text_for_models)
        sentiment_result = sentiment.analyze_sentiment(text_for_models)

        processed_article = {
            **article,
            "category": category_result["category"],
            "category_confidence": category_result["confidence"],
            "sentiment": sentiment_result["sentiment"],
            "sentiment_confidence": sentiment_result["confidence"],
        }

        was_inserted = database.insert_article(processed_article)
        if was_inserted:
            stored_count += 1
        else:
            skipped_count += 1

    return {
        "fetched": len(raw_articles),
        "stored": stored_count,
        "skipped_duplicates": skipped_count,
    }


@app.post("/run-pipeline")
def trigger_pipeline():
    """
    Manually trigger the full fetch -> categorize -> sentiment -> store pipeline.
    """
    summary = run_pipeline()
    return summary


@app.get("/news")
def get_all_news():
    """Get All News"""
    return database.get_all_news()


@app.get("/news/{news_id}")
def get_news_by_id(news_id: int):
    """Get News By ID"""
    article = database.get_news_by_id(news_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/news/sentiment/{label}")
def get_news_by_sentiment(label: str):
    """
    Get News By Sentiment

    Example:
        GET /news/sentiment/positive
        GET /news/sentiment/negative
        GET /news/sentiment/neutral
    """
    valid_labels = {"positive", "negative", "neutral"}
    if label.lower() not in valid_labels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sentiment label. Must be one of {sorted(valid_labels)}",
        )
    return database.get_news_by_sentiment(label.lower())


@app.get("/news/category/{category}")
def get_news_by_category(category: str):
    """
    Get News By Category

    Example:
        GET /news/category/Entertainment
    """
    return database.get_news_by_category(category)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
