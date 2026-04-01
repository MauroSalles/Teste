"""Coupon validation and application service."""

import logging
from datetime import datetime, timezone

from backend.database import get_db

logger = logging.getLogger(__name__)

_MAX_DISCOUNT_ABS = 20.00
_MAX_DISCOUNT_PCT_OF_ORDER = 0.50


def validate_coupon(code, user_id, order_total):
    """9-step coupon validation. Returns {"valid": True, "discount": float} or {"valid": False, "error": str}."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Step 1: code exists
            cur.execute("SELECT * FROM coupons WHERE code = %s", (code,))
            coupon = cur.fetchone()
            if not coupon:
                return {"valid": False, "error": "Cupom não encontrado"}

            coupon = dict(coupon)

            # Step 2: accessible by user (all coupons are global in this impl)
            # Step 3: not expired
            if coupon.get("expires_at"):
                now = datetime.now(timezone.utc)
                expires = coupon["expires_at"]
                if hasattr(expires, "tzinfo") and expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                if now > expires:
                    return {"valid": False, "error": "Cupom expirado"}

            # Step 4: not already used by this user beyond max_uses_per_user
            max_uses = coupon.get("max_uses_per_user", 2)
            cur.execute(
                """
                SELECT COUNT(*) AS cnt FROM coupon_usage_log
                WHERE coupon_id = %s AND user_id = %s
                """,
                (coupon["id"], user_id),
            )
            user_uses = cur.fetchone()["cnt"]
            if user_uses >= max_uses:
                return {"valid": False, "error": "Limite de uso deste cupom atingido"}

            # Step 5: daily cap (5 uses/day globally)
            max_daily = coupon.get("max_uses_daily", 5)
            cur.execute(
                """
                SELECT COUNT(*) AS cnt FROM coupon_usage_log
                WHERE coupon_id = %s AND used_at >= CURRENT_DATE
                """,
                (coupon["id"],),
            )
            daily_uses = cur.fetchone()["cnt"]
            if daily_uses >= max_daily:
                return {"valid": False, "error": "Limite diário do cupom atingido"}

            # Step 6: monthly cap (2 uses/month by this user)
            cur.execute(
                """
                SELECT COUNT(*) AS cnt FROM coupon_usage_log
                WHERE coupon_id = %s AND user_id = %s
                  AND DATE_TRUNC('month', used_at) = DATE_TRUNC('month', CURRENT_DATE)
                """,
                (coupon["id"], user_id),
            )
            monthly_uses = cur.fetchone()["cnt"]
            if monthly_uses >= max_uses:
                return {"valid": False, "error": "Limite mensal do cupom atingido"}

            # Step 7: minimum order
            min_order = float(coupon.get("min_order") or 0)
            if float(order_total) < min_order:
                return {"valid": False, "error": f"Pedido mínimo R$ {min_order:.2f} não atingido"}

            # Step 8: calculate discount
            discount_pct = float(coupon.get("discount_pct") or 0) / 100.0
            raw_discount = float(order_total) * discount_pct
            max_allowed = min(_MAX_DISCOUNT_ABS, float(order_total) * _MAX_DISCOUNT_PCT_OF_ORDER)
            discount = min(raw_discount, max_allowed)

            # Step 9: return
            return {"valid": True, "discount": round(discount, 2), "coupon_id": coupon["id"]}


def apply_coupon(code, user_id, pedido_id):
    """Record coupon usage in the log."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM coupons WHERE code = %s", (code,))
            coupon = cur.fetchone()
            if not coupon:
                return None
            cur.execute(
                """
                INSERT INTO coupon_usage_log (coupon_id, user_id, pedido_id)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (coupon["id"], user_id, pedido_id),
            )
            return dict(cur.fetchone())


def create_coupon(code, discount_pct, min_order, expires_at, max_uses_per_user=2):
    """Create a new coupon (admin only)."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO coupons (code, discount_pct, min_order, expires_at, max_uses_per_user)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (code, discount_pct, min_order, expires_at, max_uses_per_user),
            )
            return dict(cur.fetchone())
