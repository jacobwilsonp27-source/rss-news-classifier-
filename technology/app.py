"""
app.py
------
Creates the FastAPI server for the Technology category module, wires
together fetch_news.py, categorize.py, sentiment.py, and database.py,
and exposes the mandatory API endpoints.

Responsibilities (per project standards):
    - Create FastAPI server
    - Expose API endpoints
    - Connect all project components

Run with:
    uvicorn app:app --reload
"""

import logging

from fastapi import FastAPI, HTTPException

import database
import fetch_news
import categorize
import sentiment

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("technology_module.app")

app = FastAPI(title="Technology News Module", version="1.0.0")


def run_pipeline() -> None:
    """
    Runs the full mandatory pipeline once:

        RSS Feed -> Fetch News -> Categorize -> Sentiment -> Store in DB

    This is what actually populates news.db. It is called automatically
    once when the API server starts (see the startup event below), and
    can also be re-run any time by executing `python app.py` directly.
    """
    database.init_db()
    articles = fetch_news.fetch_articles()

    new_count = 0
    skipped_count = 0

    for article in articles:
        # We feed the model title + description rather than the full
        # content. This keeps classification fast and avoids diluting
        # the signal with long boilerplate text some feeds include.
        text_for_ai = f"{article['title']}. {article['description']}"

        category_result = categorize.categorize_article(text_for_ai)
        sentiment_result = sentiment.analyze_sentiment(text_for_ai)

        record = {
            **article,
            "category": category_result["category"],
            "category_confidence": category_result["confidence"],
            "sentiment": sentiment_result["sentiment"],
            "sentiment_confidence": sentiment_result["confidence"],
        }

        inserted = database.insert_article(record)
        if inserted:
            new_count += 1
        else:
            skipped_count += 1

    logger.info(f"Pipeline complete. New articles: {new_count}, skipped duplicates: {skipped_count}")


@app.on_event("startup")
def on_startup() -> None:
    """
    Runs once when the server starts (e.g. via `uvicorn app:app --reload`).

    Per the project's News Processing Pipeline, every module is expected
    to fetch, categorize, analyze, and store news before serving it via
    the API. Running the pipeline on startup means the database is
    refreshed with the latest RSS articles every time the server boots.
    """
    logger.info("API Started")
    try:
        run_pipeline()
    except Exception as e:
        # A pipeline failure (e.g. no internet connection, a feed is
        # temporarily down) should not prevent the API itself from
        # starting - it should still serve whatever is already saved
        # in news.db, or an empty list on a first-ever run.
        logger.error(f"Pipeline run failed during startup: {e}")


@app.get("/news")
def get_all_news():
    """Returns every article currently stored in the database, newest first."""
    return database.get_all_news()


@app.get("/news/sentiment/{label}")
def get_news_by_sentiment(label: str):
    """Returns all articles matching a sentiment label: positive, negative, or neutral."""
    valid_labels = {"positive", "negative", "neutral"}
    if label.lower() not in valid_labels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sentiment '{label}'. Must be one of {sorted(valid_labels)}.",
        )
    return database.get_news_by_sentiment(label.lower())


@app.get("/news/category/{category}")
def get_news_by_category(category: str):
    """Returns all articles matching a category, e.g. /news/category/Technology"""
    return database.get_news_by_category(category)


@app.get("/news/{news_id}")
def get_news_by_id(news_id: int):
    """Returns a single article by its database ID."""
    article = database.get_news_by_id(news_id)
    if article is None:
        raise HTTPException(status_code=404, detail=f"No article found with id {news_id}")
    return article


if __name__ == "__main__":
    # Lets you run `python app.py` to execute the pipeline once and
    # populate/refresh news.db without starting the web server at all -
    # handy for quick testing.
    run_pipeline()
