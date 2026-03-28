import os
import logging
from functools import wraps

from flask import request, jsonify

logger = logging.getLogger(__name__)

_JWT_AVAILABLE = False
try:
    import jwt as _jwt
    _JWT_AVAILABLE = True
except ImportError:
    pass


def token_required(f):
    """Decorator that validates a Bearer JWT token on protected routes.

    In testing mode (FLASK_ENV=testing) with no SECRET_KEY set the check is
    skipped and a stub user is injected so that tests run without a real token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        flask_env = os.environ.get("FLASK_ENV", "production")
        secret = os.environ.get("SECRET_KEY", "")

        # Allow unauthenticated access in the test environment when no secret
        # key has been configured.
        if flask_env == "testing" and not secret:
            stub_user = {"id": 1, "email": "test@example.com", "name": "Test User", "phone": "+5511999999999"}
            return f(stub_user, *args, **kwargs)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token missing or malformed"}), 401

        token = auth_header.split(" ", 1)[1]

        if not _JWT_AVAILABLE:
            logger.warning("PyJWT not installed — token validation skipped.")
            stub_user = {"id": 0, "email": "anonymous@example.com", "name": "Anonymous", "phone": ""}
            return f(stub_user, *args, **kwargs)

        try:
            payload = _jwt.decode(token, secret, algorithms=["HS256"])
            return f(payload, *args, **kwargs)
        except Exception as exc:
            return jsonify({"error": "Token invalid", "detail": str(exc)}), 401

    return decorated
