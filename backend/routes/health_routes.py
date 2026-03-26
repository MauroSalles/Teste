import time
from flask import Blueprint, jsonify
import psycopg2
from backend.database import get_pool

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Liveness + readiness probe: verifica conectividade com o banco."""
    db_status = "ok"
    db_latency_ms = None
    try:
        t0 = time.monotonic()
        pool = get_pool()
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        pool.putconn(conn)
        db_latency_ms = round((time.monotonic() - t0) * 1000, 2)
    except (psycopg2.Error, OSError) as exc:
        db_status = f"error: {exc}"

    overall = "ok" if db_status == "ok" else "degraded"
    payload = {
        "status": overall,
        "service": "gelateria-backend",
        "checks": {
            "database": db_status,
            **({"db_latency_ms": db_latency_ms} if db_latency_ms is not None else {}),
        },
    }
    http_status = 200 if overall == "ok" else 503
    return jsonify(payload), http_status
