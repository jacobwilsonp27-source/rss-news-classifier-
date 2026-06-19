from transformers import pipeline

# Project Document Specification Rule: Using mandatory model string
MODEL_NAME = "facebook/bart-large-mnli"

print("LOG: Loading BART Categorization Model... (Please wait, downloading weights)")
# Adding fallback configurations for clean streaming windows compatibility
classifier = pipeline("zero-shot-classification", model=MODEL_NAME, use_fast=False)

# Exact 11 categories array specified inside page 3 contract standard
ALLOWED_CATEGORIES = [
    "Politics", "Business and Economy", "Technology", "Science", 
    "Health", "Sports", "Entertainment", "Lifestyle", 
    "International", "Education", "Weather"
]

def classify_news_category(headline_text: str) -> dict:
    if not headline_text or not headline_text.strip():
        return {"category": "Business and Economy", "confidence": 0.50}
        
    result = classifier(headline_text, candidate_labels=ALLOWED_CATEGORIES)
    
    predicted_label = result["labels"][0]
    raw_score = result["scores"][0]
    confidence_score = round(float(raw_score), 2)
    
    print(f"LOG: Category Assigned")
    return {
        "category": predicted_label,
        "confidence": confidence_score
    }

if __name__ == "__main__":
    test_headline = "Nifty climbs past crucial resistance levels as tech stocks rally"
    print(f"\nTesting AI Engine with headline: '{test_headline}'")
    
    prediction = classify_news_category(test_headline)
    import json
    print(json.dumps(prediction, indent=2))