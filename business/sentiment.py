from transformers import pipeline

# Project Document Specification Rule: Mandatory sentiment model
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

print("LOG: Loading RoBERTa Sentiment Model... (Please wait, downloading weights)")
# Initializing Sentiment pipeline with Windows architecture fallback properties
sentiment_analyzer = pipeline("sentiment-analysis", model=MODEL_NAME, use_fast=False)

def analyze_news_sentiment(headline_text: str) -> dict:
    """
    Takes a news headline, processes it via RoBERTa transformer,
    and returns sentiment token matching strict JSON requirements.
    """
    if not headline_text or not headline_text.strip():
        return {"sentiment": "neutral", "confidence": 1.0}
        
    # Standard 512 token truncation safety check limits 
    truncated_input = headline_text[:512]
    
    # Running inference matching raw metrics execution
    result = sentiment_analyzer(truncated_input)[0]
    
    # Contract constraint values format clean matching (Lower-case strings expected)
    predicted_label = result["label"].lower()
    raw_score = result["score"]
    
    # Rounding float parameters up to 2 decimals standard layout
    confidence_score = round(float(raw_score), 2)
    
    # Logging Requirement Standard checked off here
    print("LOG: Sentiment Assigned")
    
    # Exact structure requested on page 6/7 metadata layout specification
    return {
        "sentiment": predicted_label,
        "confidence": confidence_score
    }

# ==========================================
# SELF TESTING CODE BLOCK
# ==========================================
if __name__ == "__main__":
    test_headline = "Nifty climbs past crucial resistance levels as tech stocks rally"
    print(f"\nTesting Sentiment Engine with headline: '{test_headline}'")
    
    sentiment_output = analyze_news_sentiment(test_headline)
    import json
    print(json.dumps(sentiment_output, indent=2))