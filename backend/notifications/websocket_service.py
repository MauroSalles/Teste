"""WebSocket notification helpers."""

import logging

logger = logging.getLogger(__name__)


def notify_order(pedido_data):
    """Emit pedido_novo event via Socket.IO."""
    try:
        from backend.realtime.socket_events import emit_pedido_novo
        sabor = pedido_data.get("sabor", pedido_data.get("sabor_id", "?"))
        quantidade = pedido_data.get("quantidade", 0)
        emit_pedido_novo(sabor, quantidade)
    except Exception as exc:
        logger.warning("notify_order error: %s", exc)


def notify_stock_update(estoque_data):
    """Emit estoque_atualizado event via Socket.IO."""
    try:
        from backend.realtime.socket_events import emit_estoque_atualizado
        sabor = estoque_data.get("nome", estoque_data.get("sabor_id", "?"))
        quantidade = estoque_data.get("quantidade", 0)
        emit_estoque_atualizado(sabor, quantidade)
    except Exception as exc:
        logger.warning("notify_stock_update error: %s", exc)
