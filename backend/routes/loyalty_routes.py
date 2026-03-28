import logging
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify

from backend.auth.jwt_handler import token_required
from backend.loyalty.referral_service import ReferralService
from backend.loyalty.coupon_service import CouponService
from backend.loyalty.fraud_detection import FraudDetectionService

logger = logging.getLogger(__name__)

loyalty_bp = Blueprint("loyalty", __name__, url_prefix="/api/loyalty")

referral_service = ReferralService()
coupon_service = CouponService()
fraud_service = FraudDetectionService()


@loyalty_bp.route("/referral/code", methods=["GET"])
@token_required
def get_referral_code(current_user):
    """Get/create código de referência do usuário."""
    result = referral_service.create_referral_code(current_user["id"], current_user["name"])
    return jsonify(result), 200


@loyalty_bp.route("/referral/stats", methods=["GET"])
@token_required
def get_referral_stats(current_user):
    """Estatísticas de referências do usuário."""
    count = referral_service._get_referral_count(current_user["id"])
    tier = referral_service._get_referral_tier(count)
    coupons = coupon_service.get_user_active_coupons(current_user["id"])

    next_tier_in = max(0, 5 - count) if count < 5 else max(0, 10 - count)

    return jsonify({
        "referral_count": count,
        "current_tier": tier,
        "active_coupons": coupons["coupons"],
        "next_tier_in": next_tier_in,
    }), 200


@loyalty_bp.route("/coupon/validate", methods=["POST"])
@token_required
def validate_coupon(current_user):
    """Valida cupom ANTES do checkout."""
    data = request.get_json() or {}
    coupon_code = data.get("coupon_code")
    if not coupon_code:
        return jsonify({"valid": False, "error": "coupon_code obrigatório"}), 400
    try:
        order_total = Decimal(str(data.get("order_total", 0)))
    except (InvalidOperation, ValueError):
        return jsonify({"valid": False, "error": "order_total inválido"}), 400

    validation = coupon_service.validate_coupon(coupon_code, current_user["id"], order_total)
    status_code = 200 if validation.get("valid") else 400
    return jsonify(validation), status_code


@loyalty_bp.route("/coupon/apply", methods=["POST"])
@token_required
def apply_coupon(current_user):
    """Aplica cupom à ordem."""
    data = request.get_json() or {}
    coupon_code = data.get("coupon_code")
    order_id = data.get("order_id")
    if not coupon_code or not order_id:
        return jsonify({"success": False, "error": "coupon_code e order_id obrigatórios"}), 400
    try:
        order_total = Decimal(str(data.get("order_total", 0)))
    except (InvalidOperation, ValueError):
        return jsonify({"success": False, "error": "order_total inválido"}), 400

    fraud_check = fraud_service.check_suspicious_pattern(current_user["id"], coupon_code)
    if fraud_check.get("suspicious"):
        action = fraud_check.get("action")
        if action in ("block", "block_24h"):
            return jsonify({"success": False, "error": "Acesso bloqueado"}), 403

    result = coupon_service.apply_coupon(coupon_code, current_user["id"], order_id, order_total)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@loyalty_bp.route("/coupons/active", methods=["GET"])
@token_required
def get_active_coupons(current_user):
    """Lista cupons ativos do usuário."""
    return jsonify(coupon_service.get_user_active_coupons(current_user["id"])), 200


@loyalty_bp.route("/admin/analytics", methods=["GET"])
@token_required
def get_coupon_analytics(current_user):
    """Analytics de cupons para admin."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if not start_date or not end_date:
        return jsonify({"error": "start_date e end_date obrigatórios"}), 400
    analytics = fraud_service.get_coupon_analytics(start_date, end_date)
    return jsonify(analytics), 200
