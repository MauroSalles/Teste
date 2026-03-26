import os
import logging
from functools import wraps

import jwt
from flask import request, jsonify

logger = logging.getLogger(__name__)

_DEFAULT_SECRET = "change-me-in-production"
JWT_SECRET = os.environ.get("JWT_SECRET", _DEFAULT_SECRET)
JWT_ALGORITHM = "HS256"

if JWT_SECRET == _DEFAULT_SECRET and os.environ.get("FLASK_ENV") not in ("testing", "development"):
    logger.warning(
        "JWT_SECRET is set to the default value. "
        "Set a strong secret via the JWT_SECRET environment variable before going to production."
    )


def token_required(f):
    """Decorator that validates a JWT Bearer token and injects current_user."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token missing or invalid"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as exc:
            logger.debug("Invalid JWT: %s", exc)
            return jsonify({"error": "Invalid token"}), 401

        return f(payload, *args, **kwargs)

    return decorated
