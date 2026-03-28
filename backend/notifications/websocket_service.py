import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_SOCKETIO_AVAILABLE = False
try:
    from flask_socketio import SocketIO, emit, join_room
    _SOCKETIO_AVAILABLE = True
except ImportError:
    pass


class WebSocketService:
    """Real-time notifications via Socket.IO.

    When ``flask-socketio`` is not installed the service is a no-op so the
    rest of the application continues to work.
    """

    def __init__(self, socketio=None):
        self.socketio = socketio
        if socketio is not None:
            self._register_handlers()

    def _register_handlers(self):
        if not _SOCKETIO_AVAILABLE or self.socketio is None:
            return

        from flask import request as flask_request

        @self.socketio.on("connect")
        def handle_connect():
            user_id = flask_request.args.get("user_id")
            if user_id:
                join_room(f"user_{user_id}")
            emit("notification", {
                "message": "Connected!",
                "timestamp": datetime.now().isoformat(),
            })

        @self.socketio.on("disconnect")
        def handle_disconnect():
            logger.debug("Client disconnected")

    # ------------------------------------------------------------------
    # Emit helpers
    # ------------------------------------------------------------------

    def emit_order_update(self, user_id, order_data):
        """Emit a real-time order-status update to a specific user."""
        if not self._ready():
            return
        self.socketio.emit(
            "order_update",
            {
                "order_id": order_data.get("id"),
                "status": order_data.get("status"),
                "progress": order_data.get("progress_percent"),
                "eta_minutes": order_data.get("eta"),
                "timestamp": datetime.now().isoformat(),
            },
            room=f"user_{user_id}",
        )

    def emit_new_recommendation(self, user_id, recommendation_data):
        """Emit a new personalised recommendation to a specific user."""
        if not self._ready():
            return
        self.socketio.emit(
            "new_recommendation",
            {
                "flavor_id": recommendation_data.get("flavor_id"),
                "name": recommendation_data.get("name"),
                "reason": recommendation_data.get("reason"),
                "image_url": recommendation_data.get("image_url"),
                "price": recommendation_data.get("price"),
            },
            room=f"user_{user_id}",
        )

    def emit_live_deal(self, user_id, deal_data):
        """Emit a live flash deal to a specific user."""
        if not self._ready():
            return
        expires = deal_data.get("expires_in_seconds", 600)
        self.socketio.emit(
            "live_deal",
            {
                "id": deal_data.get("id"),
                "flavor": deal_data.get("flavor"),
                "discount": deal_data.get("discount"),
                "expires_in_seconds": expires,
                "urgency": "HIGH" if expires < 300 else "MEDIUM",
            },
            room=f"user_{user_id}",
        )

    # ------------------------------------------------------------------

    def _ready(self):
        return _SOCKETIO_AVAILABLE and self.socketio is not None
