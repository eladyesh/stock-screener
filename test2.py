import feedparser
import pandas as pd
import requests
import nltk
import yfinance as yf
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

NEWS_API_KEY = os.getenv("NEWS_API_KEY") or "98ada878b35141fa872c7a7839e220b7"

nltk.download("vader_lexicon", quiet=True)
analyzer = SentimentIntensityAnalyzer()

# ======================
# ORIGINAL TICKER FUNCTIONS (UNCHANGED)
# ======================
def get_nasdaq100_tickers():
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    tables = pd.read_html(res.text)
    for table in tables:
        if "Ticker" in table.columns:
            return table["Ticker"].dropna().astype(str).tolist()

    return []


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    df = pd.read_html(res.text)[0]
    tickers = df["Symbol"].dropna().astype(str).tolist()
    return [t.replace(".", "-") for t in tickers]


def get_nasdaq_stocks():
    url = "https://datahub.io/core/nasdaq-listings/r/nasdaq-listed-symbols.csv"
    df = pd.read_csv(url)
    df.to_csv("nasdaq_listings.csv", index=False)
    return df["Symbol"].dropna().astype(str).unique().tolist()

# ======================
# NEW: NEWSAPI HEADLINES
# ======================
def get_news_headlines(ticker, limit=10):
    query = urllib.parse.quote(ticker)

    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)

    headlines = []
    for entry in feed.entries[:limit]:
        title = entry.get("title", "").strip()
        if title:
            headlines.append(title)

    return headlines

# ======================
# SENTIMENT (UNCHANGED)
# ======================
def score_sentiment(texts):
    if not texts:
        return {
            "compound": None,
            "sentiment_label": "no_data",
            "sentiment_score": None
        }

    scores = [analyzer.polarity_scores(text)["compound"] for text in texts]
    avg_compound = sum(scores) / len(scores)

    if avg_compound >= 0.20:
        label = "high_positive"
    elif avg_compound <= -0.20:
        label = "negative"
    else:
        label = "neutral"

    sentiment_score = round((avg_compound + 1) * 50, 1)

    return {
        "compound": round(avg_compound, 4),
        "sentiment_label": label,
        "sentiment_score": sentiment_score
    }

# ======================
# PIPELINE (UNCHANGED)
# ======================
def get_ticker_sentiment(ticker, limit=10):
    headlines = get_news_headlines(ticker, limit=limit)
    result = score_sentiment(headlines)

    return {
        "ticker": ticker.upper(),
        "headline_count": len(headlines),
        **result,
        "headlines": headlines
    }


def rank_tickers_by_sentiment(tickers, limit=10):
    rows = []

    for ticker in tickers:
        try:
            result = get_ticker_sentiment(ticker, limit=limit)
            print(result)

            rows.append({
                "ticker": result["ticker"],
                "headline_count": result["headline_count"],
                "compound": result["compound"],
                "sentiment_label": result["sentiment_label"],
                "sentiment_score": result["sentiment_score"]
            })

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

    # score first 25 tickers
    df = rank_tickers_by_sentiment(tickers)
    print(df.head(10))

    df.to_csv("ticker_sentiment_ranking.csv", index=False)