"""Customer review model — CRUD for the ``reviews`` table."""

import logging
from backend.database import get_db

logger = logging.getLogger(__name__)


def criar_review(user_id: int, sabor_id: int, rating: int, comentario: str):
    """Insert a new review. Rating must be 1-5."""
    if not 1 <= rating <= 5:
        raise ValueError("rating deve estar entre 1 e 5")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reviews (user_id, sabor_id, rating, comentario)
                VALUES (%s, %s, %s, %s)
                RETURNING id, user_id, sabor_id, rating, comentario, criado_em
                """,
                (user_id, sabor_id, rating, comentario.strip()[:1000]),
            )
            return cur.fetchone()


def listar_reviews_por_sabor(sabor_id: int, limit: int = 20):
    """Return the most recent reviews for a flavour."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.id, r.user_id, u.name AS autor, r.sabor_id,
                       s.nome AS sabor_nome, r.rating, r.comentario, r.criado_em
                  FROM reviews r
                  LEFT JOIN users  u ON u.id = r.user_id
                  LEFT JOIN sabores s ON s.id = r.sabor_id
                 WHERE r.sabor_id = %s
                 ORDER BY r.criado_em DESC
                 LIMIT %s
                """,
                (sabor_id, min(limit, 100)),
            )
            return cur.fetchall()


def media_rating_por_sabor(sabor_id: int):
    """Return average rating and total reviews for a flavour."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ROUND(AVG(rating)::numeric, 2) AS media,
                       COUNT(*) AS total
                  FROM reviews
                 WHERE sabor_id = %s
                """,
                (sabor_id,),
            )
            return cur.fetchone()


def ranking_sabores_por_rating(limit: int = 10):
    """Return flavours ranked by average rating."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, s.nome, s.preco,
                       ROUND(AVG(r.rating)::numeric, 2) AS media_rating,
                       COUNT(r.id) AS total_reviews
                  FROM sabores s
                  LEFT JOIN reviews r ON r.sabor_id = s.id
                 GROUP BY s.id
                 ORDER BY media_rating DESC NULLS LAST, total_reviews DESC
                 LIMIT %s
                """,
                (min(limit, 50),),
            )
            return cur.fetchall()
