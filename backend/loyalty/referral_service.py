import logging
import random
import string

from backend.database import get_db

logger = logging.getLogger(__name__)

_TIER_THRESHOLDS = [
    (10, "Gold", 100),
    (5, "Silver", 50),
    (0, "Bronze", 0),
]


def _compute_tier(referral_count: int) -> tuple:
    for threshold, name, bonus in _TIER_THRESHOLDS:
        if referral_count >= threshold:
            return name, bonus
    return "Bronze", 0


def generate_referral_code(user_id: int) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"GEL-{suffix}"


def get_user_referral_code(user_id: int) -> dict:
    """Get or create referral code for user."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM referral_codes WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
            code = generate_referral_code(user_id)
            cur.execute(
                "INSERT INTO referral_codes (user_id, code) VALUES (%s, %s) RETURNING *",
                (user_id, code),
            )
            return dict(cur.fetchone())


def register_referral(code: str, referred_user_id: int) -> dict:
    """Register a referral conversion using a referral code."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM referral_codes WHERE code = %s", (code,))
            referral_row = cur.fetchone()
            if not referral_row:
                raise ValueError(f"Referral code '{code}' not found")
            referrer_id = referral_row["user_id"]
            if referrer_id == referred_user_id:
                raise ValueError("Cannot use your own referral code")
            cur.execute(
                "UPDATE referral_codes SET referral_count = referral_count + 1 WHERE code = %s",
                (code,),
            )
            cur.execute(
                """
                INSERT INTO referral_conversions (referrer_id, referred_id, status)
                VALUES (%s, %s, 'completed')
                ON CONFLICT DO NOTHING
                """,
                (referrer_id, referred_user_id),
            )
            return {"referrer_id": referrer_id, "referred_id": referred_user_id, "code": code}


def get_referral_stats(user_id: int) -> dict:
    """Return referral stats including tier and bonus points."""
    record = get_user_referral_code(user_id)
    count = record.get("referral_count", 0)
    tier, bonus = _compute_tier(count)
    return {
        "code": record["code"],
        "referral_count": count,
        "tier": tier,
        "bonus_points": bonus,
    }
