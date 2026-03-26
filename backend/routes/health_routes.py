import psycopg2
from flask import Blueprint, jsonify
from backend.database import get_pool

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    db_status = "ok"
    try:
        p = get_pool()
        conn = p.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        p.putconn(conn)
    except psycopg2.Error:
        db_status = "unavailable"

    status = "ok" if db_status == "ok" else "degraded"
    return jsonify({"status": status, "service": "gelateria-backend", "db": db_status})
