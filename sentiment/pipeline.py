from sentiment.finbert_sentiment import score_finbert


def build_sentiment_map(news_dict):
    results = {}

    for ticker, headlines in news_dict.items():
        sentiment = score_finbert(headlines)

        results[ticker] = {
            "sentiment": sentiment,
            "headline_count": len(headlines),
            "headlines": headlines
        }

    return results