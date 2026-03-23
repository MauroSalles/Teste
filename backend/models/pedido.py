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

