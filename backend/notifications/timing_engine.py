import logging
from datetime import datetime

import pytz

logger = logging.getLogger(__name__)


class SmartTimingEngine:
    """AI-powered timing engine for intelligent notification delivery.

    All external-dependency calls (weather API, user-behaviour DB) degrade
    gracefully: if the DB is unavailable the engine falls back to safe
    defaults.
    """

    # Peak-hour windows per notification type (24 h clock, UTC)
    _DEFAULT_PEAK_HOURS = {
        "promotional":   [11, 12, 18, 19],
        "reminder":      [9, 10, 16, 17],
        "order_update":  "immediate",
        "flash_sale":    "immediate",
    }

    def get_optimal_send_time(self, user_id, notification_type):
        """Return the best time to send a notification to *user_id*.

        Returns a dict with keys ``send_at`` (datetime), ``confidence``
        (float 0-1) and ``reason`` (str).
        """
        try:
            user_behavior = self._get_user_behavior(user_id)

            peak_hours = dict(self._DEFAULT_PEAK_HOURS)
            peak_hours["personalized"] = user_behavior.get("most_active_hours", [11, 12])

            if self._is_weekend() and user_behavior.get("weekend_active", False):
                peak_hours["promotional"] = [12, 13, 19, 20]

            if self._is_hot_weather():
                return {
                    "send_at": datetime.now(),
                    "confidence": 0.8,
                    "reason": "Hot weather — send immediately",
                }

            hours = peak_hours.get(notification_type, "immediate")
            send_at = self._calculate_next_slot(hours)

            return {
                "send_at": send_at,
                "confidence": user_behavior.get("behavior_confidence", 0.5),
                "reason": (
                    f"Based on {user_behavior.get('orders_analyzed', 0)} orders"
                ),
            }
        except Exception as exc:
            logger.warning("get_optimal_send_time fallback: %s", exc)
            return {"send_at": datetime.now(), "confidence": 0.5, "reason": "fallback"}

    def should_send_notification(self, user_id, notification_type):
        """Return True if a notification should be sent right now.

        Checks quiet hours (23:00–07:00 UTC), recent duplicates, and the
        user's opt-in preferences.
        """
        try:
            hour = datetime.now(pytz.UTC).hour
            if hour >= 23 or hour < 7:
                return False

            if self._was_recently_notified(user_id, notification_type):
                return False

            if not self._user_opted_in(user_id, notification_type):
                return False

            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_user_behavior(self, user_id):
        """Fetch behavioural stats for *user_id* (best-effort)."""
        from backend.database import get_db
        defaults = {
            "timezone": "UTC",
            "most_active_hours": [11, 12],
            "weekend_active": False,
            "behavior_confidence": 0.5,
            "orders_analyzed": 0,
        }
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM user_behavior_cache WHERE user_id = %s",
                        (user_id,),
                    )
                    row = cur.fetchone()
                    if row:
                        defaults.update(dict(row))
        except Exception as exc:
            logger.debug("_get_user_behavior fallback: %s", exc)
        return defaults

    def _was_recently_notified(self, user_id, notification_type, hours=2):
        from backend.database import get_db
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT 1 FROM notification_log
                           WHERE user_id = %s AND template = %s
                             AND sent_at > NOW() - INTERVAL '1 hour' * %s
                           LIMIT 1""",
                        (user_id, notification_type, hours),
                    )
                    return cur.fetchone() is not None
        except Exception:
            return False

    def _user_opted_in(self, user_id, notification_type):
        from backend.database import get_db
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT push_promotional, push_transactional
                           FROM user_notification_preferences
                           WHERE user_id = %s""",
                        (user_id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        return True  # default opt-in
                    if notification_type in ("promotional", "flash_sale"):
                        return bool(row["push_promotional"])
                    return bool(row["push_transactional"])
        except Exception:
            return True

    def _is_weekend(self):
        return datetime.now(pytz.UTC).weekday() >= 5

    def _is_hot_weather(self):
        """Stub — integrate a weather API to make this dynamic."""
        return False

    def _calculate_next_slot(self, hours):
        """Return the next upcoming datetime that falls in one of *hours*."""
        if hours == "immediate":
            return datetime.now()

        now = datetime.now(pytz.UTC)
        current_hour = now.hour

        for h in sorted(hours):
            if h > current_hour:
                return now.replace(hour=h, minute=0, second=0, microsecond=0)

        # All slots have passed today — use first slot tomorrow
        from datetime import timedelta
        tomorrow = now + timedelta(days=1)
        first_hour = sorted(hours)[0]
        return tomorrow.replace(hour=first_hour, minute=0, second=0, microsecond=0)
