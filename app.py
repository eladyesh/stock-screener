from flask import Flask, jsonify, request, render_template
import time

from config import TICKERS, NEWS_LIMIT
from services.analysis import run_analysis

app = Flask(__name__)


# ======================
# DASHBOARD PAGE
# ======================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ======================
# API (frontend polls this)
# ======================
@app.route("/signals")
def signals():

    tickers = request.args.get("tickers")

    if tickers:
        tickers = tickers.upper().split(",")
    else:
        tickers = TICKERS

    data = run_analysis(tickers, NEWS_LIMIT)

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)