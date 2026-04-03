"""
/infra/healthz — Infrastructure health endpoint.

Reports the status of: database, cache (Redis), proxy (nginx), and frontend.
Returns HTTP 200 when all critical services are healthy; 503 when degraded.
"""
import logging
import os
import time
import urllib.request
import urllib.error

from flask import Blueprint, jsonify

from backend.database import get_db
from backend.cache import cache_status

infra_bp = Blueprint("infra", __name__)
logger = logging.getLogger(__name__)

_START_TIME = time.time()


def _check_database() -> dict:
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as exc:
        logger.warning("infra/healthz: DB check failed — %s", exc)
        return {"status": "error", "reason": "database unreachable"}


def _check_cache() -> dict:
    return cache_status()


def _check_proxy() -> dict:
    """Probe the nginx reverse proxy if PROXY_URL is configured."""
    proxy_url = os.environ.get("PROXY_URL", "")
    if not proxy_url:
        return {"status": "disabled", "reason": "PROXY_URL not configured"}
    try:
        req = urllib.request.urlopen(f"{proxy_url.rstrip('/')}/health", timeout=3)
        code = req.getcode()
        return {"status": "ok" if code == 200 else "degraded", "http_status": code}
    except urllib.error.URLError as exc:
        logger.warning("infra/healthz: proxy check failed — %s", exc)
        return {"status": "error", "reason": "proxy unreachable"}
    except Exception as exc:
        logger.warning("infra/healthz: proxy check unexpected error — %s", exc)
        return {"status": "error", "reason": "proxy check failed"}


def _check_frontend() -> dict:
    """Probe the frontend URL if FRONTEND_URL is configured."""
    frontend_url = os.environ.get("FRONTEND_URL", "")
    if not frontend_url:
        return {"status": "disabled", "reason": "FRONTEND_URL not configured"}
    try:
        req = urllib.request.urlopen(frontend_url.rstrip("/") + "/", timeout=3)
        code = req.getcode()
        return {"status": "ok" if code == 200 else "degraded", "http_status": code}
    except urllib.error.URLError as exc:
        logger.warning("infra/healthz: frontend check failed — %s", exc)
        return {"status": "error", "reason": "frontend unreachable"}
    except Exception as exc:
        logger.warning("infra/healthz: frontend check unexpected error — %s", exc)
        return {"status": "error", "reason": "frontend check failed"}


@infra_bp.route("/infra/healthz", methods=["GET"])
def infra_healthz():
    """
    Aggregated infrastructure health check.

    Checks:
      - database: PostgreSQL connectivity
      - cache:    Redis availability
      - proxy:    nginx reverse proxy (if PROXY_URL is set)
      - frontend: static frontend (if FRONTEND_URL is set)

    Returns 200 when all configured services report "ok".
    Returns 503 when any critical service (database) is degraded/erroring.
    """
    uptime_seconds = int(time.time() - _START_TIME)

    db_check = _check_database()
    cache_check = _check_cache()
    proxy_check = _check_proxy()
    frontend_check = _check_frontend()

    checks = {
        "database": db_check,
        "cache": cache_check,
        "proxy": proxy_check,
        "frontend": frontend_check,
    }

    # Overall status: degraded if any configured service is not "ok"
    critical_ok = db_check["status"] == "ok"
    all_ok = all(
        v["status"] in ("ok", "disabled")
        for v in checks.values()
    )
    overall = "ok" if all_ok else ("degraded" if critical_ok else "error")

    payload = {
        "status": overall,
        "service": "gelateria-backend",
        "uptime_seconds": uptime_seconds,
        "checks": checks,
    }

    http_status = 200 if critical_ok else 503
    return jsonify(payload), http_status
