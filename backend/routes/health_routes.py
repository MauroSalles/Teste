import os
import time
from datetime import datetime

from flask import Blueprint, jsonify

from backend.database import get_db

health_bp = Blueprint("health", __name__)

_START_TIME = time.time()
APP_VERSION = "2.0.0"


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "gelateria-backend"})


@health_bp.route("/health/detailed", methods=["GET"])
def health_detailed():
    db_status = "connected"
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    except Exception:
        db_status = "disconnected"

    return jsonify({
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": APP_VERSION,
        "database": db_status,
        "services": {
            "stripe": "configured" if os.getenv("STRIPE_SECRET_KEY") else "not_configured",
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
            "sendgrid": "configured" if os.getenv("SENDGRID_API_KEY") else "not_configured",
            "socketio": "active",
        },
        "uptime_seconds": round(time.time() - _START_TIME, 1),
    })
