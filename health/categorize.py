"""
categorize.py

Category: Health

Responsibility (per project standards document):
    - Load BART model
    - Predict article category
    - Return category and confidence score

Model (mandatory): facebook/bart-large-mnli
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
    global _classifier
    if _classifier is None:
        logger.info(f"Loading categorization model: {MODEL_NAME}")
        # Force CPU device to avoid meta-device / accelerated device_map issues
        _classifier = pipeline("zero-shot-classification", model=MODEL_NAME, device=-1)
        logger.info("Categorization model loaded successfully.")
    return _classifier


def categorize_article(text: str) -> Dict:
    if not text or not text.strip():
        logger.warning("Empty text provided for categorization.")
        return {"category": "Health", "confidence": 0.0}

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
        return {"category": "Health", "confidence": 0.0}


if __name__ == "__main__":
    sample_text = "New study finds regular exercise significantly reduces risk of chronic illness."
    output = categorize_article(sample_text)
    print(output)