from flask import Flask, jsonify
import os
import requests
import pandas as pd
import numpy as np
import threading
import time
import traceback

app = Flask(__name__)

API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1"

CACHE = {
    "top10": [],
    "last_update": "never"
}

# -----------------------------
# SAFE REQUEST WRAPPER
# -----------------------------
def safe_get(url):
    try:
        r = requests.get(url, timeout=6)
        data = r.json()

        if isinstance(data, dict) and "error" in data:
            print("API ERROR:", data["error"])
            return None

        return data
    except Exception as e:
        print("REQUEST ERROR:", e)
        return None


# -----------------------------
# UNIVERSE (SAFE FALLBACK)
# -----------------------------
SAMPLE_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "TSLA", "AVGO", "AMD", "NFLX",
    "JPM", "V", "MA", "UNH", "HD",
    "BAC", "XOM", "COST", "WMT", "LLY"
]


# -----------------------------
# FUNDAMENTALS
# -----------------------------
def get_fundamentals(symbol):
    url = f"{BASE_URL}/stock/metric?symbol={symbol}&metric=all&token={API_KEY}"
    data = safe_get(url)

    if not data:
        return {}

    m = data.get("metric", {})

    return {
        "pe": m.get("peBasicExclExtraTTM"),
        "forward_pe": m.get("peNormalizedAnnual"),
        "margin": m.get("ebitdaMarginTTM"),
        "growth": m.get("revenueGrowthTTMYoy"),
    }


# -----------------------------
# SENTIMENT
# -----------------------------
def get_sentiment(symbol):
    url = f"{BASE_URL}/news-sentiment?symbol={symbol}&token={API_KEY}"
    data = safe_get(url)

    if not data:
        return 0

    return data.get("buzz", {}).get("sentimentScore", 0)


# -----------------------------
# PRICE DATA
# -----------------------------
def get_price(symbol):
    url = f"{BASE_URL}/stock/candle?symbol={symbol}&resolution=D&count=80&token={API_KEY}"
    data = safe_get(url)

    if not data or data.get("s") != "ok":
        return None

    return pd.Series(data["c"])


# -----------------------------
# INDICATORS
# -----------------------------
def sma(series, window=20):
    return series.rolling(window).mean()


def rsi(series, period=14):
    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


def macd(series):
    return series.ewm(span=12, adjust=False).mean() - series.ewm(span=26, adjust=False).mean()


# -----------------------------
# SCORING ENGINE
# -----------------------------
def score_stock(symbol):
    try:
        f = get_fundamentals(symbol)
        sentiment = get_sentiment(symbol)
        price = get_price(symbol)

        if price is None:
            return None

        df = pd.DataFrame({"close": price})

        df["rsi"] = rsi(df["close"])
        df["sma"] = sma(df["close"])
        df["macd"] = macd(df["close"])

        last = df.iloc[-1]

        score = 0

        # Fundamentals
        if f.get("pe"):
            score += max(0, 10 - f["pe"])

        if f.get("forward_pe"):
            score += max(0, 10 - f["forward_pe"])

        if f.get("margin"):
            score += f["margin"] * 10

        if f.get("growth"):
            score += f["growth"] * 10

        # Sentiment
        score += sentiment * 10

        # Technicals
        if not np.isnan(last["rsi"]):
            score += (50 - abs(50 - last["rsi"])) / 10

        if not np.isnan(last["macd"]) and last["macd"] > 0:
            score += 2

        if not np.isnan(last["sma"]) and last["close"] > last["sma"]:
            score += 2

        return {
            "symbol": symbol,
            "score": round(score, 2)
        }

    except Exception:
        print("Score error:", symbol)
        traceback.print_exc()
        return None


# -----------------------------
# BACKGROUND ENGINE
# -----------------------------
def recompute():
    print("Recomputing stocks...")

    results = []

    for sym in SAMPLE_UNIVERSE:
        r = score_stock(sym)
        if r:
            results.append(r)
            print("OK:", sym, r["score"])
        else:
            print("SKIP:", sym)

    results.sort(key=lambda x: x["score"], reverse=True)

    CACHE["top10"] = results[:10]
    CACHE["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")

    print("DONE:", CACHE["last_update"])


def background_loop():
    while True:
        recompute()
        time.sleep(300)  # every 5 min


# -----------------------------
# STARTUP FIX (CRITICAL)
# -----------------------------
recompute()  # run once immediately
threading.Thread(target=background_loop, daemon=True).start()


# -----------------------------
# API
# -----------------------------
@app.route("/top10")
def top10():
    return jsonify(CACHE)


# -----------------------------
# UI
# -----------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial; padding: 20px; }
            button { padding: 12px; font-size: 16px; margin: 5px; }
            pre { background: #111; color: #0f0; padding: 10px; }
        </style>
    </head>
    <body>

        <h2>📊 Stock Screener</h2>

        <button onclick="load()">Load Top 10</button>

        <pre id="out">Waiting...</pre>

        <script>
        async function load(){
            const out = document.getElementById('out');
            out.innerText = "Loading...";

            const res = await fetch('/top10');
            const data = await res.json();

            out.innerText = JSON.stringify(data, null, 2);
        }
        </script>

    </body>
    </html>
    """


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)