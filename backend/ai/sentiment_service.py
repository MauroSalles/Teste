"""Sentiment analysis service."""

import logging
import re

logger = logging.getLogger(__name__)

_POSITIVE_WORDS = {
    "ótimo", "excelente", "maravilhoso", "delicioso", "incrível", "perfeito",
    "adorei", "amei", "gostei", "bom", "boa", "lindo", "linda", "top",
    "recomendo", "nota 10", "parabéns", "show", "sensacional",
}

_NEGATIVE_WORDS = {
    "ruim", "péssimo", "horrível", "terrível", "detestei", "odiei", "não gostei",
    "decepcionante", "fraco", "fraca", "nojento", "nojenta", "pior",
    "problema", "demora", "demorou", "errado", "errada",
}


def analyze_sentiment(text):
    """Analyze text sentiment. Returns dict with sentiment and score."""
    if not text or not isinstance(text, str):
        return {"sentiment": "neutral", "score": 0.0}

    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        score = blob.sentiment.polarity
        if score > 0.1:
            sentiment = "positive"
        elif score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return {"sentiment": sentiment, "score": round(score, 4)}
    except ImportError:
        pass

    return _keyword_sentiment(text)


def _keyword_sentiment(text):
    """Simple keyword-based fallback sentiment analysis."""
    lower = text.lower()
    tokens = set(re.findall(r"\w+", lower))

    pos_hits = len(tokens & _POSITIVE_WORDS)
    neg_hits = len(tokens & _NEGATIVE_WORDS)

    total = pos_hits + neg_hits
    if total == 0:
        return {"sentiment": "neutral", "score": 0.0}

    score = (pos_hits - neg_hits) / total
    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {"sentiment": sentiment, "score": round(score, 4)}
