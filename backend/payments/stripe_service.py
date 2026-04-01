import os
import logging

logger = logging.getLogger(__name__)

_STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")


def create_payment_intent(amount_cents: int, currency: str = "brl", metadata: dict = None):
    """Create a Stripe PaymentIntent. Falls back gracefully if key not configured."""
    if not _STRIPE_SECRET_KEY:
        logger.warning("STRIPE_SECRET_KEY not set — returning mock PaymentIntent")
        return {
            "id": "pi_mock_000",
            "client_secret": "pi_mock_000_secret_mock",
            "amount": amount_cents,
            "currency": currency,
            "status": "requires_payment_method",
            "mock": True,
        }
    try:
        import stripe  # type: ignore

        stripe.api_key = _STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            metadata=metadata or {},
        )
        return {
            "id": intent["id"],
            "client_secret": intent["client_secret"],
            "amount": intent["amount"],
            "currency": intent["currency"],
            "status": intent["status"],
        }
    except Exception as exc:
        logger.error("Stripe PaymentIntent error: %s", exc)
        raise


def handle_webhook(payload: bytes, sig_header: str):
    """Verify and parse a Stripe webhook event."""
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    if not _STRIPE_SECRET_KEY or not webhook_secret:
        logger.warning("Stripe webhook secrets not configured — skipping verification")
        import json

        return json.loads(payload)
    try:
        import stripe  # type: ignore

        stripe.api_key = _STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        return event
    except Exception as exc:
        logger.error("Stripe webhook error: %s", exc)
        raise
