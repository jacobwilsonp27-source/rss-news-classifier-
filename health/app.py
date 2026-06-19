"""
app.py

Category: Health

Responsibility (per project standards document):
    - Create FastAPI server
    - Expose API endpoints
    - Connect all project components
"""

import logging
import threading

from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import database
from fetch_news import fetch_all_news
from categorize import categorize_article
from sentiment import analyze_sentiment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("app")

app = FastAPI(title="Health News Module")
scheduler = BackgroundScheduler()

# Only accept predicted Health category above this confidence
CONFIDENCE_THRESHOLD = 0.2

# No keyword fallback — rely on model prediction + confidence only


def run_pipeline() -> None:
    articles = fetch_all_news()

    for article in articles:
        text_for_analysis = f"{article.get('title', '')}. {article.get('description', '')}"

        category_result = categorize_article(text_for_analysis)
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

        # Enforce Health-only storage: accept only when predicted category is
        # exactly "Health" and classifier confidence meets the threshold.
        predicted = category_result.get("category", "")
        confidence = category_result.get("confidence", 0.0)

        if predicted == "Health" and confidence >= CONFIDENCE_THRESHOLD:
            database.insert_article(processed_article)
        else:
            logger.info(
                f"Skipped non-Health article - Title: {processed_article['title']} - "
                f"Predicted: {predicted} - Confidence: {confidence}"
            )


@app.on_event("startup")
def startup_event():
    logger.info("API Started")
    database.init_db()
    # Run pipeline immediately on startup
    threading.Thread(target=run_pipeline, daemon=True).start()
    # Schedule pipeline to run every second
    scheduler.add_job(
        run_pipeline,
        IntervalTrigger(seconds=1),
        id="fetch_news_job",
        name="Fetch News Pipeline",
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()
        logger.info("News fetching scheduler started - runs every 2 hours")


@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("News fetching scheduler stopped")


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


@app.post("/admin/run_pipeline")
def admin_run_pipeline():
    """Admin: trigger pipeline run (returns immediately)."""
    threading.Thread(target=run_pipeline, daemon=True).start()
    return {"started": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)