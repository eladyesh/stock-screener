from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

API_KEY = "INU55O0DKFYMA25L"

HTML = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mini Trading Terminal</title>

<style>
body { font-family: Arial; background:#0f0f0f; color:#eee; text-align:center; margin:0; }
input, button { padding:10px; margin:5px; font-size:16px; border-radius:8px; border:none; }
button { background:#1e88e5; color:white; }
.card { background:#1c1c1c; margin:15px; padding:15px; border-radius:12px; }
.small { font-size:12px; color:#aaa; }
.row { display:flex; justify-content:center; flex-wrap:wrap; }
</style>
</head>

<body>

<h2>📊 Mini Trading Terminal</h2>

<input id="symbol" placeholder="Enter ticker (AAPL)">
<button onclick="loadStock()">Search</button>

<div class="card" id="result" style="display:none;"></div>

<div class="card">
<h3>⭐ Watchlist</h3>
<div id="watchlist"></div>
</div>

<script>
let watchlist = JSON.parse(localStorage.getItem("watchlist") || "[]");

function saveWatchlist(){
    localStorage.setItem("watchlist", JSON.stringify(watchlist));
    renderWatchlist();
}

function addToWatch(symbol){
    if(!watchlist.includes(symbol)){
        watchlist.push(symbol);
        saveWatchlist();
    }
}

function renderWatchlist(){
    let html = "";
    watchlist.forEach(s => {
        html += `<p onclick="quickLoad('${s}')">📌 ${s}</p>`;
    });
    document.getElementById("watchlist").innerHTML = html;
}

function quickLoad(s){
    document.getElementById("symbol").value = s;
    loadStock();
}

async function loadStock(){
    let symbol = document.getElementById("symbol").value;

    let res = await fetch("/stock?symbol=" + symbol);
    let data = await res.json();

    let html = `
        <h3>${data.symbol}</h3>
        <p>💰 Price: $${data.price}</p>
        <p>📈 Open: ${data.open}</p>
        <p>📉 High: ${data.high}</p>
        <p>📉 Low: ${data.low}</p>
        <p>📊 Volume: ${data.volume}</p>

        <button onclick="addToWatch('${data.symbol}')">Add to Watchlist ⭐</button>

        <h4>📈 Simple Chart</h4>
        <div>${data.chart}</div>
    `;

    document.getElementById("result").style.display = "block";
    document.getElementById("result").innerHTML = html;
}

renderWatchlist();
</script>

</body>
</html>
"""

# -------- DATA -------- #

def get_stock(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }

    r = requests.get(url, params=params)
    data = r.json().get("Global Quote", {})

    price = float(data.get("05. price", 0) or 0)

    # fake mini chart (since free API doesn't give intraday easily)
    chart = simple_chart(price)

    return {
        "symbol": symbol,
        "price": data.get("05. price"),
        "open": data.get("02. open"),
        "high": data.get("03. high"),
        "low": data.get("04. low"),
        "volume": data.get("06. volume"),
        "chart": chart
    }

def simple_chart(price):
    # tiny visual bar chart (no extra APIs needed)
    bars = ""
    for i in range(10):
        height = max(5, (price % 10) * 5 + i * 2)
        bars += f"<div style='display:inline-block;width:6px;height:{height}px;background:#1e88e5;margin:1px'></div>"
    return bars

# -------- ROUTES -------- #

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/stock")
def stock():
    symbol = request.args.get("symbol", "").upper()
    return jsonify(get_stock(symbol))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)