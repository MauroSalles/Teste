import logging
from flask_socketio import SocketIO, emit
from flask import request as flask_request

logger = logging.getLogger(__name__)

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")


def init_socketio(app):
    socketio.init_app(app)


@socketio.on("connect")
def on_connect():
    sid = getattr(flask_request, "sid", "unknown")
    logger.info("Client connected: %s", sid)
    emit("connected", {"status": "ok"})


@socketio.on("disconnect")
def on_disconnect():
    logger.info("Client disconnected")


def emit_novo_pedido(pedido_data: dict):
    socketio.emit("pedido_novo", pedido_data)


def emit_estoque_atualizado(estoque_data: dict):
    socketio.emit("estoque_atualizado", estoque_data)


def emit_dashboard_update(dashboard_data: dict):
    socketio.emit("dashboard_atualizado", dashboard_data)
