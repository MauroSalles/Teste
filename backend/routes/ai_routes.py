"""AI routes blueprint — /api/ai/*"""

import logging

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.post("/chat")
def chat_endpoint():
    from backend.ai.chatbot_service import chat
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message é obrigatório"}), 400
    context = data.get("context")
    result = chat(message, context=context)
    return jsonify(result), 200


@ai_bp.get("/recommendations")
def recommendations_endpoint():
    from backend.ai.recommendation_engine import get_recommendations
    user_id = request.args.get("user_id")
    limit = min(int(request.args.get("limit", 5)), 20)
    try:
        recs = get_recommendations(user_id, limit=limit)
    except Exception as exc:
        logger.error("Recommendations error: %s", exc)
        recs = []
    return jsonify({"recommendations": recs}), 200


@ai_bp.post("/sentiment")
def sentiment_endpoint():
    from backend.ai.sentiment_service import analyze_sentiment
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text é obrigatório"}), 400
    result = analyze_sentiment(text)
    return jsonify(result), 200
