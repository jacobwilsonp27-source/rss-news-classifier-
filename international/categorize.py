"""
categorize.py

Category: International / World

Responsibility (per project standards document):
    - Load BART model
    - Predict article category
    - Return category and confidence score

Model (mandatory): facebook/bart-large-mnli
Purpose: Zero-shot news classification

No keyword-based logic of any kind is used in this file. All category
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
logger = logging.getLogger("categorize")

MODEL_NAME = "facebook/bart-large-mnli"

# Categories exactly as specified in the standards document.
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


def load_model():
    """
    Load the mandatory zero-shot classification model
    (facebook/bart-large-mnli).
    """
    global _classifier
    if _classifier is None:
        logger.info(f"Loading categorization model: {MODEL_NAME}")
        _classifier = pipeline("zero-shot-classification", model=MODEL_NAME)
        logger.info("Categorization model loaded successfully.")
    return _classifier


def categorize_article(text: str) -> Dict:
    """
    Predict the category of a news article using zero-shot classification.

    Args:
        text: The article text to classify (title + description/content
        recommended for best context).

    Returns:
        Dictionary in the standard output format:
        {"category": "Sports", "confidence": 0.96}
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for categorization.")
        return {"category": "International", "confidence": 0.0}

    classifier = load_model()

    try:
        result = classifier(
            text,
            candidate_labels=CATEGORIES,
            truncation=True,
            max_length=512
        )
        predicted_category = result["labels"][0]
        confidence = round(float(result["scores"][0]), 4)

        logger.info(f"Category Assigned - Category: {predicted_category} - Confidence: {confidence}")

        return {
            "category": predicted_category,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Failed to categorize article: {e}")
        return {"category": "International", "confidence": 0.0}


if __name__ == "__main__":
    sample_text = "World leaders gathered for an emergency summit to discuss the ongoing global crisis."
    output = categorize_article(sample_text)
    print(output)