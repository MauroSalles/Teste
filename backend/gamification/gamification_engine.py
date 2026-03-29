import json
import logging
from datetime import datetime

import numpy as np

from backend.database import get_db

logger = logging.getLogger(__name__)

_BADGES = {
    "first_order": {
        "icon": "🌱",
        "name": "Seed Planted",
        "description": "Bought your first açaí",
        "rarity": "common",
    },
    "seven_day_streak": {
        "icon": "🔥",
        "name": "On Fire",
        "description": "7 days in a row",
        "rarity": "uncommon",
        "reward": "50 points",
    },
    "referrer_5": {
        "icon": "🌟",
        "name": "5 Friends Legend",
        "description": "Referred 5 friends",
        "rarity": "uncommon",
        "reward": "R$25 credit",
    },
    "referrer_10": {
        "icon": "👑",
        "name": "King Referrer",
        "description": "Referred 10 friends",
        "rarity": "rare",
        "reward": "R$100 credit",
    },
    "flavor_collector": {
        "icon": "🎨",
        "name": "Flavor Connoisseur",
        "description": "Tried 20 different flavors",
        "rarity": "rare",
    },
    "night_owl": {
        "icon": "🌙",
        "name": "Night Owl",
        "description": "Ordered after midnight 5 times",
        "rarity": "uncommon",
    },
    "social_butterfly": {
        "icon": "🦋",
        "name": "Social Butterfly",
        "description": "Shared 10 orders to social media",
        "rarity": "uncommon",
    },
    "sustainability_hero": {
        "icon": "♻️",
        "name": "Eco Warrior",
        "description": "Chose bike delivery 10 times",
        "rarity": "rare",
    },
    "review_master": {
        "icon": "✍️",
        "name": "Critic",
        "description": "Wrote 20 detailed reviews",
        "rarity": "uncommon",
    },
    "photo_legend": {
        "icon": "📸",
        "name": "Instagrammer",
        "description": "Shared 50 AR photos",
        "rarity": "rare",
    },
}

_WHEEL_REWARDS = [
    {"name": "10% OFF", "value": "10% OFF next order", "rarity": "common"},
    {"name": "25% OFF", "value": "25% OFF next order", "rarity": "uncommon"},
    {"name": "50% OFF", "value": "50% OFF next order", "rarity": "rare"},
    {"name": "Free Small", "value": "Free small açaí", "rarity": "uncommon"},
    {"name": "Free Large", "value": "Free large açaí", "rarity": "rare"},
    {"name": "100 points", "value": "100 loyalty points", "rarity": "common"},
    {"name": "Surprise", "value": "???", "rarity": "legendary"},
    {"name": "5 Referral Bonus", "value": "R$25 if you refer 1 friend", "rarity": "uncommon"},
]

_WHEEL_WEIGHTS = np.array([40, 25, 5, 15, 5, 25, 1, 10], dtype=float)
_WHEEL_PROBS = _WHEEL_WEIGHTS / _WHEEL_WEIGHTS.sum()


class GamificationEngine:
    """Gamification engine: badges, levels, daily challenges, spin wheel."""

    # ─────────────────────────────────────────────────────────
    # Badges & Achievements
    # ─────────────────────────────────────────────────────────

    def award_badge(self, user_id, badge_type):
        """Award a badge to user_id when a milestone is reached."""
        badge = _BADGES.get(badge_type)
        if not badge:
            return {"success": False, "error": "Badge not found"}

        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO user_badges (user_id, badge_type, badge_data, awarded_at)
                        VALUES (%s, %s, %s, NOW())
                        """,
                        (user_id, badge_type, json.dumps(badge)),
                    )
            return {"success": True, "badge": badge}
        except Exception as e:
            logger.error("award_badge error: %s", e)
            return {"success": False, "error": str(e)}

    def get_user_badges(self, user_id):
        """Return all badges earned by user_id."""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM user_badges WHERE user_id = %s ORDER BY awarded_at DESC",
                        (user_id,),
                    )
                    badges = cur.fetchall()
            return {"success": True, "badges": [dict(b) for b in badges]}
        except Exception as e:
            logger.error("get_user_badges error: %s", e)
            return {"success": False, "error": str(e)}

    # ─────────────────────────────────────────────────────────
    # Levels & Progression
    # ─────────────────────────────────────────────────────────

    def update_user_level(self, user_id):
        """Recalculate and persist the user's level (1-100, 1000 pts/level)."""
        try:
            points = self._get_user_total_points(user_id)

            level = (points // 1000) + 1
            level = min(level, 100)
            xp_for_next = 1000 - (points % 1000)

            level_data = {
                "level": level,
                "total_points": points,
                "xp_for_next_level": xp_for_next,
                "progress_percent": ((points % 1000) / 1000) * 100,
            }

            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE users
                        SET level = %s, total_points = %s, level_updated_at = NOW()
                        WHERE id = %s
                        """,
                        (level, points, user_id),
                    )

            return {"success": True, "level_data": level_data}
        except Exception as e:
            logger.error("update_user_level error: %s", e)
            return {"success": False, "error": str(e)}

    def _get_user_total_points(self, user_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT total_points FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
        return int(row["total_points"]) if row else 0

    # ─────────────────────────────────────────────────────────
    # Daily Challenges
    # ─────────────────────────────────────────────────────────

    def generate_daily_challenges(self, user_id):
        """Generate (or fetch) today's 5 challenges for user_id."""
        try:
            streak = self._get_streak_count(user_id)
            today_referrals = self._get_today_referrals(user_id)
            today_reviews = self._get_today_reviews(user_id)
            today_shares = self._get_today_shares(user_id)

            challenges = [
                {
                    "id": "streak_3",
                    "title": "🔥 Three-Day Burner",
                    "description": "Order 3 days in a row",
                    "progress": streak,
                    "target": 3,
                    "reward": "50 points",
                    "icon": "🔥",
                },
                {
                    "id": "invite_1",
                    "title": "👥 Bring a Friend",
                    "description": "Refer 1 friend today",
                    "progress": today_referrals,
                    "target": 1,
                    "reward": "R$10 credit",
                    "icon": "👥",
                },
                {
                    "id": "review_1",
                    "title": "⭐ Be a Critic",
                    "description": "Write a review with photo",
                    "progress": today_reviews,
                    "target": 1,
                    "reward": "25 points",
                    "icon": "⭐",
                },
                {
                    "id": "flavor_new",
                    "title": "🎨 Flavor Explorer",
                    "description": "Try a new flavor you never had",
                    "progress": 0,
                    "target": 1,
                    "reward": "100 points + badge",
                    "icon": "🎨",
                },
                {
                    "id": "share_1",
                    "title": "📸 Share Your Moment",
                    "description": "Share order to social media",
                    "progress": today_shares,
                    "target": 1,
                    "reward": "25 points",
                    "icon": "📸",
                },
            ]

            challenges_json = json.dumps(challenges)
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO daily_challenges (user_id, challenges, date)
                        VALUES (%s, %s, CURRENT_DATE)
                        ON CONFLICT (user_id, date) DO UPDATE SET challenges = EXCLUDED.challenges
                        """,
                        (user_id, challenges_json),
                    )

            return {"success": True, "challenges": challenges}
        except Exception as e:
            logger.error("generate_daily_challenges error: %s", e)
            return {"success": False, "error": str(e)}

    def _get_streak_count(self, user_id):
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(DISTINCT DATE(spun_at)) AS streak
                        FROM wheel_spins
                        WHERE user_id = %s
                          AND spun_at >= NOW() - INTERVAL '3 days'
                        """,
                        (user_id,),
                    )
                    row = cur.fetchone()
            return int(row["streak"]) if row else 0
        except Exception:
            return 0

    def _get_today_referrals(self, user_id):
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*) AS cnt FROM referral_conversions
                        WHERE referrer_id = %s AND DATE(created_at) = CURRENT_DATE
                        """,
                        (user_id,),
                    )
                    row = cur.fetchone()
            return int(row["cnt"]) if row else 0
        except Exception:
            return 0

    def _get_today_reviews(self, user_id):
        return 0

    def _get_today_shares(self, user_id):
        return 0

    # ─────────────────────────────────────────────────────────
    # Seasonal Events
    # ─────────────────────────────────────────────────────────

    def create_seasonal_event(self, event_type):
        """Return configuration for a seasonal event."""
        events = {
            "summer_tropical": {
                "name": "☀️ Tropical Summer",
                "duration": "30 days",
                "featured_flavors": ["Mango", "Coconut", "Pineapple"],
                "special_bonus": "+50 points per order",
                "limited_time": True,
            },
            "halloween": {
                "name": "🎃 Spooky Halloween",
                "duration": "7 days",
                "featured_flavors": ["Black Açaí", "Red Velvet"],
                "challenge": "Order after 8pm = 2x points",
                "limited_edition_merch": True,
            },
            "christmas": {
                "name": "🎄 Holiday Magic",
                "duration": "14 days",
                "featured_flavors": ["Cranberry Spice", "Gingerbread"],
                "gift_wrapping": True,
                "group_order_bonus": "Group of 5+ = 30% OFF",
            },
            "new_year": {
                "name": "🎆 New Year New You",
                "duration": "7 days",
                "wellness_focus": True,
                "challenge": "Health challenge = 500 points prize",
                "reset_leaderboard": True,
            },
        }
        return events.get(event_type)

    # ─────────────────────────────────────────────────────────
    # Weekly Battle
    # ─────────────────────────────────────────────────────────

    def create_weekly_battle(self):
        """Return the current week's battle royale configuration."""
        try:
            battle = {
                "week": datetime.now().isocalendar()[1],
                "type": "referral_battle_royale",
                "rules": {
                    "description": "Top 10 referrers this week win prizes",
                    "positions": {
                        "1st": "R$500 credit + badge + merch",
                        "2nd": "R$300 credit + badge",
                        "3rd": "R$200 credit + badge",
                        "4-10th": "R$50 credit each",
                    },
                },
                "live_leaderboard": {
                    "refresh": "5 minutes",
                    "show_top_5": True,
                    "show_your_rank": True,
                },
            }
            return {"success": True, "battle": battle}
        except Exception as e:
            logger.error("create_weekly_battle error: %s", e)
            return {"success": False, "error": str(e)}

    # ─────────────────────────────────────────────────────────
    # Spin the Wheel
    # ─────────────────────────────────────────────────────────

    def spin_reward_wheel(self, user_id):
        """Spin the reward wheel once per day."""
        try:
            last_spin = self._get_last_spin_date(user_id)
            if last_spin == datetime.now().date():
                return {
                    "success": False,
                    "error": "Already spun today. Come back tomorrow!",
                }

            winner = _WHEEL_REWARDS[
                int(np.random.choice(len(_WHEEL_REWARDS), p=_WHEEL_PROBS))
            ]

            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO wheel_spins (user_id, reward, spun_at) VALUES (%s, %s, NOW())",
                        (user_id, winner["name"]),
                    )

            return {
                "success": True,
                "reward": winner,
                "celebration": f"🎉 You won: {winner['name']}!",
            }
        except Exception as e:
            logger.error("spin_reward_wheel error: %s", e)
            return {"success": False, "error": str(e)}

    def _get_last_spin_date(self, user_id):
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT DATE(spun_at) AS spin_date FROM wheel_spins "
                        "WHERE user_id = %s ORDER BY spun_at DESC LIMIT 1",
                        (user_id,),
                    )
                    row = cur.fetchone()
            return row["spin_date"] if row else None
        except Exception:
            return None
