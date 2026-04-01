import logging
from datetime import date

from backend.database import get_db

logger = logging.getLogger(__name__)


def create_coupon(
    code: str,
    discount_pct: float,
    max_discount_brl: float,
    min_order_brl: float,
    expiry_date,
    max_uses_per_day: int = 5,
    max_uses_per_month: int = 2,
) -> dict:
    sql = """
        INSERT INTO coupons
            (code, discount_pct, max_discount_brl, min_order_brl, expiry_date, max_uses_per_day, max_uses_per_month)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                code, discount_pct, max_discount_brl, min_order_brl,
                expiry_date, max_uses_per_day, max_uses_per_month,
            ))
            return dict(cur.fetchone())


def validate_coupon(code: str, user_id: int, order_value: float) -> dict:
    """9-step coupon validation. Returns discount amount on success."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Step 1: existence
            cur.execute("SELECT * FROM coupons WHERE code = %s", (code,))
            coupon = cur.fetchone()
            if not coupon:
                return {"valid": False, "error": "Cupom não encontrado"}
            coupon = dict(coupon)

            # Step 2: active
            if not coupon.get("is_active"):
                return {"valid": False, "error": "Cupom inativo"}

            # Step 3: not expired
            expiry = coupon.get("expiry_date")
            if expiry and date.today() > expiry:
                return {"valid": False, "error": "Cupom expirado"}

            # Step 4: single use per user
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM coupon_usage_log WHERE coupon_id = %s AND user_id = %s",
                (coupon["id"], user_id),
            )
            if cur.fetchone()["cnt"] > 0:
                return {"valid": False, "error": "Cupom já utilizado por este usuário"}

            # Step 5: daily cap
            cur.execute(
                """
                SELECT COUNT(*) AS cnt FROM coupon_usage_log
                WHERE coupon_id = %s AND used_at::date = CURRENT_DATE
                """,
                (coupon["id"],),
            )
            if cur.fetchone()["cnt"] >= coupon.get("max_uses_per_day", 5):
                return {"valid": False, "error": "Limite diário de uso do cupom atingido"}

            # Step 6: monthly cap (per user)
            cur.execute(
                """
                SELECT COUNT(*) AS cnt FROM coupon_usage_log
                WHERE coupon_id = %s AND user_id = %s
                  AND DATE_TRUNC('month', used_at) = DATE_TRUNC('month', CURRENT_DATE)
                """,
                (coupon["id"], user_id),
            )
            if cur.fetchone()["cnt"] >= coupon.get("max_uses_per_month", 2):
                return {"valid": False, "error": "Limite mensal de uso do cupom atingido"}

            # Step 7: min order
            min_order = float(coupon.get("min_order_brl", 0))
            if order_value < min_order:
                return {
                    "valid": False,
                    "error": f"Pedido mínimo de R${min_order:.2f} necessário para este cupom",
                }

            # Step 8 & 9: compute discount
            raw_discount = order_value * float(coupon["discount_pct"]) / 100
            max_disc = float(coupon.get("max_discount_brl", 9999))
            cap_50 = order_value * 0.5
            discount = min(raw_discount, max_disc, cap_50)

            return {
                "valid": True,
                "coupon_id": coupon["id"],
                "code": code,
                "discount_pct": float(coupon["discount_pct"]),
                "discount_amount": round(discount, 2),
            }


def apply_coupon(code: str, user_id: int, order_value: float) -> dict:
    """Validate and record coupon usage."""
    result = validate_coupon(code, user_id, order_value)
    if not result.get("valid"):
        return result

    sql = """
        INSERT INTO coupon_usage_log (coupon_id, user_id, order_value, discount_applied)
        VALUES (%s, %s, %s, %s)
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (result["coupon_id"], user_id, order_value, result["discount_amount"]))

    return result
