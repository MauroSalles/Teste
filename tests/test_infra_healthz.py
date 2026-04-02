"""Tests for the /infra/healthz endpoint."""
from unittest.mock import MagicMock, patch

import pytest

from backend.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestInfraHealthz:

    @patch("backend.routes.infra_routes._check_frontend")
    @patch("backend.routes.infra_routes._check_proxy")
    @patch("backend.routes.infra_routes._check_cache")
    @patch("backend.routes.infra_routes._check_database")
    def test_all_ok(self, mock_db, mock_cache, mock_proxy, mock_frontend, client):
        mock_db.return_value = {"status": "ok"}
        mock_cache.return_value = {"status": "ok"}
        mock_proxy.return_value = {"status": "disabled", "reason": "PROXY_URL not configured"}
        mock_frontend.return_value = {"status": "disabled", "reason": "FRONTEND_URL not configured"}

        resp = client.get("/infra/healthz")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert "uptime_seconds" in data
        assert data["checks"]["database"]["status"] == "ok"

    @patch("backend.routes.infra_routes._check_frontend")
    @patch("backend.routes.infra_routes._check_proxy")
    @patch("backend.routes.infra_routes._check_cache")
    @patch("backend.routes.infra_routes._check_database")
    def test_db_down_returns_503(self, mock_db, mock_cache, mock_proxy, mock_frontend, client):
        mock_db.return_value = {"status": "error", "reason": "connection refused"}
        mock_cache.return_value = {"status": "disabled", "reason": "REDIS_URL not configured"}
        mock_proxy.return_value = {"status": "disabled", "reason": "PROXY_URL not configured"}
        mock_frontend.return_value = {"status": "disabled", "reason": "FRONTEND_URL not configured"}

        resp = client.get("/infra/healthz")
        assert resp.status_code == 503
        data = resp.get_json()
        assert data["status"] == "error"
        assert data["checks"]["database"]["status"] == "error"

    @patch("backend.routes.infra_routes._check_frontend")
    @patch("backend.routes.infra_routes._check_proxy")
    @patch("backend.routes.infra_routes._check_cache")
    @patch("backend.routes.infra_routes._check_database")
    def test_cache_error_returns_degraded(self, mock_db, mock_cache, mock_proxy, mock_frontend, client):
        mock_db.return_value = {"status": "ok"}
        mock_cache.return_value = {"status": "error", "reason": "timeout"}
        mock_proxy.return_value = {"status": "disabled", "reason": "PROXY_URL not configured"}
        mock_frontend.return_value = {"status": "disabled", "reason": "FRONTEND_URL not configured"}

        resp = client.get("/infra/healthz")
        # HTTP 200 because DB (critical service) is ok, but overall status is degraded
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "degraded"
        assert data["checks"]["cache"]["status"] == "error"

    @patch("backend.routes.infra_routes._check_frontend")
    @patch("backend.routes.infra_routes._check_proxy")
    @patch("backend.routes.infra_routes._check_cache")
    @patch("backend.routes.infra_routes._check_database")
    def test_response_structure(self, mock_db, mock_cache, mock_proxy, mock_frontend, client):
        mock_db.return_value = {"status": "ok"}
        mock_cache.return_value = {"status": "disabled", "reason": "REDIS_URL not configured"}
        mock_proxy.return_value = {"status": "disabled", "reason": "PROXY_URL not configured"}
        mock_frontend.return_value = {"status": "disabled", "reason": "FRONTEND_URL not configured"}

        resp = client.get("/infra/healthz")
        data = resp.get_json()

        assert "status" in data
        assert "service" in data
        assert "uptime_seconds" in data
        assert "checks" in data
        assert set(data["checks"].keys()) == {"database", "cache", "proxy", "frontend"}
        assert data["service"] == "gelateria-backend"


class TestCacheModule:
    """Tests for the cache module graceful-fallback behaviour."""

    def test_cache_status_no_redis_url(self):
        """cache_status() returns disabled when REDIS_URL is not set."""
        import os
        import backend.cache as cache_mod

        original = os.environ.pop("REDIS_URL", None)
        cache_mod._reset_for_testing()
        try:
            result = cache_mod.cache_status()
            assert result["status"] == "disabled"
        finally:
            if original is not None:
                os.environ["REDIS_URL"] = original
            cache_mod._reset_for_testing()

    def test_cache_get_returns_none_when_unavailable(self):
        """cache_get() returns None gracefully when Redis is not available."""
        import backend.cache as cache_mod

        cache_mod._reset_for_testing()
        cache_mod._redis_available = False
        result = cache_mod.cache_get("some_key")
        assert result is None

    def test_cache_set_returns_false_when_unavailable(self):
        """cache_set() returns False gracefully when Redis is not available."""
        import backend.cache as cache_mod

        cache_mod._reset_for_testing()
        cache_mod._redis_available = False
        result = cache_mod.cache_set("some_key", {"data": 1})
        assert result is False
