"""OpenAPI 3.0 specification endpoint — GET /api/docs.

Serves a machine-readable OpenAPI 3.0 JSON document that describes all
public endpoints of the Gelateria Pro API.

External integrators can import this into Postman, Insomnia, or any other
API client to start using the public API immediately.
"""

from __future__ import annotations

import os
from flask import Blueprint, jsonify

from backend.tenant import get_tenant_config

openapi_bp = Blueprint("openapi", __name__, url_prefix="/api")


def _build_spec() -> dict:
    tenant = get_tenant_config()
    version = os.environ.get("APP_VERSION", "1.0.0")
    base_url = os.environ.get("BASE_URL", "https://gelateria-backend.onrender.com")

    return {
        "openapi": "3.0.3",
        "info": {
            "title": f"{tenant['tenant_name']} API",
            "version": version,
            "description": (
                "REST API pública da Gelateria Pro. "
                "Autenticação via JWT (Bearer) ou X-API-Key para parceiros."
            ),
            "contact": {
                "email": "api@gelateria.pro",
            },
            "license": {"name": "MIT"},
        },
        "servers": [
            {"url": base_url, "description": "Production"},
            {"url": "http://localhost:5000", "description": "Local development"},
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
                "apiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                },
            },
            "schemas": {
                "Sabor": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nome": {"type": "string"},
                        "preco": {"type": "number", "format": "float"},
                    },
                },
                "Pedido": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "sabor_id": {"type": "integer"},
                        "quantidade": {"type": "integer"},
                        "data": {"type": "string", "format": "date-time"},
                    },
                },
                "Partner": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "plan": {"type": "string", "enum": ["free", "starter", "pro"]},
                        "active": {"type": "boolean"},
                        "api_key": {"type": "string"},
                    },
                },
                "Franchise": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "owner_name": {"type": "string"},
                        "email": {"type": "string"},
                        "city": {"type": "string"},
                        "country": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "active", "suspended"]},
                    },
                },
                "Error": {
                    "type": "object",
                    "properties": {"error": {"type": "string"}},
                },
            },
        },
        "paths": {
            # ── Health ────────────────────────────────────────────────────────
            "/health": {
                "get": {
                    "summary": "Basic health check",
                    "tags": ["Infrastructure"],
                    "responses": {
                        "200": {"description": "Service is healthy"}
                    },
                }
            },
            "/health/detailed": {
                "get": {
                    "summary": "Detailed health check (DB + uptime)",
                    "tags": ["Infrastructure"],
                    "responses": {"200": {"description": "Detailed status"}},
                }
            },
            # ── Auth ──────────────────────────────────────────────────────────
            "/api/auth/register": {
                "post": {
                    "summary": "Register a new user",
                    "tags": ["Auth"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name", "email", "password"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 8},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "User created"},
                        "400": {"description": "Validation error"},
                        "409": {"description": "Email already registered"},
                    },
                }
            },
            "/api/auth/login": {
                "post": {
                    "summary": "Login and receive JWT",
                    "tags": ["Auth"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email", "password"],
                                    "properties": {
                                        "email": {"type": "string"},
                                        "password": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "JWT token returned"},
                        "401": {"description": "Invalid credentials"},
                    },
                }
            },
            # ── Sabores ───────────────────────────────────────────────────────
            "/api/sabores": {
                "get": {
                    "summary": "List all flavors",
                    "tags": ["Sabores"],
                    "responses": {
                        "200": {
                            "description": "List of flavors",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Sabor"},
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create a new flavor",
                    "tags": ["Sabores"],
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["nome", "preco"],
                                    "properties": {
                                        "nome": {"type": "string"},
                                        "preco": {"type": "number"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Flavor created"},
                        "400": {"description": "Validation error"},
                    },
                },
            },
            # ── Pedidos ───────────────────────────────────────────────────────
            "/api/pedidos": {
                "get": {
                    "summary": "List all orders",
                    "tags": ["Pedidos"],
                    "responses": {"200": {"description": "List of orders"}},
                },
                "post": {
                    "summary": "Place a new order",
                    "tags": ["Pedidos"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["sabor_id", "quantidade"],
                                    "properties": {
                                        "sabor_id": {"type": "integer"},
                                        "quantidade": {"type": "integer", "minimum": 1},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Order placed"},
                        "400": {"description": "Validation error"},
                    },
                },
            },
            # ── Feature Flags ─────────────────────────────────────────────────
            "/api/features": {
                "get": {
                    "summary": "List all feature flags and their state",
                    "tags": ["Platform"],
                    "responses": {"200": {"description": "Feature flags map"}},
                }
            },
            # ── Onboarding ────────────────────────────────────────────────────
            "/api/onboarding": {
                "get": {
                    "summary": "Automated onboarding guide (i18n)",
                    "tags": ["Platform"],
                    "parameters": [
                        {
                            "name": "Accept-Language",
                            "in": "header",
                            "schema": {"type": "string", "example": "en"},
                            "description": "Preferred language (pt, en, es)",
                        }
                    ],
                    "responses": {"200": {"description": "Step-by-step onboarding"}},
                }
            },
            # ── Partners ──────────────────────────────────────────────────────
            "/api/partners": {
                "get": {
                    "summary": "List partners (FEATURE_MARKETPLACE)",
                    "tags": ["Marketplace"],
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "Partner list"}},
                },
                "post": {
                    "summary": "Register a new partner",
                    "tags": ["Marketplace"],
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name", "email"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string"},
                                        "plan": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "Partner created with API key"}},
                },
            },
            # ── Franchises ────────────────────────────────────────────────────
            "/api/franchises": {
                "get": {
                    "summary": "List franchise units (FEATURE_FRANCHISE_PORTAL)",
                    "tags": ["Franchise"],
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "Franchise list"}},
                },
                "post": {
                    "summary": "Apply for a new franchise",
                    "tags": ["Franchise"],
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name", "owner_name", "email"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "owner_name": {"type": "string"},
                                        "email": {"type": "string"},
                                        "city": {"type": "string"},
                                        "country": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "Franchise application submitted"}},
                },
            },
        },
    }


@openapi_bp.get("/docs")
def openapi_spec():
    """Serve OpenAPI 3.0 JSON specification."""
    return jsonify(_build_spec())
