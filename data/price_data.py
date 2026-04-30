import pandas as pd
import requests


def get_price_data(ticker, days=10):
    """
    Fetch historical data from Financial Modeling Prep (no API key needed)
    """
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print(f"❌ Failed {ticker}: {res.status_code}")
            return None

        data = res.json()

        if "historical" not in data:
            print(f"❌ No data for {ticker}")
            return None

        df = pd.DataFrame(data["historical"])

        if df.empty or "close" not in df.columns:
            print(f"❌ Bad data for {ticker}")
            return None

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        return df.tail(days)

    except Exception as e:
        print(f"❌ Error {ticker}: {e}")
        return None


def get_return(ticker, days=5):
    df = get_price_data(ticker, days + 5)

    if df is None or len(df) < 2:
        return None

    df = df.tail(days + 1)

    start = df["close"].iloc[0]
    end = df["close"].iloc[-1]

    return (end - start) / start