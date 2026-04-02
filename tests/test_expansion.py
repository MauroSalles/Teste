"""Tests for the new expansion modules:
- Feature Flags
- i18n
- Tenant configuration
- API key handler
- Feature flag endpoint (/api/features)
- Onboarding endpoint (/api/onboarding)
- OpenAPI docs endpoint (/api/docs)
"""

import os
import pytest

from backend.feature_flags import is_enabled, all_flags, flag_descriptions
from backend.i18n import t, get_lang, SUPPORTED_LANGS
from backend.tenant import get_tenant_config


# ══════════════════════════════════════════════════════════════════════════════
# Feature Flags
# ══════════════════════════════════════════════════════════════════════════════

class TestFeatureFlags:
    def test_disabled_by_default(self):
        os.environ.pop("FEATURE_MARKETPLACE", None)
        assert is_enabled("MARKETPLACE") is False

    def test_enabled_with_1(self, monkeypatch):
        monkeypatch.setenv("FEATURE_MARKETPLACE", "1")
        assert is_enabled("MARKETPLACE") is True

    def test_enabled_with_true(self, monkeypatch):
        monkeypatch.setenv("FEATURE_PUBLIC_API", "true")
        assert is_enabled("PUBLIC_API") is True

    def test_enabled_with_yes(self, monkeypatch):
        monkeypatch.setenv("FEATURE_I18N", "yes")
        assert is_enabled("I18N") is True

    def test_case_insensitive_flag_name(self, monkeypatch):
        monkeypatch.setenv("FEATURE_MARKETPLACE", "1")
        assert is_enabled("marketplace") is True
        assert is_enabled("Marketplace") is True

    def test_all_flags_returns_dict(self):
        flags = all_flags()
        assert isinstance(flags, dict)
        assert "MARKETPLACE" in flags
        assert "FRANCHISE_PORTAL" in flags
        assert "PUBLIC_API" in flags
        assert "I18N" in flags
        assert "AB_TEST" in flags
        assert "SPIN_OFF" in flags

    def test_flag_descriptions_structure(self):
        desc = flag_descriptions()
        for flag, info in desc.items():
            assert "enabled" in info
            assert "description" in info
            assert isinstance(info["enabled"], bool)
            assert isinstance(info["description"], str)


# ══════════════════════════════════════════════════════════════════════════════
# Internationalization
# ══════════════════════════════════════════════════════════════════════════════

class TestI18n:
    def test_translate_known_key_pt(self):
        assert "não encontrado" in t("not_found", "pt").lower()

    def test_translate_known_key_en(self):
        assert "not found" in t("not_found", "en").lower()

    def test_translate_known_key_es(self):
        assert "encontrado" in t("not_found", "es").lower()

    def test_unknown_key_returns_key(self):
        assert t("this_key_does_not_exist", "pt") == "this_key_does_not_exist"

    def test_get_lang_from_header_pt(self):
        lang = get_lang("pt-BR,pt;q=0.9")
        assert lang == "pt"

    def test_get_lang_from_header_en(self):
        lang = get_lang("en-US,en;q=0.8")
        assert lang == "en"

    def test_get_lang_from_header_es(self):
        lang = get_lang("es-MX,es;q=0.9")
        assert lang == "es"

    def test_get_lang_unsupported_falls_back(self, monkeypatch):
        monkeypatch.setenv("DEFAULT_LANG", "pt")
        lang = get_lang("zh-CN,zh;q=0.9")
        assert lang in SUPPORTED_LANGS

    def test_get_lang_empty_falls_back(self, monkeypatch):
        monkeypatch.setenv("DEFAULT_LANG", "en")
        lang = get_lang("")
        assert lang == "en"

    def test_all_keys_have_pt_fallback(self):
        """Every message key must have a Portuguese translation."""
        from backend.i18n import _MESSAGES
        for key, translations in _MESSAGES.items():
            assert "pt" in translations, f"Key '{key}' missing 'pt' translation"


# ══════════════════════════════════════════════════════════════════════════════
# Tenant
# ══════════════════════════════════════════════════════════════════════════════

class TestTenant:
    def test_default_config(self, monkeypatch):
        monkeypatch.delenv("TENANT_ID", raising=False)
        monkeypatch.delenv("TENANT_NAME", raising=False)
        config = get_tenant_config()
        assert config["tenant_id"] == "gelateria_pro"
        assert config["tenant_name"] == "Gelateria Pro"
        assert config["currency"] == "BRL"

    def test_custom_tenant(self, monkeypatch):
        monkeypatch.setenv("TENANT_ID", "delivery_xyz")
        monkeypatch.setenv("TENANT_NAME", "Delivery XYZ")
        monkeypatch.setenv("TENANT_CURRENCY", "USD")
        config = get_tenant_config()
        assert config["tenant_id"] == "delivery_xyz"
        assert config["tenant_name"] == "Delivery XYZ"
        assert config["currency"] == "USD"

    def test_config_has_required_keys(self):
        config = get_tenant_config()
        for key in ("tenant_id", "tenant_name", "currency", "locale", "timezone"):
            assert key in config


# ══════════════════════════════════════════════════════════════════════════════
# API Key Handler
# ══════════════════════════════════════════════════════════════════════════════

class TestApiKeyHandler:
    def test_no_keys_configured_allows_all(self, client, monkeypatch):
        """When PARTNER_API_KEYS is empty, endpoint is open."""
        from backend.app import create_app
        from functools import wraps
        from flask import Blueprint, jsonify
        from backend.auth.api_key_handler import api_key_required

        monkeypatch.delenv("PARTNER_API_KEYS", raising=False)
        app = create_app()
        app.config["TESTING"] = True

        test_bp = Blueprint("_test_apikey", __name__)

        @test_bp.get("/_test/key-endpoint")
        @api_key_required
        def _key_endpoint():
            return jsonify({"ok": True})

        app.register_blueprint(test_bp)
        with app.test_client() as c:
            rv = c.get("/_test/key-endpoint")
            assert rv.status_code == 200

    def test_valid_key_accepted(self, monkeypatch):
        monkeypatch.setenv("PARTNER_API_KEYS", "secret123,another")
        from backend.app import create_app
        from flask import Blueprint, jsonify
        from backend.auth.api_key_handler import api_key_required

        app = create_app()
        app.config["TESTING"] = True
        test_bp = Blueprint("_test_apikey2", __name__)

        @test_bp.get("/_test/key-endpoint2")
        @api_key_required
        def _key_endpoint2():
            return jsonify({"ok": True})

        app.register_blueprint(test_bp)
        with app.test_client() as c:
            rv = c.get("/_test/key-endpoint2", headers={"X-API-Key": "secret123"})
            assert rv.status_code == 200

    def test_invalid_key_rejected(self, monkeypatch):
        monkeypatch.setenv("PARTNER_API_KEYS", "secret123")
        from backend.app import create_app
        from flask import Blueprint, jsonify
        from backend.auth.api_key_handler import api_key_required

        app = create_app()
        app.config["TESTING"] = True
        test_bp = Blueprint("_test_apikey3", __name__)

        @test_bp.get("/_test/key-endpoint3")
        @api_key_required
        def _key_endpoint3():
            return jsonify({"ok": True})

        app.register_blueprint(test_bp)
        with app.test_client() as c:
            rv = c.get("/_test/key-endpoint3", headers={"X-API-Key": "wrong"})
            assert rv.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# /api/features endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestFeaturesEndpoint:
    def test_list_features_returns_200(self, client):
        rv = client.get("/api/features")
        assert rv.status_code == 200

    def test_list_features_has_expected_keys(self, client):
        rv = client.get("/api/features")
        data = rv.get_json()
        assert "MARKETPLACE" in data
        assert "FRANCHISE_PORTAL" in data
        assert "PUBLIC_API" in data

    def test_feature_flag_structure(self, client):
        rv = client.get("/api/features")
        data = rv.get_json()
        for flag, info in data.items():
            assert "enabled" in info
            assert "description" in info

    def test_get_single_feature(self, client):
        rv = client.get("/api/features/MARKETPLACE")
        assert rv.status_code == 200
        data = rv.get_json()
        assert "MARKETPLACE" in data

    def test_get_unknown_feature(self, client):
        rv = client.get("/api/features/DOES_NOT_EXIST")
        assert rv.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# /api/onboarding endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestOnboardingEndpoint:
    def test_onboarding_returns_200(self, client):
        rv = client.get("/api/onboarding")
        assert rv.status_code == 200

    def test_onboarding_has_steps(self, client):
        rv = client.get("/api/onboarding")
        data = rv.get_json()
        assert "steps" in data
        assert len(data["steps"]) >= 5

    def test_onboarding_has_welcome(self, client):
        rv = client.get("/api/onboarding")
        data = rv.get_json()
        assert "welcome" in data
        assert len(data["welcome"]) > 0

    def test_onboarding_english(self, client):
        rv = client.get("/api/onboarding", headers={"Accept-Language": "en"})
        data = rv.get_json()
        assert data["language"] == "en"
        assert "Welcome" in data["welcome"]

    def test_onboarding_spanish(self, client):
        rv = client.get("/api/onboarding", headers={"Accept-Language": "es"})
        data = rv.get_json()
        assert data["language"] == "es"
        assert "Bienvenido" in data["welcome"]

    def test_onboarding_tenant_name(self, client):
        rv = client.get("/api/onboarding")
        data = rv.get_json()
        assert "tenant" in data


# ══════════════════════════════════════════════════════════════════════════════
# /api/docs (OpenAPI spec) endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestOpenAPIEndpoint:
    def test_docs_returns_200(self, client):
        rv = client.get("/api/docs")
        assert rv.status_code == 200

    def test_docs_is_openapi_3(self, client):
        rv = client.get("/api/docs")
        data = rv.get_json()
        assert data["openapi"].startswith("3.")

    def test_docs_has_paths(self, client):
        rv = client.get("/api/docs")
        data = rv.get_json()
        assert "paths" in data
        assert "/api/sabores" in data["paths"]
        assert "/api/pedidos" in data["paths"]

    def test_docs_has_components(self, client):
        rv = client.get("/api/docs")
        data = rv.get_json()
        assert "components" in data
        assert "securitySchemes" in data["components"]

    def test_docs_has_servers(self, client):
        rv = client.get("/api/docs")
        data = rv.get_json()
        assert "servers" in data
        assert len(data["servers"]) >= 1

    def test_docs_info_has_title(self, client):
        rv = client.get("/api/docs")
        data = rv.get_json()
        assert "info" in data
        assert "title" in data["info"]
