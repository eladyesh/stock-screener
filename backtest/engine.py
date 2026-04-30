import pandas as pd
from data.price_data import get_return


def backtest(sentiment_map, days=5):
    rows = []

    for ticker, data in sentiment_map.items():
        ret = get_return(ticker, days)

        if ret is None:
            continue

        rows.append({
            "ticker": ticker,
            "sentiment": data["sentiment"],
            "future_return": ret
        })

    df = pd.DataFrame(rows)

    if df.empty:
        print("No data")
        return df

    correlation = df["sentiment"].corr(df["future_return"])
    print("Correlation:", correlation)

    return df