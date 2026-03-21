from database import get_connection


def listar_sabores():
    """Return all available flavors."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, preco, disponivel FROM sabores ORDER BY nome")
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def adicionar_sabor(nome, preco):
    """Insert a new flavor and add a stock entry."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sabores (nome, preco) VALUES (%s, %s) RETURNING id, nome, preco",
                (nome, float(preco)),
            )
            sabor = dict(cur.fetchone())
            cur.execute(
                "INSERT INTO estoque (sabor_id, quantidade) VALUES (%s, 0)",
                (sabor["id"],),
            )
        conn.commit()
        return sabor
    finally:
        conn.close()


def remover_sabor(sabor_id):
    """Delete a flavor by id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM sabores WHERE id = %s RETURNING nome",
                (int(sabor_id),),
            )
            row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        conn.close()
