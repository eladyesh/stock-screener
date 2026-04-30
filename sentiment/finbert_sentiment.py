from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download("vader_lexicon", quiet=True)

analyzer = SentimentIntensityAnalyzer()

POSITIVE = {"beats", "surge", "growth", "profit", "upgrade", "strong"}
NEGATIVE = {"miss", "drop", "loss", "downgrade", "weak", "lawsuit"}


def score_finbert(headlines):  # keep same name for compatibility
    if not headlines:
        return 0.0

    scores = []

    for text in headlines:
        base = analyzer.polarity_scores(text)["compound"]

        boost = 0
        t = text.lower()

        for w in POSITIVE:
            if w in t:
                boost += 0.15

        for w in NEGATIVE:
            if w in t:
                boost -= 0.15

        final = max(min(base + boost, 1), -1)
        scores.append(final)

    return sum(scores) / len(scores)