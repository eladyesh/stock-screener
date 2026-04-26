def safe(v):
    return v if v is not None else 0


def score_stock(s):
    closes = s["closes"]

    if len(closes) < 60:
        return None

    # -------------------------
    # PRICE BEHAVIOR (stability, not hype)
    # -------------------------
    price_now = closes[-1]
    price_90 = closes[0]

    price_growth = (price_now - price_90) / price_90

    avg_price = sum(closes) / len(closes)
    volatility = sum(
        abs(closes[i] - closes[i - 1]) / closes[i - 1]
        for i in range(1, len(closes))
    ) / len(closes)

    # -------------------------
    # FUNDAMENTALS (REAL INVESTING EDGE)
    # -------------------------
    pe = safe(s.get("pe"))
    revenue_growth = safe(s.get("revenue_growth"))
    margin = safe(s.get("margin"))

    # -------------------------
    # QUALITY SCORING
    # -------------------------

    # Growth (moderate reward)
    growth_score = price_growth * 30

    # Revenue growth (very important)
    revenue_score = revenue_growth * 80 if revenue_growth else 0

    # Profitability
    margin_score = margin * 50 if margin else 0

    # Valuation (penalty if too expensive)
    if pe == 0:
        pe_score = 0
    elif pe < 15:
        pe_score = 20
    elif pe < 25:
        pe_score = 10
    elif pe < 40:
        pe_score = 0
    else:
        pe_score = -20

    # Stability (lower volatility = better for long-term)
    stability_score = -volatility * 40

    # FINAL SCORE
    score = (
        growth_score +
        revenue_score +
        margin_score +
        pe_score +
        stability_score
    )

    s.update({
        "score": score,
        "price_growth": price_growth,
        "volatility": volatility,
        "pe": pe,
        "revenue_growth": revenue_growth,
        "margin": margin
    })

    return score


def score_stocks(stocks):
    results = []

    for s in stocks:
        sc = score_stock(s)
        if sc is not None:
            results.append(s)

    return results