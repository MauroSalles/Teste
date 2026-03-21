from backend.database import get_connection


def listar_sabores():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM sabores ORDER BY nome")
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conn.close()


def adicionar_sabor(nome, preco):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO sabores (nome, preco) VALUES (%s, %s) RETURNING *",
                (nome, float(preco)),
            )
            sabor = cursor.fetchone()
            conn.commit()
            return sabor
        finally:
            cursor.close()
    finally:
        conn.close()


def remover_sabor(sabor_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM sabores WHERE id = %s RETURNING *", (sabor_id,))
            sabor = cursor.fetchone()
            conn.commit()
            return sabor
        finally:
            cursor.close()
    finally:
        conn.close()


def buscar_sabor_por_nome(nome):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM sabores WHERE LOWER(nome) = LOWER(%s)", (nome,))
            return cursor.fetchone()
        finally:
            cursor.close()
    finally:
        conn.close()
