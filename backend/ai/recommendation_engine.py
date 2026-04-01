import logging
from backend.database import get_db

logger = logging.getLogger(__name__)


def get_popular_flavors(limit: int = 5) -> list:
    """Return the most ordered flavors based on order history."""
    sql = """
        SELECT s.id, s.nome, s.preco, SUM(p.quantidade) AS total_pedidos
        FROM pedidos p
        JOIN sabores s ON s.id = p.sabor_id
        GROUP BY s.id, s.nome, s.preco
        ORDER BY total_pedidos DESC
        LIMIT %s
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (limit,))
                rows = cur.fetchall()
                return [dict(r) for r in rows]
    except Exception as exc:
        logger.error("get_popular_flavors error: %s", exc)
        return []


def get_recommendations(user_id: int = None, limit: int = 3) -> list:
    """Return flavor recommendations based on global popularity (simple frequency-based)."""
    return get_popular_flavors(limit)
