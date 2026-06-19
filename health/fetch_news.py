"""
fetch_news.py

Category: Health

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
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import feedparser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fetch_news")

# RSS Feed Sources — Health News
RSS_FEEDS = {
    "BBC Health": "http://feeds.bbci.co.uk/news/health/rss.xml",
    "Reuters Health": "http://feeds.reuters.com/reuters/healthNews",
    "Medical News Today": "https://www.medicalnewstoday.com/rss",
    "NPR Health": "https://feeds.npr.org/1128/rss.xml",
    "WebMD Health News": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
}


def fetch_rss_feed(feed_url: str, source_name: str) -> Optional[feedparser.FeedParserDict]:
    try:
        logger.info(f"RSS Fetch Started - Source: {source_name} - URL: {feed_url}")
        parsed_feed = feedparser.parse(feed_url)

        if parsed_feed.bozo:
            logger.error(
                f"Feed parsing issue for {source_name}. "
                f"Reason: {parsed_feed.bozo_exception}"
            )
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
    title = entry.get("title", "").strip()
    description = entry.get("summary", "").strip()

    if entry.get("content"):
        content = entry["content"][0].get("value", "").strip()
    else:
        content = description

    url = entry.get("link", "").strip()

    if entry.get("published_parsed"):
        try:
            published_date = datetime(*entry["published_parsed"][:6]).isoformat()
        except (TypeError, ValueError):
            published_date = entry.get("published", "")
    else:
        published_date = entry.get("published", "")

    return {
        "title": title,
        "description": description,
        "content": content,
        "source": source_name,
        "url": url,
        "published_date": published_date,
    }


def fetch_all_news() -> List[Dict]:
    all_articles: List[Dict] = []

    for source_name, feed_url in RSS_FEEDS.items():
        parsed_feed = fetch_rss_feed(feed_url, source_name)

        if parsed_feed is None:
            continue

        retrieved_count = 0
        for entry in parsed_feed.entries:
            try:
                article = extract_article_data(entry, source_name)

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
    print(f"Fetched {len(articles)} Health news articles.")