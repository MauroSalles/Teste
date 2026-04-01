import logging
import os

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str) -> dict:
    """Send email via SendGrid if configured, otherwise log the email."""
    api_key = os.environ.get("SENDGRID_API_KEY", "")
    if not api_key:
        logger.info(
            "[EMAIL LOG] To: %s | Subject: %s | Body: %s",
            to,
            subject,
            html_body[:200],
        )
        return {"status": "logged", "to": to, "subject": subject}

    try:
        import sendgrid  # type: ignore
        from sendgrid.helpers.mail import Mail  # type: ignore

        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@gelateriapro.com")
        message = Mail(
            from_email=from_email,
            to_emails=to,
            subject=subject,
            html_content=html_body,
        )
        response = sg.send(message)
        logger.info("Email sent to %s — status %s", to, response.status_code)
        return {"status": "sent", "to": to, "http_status": response.status_code}
    except Exception as exc:
        logger.error("SendGrid error: %s", exc)
        return {"status": "error", "error": str(exc)}


def send_order_confirmation(user_email: str, user_name: str, pedido_data: dict) -> dict:
    subject = "✅ Pedido confirmado — Gelateria Pro"
    sabor = pedido_data.get("sabor", "")
    quantidade = pedido_data.get("quantidade", "")
    total = pedido_data.get("total", "")
    html_body = f"""
    <h2>Olá, {user_name}! 🍦</h2>
    <p>Seu pedido foi confirmado com sucesso.</p>
    <table>
      <tr><td><strong>Sabor:</strong></td><td>{sabor}</td></tr>
      <tr><td><strong>Quantidade:</strong></td><td>{quantidade}</td></tr>
      <tr><td><strong>Total:</strong></td><td>R$ {total}</td></tr>
    </table>
    <p>Obrigado por escolher a Gelateria Pro! 🎉</p>
    """
    return send_email(user_email, subject, html_body)


def send_welcome_email(user_email: str, user_name: str, referral_code: str) -> dict:
    subject = "🍦 Bem-vindo à Gelateria Pro!"
    html_body = f"""
    <h2>Bem-vindo, {user_name}! 🎉</h2>
    <p>Estamos felizes em ter você conosco na <strong>Gelateria Pro</strong>.</p>
    <p>Seu código de indicação exclusivo: <strong>{referral_code}</strong></p>
    <p>Compartilhe com amigos e ganhe pontos de bônus!</p>
    <ul>
      <li>Bronze (0-4 indicações): sem bônus</li>
      <li>Prata (5-9 indicações): +50 pontos de bônus</li>
      <li>Ouro (10+ indicações): +100 pontos de bônus</li>
    </ul>
    <p>Aproveite nosso cardápio premium e acumule pontos a cada pedido! 🍦</p>
    """
    return send_email(user_email, subject, html_body)
