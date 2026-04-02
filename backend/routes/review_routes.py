"""Customer review routes — /api/reviews/*"""

import logging

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required
import backend.models.review as review_model

review_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")
logger = logging.getLogger(__name__)


@review_bp.get("/sabor/<int:sabor_id>")
def listar_reviews(sabor_id: int):
    """List reviews for a given flavour (public)."""
    try:
        limit = max(1, min(int(request.args.get("limit", 20)), 100))
    except (TypeError, ValueError):
        limit = 20

    try:
        rows = review_model.listar_reviews_por_sabor(sabor_id, limit)
        media = review_model.media_rating_por_sabor(sabor_id)
        return jsonify(
            {
                "sabor_id": sabor_id,
                "media_rating": float(media["media"]) if media and media["media"] else None,
                "total_reviews": int(media["total"]) if media else 0,
                "reviews": [dict(r) for r in rows],
            }
        )
    except Exception as exc:
        logger.error("listar_reviews error: %s", exc)
        return jsonify({"error": "Erro ao buscar avaliações"}), 500


@review_bp.post("/")
@token_required
def criar_review(current_user):
    """Create a review for a flavour (authenticated)."""
    data = request.get_json(silent=True) or {}
    sabor_id = data.get("sabor_id")
    rating = data.get("rating")
    comentario = (data.get("comentario") or "").strip()

    if sabor_id is None or rating is None:
        return jsonify({"error": "sabor_id e rating são obrigatórios"}), 400

    try:
        sabor_id = int(sabor_id)
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({"error": "sabor_id e rating devem ser inteiros"}), 400

    if not 1 <= rating <= 5:
        return jsonify({"error": "rating deve ser entre 1 e 5"}), 400

    if not comentario:
        return jsonify({"error": "comentario é obrigatório"}), 400

    try:
        row = review_model.criar_review(current_user["id"], sabor_id, rating, comentario)
        return jsonify(dict(row)), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.error("criar_review error: %s", exc)
        return jsonify({"error": "Erro ao salvar avaliação"}), 500


@review_bp.get("/ranking")
def ranking_por_rating():
    """Flavours ranked by average customer rating (public)."""
    try:
        limit = max(1, min(int(request.args.get("limit", 10)), 50))
    except (TypeError, ValueError):
        limit = 10

    try:
        rows = review_model.ranking_sabores_por_rating(limit)
        return jsonify([dict(r) for r in rows])
    except Exception as exc:
        logger.error("ranking_por_rating error: %s", exc)
        return jsonify({"error": "Erro ao buscar ranking"}), 500
