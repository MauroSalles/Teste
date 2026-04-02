"""Email notification service via SendGrid."""

import logging
import os

logger = logging.getLogger(__name__)


def send_order_confirmation(email, pedido_id, itens, total):
    """Send order confirmation email. Logs if SENDGRID_API_KEY not set."""
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        logger.info(
            "[EMAIL] Order confirmation would be sent to %s — Pedido #%s Total R$%.2f",
            email, pedido_id, float(total),
        )
        return False

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        itens_html = "".join(
            f"<li>{item.get('nome', item.get('sabor', 'Item'))} x{item.get('quantidade', 1)}</li>"
            for item in itens
        )
        body = (
            f"<h2>🍦 Pedido Confirmado!</h2>"
            f"<p>Pedido <strong>#{pedido_id}</strong></p>"
            f"<ul>{itens_html}</ul>"
            f"<p><strong>Total: R$ {float(total):.2f}</strong></p>"
        )
        message = Mail(
            from_email=os.environ.get("SENDGRID_FROM_EMAIL", "noreply@gelateriapro.com"),
            to_emails=email,
            subject=f"Pedido #{pedido_id} Confirmado — Gelateria Pro",
            html_content=body,
        )
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        logger.info("Order confirmation email sent to %s", email)
        return True
    except Exception as exc:
        logger.error("SendGrid error: %s", exc)
        return False


def send_coupon_email(email, coupon_code, discount):
    """Notify user about a new coupon."""
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        logger.info("[EMAIL] Coupon %s (%.2f) would be sent to %s", coupon_code, float(discount), email)
        return False

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        body = (
            f"<h2>🎉 Você ganhou um cupom!</h2>"
            f"<p>Código: <strong>{coupon_code}</strong></p>"
            f"<p>Desconto: R$ {float(discount):.2f}</p>"
        )
        message = Mail(
            from_email=os.environ.get("SENDGRID_FROM_EMAIL", "noreply@gelateriapro.com"),
            to_emails=email,
            subject="Cupom especial para você — Gelateria Pro",
            html_content=body,
        )
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception as exc:
        logger.error("SendGrid coupon email error: %s", exc)
        return False


def send_low_stock_alert(email, sabor_nome, quantidade):
    """Send low-stock alert to admin."""
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        logger.warning("[EMAIL] Low stock alert: %s qty=%d would be sent to %s", sabor_nome, quantidade, email)
        return False

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        body = (
            f"<h2>⚠️ Alerta de Estoque Baixo</h2>"
            f"<p>Sabor: <strong>{sabor_nome}</strong></p>"
            f"<p>Quantidade restante: <strong>{quantidade}</strong></p>"
        )
        message = Mail(
            from_email=os.environ.get("SENDGRID_FROM_EMAIL", "noreply@gelateriapro.com"),
            to_emails=email,
            subject=f"⚠️ Estoque baixo: {sabor_nome}",
            html_content=body,
        )
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception as exc:
        logger.error("SendGrid low-stock email error: %s", exc)
        return False
