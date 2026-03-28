import json
import logging

from flask import Blueprint, request, jsonify

from backend.auth.jwt_handler import token_required
from backend.notifications.email_service import EmailNotificationService
from backend.notifications.sms_service import SMSNotificationService
from backend.notifications.push_service import PushNotificationService
from backend.notifications.timing_engine import SmartTimingEngine
from backend.database import get_db

logger = logging.getLogger(__name__)

notif_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

email_service = EmailNotificationService()
sms_service = SMSNotificationService()
push_service = PushNotificationService()
timing_engine = SmartTimingEngine()


@notif_bp.route("/preferences", methods=["GET", "POST"])
@token_required
def notification_preferences(current_user):
    """Get or update the current user's notification preferences."""
    user_id = current_user["id"]

    if request.method == "POST":
        data = request.get_json() or {}
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO user_notification_preferences
                               (user_id, email_promotional, email_transactional,
                                sms_promotional, sms_transactional,
                                push_promotional, push_transactional, quiet_hours)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (user_id) DO UPDATE SET
                               email_promotional  = EXCLUDED.email_promotional,
                               email_transactional = EXCLUDED.email_transactional,
                               sms_promotional    = EXCLUDED.sms_promotional,
                               sms_transactional  = EXCLUDED.sms_transactional,
                               push_promotional   = EXCLUDED.push_promotional,
                               push_transactional = EXCLUDED.push_transactional,
                               quiet_hours        = EXCLUDED.quiet_hours""",
                        (
                            user_id,
                            data.get("email_promotional", True),
                            data.get("email_transactional", True),
                            data.get("sms_promotional", True),
                            data.get("sms_transactional", True),
                            data.get("push_promotional", True),
                            data.get("push_transactional", True),
                            json.dumps(data.get("quiet_hours", {})),
                        ),
                    )
            return jsonify({"success": True}), 200
        except Exception as exc:
            logger.exception("Failed to save notification preferences")
            return jsonify({"error": str(exc)}), 500

    # GET
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM user_notification_preferences WHERE user_id = %s",
                    (user_id,),
                )
                prefs = cur.fetchone()
        if prefs is None:
            return jsonify({}), 200
        return jsonify(dict(prefs)), 200
    except Exception as exc:
        logger.exception("Failed to fetch notification preferences")
        return jsonify({"error": str(exc)}), 500


@notif_bp.route("/send-test", methods=["POST"])
@token_required
def send_test_notification(current_user):
    """Trigger a test notification on the requested channel."""
    data = request.get_json() or {}
    channel = data.get("channel", "email")

    if channel == "email":
        result = email_service.send_personalized_offer(
            current_user["id"],
            current_user.get("email", ""),
            current_user.get("name", "User"),
            {},
        )
    elif channel == "sms":
        result = sms_service.send_flash_sale_alert(
            current_user.get("phone", ""),
            "Açaí especial",
            25,
            60,
        )
    elif channel == "push":
        result = push_service.send_personalized_push(
            current_user["id"],
            "Teste de notificação",
            "Esta é uma mensagem de teste",
        )
    else:
        return jsonify({"error": f"Unknown channel: {channel}"}), 400

    return jsonify(result), 200


@notif_bp.route("/upcoming", methods=["GET"])
@token_required
def get_upcoming_notifications(current_user):
    """Return the next 10 scheduled notifications for the current user."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM notification_queue
                       WHERE user_id = %s AND status = 'pending'
                       ORDER BY scheduled_at
                       LIMIT 10""",
                    (current_user["id"],),
                )
                notifications = cur.fetchall()
        return jsonify({"notifications": [dict(n) for n in notifications]}), 200
    except Exception as exc:
        logger.exception("Failed to fetch upcoming notifications")
        return jsonify({"error": str(exc)}), 500


@notif_bp.route("/timing", methods=["GET"])
@token_required
def get_optimal_timing(current_user):
    """Return the optimal send time for a given notification type."""
    notification_type = request.args.get("type", "promotional")
    timing = timing_engine.get_optimal_send_time(current_user["id"], notification_type)
    # Convert datetime to ISO string for JSON serialisation
    if hasattr(timing.get("send_at"), "isoformat"):
        timing["send_at"] = timing["send_at"].isoformat()
    return jsonify(timing), 200
