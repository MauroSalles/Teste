"""Tests for auth endpoints (register / login / me)."""

from unittest.mock import MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _user_row(id=1, name="Mauro", email="mauro@example.com",
              password_hash="abc$def", level=1, total_points=0,
              created_at="2026-01-01"):
    return {
        "id": id,
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "level": level,
        "total_points": total_points,
        "created_at": created_at,
        "deleted_at": None,
    }


# ── Register ──────────────────────────────────────────────────────────────────

class TestRegister:

    def test_register_missing_fields(self, client):
        resp = client.post("/api/auth/register", json={})
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        resp = client.post("/api/auth/register",
                           json={"name": "Mauro", "email": "m@m.com", "password": "123"})
        assert resp.status_code == 400

    @patch("backend.models.user.get_db")
    def test_register_success(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        user_no_hash = {k: v for k, v in _user_row().items() if k != "password_hash"}
        mock_cursor.fetchone.return_value = user_no_hash
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/auth/register",
                           json={"name": "Mauro", "email": "mauro@example.com",
                                 "password": "secret123"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data
        assert "user" in data

    @patch("backend.models.user.get_db")
    def test_register_duplicate_email(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("unique constraint violated")
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/auth/register",
                           json={"name": "Mauro", "email": "mauro@example.com",
                                 "password": "secret123"})
        assert resp.status_code == 409


# ── Login ─────────────────────────────────────────────────────────────────────

class TestLogin:

    def test_login_missing_fields(self, client):
        resp = client.post("/api/auth/login", json={})
        assert resp.status_code == 400

    @patch("backend.models.user.get_db")
    def test_login_wrong_password(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Return a real hashed password so _verify_password fails for "wrong"
        import hashlib, os
        salt = os.urandom(16)
        digest = hashlib.scrypt(b"correct_password", salt=salt, n=16384, r=8, p=1)
        stored_hash = f"{salt.hex()}${digest.hex()}"
        mock_cursor.fetchone.return_value = _user_row(password_hash=stored_hash)
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/auth/login",
                           json={"email": "mauro@example.com", "password": "wrong"})
        assert resp.status_code == 401

    @patch("backend.models.user.get_db")
    def test_login_success(self, mock_db, client):
        import hashlib, os
        password = "secret123"
        salt = os.urandom(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
        stored_hash = f"{salt.hex()}${digest.hex()}"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _user_row(password_hash=stored_hash)
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/auth/login",
                           json={"email": "mauro@example.com", "password": password})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data


# ── /me endpoint ──────────────────────────────────────────────────────────────

class TestMe:

    def test_me_no_token(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        resp = client.get("/api/auth/me",
                          headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401

    @patch("backend.models.user.get_db")
    def test_me_valid_token(self, mock_db, client):
        from backend.auth.jwt_handler import generate_token
        token = generate_token(1, "mauro@example.com")

        user_public = {k: v for k, v in _user_row().items()
                       if k not in ("password_hash", "deleted_at")}
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = user_public
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/auth/me",
                          headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["email"] == "mauro@example.com"
