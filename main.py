import asyncio
import pandas as pd

from config import TICKERS, NEWS_LIMIT
from news.async_news import get_all_news
from sentiment.pipeline import build_sentiment_map
from storage.history import save_snapshot, load_history
from analytics.momentum import compute_momentum


def run():
    print("Fetching news...")
    news = asyncio.run(get_all_news(TICKERS, NEWS_LIMIT))

    print("Scoring sentiment...")
    sentiment_map = build_sentiment_map(news)

    # build dataframe
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

    print("\n📊 Today's sentiment:")
    print(df.sort_values("sentiment", ascending=False))
    save_snapshot(df)
    history = load_history()
    momentum = compute_momentum(history)

    if not momentum.empty:
        print("\n🚀 Sentiment momentum:")
        print(momentum[["ticker", "momentum"]].head(10))

    return df


if __name__ == "__main__":
    run()