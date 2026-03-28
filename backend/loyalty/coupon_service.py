import logging
from datetime import datetime
from decimal import Decimal

from backend.database import get_db
from backend.loyalty.constants import PRODUCT_COSTS

logger = logging.getLogger(__name__)


class CouponService:
    """Sistema de coupons blindado contra fraude + prejuízo."""

    max_coupons_per_user_per_month = 2
    max_discount_per_order = Decimal("20.00")
    daily_max_coupon_usage = 5

    def validate_coupon(self, coupon_code, user_id, order_total):
        """Valida cupom ANTES de aplicar."""
        try:
            coupon = self._get_coupon(coupon_code)
            if not coupon:
                return {"valid": False, "error": "Cupom não encontrado"}

            if coupon["user_id"] != user_id:
                return {"valid": False, "error": "Cupom não é seu"}

            if datetime.now() > coupon["valid_until"]:
                return {"valid": False, "error": "Cupom expirado"}

            if coupon["current_uses"] >= coupon["max_uses"]:
                return {"valid": False, "error": "Cupom já foi utilizado"}

            today_usage = self._count_today_coupon_usage(user_id)
            if today_usage >= self.daily_max_coupon_usage:
                return {"valid": False, "error": "Você já usou seu limite de coupons hoje"}

            month_coupons = self._count_month_coupons_used(user_id)
            if month_coupons >= self.max_coupons_per_user_per_month:
                return {"valid": False, "error": "Limite de coupons/mês atingido"}

            min_order = coupon.get("min_order_value") or Decimal("0")
            if order_total < min_order:
                return {
                    "valid": False,
                    "error": f"Pedido mínimo: R${min_order:.2f}",
                }

            discount = self._calculate_safe_discount(coupon, order_total)
            if discount > self.max_discount_per_order:
                discount = self.max_discount_per_order

            return {
                "valid": True,
                "coupon_code": coupon_code,
                "discount_amount": float(discount),
                "new_total": float(order_total - discount),
                "coupon_uses_remaining": coupon["max_uses"] - coupon["current_uses"] - 1,
            }

        except Exception as e:
            logger.exception("validate_coupon failed")
            return {"valid": False, "error": str(e)}

    def apply_coupon(self, coupon_code, user_id, order_id, original_total):
        """Aplica cupom à ordem (após validação)."""
        try:
            validation = self.validate_coupon(coupon_code, user_id, original_total)
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}

            discount = Decimal(str(validation["discount_amount"]))

            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE coupons SET current_uses = current_uses + 1, last_used_at = NOW() WHERE code = %s",
                        (coupon_code,),
                    )
                    cursor.execute(
                        """
                        UPDATE orders
                        SET applied_coupon = %s,
                            discount_amount = %s,
                            final_total = %s
                        WHERE id = %s
                        """,
                        (coupon_code, discount, original_total - discount, order_id),
                    )

            self._log_coupon_usage(user_id, coupon_code, order_id, discount)

            return {
                "success": True,
                "discount_applied": float(discount),
                "final_total": float(original_total - discount),
            }

        except Exception as e:
            logger.exception("apply_coupon failed")
            return {"success": False, "error": str(e)}

    def _get_coupon(self, coupon_code):
        """Busca cupom pelo código."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM coupons WHERE code = %s",
                    (coupon_code,),
                )
                return cursor.fetchone()

    def _calculate_safe_discount(self, coupon, order_total):
        """Calcula desconto sem quebrar o lucro."""
        discount_type = coupon.get("discount_type")

        if discount_type == "percentage":
            pct = Decimal(str(coupon["discount_percentage"] or 0))
            discount = (order_total * pct) / 100

        elif discount_type == "fixed":
            discount = Decimal(str(coupon["discount_value"] or 0))

        elif discount_type == "free_product":
            product_key = coupon.get("discount_value", "small_acai")
            product_cost = Decimal(PRODUCT_COSTS.get(str(product_key), "20.00"))
            discount = min(product_cost, self.max_discount_per_order)

        else:
            discount = Decimal("0")

        max_allowed = order_total * Decimal("0.5")
        return min(discount, max_allowed)

    def _count_month_coupons_used(self, user_id):
        """Conta quantos cupons o usuário usou neste mês."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM coupon_usage_log
                    WHERE user_id = %s
                    AND EXTRACT(MONTH FROM used_at) = EXTRACT(MONTH FROM NOW())
                    AND EXTRACT(YEAR FROM used_at) = EXTRACT(YEAR FROM NOW())
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return row["count"]

    def _count_today_coupon_usage(self, user_id):
        """Conta quantos cupons o usuário usou hoje."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM coupon_usage_log
                    WHERE user_id = %s
                    AND DATE(used_at) = CURRENT_DATE
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return row["count"]

    def get_user_active_coupons(self, user_id):
        """Lista cupons ativos do usuário."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        code,
                        discount_percentage,
                        discount_type,
                        discount_value,
                        valid_until,
                        max_uses,
                        current_uses,
                        tier_level,
                        (max_uses - current_uses) AS remaining_uses
                    FROM coupons
                    WHERE user_id = %s
                    AND status = 'active'
                    AND valid_until > NOW()
                    AND current_uses < max_uses
                    ORDER BY valid_until ASC
                    """,
                    (user_id,),
                )
                coupons = cursor.fetchall()
                return {"coupons": [dict(c) for c in coupons]}

    def _log_coupon_usage(self, user_id, coupon_code, order_id, discount_amount):
        """Registra uso para auditoria."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO coupon_usage_log (user_id, coupon_code, order_id, discount_amount, used_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (user_id, coupon_code, order_id, discount_amount),
                )
