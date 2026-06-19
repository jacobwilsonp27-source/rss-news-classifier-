from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

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

def categorize_news(text):
    result = classifier(text, CATEGORIES)

    return {
        "category": result["labels"][0],
        "confidence": float(result["scores"][0])
    }