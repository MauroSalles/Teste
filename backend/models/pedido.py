from backend.database import get_db

METODOS_PAGAMENTO = ("dinheiro", "pix", "cartao_credito", "cartao_debito")
STATUS_PEDIDO = ("confirmado", "cancelado", "pendente")


def listar_pedidos(page=1, per_page=50):
    with get_db() as conn:
        with conn.cursor() as cursor:
            page = max(1, page)
            per_page = max(1, min(per_page, 100))
            offset = (page - 1) * per_page
            cursor.execute(
                """
                SELECT p.id, s.nome AS sabor, p.sabor_id, p.quantidade, p.data,
                       p.metodo_pagamento, p.status, p.observacao, p.user_id
                FROM pedidos p
                JOIN sabores s ON p.sabor_id = s.id
                ORDER BY p.data DESC
                LIMIT %s OFFSET %s
                """,
                (per_page, offset),
            )
            return cursor.fetchall()


def obter_pedido(pedido_id):
    """Return a single order by id, or None."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.id, s.nome AS sabor, p.sabor_id, p.quantidade, p.data,
                       p.metodo_pagamento, p.status, p.observacao, p.user_id
                FROM pedidos p
                JOIN sabores s ON p.sabor_id = s.id
                WHERE p.id = %s
                """,
                (pedido_id,),
            )
            return cursor.fetchone()


def criar_pedido(sabor_id, quantidade, metodo_pagamento="dinheiro", observacao=None, user_id=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO pedidos (sabor_id, quantidade, metodo_pagamento, observacao, user_id)
                   VALUES (%s, %s, %s, %s, %s) RETURNING *""",
                (sabor_id, quantidade, metodo_pagamento, observacao, user_id),
            )
            return cursor.fetchone()


def atualizar_pedido(pedido_id, quantidade=None, metodo_pagamento=None,
                     status=None, observacao=None):
    """Update editable fields of an existing order. Returns updated row or None."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Build SET clause dynamically — column names are hardcoded
            # string literals, never user input. Values use %s placeholders.
            _ALLOWED_COLUMNS = {
                "quantidade", "metodo_pagamento", "status", "observacao",
            }
            sets = []
            params = []
            if quantidade is not None:
                sets.append("quantidade = %s")
                params.append(quantidade)
            if metodo_pagamento is not None:
                sets.append("metodo_pagamento = %s")
                params.append(metodo_pagamento)
            if status is not None:
                sets.append("status = %s")
                params.append(status)
            if observacao is not None:
                sets.append("observacao = %s")
                params.append(observacao)
            if not sets:
                return obter_pedido(pedido_id)
            params.append(pedido_id)
            cursor.execute(
                f"UPDATE pedidos SET {', '.join(sets)} WHERE id = %s RETURNING *",
                params,
            )
            return cursor.fetchone()


def cancelar_pedido(pedido_id):
    """Mark an order as cancelled. Returns updated row or None."""
    return atualizar_pedido(pedido_id, status="cancelado")


def relatorio_vendas(periodo: str = "diario") -> list:
    """Aggregate sales totals grouped by the requested period.

    periodo: 'diario' | 'semanal' | 'mensal'
    Returns list of {periodo, total_pedidos, total_itens, receita_total}.
    """
    _TRUNCATIONS = {
        "diario": "day",
        "semanal": "week",
        "mensal": "month",
    }
    trunc = _TRUNCATIONS.get(periodo, "day")

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    DATE_TRUNC(%s, p.data)          AS periodo,
                    COUNT(p.id)                     AS total_pedidos,
                    SUM(p.quantidade)               AS total_itens,
                    SUM(p.quantidade * s.preco)     AS receita_total
                FROM pedidos p
                JOIN sabores s ON s.id = p.sabor_id
                GROUP BY DATE_TRUNC(%s, p.data)
                ORDER BY periodo DESC
                LIMIT 30
                """,
                (trunc, trunc),
            )
            return cursor.fetchall()


def sabores_populares(limit: int = 5) -> list:
    """Top N flavors by order count."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id, s.nome, s.preco,
                       COUNT(p.id)       AS total_pedidos,
                       SUM(p.quantidade) AS total_itens
                FROM sabores s
                LEFT JOIN pedidos p ON p.sabor_id = s.id
                GROUP BY s.id, s.nome, s.preco
                ORDER BY total_pedidos DESC NULLS LAST
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()

