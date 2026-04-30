import pandas as pd
import requests
import nltk
import yfinance as yf
import urllib.parse
import feedparser
import time
from functools import lru_cache
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from services.stock_fetcher import get_nasdaq100_tickers

# ======================
# SETUP
# ======================
nltk.download("vader_lexicon", quiet=True)
analyzer = SentimentIntensityAnalyzer()

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ======================
# FINANCE KEYWORDS BOOST
# ======================
POSITIVE_WORDS = {
    "beats", "surge", "growth", "profit", "upgrade", "strong", "record",
    "bullish", "outperform", "buyback", "expansion"
}

NEGATIVE_WORDS = {
    "miss", "drop", "loss", "downgrade", "weak", "lawsuit",
    "bearish", "decline", "cut", "fraud", "risk"
}

def finance_boost(text):
    text_lower = text.lower()

    score = 0
    for word in POSITIVE_WORDS:
        if word in text_lower:
            score += 0.15

    for word in NEGATIVE_WORDS:
        if word in text_lower:
            score -= 0.15

    return score

# ======================
# GOOGLE NEWS RSS (NO API)
# ======================
@lru_cache(maxsize=256)
def get_news_headlines(ticker, limit=10):
    query = urllib.parse.quote(f"{ticker} stock")

    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)

    headlines = []
    seen = set()

    for entry in feed.entries:
        title = entry.get("title", "").strip()

        # basic dedup (normalized)
        key = title.lower()
        if title and key not in seen:
            seen.add(key)
            headlines.append(title)

        if len(headlines) >= limit:
            break

    return headlines

# ======================
# SENTIMENT SCORING (UPGRADED)
# ======================
def score_sentiment(texts):
    if not texts:
        return {
            "compound": None,
            "sentiment_label": "no_data",
            "sentiment_score": None
        }

    scores = []

    for text in texts:
        base = analyzer.polarity_scores(text)["compound"]
        boost = finance_boost(text)

        final_score = max(min(base + boost, 1), -1)
        scores.append(final_score)

    avg = sum(scores) / len(scores)

    # stronger thresholds
    if avg >= 0.25:
        label = "bullish"
    elif avg <= -0.25:
        label = "bearish"
    else:
        label = "neutral"

    sentiment_score = round((avg + 1) * 50, 1)

    return {
        "compound": round(avg, 4),
        "sentiment_label": label,
        "sentiment_score": sentiment_score
    }

# ======================
# PIPELINE
# ======================
def get_ticker_sentiment(ticker, limit=10):
    headlines = get_news_headlines(ticker, limit)

    result = score_sentiment(headlines)

    return {
        "ticker": ticker.upper(),
        "headline_count": len(headlines),
        **result,
        "headlines": headlines
    }

def rank_tickers_by_sentiment(tickers, limit=10, delay=0.2):
    rows = []

    for ticker in tickers:
        try:
            result = get_ticker_sentiment(ticker, limit)

            rows.append({
                "ticker": result["ticker"],
                "headline_count": result["headline_count"],
                "compound": result["compound"],
                "sentiment_label": result["sentiment_label"],
                "sentiment_score": result["sentiment_score"]
            })

            time.sleep(delay)  # avoid hammering RSS

        except Exception as e:
            rows.append({
                "ticker": ticker.upper(),
                "headline_count": 0,
                "compound": None,
                "sentiment_label": f"error: {type(e).__name__}",
                "sentiment_score": None
            })

    df = pd.DataFrame(rows)
    return df.sort_values(by="compound", ascending=False, na_position="last")


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    tickers = get_nasdaq100_tickers()

    df = rank_tickers_by_sentiment(tickers[:30])  # test smaller batch first
    print(df.head(10))

    df.to_csv("ticker_sentiment_ranking_v2.csv", index=False)