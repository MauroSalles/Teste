import os
import random
import secrets
from datetime import datetime
from decimal import Decimal

from backend.database import get_db


class ReferralService:
    """Sistema de referência inteligente - conversão > quantidade"""

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def create_referral_link(self, user_id, user_email, user_name):
        """Gera link de referência único e rastreável"""
        try:
            unique_code = self._generate_unique_code(user_id)

            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO referral_links (
                            user_id, referral_code, created_at,
                            status, total_conversions
                        ) VALUES (%s, %s, NOW(), 'active', 0)
                        RETURNING id, referral_code
                        """,
                        (user_id, unique_code),
                    )
                    row = cur.fetchone()

            referral_link = {
                "code": row["referral_code"],
                "url": f'{os.getenv("APP_URL", "")}/signup?ref={row["referral_code"]}',
                "share_message": self._get_share_message(user_name),
                "qr_code": self._generate_qr_code(row["referral_code"]),
            }

            return {"success": True, "referral_link": referral_link}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def register_referred_user(self, referral_code, new_user_id, new_user_email):
        """Registra novo usuário que veio de referência"""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT user_id FROM referral_links "
                        "WHERE referral_code = %s AND status = 'active'",
                        (referral_code,),
                    )
                    referrer = cur.fetchone()

                    if not referrer:
                        return {
                            "success": False,
                            "error": "Código de referência inválido",
                        }

                    referrer_id = referrer["user_id"]

                    cur.execute(
                        """
                        INSERT INTO referral_conversions (
                            referrer_id, referred_user_id, referral_code,
                            created_at, status
                        ) VALUES (%s, %s, %s, NOW(), 'pending')
                        """,
                        (referrer_id, new_user_id, referral_code),
                    )

                    cur.execute(
                        """
                        UPDATE referral_links
                        SET total_conversions = total_conversions + 1
                        WHERE referral_code = %s
                        """,
                        (referral_code,),
                    )

            return {"success": True, "referrer_id": referrer_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def confirm_referral_purchase(self, referred_user_id, order_total):
        """Confirma primeira compra do usuário referido"""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT referrer_id, referral_code
                        FROM referral_conversions
                        WHERE referred_user_id = %s AND status = 'pending'
                        LIMIT 1
                        """,
                        (referred_user_id,),
                    )
                    referral = cur.fetchone()

                    if not referral:
                        return {
                            "success": False,
                            "error": "Nenhuma referência pendente",
                        }

                    referrer_id = referral["referrer_id"]

                    cur.execute(
                        """
                        UPDATE referral_conversions
                        SET status = 'confirmed', confirmed_at = NOW()
                        WHERE referred_user_id = %s AND status = 'pending'
                        """,
                        (referred_user_id,),
                    )

            referrer_tier = self._get_referrer_tier(referrer_id)
            referred_tier = self._get_referred_tier(referred_user_id)

            rewards = self._calculate_referral_rewards(
                referrer_id,
                referred_user_id,
                referrer_tier,
                referred_tier,
                order_total,
            )

            self._credit_referral_rewards(referrer_id, referred_user_id, rewards)

            return {
                "success": True,
                "referrer_id": referrer_id,
                "rewards": self._serialize_rewards(rewards),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_referral_dashboard(self, user_id):
        """Dashboard com status de referências"""
        try:
            conversion_count = self._get_referral_conversion_count(user_id)
            confirmed_count = conversion_count
            referral_link = self._get_referral_link(user_id)

            if not referral_link:
                return {
                    "success": False,
                    "error": "Link de referência não encontrado",
                }

            milestones = [1, 5, 10, 15, 20]
            upcoming = [m for m in milestones if m > conversion_count]
            next_milestone = upcoming[0] if upcoming else 999

            dashboard = {
                "referral_code": referral_link["referral_code"],
                "referral_url": (
                    f'{os.getenv("APP_URL", "")}/signup?ref={referral_link["referral_code"]}'
                ),
                "qr_code": self._generate_qr_code(referral_link["referral_code"]),
                "stats": {
                    "total_conversions": conversion_count,
                    "confirmed_conversions": confirmed_count,
                    "pending_conversions": conversion_count - confirmed_count,
                },
                "progress": {
                    "next_milestone": next_milestone,
                    "progress_percent": (
                        (conversion_count / next_milestone) * 100
                        if next_milestone
                        else 100
                    ),
                },
                "share_templates": self._get_share_templates(
                    user_id, referral_link["referral_code"]
                ),
            }

            return {"success": True, "dashboard": dashboard}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_leaderboard(self, limit=10):
        """Top referrers do mês"""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            rc.referrer_id AS id,
                            COUNT(rc.id) AS total_referrals,
                            COUNT(CASE WHEN rc.status = 'confirmed' THEN 1 END)
                                AS confirmed_referrals
                        FROM referral_conversions rc
                        WHERE rc.created_at > NOW() - INTERVAL '30 days'
                        GROUP BY rc.referrer_id
                        ORDER BY confirmed_referrals DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    leaderboard = cur.fetchall()

            return {
                "success": True,
                "leaderboard": [dict(r) for r in leaderboard],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ──────────────────────────────────────────────────────────────────────────
    # Reward calculation
    # ──────────────────────────────────────────────────────────────────────────

    def _calculate_referral_rewards(
        self, referrer_id, referred_id, referrer_tier, referred_tier, order_total
    ):
        """
        NOVO SISTEMA REALISTA E ESCALÁVEL

        Foco: Qualidade > Quantidade
        Meta: Gerar usuários ativos, não spam
        """
        conversion_count = self._get_referral_conversion_count(referrer_id)

        rewards = {
            "both_get": {},
            "referrer_only": {},
            "milestone_unlocked": None,
        }

        # ══ TIER 1: 1-4 Referências (CULTIVAR) ══
        if conversion_count <= 4:
            rewards["both_get"] = {
                "type": "credit",
                "amount": Decimal("5.00"),
                "description": "Crédito por vir de amigo",
            }
            rewards["referrer_only"] = {
                "type": "discount_coupon",
                "discount_percent": 8,
                "max_value": Decimal("15.00"),
                "expires_days": 30,
                "code": f"REF_AMIGO_{conversion_count}",
                "description": f"{conversion_count} amigos = 8% OFF próximo pedido",
            }

        # ══ TIER 2: 5 Referências (MOMENTUM) ══
        elif conversion_count == 5:
            rewards["both_get"] = {
                "type": "credit",
                "amount": Decimal("7.50"),
                "description": "Bônus especial - 5 amigos chegou!",
            }
            rewards["referrer_only"] = {
                "type": "discount_coupon",
                "discount_percent": 15,
                "max_value": Decimal("25.00"),
                "expires_days": 60,
                "code": "REF_5AMIGOS",
                "description": "Atingiu 5 amigos! 15% OFF por 60 dias",
            }
            rewards["milestone_unlocked"] = {
                "name": "🌟 5 Amigos Legend",
                "badge": "legend_5friends",
                "perks": [
                    "Status especial no app",
                    "15% OFF por 2 meses",
                    "Acesso early a novos sabores",
                    "Birthday surprise +5% extra",
                ],
            }

        # ══ TIER 3: 10 Referências (AÇAÍ FREE) ══
        elif conversion_count == 10:
            rewards["both_get"] = {
                "type": "free_product",
                "product": "SMALL_ACAI",
                "expires_days": 7,
                "description": "Açaí pequeno grátis! Vale em 7 dias",
                "value": Decimal("20.00"),
            }
            rewards["referrer_only"] = {
                "type": "daily_discount",
                "discount_percent": 20,
                "duration_hours": 24,
                "starts_at": datetime.now().isoformat(),
                "description": "20% OFF em TUDO por 24h",
                "value": Decimal("50.00"),
            }
            rewards["milestone_unlocked"] = {
                "name": "👑 Top Referrer",
                "badge": "top_referrer_10",
                "perks": [
                    "20% OFF por 24h",
                    "Açaí grátis (ambos)",
                    "Exclusive merchandise",
                    "Priority support",
                    "Feature no hall da fama do app",
                ],
            }

        # ══ TIER 4+: Incentivos Contínuos (11+ referências) ══
        else:
            rewards["both_get"] = {
                "type": "credit",
                "amount": Decimal("3.00"),
                "description": "Crédito por referência",
            }
            rewards["referrer_only"] = {
                "type": "points_bonus",
                "points": 100,
                "description": "Ganhe 100 pontos por referência",
            }

        return rewards

    def _credit_referral_rewards(self, referrer_id, referred_id, rewards):
        """Credita os rewards no banco de dados"""
        try:
            both_get = rewards.get("both_get") or {}
            if both_get:
                reward_type = both_get.get("type")
                reward_value = both_get.get("amount") or both_get.get("value")
                if reward_type:
                    with get_db() as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                INSERT INTO referral_rewards (
                                    referrer_id, referred_user_id, reward_type,
                                    reward_value, status, created_at
                                ) VALUES (%s, %s, %s, %s, 'pending', NOW())
                                """,
                                (referrer_id, referred_id, reward_type, reward_value),
                            )

            referrer_only = rewards.get("referrer_only") or {}
            if referrer_only:
                r_type = referrer_only.get("type")
                r_value = referrer_only.get("max_value") or referrer_only.get("value")
                if r_type:
                    with get_db() as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                INSERT INTO referral_rewards (
                                    referrer_id, referred_user_id, reward_type,
                                    reward_value, status, created_at
                                ) VALUES (%s, %s, %s, %s, 'pending', NOW())
                                """,
                                (referrer_id, referred_id, r_type, r_value),
                            )

            return True
        except Exception as e:
            print(f"Erro creditando rewards: {e}")
            return False

    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _generate_unique_code(self, user_id):
        """Gera código único e memorável"""
        random_part = secrets.token_hex(3).upper()
        return f"REF{user_id}{random_part}"

    def _get_share_message(self, user_name):
        messages = [
            "Vem provar meu açaí favorito! Use meu código de referência",
            "Já descobriu esse lugar? Usa meu código e aproveita o desconto!",
            "Açaí top demais! Convida aí com meu código de amigo",
        ]
        return random.choice(messages)

    def _generate_qr_code(self, code):
        """Retorna URL de QR code para compartilhamento"""
        app_url = os.getenv("APP_URL", "")
        url = f"{app_url}/signup?ref={code}"
        return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}"

    def _get_referral_conversion_count(self, user_id):
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT COUNT(*) AS count FROM referral_conversions "
                        "WHERE referrer_id = %s AND status = 'confirmed'",
                        (user_id,),
                    )
                    result = cur.fetchone()
            return result["count"] if result else 0
        except Exception:
            return 0

    def _get_referral_link(self, user_id):
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT referral_code FROM referral_links "
                        "WHERE user_id = %s AND status = 'active' LIMIT 1",
                        (user_id,),
                    )
                    return cur.fetchone()
        except Exception:
            return None

    def _get_referrer_tier(self, user_id):
        return "bronze"

    def _get_referred_tier(self, user_id):
        return "bronze"

    def _get_share_templates(self, user_id, referral_code):
        app_url = os.getenv("APP_URL", "")
        return {
            "whatsapp": (
                f"Ei! Quer um açaí incrível? Usa meu código {referral_code} "
                f"e ganha R$5 de crédito! {app_url}/signup?ref={referral_code}"
            ),
            "instagram": (
                f"Convida seus amigos com meu código referência: {referral_code} "
                f"👇 Todos ganham crédito! #açaí #referência"
            ),
            "email": (
                f"Oi! Queria compartilhar esse lugar incrível de açaí. "
                f"Usa meu código {referral_code} e ganha desconto! "
                f"{app_url}/signup?ref={referral_code}"
            ),
            "facebook": (
                f"Meu lugar favorito de açaí tem um programa de referência! "
                f"Vem com meu código: {referral_code}"
            ),
        }

    def _serialize_rewards(self, rewards):
        """Convert Decimal values to float for JSON serialization"""
        def _convert(obj):
            if isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_convert(i) for i in obj]
            if isinstance(obj, Decimal):
                return float(obj)
            return obj

        return _convert(rewards)
