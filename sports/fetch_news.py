"""
fetch_news.py
Module: Sports
Compatible with: Python 3.12.10 / 3.14.6

Responsibilities:
- Read RSS feeds
- Extract article information
- Return structured article data
"""

import logging
from datetime import datetime, timezone

import feedparser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fetch_news")

# RSS feeds for the Sports category.
# Only this list changes between category modules (e.g. politics, health, technology).
RSS_FEEDS = [
    "https://www.espn.com/espn/rss/news",
    "https://feeds.bbci.co.uk/sport/rss.xml",
    "https://www.skysports.com/rss/12040",
    
]


def _extract_content(entry) -> str:
    """Pull the best available body text out of a feedparser entry."""
    if entry.get("content"):
        return entry["content"][0].get("value", "").strip()
    return entry.get("summary", "").strip()


def fetch_articles() -> list[dict]:
    """
    Fetch and parse articles from all configured Sports RSS feeds.

    Returns:
        list[dict]: Structured article dictionaries with keys:
            title, description, content, source, url, published_date
    """
    logger.info("RSS Fetch Started")
    articles = []

    for feed_url in RSS_FEEDS:
        try:
            parsed_feed = feedparser.parse(feed_url)
        except Exception as exc:
            logger.warning(f"Failed to fetch feed {feed_url}: {exc}")
            continue

        source_name = parsed_feed.feed.get("title", feed_url)

        for entry in parsed_feed.entries:
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()

            if not title or not url:
                continue

            article = {
                "title": title,
                "description": entry.get("summary", "").strip(),
                "content": _extract_content(entry),
                "source": source_name,
                "url": url,
                "published_date": entry.get(
                    "published", datetime.now(timezone.utc).isoformat()
                ),
            }
            articles.append(article)

    logger.info(f"News Retrieved: {len(articles)} articles")
    return articles


if __name__ == "__main__":
    results = fetch_articles()
    for item in results[:3]:
        print(item)
