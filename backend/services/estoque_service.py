from database import get_connection


def listar_estoque():
    """Return stock levels for all flavors."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id, s.nome, e.quantidade, s.preco
                FROM estoque e
                JOIN sabores s ON e.sabor_id = s.id
                ORDER BY s.nome
                """
            )
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def atualizar_estoque(sabor_nome, quantidade):
    """Set the stock quantity for a flavor by name."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM sabores WHERE LOWER(nome) = LOWER(%s)",
                (sabor_nome,),
            )
            sabor = cur.fetchone()
            if not sabor:
                return None, "Sabor não encontrado"

            cur.execute(
                "UPDATE estoque SET quantidade = %s, atualizado_em = NOW() WHERE sabor_id = %s RETURNING quantidade",
                (int(quantidade), sabor["id"]),
            )
            updated = cur.fetchone()
        conn.commit()
        return {"quantidade": updated["quantidade"]}, None
    finally:
        conn.close()
