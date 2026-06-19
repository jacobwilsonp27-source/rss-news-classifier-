import feedparser

BUSINESS_RSS_FEEDS = [
    "https://finance.yahoo.com/news/rssindex",
    "https://www.reutersagency.com/feed/?best-topics=business"
]

def _normalize_feed_value(value, fallback=""):
    if isinstance(value, list) and value:
        value = value[0]

    if isinstance(value, dict):
        value = value.get("value", value.get("text", fallback))

    if value is None:
        return fallback

    return str(value).strip()


def _get_entry_text(entry, key, fallback=""):
    return _normalize_feed_value(entry.get(key, fallback), fallback)


def fetch_business_news():
    print("LOG: RSS Fetch Started")

    all_extracted_articles = []

    for feed_url in BUSINESS_RSS_FEEDS:
        try:
            parsed_feed = feedparser.parse(feed_url)

            # Source name
            feed_obj = getattr(parsed_feed, "feed", {})
            if isinstance(feed_obj, dict):
                source_name = feed_obj.get("title", "Global Business News")
            else:
                source_name = "Global Business News"

            for entry in parsed_feed.entries:
                title = _get_entry_text(entry, "title")

                # Safer description fallback
                description = (
                    _get_entry_text(entry, "summary")
                    or _get_entry_text(entry, "description")
                    or ""
                )

                # FIX: Proper content extraction
                content_data = entry.get("content", "")
                content = _normalize_feed_value(content_data, description)

                article_url = _get_entry_text(entry, "link")

                # FIX: Safe published date
                published_date = (
                    _get_entry_text(entry, "published")
                    or _get_entry_text(entry, "updated")
                    or ""
                )

                article_data = {
                    "title": title,
                    "description": description,
                    "content": content,
                    "source": source_name,
                    "url": article_url,
                    "published_date": published_date,
                }

                if title and article_url:
                    all_extracted_articles.append(article_data)

        except Exception as e:
            print(f"ERROR: Failed to parse {feed_url} → {e}")

    print("LOG: News Retrieved")
    return all_extracted_articles


# ==========================================
# SELF TEST
# ==========================================
if __name__ == "__main__":
    sample_news = fetch_business_news()
    print(f"\nTotal articles grabbed: {len(sample_news)}")

    if sample_news:
        import json
        print("\n--- FIRST SAMPLE ARTICLE FETCHED ---")
        print(json.dumps(sample_news[0], indent=2))