"""Tests for the Referral System (loyalty module)."""

import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from backend.loyalty.referral_service import ReferralService


# ──────────────────────────────────────────────────────────────────────────────
# Helper — build a service with a mocked conversion count
# ──────────────────────────────────────────────────────────────────────────────

def _service_with_count(count):
    svc = ReferralService()
    svc._get_referral_conversion_count = MagicMock(return_value=count)
    return svc


# ──────────────────────────────────────────────────────────────────────────────
# Reward-calculation unit tests (no DB required)
# ──────────────────────────────────────────────────────────────────────────────

class TestCalculateReferralRewards:
    def test_tier_1_credit_and_coupon(self):
        """1-4 amigos: R$5 crédito para o referido + cupom 8% para o referidor"""
        svc = _service_with_count(2)
        rewards = svc._calculate_referral_rewards(1, 2, "silver", "bronze", 100)

        assert rewards["both_get"]["type"] == "credit"
        assert rewards["both_get"]["amount"] == Decimal("5.00")
        assert rewards["referrer_only"]["type"] == "discount_coupon"
        assert rewards["referrer_only"]["discount_percent"] == 8
        assert rewards["milestone_unlocked"] is None

    def test_tier_1_boundary_zero_conversions(self):
        """0 conversões ainda é Tier 1"""
        svc = _service_with_count(0)
        rewards = svc._calculate_referral_rewards(1, 2, "bronze", "bronze", 50)

        assert rewards["both_get"]["type"] == "credit"
        assert rewards["both_get"]["amount"] == Decimal("5.00")

    def test_tier_2_five_friends_milestone(self):
        """5 amigos: R$7.50 crédito + cupom 15% + badge desbloqueado"""
        svc = _service_with_count(5)
        rewards = svc._calculate_referral_rewards(1, 2, "gold", "silver", 100)

        assert rewards["both_get"]["type"] == "credit"
        assert rewards["both_get"]["amount"] == Decimal("7.50")
        assert rewards["referrer_only"]["discount_percent"] == 15
        assert rewards["referrer_only"]["expires_days"] == 60
        assert rewards["milestone_unlocked"] is not None
        assert "5 Amigos" in rewards["milestone_unlocked"]["name"]
        assert rewards["milestone_unlocked"]["badge"] == "legend_5friends"

    def test_tier_3_ten_friends_milestone(self):
        """10 amigos: produto grátis + desconto diário 20% + badge Top Referrer"""
        svc = _service_with_count(10)
        rewards = svc._calculate_referral_rewards(1, 2, "platinum", "gold", 100)

        assert rewards["both_get"]["type"] == "free_product"
        assert rewards["both_get"]["product"] == "SMALL_ACAI"
        assert rewards["referrer_only"]["type"] == "daily_discount"
        assert rewards["referrer_only"]["discount_percent"] == 20
        assert rewards["milestone_unlocked"] is not None
        assert rewards["milestone_unlocked"]["badge"] == "top_referrer_10"

    def test_tier_4_continued_points(self):
        """11+ amigos: crédito reduzido R$3 + bônus de pontos"""
        svc = _service_with_count(11)
        rewards = svc._calculate_referral_rewards(1, 2, "gold", "bronze", 200)

        assert rewards["both_get"]["type"] == "credit"
        assert rewards["both_get"]["amount"] == Decimal("3.00")
        assert rewards["referrer_only"]["type"] == "points_bonus"
        assert rewards["referrer_only"]["points"] == 100

    def test_tier_4_high_count(self):
        """50+ amigos também cai no Tier 4"""
        svc = _service_with_count(50)
        rewards = svc._calculate_referral_rewards(1, 2, "gold", "bronze", 150)

        assert rewards["both_get"]["type"] == "credit"
        assert rewards["both_get"]["amount"] == Decimal("3.00")


class TestSerializeRewards:
    def test_decimal_values_become_float(self):
        svc = ReferralService()
        rewards = {
            "both_get": {"type": "credit", "amount": Decimal("5.00")},
            "referrer_only": {"type": "discount_coupon", "max_value": Decimal("15.00")},
            "milestone_unlocked": None,
        }
        serialized = svc._serialize_rewards(rewards)

        assert isinstance(serialized["both_get"]["amount"], float)
        assert serialized["both_get"]["amount"] == 5.0
        assert isinstance(serialized["referrer_only"]["max_value"], float)

    def test_nested_list_preserved(self):
        svc = ReferralService()
        rewards = {
            "milestone_unlocked": {
                "name": "Test",
                "perks": ["perk1", "perk2"],
            },
            "both_get": {},
            "referrer_only": {},
        }
        serialized = svc._serialize_rewards(rewards)
        assert serialized["milestone_unlocked"]["perks"] == ["perk1", "perk2"]


class TestGenerateUniqueCode:
    def test_code_starts_with_ref_and_user_id(self):
        svc = ReferralService()
        code = svc._generate_unique_code(42)
        assert code.startswith("REF42")

    def test_codes_are_unique(self):
        svc = ReferralService()
        codes = {svc._generate_unique_code(1) for _ in range(20)}
        # Very unlikely to have a collision with 20 attempts
        assert len(codes) > 1


class TestGetShareTemplates:
    def test_templates_contain_referral_code(self):
        svc = ReferralService()
        templates = svc._get_share_templates(1, "REFTEST123")

        for platform, text in templates.items():
            assert "REFTEST123" in text, f"Platform {platform} missing referral code"

    def test_all_platforms_present(self):
        svc = ReferralService()
        templates = svc._get_share_templates(1, "CODE")

        assert "whatsapp" in templates
        assert "instagram" in templates
        assert "email" in templates
        assert "facebook" in templates


# ──────────────────────────────────────────────────────────────────────────────
# Route integration tests (Flask test client, DB mocked)
# ──────────────────────────────────────────────────────────────────────────────

class TestReferralRoutes:
    def test_leaderboard_returns_200(self, client):
        with patch(
            "backend.routes.referral_routes.referral_service"
        ) as mock_svc:
            mock_svc.get_leaderboard.return_value = {
                "success": True,
                "leaderboard": [],
            }
            response = client.get("/api/referral/leaderboard")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_leaderboard_custom_limit(self, client):
        with patch(
            "backend.routes.referral_routes.referral_service"
        ) as mock_svc:
            mock_svc.get_leaderboard.return_value = {
                "success": True,
                "leaderboard": [],
            }
            client.get("/api/referral/leaderboard?limit=5")
            mock_svc.get_leaderboard.assert_called_once_with(5)

    def test_dashboard_returns_200_on_success(self, client):
        with patch(
            "backend.routes.referral_routes.referral_service"
        ) as mock_svc:
            mock_svc.get_referral_dashboard.return_value = {
                "success": True,
                "dashboard": {"referral_code": "REF1ABC"},
            }
            response = client.get("/api/referral/dashboard/1")

        assert response.status_code == 200

    def test_dashboard_returns_400_on_error(self, client):
        with patch(
            "backend.routes.referral_routes.referral_service"
        ) as mock_svc:
            mock_svc.get_referral_dashboard.return_value = {
                "success": False,
                "error": "Not found",
            }
            response = client.get("/api/referral/dashboard/999")

        assert response.status_code == 400

    def test_register_referred_missing_fields(self, client):
        response = client.post(
            "/api/referral/register-referred",
            json={"referral_code": "REF1ABC"},  # missing user_id
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_register_referred_success(self, client):
        with patch(
            "backend.routes.referral_routes.referral_service"
        ) as mock_svc:
            mock_svc.register_referred_user.return_value = {
                "success": True,
                "referrer_id": 1,
            }
            response = client.post(
                "/api/referral/register-referred",
                json={"referral_code": "REF1ABC", "user_id": 2},
                content_type="application/json",
            )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_confirm_purchase_missing_order_total(self, client):
        response = client.post(
            "/api/referral/confirm-purchase/2",
            json={},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_confirm_purchase_success(self, client):
        with patch(
            "backend.routes.referral_routes.referral_service"
        ) as mock_svc:
            mock_svc.confirm_referral_purchase.return_value = {
                "success": True,
                "referrer_id": 1,
                "rewards": {},
            }
            response = client.post(
                "/api/referral/confirm-purchase/2",
                json={"order_total": 50.0},
                content_type="application/json",
            )

        assert response.status_code == 200

    def test_create_link_returns_200_on_success(self, client):
        with patch(
            "backend.routes.referral_routes.referral_service"
        ) as mock_svc:
            mock_svc.create_referral_link.return_value = {
                "success": True,
                "referral_link": {"code": "REF1XYZ"},
            }
            response = client.post("/api/referral/link/1")

        assert response.status_code == 200
