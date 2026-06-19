"""
fetch_news.py - Entertainment Module

Responsibilities (per project standards):
    - Read RSS feeds
    - Extract article information
    - Return structured article data

Extracted fields:
    - title
    - description
    - content
    - source
    - url
    - published_date
"""

import logging
from datetime import datetime, timezone

import feedparser
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fetch_news")

# Entertainment-focused RSS feeds.
# This is the only part of fetch_news.py that differs between category modules.
RSS_FEEDS = [
    
    "https://variety.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://www.rollingstone.com/feed/",
    "https://deadline.com/feed/",
    "https://www.billboard.com/feed/",
    "https://www.nme.com/feed",
    "https://www.empireonline.com/movies/feed/",
    "https://www.tvinsider.com/feed/",
    "https://www.polygon.com/rss/index.xml",
    "https://www.ign.com/rss",
    "https://www.thewrap.com/feed/",
    "https://screenrant.com/feed/",
    "https://comicbook.com/feed/",
    "https://movieweb.com/rss/all.xml",
    "https://www.cbr.com/feed/",
    "https://www.digitalspy.com/rss/",
    "https://www.denofgeek.com/feed/",
    "https://www.gamespot.com/feeds/mashup/"
]



def _safe_get(entry, field, default=""):
    """Return entry.get(field, default) but always coerce to str."""
    value = entry.get(field, default)
    if value is None:
        return default
    return str(value)


def _extract_content(entry):
    """
    feedparser entries store full content differently across feeds.
    Try 'content' first, then fall back to 'summary'/'description'.
    """
    if "content" in entry and entry["content"]:
        try:
            return entry["content"][0].get("value", "")
        except (IndexError, AttributeError, KeyError):
            pass
    return _safe_get(entry, "summary", _safe_get(entry, "description", ""))


def _extract_published_date(entry):
    """
    Normalize published date to ISO 8601 string.
    Falls back to current UTC time if not present/parseable.
    """
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        try:
            dt = datetime(*parsed[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc).isoformat()

def clean_html(text: str) -> str:
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text

def fetch_from_feed(feed_url: str) -> list[dict]:
    """
    Fetch and parse a single RSS feed.

    Returns a list of structured article dicts (raw, pre-categorization,
    pre-sentiment). Fields not yet known (category, sentiment, id) are
    left for downstream modules to populate.
    """
    logger.info("RSS Fetch Started: %s", feed_url)
    articles = []

    parsed_feed = feedparser.parse(feed_url)
    
    if parsed_feed.bozo:
        logger.warning("Feed may be malformed: %s (%s)", feed_url, parsed_feed.bozo_exception)

    for entry in parsed_feed.entries:
        article = {
            "title": clean_html(_safe_get(entry, "title")),
            "description": clean_html(_safe_get(entry, "summary"))[:300],
            "content": clean_html(_extract_content(entry)),
            "source": _safe_get(parsed_feed.feed, "title", feed_url),
            "url": _safe_get(entry, "link"),
            "published_date": _extract_published_date(entry),
        }
        articles.append(article)

    logger.info("News Retrieved: %d articles from %s", len(articles), feed_url)
    return articles


def fetch_all_news() -> list[dict]:
    """
    Fetch articles from every configured RSS feed for this category module.
    """
    all_articles = []
    for feed_url in RSS_FEEDS:
        try:
            all_articles.extend(fetch_from_feed(feed_url))
        except Exception as exc:  # noqa: BLE001 - log and continue with other feeds
            logger.error("Failed to fetch feed %s: %s", feed_url, exc)
    return all_articles


if __name__ == "__main__":
    results = fetch_all_news()
    print(f"Fetched {len(results)} total articles.")
    for item in results[:3]:
        print(item)
    
