"""Tests for payment routes with mocked DB."""

from unittest.mock import MagicMock, patch

import pytest


def _make_db_mock(fetchone_val=None, fetchall_val=None):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = fetchone_val
    mock_cursor.fetchall.return_value = fetchall_val or []
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn, mock_cursor


def _auth_header(client):
    """Generate a valid JWT token for testing."""
    from backend.auth.jwt_handler import generate_token
    token = generate_token(1, "test@example.com")
    return {"Authorization": f"Bearer {token}"}


class TestPaymentMethods:
    def test_get_methods(self, client):
        resp = client.get("/api/payments/methods")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 3
        ids = [m["id"] for m in data]
        assert "stripe" in ids
        assert "pix" in ids
        assert "dinheiro" in ids


class TestStripeRoutes:
    def test_stripe_intent_requires_auth(self, client):
        resp = client.post("/api/payments/stripe/intent", json={"amount_cents": 1000})
        assert resp.status_code == 401

    def test_stripe_intent_missing_amount(self, client):
        headers = _auth_header(client)
        resp = client.post("/api/payments/stripe/intent", json={}, headers=headers)
        assert resp.status_code == 400

    def test_stripe_intent_invalid_amount(self, client):
        headers = _auth_header(client)
        resp = client.post("/api/payments/stripe/intent", json={"amount_cents": -100}, headers=headers)
        assert resp.status_code == 400

    def test_stripe_intent_no_key_returns_503(self, client):
        headers = _auth_header(client)
        with patch.dict("os.environ", {"STRIPE_SECRET_KEY": ""}):
            resp = client.post(
                "/api/payments/stripe/intent",
                json={"amount_cents": 1000},
                headers=headers,
            )
        assert resp.status_code == 503

    def test_stripe_webhook_bad_signature(self, client):
        resp = client.post(
            "/api/payments/stripe/webhook",
            data=b"payload",
            content_type="application/json",
            headers={"Stripe-Signature": "invalid"},
        )
        assert resp.status_code == 400


class TestPixRoutes:
    def test_pix_qrcode_requires_auth(self, client):
        resp = client.post("/api/payments/pix/qrcode", json={"valor": 10.0})
        assert resp.status_code == 401

    def test_pix_qrcode_missing_valor(self, client):
        headers = _auth_header(client)
        resp = client.post("/api/payments/pix/qrcode", json={}, headers=headers)
        assert resp.status_code == 400

    def test_pix_qrcode_invalid_valor(self, client):
        headers = _auth_header(client)
        resp = client.post("/api/payments/pix/qrcode", json={"valor": -5}, headers=headers)
        assert resp.status_code == 400

    def test_pix_qrcode_success(self, client):
        headers = _auth_header(client)
        resp = client.post(
            "/api/payments/pix/qrcode",
            json={"valor": 25.0, "descricao": "Teste"},
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert "txid" in data
        assert data["valor"] == 25.0

    def test_pix_status_requires_auth(self, client):
        resp = client.get("/api/payments/pix/status/TXID123")
        assert resp.status_code == 401

    def test_pix_status_not_found(self, client):
        headers = _auth_header(client)
        resp = client.get("/api/payments/pix/status/NONEXISTENT", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "nao_encontrado"

    def test_pix_status_after_create(self, client):
        headers = _auth_header(client)
        create_resp = client.post(
            "/api/payments/pix/qrcode",
            json={"valor": 10.0},
            headers=headers,
        )
        txid = create_resp.get_json()["txid"]
        status_resp = client.get(f"/api/payments/pix/status/{txid}", headers=headers)
        assert status_resp.status_code == 200
        assert status_resp.get_json()["txid"] == txid
