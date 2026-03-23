from backend.database import get_db


def listar_sabores():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sabores ORDER BY nome")
            return cursor.fetchall()


def adicionar_sabor(nome, preco):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sabores (nome, preco) VALUES (%s, %s) RETURNING *",
                (nome, float(preco)),
            )
            return cursor.fetchone()


def atualizar_sabor(sabor_id, novo_preco):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE sabores SET preco = %s WHERE id = %s RETURNING *",
                (float(novo_preco), sabor_id),
            )
            return cursor.fetchone()


def remover_sabor(sabor_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM sabores WHERE id = %s RETURNING *", (sabor_id,))
            return cursor.fetchone()


def buscar_sabor_por_nome(nome):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sabores WHERE LOWER(nome) = LOWER(%s)", (nome,))
            return cursor.fetchone()

