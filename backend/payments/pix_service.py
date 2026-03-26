import os
import logging
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger(__name__)


class PIXPaymentService:
    """Dynamic PIX with real-time QR code via Braspag/Cielo."""

    def __init__(self):
        self.api_url = os.getenv("BRASPAG_API_URL", "")
        self.merchant_id = os.getenv("BRASPAG_MERCHANT_ID", "")
        self.api_key = os.getenv("BRASPAG_API_KEY", "")

    def generate_pix_qr_code(self, order_id, amount, customer_email):
        """Generate a dynamic PIX QR code."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "MerchantOrderId": str(order_id),
            "Customer": {
                "Name": customer_email,
                "Email": customer_email,
            },
            "Payment": {
                "Type": "Pix",
                "Amount": int(float(amount) * 100),
                "Installments": 1,
                "Capture": True,
                "ExpirationDate": (
                    datetime.now(timezone.utc) + timedelta(hours=1)
                ).isoformat(),
            },
        }

        try:
            response = requests.post(
                f"{self.api_url}/sales",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "qr_code": data["Payment"]["QrCodeString"],
                    "copy_paste": data["Payment"]["QrCodeString"],
                    "transaction_id": data["MerchantOrderId"],
                    "expires_at": data["Payment"]["ExpirationDate"],
                }
            logger.error("PIX API error %s: %s", response.status_code, response.text)
            return {"success": False, "error": "PIX generation failed"}
        except requests.RequestException as exc:
            logger.error("PIX request failed: %s", exc)
            return {"success": False, "error": str(exc)}

    def check_pix_status(self, transaction_id):
        """Check PIX payment status in real time."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(
                f"{self.api_url}/sales/{transaction_id}",
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                status = data["Payment"]["Status"]
                return {
                    "success": True,
                    "status": status,
                    "paid": status == 2,  # 2 = payment received
                }
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except requests.RequestException as exc:
            logger.error("PIX status check failed: %s", exc)
            return {"success": False, "error": str(exc)}
