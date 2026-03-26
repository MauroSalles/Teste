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


def buscar_pedido_por_id(pedido_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.id, s.nome AS sabor, p.quantidade, p.data,
                       (p.quantidade * s.preco) AS total
                FROM pedidos p
                JOIN sabores s ON p.sabor_id = s.id
                WHERE p.id = %s
                """,
                (pedido_id,),
            )
            return cursor.fetchone()


def criar_pedido(sabor_id, quantidade):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pedidos (sabor_id, quantidade) VALUES (%s, %s) RETURNING *",
                (sabor_id, quantidade),
            )
            return cursor.fetchone()


def relatorio_vendas():
    """Return sales totals grouped by flavor, ordered by quantity sold descending."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.nome AS sabor,
                       SUM(p.quantidade)             AS total_unidades,
                       SUM(p.quantidade * s.preco)   AS total_receita
                FROM pedidos p
                JOIN sabores s ON p.sabor_id = s.id
                GROUP BY s.id, s.nome
                ORDER BY total_unidades DESC
                """
            )
            return cursor.fetchall()


def total_receita():
    """Return the grand total revenue and total units sold across all orders."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(p.id)                       AS total_pedidos,
                       COALESCE(SUM(p.quantidade), 0)    AS total_unidades,
                       COALESCE(SUM(p.quantidade * s.preco), 0) AS total_receita
                FROM pedidos p
                JOIN sabores s ON p.sabor_id = s.id
                """
            )
            return cursor.fetchone()

