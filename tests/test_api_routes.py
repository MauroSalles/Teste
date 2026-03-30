"""Tests for the REST API routes (all DB calls are mocked)."""
import pytest
from contextlib import contextmanager
from unittest.mock import MagicMock, patch
from datetime import datetime

from backend.app import create_app


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

SABOR_1 = {"id": 1, "nome": "Chocolate", "preco": 10.00}
SABOR_2 = {"id": 2, "nome": "Morango", "preco": 9.50}
PEDIDO_1 = {"id": 1, "sabor": "Chocolate", "quantidade": 2, "data": datetime(2024, 1, 1, 12, 0)}
ESTOQUE_1 = {"id": 1, "sabor_id": 1, "quantidade": 20}
ESTOQUE_VIEW_1 = {"id": 1, "nome": "Chocolate", "quantidade": 20}


# ─────────────────────────────────────────────────────────────────────────────
# Sabores
# ─────────────────────────────────────────────────────────────────────────────

class TestSaboresAPI:

    def test_get_sabores(self, client):
        with patch("backend.routes.api_routes.listar_sabores", return_value=[SABOR_1, SABOR_2]):
            resp = client.get("/api/sabores")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["sabores"]) == 2
        assert data["sabores"][0]["nome"] == "Chocolate"

    def test_post_sabores_success(self, client):
        with patch("backend.routes.api_routes.adicionar_sabor", return_value=SABOR_1):
            resp = client.post("/api/sabores", json={"nome": "Chocolate", "preco": 10.00})
        assert resp.status_code == 201
        assert resp.get_json()["sabor"]["nome"] == "Chocolate"

    def test_post_sabores_missing_nome(self, client):
        resp = client.post("/api/sabores", json={"preco": 10.00})
        assert resp.status_code == 400

    def test_post_sabores_invalid_preco(self, client):
        resp = client.post("/api/sabores", json={"nome": "Teste", "preco": "abc"})
        assert resp.status_code == 400

    def test_post_sabores_negative_preco(self, client):
        resp = client.post("/api/sabores", json={"nome": "Teste", "preco": -5})
        assert resp.status_code == 400

    def test_put_sabor_success(self, client):
        updated = {"id": 1, "nome": "Chocolate", "preco": 12.00}
        with patch("backend.routes.api_routes.atualizar_sabor", return_value=updated):
            resp = client.put("/api/sabores/1", json={"preco": 12.00})
        assert resp.status_code == 200
        assert resp.get_json()["sabor"]["preco"] == 12.00

    def test_put_sabor_not_found(self, client):
        with patch("backend.routes.api_routes.atualizar_sabor", return_value=None):
            resp = client.put("/api/sabores/999", json={"preco": 12.00})
        assert resp.status_code == 404

    def test_put_sabor_invalid_preco(self, client):
        resp = client.put("/api/sabores/1", json={"preco": "nope"})
        assert resp.status_code == 400

    def test_delete_sabor_success(self, client):
        with patch("backend.routes.api_routes.remover_sabor", return_value=SABOR_1):
            resp = client.delete("/api/sabores/1")
        assert resp.status_code == 200
        assert "removido" in resp.get_json()["message"]

    def test_delete_sabor_not_found(self, client):
        with patch("backend.routes.api_routes.remover_sabor", return_value=None):
            resp = client.delete("/api/sabores/999")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Pedidos
# ─────────────────────────────────────────────────────────────────────────────

class TestPedidosAPI:

    def test_get_pedidos(self, client):
        with patch("backend.routes.api_routes.listar_pedidos", return_value=[PEDIDO_1]):
            resp = client.get("/api/pedidos")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["pedidos"]) == 1

    def test_post_pedidos_by_id_success(self, client):
        pedido_row = {"id": 1, "sabor_id": 1, "quantidade": 2, "data": None}
        with patch("backend.routes.api_routes.listar_sabores", return_value=[SABOR_1]), \
             patch("backend.routes.api_routes.obter_estoque", return_value=0), \
             patch("backend.routes.api_routes.criar_pedido", return_value=pedido_row):
            resp = client.post("/api/pedidos", json={"sabor_id": 1, "quantidade": 2})
        assert resp.status_code == 201

    def test_post_pedidos_by_name_success(self, client):
        pedido_row = {"id": 1, "sabor_id": 1, "quantidade": 1, "data": None}
        with patch("backend.routes.api_routes.buscar_sabor_por_nome", return_value=SABOR_1), \
             patch("backend.routes.api_routes.obter_estoque", return_value=0), \
             patch("backend.routes.api_routes.criar_pedido", return_value=pedido_row):
            resp = client.post("/api/pedidos", json={"sabor": "Chocolate", "quantidade": 1})
        assert resp.status_code == 201

    def test_post_pedidos_invalid_quantidade(self, client):
        resp = client.post("/api/pedidos", json={"sabor_id": 1, "quantidade": 0})
        assert resp.status_code == 400

    def test_post_pedidos_sabor_not_found(self, client):
        with patch("backend.routes.api_routes.listar_sabores", return_value=[]):
            resp = client.post("/api/pedidos", json={"sabor_id": 999, "quantidade": 1})
        assert resp.status_code == 404

    def test_post_pedidos_sem_sabor_field(self, client):
        resp = client.post("/api/pedidos", json={"quantidade": 1})
        assert resp.status_code == 400

    def test_post_pedidos_estoque_insuficiente(self, client):
        with patch("backend.routes.api_routes.listar_sabores", return_value=[SABOR_1]), \
             patch("backend.routes.api_routes.obter_estoque", return_value=1):
            resp = client.post("/api/pedidos", json={"sabor_id": 1, "quantidade": 5})
        assert resp.status_code == 409


# ─────────────────────────────────────────────────────────────────────────────
# Estoque
# ─────────────────────────────────────────────────────────────────────────────

class TestEstoqueAPI:

    def test_get_estoque(self, client):
        with patch("backend.routes.api_routes.ver_estoque", return_value=[ESTOQUE_VIEW_1]):
            resp = client.get("/api/estoque")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["estoque"]) == 1

    def test_put_estoque_set_quantidade(self, client):
        with patch("backend.routes.api_routes.definir_estoque", return_value=ESTOQUE_1):
            resp = client.put("/api/estoque/1", json={"quantidade": 50})
        assert resp.status_code == 200
        assert resp.get_json()["estoque"]["quantidade"] == 20

    def test_put_estoque_delta(self, client):
        with patch("backend.routes.api_routes.ajustar_estoque", return_value=ESTOQUE_1):
            resp = client.put("/api/estoque/1", json={"delta": 10})
        assert resp.status_code == 200

    def test_put_estoque_invalid_quantidade(self, client):
        resp = client.put("/api/estoque/1", json={"quantidade": -1})
        assert resp.status_code == 400

    def test_put_estoque_no_field(self, client):
        resp = client.put("/api/estoque/1", json={})
        assert resp.status_code == 400

    def test_put_estoque_not_found(self, client):
        with patch("backend.routes.api_routes.definir_estoque", return_value=None):
            resp = client.put("/api/estoque/999", json={"quantidade": 10})
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

class TestDashboardAPI:

    def test_get_dashboard(self, client):
        estoque_items = [
            {"id": 1, "nome": "Chocolate", "quantidade": 10},
            {"id": 2, "nome": "Morango", "quantidade": 0},
            {"id": 3, "nome": "Baunilha", "quantidade": 3},
        ]
        with patch("backend.routes.api_routes.listar_sabores", return_value=[SABOR_1, SABOR_2]), \
             patch("backend.routes.api_routes.listar_pedidos", return_value=[PEDIDO_1]), \
             patch("backend.routes.api_routes.ver_estoque", return_value=estoque_items):
            resp = client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_sabores"] == 2
        assert data["total_pedidos"] == 1
        assert len(data["sem_estoque"]) == 1
        assert data["sem_estoque"][0]["nome"] == "Morango"
        assert len(data["estoque_baixo"]) == 1
        assert data["estoque_baixo"][0]["nome"] == "Baunilha"
