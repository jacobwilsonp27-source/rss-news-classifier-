import feedparser

RSS_FEEDS = [
    "https://www.sciencedaily.com/rss/top/science.xml",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss"
]

def fetch_news():
    articles = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:2]:
            article = {
                "title": entry.get("title", ""),
                "description": entry.get("summary", ""),
                "content": entry.get("summary", ""),
                "source": feed.feed.get("title", ""),
                "url": entry.get("link", ""),
                "published_date": entry.get("published", "")
            }

            articles.append(article)

    return articles