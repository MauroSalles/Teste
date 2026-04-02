"""Smoke tests for Gelateria Pro v4.0 — Presence First blueprints.

Tests cover:
  - GET /api/daily/sabor          → 200
  - GET /api/daily/humor/media    → 200
  - GET /api/daily/streak/1       → 200
  - GET /api/clube/planos         → 200 with 3 plans
  - GET /api/feed                 → 200 with posts key
  - GET /api/feed/trending        → 200
  - GET /api/feed/usuario/1       → 200
  - GET /api/gelinho/conversa     → 401 (no token)
  - GET /api/gelinho/frase-do-dia → 401 (no token)
  - GET /api/gelinho/dica         → 401 (no token)
  - GET /api/eventos/ativo        → 200
  - GET /api/qrcode/mesa/5        → 200 SVG
  - GET /api/aniversariantes/hoje → 200
"""

import pytest
from unittest.mock import MagicMock, patch

from backend.app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


# ── Daily ──────────────────────────────────────────────────────────────────────

class TestDailyRoutes:

    @patch("backend.routes.daily_routes.get_db")
    def test_sabor_do_dia(self, mock_db, client):
        """GET /api/daily/sabor returns deterministic daily flavor."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            {"id": 1, "nome": "Chocolate", "preco": 10.0},
            {"id": 2, "nome": "Morango", "preco": 9.5},
        ]
        cursor.__enter__ = lambda s: s
        cursor.__exit__ = MagicMock(return_value=False)
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = conn

        r = client.get("/api/daily/sabor")
        assert r.status_code == 200
        d = r.get_json()
        assert "nome" in d
        assert "preco_com_desconto" in d
        assert d["desconto_percent"] == 10

    def test_sabor_do_dia_fallback(self, client):
        """GET /api/daily/sabor returns fallback when DB is unavailable."""
        r = client.get("/api/daily/sabor")
        assert r.status_code == 200
        d = r.get_json()
        assert "nome" in d

    @patch("backend.routes.daily_routes.get_db")
    def test_humor_media(self, mock_db, client):
        """GET /api/daily/humor/media returns mood counts."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            {"humor": "feliz", "total": 5},
            {"humor": "triste", "total": 2},
        ]
        cursor.__enter__ = lambda s: s
        cursor.__exit__ = MagicMock(return_value=False)
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = conn

        r = client.get("/api/daily/humor/media")
        assert r.status_code == 200
        d = r.get_json()
        assert "feliz" in d
        assert "triste" in d

    @patch("backend.routes.daily_routes.get_db")
    def test_streak_endpoint(self, mock_db, client):
        """GET /api/daily/streak/<id> returns streak info."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = {"streak_atual": 7}
        cursor.__enter__ = lambda s: s
        cursor.__exit__ = MagicMock(return_value=False)
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = conn

        r = client.get("/api/daily/streak/1")
        assert r.status_code == 200
        d = r.get_json()
        assert d["streak"] == 7

    def test_checkin_requires_auth(self, client):
        """POST /api/daily/checkin requires JWT."""
        r = client.post("/api/daily/checkin")
        assert r.status_code == 401


# ── Clube ──────────────────────────────────────────────────────────────────────

class TestClubeRoutes:

    def test_listar_planos(self, client):
        """GET /api/clube/planos returns 3 plans."""
        r = client.get("/api/clube/planos")
        assert r.status_code == 200
        d = r.get_json()
        assert isinstance(d, list)
        assert len(d) == 3
        nomes = [p["nome"] for p in d]
        assert any("Bronze" in n for n in nomes)
        assert any("Prata" in n for n in nomes)
        assert any("Ouro" in n for n in nomes)

    def test_assinar_requires_auth(self, client):
        """POST /api/clube/assinar requires JWT."""
        r = client.post("/api/clube/assinar", json={"plano": "bronze"})
        assert r.status_code == 401

    def test_meu_plano_requires_auth(self, client):
        """GET /api/clube/meu-plano requires JWT."""
        r = client.get("/api/clube/meu-plano")
        assert r.status_code == 401

    def test_cancelar_requires_auth(self, client):
        """POST /api/clube/cancelar requires JWT."""
        r = client.post("/api/clube/cancelar")
        assert r.status_code == 401


# ── Feed ──────────────────────────────────────────────────────────────────────

class TestFeedRoutes:

    @patch("backend.routes.feed_routes.get_db")
    def test_listar_feed(self, mock_db, client):
        """GET /api/feed returns posts list."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.__enter__ = lambda s: s
        cursor.__exit__ = MagicMock(return_value=False)
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = conn

        r = client.get("/api/feed")
        assert r.status_code == 200
        d = r.get_json()
        assert "posts" in d

    @patch("backend.routes.feed_routes.get_db")
    def test_trending(self, mock_db, client):
        """GET /api/feed/trending returns trending key."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.__enter__ = lambda s: s
        cursor.__exit__ = MagicMock(return_value=False)
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = conn

        r = client.get("/api/feed/trending")
        assert r.status_code == 200
        d = r.get_json()
        assert "trending" in d

    @patch("backend.routes.feed_routes.get_db")
    def test_feed_usuario(self, mock_db, client):
        """GET /api/feed/usuario/<id> returns user posts."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.__enter__ = lambda s: s
        cursor.__exit__ = MagicMock(return_value=False)
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = conn

        r = client.get("/api/feed/usuario/1")
        assert r.status_code == 200
        d = r.get_json()
        assert "posts" in d

    def test_criar_post_requires_auth(self, client):
        """POST /api/feed/post requires JWT."""
        r = client.post("/api/feed/post", json={"conteudo": "test"})
        assert r.status_code == 401

    def test_curtir_requires_auth(self, client):
        """POST /api/feed/<id>/curtir requires JWT."""
        r = client.post("/api/feed/1/curtir")
        assert r.status_code == 401


# ── Gelinho ───────────────────────────────────────────────────────────────────

class TestGelinhoRoutes:

    def test_conversa_requires_auth(self, client):
        """POST /api/gelinho/conversa requires JWT."""
        r = client.post("/api/gelinho/conversa", json={"mensagem": "oi"})
        assert r.status_code == 401

    def test_frase_requires_auth(self, client):
        """GET /api/gelinho/frase-do-dia requires JWT."""
        r = client.get("/api/gelinho/frase-do-dia")
        assert r.status_code == 401

    def test_dica_requires_auth(self, client):
        """GET /api/gelinho/dica requires JWT."""
        r = client.get("/api/gelinho/dica")
        assert r.status_code == 401


# ── Presence ──────────────────────────────────────────────────────────────────

class TestPresenceRoutes:

    def test_evento_ativo(self, client):
        """GET /api/eventos/ativo returns seasonal event."""
        r = client.get("/api/eventos/ativo")
        assert r.status_code == 200
        d = r.get_json()
        assert "nome" in d
        assert "emoji" in d
        assert "cor" in d

    def test_qrcode_mesa(self, client):
        """GET /api/qrcode/mesa/<n> returns SVG."""
        r = client.get("/api/qrcode/mesa/5")
        assert r.status_code == 200
        assert b"svg" in r.data.lower()

    def test_qrcode_mesa_invalida(self, client):
        """GET /api/qrcode/mesa/0 returns 400."""
        r = client.get("/api/qrcode/mesa/0")
        assert r.status_code == 400

    @patch("backend.routes.presence_routes.get_db")
    def test_aniversariantes_hoje(self, mock_db, client):
        """GET /api/aniversariantes/hoje returns birthday list."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.__enter__ = lambda s: s
        cursor.__exit__ = MagicMock(return_value=False)
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: s
        conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = conn

        r = client.get("/api/aniversariantes/hoje")
        assert r.status_code == 200
        d = r.get_json()
        assert "aniversariantes" in d
        assert "data" in d
