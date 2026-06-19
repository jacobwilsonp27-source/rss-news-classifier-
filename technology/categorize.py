"""
categorize.py
--------------
Responsible for classifying an article into one of the project's 11
mandatory news categories using zero-shot classification.

Responsibilities (per project standards):
    - Load the facebook/bart-large-mnli model
    - Predict the article's category
    - Return category and confidence score

IMPORTANT: keyword matching (e.g. `if "chip" in text: category = "Technology"`)
is strictly prohibited by the project standards. Every prediction here comes
from the transformer model's own understanding of the text - never from
string matching or hand-written rules.
"""

import logging
from typing import Dict, Any

from transformers import pipeline

logger = logging.getLogger("technology_module.categorize")

# Exact category list mandated by the project document. Order does not
# affect the result, but every module must offer the model this same set
# of candidate labels so all modules classify consistently.
CANDIDATE_CATEGORIES = [
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

# The model is loaded once, at import time, and reused for every
# classification call. Loading it inside the function would reload
# roughly 1.6 GB of model weights on every single article, which would
# be extremely slow and would also re-download/re-initialize unnecessarily.
logger.info("Loading facebook/bart-large-mnli (this can take a while on first run)...")
_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
logger.info("Category model loaded.")


def categorize_article(text: str) -> Dict[str, Any]:
    """
    Classifies `text` against CANDIDATE_CATEGORIES using zero-shot
    classification and returns:

        {
            "category": "Technology",
            "confidence": 0.97
        }

    Zero-shot classification works by having the model score how well
    the text entails a natural-language hypothesis built from each
    candidate label internally (roughly "This text is about Technology.").
    No fine-tuning and no keyword lists are involved - the model relies
    purely on what it already learned about language during pretraining.
    """
    if not text or not text.strip():
        return {"category": "Unknown", "confidence": 0.0}

    result = _classifier(text, candidate_labels=CANDIDATE_CATEGORIES, multi_label=False)

    top_category = result["labels"][0]
    top_score = float(result["scores"][0])

    logger.info(f"Category Assigned: {top_category} ({top_score:.2f})")

    return {
        "category": top_category,
        "confidence": round(top_score, 4),
    }


if __name__ == "__main__":
    # Independent test block - lets you verify categorize.py works
    # correctly by running `python categorize.py` directly, with no RSS
    # feeds, database, or FastAPI involved.
    logging.basicConfig(level=logging.INFO)

    sample_text = (
        "Apple unveiled its newest M5 chip today, promising significant "
        "performance gains for laptops and tablets while improving battery life."
    )
    print(categorize_article(sample_text))

    sample_text_2 = "The national team won the championship final in a dramatic penalty shootout."
    print(categorize_article(sample_text_2))
