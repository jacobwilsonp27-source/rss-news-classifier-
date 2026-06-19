"""
app.py
------
Responsibility:
  - Create FastAPI server
  - Expose the four mandatory API endpoints
  - Connect fetch → categorise → sentiment → database pipeline
  - Trigger the pipeline via a /refresh endpoint

Run:
    uvicorn app:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse

import database
import fetch_news
import categorize
import sentiment

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Startup / shutdown ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise DB and log API start on startup."""
    database.init_db()
    if not database.get_all_news():
        logger.info("Education DB empty, running initial pipeline to populate news.")
        stats = _run_pipeline()
        logger.info(
            "Initial pipeline complete | fetched=%d | saved=%d | skipped=%d",
            stats["fetched"], stats["saved"], stats["skipped"],
        )
    logger.info("API Started | Education News Module is live.")
    yield


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Education News API",
    description=(
        "AI-Powered News Categorization Platform – Education Module.\n\n"
        "Models used:\n"
        "- **Categorisation**: facebook/bart-large-mnli\n"
        "- **Sentiment**: cardiffnlp/twitter-roberta-base-sentiment-latest"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── Pipeline helper ───────────────────────────────────────────────────────────
def _run_pipeline() -> dict[str, int]:
    """
    Full pipeline:  Fetch → Categorise → Sentiment → Store
    Returns summary counts.
    """
    logger.info("Pipeline started.")

    # Step 1 – Fetch
    articles = fetch_news.fetch_all_news()
    if not articles:
        logger.warning("No articles fetched.")
        return {"fetched": 0, "saved": 0, "skipped": 0}

    # Filter out URLs already in DB (avoid re-running AI on duplicates)
    new_articles = [a for a in articles if not database.url_exists(a["url"])]
    logger.info("New articles (not in DB): %d", len(new_articles))

    if not new_articles:
        return {"fetched": len(articles), "saved": 0, "skipped": len(articles)}

    # Step 2 – Categorise
    categorize.categorize_batch(new_articles)

    # Step 3 – Sentiment
    sentiment.analyze_batch(new_articles)

    # Step 4 – Store
    stats = database.save_articles(new_articles)

    return {
        "fetched":  len(articles),
        "saved":    stats["saved"],
        "skipped":  len(articles) - len(new_articles) + stats["skipped"],
    }


# ── Standard JSON response builder ───────────────────────────────────────────
def _article_response(row: dict) -> dict:
    """Map a DB row to the mandatory JSON format from the PDF."""
    return {
        "id":                   row.get("id"),
        "title":                row.get("title",                ""),
        "description":          row.get("description",          ""),
        "content":              row.get("content",              ""),
        "source":               row.get("source",               ""),
        "url":                  row.get("url",                  ""),
        "category":             row.get("category",             ""),
        "category_confidence":  row.get("category_confidence",  0.0),
        "sentiment":            row.get("sentiment",            ""),
        "sentiment_confidence": row.get("sentiment_confidence", 0.0),
        "published_date":       row.get("published_date",       ""),
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

# POST /refresh  – trigger pipeline (can be called manually or by a scheduler)
@app.post("/refresh", summary="Fetch, classify, and store latest education news")
def refresh_news(background_tasks: BackgroundTasks):
    """
    Trigger the full pipeline in the background:
    RSS Fetch → Categorise (BART) → Sentiment (RoBERTa) → SQLite.
    """
    background_tasks.add_task(_run_pipeline)
    return {"message": "Pipeline triggered. Check logs for progress."}


# POST /refresh/sync  – synchronous version (useful for testing)
@app.post("/refresh/sync", summary="Synchronous pipeline run (for testing)")
def refresh_news_sync():
    stats = _run_pipeline()
    return {"message": "Pipeline complete.", "stats": stats}


# GET /news
@app.get("/news", summary="Get all news articles")
def get_all_news(
    limit:  int = Query(default=50, ge=1, le=500, description="Max results"),
    offset: int = Query(default=0,  ge=0,         description="Pagination offset"),
):
    rows = database.get_all_news(limit=limit, offset=offset)
    return [_article_response(r) for r in rows]


# GET /news/{id}
@app.get("/news/{news_id}", summary="Get news article by ID")
def get_news_by_id(news_id: int):
    row = database.get_news_by_id(news_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Article {news_id} not found.")
    return _article_response(row)


# GET /news/sentiment/{label}
@app.get("/news/sentiment/{label}", summary="Get news by sentiment label")
def get_news_by_sentiment(label: str):
    """
    Valid labels: positive | negative | neutral
    Example: GET /news/sentiment/positive
    """
    valid = {"positive", "negative", "neutral"}
    if label.lower() not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid label '{label}'. Choose from: {sorted(valid)}",
        )
    rows = database.get_news_by_sentiment(label)
    return [_article_response(r) for r in rows]


# GET /news/category/{category}
@app.get("/news/category/{category}", summary="Get news by category")
def get_news_by_category(category: str):
    """
    Valid categories: Education, Technology, Science, Health, Sports, …
    Example: GET /news/category/Education
    """
    rows = database.get_news_by_category(category)
    return [_article_response(r) for r in rows]


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "module": "Education News"}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
