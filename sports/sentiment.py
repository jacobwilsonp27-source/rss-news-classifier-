"""
sentiment.py
Module: Sports
Compatible with: Python 3.12.10 / 3.14.6

Responsibilities:
- Load RoBERTa sentiment model (cardiffnlp/twitter-roberta-base-sentiment-latest)
- Analyze article sentiment
- Return sentiment and confidence score

NOTE: Keyword matching is strictly prohibited. There is no "if 'win' in text"
or similar rule-based logic anywhere in this file. The sentiment label and
confidence are produced entirely by the transformer model below.
"""

import logging

from transformers import pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentiment")

logger.info("Loading sentiment model: cardiffnlp/twitter-roberta-base-sentiment-latest")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
)

# Some model revisions return LABEL_0/1/2 instead of named labels.
LABEL_MAP = {
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
    "label_0": "negative",
    "label_1": "neutral",
    "label_2": "positive",
}


def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of a news article using a transformer model.

    Args:
        text (str): The article text (title + description/content).

    Returns:
        dict: {"sentiment": str, "confidence": float}
    """
    if not text or not text.strip():
        return {"sentiment": "neutral", "confidence": 0.0}

    # The model has a 512-token limit; truncate long article bodies.
    truncated_text = text[:512]
    result = sentiment_pipeline(truncated_text)[0]

    raw_label = result["label"].lower()
    sentiment = LABEL_MAP.get(raw_label, raw_label)
    confidence = round(float(result["score"]), 4)

    logger.info(f"Sentiment Assigned: {sentiment} ({confidence})")
    return {"sentiment": sentiment, "confidence": confidence}


if __name__ == "__main__":
    sample = "The team played an outstanding game and fans were thrilled with the result."
    print(analyze_sentiment(sample))
