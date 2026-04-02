"""Internationalization (i18n) helpers.

Supports Portuguese (pt), English (en), and Spanish (es).

Usage::

    from backend.i18n import t, get_lang

    lang = get_lang()          # detects from Accept-Language header
    msg  = t("not_found", lang)

Flask request context is optional — falls back to ``DEFAULT_LANG`` env var
(default ``"pt"``).
"""

from __future__ import annotations

import os
from typing import Dict

# ---------------------------------------------------------------------------
# Translation catalogue
# ---------------------------------------------------------------------------

_MESSAGES: Dict[str, Dict[str, str]] = {
    # ── Generic ─────────────────────────────────────────────────────────────
    "not_found": {
        "pt": "Recurso não encontrado",
        "en": "Resource not found",
        "es": "Recurso no encontrado",
    },
    "bad_request": {
        "pt": "Requisição inválida",
        "en": "Bad request",
        "es": "Solicitud incorrecta",
    },
    "unauthorized": {
        "pt": "Não autorizado",
        "en": "Unauthorized",
        "es": "No autorizado",
    },
    "forbidden": {
        "pt": "Acesso negado",
        "en": "Forbidden",
        "es": "Acceso denegado",
    },
    "internal_error": {
        "pt": "Erro interno do servidor",
        "en": "Internal server error",
        "es": "Error interno del servidor",
    },
    "success": {
        "pt": "Operação realizada com sucesso",
        "en": "Operation completed successfully",
        "es": "Operación completada con éxito",
    },
    # ── Sabores ─────────────────────────────────────────────────────────────
    "sabor_required": {
        "pt": "nome e preco são obrigatórios",
        "en": "name and price are required",
        "es": "nombre y precio son obligatorios",
    },
    "sabor_not_found": {
        "pt": "Sabor não encontrado",
        "en": "Flavor not found",
        "es": "Sabor no encontrado",
    },
    # ── Pedidos ─────────────────────────────────────────────────────────────
    "pedido_required": {
        "pt": "sabor_id e quantidade são obrigatórios",
        "en": "sabor_id and quantity are required",
        "es": "sabor_id y cantidad son obligatorios",
    },
    # ── Partners ────────────────────────────────────────────────────────────
    "partner_created": {
        "pt": "Parceiro cadastrado com sucesso",
        "en": "Partner registered successfully",
        "es": "Socio registrado con éxito",
    },
    "partner_not_found": {
        "pt": "Parceiro não encontrado",
        "en": "Partner not found",
        "es": "Socio no encontrado",
    },
    # ── Franchise ────────────────────────────────────────────────────────────
    "franchise_created": {
        "pt": "Franquia cadastrada com sucesso",
        "en": "Franchise registered successfully",
        "es": "Franquicia registrada con éxito",
    },
    "franchise_not_found": {
        "pt": "Franquia não encontrada",
        "en": "Franchise not found",
        "es": "Franquicia no encontrada",
    },
    # ── API Keys ─────────────────────────────────────────────────────────────
    "api_key_invalid": {
        "pt": "Chave de API inválida ou ausente",
        "en": "Invalid or missing API key",
        "es": "Clave de API inválida o ausente",
    },
    # ── Onboarding ───────────────────────────────────────────────────────────
    "onboarding_welcome": {
        "pt": "Bem-vindo à Gelateria Pro! Siga os passos abaixo para começar.",
        "en": "Welcome to Gelateria Pro! Follow the steps below to get started.",
        "es": "¡Bienvenido a Gelateria Pro! Siga los pasos a continuación para comenzar.",
    },
}

SUPPORTED_LANGS = ("pt", "en", "es")


def get_lang(accept_language: str | None = None) -> str:
    """Pick the best supported language from an ``Accept-Language`` header.

    Falls back to ``DEFAULT_LANG`` env var (default ``"pt"``).

    Args:
        accept_language: raw ``Accept-Language`` header value, or ``None``
            to read from the current Flask request context.
    """
    if accept_language is None:
        try:
            from flask import request as _req  # noqa: PLC0415
            accept_language = _req.headers.get("Accept-Language", "")
        except RuntimeError:
            # Outside request context
            accept_language = ""

    for part in accept_language.lower().replace("-", "_").split(","):
        lang = part.strip().split(";")[0].strip()[:2]
        if lang in SUPPORTED_LANGS:
            return lang

    default = os.environ.get("DEFAULT_LANG", "pt").strip().lower()
    return default if default in SUPPORTED_LANGS else "pt"


def t(key: str, lang: str | None = None) -> str:
    """Translate *key* to *lang* (auto-detected if ``None``).

    Returns the Portuguese fallback if the key or language is missing.
    """
    if lang is None:
        lang = get_lang()
    bucket = _MESSAGES.get(key, {})
    return bucket.get(lang) or bucket.get("pt") or key
