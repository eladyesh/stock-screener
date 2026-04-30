import asyncio

from cache.memory import get_cache, set_cache
from news.async_news import get_all_news
from sentiment.pipeline import build_sentiment_map
from signals.engine import compute_signal


def run_analysis(tickers, limit):

    cache_key = ",".join(tickers)

    cached = get_cache(cache_key)
    if cached:
        return cached

    news = asyncio.run(get_all_news(tickers, limit))
    sentiment_map = build_sentiment_map(news)

    results = {}

    for ticker, data in sentiment_map.items():
        signal = compute_signal(data["events"])

        results[ticker] = {
            "signal": signal["signal"],
            "score": signal["score"],
            "confidence": signal["confidence"],
            "sentiment": data["sentiment"]
        }

    set_cache(cache_key, results)

    return results