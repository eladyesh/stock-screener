def compute_signal(event_scores):
    """
    event_scores example:
    {
        "earnings": 0.6,
        "legal": -0.4,
        "analyst": 0.3
    }
    """

    earnings = event_scores.get("earnings", 0)
    legal = event_scores.get("legal", 0)
    analyst = event_scores.get("analyst", 0)
    product = event_scores.get("product", 0)

    # ======================
    # SIGNAL LOGIC
    # ======================

    score = (
        earnings * 1.5 +
        analyst * 1.2 +
        product * 0.8 +
        legal * 1.8  # risk penalty
    )

    # ======================
    # CONFIDENCE (IMPORTANT)
    # ======================

    confidence = min(1.0, abs(score))

    # ======================
    # DECISION RULES
    # ======================

    if score > 0.5 and legal > -0.3:
        signal = "BUY"

    elif score < -0.5 or legal < -0.5:
        signal = "SELL"

    else:
        signal = "HOLD"

    return {
        "score": round(score, 3),
        "confidence": round(confidence, 3),
        "signal": signal
    }