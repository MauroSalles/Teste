"""Unit tests for cmd_service.processar_comando (DB mocked)."""

from unittest.mock import MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_mock_conn(rows=None, row=None):
    """Return a context-manager-compatible mock connection."""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = rows or []
    mock_cursor.fetchone.return_value = row
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn, mock_cursor


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestProcessarComando:

    @patch("backend.models.sabor.get_db")
    def test_listar_sabores(self, mock_get_db):
        mock_conn, mock_cursor = _make_mock_conn(
            rows=[{"id": 1, "nome": "Chocolate", "preco": 10.0}]
        )
        mock_get_db.return_value = mock_conn

        from backend.services.cmd_service import processar_comando
        result = processar_comando("listar sabores")
        assert "Chocolate" in result

    def test_unknown_command_returns_error(self):
        from backend.services.cmd_service import processar_comando
        result = processar_comando("comando_invalido_xyz")
        assert result  # should return some message, not crash

    @patch("backend.models.estoque.get_db")
    @patch("backend.models.pedido.get_db")
    @patch("backend.models.sabor.get_db")
    def test_status_command(self, mock_sabor_db, mock_pedido_db, mock_estoque_db):
        mock_conn_s, _ = _make_mock_conn(rows=[])
        mock_conn_p, _ = _make_mock_conn(rows=[])
        mock_conn_e, _ = _make_mock_conn(rows=[])
        mock_sabor_db.return_value = mock_conn_s
        mock_pedido_db.return_value = mock_conn_p
        mock_estoque_db.return_value = mock_conn_e

        from backend.services.cmd_service import processar_comando
        result = processar_comando("status")
        assert result  # should not crash

    def test_ajuda_command(self):
        from backend.services.cmd_service import processar_comando
        result = processar_comando("ajuda")
        assert result
        assert len(result) > 10  # should have some help text

    def test_limpar_command(self):
        from backend.services.cmd_service import processar_comando
        result = processar_comando("limpar")
        # limpar returns a sentinel or empty; just should not raise
        assert result is not None
