import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_FIREBASE_AVAILABLE = False
try:
    import firebase_admin
    from firebase_admin import messaging as _messaging
    _FIREBASE_AVAILABLE = True
except ImportError:
    pass


class PushNotificationService:
    """Firebase Cloud Messaging for Web and Mobile.

    Degrades gracefully when the ``firebase-admin`` package or application
    credentials are not available.
    """

    def __init__(self):
        self._initialized = False
        if _FIREBASE_AVAILABLE:
            try:
                firebase_admin.get_app()
                self._initialized = True
            except ValueError:
                try:
                    firebase_admin.initialize_app()
                    self._initialized = True
                except Exception as exc:
                    logger.warning("Firebase initialisation failed: %s", exc)

    # ------------------------------------------------------------------
    # Public send methods
    # ------------------------------------------------------------------

    def send_personalized_push(self, user_id, title, body, image_url=None):
        """Send a push notification to all of a user's registered devices."""
        if not _FIREBASE_AVAILABLE or not self._initialized:
            logger.info("Firebase not configured — push for user %s skipped.", user_id)
            return {"success": False, "error": "Firebase not configured"}

        try:
            tokens = self._get_user_device_tokens(user_id)
            if not tokens:
                return {"success": False, "error": "No device tokens registered"}

            notification = _messaging.Notification(title=title, body=body, image=image_url)
            sent = 0
            for token in tokens:
                message = _messaging.Message(
                    notification=notification,
                    token=token,
                    data={
                        "user_id": str(user_id),
                        "timestamp": datetime.now().isoformat(),
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    },
                )
                _messaging.send(message)
                sent += 1

            return {"success": True, "tokens_sent": sent}
        except Exception as exc:
            logger.exception("send_personalized_push failed")
            return {"success": False, "error": str(exc)}

    def send_order_tracking_notification(self, user_id, order_id, progress_percent):
        """Notify a user about the progress of their order."""
        emoji_map = {0: "📋", 25: "👨‍🍳", 50: "🎉", 75: "🚗", 100: "✨"}
        emoji = emoji_map.get(progress_percent, "⏳")
        title = f"{emoji} Seu pedido #{order_id}"
        body = self._get_progress_message(progress_percent)
        return self.send_personalized_push(user_id, title, body)

    def send_recommendation_push(self, user_id, flavor_name, recommendation_reason):
        """Send an AI-driven flavour recommendation notification."""
        return self.send_personalized_push(
            user_id,
            f"🍓 {flavor_name} está à sua espera!",
            recommendation_reason,
            image_url=self._get_flavor_image(flavor_name),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_user_device_tokens(self, user_id):
        """Return FCM device tokens for a user (fetched from DB when available)."""
        from backend.database import get_db
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT token FROM device_tokens WHERE user_id = %s AND active = TRUE",
                        (user_id,),
                    )
                    rows = cur.fetchall()
                    return [row["token"] for row in rows]
        except Exception as exc:
            logger.warning("Could not fetch device tokens: %s", exc)
            return []

    def _get_progress_message(self, progress_percent):
        messages = {
            0:   "Pedido recebido, aguardando confirmação.",
            25:  "Seu pedido está sendo preparado! 👨‍🍳",
            50:  "Quase pronto! 🎉",
            75:  "Saiu para entrega! 🚗 Chegará em breve.",
            100: "Entregue! Bom apetite! ✨",
        }
        return messages.get(progress_percent, f"Progresso: {progress_percent}%")

    def _get_flavor_image(self, flavor_name):
        return ""
