"""Model for self-service flavor inventory (estoque_sabores)."""

import json
from backend.database import get_db


def listar_estoque_sabores():
    """Return all self-service flavors with their current stock levels."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome, volume_litros, categoria, em_exposicao,
                       quantidade_atual, estoque_minimo_sugestao, resposicao_rapida,
                       data_atualizacao
                FROM estoque_sabores
                ORDER BY categoria, nome, volume_litros
                """
            )
            return cursor.fetchall()


def listar_faltando():
    """Return flavors whose current stock is below the suggested minimum."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome, volume_litros, categoria, em_exposicao,
                       quantidade_atual, estoque_minimo_sugestao, resposicao_rapida,
                       data_atualizacao
                FROM estoque_sabores
                WHERE estoque_minimo_sugestao > 0
                  AND quantidade_atual < estoque_minimo_sugestao
                ORDER BY resposicao_rapida DESC, nome
                """
            )
            return cursor.fetchall()


def registrar_pedido_semanal(itens, observacao=None):
    """Log a weekly replenishment order.

    ``itens`` should be a list of dicts with ``estoque_sabor_id`` and
    ``quantidade`` keys.  Returns the newly created pedido_reposicao row.
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pedidos_reposicao (itens, observacao, status)
                VALUES (%s, %s, 'pendente')
                RETURNING id, data_pedido, itens, observacao, status
                """,
                (json.dumps(itens), observacao),
            )
            return cursor.fetchone()


def registrar_remessa(itens):
    """Register arrival of a new shipment and update current quantities.

    ``itens`` should be a list of dicts with ``estoque_sabor_id`` and
    ``quantidade`` keys.  Each entry increases ``quantidade_atual`` by the
    given amount.  Returns the list of updated rows.
    """
    updated = []
    with get_db() as conn:
        with conn.cursor() as cursor:
            for item in itens:
                sabor_id = int(item["estoque_sabor_id"])
                quantidade = int(item["quantidade"])
                cursor.execute(
                    """
                    UPDATE estoque_sabores
                    SET quantidade_atual = quantidade_atual + %s,
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, nome, volume_litros, categoria,
                              quantidade_atual, estoque_minimo_sugestao,
                              resposicao_rapida, data_atualizacao
                    """,
                    (quantidade, sabor_id),
                )
                row = cursor.fetchone()
                if row:
                    updated.append(row)
    return updated
