import os
import logging
from decimal import Decimal

import stripe

logger = logging.getLogger(__name__)


class StripePaymentService:
    """Stripe payment processing with webhooks and tokenization."""

    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    def create_payment_intent(self, amount, customer_id, metadata):
        """Create a payment intent for card / Google Pay / Apple Pay."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(Decimal(str(amount)) * 100),  # centavos
                currency="brl",
                customer=customer_id,
                metadata=metadata,
                payment_method_types=["card", "link"],
                statement_descriptor="GELATERIA STORE",
            )
            return {"success": True, "client_secret": intent.client_secret}
        except stripe.error.CardError as e:
            return {"success": False, "error": str(e)}
        except stripe.error.StripeError as e:
            logger.error("Stripe error: %s", e)
            return {"success": False, "error": str(e)}

    def create_setup_intent(self, customer_id):
        """Save a card for future off-session payments."""
        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"],
                usage="off_session",
            )
            return {"success": True, "client_secret": setup_intent.client_secret}
        except stripe.error.StripeError as e:
            logger.error("Stripe error: %s", e)
            return {"success": False, "error": str(e)}

    def process_webhook(self, payload, sig_header):
        """Process incoming Stripe webhooks."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )

            if event["type"] == "payment_intent.succeeded":
                self._handle_payment_success(event["data"]["object"])
            elif event["type"] == "payment_intent.payment_failed":
                self._handle_payment_failed(event["data"]["object"])

            return {"success": True}
        except ValueError:
            return {"success": False, "error": "Invalid payload"}
        except stripe.error.SignatureVerificationError:
            return {"success": False, "error": "Invalid signature"}

    def refund_payment(self, payment_id, amount=None):
        """Issue a full or partial refund."""
        try:
            kwargs = {"payment_intent": payment_id}
            if amount is not None:
                kwargs["amount"] = amount
            refund = stripe.Refund.create(**kwargs)
            return {"success": True, "refund_id": refund.id}
        except stripe.error.StripeError as e:
            logger.error("Stripe refund error: %s", e)
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _handle_payment_success(self, payment_intent):
        logger.info("Payment succeeded: %s", payment_intent.get("id"))

    def _handle_payment_failed(self, payment_intent):
        logger.warning("Payment failed: %s", payment_intent.get("id"))
