import asyncio

from config import TICKERS, NEWS_LIMIT
from news.async_news import get_all_news
from sentiment.pipeline import build_sentiment_map
from output.reporter import generate_report


def run():

    print("Fetching news...")
    news = asyncio.run(get_all_news(TICKERS, NEWS_LIMIT))

    print("Building sentiment map...")
    sentiment_map = build_sentiment_map(news)

    print("Generating signals...\n")
    df = generate_report(sentiment_map)

    print(df)

    df.to_csv("signals_output.csv", index=False)


if __name__ == "__main__":
    run()