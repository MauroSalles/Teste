from flask import Blueprint, jsonify, request

from backend.loyalty.referral_service import ReferralService

referral_bp = Blueprint("referral", __name__, url_prefix="/api/referral")
referral_service = ReferralService()


@referral_bp.route("/link/<int:user_id>", methods=["GET", "POST"])
def get_or_create_referral_link(user_id):
    """Gera ou retorna link de referência do usuário"""
    result = referral_service.create_referral_link(user_id, "", "")
    return jsonify(result), 200 if result["success"] else 400


@referral_bp.route("/dashboard/<int:user_id>", methods=["GET"])
def referral_dashboard(user_id):
    """Dashboard com estatísticas de referência"""
    result = referral_service.get_referral_dashboard(user_id)
    return jsonify(result), 200 if result["success"] else 400


@referral_bp.route("/register-referred", methods=["POST"])
def register_referred():
    """Registra usuário referido pelo código de referência"""
    data = request.get_json()
    if not data or "referral_code" not in data or "user_id" not in data:
        return jsonify({"success": False, "error": "Dados inválidos"}), 400
    result = referral_service.register_referred_user(
        data["referral_code"],
        data["user_id"],
        data.get("email", ""),
    )
    return jsonify(result), 200 if result["success"] else 400


@referral_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    """Leaderboard de top referrers do mês"""
    limit = request.args.get("limit", 10, type=int)
    result = referral_service.get_leaderboard(limit)
    return jsonify(result), 200 if result["success"] else 400


@referral_bp.route("/confirm-purchase/<int:user_id>", methods=["POST"])
def confirm_purchase(user_id):
    """Confirma primeira compra do usuário referido e credita rewards"""
    data = request.get_json()
    if not data or "order_total" not in data:
        return jsonify({"success": False, "error": "Dados inválidos"}), 400
    result = referral_service.confirm_referral_purchase(
        user_id,
        data["order_total"],
    )
    return jsonify(result), 200 if result["success"] else 400
