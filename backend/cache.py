"""Simple in-memory TTL cache with optional Redis backend.

Usage:
    from backend.cache import cache

    @cache(ttl=60)
    def expensive_query():
        ...
"""

import hashlib
import json
import logging
import os
import threading
import time
from functools import wraps
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Optional Redis backend ─────────────────────────────────────────────────

_redis_client = None
_REDIS_URL = os.environ.get("REDIS_URL", "")

if _REDIS_URL:
    try:
        import redis  # type: ignore

        _redis_client = redis.from_url(_REDIS_URL, decode_responses=True, socket_timeout=1)
        _redis_client.ping()
        logger.info("Cache: Redis connected at %s", _REDIS_URL)
    except Exception as exc:  # pragma: no cover
        logger.warning("Cache: Redis unavailable (%s), falling back to in-memory.", exc)
        _redis_client = None

# ── In-memory fallback ─────────────────────────────────────────────────────

_store: dict[str, tuple[Any, float]] = {}
_store_lock = threading.Lock()


def _mem_get(key: str, ttl: int) -> Optional[Any]:
    with _store_lock:
        entry = _store.get(key)
        if entry is None:
            return None
        value, ts = entry
        if time.time() - ts > ttl:
            del _store[key]
            return None
        return value


def _mem_set(key: str, value: Any) -> None:
    with _store_lock:
        _store[key] = (value, time.time())


def _evict_expired() -> int:
    """Remove expired keys from the in-memory store. Returns count removed."""
    now = time.time()
    with _store_lock:
        expired = [k for k, (_, ts) in _store.items() if now - ts > 3600]
        for k in expired:
            del _store[k]
    return len(expired)


# ── Public API ─────────────────────────────────────────────────────────────

def get(key: str, ttl: int = 60) -> Optional[Any]:
    """Return cached value for *key* or None if missing/expired."""
    if _redis_client:
        try:
            raw = _redis_client.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.debug("Cache get error (Redis): %s", exc)
    return _mem_get(key, ttl)


def set(key: str, value: Any, ttl: int = 60) -> None:  # noqa: A001
    """Store *value* under *key* with the given TTL (seconds)."""
    if _redis_client:
        try:
            _redis_client.setex(key, ttl, json.dumps(value))
            return
        except Exception as exc:
            logger.debug("Cache set error (Redis): %s", exc)
    _mem_set(key, value)


def delete(key: str) -> None:
    """Invalidate a cache entry."""
    if _redis_client:
        try:
            _redis_client.delete(key)
        except Exception as exc:
            logger.debug("Cache delete error (Redis): %s", exc)
    with _store_lock:
        _store.pop(key, None)


def flush_all() -> None:
    """Clear the entire cache (in-memory only; does NOT flush Redis)."""
    with _store_lock:
        _store.clear()


def cache(ttl: int = 60, key_prefix: str = ""):
    """Decorator: cache function return value for *ttl* seconds.

    The cache key is derived from the function name + serialised args/kwargs.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            raw_key = json.dumps(
                {"fn": fn.__qualname__, "args": args, "kwargs": kwargs},
                default=str,
                sort_keys=True,
            )
            cache_key = (key_prefix or "cache") + ":" + hashlib.md5(
                raw_key.encode()
            ).hexdigest()

            cached = get(cache_key, ttl)
            if cached is not None:
                return cached

            result = fn(*args, **kwargs)
            set(cache_key, result, ttl)
            return result

        wrapper.cache_key_prefix = key_prefix or fn.__qualname__
        return wrapper

    return decorator


def info() -> dict:
    """Return cache backend info (for health/diagnostics)."""
    if _redis_client:
        try:
            info_data = _redis_client.info("memory")
            return {
                "backend": "redis",
                "used_memory_human": info_data.get("used_memory_human", "?"),
                "connected": True,
            }
        except Exception:
            pass
    _evict_expired()
    with _store_lock:
        return {"backend": "memory", "entries": len(_store), "connected": True}
