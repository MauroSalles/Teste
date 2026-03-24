"""
Integration tests for HTTP routes (/cmd and /health).
"""
import json
import pytest
from backend.services.cmd_service import processar_comando


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health_returns_ok(client):
    resp = client.get("/health")
    # 200 when DB is up, 503 when DB is unavailable (e.g. no DB in test env)
    assert resp.status_code in (200, 503)
    data = resp.get_json()
    assert data["service"] == "gelateria-backend"
    assert data["status"] in ("ok", "degraded")


# ---------------------------------------------------------------------------
# /cmd — input validation
# ---------------------------------------------------------------------------

def test_cmd_missing_body(client):
    resp = client.post("/cmd", data="not json", content_type="text/plain")
    # Flask 3 returns 415 (Unsupported Media Type) for non-JSON content type
    assert resp.status_code in (400, 415)


def test_cmd_missing_campo_comando(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"outro": "valor"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "inválid" in data["resposta"].lower()


def test_cmd_campo_nao_string(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": 123}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_cmd_muito_longo(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "a" * 501}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "longo" in data["resposta"].lower()


# ---------------------------------------------------------------------------
# /cmd — successful commands
# ---------------------------------------------------------------------------

def test_cmd_ajuda(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "ajuda"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "listar sabores" in data["resposta"]


def test_cmd_listar_sabores_empty(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "listar sabores"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Nenhum" in data["resposta"]


def test_cmd_add_and_list_sabor(client):
    add_resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "add sabor Chocolate 10.00"}),
        content_type="application/json",
    )
    assert add_resp.status_code == 200

    list_resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "listar sabores"}),
        content_type="application/json",
    )
    assert list_resp.status_code == 200
    assert "Chocolate" in list_resp.get_json()["resposta"]


def test_cmd_status(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "status"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Status do Sistema" in data["resposta"]


def test_cmd_desconhecido(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "comandoinvalido"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "não reconhecido" in data["resposta"]
