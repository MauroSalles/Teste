import os
import logging
import datetime
from functools import wraps

import jwt
from flask import request, jsonify

logger = logging.getLogger(__name__)

_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production-32chars!!")
_ALGORITHM = "HS256"

if len(_SECRET_KEY) < 32:
    logger.warning(
        "JWT_SECRET_KEY is shorter than 32 characters (%d bytes). "
        "Set a strong random secret via the JWT_SECRET_KEY environment variable.",
        len(_SECRET_KEY),
    )


def token_required(f):
    """Decorator that validates a Bearer JWT token and injects current_user."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid JWT token: %s", e)
            return jsonify({"error": "Invalid token"}), 401

        current_user = {"id": int(payload.get("sub")), "email": payload.get("email")}
        return f(current_user, *args, **kwargs)

    return decorated


def generate_token(user_id, email):
    """Generate a JWT token for the given user (utility for testing / login endpoint)."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)
