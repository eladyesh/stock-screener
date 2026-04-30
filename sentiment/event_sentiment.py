import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


# ======================
# EVENT DETECTION
# ======================
def detect_event(text):
    t = text.lower()

    if any(k in t for k in ["earnings", "eps", "revenue", "quarter"]):
        return "earnings"

    if any(k in t for k in ["guidance", "forecast", "outlook"]):
        return "guidance"

    if any(k in t for k in ["lawsuit", "sec", "investigation", "fine"]):
        return "legal"

    if any(k in t for k in ["acquire", "merger", "buy", "stake", "deal"]):
        return "ma"

    if any(k in t for k in ["launch", "announces", "unveil", "release"]):
        return "product"

    if any(k in t for k in ["upgrade", "downgrade", "price target"]):
        return "analyst"

    return "general"


# ======================
# EVENT WEIGHTS
# ======================
EVENT_WEIGHTS = {
    "earnings": 1.5,
    "guidance": 1.4,
    "legal": 1.6,
    "ma": 1.3,
    "product": 1.0,
    "analyst": 1.2,
    "general": 0.8
}


# ======================
# SENTIMENT PER HEADLINE
# ======================
def score_headline(text):
    base = analyzer.polarity_scores(text)["compound"]
    event = detect_event(text)
    weight = EVENT_WEIGHTS[event]

    return base * weight, event