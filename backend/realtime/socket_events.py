"""Flask-SocketIO realtime events for Gelateria Pro."""

import logging
import threading
import datetime

logger = logging.getLogger(__name__)

try:
    from flask_socketio import SocketIO, emit

    socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")

    def init_socketio(app):
        socketio.init_app(app)
        _start_dashboard_task()
        return socketio

    @socketio.on("connect")
    def handle_connect():
        logger.info("Client connected via SocketIO")
        emit("connected", {"status": "ok"})

    @socketio.on("disconnect")
    def handle_disconnect():
        logger.info("Client disconnected from SocketIO")

    def emit_pedido_novo(sabor, quantidade):
        """Emit pedido_novo event when a new order is created."""
        socketio.emit("pedido_novo", {"sabor": sabor, "quantidade": quantidade})

    def emit_estoque_atualizado(sabor, quantidade):
        """Emit estoque_atualizado event when stock changes."""
        socketio.emit("estoque_atualizado", {"sabor": sabor, "quantidade": quantidade})

    def emit_dashboard_atualizado(data):
        """Emit dashboard_atualizado event with summary data."""
        socketio.emit("dashboard_atualizado", data)

    def _dashboard_background():
        import time
        while True:
            time.sleep(30)
            try:
                emit_dashboard_atualizado({"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})
            except Exception as exc:
                logger.warning("dashboard background task error: %s", exc)

    def _start_dashboard_task():
        t = threading.Thread(target=_dashboard_background, daemon=True)
        t.start()

except ImportError:
    logger.warning("flask-socketio not installed; realtime features disabled")

    class _NoOpSocketIO:
        def init_app(self, app):
            pass

        def emit(self, *args, **kwargs):
            pass

        def on(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

    socketio = _NoOpSocketIO()

    def init_socketio(app):
        return socketio

    def emit_pedido_novo(sabor, quantidade):
        pass

    def emit_estoque_atualizado(sabor, quantidade):
        pass

    def emit_dashboard_atualizado(data):
        pass
