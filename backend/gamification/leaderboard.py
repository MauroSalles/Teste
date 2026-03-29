import logging

from backend.database import get_db

logger = logging.getLogger(__name__)


class LeaderboardSystem:
    """Real-time competitive rankings."""

    def get_global_leaderboard(self, limit=100):
        """Return the top *limit* users ordered by total confirmed referrals."""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            RANK() OVER (ORDER BY COUNT(DISTINCT rc.id) DESC) AS rank,
                            u.id,
                            u.name,
                            u.avatar_url,
                            COUNT(DISTINCT rc.id)  AS total_referrals,
                            u.level,
                            u.total_points
                        FROM users u
                        LEFT JOIN referral_conversions rc
                            ON u.id = rc.referrer_id AND rc.status = 'confirmed'
                        WHERE u.deleted_at IS NULL
                        GROUP BY u.id
                        ORDER BY total_referrals DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            return {"success": True, "leaderboard": [dict(r) for r in rows]}
        except Exception as e:
            logger.error("get_global_leaderboard error: %s", e)
            return {"success": False, "error": str(e)}

    def get_weekly_leaderboard(self):
        """Return the top 100 users ordered by referrals in the last 7 days."""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            RANK() OVER (ORDER BY COUNT(DISTINCT rc.id) DESC) AS rank,
                            u.id,
                            u.name,
                            u.avatar_url,
                            COUNT(DISTINCT rc.id)  AS week_referrals,
                            u.level
                        FROM users u
                        LEFT JOIN referral_conversions rc
                            ON u.id = rc.referrer_id
                            AND rc.status = 'confirmed'
                            AND rc.created_at > NOW() - INTERVAL '7 days'
                        WHERE u.deleted_at IS NULL
                        GROUP BY u.id
                        ORDER BY week_referrals DESC
                        LIMIT 100
                        """
                    )
                    rows = cur.fetchall()
            return {"success": True, "leaderboard": [dict(r) for r in rows]}
        except Exception as e:
            logger.error("get_weekly_leaderboard error: %s", e)
            return {"success": False, "error": str(e)}

    def get_user_rank(self, user_id):
        """Return the rank, total referrals and percentile for user_id."""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            ranked.rank,
                            ranked.total_referrals,
                            (SELECT COUNT(*) FROM users WHERE deleted_at IS NULL) AS total_users
                        FROM (
                            SELECT
                                u.id,
                                RANK() OVER (ORDER BY COUNT(DISTINCT rc.id) DESC) AS rank,
                                COUNT(DISTINCT rc.id) AS total_referrals
                            FROM users u
                            LEFT JOIN referral_conversions rc
                                ON u.id = rc.referrer_id AND rc.status = 'confirmed'
                            WHERE u.deleted_at IS NULL
                            GROUP BY u.id
                        ) ranked
                        WHERE ranked.id = %s
                        """,
                        (user_id,),
                    )
                    result = cur.fetchone()

            if not result:
                return {"success": False, "error": "User not found"}

            total_users = result["total_users"] or 1
            return {
                "success": True,
                "rank": result["rank"],
                "total_referrals": result["total_referrals"],
                "percentile": round((result["rank"] / total_users) * 100, 2),
            }
        except Exception as e:
            logger.error("get_user_rank error: %s", e)
            return {"success": False, "error": str(e)}
