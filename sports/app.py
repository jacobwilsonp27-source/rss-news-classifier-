"""
app.py
"""

import importlib
import logging

try:
    fastapi = importlib.import_module("fastapi")
    FastAPI = fastapi.FastAPI
    HTTPException = fastapi.HTTPException
except Exception:

    class HTTPException(Exception):
        def __init__(self, status_code: int = 500, detail: str | None = None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class FastAPI:
        def __init__(self, *args, **kwargs):
            pass

        def on_event(self, name):
            def decorator(fn):
                return fn
            return decorator

        def post(self, path: str):
            def decorator(fn):
                return fn
            return decorator

        def get(self, path: str):
            def decorator(fn):
                return fn
            return decorator


import database
from categorize import categorize_article
from fetch_news import fetch_articles
from sentiment import analyze_sentiment


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("app")

app = FastAPI(title="Sports News")

database.init_db()


def process_and_store_news() -> int:
    articles = fetch_articles()
    saved_count = 0

    for article in articles:

        text_for_ai = (
            f"{article.get('title', '')}. "
            f"{article.get('description', '')}"
        ).strip()

        try:
            category_result = categorize_article(text_for_ai)

            # ONLY SPORTS NEWS
            if category_result["category"] != "Sports":
                logger.info(
                    f"Skipped: {article['title'][:60]} "
                    f"| Category={category_result['category']}"
                )
                continue

            sentiment_result = analyze_sentiment(text_for_ai)

            article["category"] = "Sports"
            article["category_confidence"] = category_result["confidence"]

            article["sentiment"] = sentiment_result["sentiment"]
            article["sentiment_confidence"] = sentiment_result["confidence"]

            success = database.insert_article(article)

            if success:
                saved_count += 1
                logger.info(
                    f"Saved: {article['title'][:60]}"
                )

        except Exception as e:
            logger.error(
                f"Error processing article: {e}"
            )

    logger.info(f"Total Saved: {saved_count}")

    return saved_count


@app.on_event("startup")
def on_startup():
    logger.info("API Started")


@app.post("/fetch")
def trigger_fetch():
    saved_count = process_and_store_news()

    return {
        "message": "Pipeline executed",
        "new_articles_saved": saved_count
    }


@app.get("/news")
def get_all_news():
    return database.get_all_news()


@app.get("/news/{news_id}")
def get_news_by_id(news_id: int):
    article = database.get_news_by_id(news_id)

    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found"
        )

    return article


@app.get("/news/sentiment/{label}")
def get_news_by_sentiment(label: str):
    return database.get_news_by_sentiment(label)


@app.get("/news/category/{category}")
def get_news_by_category(category: str):
    return database.get_news_by_category(category)