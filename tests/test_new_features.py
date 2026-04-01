"""Tests for new API endpoints: feedback, sabor-do-dia, cardápio, health/detailed."""

from unittest.mock import MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sabor(id=1, nome="Chocolate", preco=10.0):
    return {"id": id, "nome": nome, "preco": preco}


def _feedback_row(**kw):
    base = {
        "id": 1,
        "nome": "Mauro",
        "email": "mauro@example.com",
        "mensagem": "Excelente!",
        "nota": 5,
        "criado_em": "2026-01-01T00:00:00",
    }
    base.update(kw)
    return base


# ── Feedback ──────────────────────────────────────────────────────────────────

class TestFeedbackAPI:

    @patch("backend.models.feedback.get_db")
    def test_criar_feedback_sucesso(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = _feedback_row()
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post(
            "/api/feedback",
            json={"nome": "Mauro", "email": "mauro@example.com", "mensagem": "Excelente!", "nota": 5},
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["nota"] == 5

    def test_criar_feedback_sem_nome(self, client):
        resp = client.post("/api/feedback", json={"mensagem": "Ótimo!", "nota": 4})
        assert resp.status_code == 400

    def test_criar_feedback_sem_mensagem(self, client):
        resp = client.post("/api/feedback", json={"nome": "Mauro", "nota": 3})
        assert resp.status_code == 400

    def test_criar_feedback_nota_invalida(self, client):
        resp = client.post(
            "/api/feedback",
            json={"nome": "Mauro", "mensagem": "Ok", "nota": 6},
        )
        assert resp.status_code == 400

    def test_criar_feedback_nota_zero(self, client):
        resp = client.post(
            "/api/feedback",
            json={"nome": "Mauro", "mensagem": "Ok", "nota": 0},
        )
        assert resp.status_code == 400

    def test_criar_feedback_nota_texto(self, client):
        resp = client.post(
            "/api/feedback",
            json={"nome": "Mauro", "mensagem": "Ok", "nota": "ótimo"},
        )
        assert resp.status_code == 400

    @patch("backend.models.feedback.get_db")
    def test_listar_feedback(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_feedback_row()]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/feedback")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    @patch("backend.models.feedback.get_db")
    def test_media_feedback(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"avg": 4.5}
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/feedback/media")
        assert resp.status_code == 200
        assert resp.get_json()["media_nota"] == 4.5


# ── Sabor do Dia ──────────────────────────────────────────────────────────────

class TestSaborDoDia:

    @patch("backend.models.sabor.get_db")
    def test_sabor_do_dia_com_sabores(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_sabor(1, "Chocolate", 10.0), _sabor(2, "Morango", 9.5)]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/sabor-do-dia")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "sabor" in data
        assert "data" in data
        assert "descricao" in data

    @patch("backend.models.sabor.get_db")
    def test_sabor_do_dia_sem_sabores(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/sabor-do-dia")
        assert resp.status_code == 404

    @patch("backend.models.sabor.get_db")
    def test_sabor_do_dia_determinismo(self, mock_db, client):
        """Same day should always return the same flavor."""
        sabores = [_sabor(i, f"Sabor{i}", float(i)) for i in range(1, 6)]
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = sabores
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp1 = client.get("/api/sabor-do-dia")
        resp2 = client.get("/api/sabor-do-dia")
        assert resp1.get_json()["sabor"]["id"] == resp2.get_json()["sabor"]["id"]


# ── Cardápio ──────────────────────────────────────────────────────────────────

class TestCardapioAPI:

    @patch("backend.models.sabor.get_db")
    def test_cardapio_com_info_nutricional(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_sabor(1, "Chocolate", 10.0)]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/cardapio")
        assert resp.status_code == 200
        items = resp.get_json()
        assert len(items) == 1
        assert "nutricional" in items[0]
        assert "alergenos" in items[0]
        assert items[0]["nutricional"]["calorias"] == 216

    @patch("backend.models.sabor.get_db")
    def test_cardapio_sabor_desconhecido_nutricional_vazio(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_sabor(1, "Açaí Exótico", 15.0)]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/cardapio")
        assert resp.status_code == 200
        items = resp.get_json()
        assert items[0]["nutricional"] == {}
        assert items[0]["alergenos"] == []

    @patch("backend.models.sabor.get_db")
    def test_cardapio_sabor_especifico(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [_sabor(3, "Baunilha", 8.0)]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/cardapio/3")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["nome"] == "Baunilha"
        assert "calorias" in data["nutricional"]

    @patch("backend.models.sabor.get_db")
    def test_cardapio_sabor_nao_encontrado(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/cardapio/9999")
        assert resp.status_code == 404


# ── Health Detailed ───────────────────────────────────────────────────────────

class TestHealthDetailed:

    def test_health_basic(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"

    @patch("backend.database.get_db")
    def test_health_detailed_db_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/health/detailed")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["components"]["database"]["status"] == "ok"
        assert "uptime_seconds" in data
        assert "stripe" in data["components"]
        assert "openai" in data["components"]

    @patch("backend.database.get_db")
    def test_health_detailed_db_error(self, mock_db, client):
        mock_db.side_effect = Exception("DB connection refused")

        resp = client.get("/health/detailed")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "degraded"
        assert data["components"]["database"]["status"] == "error"
