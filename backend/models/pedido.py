from backend.database import get_db


def listar_pedidos():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.id, s.nome AS sabor, p.quantidade, p.data
                FROM pedidos p
                JOIN sabores s ON p.sabor_id = s.id
                ORDER BY p.data DESC
                """
            )
            return cursor.fetchall()


def criar_pedido(sabor_id, quantidade):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pedidos (sabor_id, quantidade) VALUES (%s, %s) RETURNING *",
                (sabor_id, quantidade),
            )
            return cursor.fetchone()


def relatorio_vendas(periodo: str = "diario") -> list:
    """Aggregate sales totals grouped by the requested period.

    periodo: 'diario' | 'semanal' | 'mensal'
    Returns list of {periodo, total_pedidos, total_itens, receita_total}.
    """
    _TRUNCATIONS = {
        "diario": "day",
        "semanal": "week",
        "mensal": "month",
    }
    trunc = _TRUNCATIONS.get(periodo, "day")

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    DATE_TRUNC(%s, p.data)          AS periodo,
                    COUNT(p.id)                     AS total_pedidos,
                    SUM(p.quantidade)               AS total_itens,
                    SUM(p.quantidade * s.preco)     AS receita_total
                FROM pedidos p
                JOIN sabores s ON s.id = p.sabor_id
                GROUP BY DATE_TRUNC(%s, p.data)
                ORDER BY periodo DESC
                LIMIT 30
                """,
                (trunc, trunc),
            )
            return cursor.fetchall()


def sabores_populares(limit: int = 5) -> list:
    """Top N flavors by order count."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id, s.nome, s.preco,
                       COUNT(p.id)       AS total_pedidos,
                       SUM(p.quantidade) AS total_itens
                FROM sabores s
                LEFT JOIN pedidos p ON p.sabor_id = s.id
                GROUP BY s.id, s.nome, s.preco
                ORDER BY total_pedidos DESC NULLS LAST
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()

