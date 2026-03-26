import os
import logging

import paypalrestsdk

logger = logging.getLogger(__name__)


class PayPalPaymentService:
    """PayPal payments for multiple countries."""

    def __init__(self):
        paypalrestsdk.configure(
            {
                "mode": os.getenv("PAYPAL_MODE", "sandbox"),
                "client_id": os.getenv("PAYPAL_CLIENT_ID", ""),
                "client_secret": os.getenv("PAYPAL_CLIENT_SECRET", ""),
            }
        )

    def create_payment(self, amount, description, return_url, cancel_url=None):
        """Create a PayPal payment and return the approval URL."""
        if cancel_url is None:
            cancel_url = return_url

        payment = paypalrestsdk.Payment(
            {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                },
                "transactions": [
                    {
                        "amount": {
                            "total": f"{float(amount):.2f}",
                            "currency": "BRL",
                            "details": {"subtotal": f"{float(amount):.2f}"},
                        },
                        "description": description,
                    }
                ],
            }
        )

        if payment.create():
            approval_url = next(
                (link.href for link in payment.links if link.rel == "approval_url"),
                None,
            )
            return {
                "success": True,
                "approval_url": approval_url,
                "payment_id": payment.id,
            }

        logger.error("PayPal payment creation failed: %s", payment.error)
        return {"success": False, "error": payment.error}

    def execute_payment(self, payment_id, payer_id):
        """Execute a previously approved PayPal payment."""
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            return {"success": True, "payment_id": payment.id}
        logger.error("PayPal execute failed: %s", payment.error)
        return {"success": False, "error": payment.error}
