"""Shared Flask-Limiter instance — import and init_app in app.py to avoid circular imports."""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address, storage_uri="memory://")
