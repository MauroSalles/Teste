"""Feature Flags — runtime toggles driven by environment variables.

Convention: ``FEATURE_<NAME>=1`` (or ``true`` / ``yes``) enables the flag.

Usage::

    from backend.feature_flags import is_enabled

    if is_enabled("MARKETPLACE"):
        # marketplace-specific logic
        ...

Available flags (set via env vars):
    FEATURE_MARKETPLACE       – partner/marketplace module
    FEATURE_FRANCHISE_PORTAL  – franchise management portal
    FEATURE_PUBLIC_API        – public API key authentication
    FEATURE_I18N              – internationalization / Accept-Language
    FEATURE_AB_TEST           – A/B test variant assignment
    FEATURE_SPIN_OFF          – multi-tenant / white-label spin-off mode
"""

from __future__ import annotations

import os
from typing import Dict

# ---------------------------------------------------------------------------
# Internal registry
# ---------------------------------------------------------------------------

_KNOWN_FLAGS: Dict[str, str] = {
    "MARKETPLACE": "Partner/gelato marketplace module",
    "FRANCHISE_PORTAL": "Franchise management portal",
    "PUBLIC_API": "Public API key authentication",
    "I18N": "Internationalization (Accept-Language header)",
    "AB_TEST": "A/B test variant assignment",
    "SPIN_OFF": "Multi-tenant / white-label spin-off mode",
}

_TRUTHY = {"1", "true", "yes", "on"}


def is_enabled(flag: str) -> bool:
    """Return ``True`` if *flag* is enabled via ``FEATURE_<FLAG>`` env var."""
    env_key = f"FEATURE_{flag.upper()}"
    return os.environ.get(env_key, "").strip().lower() in _TRUTHY


def all_flags() -> Dict[str, bool]:
    """Return a dict of all known flags with their current state."""
    return {flag: is_enabled(flag) for flag in _KNOWN_FLAGS}


def flag_descriptions() -> Dict[str, Dict[str, object]]:
    """Return all flags with enabled state and description."""
    return {
        flag: {"enabled": is_enabled(flag), "description": desc}
        for flag, desc in _KNOWN_FLAGS.items()
    }
