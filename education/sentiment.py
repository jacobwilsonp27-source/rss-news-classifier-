"""
sentiment.py
------------
Responsibility:
  - Load cardiffnlp/twitter-roberta-base-sentiment-latest
  - Analyse article sentiment
  - Return sentiment label (positive / negative / neutral) and confidence score

NO keyword matching – all predictions via Hugging Face transformer model.
"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

MODEL_NAME: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Label map: model outputs Roberta labels → human-readable
LABEL_MAP: dict[str, str] = {
    "positive": "positive",
    "negative": "negative",
    "neutral":  "neutral",
    # fallback for older model label formats
    "LABEL_0":  "negative",
    "LABEL_1":  "neutral",
    "LABEL_2":  "positive",
}


# ── Model loader (singleton via lru_cache) ────────────────────────────────────
@lru_cache(maxsize=1)
def _load_sentiment_model():
    """Load and cache the sentiment analysis pipeline."""
    from transformers import pipeline

    logger.info("Loading sentiment model: %s", MODEL_NAME)
    # Use the generic text-classification task to satisfy type stubs
    # (equivalent to sentiment-analysis for this model).
    model = pipeline(
        "text-classification",
        model=MODEL_NAME,
        device=-1,          # CPU; set to 0 for GPU
    )
    logger.info("Sentiment model loaded.")
    return model


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_sentiment(text: str) -> dict[str, float | str]:
    """
    Predict sentiment for *text*.

    Parameters
    ----------
    text : str
        Article text (title + description recommended).

    Returns
    -------
    dict
        {"sentiment": str, "confidence": float}
    """
    if not text or not text.strip():
        logger.warning("Empty text passed to analyze_sentiment; defaulting neutral.")
        return {"sentiment": "neutral", "confidence": 0.0}

    model = _load_sentiment_model()

    # RoBERTa max input ~512 tokens; character-level truncation before tokeniser
    truncated = text[:1000]

    result = model(truncated)[0]

    raw_label = result["label"].lower()
    label     = LABEL_MAP.get(raw_label, "neutral")
    confidence = round(float(result["score"]), 4)

    logger.info("Sentiment Assigned | sentiment=%s | confidence=%.4f",
                label, confidence)

    return {"sentiment": label, "confidence": confidence}


def analyze_batch(articles: list[dict]) -> list[dict]:
    """
    Analyse sentiment for a list of article dicts in-place (adds 'sentiment'
    and 'sentiment_confidence' keys).
    """
    _load_sentiment_model()   # warm-up once

    for article in articles:
        text   = f"{article.get('title', '')} {article.get('description', '')}"
        result = analyze_sentiment(text)
        article["sentiment"]            = result["sentiment"]
        article["sentiment_confidence"] = result["confidence"]

    return articles


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = "Students across India celebrate record-breaking board exam results"
    print(analyze_sentiment(sample))
