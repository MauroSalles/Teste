from backend.database import get_db


def listar_ingredientes():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ingredientes ORDER BY nome")
            return cursor.fetchall()


def adicionar_ingrediente(nome, unidade, preco_unitario, quantidade_minima=0):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredientes (nome, unidade, preco_unitario, quantidade_minima)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """,
                (nome, unidade, float(preco_unitario), float(quantidade_minima)),
            )
            return cursor.fetchone()


def atualizar_estoque_ingrediente(ingrediente_id, quantidade):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE ingredientes SET quantidade_atual = %s WHERE id = %s RETURNING *",
                (float(quantidade), ingrediente_id),
            )
            return cursor.fetchone()


def ingredientes_em_alerta():
    """Return ingredients whose current quantity is at or below the minimum threshold
    or expiring within 3 days."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome, unidade, quantidade_atual, quantidade_minima, data_validade
                FROM ingredientes
                WHERE quantidade_atual <= quantidade_minima
                   OR (data_validade IS NOT NULL AND data_validade <= CURRENT_DATE + INTERVAL '3 days')
                ORDER BY data_validade NULLS LAST, nome
                """
            )
            return cursor.fetchall()


def buscar_ingrediente_por_id(ingrediente_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ingredientes WHERE id = %s", (ingrediente_id,))
            return cursor.fetchone()
