"""Tests for health check endpoints."""

from unittest.mock import MagicMock, patch


class TestHealthBasic:

    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "gelateria-backend"


class TestHealthDetailed:

    @patch("backend.routes.health_routes.get_db")
    def test_health_detailed_ok(self, mock_db, client):
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
        assert "uptime_seconds" in data
        assert data["checks"]["database"]["status"] == "ok"

    @patch("backend.routes.health_routes.get_db")
    def test_health_detailed_db_down(self, mock_db, client):
        mock_db.side_effect = Exception("connection refused")

        resp = client.get("/health/detailed")
        assert resp.status_code == 503
        data = resp.get_json()
        assert data["status"] == "degraded"
        assert data["checks"]["database"]["status"] == "error"
        assert "error" in data["checks"]["database"]
