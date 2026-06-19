"""
fetch_news.py
-------------
Responsibility:
  - Read RSS feeds (Times of India, The Hindu, NDTV, BBC, etc.)
  - Extract article information
  - Return structured article data

Extracts: title, description, content, source, url, published_date
"""

import logging
import feedparser
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Education RSS Feeds ───────────────────────────────────────────────────────
EDUCATION_RSS_FEEDS: list[dict[str, str]] = [
    {
        "source": "Times of India - Education",
        "url": "https://timesofindia.indiatimes.com/rssfeeds/913168846.cms",
    },
    {
        "source": "The Hindu - Education",
        "url": "https://www.thehindu.com/education/feeder/default.rss",
    },
   
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(entry: feedparser.FeedParserDict) -> str:
    """Convert feedparser time struct to ISO-8601 string; fallback to now."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6]).isoformat()
        except Exception:
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6]).isoformat()
        except Exception:
            pass
    return datetime.utcnow().isoformat()


def _clean_html(text: str) -> str:
    """Strip basic HTML tags for cleaner text storage."""
    import re
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _fetch_single_feed(feed_info: dict[str, str]) -> list[dict]:
    """Fetch and parse one RSS feed; return list of article dicts."""
    source = feed_info["source"]
    url    = feed_info["url"]
    articles: list[dict] = []

    logger.info("RSS Fetch Started | source=%s", source)

    try:
        parsed = feedparser.parse(url)

        if parsed.bozo:
            logger.warning("Feed may be malformed | source=%s | reason=%s",
                           source, parsed.bozo_exception)

        for entry in parsed.entries:
            title       = _clean_html(getattr(entry, "title",   "") or "")
            description = _clean_html(getattr(entry, "summary", "") or "")
            # 'content' field (Atom) preferred over summary
            content_list = getattr(entry, "content", [])
            content = _clean_html(
                content_list[0].get("value", "") if content_list else description
            )
            link  = getattr(entry, "link",  "") or ""
            pub   = _parse_date(entry)

            if not title or not link:
                continue                         # skip malformed entries

            articles.append({
                "title":          title,
                "description":    description,
                "content":        content,
                "source":         source,
                "url":            link,
                "published_date": pub,
            })

        logger.info("News Retrieved | source=%s | count=%d", source, len(articles))

    except Exception as exc:
        logger.error("Fetch failed | source=%s | error=%s", source, exc)

    return articles


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_all_news(max_workers: int = 6) -> list[dict]:
    """
    Fetch all RSS feeds concurrently.

    Parameters
    ----------
    max_workers : int
        Thread-pool size (default 6 – one per feed group).

    Returns
    -------
    list[dict]
        Deduplicated list of article dicts ready for categorisation.
    """
    all_articles: list[dict] = []
    seen_urls: set[str]      = set()

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_fetch_single_feed, feed): feed["source"]
            for feed in EDUCATION_RSS_FEEDS
        }
        for future in as_completed(futures):
            for article in future.result():
                if article["url"] not in seen_urls:
                    seen_urls.add(article["url"])
                    all_articles.append(article)

    logger.info("Total unique articles fetched: %d", len(all_articles))
    return all_articles


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    news = fetch_all_news()
    for n in news[:3]:
        print(n)
