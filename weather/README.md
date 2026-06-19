# Weather News Intelligence Module

AI-Powered News Categorization Platform — Weather Domain Module

## Features

- **RSS Feeds**: 10 weather-specific RSS sources
- **NewsAPI Integration**: Fetches weather-related articles via NewsAPI `/everything` endpoint
- **AI Categorization**: BART zero-shot classification (same model as all modules)
- **Sentiment Analysis**: RoBERTa sentiment model
- **SQLite Database**: Stores processed articles with duplicate prevention

## Structure

| File | Purpose |
|------|---------|
| `app.py` | FastAPI server with endpoints |
| `fetch_news.py` | Fetches weather news from RSS + NewsAPI |
| `categorize.py` | BART zero-shot classification |
| `sentiment.py` | Sentiment analysis using RoBERTa |
| `database.py` | SQLite database operations |
| `requirements.txt` | Python dependencies |

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get NewsAPI Key (Optional but Recommended)

1. Go to [https://newsapi.org](https://newsapi.org) and sign up for a free API key
2. Set it as an environment variable:

```bash
export NEWSAPI_KEY="your_actual_api_key_here"
```

Or edit `fetch_news.py` and replace `YOUR_NEWSAPI_KEY_HERE` with your key.

> **Note**: Without a NewsAPI key, the module will still work using RSS feeds only.

### 3. Run the API

```bash
python app.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/fetch` | Fetch and process latest weather news (RSS + NewsAPI) |
| GET | `/news` | Get all weather news articles |
| GET | `/news/{id}` | Get article by ID |
| GET | `/news/sentiment/{label}` | Get news by sentiment (positive/negative/neutral) |
| GET | `/news/category/{category}` | Get news by category (returns Weather only) |

## Data Sources

### RSS Feeds
- The Weather Network
- Weather.com
- AccuWeather
- NOAA
- UK Met Office
- US National Weather Service
- WeatherZone
- Weather Underground
- Climate Central
- National Geographic

### NewsAPI
- Searches for: weather forecast, severe weather, hurricane, tornado, flood, drought, heatwave, snowstorm, climate change, meteorology
- Time range: Last 7 days
- Max results: 20 per fetch

## Database

- File: `weather_news.db`
- Same schema as all other domain modules

## NewsAPI Free Tier Limits

- 100 requests per day
- JSON response only
- No historical data beyond 1 month
- Requires attribution: "Powered by News API"

## Running Multiple Modules

If running alongside other domain modules, change the port in `app.py`:

```python
uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)  # Weather
```
