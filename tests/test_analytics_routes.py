"""Tests for analytics routes."""

from unittest.mock import patch, MagicMock

import pytest


class TestAnalyticsOverview:
    @patch("backend.models.sabor.get_db")
    @patch("backend.models.pedido.get_db")
    @patch("backend.models.estoque.get_db")
    def test_overview_ok(self, mock_estoque_db, mock_pedido_db, mock_sabor_db, client):
        def _make_mock(rows):
            mock_conn = MagicMock()
            mock_cur = MagicMock()
            mock_cur.fetchall.return_value = rows
            mock_cur.__enter__ = lambda s: s
            mock_cur.__exit__ = MagicMock(return_value=False)
            mock_conn.cursor.return_value = mock_cur
            mock_conn.__enter__ = lambda s: s
            mock_conn.__exit__ = MagicMock(return_value=False)
            return mock_conn

        mock_sabor_db.return_value = _make_mock(
            [{"id": 1, "nome": "Chocolate", "preco": 10.0}]
        )
        mock_pedido_db.return_value = _make_mock(
            [{"id": 1, "sabor": "Chocolate", "quantidade": 2, "data": "2026-01-01"}]
        )
        mock_estoque_db.return_value = _make_mock(
            [{"id": 1, "nome": "Chocolate", "quantidade": 10}]
        )

        resp = client.get("/api/analytics/overview")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "resumo" in data
        assert "estoque" in data
        assert "generated_at" in data

    def test_overview_has_json_content_type(self, client):
        resp = client.get("/api/analytics/overview")
        assert "application/json" in resp.content_type


class TestAnalyticsVendas:
    @patch("backend.models.pedido.get_db")
    def test_tendencia_default(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/analytics/vendas/tendencia")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["dias"] == 30

    @patch("backend.models.pedido.get_db")
    def test_tendencia_custom_days(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/analytics/vendas/tendencia?dias=7")
        assert resp.status_code == 200
        assert resp.get_json()["dias"] == 7

    @patch("backend.models.pedido.get_db")
    def test_tendencia_clamps_days(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/analytics/vendas/tendencia?dias=999")
        assert resp.status_code == 200
        assert resp.get_json()["dias"] == 90


class TestAnalyticsEstoqueAlertas:
    @patch("backend.models.estoque.get_db")
    def test_alertas_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            {"id": 1, "nome": "Chocolate", "quantidade": 0},
            {"id": 2, "nome": "Morango", "quantidade": 3},
            {"id": 3, "nome": "Baunilha", "quantidade": 20},
        ]
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/api/analytics/estoque/alertas")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["criticos"] == 1
        assert data["baixos"] == 1
        assert data["total_itens"] == 3

    def test_cache_info(self, client):
        resp = client.get("/api/analytics/cache/info")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "backend" in data
