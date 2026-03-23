from typing import Any

from database import get_connection


def listar_clientes() -> list[dict[str, Any]]:
    """Return all customers ordered by name.

    ``total_pedidos`` and ``valor_total`` count only non-cancelled orders.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.nome, c.telefone, c.email,
                       COUNT(p.id) AS total_pedidos,
                       COALESCE(SUM(p.total), 0) AS valor_total
                FROM clientes c
                LEFT JOIN pedidos p
                    ON p.cliente_id = c.id AND p.status != 'cancelado'
                GROUP BY c.id, c.nome, c.telefone, c.email
                ORDER BY c.nome
                """
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]
