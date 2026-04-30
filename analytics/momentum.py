import pandas as pd


def compute_momentum(history_df):
    if history_df.empty:
        return pd.DataFrame()

    history_df["date"] = pd.to_datetime(history_df["date"])

    latest = history_df.sort_values("date").groupby("ticker").tail(1)
    previous = history_df.sort_values("date").groupby("ticker").nth(-2)

    merged = latest.merge(
        previous,
        on="ticker",
        suffixes=("_now", "_prev")
    )

    merged["momentum"] = merged["sentiment_now"] - merged["sentiment_prev"]

    return merged.sort_values("momentum", ascending=False)