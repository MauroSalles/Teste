import os
import time
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

_START_TIME = time.time()


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "gelateria-backend"})


@health_bp.route("/health/detailed", methods=["GET"])
def health_detailed():
    """Extended health check with per-component status and uptime."""
    uptime_seconds = int(time.time() - _START_TIME)

    components = {}

    # Database probe
    try:
        from backend.database import get_db
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        components["database"] = {"status": "ok"}
    except Exception as exc:
        components["database"] = {"status": "error", "detail": str(exc)}

    # Optional integrations — report configured / not_configured
    components["stripe"] = {
        "status": "configured" if os.environ.get("STRIPE_SECRET_KEY") else "not_configured"
    }
    components["openai"] = {
        "status": "configured" if os.environ.get("OPENAI_API_KEY") else "not_configured"
    }
    components["sendgrid"] = {
        "status": "configured" if os.environ.get("SENDGRID_API_KEY") else "not_configured"
    }

    overall = "ok" if components["database"]["status"] == "ok" else "degraded"

    return jsonify({
        "status": overall,
        "service": "gelateria-backend",
        "uptime_seconds": uptime_seconds,
        "components": components,
    })

