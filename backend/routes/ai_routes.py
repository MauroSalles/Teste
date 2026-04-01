import logging
from flask import Blueprint, request, jsonify

from backend.ai.chatbot_service import get_bot_response
from backend.ai.recommendation_engine import get_recommendations
from backend.ai.sentiment_service import analyze_sentiment

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai_bp", __name__, url_prefix="/api/ai")


@ai_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400
    user_id = data.get("user_id")
    result = get_bot_response(message, user_id=user_id)
    return jsonify(result)


@ai_bp.route("/recommendations", methods=["GET"])
def recommendations():
    user_id = request.args.get("user_id", type=int)
    limit = request.args.get("limit", default=3, type=int)
    flavors = get_recommendations(user_id=user_id, limit=limit)
    return jsonify({"recommendations": flavors})


@ai_bp.route("/sentiment", methods=["POST"])
def sentiment():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text is required"}), 400
    result = analyze_sentiment(text)
    return jsonify(result)
