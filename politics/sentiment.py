import logging
from transformers import pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Mandatory model as per project standards
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Label mapping from model output to standard labels
LABEL_MAP = {
    "positive": "positive",
    "negative": "negative",
    "neutral" : "neutral",
    "LABEL_0" : "negative",
    "LABEL_1" : "neutral",
    "LABEL_2" : "positive",
}

# Load model once at module level
logger.info(f"Loading sentiment model: {SENTIMENT_MODEL}")
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model=SENTIMENT_MODEL,
    truncation=True,
    max_length=512
)
logger.info("Sentiment model loaded successfully")


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a news article using RoBERTa.

    Args:
        text (str): The article title + description combined text.

    Returns:
        dict: {
            "sentiment": str,   # positive / negative / neutral
            "confidence": float
        }
    """
    try:
        result = sentiment_analyzer(text[:512])  # Truncate for model input limit

        raw_label  = result[0]["label"].lower()
        confidence = round(result[0]["score"], 4)

        # Normalize label to standard format
        sentiment = LABEL_MAP.get(raw_label, raw_label)

        logger.info(f"Sentiment Assigned: {sentiment} (confidence: {confidence})")

        return {
            "sentiment" : sentiment,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Error during sentiment analysis: {e}")
        return {
            "sentiment" : "neutral",
            "confidence": 0.0
        }
