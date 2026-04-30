from collections import defaultdict
from sentiment.event_sentiment import score_headline


def build_sentiment_map(news_dict):
    results = {}

    for ticker, headlines in news_dict.items():

        weighted_scores = []
        event_scores = defaultdict(list)

        for h in headlines:
            score, event = score_headline(h)

            weighted_scores.append(score)
            event_scores[event].append(score)

        overall = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0

        event_summary = {}
        for event, scores in event_scores.items():
            event_summary[event] = sum(scores) / len(scores)

        results[ticker] = {
            "sentiment": overall,
            "events": event_summary,
            "headline_count": len(headlines)
        }

    return results