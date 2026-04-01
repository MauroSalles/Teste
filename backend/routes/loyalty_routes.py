import logging
from flask import Blueprint, request, jsonify

from backend.auth.jwt_handler import token_required
from backend.loyalty.referral_service import get_referral_stats, register_referral
from backend.loyalty.coupon_service import validate_coupon, apply_coupon

logger = logging.getLogger(__name__)

loyalty_bp = Blueprint("loyalty_bp", __name__, url_prefix="/api/loyalty")


@loyalty_bp.route("/referral/<int:user_id>", methods=["GET"])
@token_required
def referral_info(current_user, user_id):
    stats = get_referral_stats(user_id)
    return jsonify(stats)


@loyalty_bp.route("/referral/register", methods=["POST"])
@token_required
def referral_register(current_user):
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip().upper()
    if not code:
        return jsonify({"error": "code is required"}), 400
    try:
        result = register_referral(code, current_user["id"])
        return jsonify(result), 201
    except ValueError as exc:
        logger.warning("Referral code validation failed: %s", exc)
        return jsonify({"error": "Invalid referral code or operation not allowed"}), 400
    except Exception as exc:
        logger.error("referral_register error: %s", exc)
        return jsonify({"error": "Internal server error"}), 500


@loyalty_bp.route("/coupon/validate", methods=["POST"])
@token_required
def coupon_validate(current_user):
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip().upper()
    order_value = data.get("order_value", 0)
    if not code:
        return jsonify({"error": "code is required"}), 400
    result = validate_coupon(code, current_user["id"], float(order_value))
    return jsonify(result)


@loyalty_bp.route("/coupon/apply", methods=["POST"])
@token_required
def coupon_apply(current_user):
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip().upper()
    order_value = data.get("order_value", 0)
    if not code:
        return jsonify({"error": "code is required"}), 400
    try:
        result = apply_coupon(code, current_user["id"], float(order_value))
        status_code = 200 if result.get("valid") else 400
        return jsonify(result), status_code
    except Exception as exc:
        logger.error("coupon_apply error: %s", exc)
        return jsonify({"error": "Internal server error"}), 500
