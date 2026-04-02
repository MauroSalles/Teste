import os
import time
import logging

from flask import Blueprint, jsonify

from backend.database import get_db
from backend.auth.jwt_handler import _SECRET_KEY as _JWT_SECRET_KEY

health_bp = Blueprint("health", __name__)
logger = logging.getLogger(__name__)

_START_TIME = time.time()


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "gelateria-backend"})


@health_bp.route("/health/detailed", methods=["GET"])
def health_detailed():
    """Detailed health check — reports DB connectivity and uptime."""
    uptime_seconds = int(time.time() - _START_TIME)

    db_status = "ok"
    db_error = None
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as exc:
        db_status = "error"
        db_error = str(exc)
        logger.warning("Health check: DB unreachable — %s", exc)

    jwt_status = "ok" if len(_JWT_SECRET_KEY) >= 32 else "weak"

    overall = "ok" if db_status == "ok" else "degraded"

    payload = {
        "status": overall,
        "service": "gelateria-backend",
        "uptime_seconds": uptime_seconds,
        "checks": {
            "database": {"status": db_status},
            "jwt_secret": {"status": jwt_status},
        },
    }
    if db_error:
        payload["checks"]["database"]["error"] = db_error

    http_status = 200 if overall == "ok" else 503
    return jsonify(payload), http_status
