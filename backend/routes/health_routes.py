import logging

from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    db_status = "ok"
    try:
        from backend.database import get_db
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
    except Exception as exc:
        logger.warning("Health check — DB unreachable: %s", exc)
        db_status = "unavailable"

    return jsonify({
        "status":   "ok" if db_status == "ok" else "degraded",
        "service":  "gelateria-backend",
        "database": db_status,
    })
