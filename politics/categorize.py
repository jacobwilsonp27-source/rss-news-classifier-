import logging
from transformers import pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Mandatory model as per project standards
CATEGORIZATION_MODEL = "facebook/bart-large-mnli"

# All categories as defined in the project document
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
    "Weather"
]

# Load model once at module level
logger.info(f"Loading categorization model: {CATEGORIZATION_MODEL}")
classifier = pipeline("zero-shot-classification", model=CATEGORIZATION_MODEL)
logger.info("Categorization model loaded successfully")


def categorize_article(text: str) -> dict:
    """
    Categorize a news article using BART zero-shot classification.

    Args:
        text (str): The article title + description combined text.

    Returns:
        dict: {
            "category": str,
            "confidence": float
        }
    """
    try:
        result = classifier(text, candidate_labels=CATEGORIES)

        category   = result["labels"][0]
        confidence = round(result["scores"][0], 4)

        logger.info(f"Category Assigned: {category} (confidence: {confidence})")

        return {
            "category"  : category,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Error during categorization: {e}")
        return {
            "category"  : "Politics",
            "confidence": 0.0
        }
