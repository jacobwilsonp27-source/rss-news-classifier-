"""
fetch_news.py

Category: International / World

Responsibility (per project standards document):
    - Read RSS feeds
    - Extract article information
    - Return structured article data

Extracted fields (exactly as specified in the standards document):
    - title
    - description
    - content
    - source
    - url
    - published_date

No keyword-based logic of any kind is used in this file. This module only
fetches and extracts raw article data; categorization and sentiment analysis
are handled exclusively by categorize.py and sentiment.py using the
approved Hugging Face transformer models.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import feedparser

# ---------------------------------------------------------------------------
# Logging Configuration
# (Standard required by the document: "RSS Fetch Started", "News Retrieved")
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fetch_news")

# ---------------------------------------------------------------------------
# RSS Feed Sources — International / World News
# ---------------------------------------------------------------------------
RSS_FEEDS = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters World": "http://feeds.reuters.com/Reuters/worldNews",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "The Guardian World": "https://www.theguardian.com/world/rss",
    "NPR World": "https://feeds.npr.org/1004/rss.xml",
}


def fetch_rss_feed(feed_url: str, source_name: str) -> Optional[feedparser.FeedParserDict]:
    """
    Fetch and parse a single RSS feed.

    Args:
        feed_url: URL of the RSS feed.
        source_name: Human readable name of the source.

    Returns:
        Parsed feedparser object, or None if the feed could not be fetched
        or parsed.
    """
    try:
        logger.info(f"RSS Fetch Started - Source: {source_name} - URL: {feed_url}")
        parsed_feed = feedparser.parse(feed_url)

        # feedparser sets bozo=1 when the feed is malformed or unreachable.
        if parsed_feed.bozo:
            logger.error(
                f"Feed parsing issue for {source_name}. "
                f"Reason: {parsed_feed.bozo_exception}"
            )
            # Some feeds set bozo=1 but still return usable entries.
            # Only treat it as a hard failure if there are no entries at all.
            if not parsed_feed.entries:
                return None

        if not parsed_feed.entries:
            logger.warning(f"No entries found in feed from {source_name}")
            return None

        return parsed_feed

    except Exception as e:
        logger.error(f"Unexpected error while fetching feed from {source_name}: {e}")
        return None


def extract_article_data(entry, source_name: str) -> Dict:
    """
    Extract the standard fields required by the project standards document
    from a single RSS feed entry.

    Returns:
        Dictionary containing: title, description, content, source, url,
        published_date
    """
    title = entry.get("title", "").strip()
    description = entry.get("summary", "").strip()

    # Some feeds provide full article content under 'content',
    # others only provide a summary.
    if entry.get("content"):
        content = entry["content"][0].get("value", "").strip()
    else:
        content = description

    url = entry.get("link", "").strip()

    # Normalize published date to ISO format where possible.
    if entry.get("published_parsed"):
        try:
            published_date = datetime(*entry["published_parsed"][:6]).isoformat()
        except (TypeError, ValueError):
            published_date = entry.get("published", "")
    else:
        published_date = entry.get("published", "")

    article = {
        "title": title,
        "description": description,
        "content": content,
        "source": source_name,
        "url": url,
        "published_date": published_date,
    }

    return article


def fetch_all_news() -> List[Dict]:
    """
    Fetch and extract articles from all configured International / World
    RSS feeds.

    Returns:
        List of article dictionaries in the structure expected by the
        rest of the pipeline (categorize.py, sentiment.py, database.py).
    """
    all_articles: List[Dict] = []

    for source_name, feed_url in RSS_FEEDS.items():
        parsed_feed = fetch_rss_feed(feed_url, source_name)

        if parsed_feed is None:
            # Failure already logged inside fetch_rss_feed; skip this source
            # so one broken feed does not stop the rest of the pipeline.
            continue

        retrieved_count = 0
        for entry in parsed_feed.entries:
            try:
                article = extract_article_data(entry, source_name)

                # A URL is required for later duplicate-checking in
                # database.py, so skip articles without one.
                if not article["url"]:
                    logger.warning(f"Skipped article with missing URL from {source_name}")
                    continue

                all_articles.append(article)
                retrieved_count += 1

            except Exception as e:
                logger.error(f"Failed to extract article data from {source_name}: {e}")
                continue

        logger.info(f"News Retrieved - Source: {source_name} - Articles: {retrieved_count}")

    logger.info(f"News Retrieved - Total Articles Across All Sources: {len(all_articles)}")
    return all_articles


if __name__ == "__main__":
    articles = fetch_all_news()
    print(f"Fetched {len(articles)} International / World news articles.")