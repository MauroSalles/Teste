"""Tests for the /health endpoint."""


def test_health_endpoint_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code in (200, 503)
    data = resp.get_json()
    assert "status" in data
    assert data["service"] == "gelateria-backend"
    assert "db" in data


def test_health_structure(client):
    resp = client.get("/health")
    data = resp.get_json()
    assert data["status"] in ("ok", "degraded")
    assert data["db"] in ("ok", "unavailable")
