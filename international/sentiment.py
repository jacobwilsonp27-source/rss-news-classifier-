"""
sentiment.py

Category: International / World

Responsibility (per project standards document):
    - Load RoBERTa sentiment model
    - Analyze article sentiment
    - Return sentiment and confidence score

Model (mandatory): cardiffnlp/twitter-roberta-base-sentiment-latest
Output Labels: positive, negative, neutral

No keyword-based logic of any kind is used in this file. All sentiment
predictions are produced exclusively by the approved Hugging Face
transformer model.
"""

import logging
from typing import Dict

from transformers import pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sentiment")

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# The model's native labels map directly to these standard labels.
LABEL_MAP = {
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}

_sentiment_analyzer = None


def load_model():
    """
    Load the mandatory sentiment analysis model
    (cardiffnlp/twitter-roberta-base-sentiment-latest).
    """
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        logger.info(f"Loading sentiment model: {MODEL_NAME}")
        _sentiment_analyzer = pipeline("sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME)
        logger.info("Sentiment model loaded successfully.")
    return _sentiment_analyzer


def analyze_sentiment(text: str) -> Dict:
    """
    Predict the sentiment of a news article using the mandated transformer model.

    Args:
        text: The article text to analyze.

    Returns:
        Dictionary in the standard output format:
        {"sentiment": "positive", "confidence": 0.91}
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for sentiment analysis.")
        return {"sentiment": "neutral", "confidence": 0.0}

    analyzer = load_model()

    try:
        result = analyzer(text, truncation=True, max_length=512)[0]
        raw_label = result["label"]
        sentiment_label = LABEL_MAP.get(raw_label, raw_label.lower())
        confidence = round(float(result["score"]), 4)

        logger.info(f"Sentiment Assigned - Sentiment: {sentiment_label} - Confidence: {confidence}")

        return {
            "sentiment": sentiment_label,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        return {"sentiment": "neutral", "confidence": 0.0}


if __name__ == "__main__":
    sample_text = "The peace agreement marks a hopeful turning point for the region."
    output = analyze_sentiment(sample_text)
    print(output)