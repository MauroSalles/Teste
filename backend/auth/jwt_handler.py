"""JWT authentication utilities — access + refresh token lifecycle."""

import os
import logging
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import request, jsonify, g

logger = logging.getLogger(__name__)

_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production")
_ACCESS_TTL = int(os.environ.get("JWT_ACCESS_TTL_MINUTES", 60))
_REFRESH_TTL = int(os.environ.get("JWT_REFRESH_TTL_DAYS", 7))
_ALGORITHM = "HS256"

# In-memory token blacklist (works for single-instance deployments).
# For multi-instance / horizontal scaling, replace with a Redis-backed set.
# Example: use redis.Redis().sadd / sismember with key expiry matching token TTL.
_blacklist: set[str] = set()


def create_access_token(user_id: int, role: str = "user") -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TTL),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=_REFRESH_TTL),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])


def blacklist_token(token: str) -> None:
    _blacklist.add(token)


def is_blacklisted(token: str) -> bool:
    return token in _blacklist


def _extract_bearer() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def require_auth(f):
    """Decorator: enforce valid JWT access token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_bearer()
        if not token:
            return jsonify({"error": "Token de autenticação não fornecido."}), 401
        if is_blacklisted(token):
            return jsonify({"error": "Token inválido (logout efetuado)."}), 401
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return jsonify({"error": "Tipo de token inválido."}), 401
            g.user_id = payload["sub"]
            g.user_role = payload.get("role", "user")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido."}), 401
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """Decorator: enforce valid JWT access token with admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_bearer()
        if not token:
            return jsonify({"error": "Token de autenticação não fornecido."}), 401
        if is_blacklisted(token):
            return jsonify({"error": "Token inválido (logout efetuado)."}), 401
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return jsonify({"error": "Tipo de token inválido."}), 401
            if payload.get("role") != "admin":
                return jsonify({"error": "Acesso restrito a administradores."}), 403
            g.user_id = payload["sub"]
            g.user_role = "admin"
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido."}), 401
        return f(*args, **kwargs)
    return decorated
