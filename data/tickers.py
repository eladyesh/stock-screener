import requests
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_nasdaq100_tickers():
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    from io import StringIO
    tables = pd.read_html(StringIO(res.text))
    for table in tables:
        if "Ticker" in table.columns:
            return table["Ticker"].dropna().astype(str).tolist()

    return []


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    df = pd.read_html(res.text)[0]
    tickers = df["Symbol"].dropna().astype(str).tolist()
    return [t.replace(".", "-") for t in tickers]


def get_nasdaq_stocks():
    url = "https://datahub.io/core/nasdaq-listings/r/nasdaq-listed-symbols.csv"
    df = pd.read_csv(url)
    df.to_csv("nasdaq_listings.csv", index=False)
    return df["Symbol"].dropna().astype(str).unique().tolist()
