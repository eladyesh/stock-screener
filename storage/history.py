import pandas as pd
import os
from datetime import datetime

FILE = "sentiment_history.csv"


def save_snapshot(df):
    df = df.copy()
    df["date"] = datetime.utcnow().strftime("%Y-%m-%d")

    if os.path.exists(FILE):
        old = pd.read_csv(FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(FILE, index=False)


def load_history():
    if not os.path.exists(FILE):
        return pd.DataFrame()

    return pd.read_csv(FILE)