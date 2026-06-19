"""
sentiment.py - Entertainment Module

Responsibilities (per project standards):
    - Load RoBERTa sentiment model (cardiffnlp/twitter-roberta-base-sentiment-latest)
    - Analyze article sentiment
    - Return sentiment and confidence score

IMPORTANT: Keyword matching is strictly prohibited.
All predictions are generated using the approved Hugging Face
transformer model. No "if 'win' in text" logic anywhere.
"""

import logging

from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentiment")

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# This model's raw output labels are LABEL_0 / LABEL_1 / LABEL_2 unless the
# pipeline picks up the model's config id2label mapping. We normalize to the
# exact label strings required by the project's standard JSON format.
LABEL_MAP = {
    "negative": "negative",
    "neutral": "neutral",
    "positive": "positive",
    "label_0": "negative",
    "label_1": "neutral",
    "label_2": "positive",
}

_sentiment_pipeline = None

# Most transformer sentiment models truncate long input; this is a
# tokenizer-level limit, not keyword logic.
MAX_CHARS = 512


def get_sentiment_pipeline():
    """
    Lazily load the sentiment-analysis pipeline so the model
    is only loaded into memory once per process.
    """
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        logger.info("Loading sentiment model: %s", MODEL_NAME)
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=MODEL_NAME,
            tokenizer=MODEL_NAME,
        )
    return _sentiment_pipeline


def analyze_sentiment(text: str) -> dict:
    """
    Predict the sentiment of a news article using the approved
    transformer model.

    Args:
        text: The article text to analyze.

    Returns:
        {
            "sentiment": "positive",
            "confidence": 0.94
        }
    """
    if not text or not text.strip():
        logger.warning("Empty text passed to analyze_sentiment; defaulting to neutral.")
        return {"sentiment": "neutral", "confidence": 0.0}

    classifier = get_sentiment_pipeline()
    truncated_text = text[:MAX_CHARS]

    result = classifier(truncated_text)[0]

    raw_label = str(result["label"]).lower()
    normalized_label = LABEL_MAP.get(raw_label, raw_label)
    confidence = float(result["score"])

    logger.info("Sentiment Assigned: %s (confidence=%.4f)", normalized_label, confidence)

    return {
        "sentiment": normalized_label,
        "confidence": round(confidence, 4),
    }


if __name__ == "__main__":
    sample = "Fans and critics alike loved the surprise twist ending of the new series finale."
    print(analyze_sentiment(sample))
