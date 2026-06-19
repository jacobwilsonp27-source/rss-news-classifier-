"""
categorize.py - Entertainment Module

Responsibilities (per project standards):
    - Load BART model (facebook/bart-large-mnli)
    - Predict article category
    - Return category and confidence score

IMPORTANT: Keyword matching is strictly prohibited.
All predictions are generated using the approved Hugging Face
zero-shot classification model. No "if 'word' in text" logic anywhere.
"""

import logging

from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("categorize")

MODEL_NAME = "facebook/bart-large-mnli"

CATEGORIES = [
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

_classifier = None


def get_classifier():
    """
    Lazily load the zero-shot classification pipeline so the model
    is only loaded into memory once per process.
    """
    global _classifier
    if _classifier is None:
        logger.info("Loading categorization model: %s", MODEL_NAME)
        _classifier = pipeline("zero-shot-classification", model=MODEL_NAME)
    return _classifier


def categorize_article(text: str) -> dict:
    """
    Predict the category of a news article using zero-shot classification.

    Args:
        text: The article text to classify (title + description/content
              recommended for best accuracy).

    Returns:
        {
            "category": "Entertainment",
            "confidence": 0.97
        }
    """
    if not text or not text.strip():
        logger.warning("Empty text passed to categorize_article; defaulting to lowest confidence.")
        return {"category": "Entertainment", "confidence": 0.0}

    classifier = get_classifier()
    result = classifier(text, candidate_labels=CATEGORIES, multi_label=False)

    top_label = result["labels"][0]
    top_score = float(result["scores"][0])

    logger.info("Category Assigned: %s (confidence=%.4f)", top_label, top_score)

    return {
        "category": top_label,
        "confidence": round(top_score, 4),
    }


if __name__ == "__main__":
    sample = (
        "The film took home five awards at last night's ceremony, "
        "with the lead actress praised for her performance."
    )
    print(categorize_article(sample))
