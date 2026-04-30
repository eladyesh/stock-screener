import asyncio
import pandas as pd

from config import TICKERS, NEWS_LIMIT
from news.async_news import get_all_news
from sentiment.pipeline import build_sentiment_map


def run():
    print("Fetching news...")
    news = asyncio.run(get_all_news(TICKERS, NEWS_LIMIT))

    print("Scoring sentiment...")
    sentiment_map = build_sentiment_map(news)

    rows = []

    for ticker, data in sentiment_map.items():
        rows.append({
            "ticker": ticker,
            "sentiment": data["sentiment"],
            "headline_count": data["headline_count"]
        })

    df = pd.DataFrame(rows)

    if df.empty:
        print("No data")
        return

    df = df.sort_values("sentiment", ascending=False)

    print("\nTop sentiment stocks:")
    print(df.head(10))

    df.to_csv("sentiment_ranking.csv", index=False)


if __name__ == "__main__":
    run()