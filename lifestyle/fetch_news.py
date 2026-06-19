import feedparser
import logging

# Lifestyle RSS Feeds
RSS_FEEDS = [
    "https://rss.cnn.com/rss/cnn_living.rss",
    "https://www.theguardian.com/lifeandstyle/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Travel.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Food.xml"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_news():
    logging.info("RSS Fetch Started")

    articles = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            source_name = feed.feed.get("title", "Unknown Source")

            for entry in feed.entries:

                article = {
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", ""),
                    "content": entry.get("summary", ""),
                    "source": source_name,
                    "url": entry.get("link", ""),
                    "published_date": entry.get("published", "")
                }

                articles.append(article)

        except Exception as e:
            logging.error(f"Error reading feed: {feed_url}")
            logging.error(str(e))

    logging.info(f"News Retrieved: {len(articles)} articles")

    return articles


if __name__ == "__main__":
    news = fetch_news()

    print(f"\nTotal News: {len(news)}\n")

    for article in news[:5]:
        print("Title:", article["title"])
        print("Source:", article["source"])
        print("Published:", article["published_date"])
        print("-" * 80)