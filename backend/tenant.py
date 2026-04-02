"""Tenant / white-label configuration.

Each deployment can represent a different tenant (a white-label gelateria brand,
a delivery spin-off, a different segment SaaS, etc.).

Configuration is driven purely by environment variables so the same Docker image
can serve multiple tenants with zero code changes.

Environment variables:
    TENANT_ID       – short slug, e.g. ``"gelateria_pro"`` / ``"delivery_abc"``
    TENANT_NAME     – human-readable name for this tenant
    TENANT_CURRENCY – ISO 4217 code (default ``"BRL"``)
    TENANT_LOCALE   – default locale, e.g. ``"pt_BR"`` / ``"en_US"``
    TENANT_TIMEZONE – e.g. ``"America/Sao_Paulo"``
    TENANT_LOGO_URL – URL to tenant logo (used in onboarding / email)
    TENANT_PRIMARY_COLOR – hex colour for white-label UI theming
"""

from __future__ import annotations

import os
from typing import Dict, Any


def get_tenant_config() -> Dict[str, Any]:
    """Return the current tenant configuration as a plain dict."""
    return {
        "tenant_id": os.environ.get("TENANT_ID", "gelateria_pro"),
        "tenant_name": os.environ.get("TENANT_NAME", "Gelateria Pro"),
        "currency": os.environ.get("TENANT_CURRENCY", "BRL"),
        "locale": os.environ.get("TENANT_LOCALE", "pt_BR"),
        "timezone": os.environ.get("TENANT_TIMEZONE", "America/Sao_Paulo"),
        "logo_url": os.environ.get("TENANT_LOGO_URL", ""),
        "primary_color": os.environ.get("TENANT_PRIMARY_COLOR", "#6C63FF"),
    }


TENANT = get_tenant_config()
