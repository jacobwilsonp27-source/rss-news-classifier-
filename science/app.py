from fastapi import FastAPI

from fetch_news import fetch_news
from categorize import categorize_news
from sentiment import analyze_sentiment

from database import create_database
from database import save_article
from database import get_all_news
from database import get_news_by_id
from database import get_news_by_sentiment
from database import get_news_by_category

app = FastAPI()

create_database()


@app.get("/")
def home():
    return {"message": "Science News API Working"}


@app.get("/news")
def get_news():

    articles = fetch_news()

    processed_articles = []

    for article in articles:

        text = article["title"] + " " + article["description"]

        category_result = categorize_news(text)

        sentiment_result = analyze_sentiment(text)

        article["category"] = category_result["category"]
        article["category_confidence"] = category_result["confidence"]

        article["sentiment"] = sentiment_result["sentiment"]
        article["sentiment_confidence"] = sentiment_result["confidence"]

        save_article(article)

        processed_articles.append(article)

    return processed_articles


@app.get("/news/{id}")
def news_by_id(id: int):
    return get_news_by_id(id)


@app.get("/news/sentiment/{label}")
def news_by_sentiment(label: str):
    return get_news_by_sentiment(label)


@app.get("/news/category/{category}")
def news_by_category(category: str):
    return get_news_by_category(category)