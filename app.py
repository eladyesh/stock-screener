from flask import Flask, jsonify, render_template_string
import requests
import numpy as np
import pandas as pd
import threading
import time

app = Flask(__name__)

# =========================
# CONFIG
# =========================

API_KEY = "d7mvkf9r01qngrvpjeg0d7mvkf9r01qngrvpjegg"  # <-- replace with your key

HEADERS = {"User-Agent": "Mozilla/5.0"}

CACHE = []
MAX_TICKERS = 100
CACHE_TTL = 60 * 15  # 15 min

# S&P 500 universe (simple + stable)
def get_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = requests.get(url, headers=HEADERS).text
    table = pd.read_html(html)[0]
    return table["Symbol"].tolist()[:MAX_TICKERS]

TICKERS = get_sp500()

# =========================
# FINNHUB HELPERS
# =========================

def finnhub_candles(symbol):
    try:
        url = f"https://finnhub.io/api/v1/stock/candle"
        params = {
            "symbol": symbol,
            "resolution": "D",
            "from": int(time.time()) - 60 * 60 * 24 * 180,
            "to": int(time.time()),
            "token": API_KEY
        }

        r = requests.get(url, params=params)
        data = r.json()

        if data.get("s") != "ok":
            return None

        df = pd.DataFrame({
            "close": data["c"]
        })

        return df

    except:
        return None


def finnhub_sentiment(symbol):
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={API_KEY}"
        news = requests.get(url).json()

        scores = []
        for n in news[:20]:
            title = n.get("headline", "")
            if "earnings" in title.lower():
                scores.append(0.2)
            elif "upgrade" in title.lower():
                scores.append(0.3)
            elif "downgrade" in title.lower():
                scores.append(-0.3)
            else:
                scores.append(0)

        return np.mean(scores) if scores else 0

    except:
        return 0


def finnhub_metrics(symbol):
    try:
        url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={API_KEY}"
        data = requests.get(url).json().get("metric", {})

        score = 0

        pe = data.get("peBasicExclExtraTTM")
        fpe = data.get("peNormalizedAnnual")
        debt = data.get("totalDebt/totalEquityAnnual")
        growth = data.get("revenueGrowthTTMYoy")

        if pe and pe < 20:
            score += 1
        if fpe and fpe < 18:
            score += 1
        if debt and debt < 100:
            score += 1
        if growth and growth > 0.1:
            score += 1

        return score

    except:
        return 0


# =========================
# TECHNICALS
# =========================

def technical_score(df):
    try:
        closes = df["close"]

        sma20 = closes.rolling(20).mean()
        sma50 = closes.rolling(50).mean()

        if len(closes) < 60:
            return 0

        score = 0

        if sma20.iloc[-1] > sma50.iloc[-1]:
            score += 1
        else:
            score -= 1

        momentum = closes.pct_change().tail(5).mean()

        score += 1 if momentum > 0 else -1

        return score

    except:
        return 0


# =========================
# PRICE SCORE
# =========================

def price_score(df):
    try:
        r = df["close"].pct_change()

        score = 0
        if r.tail(10).mean() > 0:
            score += 1
        else:
            score -= 1

        return score
    except:
        return 0


# =========================
# MASTER SCORER
# =========================

def score_stock(symbol):
    try:
        df = finnhub_candles(symbol)
        if df is None or df.empty:
            return None

        sentiment = finnhub_sentiment(symbol)
        tech = technical_score(df)
        price = price_score(df)
        fund = finnhub_metrics(symbol)

        score = (
            sentiment * 2 +
            tech * 2 +
            price * 1.5 +
            fund * 3
        )

        return {
            "ticker": symbol,
            "score": round(score, 2),
            "sentiment": round(sentiment, 2),
            "technical": tech,
            "price": price,
            "fundamentals": fund
        }

    except:
        return None


# =========================
# SCAN ENGINE
# =========================

def run_scan():
    global CACHE

    results = []

    for i, t in enumerate(TICKERS):
        print(f"Scanning {t} ({i+1}/{len(TICKERS)})")

        r = score_stock(t)
        if r:
            results.append(r)

        time.sleep(0.1)  # important for rate limits

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    CACHE = results[:10]


# =========================
# BACKGROUND WORKER
# =========================

def worker():
    while True:
        run_scan()
        time.sleep(CACHE_TTL)

threading.Thread(target=worker, daemon=True).start()


# =========================
# MOBILE UI
# =========================

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stock Screener</title>

<style>
body { background:#0f1115; color:white; font-family:Arial; margin:0; }
.header { padding:15px; text-align:center; background:#1c1f26; font-size:20px; }
.card { margin:10px; padding:15px; background:#1c1f26; border-radius:12px; }
.t { font-size:18px; font-weight:bold; }
.s { color:#4ade80; margin-top:5px; }
.small { color:#aaa; font-size:12px; }
button {
  width:90%; margin:10px auto; display:block;
  padding:12px; border:none; border-radius:10px;
  background:#2d6cdf; color:white; font-size:16px;
}
</style>
</head>

<body>

<div class="header">📊 Finnhub Stock Screener</div>

<button onclick="load()">🔄 Refresh</button>

<div id="out"></div>

<script>
async function load(){
  let r = await fetch("/top10");
  let data = await r.json();

  let html = "";
  data.forEach(s => {
    html += `
    <div class="card">
      <div class="t">${s.ticker}</div>
      <div class="s">Score: ${s.score}</div>
      <div class="small">
        Sentiment: ${s.sentiment} | Tech: ${s.technical} | Price: ${s.price} | Fund: ${s.fundamentals}
      </div>
    </div>`;
  });

  document.getElementById("out").innerHTML = html;
}

load();
setInterval(load, 60000);
</script>

</body>
</html>
"""


# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return HTML

@app.route("/top10")
def top10():
    return jsonify(CACHE)


# =========================
# START
# =========================

if __name__ == "__main__":
    run_scan()
    app.run(host="0.0.0.0", port=5000, debug=True)