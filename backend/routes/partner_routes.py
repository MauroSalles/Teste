"""Partner, Marketplace & Franchise routes — /api/partners, /api/franchises.

These endpoints are only active when ``FEATURE_MARKETPLACE`` and
``FEATURE_FRANCHISE_PORTAL`` feature flags are enabled respectively.

Authentication: JWT (owner operations) or API key (partner operations).
"""

from __future__ import annotations

import secrets
from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required
from backend.database import get_db
from backend.feature_flags import is_enabled
from backend.i18n import get_lang, t

partner_bp = Blueprint("partners", __name__, url_prefix="/api")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _feature_check(flag: str):
    """Return a 404 response if *flag* is not enabled, else None."""
    if not is_enabled(flag):
        return jsonify({"error": "Feature not enabled"}), 404
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Partner endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@partner_bp.get("/partners")
@token_required
def list_partners(current_user):
    """List all registered partners."""
    err = _feature_check("MARKETPLACE")
    if err:
        return err
    lang = get_lang()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, plan, active, created_at FROM partners ORDER BY created_at DESC"
            )
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


@partner_bp.post("/partners")
@token_required
def create_partner(current_user):
    """Register a new partner and issue an API key."""
    err = _feature_check("MARKETPLACE")
    if err:
        return err
    lang = get_lang()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    plan = (data.get("plan") or "free").strip()

    if not name or not email:
        return jsonify({"error": t("bad_request", lang)}), 400

    api_key = "gp_" + secrets.token_urlsafe(32)
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO partners (name, email, api_key, plan)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, email, plan, active, api_key, created_at
                """,
                (name, email, api_key, plan),
            )
            partner = dict(cur.fetchone())
    return jsonify({**partner, "message": t("partner_created", lang)}), 201


@partner_bp.get("/partners/<int:partner_id>")
@token_required
def get_partner(current_user, partner_id: int):
    """Get a single partner by ID."""
    err = _feature_check("MARKETPLACE")
    if err:
        return err
    lang = get_lang()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, plan, active, created_at FROM partners WHERE id = %s",
                (partner_id,),
            )
            row = cur.fetchone()
    if not row:
        return jsonify({"error": t("partner_not_found", lang)}), 404
    return jsonify(dict(row))


@partner_bp.delete("/partners/<int:partner_id>")
@token_required
def deactivate_partner(current_user, partner_id: int):
    """Soft-deactivate a partner."""
    err = _feature_check("MARKETPLACE")
    if err:
        return err
    lang = get_lang()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE partners SET active = FALSE WHERE id = %s RETURNING id",
                (partner_id,),
            )
            row = cur.fetchone()
    if not row:
        return jsonify({"error": t("partner_not_found", lang)}), 404
    return jsonify({"id": partner_id, "active": False})


# ═══════════════════════════════════════════════════════════════════════════════
# Franchise endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@partner_bp.get("/franchises")
@token_required
def list_franchises(current_user):
    """List all franchise units."""
    err = _feature_check("FRANCHISE_PORTAL")
    if err:
        return err
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, owner_name, email, city, country, status, opened_at, created_at
                FROM franchises ORDER BY created_at DESC
                """
            )
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


@partner_bp.post("/franchises")
@token_required
def create_franchise(current_user):
    """Apply for a new franchise unit."""
    err = _feature_check("FRANCHISE_PORTAL")
    if err:
        return err
    lang = get_lang()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    owner_name = (data.get("owner_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    city = (data.get("city") or "").strip() or None
    country = (data.get("country") or "Brazil").strip()

    if not name or not owner_name or not email:
        return jsonify({"error": t("bad_request", lang)}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO franchises (name, owner_name, email, city, country)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, owner_name, email, city, country, status, created_at
                """,
                (name, owner_name, email, city, country),
            )
            franchise = dict(cur.fetchone())
    return jsonify({**franchise, "message": t("franchise_created", lang)}), 201


@partner_bp.get("/franchises/<int:franchise_id>")
@token_required
def get_franchise(current_user, franchise_id: int):
    """Get a single franchise unit by ID."""
    err = _feature_check("FRANCHISE_PORTAL")
    if err:
        return err
    lang = get_lang()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, owner_name, email, city, country, status, opened_at, created_at
                FROM franchises WHERE id = %s
                """,
                (franchise_id,),
            )
            row = cur.fetchone()
    if not row:
        return jsonify({"error": t("franchise_not_found", lang)}), 404
    return jsonify(dict(row))


@partner_bp.patch("/franchises/<int:franchise_id>/status")
@token_required
def update_franchise_status(current_user, franchise_id: int):
    """Update franchise status (pending → active → suspended)."""
    err = _feature_check("FRANCHISE_PORTAL")
    if err:
        return err
    lang = get_lang()
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip().lower()
    if status not in ("pending", "active", "suspended"):
        return jsonify({"error": t("bad_request", lang)}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE franchises SET status = %s WHERE id = %s RETURNING id, status",
                (status, franchise_id),
            )
            row = cur.fetchone()
    if not row:
        return jsonify({"error": t("franchise_not_found", lang)}), 404
    return jsonify(dict(row))
