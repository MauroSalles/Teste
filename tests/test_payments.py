"""Tests for payment routes and services."""

import json
from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# JWT / Auth
# ─────────────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_protected_route_without_token_returns_401(self, client):
        resp = client.post("/api/payments/stripe/intent", json={"amount": 10, "order_id": 1})
        assert resp.status_code == 401

    def test_protected_route_with_invalid_token_returns_401(self, client):
        resp = client.post(
            "/api/payments/stripe/intent",
            json={"amount": 10, "order_id": 1},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401

    def test_protected_route_with_valid_token_is_reachable(self, client, auth_headers):
        """A valid token should pass auth (result depends on downstream mock)."""
        with patch(
            "backend.routes.payment_routes.stripe_service.create_payment_intent",
            return_value={"success": True, "client_secret": "pi_test_secret"},
        ):
            resp = client.post(
                "/api/payments/stripe/intent",
                json={"amount": 10.00, "order_id": 1},
                headers=auth_headers,
            )
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Stripe Routes
# ─────────────────────────────────────────────────────────────────────────────

class TestStripeRoutes:
    def test_create_intent_missing_fields_returns_400(self, client, auth_headers):
        resp = client.post(
            "/api/payments/stripe/intent",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_create_intent_success(self, client, auth_headers):
        with patch(
            "backend.routes.payment_routes.stripe_service.create_payment_intent",
            return_value={"success": True, "client_secret": "pi_secret_test"},
        ):
            resp = client.post(
                "/api/payments/stripe/intent",
                json={"amount": 100.00, "order_id": 42},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["client_secret"] == "pi_secret_test"

    def test_create_intent_failure_returns_400(self, client, auth_headers):
        with patch(
            "backend.routes.payment_routes.stripe_service.create_payment_intent",
            return_value={"success": False, "error": "Card declined"},
        ):
            resp = client.post(
                "/api/payments/stripe/intent",
                json={"amount": 100.00, "order_id": 42},
                headers=auth_headers,
            )
        assert resp.status_code == 400

    def test_webhook_endpoint_is_public(self, client):
        """Webhook must not require auth."""
        with patch(
            "backend.routes.payment_routes.stripe_service.process_webhook",
            return_value={"success": True},
        ):
            resp = client.post(
                "/api/payments/stripe/webhook",
                data=b'{"type":"payment_intent.succeeded"}',
                content_type="application/json",
            )
        assert resp.status_code == 200

    def test_refund_missing_payment_id_returns_400(self, client, auth_headers):
        resp = client.post(
            "/api/payments/stripe/refund",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_refund_success(self, client, auth_headers):
        with patch(
            "backend.routes.payment_routes.stripe_service.refund_payment",
            return_value={"success": True, "refund_id": "re_test123"},
        ):
            resp = client.post(
                "/api/payments/stripe/refund",
                json={"payment_id": "pi_test123"},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert resp.get_json()["refund_id"] == "re_test123"


# ─────────────────────────────────────────────────────────────────────────────
# PIX Routes
# ─────────────────────────────────────────────────────────────────────────────

class TestPIXRoutes:
    def test_generate_qr_missing_fields_returns_400(self, client, auth_headers):
        resp = client.post(
            "/api/payments/pix/qrcode",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_generate_qr_success(self, client, auth_headers):
        mock_result = {
            "success": True,
            "qr_code": "00020101...",
            "copy_paste": "00020101...",
            "transaction_id": "order-42",
            "expires_at": "2026-03-26T21:48:00",
        }
        with patch(
            "backend.routes.payment_routes.pix_service.generate_pix_qr_code",
            return_value=mock_result,
        ):
            resp = client.post(
                "/api/payments/pix/qrcode",
                json={"order_id": 42, "amount": 100.00},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "qr_code" in data
        assert "copy_paste" in data

    def test_check_status(self, client, auth_headers):
        with patch(
            "backend.routes.payment_routes.pix_service.check_pix_status",
            return_value={"success": True, "status": 2, "paid": True},
        ):
            resp = client.get(
                "/api/payments/pix/status/order-42",
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert resp.get_json()["paid"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Payment Methods Route
# ─────────────────────────────────────────────────────────────────────────────

class TestPaymentMethodsRoute:
    def test_list_payment_methods(self, client, auth_headers):
        resp = client.get("/api/payments/methods", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "methods" in data


# ─────────────────────────────────────────────────────────────────────────────
# StripePaymentService unit tests
# ─────────────────────────────────────────────────────────────────────────────

class TestStripePaymentService:
    def test_create_payment_intent_success(self):
        from backend.payments.stripe_service import StripePaymentService

        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_secret_xyz"

        with patch("stripe.PaymentIntent.create", return_value=mock_intent):
            service = StripePaymentService()
            result = service.create_payment_intent(100.00, "cus_123", {"order_id": "1"})

        assert result["success"] is True
        assert result["client_secret"] == "pi_secret_xyz"

    def test_create_payment_intent_card_error(self):
        import stripe
        from backend.payments.stripe_service import StripePaymentService

        with patch(
            "stripe.PaymentIntent.create",
            side_effect=stripe.error.CardError("Card declined", None, None),
        ):
            service = StripePaymentService()
            result = service.create_payment_intent(100.00, "cus_123", {})

        assert result["success"] is False
        assert "error" in result

    def test_refund_payment_success(self):
        from backend.payments.stripe_service import StripePaymentService

        mock_refund = MagicMock()
        mock_refund.id = "re_test_123"

        with patch("stripe.Refund.create", return_value=mock_refund):
            service = StripePaymentService()
            result = service.refund_payment("pi_test123", amount=5000)

        assert result["success"] is True
        assert result["refund_id"] == "re_test_123"

    def test_process_webhook_invalid_payload(self):
        import stripe
        from backend.payments.stripe_service import StripePaymentService

        with patch(
            "stripe.Webhook.construct_event",
            side_effect=ValueError("Invalid"),
        ):
            service = StripePaymentService()
            result = service.process_webhook(b"bad_payload", "sig")

        assert result["success"] is False
        assert result["error"] == "Invalid payload"


# ─────────────────────────────────────────────────────────────────────────────
# PIXPaymentService unit tests
# ─────────────────────────────────────────────────────────────────────────────

class TestPIXPaymentService:
    def test_generate_pix_qr_code_success(self):
        from backend.payments.pix_service import PIXPaymentService

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "MerchantOrderId": "order-1",
            "Payment": {
                "QrCodeString": "00020101...",
                "ExpirationDate": "2026-03-26T22:00:00",
            },
        }

        with patch("requests.post", return_value=mock_response):
            service = PIXPaymentService()
            result = service.generate_pix_qr_code(1, 100.00, "test@test.com")

        assert result["success"] is True
        assert "qr_code" in result
        assert "copy_paste" in result

    def test_generate_pix_qr_code_failure(self):
        from backend.payments.pix_service import PIXPaymentService

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("requests.post", return_value=mock_response):
            service = PIXPaymentService()
            result = service.generate_pix_qr_code(1, 100.00, "test@test.com")

        assert result["success"] is False

    def test_check_pix_status_paid(self):
        from backend.payments.pix_service import PIXPaymentService

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Payment": {"Status": 2}
        }

        with patch("requests.get", return_value=mock_response):
            service = PIXPaymentService()
            result = service.check_pix_status("order-1")

        assert result["success"] is True
        assert result["paid"] is True
