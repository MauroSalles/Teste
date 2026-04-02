"""Feature-flag management routes — /api/features.

These endpoints expose which feature flags are enabled at runtime.
Setting flags is done via environment variables (``FEATURE_<NAME>=1``).
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from backend.feature_flags import flag_descriptions, is_enabled

features_bp = Blueprint("features", __name__, url_prefix="/api")


@features_bp.get("/features")
def list_features():
    """Return all feature flags and their current state.

    Response::

        {
          "MARKETPLACE":      {"enabled": false, "description": "..."},
          "FRANCHISE_PORTAL": {"enabled": false, "description": "..."},
          ...
        }
    """
    return jsonify(flag_descriptions())


@features_bp.get("/features/<string:flag>")
def get_feature(flag: str):
    """Return a single feature flag state."""
    flag = flag.upper()
    descriptions = flag_descriptions()
    if flag not in descriptions:
        return jsonify({"error": "Unknown feature flag"}), 404
    return jsonify({flag: descriptions[flag]})
