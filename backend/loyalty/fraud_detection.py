import logging
from datetime import datetime, timedelta

from backend.database import get_db
from backend.loyalty.constants import DISPOSABLE_EMAIL_DOMAINS

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """Detecta padrões suspeitos antes de perder dinheiro."""

    def check_suspicious_pattern(self, user_id, coupon_code):
        """Analisa comportamento antes de aplicar cupom."""
        try:
            user = self._get_user(user_id)
            if not user:
                return {"suspicious": True, "reason": "Usuário não encontrado", "action": "block"}

            if self._is_new_account(user):
                return {
                    "suspicious": True,
                    "reason": "Conta nova + cupom",
                    "action": "require_verification",
                }

            device_accounts = self._count_accounts_same_device(user_id)
            if device_accounts > 3:
                return {
                    "suspicious": True,
                    "reason": "Múltiplas contas mesmo device",
                    "action": "block",
                }

            hourly_usage = self._count_coupons_last_hour(user_id)
            if hourly_usage > 4:
                return {
                    "suspicious": True,
                    "reason": "Uso excessivo coupons (último 1h)",
                    "action": "block_24h",
                }

            if self._is_suspicious_email(user["email"]):
                return {
                    "suspicious": True,
                    "reason": "Email suspeito",
                    "action": "require_verification",
                }

            return {"suspicious": False, "action": "allow"}

        except Exception:
            logger.exception("check_suspicious_pattern failed for user %s", user_id)
            return {"suspicious": True, "action": "require_verification"}

    def get_coupon_analytics(self, start_date, end_date):
        """Analytics para saber se está quebrando a empresa."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        DATE(used_at) AS day,
                        COUNT(*) AS coupons_used,
                        SUM(discount_amount) AS total_discount,
                        AVG(discount_amount) AS avg_discount,
                        COUNT(DISTINCT user_id) AS unique_users
                    FROM coupon_usage_log
                    WHERE used_at BETWEEN %s AND %s
                    GROUP BY DATE(used_at)
                    ORDER BY day DESC
                    """,
                    (start_date, end_date),
                )
                daily_stats = [dict(r) for r in cursor.fetchall()]

        total_coupons = sum(s["coupons_used"] for s in daily_stats)
        total_discount = sum(s["total_discount"] or 0 for s in daily_stats)

        estimated_revenue = self._get_period_revenue(start_date, end_date)
        discount_percentage = (
            (float(total_discount) / float(estimated_revenue) * 100)
            if estimated_revenue and estimated_revenue > 0
            else 0
        )

        alert = None
        if discount_percentage > 10:
            alert = f"⚠️ ALERTA: {discount_percentage:.1f}% do revenue em descontos!"

        return {
            "period": f"{start_date} to {end_date}",
            "total_coupons_used": total_coupons,
            "total_discount_given": float(total_discount),
            "avg_discount_per_coupon": float(total_discount / total_coupons) if total_coupons > 0 else 0,
            "unique_users": sum(s["unique_users"] for s in daily_stats),
            "discount_percentage_of_revenue": discount_percentage,
            "alert": alert,
            "daily_breakdown": daily_stats,
        }

    def _get_user(self, user_id):
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                return cursor.fetchone()

    def _get_coupon(self, coupon_code):
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM coupons WHERE code = %s", (coupon_code,))
                return cursor.fetchone()

    def _is_new_account(self, user):
        """Retorna True se conta foi criada há menos de 24 horas."""
        created_at = user.get("created_at")
        if not created_at:
            return False
        return datetime.now() - created_at < timedelta(hours=24)

    def _count_accounts_same_device(self, user_id):
        """Conta quantas contas têm o mesmo device_id."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM users
                    WHERE device_id = (
                        SELECT device_id FROM users WHERE id = %s AND device_id IS NOT NULL
                    )
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return row["count"] if row else 0

    def _count_coupons_last_hour(self, user_id):
        """Conta cupons usados pelo usuário na última hora."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM coupon_usage_log
                    WHERE user_id = %s
                    AND used_at >= NOW() - INTERVAL '1 hour'
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return row["count"] if row else 0

    def _is_suspicious_email(self, email):
        """Verifica se o domínio do email é suspeito."""
        if not email or "@" not in email:
            return True
        domain = email.split("@", 1)[1].lower()
        return domain in DISPOSABLE_EMAIL_DOMAINS

    def _get_period_revenue(self, start_date, end_date):
        """Retorna receita total do período."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(final_total), 0) AS revenue
                    FROM orders
                    WHERE status = 'delivered'
                    AND created_at BETWEEN %s AND %s
                    """,
                    (start_date, end_date),
                )
                row = cursor.fetchone()
                return row["revenue"] if row else 0
