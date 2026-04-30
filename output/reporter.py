import pandas as pd
from signals.engine import compute_signal


def generate_report(sentiment_map):
    rows = []

    for ticker, data in sentiment_map.items():

        signal_data = compute_signal(data["events"])

        rows.append({
            "ticker": ticker,
            "signal": signal_data["signal"],
            "score": signal_data["score"],
            "confidence": signal_data["confidence"],
            "sentiment": data["sentiment"],
            "headlines": data["headline_count"]
        })

    df = pd.DataFrame(rows)

    return df.sort_values(["score"], ascending=False)