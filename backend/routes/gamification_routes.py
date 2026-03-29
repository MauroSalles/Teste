from flask import Blueprint, request, jsonify

from backend.gamification.gamification_engine import GamificationEngine
from backend.gamification.leaderboard import LeaderboardSystem
from backend.ar.ar_system import ARExperienceSystem
from backend.auth.jwt_handler import token_required

gamification_bp = Blueprint("gamification", __name__, url_prefix="/api/gamification")

_gamif_engine = GamificationEngine()
_leaderboard = LeaderboardSystem()
_ar_system = ARExperienceSystem()


# ─────────────────────────────────────────────────────────
# AR endpoints
# ─────────────────────────────────────────────────────────

@gamification_bp.route("/ar/create", methods=["POST"])
@token_required
def create_ar_experience(current_user):
    """Create a 3D AR model for the chosen flavor."""
    data = request.get_json(force=True) or {}
    flavor_id = data.get("flavor_id")
    custom_toppings = data.get("custom_toppings", [])
    result = _ar_system.create_ar_experience(flavor_id, custom_toppings)
    return jsonify(result), 200


@gamification_bp.route("/ar/try-on", methods=["POST"])
@token_required
def try_multiple_flavors(current_user):
    """Try multiple flavors in AR."""
    data = request.get_json(force=True) or {}
    flavors = data.get("flavors", [])
    result = _ar_system.ar_try_on_multiple_flavors(current_user["id"], flavors)
    return jsonify(result), 200


# ─────────────────────────────────────────────────────────
# Badges
# ─────────────────────────────────────────────────────────

@gamification_bp.route("/badges", methods=["GET"])
@token_required
def get_user_badges(current_user):
    """List badges earned by the current user."""
    result = _gamif_engine.get_user_badges(current_user["id"])
    return jsonify(result), 200


# ─────────────────────────────────────────────────────────
# Level
# ─────────────────────────────────────────────────────────

@gamification_bp.route("/level", methods=["GET"])
@token_required
def get_user_level(current_user):
    """Return current level and XP progress."""
    result = _gamif_engine.update_user_level(current_user["id"])
    return jsonify(result), 200


# ─────────────────────────────────────────────────────────
# Daily challenges
# ─────────────────────────────────────────────────────────

@gamification_bp.route("/challenges/daily", methods=["GET"])
@token_required
def get_daily_challenges(current_user):
    """Return today's challenges for the current user."""
    result = _gamif_engine.generate_daily_challenges(current_user["id"])
    return jsonify(result), 200


# ─────────────────────────────────────────────────────────
# Spin the wheel
# ─────────────────────────────────────────────────────────

@gamification_bp.route("/spin", methods=["POST"])
@token_required
def spin_wheel(current_user):
    """Spin the daily reward wheel."""
    result = _gamif_engine.spin_reward_wheel(current_user["id"])
    return jsonify(result), 200


# ─────────────────────────────────────────────────────────
# Leaderboards (public)
# ─────────────────────────────────────────────────────────

@gamification_bp.route("/leaderboard/global", methods=["GET"])
def get_global_leaderboard():
    """Global all-time leaderboard (public)."""
    limit = request.args.get("limit", 100, type=int)
    result = _leaderboard.get_global_leaderboard(limit)
    return jsonify(result), 200


@gamification_bp.route("/leaderboard/weekly", methods=["GET"])
def get_weekly_leaderboard():
    """Weekly battle royale leaderboard (public)."""
    result = _leaderboard.get_weekly_leaderboard()
    return jsonify(result), 200


@gamification_bp.route("/leaderboard/my-rank", methods=["GET"])
@token_required
def get_my_rank(current_user):
    """Return the current user's rank in the global leaderboard."""
    result = _leaderboard.get_user_rank(current_user["id"])
    return jsonify(result), 200
