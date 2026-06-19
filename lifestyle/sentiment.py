from transformers import pipeline

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)


def analyze_sentiment(text):
    text = str(text)

    if len(text) > 300:
        text = text[:300]

    result = sentiment_analyzer(text)[0]

    return {
        "sentiment": result["label"].lower(),
        "confidence": float(result["score"])
    }