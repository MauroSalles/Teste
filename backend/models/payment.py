"""Payment model — DB operations for the payments table."""

import logging
from backend.database import get_db

logger = logging.getLogger(__name__)


def criar_pagamento(pedido_id, metodo, valor, stripe_id=None, pix_txid=None):
    """Insert a new payment record and return it."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO payments (pedido_id, metodo, valor, stripe_id, pix_txid, status)
                VALUES (%s, %s, %s, %s, %s, 'pendente')
                RETURNING *
                """,
                (pedido_id, metodo, valor, stripe_id, pix_txid),
            )
            return cur.fetchone()


def obter_pagamento(id):
    """Return a payment by its primary key."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM payments WHERE id = %s", (id,))
            return cur.fetchone()


def atualizar_status_pagamento(id, status):
    """Update the status of a payment and return the updated row."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE payments SET status = %s WHERE id = %s RETURNING *",
                (status, id),
            )
            return cur.fetchone()


def listar_pagamentos_pedido(pedido_id):
    """Return all payments for a given pedido."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM payments WHERE pedido_id = %s ORDER BY created_at DESC",
                (pedido_id,),
            )
            return cur.fetchall()
