"""Integration tests for the Flask HTTP routes."""
import json
import pytest


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health_ok(client, clean_db):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] in ("ok", "degraded")


# ---------------------------------------------------------------------------
# /cmd — validation (no DB needed)
# ---------------------------------------------------------------------------

def test_cmd_missing_body(client):
    resp = client.post("/cmd", data="", content_type="application/json")
    assert resp.status_code == 400


def test_cmd_missing_campo_comando(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"other": "value"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "resposta" in data


def test_cmd_comando_nao_string(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": 12345}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_cmd_comando_muito_longo(client):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "a" * 501}),
        content_type="application/json",
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /cmd — functional (requires running DB via clean_db fixture)
# ---------------------------------------------------------------------------

def test_cmd_ajuda(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "ajuda"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "listar sabores" in data["resposta"]


def test_cmd_listar_sabores(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "listar sabores"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "resposta" in data


def test_cmd_add_e_remover_sabor(client, clean_db):
    # Add
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "add sabor IntegracaoTest 7.77"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "IntegracaoTest" in data["resposta"]

    # List to get id
    resp2 = client.post(
        "/cmd",
        data=json.dumps({"comando": "listar sabores"}),
        content_type="application/json",
    )
    lines = resp2.get_json()["resposta"].split("\n")
    sabor_line = next((l for l in lines if "IntegracaoTest" in l), None)
    assert sabor_line is not None
    sabor_id = int(sabor_line.split("|")[0].replace("ID:", "").strip())

    # Remove
    resp3 = client.post(
        "/cmd",
        data=json.dumps({"comando": f"remover sabor {sabor_id}"}),
        content_type="application/json",
    )
    assert resp3.status_code == 200
    assert "removido" in resp3.get_json()["resposta"].lower()


def test_cmd_fazer_pedido(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "fazer pedido TestChocolate 1"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Pedido registrado" in data["resposta"]


def test_cmd_status(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "status"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Status" in data["resposta"]


def test_cmd_ver_estoque(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "ver estoque"}),
        content_type="application/json",
    )
    assert resp.status_code == 200


def test_cmd_set_estoque(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "set estoque TestChocolate 30"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert "30" in resp.get_json()["resposta"]


def test_cmd_limpar(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "limpar"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.get_json()["resposta"] == "__LIMPAR__"


def test_cmd_desconhecido(client, clean_db):
    resp = client.post(
        "/cmd",
        data=json.dumps({"comando": "comando_inexistente_xyz"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert "não reconhecido" in resp.get_json()["resposta"].lower()
