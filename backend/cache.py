"""
Redis caching layer with graceful fallback.

If Redis is unavailable, all operations silently degrade to no-ops so the
application continues working without cache.
"""
import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

_redis_client = None
_redis_available: Optional[bool] = None  # None = not yet probed


def _get_client():
    """Return a Redis client, initialising it once. Returns None if unavailable."""
    global _redis_client, _redis_available
    if _redis_available is not None:
        return _redis_client if _redis_available else None

    redis_url = os.environ.get("REDIS_URL", "")
    if not redis_url:
        logger.info("REDIS_URL not set — running without cache.")
        _redis_available = False
        return None

    try:
        import redis as redis_lib  # noqa: PLC0415

        client = redis_lib.Redis.from_url(redis_url, socket_connect_timeout=2, decode_responses=True)
        client.ping()
        _redis_client = client
        _redis_available = True
        logger.info("Redis cache connected: %s", redis_url.split("@")[-1])
    except Exception as exc:
        logger.warning("Redis unavailable (%s) — cache disabled.", exc)
        _redis_available = False
    return _redis_client


def cache_get(key: str) -> Any:
    """Return the cached value for *key*, or None on cache-miss / unavailability."""
    client = _get_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw is not None else None
    except Exception as exc:
        logger.debug("cache_get(%s) error: %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Store *value* under *key* with a TTL in seconds. Returns True on success."""
    client = _get_client()
    if client is None:
        return False
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as exc:
        logger.debug("cache_set(%s) error: %s", key, exc)
        return False


def cache_delete(key: str) -> bool:
    """Delete a cached key. Returns True on success."""
    client = _get_client()
    if client is None:
        return False
    try:
        client.delete(key)
        return True
    except Exception as exc:
        logger.debug("cache_delete(%s) error: %s", key, exc)
        return False


def _reset_for_testing() -> None:
    """Reset cached probe state. For use in tests only."""
    global _redis_client, _redis_available
    _redis_available = None
    _redis_client = None


def cache_status() -> dict:
    """Return a dict describing the current Redis status for health checks."""
    redis_url = os.environ.get("REDIS_URL", "")
    if not redis_url:
        return {"status": "disabled", "reason": "REDIS_URL not configured"}

    client = _get_client()
    if client is None:
        return {"status": "error", "reason": "connection failed"}

    try:
        client.ping()
        info = client.info("server")
        return {
            "status": "ok",
            "version": info.get("redis_version", "unknown"),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
        }
    except Exception as exc:
        logger.warning("cache_status() probe error: %s", exc)
        return {"status": "error", "reason": "cache unreachable"}
