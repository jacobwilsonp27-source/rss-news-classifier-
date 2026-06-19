"""
sentiment.py
------------
Responsible for analyzing the sentiment of an article using a
transformer model - never keyword matching.

Responsibilities (per project standards):
    - Load the cardiffnlp/twitter-roberta-base-sentiment-latest model
    - Analyze article sentiment
    - Return sentiment label and confidence score
"""

import logging
from typing import Any, Dict, cast

from transformers import pipeline

logger = logging.getLogger("technology_module.sentiment")

# cardiffnlp/twitter-roberta-base-sentiment-latest returns "negative",
# "neutral", "positive" labels directly in most recent versions of
# transformers, but some pipeline/model-config combinations surface raw
# LABEL_0 / LABEL_1 / LABEL_2 instead. This map normalizes either case to
# the exact three labels mandated by the project spec.
_LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
    "negative": "negative",
    "neutral": "neutral",
    "positive": "positive",
}

logger.info("Loading cardiffnlp/twitter-roberta-base-sentiment-latest...")
_pipeline = cast(Any, pipeline)
_sentiment_pipeline = cast(Any, _pipeline(
    task="sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
))
logger.info("Sentiment model loaded.")


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyzes `text` and returns:

        {
            "sentiment": "positive",
            "confidence": 0.94
        }

    The model was trained on a large corpus of real-world text to
    recognize tone and emotional valence directly. It has no concept of
    a fixed "positive words list" - which is exactly why it can correctly
    read a sentence like "prices finally stopped crashing" as positive,
    even though the word "crashing" looks negative in isolation.
    """
    if not text or not text.strip():
        return {"sentiment": "neutral", "confidence": 0.0}

    # The model has a maximum input length. truncation=True safely cuts
    # off extra tokens instead of crashing on long article bodies.
    truncated = text[:2000]
    result = _sentiment_pipeline(truncated, truncation=True)[0]

    label = _LABEL_MAP.get(result["label"], result["label"].lower())
    score = float(result["score"])

    logger.info(f"Sentiment Assigned: {label} ({score:.2f})")

    return {
        "sentiment": label,
        "confidence": round(score, 4),
    }


if __name__ == "__main__":
    # Independent test block - lets you verify sentiment.py works
    # correctly by running `python sentiment.py` directly, with no RSS
    # feeds, database, or FastAPI involved.
    logging.basicConfig(level=logging.INFO)

    print(analyze_sentiment("This new chip is an incredible leap forward for the entire industry."))
    print(analyze_sentiment("The company's latest update bricked thousands of devices overnight."))
    print(analyze_sentiment("The conference has been rescheduled to next Tuesday."))
