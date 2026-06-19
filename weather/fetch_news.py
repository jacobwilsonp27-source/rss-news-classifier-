import feedparser
import logging
import os
import requests
import time
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ── NewsAPI Configuration ──────────────────────────────────────────────────────
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY_HERE")
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# Weather-specific RSS Feeds
WEATHER_RSS_FEEDS = [
    "https://www.theweathernetwork.com/rss/news",
    "https://weather.com/news/rss.xml",
    "https://www.accuweather.com/en/rss/news",
    "https://www.noaa.gov/news/rss.xml",
    "https://www.metoffice.gov.uk/news/releases/rss",
    "https://www.weather.gov/rss_page.php?site_name=nws",
    "https://feeds.feedburner.com/weatherzone",
    "https://www.wunderground.com/news/rss.xml",
    "https://www.climatecentral.org/rss",
    "https://feeds.nationalgeographic.com/ng/News/News_Main.rss",
]

# Weather-related keywords for NewsAPI search
WEATHER_KEYWORDS = [
    "weather forecast",
    "severe weather",
    "hurricane",
    "tornado",
    "flood",
    "drought",
    "heatwave",
    "snowstorm",
    "climate change",
    "meteorology",
]


def fetch_from_newsapi(max_results=20):
    """
    Fetch weather-related articles from NewsAPI using the /everything endpoint.
    Searches for weather keywords from the past 7 days.
    """
    articles = []

    if NEWSAPI_KEY == "YOUR_NEWSAPI_KEY_HERE":
        logger.warning("NewsAPI key not set. Skipping NewsAPI fetch.")
        logger.warning("Set NEWSAPI_KEY environment variable or update fetch_news.py")
        return articles

    # Build query: weather OR forecast OR hurricane OR ...
    query = " OR ".join(WEATHER_KEYWORDS)

    # Calculate date range (last 7 days)
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    url = f"{NEWSAPI_BASE_URL}/everything"
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "sortBy": "publishedAt",
        "pageSize": min(max_results, 100),  # NewsAPI max is 100
        "language": "en",
        "apiKey": NEWSAPI_KEY,
    }

    try:
        logger.info(f"Fetching from NewsAPI: {url}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return articles

        for item in data.get("articles", []):
            title = item.get("title", "").strip()
            description = item.get("description", "").strip()
            content = item.get("content", "").strip()
            url_link = item.get("url", "").strip()
            source = item.get("source", {}).get("name", "NewsAPI").strip()
            published_at = item.get("publishedAt", "")

            # Skip entries with missing critical fields
            if not title or not url_link:
                continue

            # Format published date
            published_date = ""
            if published_at:
                try:
                    dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                    published_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    published_date = published_at

            article = {
                "title": title,
                "description": description,
                "content": content if content else description,
                "source": f"NewsAPI - {source}",
                "url": url_link,
                "published_date": published_date,
            }
            articles.append(article)

        logger.info(f"NewsAPI fetched: {len(articles)} articles")

    except requests.exceptions.RequestException as e:
        logger.error(f"NewsAPI request failed: {e}")
    except Exception as e:
        logger.error(f"NewsAPI unexpected error: {e}")

    return articles


def fetch_from_rss():
    """
    Fetch news articles from all weather RSS feeds.
    Returns a list of structured article dictionaries.
    """
    logger.info("RSS Fetch Started - Weather Domain")
    all_articles = []

    for feed_url in WEATHER_RSS_FEEDS:
        try:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            def safe_entry_text(entry, key):
                value = entry.get(key, "")
                if isinstance(value, list):
                    value = value[0] if value else ""
                if value is None:
                    return ""
                return str(value).strip()

            for entry in feed.entries:
                title = safe_entry_text(entry, "title")
                description = safe_entry_text(entry, "summary") or safe_entry_text(entry, "description")
                content = ""

                # Try to extract full content if available
                if hasattr(entry, "content") and entry.content:
                    content_value = entry.content[0].get("value", "")
                    if isinstance(content_value, list):
                        content = " ".join(str(item) for item in content_value if item is not None).strip()
                    else:
                        content = str(content_value).strip() if content_value is not None else ""
                if not content:
                    content = description

                # feed.feed may be a mapping or a list (depending on feedparser version/structure)
                feed_meta = feed.feed
                if isinstance(feed_meta, list):
                    feed_meta = feed_meta[0] if feed_meta else {}

                # Now safely get the title if possible
                if hasattr(feed_meta, "get"):
                    source = feed_meta.get("title", feed_url)
                else:
                    # fallback to string representation
                    source = feed_url if not feed_meta else str(feed_meta)

                if isinstance(source, list):
                    source = source[0] if source else feed_url
                source = str(source).strip()

                url = entry.get("link", "")
                if isinstance(url, list):
                    url = url[0] if url else ""
                url = str(url).strip()

                # Parse published date
                published_date = ""
                parsed = entry.get("published_parsed")
                def _to_int_safe(x):
                    try:
                        return int(x)
                    except Exception:
                        try:
                            return int(str(x))
                        except Exception:
                            return 0

                if parsed:
                    try:
                        # feedparser may return a time.struct_time (has tm_year) or a tuple/list
                        if hasattr(parsed, "tm_year"):
                            year = int(getattr(parsed, "tm_year", 0))
                            month = int(getattr(parsed, "tm_mon", 0))
                            day = int(getattr(parsed, "tm_mday", 0))
                            hour = int(getattr(parsed, "tm_hour", 0))
                            minute = int(getattr(parsed, "tm_min", 0))
                            second = int(getattr(parsed, "tm_sec", 0))
                            published_date = datetime(year, month, day, hour, minute, second).strftime("%Y-%m-%d %H:%M:%S")
                        elif isinstance(parsed, (tuple, list)) and len(parsed) >= 6:
                            # tuple/list like struct_time: (year, mon, mday, hour, min, sec, ...)
                            # Explicitly map the first six values to datetime parameters to avoid
                            # accidentally passing extra tuple elements (which some feedparser
                            # implementations may include) into tzinfo or other params.
                            year = _to_int_safe(parsed[0])
                            month = _to_int_safe(parsed[1])
                            day = _to_int_safe(parsed[2])
                            hour = _to_int_safe(parsed[3])
                            minute = _to_int_safe(parsed[4])
                            second = _to_int_safe(parsed[5])
                            published_date = datetime(year, month, day, hour, minute, second).strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            published_date = entry.get("published", "")
                    except Exception:
                        published_date = entry.get("published", "")
                else:
                    published_date = entry.get("published", "")

                # Skip entries with missing critical fields
                if not title or not url:
                    continue

                article = {
                    "title": title,
                    "description": description,
                    "content": content,
                    "source": source,
                    "url": url,
                    "published_date": published_date,
                }
                all_articles.append(article)

        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")

    logger.info(f"RSS Retrieved - Total articles fetched: {len(all_articles)}")
    return all_articles


def fetch_news():
    """
    Fetch weather news from both RSS feeds and NewsAPI.
    Combines results from both sources.
    """
    logger.info("=" * 60)
    logger.info("Weather News Fetch Started (RSS + NewsAPI)")
    logger.info("=" * 60)

    # Fetch from both sources
    rss_articles = fetch_from_rss()
    newsapi_articles = fetch_from_newsapi(max_results=20)

    # Combine and deduplicate by URL
    seen_urls = set()
    all_articles = []

    for article in rss_articles + newsapi_articles:
        if article["url"] not in seen_urls:
            seen_urls.add(article["url"])
            all_articles.append(article)

    logger.info(f"Total unique articles: {len(all_articles)} (RSS: {len(rss_articles)}, NewsAPI: {len(newsapi_articles)})")
    return all_articles
