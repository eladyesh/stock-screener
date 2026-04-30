
import pandas as pd
import requests
import io


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_nasdaq100_tickers():
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"

    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()

    tables = pd.read_html(res.text)

    for table in tables:
        if "Ticker" in table.columns:
            return table["Ticker"].tolist()

    return []

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()

    df = pd.read_html(res.text)[0]

    tickers = df["Symbol"].tolist()
    tickers = [t.replace(".", "-") for t in tickers]

    return tickers


def get_nasdaq_stocks():
    url = "https://datahub.io/core/nasdaq-listings/r/nasdaq-listed-symbols.csv"
    df = pd.read_csv(url)

    df.to_csv("nasdaq_listings.csv", index=False)

    # Example: just symbols
    symbols = df["Symbol"].dropna().unique().tolist()

    return symbols

if __name__ == "__main__":
    print(get_nasdaq_stocks())
    print(get_sp500_tickers())
    print(get_nasdaq100_tickers())
