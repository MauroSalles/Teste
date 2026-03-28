import os
import logging
from functools import wraps

import jwt
from flask import request, jsonify

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")


def create_token(user_id, user_name, user_email):
    """Create a signed JWT for a user."""
    import time
    payload = {
        "id": user_id,
        "name": user_name,
        "email": user_email,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400,  # 24 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def token_required(f):
    """Decorator that validates the Bearer JWT and injects current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token ausente ou inválido"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        return f(payload, *args, **kwargs)
    return decorated
