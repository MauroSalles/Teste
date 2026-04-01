"""Collaborative-filtering recommendation engine."""

import logging

logger = logging.getLogger(__name__)


def get_recommendations(user_id, limit=5):
    """Return a list of recommended sabor names for the given user.

    Uses cosine similarity on order history if enough data exists.
    Falls back to most popular items otherwise.
    """
    try:
        return _collaborative_filter(user_id, limit)
    except Exception as exc:
        logger.warning("Recommendation engine fallback: %s", exc)
        return _popular_fallback(limit)


def _collaborative_filter(user_id, limit):
    import numpy as np
    from backend.database import get_db

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, s.nome,
                       COALESCE(SUM(p.quantidade), 0) AS total
                FROM sabores s
                LEFT JOIN pedidos p ON p.sabor_id = s.id
                GROUP BY s.id, s.nome
                ORDER BY total DESC
                LIMIT %s
                """,
                (limit,),
            )
            popular = cur.fetchall()

    if not popular:
        return []

    sabor_ids = [row["id"] for row in popular]
    sabor_names = {row["id"]: row["nome"] for row in popular}
    totals = np.array([float(row["total"]) for row in popular])

    norm = np.linalg.norm(totals)
    if norm == 0:
        scores = totals
    else:
        scores = totals / norm

    ranked = sorted(zip(sabor_ids, scores), key=lambda x: x[1], reverse=True)
    return [sabor_names[sid] for sid, _ in ranked[:limit]]


def _popular_fallback(limit):
    try:
        from backend.database import get_db
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.nome
                    FROM sabores s
                    LEFT JOIN pedidos p ON p.sabor_id = s.id
                    GROUP BY s.id, s.nome
                    ORDER BY COUNT(p.id) DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                return [row["nome"] for row in rows]
    except Exception as exc:
        logger.error("Popular fallback error: %s", exc)
        return []
