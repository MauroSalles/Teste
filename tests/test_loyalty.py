"""Tests for loyalty routes with mocked DB."""

from unittest.mock import MagicMock, patch

import pytest


def _auth_header(client):
    from backend.auth.jwt_handler import generate_token
    token = generate_token(1, "test@example.com")
    return {"Authorization": f"Bearer {token}"}


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


class TestReferralRoutes:
    def test_get_referral_requires_auth(self, client):
        resp = client.get("/api/loyalty/referral/1")
        assert resp.status_code == 401

    @patch("backend.loyalty.referral_service.get_db")
    def test_get_referral_existing(self, mock_db, client):
        mock_conn, mock_cursor = _make_db_mock(
            fetchone_val={"id": 1, "user_id": 1, "code": "ACAI-ABCDE", "tier": 1}
        )
        mock_db.return_value = mock_conn
        headers = _auth_header(client)
        resp = client.get("/api/loyalty/referral/1", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == "ACAI-ABCDE"

    @patch("backend.loyalty.referral_service.get_db")
    def test_post_referral_creates(self, mock_db, client):
        mock_conn, mock_cursor = _make_db_mock(
            fetchone_val={"id": 1, "user_id": 1, "code": "ACAI-NEWCO", "tier": 1}
        )
        mock_db.return_value = mock_conn
        headers = _auth_header(client)
        resp = client.post("/api/loyalty/referral/1", headers=headers)
        assert resp.status_code == 201


class TestCouponValidation:
    def test_validate_requires_auth(self, client):
        resp = client.post("/api/loyalty/coupon/validate", json={"code": "TEST10", "order_total": 50})
        assert resp.status_code == 401

    def test_validate_missing_fields(self, client):
        headers = _auth_header(client)
        resp = client.post("/api/loyalty/coupon/validate", json={}, headers=headers)
        assert resp.status_code == 400

    @patch("backend.loyalty.coupon_service.get_db")
    def test_validate_coupon_not_found(self, mock_db, client):
        mock_conn, mock_cursor = _make_db_mock(fetchone_val=None)
        mock_db.return_value = mock_conn
        headers = _auth_header(client)
        resp = client.post(
            "/api/loyalty/coupon/validate",
            json={"code": "INVALID", "order_total": 50},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["valid"] is False

    @patch("backend.loyalty.coupon_service.get_db")
    def test_validate_coupon_valid(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {"id": 1, "code": "SAVE10", "discount_pct": 10.0,
                        "min_order": 20.0, "max_uses_per_user": 2,
                        "max_uses_daily": 5, "expires_at": None}
            return {"cnt": 0}

        mock_cursor.fetchone.side_effect = side_effect
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        headers = _auth_header(client)
        resp = client.post(
            "/api/loyalty/coupon/validate",
            json={"code": "SAVE10", "order_total": 100},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["valid"] is True
        assert data["discount"] > 0


class TestLoyaltyPoints:
    def test_get_points_requires_auth(self, client):
        resp = client.get("/api/loyalty/points/1")
        assert resp.status_code == 401

    @patch("backend.database.get_db")
    def test_get_points_no_record(self, mock_db, client):
        mock_conn, mock_cursor = _make_db_mock(fetchone_val=None)
        mock_db.return_value = mock_conn
        headers = _auth_header(client)
        resp = client.get("/api/loyalty/points/1", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["pontos"] == 0

    @patch("backend.database.get_db")
    def test_get_points_with_record(self, mock_db, client):
        mock_conn, mock_cursor = _make_db_mock(
            fetchone_val={"pontos": 150, "resgates": 3}
        )
        mock_db.return_value = mock_conn
        headers = _auth_header(client)
        resp = client.get("/api/loyalty/points/1", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["pontos"] == 150
