import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fetch_news    import fetch_news
from categorize    import categorize_article
from sentiment     import analyze_sentiment
from database      import (
    create_table,
    save_article,
    get_all_articles,
    get_article_by_id,
    get_articles_by_sentiment,
    get_articles_by_category,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ── Lifespan: runs on startup ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Started - Weather News Intelligence Module")
    create_table()
    yield


app = FastAPI(
    title       = "Weather News Intelligence API",
    description = "AI-Powered News Categorization Platform — Weather Module (RSS + NewsAPI)",
    version     = "1.0.0",
    lifespan    = lifespan,
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper: run the full pipeline for one article ─────────────────────────────
def process_and_store(article: dict) -> bool:
    """
    Run categorization + sentiment analysis on a raw article,
    then store in the database.
    """
    text = f"{article['title']}. {article['description']}"

    cat_result  = categorize_article(text)
    sent_result = analyze_sentiment(text)

    processed = {
        "title"               : article["title"],
        "description"         : article["description"],
        "content"             : article["content"],
        "source"              : article["source"],
        "url"                 : article["url"],
        "published_date"      : article["published_date"],
        "category"            : cat_result["category"],
        "category_confidence" : cat_result["confidence"],
        "sentiment"           : sent_result["sentiment"],
        "sentiment_confidence": sent_result["confidence"],
    }

    return save_article(processed)


# ── Trigger pipeline manually ─────────────────────────────────────────────────
@app.post("/fetch", summary="Fetch and process latest weather news")
def fetch_and_process():
    """
    Triggers the full pipeline:
    RSS Fetch + NewsAPI Fetch → Categorize → Sentiment → Store in DB
    Returns a summary of what was fetched and saved.
    """
    articles = fetch_news()
    saved = 0
    skipped = 0
    processed_list = []

    for article in articles:
        result = process_and_store(article)
        if result:
            saved += 1
            processed_list.append({
                "title"    : article["title"],
                "source"   : article["source"],
                "status"   : "saved"
            })
        else:
            skipped += 1

    logger.info(f"Pipeline complete. {saved}/{len(articles)} new articles saved.")

    return {
        "status"          : "success",
        "total_fetched"   : len(articles),
        "saved"           : saved,
        "skipped_duplicates": skipped,
        "message"         : f"{saved} new articles saved, {skipped} duplicates skipped.",
        "saved_articles"  : processed_list
    }


# ── GET /news ─────────────────────────────────────────────────────────────────
@app.get("/news", summary="Get all Weather news articles")
def get_news():
    """
    Returns only Weather category articles from the database.
    """
    articles = get_articles_by_category("Weather")
    return {"total": len(articles), "articles": articles}


# ── GET /news/{id} ────────────────────────────────────────────────────────────
@app.get("/news/{id}", summary="Get news article by ID")
def get_news_by_id(id: int):
    """
    Returns a single article by its database ID.
    """
    article = get_article_by_id(id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article with id {id} not found")
    return article


# ── GET /news/sentiment/{label} ───────────────────────────────────────────────
@app.get("/news/sentiment/{label}", summary="Get news by sentiment")
def get_news_by_sentiment(label: str):
    """
    Returns all articles matching the given sentiment label.
    Accepted values: positive | negative | neutral
    """
    valid = ["positive", "negative", "neutral"]
    if label.lower() not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sentiment label '{label}'. Choose from: {valid}"
        )
    articles = get_articles_by_sentiment(label)
    return {"sentiment": label, "total": len(articles), "articles": articles}


# ── GET /news/category/{category} ────────────────────────────────────────────
@app.get("/news/category/{category}", summary="Get news by category")
def get_news_by_category(category: str):
    """
    This is the Weather module.
    Only returns articles for 'Weather' category.
    All other categories return empty list.
    """
    if category.lower() != "weather":
        return {"category": category, "total": 0, "articles": []}

    articles = get_articles_by_category("Weather")
    return {"category": "Weather", "total": len(articles), "articles": articles}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("API Started")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
