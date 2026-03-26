"""Tests for /api/pedidos endpoint."""

from backend.auth.jwt_handler import create_access_token


def auth_headers():
    token = create_access_token(user_id=1, role="user")
    return {"Authorization": f"Bearer {token}"}


def test_create_pedido_success(client):
    resp = client.post(
        "/api/pedidos",
        json={"sabor": "Chocolate", "quantidade": 2},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["sabor"] == "Chocolate"
    assert data["quantidade"] == 2
    assert abs(data["total"] - data["preco_unitario"] * 2) < 0.01


def test_create_pedido_invalid_sabor(client):
    resp = client.post(
        "/api/pedidos",
        json={"sabor": "Sabor Inexistente XYZABC", "quantidade": 1},
    )
    assert resp.status_code == 404


def test_create_pedido_zero_quantidade(client):
    resp = client.post(
        "/api/pedidos",
        json={"sabor": "Chocolate", "quantidade": 0},
    )
    assert resp.status_code == 400


def test_create_pedido_negative_quantidade(client):
    resp = client.post(
        "/api/pedidos",
        json={"sabor": "Morango", "quantidade": -1},
    )
    assert resp.status_code == 400


def test_create_pedido_missing_sabor(client):
    resp = client.post("/api/pedidos", json={"quantidade": 1})
    assert resp.status_code == 400


def test_list_pedidos_requires_auth(client):
    resp = client.get("/api/pedidos")
    assert resp.status_code == 401


def test_list_pedidos_authenticated(client):
    # create a pedido first
    client.post("/api/pedidos", json={"sabor": "Baunilha", "quantidade": 1})

    resp = client.get("/api/pedidos", headers=auth_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_pedido_estoque_enforcement(client):
    admin_tok = create_access_token(user_id=1, role="admin")
    headers = {"Authorization": f"Bearer {admin_tok}"}

    # Get Morango id
    sabors = client.get("/api/sabores").get_json()
    sabor_id = next(s["id"] for s in sabors if s["nome"] == "Morango")

    # Set stock to 2
    client.put(f"/api/estoque/{sabor_id}", json={"quantidade": 2}, headers=headers)

    # Order 3 should fail
    resp = client.post("/api/pedidos", json={"sabor": "Morango", "quantidade": 3})
    assert resp.status_code == 409
