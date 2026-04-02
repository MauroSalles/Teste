"""Notification routes blueprint — /api/notifications/*"""

import logging

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

logger = logging.getLogger(__name__)

notification_bp = Blueprint("notification", __name__, url_prefix="/api/notifications")

_preferences_store = {}


@notification_bp.get("/preferences")
@token_required
def get_preferences(current_user):
    prefs = _preferences_store.get(current_user["id"], {
        "email": True,
        "push": False,
        "sms": False,
    })
    return jsonify({"user_id": current_user["id"], "preferences": prefs}), 200


@notification_bp.post("/preferences")
@token_required
def set_preferences(current_user):
    data = request.get_json(silent=True) or {}
    current = _preferences_store.get(current_user["id"], {})
    current.update({k: bool(v) for k, v in data.items() if k in ("email", "push", "sms")})
    _preferences_store[current_user["id"]] = current
    return jsonify({"user_id": current_user["id"], "preferences": current}), 200


@notification_bp.post("/send-test")
@token_required
def send_test(current_user):
    from backend.notifications.email_service import send_order_confirmation
    email = current_user.get("email", "test@example.com")
    send_order_confirmation(
        email,
        pedido_id=0,
        itens=[{"nome": "Chocolate", "quantidade": 1, "preco": 10.0}],
        total=10.0,
    )
    return jsonify({"message": f"Notificação de teste enviada para {email}"}), 200
