import logging
from flask import Blueprint, request, jsonify

from backend.auth.jwt_handler import token_required
from backend.notifications.email_service import send_email

logger = logging.getLogger(__name__)

notification_bp = Blueprint("notification_bp", __name__, url_prefix="/api/notifications")


@notification_bp.route("/send", methods=["POST"])
@token_required
def send_notification(current_user):
    """Admin-only: send a custom notification."""
    data = request.get_json(silent=True) or {}
    to = data.get("to", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()

    if not all([to, subject, body]):
        return jsonify({"error": "to, subject, and body are required"}), 400

    result = send_email(to, subject, body)
    if result.get("status") == "error":
        logger.error("Email send failed to %s", to)
        return jsonify({"status": "error", "to": to}), 500
    return jsonify({"status": "ok", "to": to})


@notification_bp.route("/order-confirmation", methods=["POST"])
@token_required
def order_confirmation(current_user):
    """Send order confirmation email."""
    data = request.get_json(silent=True) or {}
    user_email = data.get("user_email", "").strip()
    user_name = data.get("user_name", "").strip()
    pedido_data = data.get("pedido_data", {})

    if not user_email or not user_name:
        return jsonify({"error": "user_email and user_name are required"}), 400

    from backend.notifications.email_service import send_order_confirmation
    result = send_order_confirmation(user_email, user_name, pedido_data)
    if result.get("status") == "error":
        logger.error("Order confirmation email failed to %s", user_email)
        return jsonify({"status": "error", "to": user_email}), 500
    return jsonify({"status": "ok", "to": user_email})
