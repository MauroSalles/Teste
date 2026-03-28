import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_SENDGRID_AVAILABLE = False
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail
    _SENDGRID_AVAILABLE = True
except ImportError:
    pass


class EmailNotificationService:
    """SendGrid integration with professional templates.

    When the ``sendgrid`` package or the ``SENDGRID_API_KEY`` environment
    variable are not available the service degrades gracefully: send calls
    return ``{'success': False, 'error': 'SendGrid not configured'}`` instead
    of raising an exception.
    """

    def __init__(self):
        api_key = os.environ.get("SENDGRID_API_KEY")
        self.from_email = os.environ.get("FROM_EMAIL", "noreply@gelateria.com")
        self._client = None

        if _SENDGRID_AVAILABLE and api_key:
            self._client = sendgrid.SendGridAPIClient(api_key)

    # ------------------------------------------------------------------
    # Public send methods
    # ------------------------------------------------------------------

    def send_welcome_series(self, user_id, user_email, user_name):
        """Schedule a five-email welcome drip series."""
        emails = [
            {"template": "welcome_day0",    "delay_hours": 0,
             "subject": f"Bem-vindo {user_name}! 🎉"},
            {"template": "welcome_day1_tips", "delay_hours": 24,
             "subject": "5 sabores que você vai amar (baseado no seu perfil)"},
            {"template": "welcome_day3_offer", "delay_hours": 72,
             "subject": "20% OFF no seu primeiro pedido! ⏰ Expires em 24h"},
            {"template": "welcome_day7_remind", "delay_hours": 168,
             "subject": "Você ainda não provou a melhor açaí?"},
            {"template": "welcome_day14_vip", "delay_hours": 336,
             "subject": "Junte-se ao nosso VIP Club — Rewards + Exclusive"},
        ]
        scheduled = []
        for email in emails:
            scheduled.append(self._schedule_email(user_id, user_email, email))
        return {"success": True, "scheduled": len(scheduled)}

    def send_abandoned_cart(self, user_id, user_email, cart_data):
        """Send an abandoned-cart recovery email."""
        try:
            if self._was_recently_sent(user_id, "abandoned_cart"):
                return {"success": False, "error": "Email já enviado recentemente"}

            products = cart_data.get("items", [])
            total = cart_data.get("total", 0.0)
            recovery_link = self._generate_recovery_link(user_id, cart_data.get("id", ""))

            html_content = self._render_template(
                "abandoned_cart",
                {
                    "products": str(products),
                    "total": f"{total:.2f}",
                    "recovery_link": recovery_link,
                    "discount": "15% OFF se você comprar agora",
                },
            )

            result = self._send(
                user_email,
                f"Você esqueceu de R${total:.2f} em açaí! 😋",
                html_content,
            )
            if result.get("success"):
                self._log_email_sent(user_id, "abandoned_cart", 202)
            return result
        except Exception as exc:
            logger.exception("send_abandoned_cart failed")
            return {"success": False, "error": str(exc)}

    def send_order_confirmation(self, order_id, user_email, order_data):
        """Send an order-confirmation email."""
        try:
            app_url = os.environ.get("APP_URL", "")
            html_content = self._render_template(
                "order_confirmation",
                {
                    "order_id": str(order_id),
                    "items": str(order_data.get("items", [])),
                    "total": f"{order_data.get('total', 0.0):.2f}",
                    "delivery_time": str(order_data.get("delivery_time", "")),
                    "tracking_url": f"{app_url}/tracking/{order_id}",
                },
            )
            return self._send(
                user_email,
                f"Seu pedido #{order_id} foi confirmado! 🎉",
                html_content,
            )
        except Exception as exc:
            logger.exception("send_order_confirmation failed")
            return {"success": False, "error": str(exc)}

    def send_personalized_offer(self, user_id, user_email, user_name, preferences):
        """Send a personalised promotional offer."""
        try:
            favorite_flavor = self._get_favorite_flavor(user_id)
            discount = self._calculate_dynamic_discount(user_id)
            offer = {
                "flavor": favorite_flavor,
                "discount": discount,
                "reason": "Você comprou esse sabor 8 vezes!",
                "expires_at": (datetime.now() + timedelta(days=3)).isoformat(),
            }

            html_content = self._render_template(
                "personalized_offer",
                {
                    "user_name": user_name,
                    "flavor": offer["flavor"],
                    "discount": str(offer["discount"]),
                    "reason": offer["reason"],
                    "cta_url": self._generate_offer_link(user_id, offer),
                    "expires_at": offer["expires_at"],
                },
            )
            result = self._send(
                user_email,
                f"{user_name}, só pra você: {discount}% OFF em {favorite_flavor}!",
                html_content,
            )
            result["offer"] = offer
            return result
        except Exception as exc:
            logger.exception("send_personalized_offer failed")
            return {"success": False, "error": str(exc)}

    def send_birthday_special(self, user_id, user_email, user_name):
        """Send a birthday discount email."""
        try:
            html_content = self._render_template(
                "birthday_special",
                {
                    "user_name": user_name,
                    "discount": "30",
                    "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
                    "cta_url": self._generate_offer_link(user_id, {"discount": 30, "type": "birthday"}),
                },
            )
            return self._send(
                user_email,
                f"🎂 Feliz Aniversário {user_name}! 30% OFF pra celebrar!",
                html_content,
            )
        except Exception as exc:
            logger.exception("send_birthday_special failed")
            return {"success": False, "error": str(exc)}

    def send_reengagement_campaign(self, user_id, user_email, user_name, days_inactive):
        """Send a win-back campaign based on inactivity period."""
        try:
            if days_inactive < 14:
                subject = f"{user_name}, saudade sua! Volta pra gente"
                discount = 15
            elif days_inactive < 30:
                subject = f"{user_name}, oferecemos TUDO pra você voltar"
                discount = 25
            else:
                subject = f"{user_name}, você merecia um açaí NOW! 50% OFF 🚀"
                discount = 50

            html_content = self._render_template(
                "reengagement",
                {
                    "user_name": user_name,
                    "days_inactive": str(days_inactive),
                    "discount": str(discount),
                    "last_order": str(self._get_last_order_summary(user_id)),
                    "cta_url": self._generate_offer_link(user_id, {"discount": discount, "type": "reengagement"}),
                },
            )
            return self._send(user_email, subject, html_content)
        except Exception as exc:
            logger.exception("send_reengagement_campaign failed")
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _send(self, to_email, subject, html_content):
        """Low-level send that delegates to SendGrid or returns a stub."""
        if not _SENDGRID_AVAILABLE or self._client is None:
            logger.info("SendGrid not configured — email to %s would have been sent.", to_email)
            return {"success": False, "error": "SendGrid not configured"}

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        response = self._client.send(message)
        return {"success": response.status_code == 202}

    def _render_template(self, template_name, variables):
        """Render an HTML email template substituting {{key}} placeholders."""
        template_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "templates", "email",
            f"{template_name}.html",
        )
        try:
            with open(template_path, "r", encoding="utf-8") as fh:
                template = fh.read()
        except FileNotFoundError:
            template = f"<p>Template '{template_name}' not found.</p>"

        for key, value in variables.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template

    def _schedule_email(self, user_id, email, email_config):
        """Record a future email in the notification queue (best-effort)."""
        from backend.database import get_db
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO notification_queue
                           (user_id, channel, template, payload, scheduled_at, status)
                           VALUES (%s, 'email', %s, %s, NOW() + INTERVAL '1 hour' * %s, 'pending')""",
                        (user_id, email_config["template"], email, email_config["delay_hours"]),
                    )
            return {"queued": True}
        except Exception as exc:
            logger.warning("Could not queue email: %s", exc)
            return {"queued": False}

    def _was_recently_sent(self, user_id, template, hours=2):
        """Return True if the same template was sent to this user within *hours*."""
        from backend.database import get_db
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT 1 FROM notification_log
                           WHERE user_id = %s AND template = %s
                             AND sent_at > NOW() - INTERVAL '1 hour' * %s
                           LIMIT 1""",
                        (user_id, template, hours),
                    )
                    return cur.fetchone() is not None
        except Exception:
            return False

    def _log_email_sent(self, user_id, template, status_code):
        from backend.database import get_db
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO notification_log (user_id, channel, template, status_code)
                           VALUES (%s, 'email', %s, %s)""",
                        (user_id, template, status_code),
                    )
        except Exception as exc:
            logger.warning("Could not log email: %s", exc)

    def _get_favorite_flavor(self, user_id):
        return "Açaí Berry"

    def _calculate_dynamic_discount(self, user_id):
        return 20

    def _generate_recovery_link(self, user_id, cart_id):
        app_url = os.environ.get("APP_URL", "")
        return f"{app_url}/cart/recover/{user_id}/{cart_id}"

    def _generate_offer_link(self, user_id, offer):
        app_url = os.environ.get("APP_URL", "")
        return f"{app_url}/offer/{user_id}"

    def _get_last_order_summary(self, user_id):
        return {}
