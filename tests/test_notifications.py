"""Tests for notification routes."""

from unittest.mock import patch, MagicMock

import pytest


def _auth_header(client):
    from backend.auth.jwt_handler import generate_token
    token = generate_token(1, "test@example.com")
    return {"Authorization": f"Bearer {token}"}


class TestNotificationPreferences:
    def test_get_preferences_requires_auth(self, client):
        resp = client.get("/api/notifications/preferences")
        assert resp.status_code == 401

    def test_get_preferences_returns_defaults(self, client):
        headers = _auth_header(client)
        resp = client.get("/api/notifications/preferences", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "preferences" in data
        prefs = data["preferences"]
        assert "email" in prefs

    def test_post_preferences_requires_auth(self, client):
        resp = client.post("/api/notifications/preferences", json={"email": False})
        assert resp.status_code == 401

    def test_post_preferences_updates(self, client):
        headers = _auth_header(client)
        resp = client.post(
            "/api/notifications/preferences",
            json={"email": False, "push": True},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["preferences"]["push"] is True

    def test_post_preferences_ignores_unknown_fields(self, client):
        headers = _auth_header(client)
        resp = client.post(
            "/api/notifications/preferences",
            json={"email": True, "unknown_field": "ignored"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "unknown_field" not in data["preferences"]


class TestSendTest:
    def test_send_test_requires_auth(self, client):
        resp = client.post("/api/notifications/send-test")
        assert resp.status_code == 401

    def test_send_test_success(self, client):
        headers = _auth_header(client)
        with patch("backend.notifications.email_service.send_order_confirmation") as mock_send:
            mock_send.return_value = False
            resp = client.post("/api/notifications/send-test", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "message" in data


class TestEmailService:
    def test_send_order_no_key_returns_false(self):
        from backend.notifications.email_service import send_order_confirmation
        import os
        os.environ.pop("SENDGRID_API_KEY", None)
        result = send_order_confirmation("test@example.com", 1, [], 10.0)
        assert result is False

    def test_send_coupon_no_key_returns_false(self):
        from backend.notifications.email_service import send_coupon_email
        import os
        os.environ.pop("SENDGRID_API_KEY", None)
        result = send_coupon_email("test@example.com", "PROMO10", 5.0)
        assert result is False

    def test_send_low_stock_no_key_returns_false(self):
        from backend.notifications.email_service import send_low_stock_alert
        import os
        os.environ.pop("SENDGRID_API_KEY", None)
        result = send_low_stock_alert("admin@example.com", "Chocolate", 2)
        assert result is False


class TestWebsocketService:
    def test_notify_order_no_error(self):
        from backend.notifications.websocket_service import notify_order
        notify_order({"sabor": "Chocolate", "quantidade": 2})

    def test_notify_stock_no_error(self):
        from backend.notifications.websocket_service import notify_stock_update
        notify_stock_update({"nome": "Morango", "quantidade": 5})
