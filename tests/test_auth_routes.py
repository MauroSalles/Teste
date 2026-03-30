"""Tests for the auth routes (register & login) — all DB calls are mocked."""
import pytest
from unittest.mock import patch
from datetime import datetime

from backend.app import create_app


@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


_USER_ROW = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
    "level": 1,
    "total_points": 0,
    "created_at": datetime(2024, 1, 1),
}

_USER_WITH_HASH = {
    **_USER_ROW,
    "password_hash": "abc$def",
    "avatar_url": None,
    "deleted_at": None,
    "level_updated_at": None,
}


class TestAuthRoutes:

    # ── Register ──────────────────────────────────────────────────────────────

    def test_register_success(self, client):
        with patch("backend.routes.auth_routes.criar_usuario", return_value=_USER_ROW):
            resp = client.post(
                "/api/auth/register",
                json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
            )
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data
        assert data["user"]["email"] == "alice@example.com"

    def test_register_missing_fields(self, client):
        resp = client.post("/api/auth/register", json={"name": "Alice"})
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        resp = client.post(
            "/api/auth/register",
            json={"name": "Alice", "email": "a@b.com", "password": "123"},
        )
        assert resp.status_code == 400

    def test_register_duplicate_email(self, client):
        def _raise(*args, **kwargs):
            raise Exception("unique constraint violated")

        with patch("backend.routes.auth_routes.criar_usuario", side_effect=_raise):
            resp = client.post(
                "/api/auth/register",
                json={"name": "Alice", "email": "alice@example.com", "password": "secret123"},
            )
        assert resp.status_code == 409

    # ── Login ─────────────────────────────────────────────────────────────────

    def test_login_success(self, client):
        safe_user = {k: v for k, v in _USER_WITH_HASH.items() if k != "password_hash"}
        with patch("backend.routes.auth_routes.autenticar_usuario", return_value=(safe_user, None)):
            resp = client.post(
                "/api/auth/login",
                json={"email": "alice@example.com", "password": "secret123"},
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data
        assert data["user"]["email"] == "alice@example.com"

    def test_login_wrong_password(self, client):
        with patch(
            "backend.routes.auth_routes.autenticar_usuario",
            return_value=(None, "Credenciais inválidas."),
        ):
            resp = client.post(
                "/api/auth/login",
                json={"email": "alice@example.com", "password": "wrongpass"},
            )
        assert resp.status_code == 401
        assert "error" in resp.get_json()

    def test_login_missing_fields(self, client):
        resp = client.post("/api/auth/login", json={"email": "alice@example.com"})
        assert resp.status_code == 400
