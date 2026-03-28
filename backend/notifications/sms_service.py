import os
import logging

logger = logging.getLogger(__name__)

_TWILIO_AVAILABLE = False
try:
    from twilio.rest import Client as TwilioClient
    _TWILIO_AVAILABLE = True
except ImportError:
    pass


class SMSNotificationService:
    """Twilio SMS with intelligent timing.

    Degrades gracefully when the ``twilio`` package or required environment
    variables are absent.
    """

    def __init__(self):
        sid = os.environ.get("TWILIO_ACCOUNT_SID")
        token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.from_phone = os.environ.get("TWILIO_PHONE_NUMBER", "")
        self._client = None

        if _TWILIO_AVAILABLE and sid and token:
            self._client = TwilioClient(sid, token)

    # ------------------------------------------------------------------
    # Public send methods
    # ------------------------------------------------------------------

    def send_flash_sale_alert(self, user_phone, flavor, discount, expires_minutes):
        """Send a flash-sale SMS with urgency messaging."""
        app_url = os.environ.get("APP_URL", "")
        body = (
            f"🔥 FLASH SALE! {flavor} com {discount}% OFF! "
            f"Válido por {expires_minutes} min. Compra agora: {app_url}/order"
        )
        return self._send(user_phone, body)

    def send_order_status_update(self, user_phone, order_id, status):
        """Notify the customer about an order-status change."""
        messages = {
            "confirmed": "✅ Pedido confirmado! Seu açaí sai do forno em 10 min.",
            "preparing": "👨‍🍳 Seu açaí está sendo preparado com AMOR.",
            "ready":     "🎉 Seu açaí está pronto! Vem buscar!",
            "on_the_way": "🚗 Saiu para entrega! Chegará em 15 min",
            "delivered": "✨ Entregue! Aproveite e deixe uma review pra gente 🙏",
        }
        body = messages.get(status, f"Pedido #{order_id}: {status}")
        return self._send(user_phone, body)

    def send_appointment_reminder(self, user_phone, event_name, time_until_minutes):
        """Send a reminder for a scheduled event."""
        body = f"📅 Lembrete: {event_name} em {time_until_minutes} minutos. Nos vemos lá! 🎉"
        return self._send(user_phone, body)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _send(self, to_phone, body):
        if not _TWILIO_AVAILABLE or self._client is None:
            logger.info("Twilio not configured — SMS to %s would have been sent.", to_phone)
            return {"success": False, "error": "Twilio not configured"}

        try:
            message = self._client.messages.create(
                body=body,
                from_=self.from_phone,
                to=to_phone,
            )
            return {"success": True, "message_sid": message.sid}
        except Exception as exc:
            logger.exception("SMS send failed")
            return {"success": False, "error": str(exc)}
