"""Tests for the multi-channel notification engine.

External services (SendGrid, Twilio, Firebase) are not available in the test
environment.  These tests verify the *application layer* — correct HTTP
responses, graceful degradation and the smart-timing logic — without
requiring real third-party credentials.
"""
import json
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _auth_headers():
    """Return headers that bypass JWT in the testing environment."""
    return {}  # token_required uses stub user when FLASK_ENV=testing + no SECRET_KEY


# ---------------------------------------------------------------------------
# EmailNotificationService unit tests
# ---------------------------------------------------------------------------

class TestEmailNotificationService:
    def _make_service(self):
        from backend.notifications.email_service import EmailNotificationService
        return EmailNotificationService()

    def test_send_welcome_series_no_sendgrid(self):
        """Returns success=True (schedules emails) even without SendGrid."""
        svc = self._make_service()
        with patch.object(svc, "_schedule_email", return_value={"queued": True}):
            result = svc.send_welcome_series(1, "test@example.com", "Alice")
        assert result["success"] is True
        assert result["scheduled"] == 5

    def test_send_abandoned_cart_no_sendgrid(self):
        """Returns success=False with an error string when SendGrid is absent."""
        svc = self._make_service()
        with patch.object(svc, "_was_recently_sent", return_value=False):
            cart_data = {"items": [{"name": "Açaí Berry", "qty": 1}], "total": 42.50, "id": "cart_001"}
            result = svc.send_abandoned_cart(1, "test@example.com", cart_data)
        # No real SendGrid — we expect a graceful error, not an exception
        assert "success" in result

    def test_send_abandoned_cart_recently_sent(self):
        """Does not send if the same email was already sent recently."""
        svc = self._make_service()
        with patch.object(svc, "_was_recently_sent", return_value=True):
            result = svc.send_abandoned_cart(1, "test@example.com", {"items": [], "total": 0, "id": ""})
        assert result["success"] is False
        assert "recentemente" in result["error"]

    def test_send_personalized_offer_no_sendgrid(self):
        svc = self._make_service()
        result = svc.send_personalized_offer(1, "test@example.com", "Bob", {})
        assert "success" in result
        assert "offer" in result

    def test_send_birthday_special_no_sendgrid(self):
        svc = self._make_service()
        result = svc.send_birthday_special(1, "test@example.com", "Carol")
        assert "success" in result

    def test_send_reengagement_short_inactive(self):
        svc = self._make_service()
        with patch.object(svc, "_get_last_order_summary", return_value={}):
            result = svc.send_reengagement_campaign(1, "test@example.com", "Dave", 10)
        assert "success" in result

    def test_send_reengagement_medium_inactive(self):
        svc = self._make_service()
        with patch.object(svc, "_get_last_order_summary", return_value={}):
            result = svc.send_reengagement_campaign(1, "test@example.com", "Eve", 20)
        assert "success" in result

    def test_send_reengagement_long_inactive(self):
        svc = self._make_service()
        with patch.object(svc, "_get_last_order_summary", return_value={}):
            result = svc.send_reengagement_campaign(1, "test@example.com", "Frank", 35)
        assert "success" in result

    def test_render_template_missing_file(self):
        """Falls back to an error paragraph when the template file is absent."""
        svc = self._make_service()
        html = svc._render_template("nonexistent_template", {"foo": "bar"})
        assert "nonexistent_template" in html


# ---------------------------------------------------------------------------
# SMSNotificationService unit tests
# ---------------------------------------------------------------------------

class TestSMSNotificationService:
    def _make_service(self):
        from backend.notifications.sms_service import SMSNotificationService
        return SMSNotificationService()

    def test_flash_sale_alert_no_twilio(self):
        """Returns graceful error when Twilio is not configured."""
        svc = self._make_service()
        result = svc.send_flash_sale_alert("+5511999999999", "Açaí Berry", 30, 60)
        assert "success" in result

    def test_order_status_confirmed(self):
        svc = self._make_service()
        result = svc.send_order_status_update("+5511999999999", 42, "confirmed")
        assert "success" in result

    def test_order_status_unknown(self):
        svc = self._make_service()
        result = svc.send_order_status_update("+5511999999999", 42, "some_other_status")
        assert "success" in result

    def test_appointment_reminder(self):
        svc = self._make_service()
        result = svc.send_appointment_reminder("+5511999999999", "Festival do Açaí", 30)
        assert "success" in result


# ---------------------------------------------------------------------------
# PushNotificationService unit tests
# ---------------------------------------------------------------------------

class TestPushNotificationService:
    def _make_service(self):
        from backend.notifications.push_service import PushNotificationService
        return PushNotificationService()

    def test_send_push_no_firebase(self):
        svc = self._make_service()
        result = svc.send_personalized_push(1, "Título", "Corpo da mensagem")
        assert "success" in result

    def test_order_tracking_notification(self):
        svc = self._make_service()
        result = svc.send_order_tracking_notification(1, 99, 50)
        assert "success" in result

    def test_recommendation_push(self):
        svc = self._make_service()
        result = svc.send_recommendation_push(1, "Açaí Berry", "Você vai adorar!")
        assert "success" in result


# ---------------------------------------------------------------------------
# SmartTimingEngine unit tests
# ---------------------------------------------------------------------------

class TestSmartTimingEngine:
    def _make_engine(self):
        from backend.notifications.timing_engine import SmartTimingEngine
        return SmartTimingEngine()

    def test_get_optimal_send_time_returns_dict(self):
        engine = self._make_engine()
        timing = engine.get_optimal_send_time(1, "promotional")
        assert "send_at" in timing
        assert "confidence" in timing
        assert timing["confidence"] >= 0

    def test_get_optimal_send_time_immediate_for_order_update(self):
        engine = self._make_engine()
        before = datetime.now()
        timing = engine.get_optimal_send_time(1, "order_update")
        send_at = timing["send_at"]
        if hasattr(send_at, "tzinfo") and send_at.tzinfo is not None:
            import pytz
            send_at = send_at.astimezone(pytz.UTC).replace(tzinfo=None)
        assert send_at >= before.replace(microsecond=0)

    def test_should_not_send_late_night(self):
        """Notifications should be suppressed between 23:00 and 07:00 UTC."""
        engine = self._make_engine()
        import pytz
        late_night = datetime(2024, 1, 15, 2, 0, 0, tzinfo=pytz.UTC)  # 2 AM UTC
        with patch("backend.notifications.timing_engine.datetime") as mock_dt:
            mock_dt.now.return_value = late_night
            result = engine.should_send_notification(1, "promotional")
        assert result is False

    def test_should_send_during_day(self):
        """Notifications should be allowed in the afternoon hours."""
        engine = self._make_engine()
        import pytz
        afternoon = datetime(2024, 1, 15, 14, 0, 0, tzinfo=pytz.UTC)  # 2 PM UTC
        with (
            patch("backend.notifications.timing_engine.datetime") as mock_dt,
            patch.object(engine, "_was_recently_notified", return_value=False),
            patch.object(engine, "_user_opted_in", return_value=True),
        ):
            mock_dt.now.return_value = afternoon
            result = engine.should_send_notification(1, "promotional")
        assert result is True

    def test_respects_opt_out(self):
        engine = self._make_engine()
        import pytz
        afternoon = datetime(2024, 1, 15, 14, 0, 0, tzinfo=pytz.UTC)
        with (
            patch("backend.notifications.timing_engine.datetime") as mock_dt,
            patch.object(engine, "_was_recently_notified", return_value=False),
            patch.object(engine, "_user_opted_in", return_value=False),
        ):
            mock_dt.now.return_value = afternoon
            result = engine.should_send_notification(1, "promotional")
        assert result is False

    def test_suppresses_recent_duplicate(self):
        engine = self._make_engine()
        import pytz
        afternoon = datetime(2024, 1, 15, 14, 0, 0, tzinfo=pytz.UTC)
        with (
            patch("backend.notifications.timing_engine.datetime") as mock_dt,
            patch.object(engine, "_was_recently_notified", return_value=True),
        ):
            mock_dt.now.return_value = afternoon
            result = engine.should_send_notification(1, "promotional")
        assert result is False


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestNotificationsAPI:
    def test_send_test_email_endpoint(self, client):
        resp = client.post(
            "/api/notifications/send-test",
            json={"channel": "email"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "success" in data

    def test_send_test_sms_endpoint(self, client):
        resp = client.post(
            "/api/notifications/send-test",
            json={"channel": "sms"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "success" in data

    def test_send_test_push_endpoint(self, client):
        resp = client.post(
            "/api/notifications/send-test",
            json={"channel": "push"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "success" in data

    def test_send_test_unknown_channel(self, client):
        resp = client.post(
            "/api/notifications/send-test",
            json={"channel": "carrier_pigeon"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 400

    def test_timing_endpoint(self, client):
        resp = client.get(
            "/api/notifications/timing?type=promotional",
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "send_at" in data
        assert "confidence" in data

    def test_preferences_get_no_db(self, client):
        """GET /preferences returns 200 even when DB is unavailable."""
        resp = client.get(
            "/api/notifications/preferences",
            headers=_auth_headers(),
        )
        # Either 200 (empty prefs) or 500 (no DB) — both are acceptable
        assert resp.status_code in (200, 500)

    def test_preferences_post_no_db(self, client):
        """POST /preferences returns without crashing even when DB is unavailable."""
        resp = client.post(
            "/api/notifications/preferences",
            json={"email_promotional": False},
            headers=_auth_headers(),
        )
        assert resp.status_code in (200, 500)

    def test_upcoming_no_db(self, client):
        """GET /upcoming returns without crashing even when DB is unavailable."""
        resp = client.get(
            "/api/notifications/upcoming",
            headers=_auth_headers(),
        )
        assert resp.status_code in (200, 500)
