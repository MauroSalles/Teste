import re

_POSITIVE_WORDS = {
    "ótimo", "otimo", "excelente", "delicioso", "deliciosa", "maravilhoso", "maravilhosa",
    "incrível", "incrivel", "perfeito", "perfeita", "adorei", "amei", "gostei", "bom", "boa",
    "lindo", "linda", "feliz", "satisfeito", "satisfeita", "recomendo", "rápido",
    "rapido", "gostoso", "gostosa", "saboroso", "saborosa", "top", "show", "parabéns",
    "parabens", "obrigado", "obrigada", "gratidão", "gratidao", "fantástico", "fantastico",
}

_NEGATIVE_WORDS = {
    "ruim", "péssimo", "pessimo", "horrível", "horrivel", "detestei", "odiei", "não gostei",
    "nao gostei", "insatisfeito", "insatisfeita", "decepcionante", "decepcao", "decepção",
    "lento", "demorado", "frio", "estragado", "estragada", "sujo", "suja", "caro", "cara",
    "terrível", "terrivel", "desagradável", "desagradavel", "problema", "erro", "falha",
    "reclamação", "reclamacao", "cancelar", "devolver", "reembolso",
}


def analyze_sentiment(text: str) -> dict:
    """Keyword-based sentiment analysis in Portuguese."""
    if not text:
        return {"sentiment": "neutro", "score": 0.0}

    words = re.findall(r"\b\w+\b", text.lower())
    pos_count = sum(1 for w in words if w in _POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in _NEGATIVE_WORDS)

    total = pos_count + neg_count
    if total == 0:
        return {"sentiment": "neutro", "score": 0.0}

    score = (pos_count - neg_count) / total
    if score > 0.2:
        sentiment = "positivo"
    elif score < -0.2:
        sentiment = "negativo"
    else:
        sentiment = "neutro"

    return {"sentiment": sentiment, "score": round(score, 4)}
