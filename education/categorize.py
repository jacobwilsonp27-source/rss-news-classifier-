"""
categorize.py
-------------
Responsibility:
  - Load facebook/bart-large-mnli (zero-shot classification)
  - Predict article category from the 11 predefined labels
  - Return category and confidence score

NO keyword matching – all predictions via Hugging Face transformer model.
"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# ── Mandatory categories (from PDF) ──────────────────────────────────────────
CATEGORIES: list[str] = [
    "Politics",
    "Business and Economy",
    "Technology",
    "Science",
    "Health",
    "Sports",
    "Entertainment",
    "Lifestyle",
    "International",
    "Education",
    "Weather",
]

MODEL_NAME: str = "facebook/bart-large-mnli"


# ── Model loader (singleton via lru_cache) ────────────────────────────────────
@lru_cache(maxsize=1)
def _load_classifier():
    """Load and cache the zero-shot classification pipeline."""
    from transformers import pipeline

    logger.info("Loading categorisation model: %s", MODEL_NAME)
    clf = pipeline(
        "zero-shot-classification",
        model=MODEL_NAME,
        device=-1,          # CPU; set to 0 for GPU
    )
    logger.info("Categorisation model loaded.")
    return clf


# ── Public API ────────────────────────────────────────────────────────────────

def categorize_article(text: str) -> dict[str, float | str]:
    """
    Classify *text* into one of the 11 mandatory categories.

    Parameters
    ----------
    text : str
        Combined title + description (or content) of the article.

    Returns
    -------
    dict
        {"category": str, "confidence": float}
    """
    if not text or not text.strip():
        logger.warning("Empty text passed to categorize_article; defaulting to Education.")
        return {"category": "Education", "confidence": 0.0}

    classifier = _load_classifier()

    # Truncate to 512 tokens worth of characters (BART limit ~1 024 tokens)
    truncated = text[:1024]

    result = classifier(truncated, CATEGORIES, multi_label=False)

    best_label      = result["labels"][0]
    best_confidence = round(float(result["scores"][0]), 4)

    logger.info("Category Assigned | category=%s | confidence=%.4f",
                best_label, best_confidence)

    return {"category": best_label, "confidence": best_confidence}


def categorize_batch(articles: list[dict]) -> list[dict]:
    """
    Categorise a list of article dicts in-place (adds 'category' and
    'category_confidence' keys).

    Uses a single model call per article for clarity; batch inference
    can be added if GPU is available.
    """
    classifier = _load_classifier()   # warm-up once

    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '')}"
        result = categorize_article(text)
        article["category"]            = result["category"]
        article["category_confidence"] = result["confidence"]

    return articles


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = "IIT Bombay introduces new undergraduate curriculum for AI and Data Science students"
    print(categorize_article(sample))
