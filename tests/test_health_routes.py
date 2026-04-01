"""Tests for health endpoints."""


class TestHealthBasic:

    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "gelateria-backend"


class TestHealthDetailed:

    def test_health_detailed_status(self, client):
        resp = client.get("/health/detailed")
        assert resp.status_code == 200

    def test_health_detailed_fields(self, client):
        data = client.get("/health/detailed").get_json()
        assert data["status"] == "ok"
        assert data["service"] == "gelateria-backend"
        assert "version" in data
        assert "timestamp" in data
        assert "uptime" in data
        assert "seconds" in data["uptime"]
        assert "human" in data["uptime"]

    def test_health_detailed_checks(self, client):
        data = client.get("/health/detailed").get_json()
        assert "checks" in data
        assert data["checks"]["api"] == "ok"

    def test_health_detailed_uptime_non_negative(self, client):
        data = client.get("/health/detailed").get_json()
        assert data["uptime"]["seconds"] >= 0
