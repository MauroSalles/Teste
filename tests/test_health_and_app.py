"""Tests for enhanced health-check endpoints and X-Request-ID middleware."""

from unittest.mock import patch, MagicMock


class TestHealthBasic:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_health_live(self, client):
        resp = client.get("/health/live")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "alive"

    @patch("backend.routes.health_routes.get_db")
    def test_health_ready_db_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/health/ready")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ready"

    @patch("backend.routes.health_routes.get_db")
    def test_health_ready_db_down(self, mock_db, client):
        mock_db.side_effect = Exception("connection refused")
        resp = client.get("/health/ready")
        assert resp.status_code == 503
        assert resp.get_json()["status"] == "not_ready"

    @patch("backend.routes.health_routes.get_db")
    def test_health_detailed_ok(self, mock_db, client):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = lambda s: s
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_conn

        resp = client.get("/health/detailed")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "uptime_seconds" in data
        assert data["checks"]["database"]["status"] == "ok"

    @patch("backend.routes.health_routes.get_db")
    def test_health_detailed_db_error(self, mock_db, client):
        mock_db.side_effect = Exception("timeout")
        resp = client.get("/health/detailed")
        assert resp.status_code == 503
        assert resp.get_json()["status"] == "degraded"


class TestRequestIDMiddleware:
    def test_response_has_request_id_header(self, client):
        resp = client.get("/health")
        assert "X-Request-ID" in resp.headers
        assert len(resp.headers["X-Request-ID"]) > 0

    def test_custom_request_id_echoed_back(self, client):
        resp = client.get("/health", headers={"X-Request-ID": "test-id-123"})
        assert resp.headers["X-Request-ID"] == "test-id-123"

    def test_x_content_type_options_header(self, client):
        resp = client.get("/health")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
