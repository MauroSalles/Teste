from flask import Blueprint, jsonify

from backend.database import get_db

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    db_ok = False
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_ok = True
    except Exception:
        pass

    status = "ok" if db_ok else "degraded"
    code = 200 if db_ok else 503
    return jsonify({
        "status": status,
        "service": "gelateria-backend",
        "database": "ok" if db_ok else "unavailable",
    }), code
