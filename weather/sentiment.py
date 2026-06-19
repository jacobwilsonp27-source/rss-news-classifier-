import logging
from transformers import pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Sentiment analysis model
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

logger.info(f"Loading sentiment model: {SENTIMENT_MODEL}")
# use positional arg for task to satisfy type-checkers that expect a Literal task argument
sentiment_analyzer = pipeline("sentiment-analysis", model=SENTIMENT_MODEL)  # type: ignore[call-arg]
logger.info("Sentiment model loaded successfully")


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a news article.

    Args:
        text (str): The article title + description combined text.

    Returns:
        dict: {
            "sentiment": str,      # positive | negative | neutral
            "confidence": float
        }
    """
    try:
        # Truncate text to max 512 tokens for the model
        truncated_text = text[:512]
        result = sentiment_analyzer(truncated_text)[0]

        raw_label = result["label"].lower()
        confidence = round(result["score"], 4)

        # Map model labels to standard labels
        label_map = {
            "positive": "positive",
            "negative": "negative",
            "neutral": "neutral",
            "label_0": "negative",
            "label_1": "neutral",
            "label_2": "positive"
        }

        sentiment = label_map.get(raw_label, "neutral")

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
