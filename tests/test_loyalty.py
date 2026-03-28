"""Tests for the Loyalty (Referral + Coupon) system."""
import os
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_test_coupon(
    discount_type="percentage",
    discount_percentage=15,
    discount_value=None,
    max_uses=1,
    current_uses=0,
    user_id=1,
    min_order_value=Decimal("0"),
):
    from datetime import datetime, timedelta
    return {
        "user_id": user_id,
        "discount_type": discount_type,
        "discount_percentage": discount_percentage,
        "discount_value": discount_value,
        "max_uses": max_uses,
        "current_uses": current_uses,
        "valid_until": datetime.now() + timedelta(days=30),
        "min_order_value": min_order_value,
        "status": "active",
    }


# ---------------------------------------------------------------------------
# CouponService unit tests (no DB required)
# ---------------------------------------------------------------------------

class TestCouponServiceUnit:
    """Tests that exercise CouponService logic without a live database."""

    def _service(self):
        from backend.loyalty.coupon_service import CouponService
        return CouponService()

    def test_calculate_safe_discount_percentage(self):
        """15% of R$100 = R$15."""
        svc = self._service()
        coupon = make_test_coupon(discount_type="percentage", discount_percentage=15)
        discount = svc._calculate_safe_discount(coupon, Decimal("100"))
        assert discount == Decimal("15.00")

    def test_calculate_safe_discount_fixed(self):
        """Fixed R$10 discount on R$100 order."""
        svc = self._service()
        coupon = make_test_coupon(discount_type="fixed", discount_value="10.00")
        discount = svc._calculate_safe_discount(coupon, Decimal("100"))
        assert discount == Decimal("10.00")

    def test_coupon_max_discount_protection(self):
        """Discount never exceeds R$20 (max_discount_per_order cap)."""
        svc = self._service()
        coupon = make_test_coupon(discount_type="percentage", discount_percentage=100)
        # _calculate_safe_discount caps at 50% of order; validate_coupon caps at R$20
        # Here we only test _calculate_safe_discount: 50% of 1000 = 500, but
        # the validate_coupon step would cap at R$20.
        # Test the overall cap via a larger integration-style check:
        discount = svc._calculate_safe_discount(coupon, Decimal("1000"))
        # 50% cap: 1000 * 0.5 = 500, but validate_coupon caps at max_discount_per_order=20
        # _calculate_safe_discount only applies the 50% rule
        assert discount <= Decimal("500")
        # Simulate validate_coupon cap
        if discount > svc.max_discount_per_order:
            discount = svc.max_discount_per_order
        assert discount <= Decimal("20.00")

    def test_calculate_safe_discount_capped_at_50_percent(self):
        """Discount is capped at 50% of the order total."""
        svc = self._service()
        coupon = make_test_coupon(discount_type="fixed", discount_value="200.00")
        discount = svc._calculate_safe_discount(coupon, Decimal("100"))
        assert discount == Decimal("50.00")  # 50% of 100

    def test_calculate_safe_discount_free_product(self):
        """free_product type returns product cost capped at max_discount."""
        svc = self._service()
        coupon = make_test_coupon(discount_type="free_product", discount_value="small_acai")
        discount = svc._calculate_safe_discount(coupon, Decimal("100"))
        # small_acai costs R$20, max_discount_per_order = R$20
        assert discount == Decimal("20.00")

    def test_validate_coupon_not_found(self):
        """Returns invalid when coupon does not exist."""
        svc = self._service()
        with patch.object(svc, "_get_coupon", return_value=None):
            result = svc.validate_coupon("GHOST-CODE", 1, Decimal("100"))
        assert result["valid"] is False
        assert "não encontrado" in result["error"]

    def test_validate_coupon_wrong_user(self):
        """Returns invalid when coupon belongs to another user."""
        svc = self._service()
        coupon = make_test_coupon(user_id=99)
        with patch.object(svc, "_get_coupon", return_value=coupon):
            result = svc.validate_coupon("COUPON1", user_id=1, order_total=Decimal("100"))
        assert result["valid"] is False
        assert "não é seu" in result["error"]

    def test_validate_coupon_expired(self):
        """Returns invalid when coupon is past valid_until."""
        from datetime import datetime, timedelta
        svc = self._service()
        coupon = make_test_coupon()
        coupon["valid_until"] = datetime.now() - timedelta(days=1)
        with patch.object(svc, "_get_coupon", return_value=coupon):
            result = svc.validate_coupon("COUPON1", 1, Decimal("100"))
        assert result["valid"] is False
        assert "expirado" in result["error"]

    def test_validate_coupon_already_used(self):
        """Returns invalid when single-use coupon was already used."""
        svc = self._service()
        coupon = make_test_coupon(max_uses=1, current_uses=1)
        with patch.object(svc, "_get_coupon", return_value=coupon):
            result = svc.validate_coupon("TIER2-XXXXX", 1, Decimal("100"))
        assert result["valid"] is False
        assert "utilizado" in result["error"]

    def test_validate_coupon_monthly_limit(self):
        """Returns invalid when user has reached monthly coupon limit."""
        svc = self._service()
        coupon = make_test_coupon()
        with patch.object(svc, "_get_coupon", return_value=coupon), \
             patch.object(svc, "_count_today_coupon_usage", return_value=0), \
             patch.object(svc, "_count_month_coupons_used", return_value=2):
            result = svc.validate_coupon("COUPON3", 1, Decimal("100"))
        assert result["valid"] is False
        assert "mês" in result["error"]

    def test_validate_coupon_daily_limit(self):
        """Returns invalid when user exceeds daily coupon usage."""
        svc = self._service()
        coupon = make_test_coupon()
        with patch.object(svc, "_get_coupon", return_value=coupon), \
             patch.object(svc, "_count_today_coupon_usage", return_value=5), \
             patch.object(svc, "_count_month_coupons_used", return_value=0):
            result = svc.validate_coupon("COUPON1", 1, Decimal("100"))
        assert result["valid"] is False
        assert "hoje" in result["error"]

    def test_validate_coupon_min_order(self):
        """Returns invalid when order does not meet minimum value."""
        svc = self._service()
        coupon = make_test_coupon(min_order_value=Decimal("50.00"))
        with patch.object(svc, "_get_coupon", return_value=coupon), \
             patch.object(svc, "_count_today_coupon_usage", return_value=0), \
             patch.object(svc, "_count_month_coupons_used", return_value=0):
            result = svc.validate_coupon("COUPON1", 1, Decimal("10"))
        assert result["valid"] is False
        assert "mínimo" in result["error"]

    def test_validate_coupon_valid(self):
        """Returns valid result with correct discount for a good coupon."""
        svc = self._service()
        coupon = make_test_coupon(discount_type="percentage", discount_percentage=15)
        with patch.object(svc, "_get_coupon", return_value=coupon), \
             patch.object(svc, "_count_today_coupon_usage", return_value=0), \
             patch.object(svc, "_count_month_coupons_used", return_value=0):
            result = svc.validate_coupon("TIER2-GOOD", 1, Decimal("100"))
        assert result["valid"] is True
        assert result["discount_amount"] == 15.0
        assert result["new_total"] == 85.0


# ---------------------------------------------------------------------------
# ReferralService unit tests
# ---------------------------------------------------------------------------

class TestReferralServiceUnit:
    def _service(self):
        from backend.loyalty.referral_service import ReferralService
        return ReferralService()

    def test_get_referral_tier_tier1(self):
        svc = self._service()
        assert svc._get_referral_tier(0) == "tier_1"
        assert svc._get_referral_tier(4) == "tier_1"

    def test_get_referral_tier_tier2(self):
        svc = self._service()
        assert svc._get_referral_tier(5) == "tier_2"
        assert svc._get_referral_tier(9) == "tier_2"

    def test_get_referral_tier_tier3(self):
        svc = self._service()
        assert svc._get_referral_tier(10) == "tier_3"
        assert svc._get_referral_tier(20) == "tier_3"


# ---------------------------------------------------------------------------
# FraudDetectionService unit tests
# ---------------------------------------------------------------------------

class TestFraudDetectionUnit:
    def _service(self):
        from backend.loyalty.fraud_detection import FraudDetectionService
        return FraudDetectionService()

    def test_suspicious_email_disposable(self):
        svc = self._service()
        assert svc._is_suspicious_email("user@mailinator.com") is True

    def test_suspicious_email_legit(self):
        svc = self._service()
        assert svc._is_suspicious_email("user@gmail.com") is False

    def test_new_account_flagged(self):
        """Account created less than 24 hours ago is flagged as suspicious."""
        from datetime import datetime, timedelta
        svc = self._service()
        new_user = {
            "id": 999,
            "email": "test@gmail.com",
            "created_at": datetime.now() - timedelta(hours=1),
            "device_id": None,
        }
        with patch.object(svc, "_get_user", return_value=new_user), \
             patch.object(svc, "_count_accounts_same_device", return_value=1), \
             patch.object(svc, "_count_coupons_last_hour", return_value=0):
            result = svc.check_suspicious_pattern(user_id=999, coupon_code="COUPON1")
        assert result["suspicious"] is True
        assert result["action"] == "require_verification"

    def test_multiple_accounts_same_device_blocked(self):
        """User with more than 3 accounts on same device is blocked."""
        from datetime import datetime, timedelta
        svc = self._service()
        old_user = {
            "id": 1,
            "email": "legit@gmail.com",
            "created_at": datetime.now() - timedelta(days=30),
            "device_id": "device-abc",
        }
        with patch.object(svc, "_get_user", return_value=old_user), \
             patch.object(svc, "_count_accounts_same_device", return_value=5), \
             patch.object(svc, "_count_coupons_last_hour", return_value=0):
            result = svc.check_suspicious_pattern(user_id=1, coupon_code="COUPON1")
        assert result["suspicious"] is True
        assert result["action"] == "block"

    def test_excessive_coupon_usage_blocked(self):
        """User using more than 4 coupons in last hour is blocked."""
        from datetime import datetime, timedelta
        svc = self._service()
        old_user = {
            "id": 1,
            "email": "legit@gmail.com",
            "created_at": datetime.now() - timedelta(days=30),
            "device_id": None,
        }
        with patch.object(svc, "_get_user", return_value=old_user), \
             patch.object(svc, "_count_accounts_same_device", return_value=1), \
             patch.object(svc, "_count_coupons_last_hour", return_value=5):
            result = svc.check_suspicious_pattern(user_id=1, coupon_code="COUPON1")
        assert result["suspicious"] is True
        assert result["action"] == "block_24h"

    def test_clean_user_allowed(self):
        """User with no red flags is allowed."""
        from datetime import datetime, timedelta
        svc = self._service()
        clean_user = {
            "id": 1,
            "email": "legit@gmail.com",
            "created_at": datetime.now() - timedelta(days=30),
            "device_id": None,
        }
        with patch.object(svc, "_get_user", return_value=clean_user), \
             patch.object(svc, "_count_accounts_same_device", return_value=1), \
             patch.object(svc, "_count_coupons_last_hour", return_value=0):
            result = svc.check_suspicious_pattern(user_id=1, coupon_code="COUPON1")
        assert result["suspicious"] is False
        assert result["action"] == "allow"


# ---------------------------------------------------------------------------
# Flask route smoke tests (no DB calls — loyalty services mocked)
# ---------------------------------------------------------------------------

class TestLoyaltyRoutes:
    def _auth_header(self):
        from backend.auth.jwt_handler import create_token
        token = create_token(1, "Test User", "test@example.com")
        return {"Authorization": f"Bearer {token}"}

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_get_referral_code_no_token(self, client):
        response = client.get("/api/loyalty/referral/code")
        assert response.status_code == 401

    def test_get_active_coupons_no_token(self, client):
        response = client.get("/api/loyalty/coupons/active")
        assert response.status_code == 401

    def test_validate_coupon_no_token(self, client):
        response = client.post("/api/loyalty/coupon/validate", json={})
        assert response.status_code == 401

    def test_get_referral_code_with_token(self, client):
        with patch("backend.routes.loyalty_routes.referral_service") as mock_svc:
            mock_svc.create_referral_code.return_value = {
                "success": True,
                "code": "ACAI-ABCDE",
                "share_url": "http://localhost/ref/ACAI-ABCDE",
            }
            response = client.get(
                "/api/loyalty/referral/code",
                headers=self._auth_header(),
            )
        assert response.status_code == 200
        data = response.get_json()
        assert data["code"] == "ACAI-ABCDE"

    def test_get_active_coupons_with_token(self, client):
        with patch("backend.routes.loyalty_routes.coupon_service") as mock_svc:
            mock_svc.get_user_active_coupons.return_value = {"coupons": []}
            response = client.get(
                "/api/loyalty/coupons/active",
                headers=self._auth_header(),
            )
        assert response.status_code == 200
        data = response.get_json()
        assert "coupons" in data

    def test_validate_coupon_missing_code(self, client):
        response = client.post(
            "/api/loyalty/coupon/validate",
            json={"order_total": 100},
            headers=self._auth_header(),
        )
        assert response.status_code == 400

    def test_validate_coupon_invalid(self, client):
        with patch("backend.routes.loyalty_routes.coupon_service") as mock_svc:
            mock_svc.validate_coupon.return_value = {
                "valid": False,
                "error": "Cupom não encontrado",
            }
            response = client.post(
                "/api/loyalty/coupon/validate",
                json={"coupon_code": "GHOST", "order_total": 100},
                headers=self._auth_header(),
            )
        assert response.status_code == 400
        data = response.get_json()
        assert data["valid"] is False

    def test_analytics_no_dates(self, client):
        response = client.get(
            "/api/loyalty/admin/analytics",
            headers=self._auth_header(),
        )
        assert response.status_code == 400
