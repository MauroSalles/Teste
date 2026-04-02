"""Stripe payment service."""

import logging
import os

logger = logging.getLogger(__name__)


def create_payment_intent(amount_cents, currency="brl", metadata=None):
    """Create a Stripe PaymentIntent. Returns None if STRIPE_SECRET_KEY not set."""
    secret_key = os.environ.get("STRIPE_SECRET_KEY")
    if not secret_key:
        logger.warning("STRIPE_SECRET_KEY not set; skipping payment intent creation")
        return None

    try:
        import stripe
        stripe.api_key = secret_key
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            metadata=metadata or {},
        )
        return intent
    except Exception as exc:
        logger.error("Stripe create_payment_intent error: %s", exc)
        return None


def handle_webhook(payload, sig_header):
    """Verify and handle a Stripe webhook event."""
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        event_type = event.get("type", "")
        logger.info("Stripe webhook received: %s", event_type)

        if event_type == "payment_intent.succeeded":
            pi = event["data"]["object"]
            logger.info("PaymentIntent succeeded: %s", pi.get("id"))

        elif event_type == "payment_intent.payment_failed":
            pi = event["data"]["object"]
            logger.warning("PaymentIntent failed: %s", pi.get("id"))

        return {"received": True, "type": event_type}
    except Exception as exc:
        logger.error("Stripe webhook error: %s", exc)
        raise
