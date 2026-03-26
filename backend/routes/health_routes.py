import os
from datetime import datetime, timezone

import redis as redis_lib
from flask import Blueprint, jsonify

from backend.database import get_db

health_bp = Blueprint("health", __name__)


def _redis_client():
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        return None
    return redis_lib.from_url(redis_url, socket_connect_timeout=3)


@health_bp.route("/health", methods=["GET"])
def health_check():
    db_status = "unavailable"
    cache_status = "unavailable"
    http_status = 200

    # Check database
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        http_status = 503

    # Check Redis (optional — skip if REDIS_URL not configured)
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            client = _redis_client()
            if client:
                client.ping()
                cache_status = "connected"
        except Exception:
            http_status = 503
    else:
        cache_status = "not_configured"

    payload = {
        "status": "healthy" if http_status == 200 else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "cache": cache_status,
        "version": os.environ.get("RELEASE_VERSION", "1.0.0"),
    }

    if http_status != 200:
        return jsonify(payload), 503

    return jsonify(payload), 200

