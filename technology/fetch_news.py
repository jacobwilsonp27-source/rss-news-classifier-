"""
fetch_news.py
-------------
Responsible for reading RSS feeds and extracting structured article data.

Responsibilities (per project standards):
    - Read RSS feeds
    - Extract article information
    - Return structured article data containing:
        title, description, content, source, url, published_date

This file does NOT categorize articles, analyze sentiment, or touch the
database. It only knows how to turn raw RSS feed XML into clean Python
dictionaries that the rest of the pipeline can use.
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import feedparser

logger = logging.getLogger("technology_module.fetch_news")

# Technology-focused RSS feeds.
# Each entry has a friendly "source" name used to label every article
# pulled from it, since the raw feed metadata doesn't always include a
# clean publisher name.
TECHNOLOGY_RSS_FEEDS = [
    {"url": "https://feeds.arstechnica.com/arstechnica/index", "source": "Ars Technica"},
    {"url": "https://www.theverge.com/rss/index.xml", "source": "The Verge"},
    {"url": "https://techcrunch.com/feed/", "source": "TechCrunch"},
    {"url": "https://www.wired.com/feed/rss", "source": "Wired"},
]


def _clean_text(raw_html: str) -> str:
    """
    feedparser sometimes returns description/content fields containing
    raw HTML tags (e.g. <p>, <a href="...">). We strip tags with a small
    regex-based cleaner so the AI models receive plain text - they
    classify and score sentiment far more reliably without markup noise.
    """
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_content(entry) -> str:
    """
    Different RSS feeds put the 'full' article text in different fields.
    Some provide entry.content, most only provide entry.summary. We try
    the richest field first and fall back gracefully so we never crash
    on a feed with a slightly different structure.
    """
    if hasattr(entry, "content") and entry.content:
        return _clean_text(entry.content[0].value)
    if hasattr(entry, "summary"):
        return _clean_text(entry.summary)
    return ""


def _extract_published_date(entry) -> str:
    """
    Normalizes the published date to ISO 8601 (YYYY-MM-DDTHH:MM:SS) when
    feedparser successfully parsed it into a time struct, otherwise falls
    back to whatever raw string the feed provided.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6]).isoformat()
    return getattr(entry, "published", "")


def fetch_articles(
    feeds: Optional[List[Dict[str, str]]] = None, limit_per_feed: int = 10
) -> List[Dict[str, Any]]:
    """
    Fetches and parses every feed in `feeds` (defaults to
    TECHNOLOGY_RSS_FEEDS), returning a flat list of article dicts:

        {
            "title": str,
            "description": str,
            "content": str,
            "source": str,
            "url": str,
            "published_date": str
        }

    `limit_per_feed` caps how many articles are pulled from each feed,
    so a single very active feed can't flood the database during testing.
    """
    if feeds is None:
        feeds = TECHNOLOGY_RSS_FEEDS

    all_articles: List[Dict[str, Any]] = []
    logger.info("RSS Fetch Started")

    for feed in feeds:
        parsed = feedparser.parse(feed["url"])

        if parsed.bozo:
            # `bozo` is feedparser's flag meaning "this feed had a parsing
            # problem". We log a warning and keep going instead of crashing,
            # since one broken feed shouldn't take down the whole module.
            logger.warning(f"Feed may be malformed: {feed['url']} ({parsed.bozo_exception})")

        entries = parsed.entries[:limit_per_feed]

        for entry in entries:
            article = {
                "title": _clean_text(getattr(entry, "title", "")),
                "description": _clean_text(getattr(entry, "summary", "")),
                "content": _extract_content(entry),
                "source": feed["source"],
                "url": getattr(entry, "link", ""),
                "published_date": _extract_published_date(entry),
            }
            # Skip anything missing a URL or title - we can't de-duplicate
            # or display it usefully without those.
            if article["url"] and article["title"]:
                all_articles.append(article)

    logger.info(f"News Retrieved: {len(all_articles)} articles")
    return all_articles


if __name__ == "__main__":
    # Independent test block - lets you verify fetch_news.py works
    # correctly by running `python fetch_news.py` directly, with no
    # AI models, database, or FastAPI involved yet.
    logging.basicConfig(level=logging.INFO)

    articles = fetch_articles(limit_per_feed=3)
    print(f"\nFetched {len(articles)} articles.\n")

    for a in articles[:5]:
        print("-" * 60)
        print("Title :", a["title"])
        print("Source:", a["source"])
        print("URL   :", a["url"])
        print("Date  :", a["published_date"])
        print("Desc  :", a["description"][:120], "...")
