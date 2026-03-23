from backend.database import get_db


def ver_estoque():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id, s.nome, COALESCE(e.quantidade, 0) AS quantidade
                FROM sabores s
                LEFT JOIN estoque e ON e.sabor_id = s.id
                ORDER BY s.nome
                """
            )
            return cursor.fetchall()


def definir_estoque(sabor_id, quantidade):
    """Insert or update the stock quantity for a given flavor."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO estoque (sabor_id, quantidade)
                VALUES (%s, %s)
                ON CONFLICT (sabor_id)
                DO UPDATE SET quantidade = EXCLUDED.quantidade
                RETURNING *
                """,
                (sabor_id, quantidade),
            )
            return cursor.fetchone()


def ajustar_estoque(sabor_id, delta):
    """Add (positive delta) or subtract (negative delta) from current stock.
    The quantity is clamped to zero — it will never go negative.
    Returns the updated estoque row."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO estoque (sabor_id, quantidade)
                VALUES (%s, GREATEST(0, %s))
                ON CONFLICT (sabor_id)
                DO UPDATE SET quantidade = GREATEST(0, estoque.quantidade + EXCLUDED.quantidade)
                RETURNING *
                """,
                (sabor_id, delta),
            )
            return cursor.fetchone()


def obter_estoque(sabor_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT quantidade FROM estoque WHERE sabor_id = %s",
                (sabor_id,),
            )
            row = cursor.fetchone()
            return int(row["quantidade"]) if row else 0
