"""
Tests for the REST API endpoints added to the Gelateria backend.
Requires a live PostgreSQL test database initialised from database/schema.sql.
"""
import json
import pytest


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "ok"


# ── /api/sabores ──────────────────────────────────────────────────────────────

def test_list_sabores(client):
    res = client.get("/api/sabores")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)


def test_add_sabor(client):
    payload = {"nome": "Test Sabor", "preco": 9.99}
    res = client.post(
        "/api/sabores",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["nome"] == "Test Sabor"
    assert float(data["preco"]) == pytest.approx(9.99)
    return data["id"]


def test_add_sabor_missing_fields(client):
    res = client.post(
        "/api/sabores",
        data=json.dumps({"nome": "Incompleto"}),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_add_sabor_negative_price(client):
    res = client.post(
        "/api/sabores",
        data=json.dumps({"nome": "Negativo", "preco": -5}),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_update_sabor(client):
    # First create
    create_res = client.post(
        "/api/sabores",
        data=json.dumps({"nome": "Sabor Para Atualizar", "preco": 5.00}),
        content_type="application/json",
    )
    sabor_id = create_res.get_json()["id"]

    # Then update
    res = client.put(
        f"/api/sabores/{sabor_id}",
        data=json.dumps({"preco": 12.50}),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert float(data["preco"]) == pytest.approx(12.50)


def test_update_sabor_not_found(client):
    res = client.put(
        "/api/sabores/999999",
        data=json.dumps({"preco": 5.00}),
        content_type="application/json",
    )
    assert res.status_code == 404


def test_delete_sabor(client):
    # Create then delete
    create_res = client.post(
        "/api/sabores",
        data=json.dumps({"nome": "Sabor Para Remover", "preco": 7.00}),
        content_type="application/json",
    )
    sabor_id = create_res.get_json()["id"]

    res = client.delete(f"/api/sabores/{sabor_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert "removido" in data["message"].lower()


def test_delete_sabor_not_found(client):
    res = client.delete("/api/sabores/999999")
    assert res.status_code == 404


# ── /api/pedidos ──────────────────────────────────────────────────────────────

def test_list_pedidos(client):
    res = client.get("/api/pedidos")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_create_pedido(client):
    # Create a flavour to order
    sabor = client.post(
        "/api/sabores",
        data=json.dumps({"nome": "Sabor Pedido Test", "preco": 8.00}),
        content_type="application/json",
    ).get_json()

    res = client.post(
        "/api/pedidos",
        data=json.dumps({"sabor_nome": sabor["nome"], "quantidade": 2}),
        content_type="application/json",
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["sabor"] == sabor["nome"]
    assert data["quantidade"] == 2
    assert float(data["total"]) == pytest.approx(16.00)


def test_create_pedido_missing_fields(client):
    res = client.post(
        "/api/pedidos",
        data=json.dumps({"sabor_nome": "Chocolate"}),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_create_pedido_invalid_sabor(client):
    res = client.post(
        "/api/pedidos",
        data=json.dumps({"sabor_nome": "Sabor Inexistente XYZ", "quantidade": 1}),
        content_type="application/json",
    )
    assert res.status_code == 404


def test_create_pedido_invalid_quantity(client):
    res = client.post(
        "/api/pedidos",
        data=json.dumps({"sabor_nome": "Chocolate", "quantidade": 0}),
        content_type="application/json",
    )
    assert res.status_code == 400


# ── /api/estoque ──────────────────────────────────────────────────────────────

def test_list_estoque(client):
    res = client.get("/api/estoque")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_set_estoque(client):
    # Create a flavour and set its stock
    sabor = client.post(
        "/api/sabores",
        data=json.dumps({"nome": "Sabor Estoque Test", "preco": 9.00}),
        content_type="application/json",
    ).get_json()

    res = client.put(
        f"/api/estoque/{sabor['id']}",
        data=json.dumps({"quantidade": 50}),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert int(data["quantidade"]) == 50


def test_set_estoque_negative(client):
    res = client.put(
        "/api/estoque/1",
        data=json.dumps({"quantidade": -1}),
        content_type="application/json",
    )
    assert res.status_code == 400


# ── /api/dashboard ────────────────────────────────────────────────────────────

def test_dashboard(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.get_json()
    assert "total_sabores" in data
    assert "total_pedidos" in data
    assert "total_receita" in data
    assert "ticket_medio" in data
    assert "top_sabores" in data
    assert "sem_estoque" in data
    assert "estoque_baixo" in data
    assert "alertas_estoque" in data
    assert isinstance(data["top_sabores"], list)
    assert isinstance(data["alertas_estoque"], list)


# ── /cmd (legacy terminal endpoint) ──────────────────────────────────────────

def test_cmd_ajuda(client):
    res = client.post(
        "/cmd",
        data=json.dumps({"comando": "ajuda"}),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "listar sabores" in data["resposta"]


def test_cmd_listar_sabores(client):
    res = client.post(
        "/cmd",
        data=json.dumps({"comando": "listar sabores"}),
        content_type="application/json",
    )
    assert res.status_code == 200


def test_cmd_invalid(client):
    res = client.post(
        "/cmd",
        data=json.dumps({"comando": "comando_inexistente_xyz"}),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "não reconhecido" in data["resposta"]


def test_cmd_too_long(client):
    res = client.post(
        "/cmd",
        data=json.dumps({"comando": "a" * 501}),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_cmd_missing_field(client):
    res = client.post(
        "/cmd",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert res.status_code == 400
