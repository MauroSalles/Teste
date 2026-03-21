from database import get_connection


def listar_pedidos():
    """Return all orders with flavor and customer info."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, c.nome AS cliente, s.nome AS sabor,
                       p.quantidade, p.total, p.status, p.criado_em
                FROM pedidos p
                LEFT JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN sabores s ON p.sabor_id = s.id
                ORDER BY p.criado_em DESC
                """
            )
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def fazer_pedido(cliente_nome, sabor_nome, quantidade):
    """Create a new order."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get or create client
            cur.execute("SELECT id FROM clientes WHERE nome = %s LIMIT 1", (cliente_nome,))
            existing = cur.fetchone()
            if existing:
                cliente_id = existing["id"]
            else:
                cur.execute(
                    "INSERT INTO clientes (nome) VALUES (%s) RETURNING id",
                    (cliente_nome,),
                )
                cliente_id = cur.fetchone()["id"]

            # Find flavor
            cur.execute(
                "SELECT id, preco FROM sabores WHERE LOWER(nome) = LOWER(%s) AND disponivel = TRUE",
                (sabor_nome,),
            )
            sabor = cur.fetchone()
            if not sabor:
                return None, "Sabor não encontrado ou indisponível"

            # Check stock
            cur.execute(
                "SELECT quantidade FROM estoque WHERE sabor_id = %s",
                (sabor["id"],),
            )
            estoque = cur.fetchone()
            if not estoque or estoque["quantidade"] < quantidade:
                return None, "Estoque insuficiente"

            total = sabor["preco"] * quantidade

            cur.execute(
                """
                INSERT INTO pedidos (cliente_id, sabor_id, quantidade, total)
                VALUES (%s, %s, %s, %s) RETURNING id
                """,
                (cliente_id, sabor["id"], quantidade, total),
            )
            pedido_id = cur.fetchone()["id"]

            # Decrease stock
            cur.execute(
                "UPDATE estoque SET quantidade = quantidade - %s, atualizado_em = NOW() WHERE sabor_id = %s",
                (quantidade, sabor["id"]),
            )
        conn.commit()
        return {"id": pedido_id, "total": float(total)}, None
    finally:
        conn.close()
