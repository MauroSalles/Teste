import os
import time
from datetime import datetime, timezone

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

_START_TIME = time.monotonic()
_VERSION = "1.1.0"


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "gelateria-backend"})


def _check_database() -> str:
    """Return 'ok', 'error', or 'not_configured' for the DB health check."""
    if not os.environ.get("DATABASE_URL") and not os.environ.get("DB_HOST"):
        return "not_configured"
    try:
        from backend.database import get_db
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return "ok"
    except Exception:
        return "error"


@health_bp.route("/health/detailed", methods=["GET"])
def health_detailed():
    uptime_seconds = int(time.monotonic() - _START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    db_status = _check_database()
    overall = "ok" if db_status in ("ok", "not_configured") else "degraded"
    return jsonify({
        "status": overall,
        "service": "gelateria-backend",
        "version": _VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": {
            "seconds": uptime_seconds,
            "human": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        },
        "checks": {
            "api": "ok",
            "database": db_status,
        },
    })
