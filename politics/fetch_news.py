import feedparser
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Politics-specific RSS Feeds
POLITICS_RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/politics/rss.xml",           # BBC Politics
    "https://feeds.reuters.com/Reuters/PoliticsNews",           # Reuters Politics
    "https://www.aljazeera.com/xml/rss/all.xml",               # Al Jazeera
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml", # NYT Politics
    "https://feeds.washingtonpost.com/rss/politics",            # Washington Post Politics
    "https://www.theguardian.com/politics/rss",                 # The Guardian Politics
    "https://feeds.feedburner.com/ndtvnews-india-news",         # NDTV India News
    "https://timesofindia.indiatimes.com/rssfeeds/1221656.cms", # Times of India Politics
    "https://www.thehindu.com/news/national/feeder/default.rss",# The Hindu National
    "https://indianexpress.com/section/political-pulse/feed/",  # Indian Express Politics
]

def fetch_news():
    """
    Fetch news articles from all politics RSS feeds.
    Returns a list of structured article dictionaries.
    """
    logger.info("RSS Fetch Started")
    all_articles = []

    for feed_url in POLITICS_RSS_FEEDS:
        try:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                title       = entry.get("title", "").strip()
                description = entry.get("summary", "").strip()
                content     = ""

                # Try to extract full content if available
                if hasattr(entry, "content") and entry.content:
                    content = entry.content[0].get("value", "").strip()
                if not content:
                    content = description

                source = feed.feed.get("title", feed_url).strip()
                url    = entry.get("link", "").strip()

                # Parse published date
                published_date = ""
                if entry.get("published_parsed"):
                    try:
                        published_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        published_date = entry.get("published", "")
                else:
                    published_date = entry.get("published", "")

                # Skip entries with missing critical fields
                if not title or not url:
                    continue

                article = {
                    "title"         : title,
                    "description"   : description,
                    "content"       : content,
                    "source"        : source,
                    "url"           : url,
                    "published_date": published_date,
                }
                all_articles.append(article)

        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")

    logger.info(f"News Retrieved - Total articles fetched: {len(all_articles)}")
    return all_articles
