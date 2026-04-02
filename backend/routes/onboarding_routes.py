"""Automated onboarding endpoint — /api/onboarding.

Returns a localised step-by-step guide for new users and external integrators,
including API examples and links to documentation.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.i18n import get_lang, t
from backend.feature_flags import all_flags
from backend.tenant import get_tenant_config

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/api")


@onboarding_bp.get("/onboarding")
def onboarding():
    """Return a structured onboarding guide for this tenant.

    Uses ``Accept-Language`` to localise step titles.
    """
    lang = get_lang()
    tenant = get_tenant_config()
    flags = all_flags()

    # ── Base steps (always present) ──────────────────────────────────────────
    steps = [
        {
            "step": 1,
            "title": {
                "pt": "Crie sua conta",
                "en": "Create your account",
                "es": "Crea tu cuenta",
            }[lang],
            "endpoint": "POST /api/auth/register",
            "body_example": {"name": "João", "email": "joao@exemplo.com", "password": "Senha@123"},
        },
        {
            "step": 2,
            "title": {
                "pt": "Faça login e obtenha seu token JWT",
                "en": "Log in and get your JWT token",
                "es": "Inicia sesión y obtén tu token JWT",
            }[lang],
            "endpoint": "POST /api/auth/login",
            "body_example": {"email": "joao@exemplo.com", "password": "Senha@123"},
        },
        {
            "step": 3,
            "title": {
                "pt": "Explore o cardápio de sabores",
                "en": "Explore the flavor menu",
                "es": "Explora el menú de sabores",
            }[lang],
            "endpoint": "GET /api/sabores",
            "auth": "Bearer <token>",
        },
        {
            "step": 4,
            "title": {
                "pt": "Faça seu primeiro pedido",
                "en": "Place your first order",
                "es": "Realiza tu primer pedido",
            }[lang],
            "endpoint": "POST /api/pedidos",
            "body_example": {"sabor_id": 1, "quantidade": 2},
            "auth": "Bearer <token>",
        },
        {
            "step": 5,
            "title": {
                "pt": "Acesse o dashboard administrativo",
                "en": "Access the admin dashboard",
                "es": "Accede al panel de administración",
            }[lang],
            "url": "/dashboard.html",
        },
    ]

    # ── Conditional steps based on enabled features ───────────────────────────
    if flags.get("PUBLIC_API"):
        steps.append({
            "step": len(steps) + 1,
            "title": {
                "pt": "Integre via API pública (chave de API)",
                "en": "Integrate via Public API (API key)",
                "es": "Integra via API pública (clave de API)",
            }[lang],
            "header": "X-API-Key: <your_api_key>",
            "docs": "GET /api/docs",
        })

    if flags.get("MARKETPLACE"):
        steps.append({
            "step": len(steps) + 1,
            "title": {
                "pt": "Cadastre-se como parceiro no marketplace",
                "en": "Register as a marketplace partner",
                "es": "Regístrate como socio en el marketplace",
            }[lang],
            "endpoint": "POST /api/partners",
        })

    if flags.get("FRANCHISE_PORTAL"):
        steps.append({
            "step": len(steps) + 1,
            "title": {
                "pt": "Solicite uma franquia",
                "en": "Apply for a franchise",
                "es": "Solicita una franquicia",
            }[lang],
            "endpoint": "POST /api/franchises",
        })

    return jsonify({
        "welcome": t("onboarding_welcome", lang),
        "tenant": tenant["tenant_name"],
        "language": lang,
        "enabled_features": [k for k, v in flags.items() if v],
        "steps": steps,
        "docs": "GET /api/docs",
        "health": "GET /health",
    })
