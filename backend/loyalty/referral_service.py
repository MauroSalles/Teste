"""Referral code service."""

import logging
import random
import string

from backend.database import get_db

logger = logging.getLogger(__name__)


_MAX_CODE_GENERATION_ATTEMPTS = 10


def _random_suffix(length=5):
    return "".join(random.choices(string.ascii_uppercase, k=length))


def get_or_create_referral_code(user_id):
    """Return existing referral code for user, or generate a new one."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM referral_codes WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                return dict(row)

            code = f"ACAI-{_random_suffix()}"
            for _ in range(_MAX_CODE_GENERATION_ATTEMPTS):
                cur.execute(
                    "SELECT id FROM referral_codes WHERE code = %s",
                    (code,),
                )
                if not cur.fetchone():
                    break
                code = f"ACAI-{_random_suffix()}"

            cur.execute(
                """
                INSERT INTO referral_codes (user_id, code, tier)
                VALUES (%s, %s, 1)
                RETURNING *
                """,
                (user_id, code),
            )
            return dict(cur.fetchone())


def process_referral(referral_code, new_user_id):
    """Record a referral conversion and award points to the referrer."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM referral_codes WHERE code = %s",
                (referral_code,),
            )
            code_row = cur.fetchone()
            if not code_row:
                return {"error": "Código de referral inválido"}

            cur.execute(
                "SELECT id FROM referrals WHERE referred_user_id = %s",
                (new_user_id,),
            )
            if cur.fetchone():
                return {"error": "Usuário já foi referenciado"}

            cur.execute(
                """
                INSERT INTO referrals (referral_code_id, referred_user_id, status)
                VALUES (%s, %s, 'completed')
                RETURNING *
                """,
                (code_row["id"], new_user_id),
            )
            referral = dict(cur.fetchone())

            cur.execute(
                """
                INSERT INTO fidelidade (user_id, pontos) VALUES (%s, 50)
                ON CONFLICT (user_id) DO UPDATE SET pontos = fidelidade.pontos + 50
                RETURNING pontos
                """,
                (code_row["user_id"],),
            )

            _update_tier(cur, code_row["user_id"])
            return referral


def get_referral_tier(user_id):
    """Return tier 1, 2, or 3 based on completed referrals count."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS cnt
                FROM referrals r
                JOIN referral_codes rc ON rc.id = r.referral_code_id
                WHERE rc.user_id = %s AND r.status = 'completed'
                """,
                (user_id,),
            )
            row = cur.fetchone()
            cnt = row["cnt"] if row else 0
            if cnt >= 10:
                return 3
            if cnt >= 5:
                return 2
            return 1


def _update_tier(cur, user_id):
    cur.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM referrals r
        JOIN referral_codes rc ON rc.id = r.referral_code_id
        WHERE rc.user_id = %s AND r.status = 'completed'
        """,
        (user_id,),
    )
    row = cur.fetchone()
    cnt = row["cnt"] if row else 0
    tier = 3 if cnt >= 10 else (2 if cnt >= 5 else 1)
    cur.execute(
        "UPDATE referral_codes SET tier = %s WHERE user_id = %s",
        (tier, user_id),
    )
