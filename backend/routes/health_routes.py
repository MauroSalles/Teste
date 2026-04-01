import os
import time
from datetime import datetime, timezone

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

# Record the moment the process started so uptime can be calculated.
_START_TIME = time.monotonic()

APP_VERSION = "2.0.0"


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "gelateria-backend"})


@health_bp.route("/health/detailed", methods=["GET"])
def health_detailed():
    """Extended health check used by Render.com monitoring and the status page."""
    # Determine database status without importing psycopg2 — just check if env vars are present.
    # This reflects configuration state; actual connectivity depends on DB availability at runtime.
    db_status = "configured" if os.environ.get("DATABASE_URL") or os.environ.get("DB_HOST") else "not_configured"

    services = {
        "stripe":   "configured" if os.environ.get("STRIPE_SECRET_KEY") else "not_configured",
        "openai":   "configured" if os.environ.get("OPENAI_API_KEY") else "not_configured",
        "sendgrid": "configured" if os.environ.get("SENDGRID_API_KEY") else "not_configured",
        "socketio": "active",
    }

    uptime_seconds = int(time.monotonic() - _START_TIME)

    return jsonify({
        "status":         "healthy",
        "timestamp":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version":        APP_VERSION,
        "database":       db_status,
        "services":       services,
        "uptime_seconds": uptime_seconds,
    })
