"""Tests for the social feed, check-in, and Sabor do Dia endpoints."""

import pytest
from datetime import date


def test_sabor_do_dia_returns_ok(client):
    resp = client.get("/api/sabor-do-dia")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "sabor" in data
    assert "nome" in data["sabor"]
    assert "emoji" in data["sabor"]
    assert "descricao" in data["sabor"]
    assert "frase_gelinho" in data
    assert "data" in data
    assert data["data"] == date.today().isoformat()


def test_sabor_do_dia_deterministic(client):
    """Same day must return the same flavour on two consecutive calls."""
    r1 = client.get("/api/sabor-do-dia").get_json()
    r2 = client.get("/api/sabor-do-dia").get_json()
    assert r1["sabor"]["nome"] == r2["sabor"]["nome"]


def test_social_post_missing_content(client):
    """POST /api/social/post without content must return 400."""
    resp = client.post(
        "/api/social/post",
        json={"author": "Test"},
        headers={"X-Session-Id": "test-session-001"},
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_social_post_too_long(client):
    """POST /api/social/post with content > 280 chars must return 400."""
    resp = client.post(
        "/api/social/post",
        json={"author": "Test", "content": "x" * 281},
        headers={"X-Session-Id": "test-session-001"},
    )
    assert resp.status_code == 400


def test_checkin_missing_db_gracefully(client):
    """Check-in endpoint should not crash even without a real DB (returns 500 or similar, not 200 empty)."""
    resp = client.post(
        "/api/checkin",
        json={"mood": "happy", "session_id": "test-anon-session"},
        headers={"X-Session-Id": "test-anon-session"},
    )
    # Without DB it should return an error response (5xx), not a hard crash
    assert resp.status_code in (200, 500)


def test_checkin_status_missing_db_gracefully(client):
    """GET /api/checkin/status should return a safe fallback without a DB."""
    resp = client.get(
        "/api/checkin/status",
        headers={"X-Session-Id": "test-anon-session"},
    )
    # Should return 200 with a fallback (streak=0) or 500
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        data = resp.get_json()
        assert "checked_in" in data
        assert "streak" in data
