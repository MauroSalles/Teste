import logging
from backend.database import get_db

logger = logging.getLogger(__name__)


def registrar_pagamento(pedido_id, metodo: str, valor: float, status: str = "pendente", external_id: str = None):
    sql = """
        INSERT INTO payments (pedido_id, metodo, valor, status, external_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, pedido_id, metodo, valor, status, external_id, created_at
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pedido_id, metodo, valor, status, external_id))
            return dict(cur.fetchone())


def obter_pagamento(payment_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
            row = cur.fetchone()
            return dict(row) if row else None


def atualizar_status(payment_id: int, status: str):
    sql = """
        UPDATE payments
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, status, updated_at
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (status, payment_id))
            row = cur.fetchone()
            return dict(row) if row else None
