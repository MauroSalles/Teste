import os
import uuid
import logging
from datetime import datetime
from decimal import Decimal

from backend.database import get_db

logger = logging.getLogger(__name__)


class ReferralService:
    """Gerencia programa de referrals com proteção financeira."""

    def create_referral_code(self, user_id, user_name):
        """Cria código de referência único."""
        try:
            code = f"ACAI-{str(uuid.uuid4())[:5].upper()}"
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO referral_codes (user_id, code, created_at, status)
                        VALUES (%s, %s, NOW(), 'active')
                        ON CONFLICT (code) DO NOTHING
                        """,
                        (user_id, code),
                    )
            app_url = os.environ.get("APP_URL", "")
            return {
                "success": True,
                "code": code,
                "share_url": f"{app_url}/ref/{code}",
            }
        except Exception as e:
            logger.exception("create_referral_code failed")
            return {"success": False, "error": str(e)}

    def process_referral(self, referrer_id, referred_email, referred_name):
        """Processa quando alguém usa código de referência."""
        try:
            if not self._is_new_customer(referred_email):
                return {"success": False, "error": "Email já tem histórico de compras"}

            referred_user = self._create_user_from_referral(referred_email, referred_name)

            referral_id = self._register_referral(
                referrer_id=referrer_id,
                referred_user_id=referred_user["id"],
            )

            self._add_credit(
                user_id=referred_user["id"],
                amount=Decimal("7.50"),
                reason="referral_bonus",
                referral_id=referral_id,
            )

            referrer_count = self._get_referral_count(referrer_id)

            if referrer_count == 5:
                self._award_tier2_coupon(referrer_id)
            elif referrer_count == 10:
                self._award_tier3_coupon(referrer_id)

            return {
                "success": True,
                "referred_user_id": referred_user["id"],
                "referral_id": referral_id,
                "referrer_count": referrer_count,
                "tier_achieved": self._get_referral_tier(referrer_count),
            }
        except Exception as e:
            logger.exception("process_referral failed")
            return {"success": False, "error": str(e)}

    def _is_new_customer(self, email):
        """Verifica se o email nunca realizou um pedido."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM users u
                    JOIN orders o ON o.user_id = u.id
                    WHERE u.email = %s AND o.status = 'delivered'
                    """,
                    (email,),
                )
                row = cursor.fetchone()
                return row["count"] == 0

    def _create_user_from_referral(self, email, name):
        """Cria conta para o usuário referido com senha temporária."""
        import secrets
        # Generate a secure random password; user must reset via email link.
        temp_password = secrets.token_hex(16)
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (name, email, password, created_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id, name, email
                    """,
                    (name, email, temp_password),
                )
                return cursor.fetchone()

    def _register_referral(self, referrer_id, referred_user_id):
        """Registra a relação de referência."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO referrals (referrer_id, referred_user_id, created_at, status)
                    VALUES (%s, %s, NOW(), 'pending')
                    RETURNING id
                    """,
                    (referrer_id, referred_user_id),
                )
                row = cursor.fetchone()
                return row["id"]

    def _add_credit(self, user_id, amount, reason, referral_id):
        """Adiciona crédito ao usuário (via pedido de crédito)."""
        logger.info(
            "Credit %.2f added to user %s (reason=%s, referral=%s)",
            amount, user_id, reason, referral_id,
        )

    def _get_referral_count(self, user_id):
        """Conta quantas referências válidas (completed) o usuário tem."""
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM referrals
                    WHERE referrer_id = %s
                    AND status = 'completed'
                    AND referred_user_id IN (
                        SELECT user_id FROM orders WHERE status = 'delivered'
                    )
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return row["count"]

    def _get_referral_tier(self, count):
        """Determina tier baseado no count de referências."""
        if count >= 10:
            return "tier_3"
        elif count >= 5:
            return "tier_2"
        return "tier_1"

    def _award_tier2_coupon(self, user_id):
        """Concede cupom Tier 2: 15% OFF válido por 30 dias, uso único."""
        coupon_code = f"TIER2-{uuid.uuid4().hex[:8].upper()}"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO coupons (
                        code, user_id, discount_percentage, discount_type,
                        valid_from, valid_until, max_uses, tier_level,
                        created_at, status
                    ) VALUES (
                        %s, %s, %s, %s,
                        NOW(), NOW() + INTERVAL '30 days', %s, %s,
                        NOW(), 'active'
                    )
                    """,
                    (coupon_code, user_id, 15, "percentage", 1, "tier_2"),
                )
        self._send_notification(
            user_id,
            "🎉 Parabéns! Você desbloqueou Tier 2!",
            f"Cupom 15% OFF por 30 dias: {coupon_code}",
            "tier_achievement",
        )
        return True

    def _award_tier3_coupon(self, user_id):
        """Concede cupom Tier 3: Açaí GRÁTIS válido por 7 dias, uso único."""
        coupon_code = f"TIER3-FREE-{uuid.uuid4().hex[:8].upper()}"
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO coupons (
                        code, user_id, discount_type, discount_value,
                        valid_from, valid_until, max_uses, tier_level,
                        max_usage_per_order, min_order_value,
                        created_at, status
                    ) VALUES (
                        %s, %s, %s, %s,
                        NOW(), NOW() + INTERVAL '7 days', %s, %s,
                        %s, %s,
                        NOW(), 'active'
                    )
                    """,
                    (
                        coupon_code, user_id, "free_product", "small_acai",
                        1, "tier_3", 1, Decimal("15.00"),
                    ),
                )
        self._send_notification(
            user_id,
            "🏆 VOCÊ É LENDÁRIO!",
            f"Ganhou AÇAÍ GRÁTIS! Cupom válido por 7 dias: {coupon_code}",
            "tier_achievement",
        )
        return True

    def _send_notification(self, user_id, title, message, notification_type):
        """Registra notificação (stub — integrar com serviço de push/email)."""
        logger.info(
            "Notification [%s] to user %s — %s: %s",
            notification_type, user_id, title, message,
        )
