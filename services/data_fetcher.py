import requests
import time
from config import Config
from utils.symbols import SYMBOLS

BASE_URL = "https://finnhub.io/api/v1"

def fetch_candles(symbol):
    now = int(time.time())
    past = now - (60 * 60 * 24 * 90)

    res = requests.get(f"{BASE_URL}/stock/candle", params={
        "symbol": symbol,
        "resolution": "D",
        "from": past,
        "to": now,
        "token": Config.FINNHUB_API_KEY
    })

    return res.json()


def fetch_fundamentals(symbol):
    res = requests.get(f"{BASE_URL}/stock/metric", params={
        "symbol": symbol,
        "metric": "all",
        "token": Config.FINNHUB_API_KEY
    })

    return res.json()


def get_market_data():
    stocks = []

    for symbol in SYMBOLS:
        candles = fetch_candles(symbol)
        fundamentals = fetch_fundamentals(symbol)

        if candles.get("s") != "ok":
            continue

        metrics = fundamentals.get("metric", {})

        stocks.append({
            "symbol": symbol,
            "closes": candles["c"],

            # fundamentals
            "pe": metrics.get("peNormalizedAnnual"),
            "revenue_growth": metrics.get("revenueGrowthTTM"),
            "net_margin": metrics.get("netProfitMarginTTM")
        })

    return stocks