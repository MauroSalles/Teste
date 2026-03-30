"""Tests for REST API endpoints using Flask test client (DB mocked)."""

from unittest.mock import MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sabor(id=1, nome="Chocolate", preco=10.0):
    return {"id": id, "nome": nome, "preco": preco}


def _pedido(id=1, sabor="Chocolate", quantidade=2, data="2026-01-01T00:00:00"):
    return {"id": id, "sabor": sabor, "quantidade": quantidade, "data": data}


def _estoque(id=1, nome="Chocolate", quantidade=10):
    return {"id": id, "nome": nome, "quantidade": quantidade}


# ── Sabores ───────────────────────────────────────────────────────────────────

class TestSaboresAPI:

    @patch("backend.models.sabor.get_db")
    def test_listar_sabores(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_sabor()]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/sabores")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    @patch("backend.models.sabor.get_db")
    def test_criar_sabor(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _sabor()
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/sabores", json={"nome": "Chocolate", "preco": 10.0})
        assert resp.status_code == 201

    def test_criar_sabor_sem_dados(self, client):
        resp = client.post("/api/sabores", json={})
        assert resp.status_code == 400

    def test_criar_sabor_preco_invalido(self, client):
        resp = client.post("/api/sabores", json={"nome": "Menta", "preco": "abc"})
        assert resp.status_code == 400

    @patch("backend.models.sabor.get_db")
    def test_remover_sabor_nao_encontrado(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.delete("/api/sabores/9999")
        assert resp.status_code == 404


# ── Pedidos ───────────────────────────────────────────────────────────────────

class TestPedidosAPI:

    @patch("backend.models.pedido.get_db")
    def test_listar_pedidos(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_pedido()]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/pedidos")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_criar_pedido_sem_dados(self, client):
        resp = client.post("/api/pedidos", json={})
        assert resp.status_code == 400

    def test_criar_pedido_quantidade_invalida(self, client):
        resp = client.post("/api/pedidos", json={"sabor_id": 1, "quantidade": -1})
        assert resp.status_code == 400


# ── Estoque ───────────────────────────────────────────────────────────────────

class TestEstoqueAPI:

    @patch("backend.models.estoque.get_db")
    def test_listar_estoque(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_estoque()]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/estoque")
        assert resp.status_code == 200

    def test_set_estoque_sem_quantidade(self, client):
        resp = client.put("/api/estoque/1", json={})
        assert resp.status_code == 400

    def test_set_estoque_quantidade_negativa(self, client):
        resp = client.put("/api/estoque/1", json={"quantidade": -5})
        assert resp.status_code == 400


# ── Status endpoint ────────────────────────────────────────────────────────────

class TestStatusAPI:

    @patch("backend.models.estoque.get_db")
    @patch("backend.models.pedido.get_db")
    @patch("backend.models.sabor.get_db")
    def test_status(self, mock_sabor_db, mock_pedido_db, mock_estoque_db, client):
        def _make_mock(rows=None, row=None):
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = rows or []
            mock_cursor.fetchone.return_value = row
            mock_cursor.__enter__ = lambda s: s
            mock_cursor.__exit__ = MagicMock(return_value=False)
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = lambda s: s
            mock_conn.__exit__ = MagicMock(return_value=False)
            return mock_conn

        mock_sabor_db.return_value = _make_mock(rows=[_sabor()])
        mock_pedido_db.return_value = _make_mock(rows=[_pedido()])
        mock_estoque_db.return_value = _make_mock(rows=[_estoque()])

        resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total_sabores" in data
        assert "total_pedidos" in data
        assert "receita_total" in data


# ── Relatórios ────────────────────────────────────────────────────────────────

class TestRelatoriosAPI:

    def test_relatorio_periodo_invalido(self, client):
        resp = client.get("/api/relatorios/vendas?periodo=anual")
        assert resp.status_code == 400

    @patch("backend.models.pedido.get_db")
    def test_relatorio_diario(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/relatorios/vendas?periodo=diario")
        assert resp.status_code == 200

    @patch("backend.models.pedido.get_db")
    def test_sabores_populares(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/relatorios/sabores-populares")
        assert resp.status_code == 200
