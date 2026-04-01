"""Loyalty routes blueprint — /api/loyalty/*"""

import logging

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

logger = logging.getLogger(__name__)

loyalty_bp = Blueprint("loyalty", __name__, url_prefix="/api/loyalty")


@loyalty_bp.get("/referral/<int:user_id>")
@token_required
def get_referral(current_user, user_id):
    from backend.loyalty.referral_service import get_or_create_referral_code
    try:
        code = get_or_create_referral_code(user_id)
        return jsonify(code), 200
    except Exception as exc:
        logger.error("get_referral error: %s", exc)
        return jsonify({"error": "Erro ao obter código de referral"}), 500


@loyalty_bp.post("/referral/<int:user_id>")
@token_required
def create_referral(current_user, user_id):
    from backend.loyalty.referral_service import get_or_create_referral_code
    try:
        code = get_or_create_referral_code(user_id)
        return jsonify(code), 201
    except Exception as exc:
        logger.error("create_referral error: %s", exc)
        return jsonify({"error": "Erro ao criar código de referral"}), 500


@loyalty_bp.post("/coupon/validate")
@token_required
def validate_coupon_endpoint(current_user):
    from backend.loyalty.coupon_service import validate_coupon
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    order_total = data.get("order_total")
    user_id = data.get("user_id", current_user["id"])

    if not code or order_total is None:
        return jsonify({"error": "code e order_total são obrigatórios"}), 400

    try:
        order_total = float(order_total)
    except (TypeError, ValueError):
        return jsonify({"error": "order_total inválido"}), 400

    result = validate_coupon(code, user_id, order_total)
    return jsonify(result), 200


@loyalty_bp.get("/points/<int:user_id>")
@token_required
def get_points(current_user, user_id):
    from backend.database import get_db
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT pontos, resgates FROM fidelidade WHERE user_id = %s",
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    return jsonify({"user_id": user_id, "pontos": 0, "resgates": 0}), 200
                return jsonify({"user_id": user_id, "pontos": row["pontos"], "resgates": row["resgates"]}), 200
    except Exception as exc:
        logger.error("get_points error: %s", exc)
        return jsonify({"error": "Erro ao obter pontos"}), 500
