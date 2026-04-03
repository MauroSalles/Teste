"""Tests for missing endpoints: PUT sabores, fidelidade, CMD HTTP, gamification routes, error handlers."""

from unittest.mock import MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mock_db(rows=None, row=None, side_effect=None):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    if side_effect:
        mock_cursor.execute.side_effect = side_effect
    mock_cursor.fetchall.return_value = rows if rows is not None else []
    mock_cursor.fetchone.return_value = row
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def _sabor(id=1, nome="Chocolate", preco=10.0):
    return {"id": id, "nome": nome, "preco": preco}


# ── PUT /api/sabores/<id> ─────────────────────────────────────────────────────

class TestAtualizarSaborAPI:

    @patch("backend.models.sabor.get_db")
    def test_atualizar_sabor_ok(self, mock_db, client):
        mock_db.return_value = _mock_db(row=_sabor(preco=15.0))
        resp = client.put("/api/sabores/1", json={"preco": 15.0})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["preco"] == 15.0

    def test_atualizar_sabor_sem_preco(self, client):
        resp = client.put("/api/sabores/1", json={})
        assert resp.status_code == 400

    def test_atualizar_sabor_preco_negativo(self, client):
        resp = client.put("/api/sabores/1", json={"preco": -5})
        assert resp.status_code == 400

    def test_atualizar_sabor_preco_invalido(self, client):
        resp = client.put("/api/sabores/1", json={"preco": "abc"})
        assert resp.status_code == 400

    @patch("backend.models.sabor.get_db")
    def test_atualizar_sabor_nao_encontrado(self, mock_db, client):
        mock_db.return_value = _mock_db(row=None)
        resp = client.put("/api/sabores/9999", json={"preco": 15.0})
        assert resp.status_code == 404


# ── Fidelidade ────────────────────────────────────────────────────────────────

class TestFidelidadeAPI:

    @patch("backend.models.fidelidade.get_db")
    def test_get_pontos_existente(self, mock_db, client):
        mock_db.return_value = _mock_db(
            row={"user_id": 1, "pontos": 50, "resgates": 0, "updated_at": "2026-01-01"}
        )
        resp = client.get("/api/fidelidade/1/pontos")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["pontos"] == 50

    @patch("backend.models.fidelidade.get_db")
    def test_get_pontos_inexistente(self, mock_db, client):
        mock_db.return_value = _mock_db(row=None)
        resp = client.get("/api/fidelidade/999/pontos")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["pontos"] == 0

    @patch("backend.models.fidelidade.get_db")
    def test_resgatar_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # First call: SELECT FOR UPDATE
        # Second call: UPDATE RETURNING
        mock_cursor.fetchone.side_effect = [
            {"pontos": 200, "resgates": 0},
            {"pontos": 200, "resgates": 1, "updated_at": "2026-01-01"},
        ]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/fidelidade/1/resgatar")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "message" in data

    @patch("backend.models.fidelidade.get_db")
    def test_resgatar_pontos_insuficientes(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"pontos": 30, "resgates": 0}
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/fidelidade/1/resgatar")
        assert resp.status_code == 400

    @patch("backend.models.fidelidade.get_db")
    def test_resgatar_sem_pontos(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.post("/api/fidelidade/999/resgatar")
        assert resp.status_code == 400


# ── POST /cmd (HTTP endpoint) ────────────────────────────────────────────────

class TestCmdEndpoint:

    @patch("backend.services.cmd_service.listar_sabores")
    def test_cmd_listar_sabores(self, mock_listar, client):
        mock_listar.return_value = [_sabor()]
        resp = client.post("/cmd", json={"comando": "listar sabores"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "resposta" in data
        assert "Chocolate" in data["resposta"]

    def test_cmd_ajuda(self, client):
        resp = client.post("/cmd", json={"comando": "ajuda"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "Comandos disponíveis" in data["resposta"]

    def test_cmd_limpar(self, client):
        resp = client.post("/cmd", json={"comando": "limpar"})
        assert resp.status_code == 200
        assert resp.get_json()["resposta"] == "__LIMPAR__"

    def test_cmd_sem_json(self, client):
        resp = client.post("/cmd", data="not json", content_type="text/plain")
        assert resp.status_code in (400, 415)

    def test_cmd_sem_campo_comando(self, client):
        resp = client.post("/cmd", json={"other": "value"})
        assert resp.status_code == 400

    def test_cmd_comando_nao_string(self, client):
        resp = client.post("/cmd", json={"comando": 123})
        assert resp.status_code == 400

    def test_cmd_muito_longo(self, client):
        resp = client.post("/cmd", json={"comando": "x" * 501})
        assert resp.status_code == 400

    def test_cmd_desconhecido(self, client):
        resp = client.post("/cmd", json={"comando": "foo bar"})
        assert resp.status_code == 200
        assert "não reconhecido" in resp.get_json()["resposta"]


# ── Gamification HTTP endpoints ──────────────────────────────────────────────

class TestGamificationRoutes:

    def _auth_header(self):
        from backend.auth.jwt_handler import generate_token
        token = generate_token(1, "test@test.com")
        return {"Authorization": f"Bearer {token}"}

    def test_badges_no_auth(self, client):
        resp = client.get("/api/gamification/badges")
        assert resp.status_code == 401

    @patch("backend.gamification.gamification_engine.get_db")
    def test_badges_ok(self, mock_db, client):
        mock_db.return_value = _mock_db(rows=[])
        resp = client.get("/api/gamification/badges", headers=self._auth_header())
        assert resp.status_code == 200

    def test_level_no_auth(self, client):
        resp = client.get("/api/gamification/level")
        assert resp.status_code == 401

    @patch("backend.gamification.gamification_engine.get_db")
    def test_level_ok(self, mock_db, client):
        mock_db.return_value = _mock_db(row={"total_points": 500, "level": 1})
        resp = client.get("/api/gamification/level", headers=self._auth_header())
        assert resp.status_code == 200

    def test_daily_challenges_no_auth(self, client):
        resp = client.get("/api/gamification/challenges/daily")
        assert resp.status_code == 401

    @patch("backend.gamification.gamification_engine.get_db")
    def test_daily_challenges_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # generate_daily_challenges checks existing challenges then upserts
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn
        resp = client.get("/api/gamification/challenges/daily", headers=self._auth_header())
        assert resp.status_code == 200

    def test_spin_no_auth(self, client):
        resp = client.post("/api/gamification/spin")
        assert resp.status_code == 401

    @patch("backend.gamification.gamification_engine.get_db")
    def test_spin_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # no previous spin
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn
        resp = client.post("/api/gamification/spin", headers=self._auth_header())
        assert resp.status_code == 200

    def test_leaderboard_global_public(self, client):
        """Global leaderboard is public — no auth needed."""
        # This will try to hit the DB. We mock.
        with patch("backend.gamification.leaderboard.get_db") as mock_db:
            mock_db.return_value = _mock_db(rows=[])
            resp = client.get("/api/gamification/leaderboard/global")
            assert resp.status_code == 200

    def test_leaderboard_weekly_public(self, client):
        with patch("backend.gamification.leaderboard.get_db") as mock_db:
            mock_db.return_value = _mock_db(rows=[])
            resp = client.get("/api/gamification/leaderboard/weekly")
            assert resp.status_code == 200

    def test_my_rank_no_auth(self, client):
        resp = client.get("/api/gamification/leaderboard/my-rank")
        assert resp.status_code == 401

    @patch("backend.gamification.leaderboard.get_db")
    def test_my_rank_ok(self, mock_db, client):
        mock_db.return_value = _mock_db(row={"rank": 1, "total_referrals": 5})
        resp = client.get("/api/gamification/leaderboard/my-rank",
                          headers=self._auth_header())
        assert resp.status_code == 200

    def test_ar_create_no_auth(self, client):
        resp = client.post("/api/gamification/ar/create", json={})
        assert resp.status_code == 401

    def test_ar_create_ok(self, client):
        resp = client.post("/api/gamification/ar/create",
                           json={"flavor_id": 1, "custom_toppings": ["granola"]},
                           headers=self._auth_header())
        assert resp.status_code == 200

    def test_ar_try_on_no_auth(self, client):
        resp = client.post("/api/gamification/ar/try-on", json={})
        assert resp.status_code == 401

    def test_ar_try_on_ok(self, client):
        resp = client.post("/api/gamification/ar/try-on",
                           json={"flavors": [{"id": 1, "name": "Açaí"}]},
                           headers=self._auth_header())
        assert resp.status_code == 200


# ── Global error handlers ────────────────────────────────────────────────────

class TestErrorHandlers:

    def test_404_json(self, client):
        resp = client.get("/nonexistent-route")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data

    def test_405_json(self, client):
        resp = client.patch("/api/sabores")
        assert resp.status_code == 405
        data = resp.get_json()
        assert "error" in data


# ── Pagination ────────────────────────────────────────────────────────────────

class TestPagination:

    @patch("backend.models.pedido.get_db")
    def test_pedidos_pagination(self, mock_db, client):
        mock_db.return_value = _mock_db(rows=[])
        resp = client.get("/api/pedidos?page=2&per_page=10")
        assert resp.status_code == 200

    @patch("backend.models.sabor.get_db")
    def test_sabores_pagination(self, mock_db, client):
        mock_db.return_value = _mock_db(rows=[])
        resp = client.get("/api/sabores?page=1&per_page=20")
        assert resp.status_code == 200

    @patch("backend.models.sabor.get_db")
    def test_sabores_no_pagination(self, mock_db, client):
        mock_db.return_value = _mock_db(rows=[_sabor()])
        resp = client.get("/api/sabores")
        assert resp.status_code == 200
