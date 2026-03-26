"""Tests for /api/sabores and /api/estoque endpoints."""

import pytest
from backend.auth.jwt_handler import create_access_token


def admin_headers():
    token = create_access_token(user_id=1, role="admin")
    return {"Authorization": f"Bearer {token}"}


def user_headers():
    token = create_access_token(user_id=2, role="user")
    return {"Authorization": f"Bearer {token}"}


# ── GET /api/sabores ──────────────────────────────────────────────────────────

def test_list_sabores_returns_list(client):
    resp = client.get("/api/sabores")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_list_sabores_has_seed_data(client):
    resp = client.get("/api/sabores")
    names = [s["nome"] for s in resp.get_json()]
    assert "Chocolate" in names


# ── POST /api/sabores ─────────────────────────────────────────────────────────

def test_create_sabor_requires_admin(client):
    resp = client.post("/api/sabores", json={"nome": "Manga", "preco": 8.5})
    assert resp.status_code == 401


def test_create_sabor_user_forbidden(client):
    resp = client.post(
        "/api/sabores",
        json={"nome": "Manga", "preco": 8.5},
        headers=user_headers(),
    )
    assert resp.status_code == 403


def test_create_sabor_admin_success(client):
    resp = client.post(
        "/api/sabores",
        json={"nome": "Manga Test", "preco": 8.5},
        headers=admin_headers(),
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["nome"] == "Manga Test"
    assert float(data["preco"]) == 8.5


def test_create_sabor_invalid_preco(client):
    resp = client.post(
        "/api/sabores",
        json={"nome": "X", "preco": -1},
        headers=admin_headers(),
    )
    assert resp.status_code == 400


def test_create_sabor_missing_nome(client):
    resp = client.post(
        "/api/sabores",
        json={"preco": 5.0},
        headers=admin_headers(),
    )
    assert resp.status_code == 400


# ── PUT /api/sabores/<id> ─────────────────────────────────────────────────────

def test_update_sabor_price(client):
    # First get seed data
    resp = client.get("/api/sabores")
    sabors = resp.get_json()
    sabor_id = next(s["id"] for s in sabors if s["nome"] == "Chocolate")

    resp = client.put(
        f"/api/sabores/{sabor_id}",
        json={"preco": 15.0},
        headers=admin_headers(),
    )
    assert resp.status_code == 200
    assert float(resp.get_json()["preco"]) == 15.0


def test_update_sabor_not_found(client):
    resp = client.put(
        "/api/sabores/999999",
        json={"preco": 5.0},
        headers=admin_headers(),
    )
    assert resp.status_code == 404


# ── DELETE /api/sabores/<id> ──────────────────────────────────────────────────

def test_delete_sabor_not_found(client):
    resp = client.delete("/api/sabores/999999", headers=admin_headers())
    assert resp.status_code == 404


# ── GET /api/estoque ──────────────────────────────────────────────────────────

def test_get_estoque_returns_list(client):
    resp = client.get("/api/estoque")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


# ── PUT /api/estoque/<id> ─────────────────────────────────────────────────────

def test_set_estoque_admin(client):
    sabors = client.get("/api/sabores").get_json()
    sabor_id = sabors[0]["id"]

    resp = client.put(
        f"/api/estoque/{sabor_id}",
        json={"quantidade": 50},
        headers=admin_headers(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["quantidade"] == 50


def test_set_estoque_invalid_quantidade(client):
    resp = client.put(
        "/api/estoque/1",
        json={"quantidade": -5},
        headers=admin_headers(),
    )
    assert resp.status_code == 400
