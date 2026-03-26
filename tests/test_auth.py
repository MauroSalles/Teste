"""Tests for JWT auth utilities (no DB required)."""

import os
import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-key")


def test_create_and_decode_access_token():
    from backend.auth.jwt_handler import create_access_token, decode_token
    token = create_access_token(user_id=42, role="admin")
    payload = decode_token(token)
    assert payload["sub"] == 42
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    from backend.auth.jwt_handler import create_refresh_token, decode_token
    token = create_refresh_token(user_id=7)
    payload = decode_token(token)
    assert payload["sub"] == 7
    assert payload["type"] == "refresh"


def test_blacklist_token():
    from backend.auth.jwt_handler import create_access_token, blacklist_token, is_blacklisted
    token = create_access_token(user_id=1)
    assert not is_blacklisted(token)
    blacklist_token(token)
    assert is_blacklisted(token)


def test_require_auth_missing_token(client):
    resp = client.get("/api/pedidos")
    assert resp.status_code == 401
    data = resp.get_json()
    assert "error" in data


def test_require_admin_missing_token(client):
    resp = client.post("/api/sabores", json={"nome": "Test", "preco": 5.0})
    assert resp.status_code == 401


def test_require_admin_user_role_rejected(client):
    from backend.auth.jwt_handler import create_access_token
    token = create_access_token(user_id=1, role="user")
    resp = client.post(
        "/api/sabores",
        json={"nome": "Test", "preco": 5.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_expired_token_rejected(client):
    import jwt
    import datetime
    payload = {
        "sub": 1,
        "role": "admin",
        "type": "access",
        "exp": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
        "iat": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
    }
    token = jwt.encode(payload, "test-secret-key", algorithm="HS256")
    resp = client.get("/api/pedidos", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
