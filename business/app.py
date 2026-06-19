from fastapi import FastAPI, HTTPException
import sqlite3
from datetime import datetime

# Importing all independent modular packages components we built
import database
import fetch_news
import categorize
import sentiment

# Initialize FastAPI framework core object
app = FastAPI(title="Business and Economy News Module Platform Instance")

# Contract Verification Mapping Rules: Lowercase database metrics to Strict Capitalized JSON Output
SENTIMENT_MAP = {
    "positive": "Positive",
    "negative": "Negative",
    "neutral": "Neutral"
}

@app.on_event("startup")
def startup_pipeline_init():
    """
    Triggers automatically when web server starts up to instantiate storage bounds safely.
    """
    database.init_db()
    print("LOG: API Started") # Mandatory Logging Standard constraint

# =========================================================
# ⚙️ BACKGROUND REVENUE STREAM PROCESSING PIPELINE ROUTE
# =========================================================
@app.post("/news/sync", summary="Fetch web data parsed transformers clean engine logs pipeline")
def synchronize_news_feeds():
    """
    Runs automated integration workflow matching standard architecture.
    """
    # Step 1 & 2 Execution routes
    raw_articles = fetch_news.fetch_business_news()
    processed_sync_count = 0
    
    for item in raw_articles:
        # Step 3 Execution: Passing title text context matrix directly
        category_meta = categorize.classify_news_category(item["title"])
        
        # CRITICAL FILTER CONSTRAINT SPEC: Only focus on your assigned team segment category!
        if category_meta["category"] != "Business and Economy":
            continue # Discard and skip if it dynamically tracks to other modules domains
            
        # Step 4 Execution: Sentiment prediction loops
        sentiment_meta = sentiment.analyze_news_sentiment(item["title"])
        
        # Mapping lowercase model output directly to rigid CamelCase contract standard strings
        clean_sentiment_string = SENTIMENT_MAP.get(sentiment_meta["sentiment"], "Neutral")
        
        # Preparing unified object structures layout matching exact table column metrics fields
        db_insert_payload = {
            "title": item["title"],
            "description": item["description"],
            "content": item["content"],
            "source": item["source"],
            "url": item["url"],
            "category": "Business and Economy", # Valid static uppercase spec strings match
            "category_confidence": category_meta["confidence"],
            "sentiment": clean_sentiment_string,
            "sentiment_confidence": sentiment_meta["confidence"],
            "published_date": item["published_date"]
        }
        
        # Step 5 Execution: Attempt insertion database logic module constraints 
        was_inserted = database.insert_news_article(db_insert_payload)
        if was_inserted:
            processed_sync_count += 1
            
    return {"status": "sync_completed", "new_business_articles_cached": processed_sync_count}

# =========================================================
# 🛣️ MANDATORY TEAM INTEGRATION API ENDPOINTS SPECIFICATIONS
# =========================================================

def format_row_to_spec_json(row):
    """
    Helper function that parses SQLite rows arrays query responses 
    into exact Page 5 structured Standard News JSON Contract output bounds.
    """
    if not row:
        return None
    return {
        "id": int(row[0]),
        "title": str(row[1]),
        "description": str(row[2]),
        "content": str(row[3]),
        "source": str(row[4]),
        "url": str(row[5]),
        "category": str(row[6]),
        "category_confidence": float(row[7]),
        "sentiment": str(row[8]),
        "sentiment_confidence": float(row[9]),
        "published_date": str(row[10])
    }

@app.get("/news", summary="Get All News API standard route mapping specs")
def get_all_news_articles():
    conn = sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news")
    rows = cursor.fetchall()
    conn.close()
    return [format_row_to_spec_json(r) for r in rows]

@app.get("/news/{id}", summary="Get News By ID metric endpoints validation")
def get_news_article_by_unique_id(id: int):
    conn = sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="News article database entry item not found")
    return format_row_to_spec_json(row)

@app.get("/news/sentiment/{label}", summary="Get News By Sentiment query filter endpoint")
def get_news_articles_by_sentiment_filter(label: str):
    # Normalize input matching exact contract case validations strings logic array checks
    formatted_label = label.strip().capitalize() # Converts 'positive' -> 'Positive'
    if formatted_label not in ["Positive", "Negative", "Neutral"]:
        raise HTTPException(status_code=400, detail="Invalid target query sentiment parameter label structure")
        
    conn = sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE sentiment = ?", (formatted_label,))
    rows = cursor.fetchall()
    conn.close()
    return [format_row_to_spec_json(r) for r in rows]

@app.get("/news/category/{category}", summary="Get News By Category validation query filters endpoint route")
def get_news_articles_by_category_grouping(category: str):
    conn = sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE LOWER(category) = ?", (category.strip().lower(),))
    rows = cursor.fetchall()
    conn.close()
    return [format_row_to_spec_json(r) for r in rows]