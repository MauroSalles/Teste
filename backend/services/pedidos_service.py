from typing import Any

from database import get_connection


def listar_pedidos() -> list[dict[str, Any]]:
    """Return all orders with flavor and customer info, newest first."""
    with get_connection() as conn:
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


def fazer_pedido(
    cliente_nome: str, sabor_nome: str, quantidade: int
) -> tuple[dict[str, Any] | None, str | None]:
    """Create a new order.

    Returns ``(pedido_dict, None)`` on success or ``(None, error_message)``
    on validation failure.
    """
    if quantidade <= 0:
        return None, "A quantidade deve ser maior que zero."

    with get_connection() as conn:
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

            # Check and reserve stock (row-level lock)
            cur.execute(
                "SELECT quantidade FROM estoque WHERE sabor_id = %s FOR UPDATE",
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
                "UPDATE estoque SET quantidade = quantidade - %s, atualizado_em = NOW() "
                "WHERE sabor_id = %s",
                (quantidade, sabor["id"]),
            )
        conn.commit()
    return {"id": pedido_id, "total": float(total)}, None


def cancelar_pedido(pedido_id: int) -> tuple[dict[str, Any] | None, str | None]:
    """Cancel an order (set status = 'cancelado') and restore stock.

    Returns ``(pedido_dict, None)`` on success or ``(None, error_message)``
    if the order is not found or already cancelled.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, sabor_id, quantidade, status FROM pedidos WHERE id = %s FOR UPDATE",
                (int(pedido_id),),
            )
            pedido = cur.fetchone()
            if not pedido:
                return None, "Pedido não encontrado."
            if pedido["status"] == "cancelado":
                return None, "Pedido já está cancelado."

            cur.execute(
                "UPDATE pedidos SET status = 'cancelado' WHERE id = %s RETURNING id, status",
                (int(pedido_id),),
            )
            updated = dict(cur.fetchone())

            # Restore stock
            cur.execute(
                "UPDATE estoque SET quantidade = quantidade + %s, atualizado_em = NOW() "
                "WHERE sabor_id = %s",
                (pedido["quantidade"], pedido["sabor_id"]),
            )
        conn.commit()
    return updated, None
