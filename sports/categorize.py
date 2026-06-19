from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

LABELS = [
    "Sports",
    "Non-Sports"
]


def categorize_article(text):
    result = classifier(
        text,
        candidate_labels=LABELS,
        hypothesis_template="This article is about {}."
    )

    return {
        "category": result["labels"][0],
        "confidence": float(result["scores"][0])
    }