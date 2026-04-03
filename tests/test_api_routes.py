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

    def test_criar_pedido_metodo_invalido(self, client):
        resp = client.post("/api/pedidos", json={
            "sabor_id": 1, "quantidade": 2, "metodo_pagamento": "bitcoin"
        })
        assert resp.status_code == 400

    @patch("backend.models.pedido.get_db")
    def test_cancelar_pedido_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "id": 1, "sabor_id": 1, "quantidade": 2,
            "metodo_pagamento": "dinheiro", "status": "cancelado",
            "observacao": None,
        }
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.delete("/api/pedidos/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["message"] == "Pedido cancelado com sucesso"

    @patch("backend.models.pedido.get_db")
    def test_cancelar_pedido_nao_encontrado(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.delete("/api/pedidos/9999")
        assert resp.status_code == 404

    @patch("backend.models.pedido.get_db")
    def test_atualizar_pedido_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "id": 1, "sabor_id": 1, "quantidade": 5,
            "metodo_pagamento": "pix", "status": "confirmado",
            "observacao": None,
        }
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.put("/api/pedidos/1", json={"metodo_pagamento": "pix"})
        assert resp.status_code == 200

    def test_atualizar_pedido_status_invalido(self, client):
        resp = client.put("/api/pedidos/1", json={"status": "finalizado"})
        assert resp.status_code == 400

    def test_atualizar_pedido_metodo_invalido(self, client):
        resp = client.put("/api/pedidos/1", json={"metodo_pagamento": "bitcoin"})
        assert resp.status_code == 400

    def test_atualizar_pedido_quantidade_invalida(self, client):
        resp = client.put("/api/pedidos/1", json={"quantidade": -3})
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


# ── Estoque Self-Service (estoque_sabores) ────────────────────────────────────

def _estoque_sabor(**kw):
    defaults = {
        "id": 1, "nome": "Açaí tradicional", "volume_litros": 10.0,
        "categoria": "açaí", "em_exposicao": True, "quantidade_atual": 5,
        "estoque_minimo_sugestao": 10, "resposicao_rapida": True,
        "data_atualizacao": "2026-01-01T00:00:00",
    }
    defaults.update(kw)
    return defaults


class TestEstoqueSaboresAPI:

    def _mock_db(self, rows=None, row=None):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = rows if rows is not None else []
        mock_cursor.fetchone.return_value = row
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        return mock_conn

    @patch("backend.models.estoque_sabores.get_db")
    def test_listar_estoque_sabores(self, mock_db, client):
        mock_db.return_value = self._mock_db(rows=[_estoque_sabor()])
        resp = client.get("/api/estoque/sabores")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["nome"] == "Açaí tradicional"

    @patch("backend.models.estoque_sabores.get_db")
    def test_resumo_estoque_sabores(self, mock_db, client):
        mock_db.return_value = self._mock_db(rows=[
            _estoque_sabor(),
            _estoque_sabor(id=2, nome="Chocolate belga", categoria="sorvete",
                           quantidade_atual=0, estoque_minimo_sugestao=1,
                           resposicao_rapida=True),
        ])
        resp = client.get("/api/estoque/sabores/resumo")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 2
        assert data["acai"] == 1
        assert data["sorvete"] == 1
        assert data["faltando"] == 2
        assert data["reposicao_rapida"] == 2

    @patch("backend.models.estoque_sabores.get_db")
    def test_estoque_faltando(self, mock_db, client):
        mock_db.return_value = self._mock_db(rows=[_estoque_sabor()])
        resp = client.get("/api/estoque/faltando")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_pedido_semanal_sem_itens(self, client):
        resp = client.post("/api/estoque/pedido-semanal", json={})
        assert resp.status_code == 400

    def test_pedido_semanal_lista_vazia(self, client):
        resp = client.post("/api/estoque/pedido-semanal", json={"itens": []})
        assert resp.status_code == 400

    def test_pedido_semanal_item_invalido(self, client):
        resp = client.post("/api/estoque/pedido-semanal",
                           json={"itens": [{"estoque_sabor_id": 1, "quantidade": -1}]})
        assert resp.status_code == 400

    @patch("backend.models.estoque_sabores.get_db")
    def test_pedido_semanal_ok(self, mock_db, client):
        mock_db.return_value = self._mock_db(row={
            "id": 1, "data_pedido": "2026-01-01T00:00:00",
            "itens": [{"estoque_sabor_id": 1, "quantidade": 3}],
            "observacao": None, "status": "pendente",
        })
        resp = client.post("/api/estoque/pedido-semanal",
                           json={"itens": [{"estoque_sabor_id": 1, "quantidade": 3}]})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "pendente"

    def test_atualizar_sem_itens(self, client):
        resp = client.post("/api/estoque/atualizar", json={})
        assert resp.status_code == 400

    def test_atualizar_lista_vazia(self, client):
        resp = client.post("/api/estoque/atualizar", json={"itens": []})
        assert resp.status_code == 400

    def test_atualizar_item_invalido(self, client):
        resp = client.post("/api/estoque/atualizar",
                           json={"itens": [{"estoque_sabor_id": 1, "quantidade": 0}]})
        assert resp.status_code == 400

    @patch("backend.models.estoque_sabores.get_db")
    def test_atualizar_ok(self, mock_db, client):
        mock_db.return_value = self._mock_db(row=_estoque_sabor(quantidade_atual=8))
        resp = client.post("/api/estoque/atualizar",
                           json={"itens": [{"estoque_sabor_id": 1, "quantidade": 3}]})
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)


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
