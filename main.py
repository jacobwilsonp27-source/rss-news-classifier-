"""
main.py  –  Combined News API
==============================
Place this file at the ROOT of your project, one level above all
11 teammate module folders (politics/, business/, health/, …).

It reads each module's news.db directly — no need to run the
individual FastAPI apps at all. Just run:

    uvicorn main:app --reload --port 8000

The frontend connects to http://localhost:8000 only.

IMPORTANT – Adjust the folder names in MODULE_DATABASES below if
any teammate named their folder differently (e.g. "business_economy"
instead of "business").
"""

import os
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI-Powered News API – Combined")

# Allow the frontend (any origin) to fetch from this server.
# Tighten allow_origins to your frontend URL in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rss-news-classifier-eu88.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────
#  Map each category's API label → relative path to its news.db
#  Adjust folder names to match your actual teammate folder names.
# ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODULE_DATABASES = {
    "Politics":             os.path.join(BASE_DIR, "politics",      "news.db"),
    "Business and Economy": os.path.join(BASE_DIR, "business",      "news.db"),
    "Technology":           os.path.join(BASE_DIR, "technology",    "news.db"),
    "Science":              os.path.join(BASE_DIR, "science",       "news.db"),
    "Health":               os.path.join(BASE_DIR, "health",        "news.db"),
    "Sports":               os.path.join(BASE_DIR, "sports",        "news.db"),
    "Entertainment":        os.path.join(BASE_DIR, "entertainment", "news.db"),
    "Lifestyle":            os.path.join(BASE_DIR, "lifestyle",     "news.db"),
    "International":        os.path.join(BASE_DIR, "international", "news.db"),
    "Education":            os.path.join(BASE_DIR, "education",     "news.db"),
    "Weather":              os.path.join(BASE_DIR, "weather",       "news.db"),
}


def query_db(db_path: str, sql: str, params: tuple = ()) -> List[dict]:
    """Run a SELECT on one module's database. Returns [] if DB is missing."""
    if not os.path.exists(db_path):
        return []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as exc:
        print(f"[DB Error] {db_path}: {exc}")
        return []


def resolve_db(label: str, path: str) -> str:
    """Resolve the actual DB path for a module, including legacy alternates."""
    if os.path.exists(path):
        return path
    if label == "Weather":
        alt_path = os.path.join(BASE_DIR, "weather", "weather_news.db")
        if os.path.exists(alt_path):
            return alt_path
        root_alt_path = os.path.join(BASE_DIR, "weather_news.db")
        if os.path.exists(root_alt_path):
            return root_alt_path
    return path


def find_db(category: str) -> Optional[str]:
    """Case-insensitive lookup of a category's DB path."""
    for label, path in MODULE_DATABASES.items():
        if label.lower() == category.lower():
            resolved = resolve_db(label, path)
            return resolved if os.path.exists(resolved) else None
    return None


# ─────────────────────────────────────────────────────────────────────
#  Endpoints
# ─────────────────────────────────────────────────────────────────────

@app.get("/news")
def get_all_news(limit: int = 200):
    """Return latest news from all 11 categories, merged and date-sorted."""
    all_articles: List[dict] = []
    for label, db_path in MODULE_DATABASES.items():
        resolved_path = resolve_db(label, db_path)
        rows = query_db(
            resolved_path,
            "SELECT * FROM news ORDER BY published_date DESC LIMIT ?",
            (limit,),
        )
        all_articles.extend(rows)
    all_articles.sort(key=lambda x: x.get("published_date", ""), reverse=True)
    return all_articles[:limit]


@app.get("/news/search")
def search_news(q: str = Query(..., min_length=1), limit: int = 100):
    """
    Full-text search across title, description, and content
    from all 11 databases.

    Example: GET /news/search?q=brazil+vs+morocco
    """
    results: List[dict] = []
    pattern = f"%{q}%"
    for label, db_path in MODULE_DATABASES.items():
        resolved_path = resolve_db(label, db_path)
        rows = query_db(
            resolved_path,
            """SELECT * FROM news
               WHERE title LIKE ? OR description LIKE ? OR content LIKE ?
               ORDER BY published_date DESC LIMIT ?""",
            (pattern, pattern, pattern, limit),
        )
        results.extend(rows)
    results.sort(key=lambda x: x.get("published_date", ""), reverse=True)
    return results[:limit]


@app.get("/news/category/{category}")
def get_by_category(category: str, limit: int = 100):
    """
    Return all news for one category.
    Example: GET /news/category/Health
             GET /news/category/Business%20and%20Economy
    """
    db_path = find_db(category)
    if db_path is None:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found.")
    return query_db(
        db_path,
        "SELECT * FROM news ORDER BY published_date DESC LIMIT ?",
        (limit,),
    )


@app.get("/news/{category}/{article_id}")
def get_article(category: str, article_id: int):
    """
    Return a single article by category + id.
    IDs are only unique within each module's own database,
    so both parameters are required.
    Example: GET /news/Health/3
    """
    db_path = find_db(category)
    if db_path is None:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found.")
    rows = query_db(
        db_path,
        "SELECT * FROM news WHERE id = ? LIMIT 1",
        (article_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found in {category}.")
    return rows[0]
