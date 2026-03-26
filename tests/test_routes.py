"""
Integration tests for the Flask routes (/health and /cmd).
"""

import json
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# /health
# ─────────────────────────────────────────────────────────────────────────────

def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "gelateria-backend"
    assert "db" in data


# ─────────────────────────────────────────────────────────────────────────────
# /cmd — validation
# ─────────────────────────────────────────────────────────────────────────────

def test_cmd_missing_body(client):
    resp = client.post("/cmd", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_cmd_missing_field(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_cmd_too_long(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "a" * 501}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_cmd_non_string_field(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": 42}),
        content_type="application/json",
    )
    assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# /cmd — valid commands
# ─────────────────────────────────────────────────────────────────────────────

def _post(client, comando):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": comando}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    return resp.get_json()["resposta"]


def test_cmd_ajuda(client):
    resp = _post(client, "ajuda")
    assert "Comandos disponíveis" in resp


def test_cmd_listar_sabores(client):
    resp = _post(client, "listar sabores")
    assert "Chocolate" in resp


def test_cmd_fazer_pedido(client):
    resp = _post(client, "fazer pedido Chocolate 1")
    assert "Chocolate" in resp


def test_cmd_relatorio_vendas_empty(client):
    resp = _post(client, "relatorio vendas")
    assert "nenhum" in resp.lower()


def test_cmd_total_vendas_after_order(client):
    # Baunilha costs R$8.00 per seed in conftest.py; 3 * 8.00 = 24.00
    _post(client, "fazer pedido Baunilha 3")
    resp = _post(client, "total vendas")
    assert "24.00" in resp   # 3 * 8.00
