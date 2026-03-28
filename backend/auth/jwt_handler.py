import os
from functools import wraps

import jwt
from flask import request, jsonify

_JWT_SECRET = os.getenv('JWT_SECRET', 'changeme')
_JWT_ALGORITHM = 'HS256'


def token_required(f):
    """Decorator that validates a Bearer JWT token on protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(payload, *args, **kwargs)

    return decorated
