from backend.database import get_connection


def listar_pedidos():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT p.id, s.nome AS sabor, p.quantidade, p.data
                FROM pedidos p
                JOIN sabores s ON p.sabor_id = s.id
                ORDER BY p.data DESC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conn.close()


def criar_pedido(sabor_id, quantidade):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO pedidos (sabor_id, quantidade) VALUES (%s, %s) RETURNING *",
                (sabor_id, quantidade),
            )
            pedido = cursor.fetchone()
            conn.commit()
            return pedido
        finally:
            cursor.close()
    finally:
        conn.close()
