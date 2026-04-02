"""API-key authentication for the public / partner-facing API.

Keys are stored as ``PARTNER_API_KEYS`` env var — a comma-separated list of
valid tokens.  In production, rotate these regularly or replace with DB-backed
key management.

Usage::

    from backend.auth.api_key_handler import api_key_required

    @api_bp.get("/public/...")
    @api_key_required
    def my_endpoint():
        ...

A client must send::

    X-API-Key: <key>

or the ``api_key`` query-string parameter.
"""

from __future__ import annotations

import functools
import os
from typing import Callable

from flask import jsonify, request


def _valid_keys() -> frozenset[str]:
    raw = os.environ.get("PARTNER_API_KEYS", "")
    return frozenset(k.strip() for k in raw.split(",") if k.strip())


def api_key_required(f: Callable) -> Callable:
    """Decorator: require a valid ``X-API-Key`` header (or ``api_key`` param)."""

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        key = (
            request.headers.get("X-API-Key")
            or request.args.get("api_key", "")
        ).strip()

        valid = _valid_keys()
        # If no keys are configured, the endpoint is open (dev / unconfigured)
        if valid and key not in valid:
            from backend.i18n import t  # noqa: PLC0415
            return jsonify({"error": t("api_key_invalid")}), 401

        return f(*args, **kwargs)

    return decorated
