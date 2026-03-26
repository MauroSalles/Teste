import logging
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)
logger = logging.getLogger(__name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    db_status = "ok"
    try:
        from backend.database import get_db
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as exc:
        logger.warning("Health check — DB unreachable: %s", exc)
        db_status = "unavailable"

    status = "ok" if db_status == "ok" else "degraded"
    code = 200 if status == "ok" else 503
    return jsonify({"status": status, "service": "gelateria-backend", "db": db_status}), code
