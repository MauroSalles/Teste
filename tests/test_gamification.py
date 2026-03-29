"""Tests for the gamification engine (all DB calls are mocked)."""
import json
import pytest
from contextlib import contextmanager
from datetime import date, timedelta
from unittest.mock import MagicMock, patch


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_db_mock(fetchone_return=None, fetchall_return=None):
    """Return a context-manager mock for backend.database.get_db."""
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone_return
    cursor.fetchall.return_value = fetchall_return or []

    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    @contextmanager
    def _get_db_cm():
        yield conn

    return _get_db_cm, cursor


# ─────────────────────────────────────────────────────────────────────────────
# Tests: GamificationEngine
# ─────────────────────────────────────────────────────────────────────────────

class TestGamification:

    def test_badge_award(self):
        from backend.gamification.gamification_engine import GamificationEngine

        mock_cm, _ = _make_db_mock()
        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.award_badge(1, "first_order")

        assert result["success"] is True
        assert result["badge"]["name"] == "Seed Planted"

    def test_badge_award_unknown_type(self):
        from backend.gamification.gamification_engine import GamificationEngine

        engine = GamificationEngine()
        result = engine.award_badge(1, "nonexistent_badge")
        assert result["success"] is False
        assert "error" in result

    def test_level_progression(self):
        from backend.gamification.gamification_engine import GamificationEngine

        # Simulate a user with 2500 total_points → level 3
        fetchone_return = {"total_points": 2500}
        mock_cm, _ = _make_db_mock(fetchone_return=fetchone_return)

        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.update_user_level(1)

        assert result["success"] is True
        assert result["level_data"]["level"] == 3
        assert result["level_data"]["total_points"] == 2500

    def test_level_progression_zero_points(self):
        from backend.gamification.gamification_engine import GamificationEngine

        fetchone_return = {"total_points": 0}
        mock_cm, _ = _make_db_mock(fetchone_return=fetchone_return)

        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.update_user_level(1)

        assert result["success"] is True
        assert result["level_data"]["level"] >= 1

    def test_level_capped_at_100(self):
        from backend.gamification.gamification_engine import GamificationEngine

        fetchone_return = {"total_points": 999_999}
        mock_cm, _ = _make_db_mock(fetchone_return=fetchone_return)

        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.update_user_level(1)

        assert result["level_data"]["level"] == 100

    def test_daily_challenges(self):
        from backend.gamification.gamification_engine import GamificationEngine

        mock_cm, _ = _make_db_mock(fetchone_return={"streak": 1, "cnt": 0, "spin_date": None})

        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.generate_daily_challenges(1)

        assert result["success"] is True
        assert len(result["challenges"]) == 5

    def test_daily_challenges_ids(self):
        from backend.gamification.gamification_engine import GamificationEngine

        mock_cm, _ = _make_db_mock(fetchone_return={"streak": 0, "cnt": 0, "spin_date": None})

        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.generate_daily_challenges(1)

        ids = {c["id"] for c in result["challenges"]}
        assert "streak_3" in ids
        assert "invite_1" in ids
        assert "review_1" in ids
        assert "flavor_new" in ids
        assert "share_1" in ids

    def test_spin_wheel_success(self):
        from backend.gamification.gamification_engine import GamificationEngine

        # No previous spin → spin_date is None
        mock_cm, _ = _make_db_mock(fetchone_return={"spin_date": None})

        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.spin_reward_wheel(1)

        assert result["success"] is True
        assert "reward" in result
        assert result["reward"]["name"] in {r["name"] for r in [
            {"name": "10% OFF"}, {"name": "25% OFF"}, {"name": "50% OFF"},
            {"name": "Free Small"}, {"name": "Free Large"}, {"name": "100 points"},
            {"name": "Surprise"}, {"name": "5 Referral Bonus"},
        ]}

    def test_spin_wheel_already_spun(self):
        from backend.gamification.gamification_engine import GamificationEngine

        today = date.today()
        mock_cm, _ = _make_db_mock(fetchone_return={"spin_date": today})

        with patch("backend.gamification.gamification_engine.get_db", mock_cm):
            engine = GamificationEngine()
            result = engine.spin_reward_wheel(1)

        assert result["success"] is False
        assert "Already spun today" in result["error"]

    def test_create_seasonal_event(self):
        from backend.gamification.gamification_engine import GamificationEngine

        engine = GamificationEngine()
        event = engine.create_seasonal_event("halloween")
        assert event is not None
        assert "featured_flavors" in event

    def test_create_seasonal_event_unknown(self):
        from backend.gamification.gamification_engine import GamificationEngine

        engine = GamificationEngine()
        event = engine.create_seasonal_event("unknown_event")
        assert event is None

    def test_create_weekly_battle(self):
        from backend.gamification.gamification_engine import GamificationEngine

        engine = GamificationEngine()
        result = engine.create_weekly_battle()
        assert result["success"] is True
        assert "battle" in result
        assert "week" in result["battle"]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: LeaderboardSystem
# ─────────────────────────────────────────────────────────────────────────────

class TestLeaderboard:

    def test_get_global_leaderboard(self):
        from backend.gamification.leaderboard import LeaderboardSystem

        mock_rows = [
            {"rank": 1, "id": 1, "name": "Alice", "avatar_url": None,
             "total_referrals": 10, "level": 5, "total_points": 5000},
        ]
        mock_cm, cursor = _make_db_mock(fetchall_return=mock_rows)

        with patch("backend.gamification.leaderboard.get_db", mock_cm):
            lb = LeaderboardSystem()
            result = lb.get_global_leaderboard(limit=10)

        assert result["success"] is True
        assert len(result["leaderboard"]) == 1
        assert result["leaderboard"][0]["name"] == "Alice"

    def test_get_weekly_leaderboard(self):
        from backend.gamification.leaderboard import LeaderboardSystem

        mock_rows = [
            {"rank": 1, "id": 2, "name": "Bob", "avatar_url": None,
             "week_referrals": 3, "level": 2},
        ]
        mock_cm, _ = _make_db_mock(fetchall_return=mock_rows)

        with patch("backend.gamification.leaderboard.get_db", mock_cm):
            lb = LeaderboardSystem()
            result = lb.get_weekly_leaderboard()

        assert result["success"] is True
        assert result["leaderboard"][0]["name"] == "Bob"

    def test_get_user_rank(self):
        from backend.gamification.leaderboard import LeaderboardSystem

        mock_row = {"rank": 5, "total_referrals": 3, "total_users": 100}
        mock_cm, _ = _make_db_mock(fetchone_return=mock_row)

        with patch("backend.gamification.leaderboard.get_db", mock_cm):
            lb = LeaderboardSystem()
            result = lb.get_user_rank(1)

        assert result["success"] is True
        assert result["rank"] == 5
        assert result["percentile"] == 5.0

    def test_get_user_rank_not_found(self):
        from backend.gamification.leaderboard import LeaderboardSystem

        mock_cm, _ = _make_db_mock(fetchone_return=None)

        with patch("backend.gamification.leaderboard.get_db", mock_cm):
            lb = LeaderboardSystem()
            result = lb.get_user_rank(999)

        assert result["success"] is False
