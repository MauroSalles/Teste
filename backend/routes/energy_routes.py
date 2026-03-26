"""
Energy-First Product Design — HTTP routes.

POST /energy/checkin   — record an energy event + upsert session profile
GET  /energy/profile   — retrieve current session profile
POST /energy/recommend — get a flavour recommendation based on energy context
"""

import datetime
import logging
import re

from flask import Blueprint, jsonify, request

from backend.models.energy import record_event, upsert_profile, get_profile
from backend.services.energy_service import recommend

logger = logging.getLogger(__name__)
energy_bp = Blueprint("energy", __name__, url_prefix="/energy")

_SESSION_RE = re.compile(r"^[a-zA-Z0-9_\-]{8,64}$")


def _validate_session(session_id) -> tuple[bool, str]:
    if not session_id or not isinstance(session_id, str):
        return False, "session_id obrigatório."
    if not _SESSION_RE.match(session_id):
        return False, "session_id inválido (8–64 caracteres alfanuméricos)."
    return True, ""


def _clamp(value, lo, hi, default=None):
    if value is None:
        return default
    try:
        v = int(value)
        return max(lo, min(hi, v))
    except (TypeError, ValueError):
        return default


# ── POST /energy/checkin ─────────────────────────────────────────────────────

@energy_bp.route("/checkin", methods=["POST"])
def checkin():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "")
    ok, err = _validate_session(session_id)
    if not ok:
        return jsonify({"error": err}), 400

    now = datetime.datetime.now()
    _days_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    event_data = {
        "energy_score":      _clamp(data.get("energy_score"), 0, 100, 50),
        "mood":              str(data.get("mood", ""))[:50] or None,
        "purpose":           str(data.get("purpose", ""))[:100] or None,
        "stress_level":      _clamp(data.get("stress_level"), 0, 100),
        "location_context":  str(data.get("location_context", ""))[:50] or None,
        "time_of_day":       now.strftime("%H:%M"),
        "day_of_week":       _days_pt[now.weekday()],
        "battery_level":     _clamp(data.get("battery_level"), 0, 100),
        "device_motion":     str(data.get("device_motion", ""))[:20] or None,
        "click_speed_ms":    _clamp(data.get("click_speed_ms"), 0, 60000),
        "scroll_pattern":    str(data.get("scroll_pattern", ""))[:20] or None,
        "typing_speed_cpm":  _clamp(data.get("typing_speed_cpm"), 0, 1000),
        "flavor_recommended": str(data.get("flavor_recommended", ""))[:100] or None,
    }

    try:
        event = record_event(session_id, event_data)
        upsert_profile(session_id, {
            "energy_score":       event_data["energy_score"],
            "mood":               event_data["mood"],
            "decision_speed_ms":  event_data["click_speed_ms"],
            "peak_energy_hour":   now.hour,
        })
    except Exception as exc:
        logger.error("checkin error: %s", exc)
        return jsonify({"error": "Erro interno ao registrar check-in."}), 500

    return jsonify({"ok": True, "event_id": event["id"] if event else None}), 201


# ── GET /energy/profile ──────────────────────────────────────────────────────

@energy_bp.route("/profile", methods=["GET"])
def profile():
    session_id = request.args.get("session_id", "")
    ok, err = _validate_session(session_id)
    if not ok:
        return jsonify({"error": err}), 400
    try:
        row = get_profile(session_id)
    except Exception as exc:
        logger.error("profile fetch error: %s", exc)
        return jsonify({"error": "Erro interno ao buscar perfil."}), 500
    if not row:
        return jsonify({"profile": None}), 200
    profile_data = dict(row)
    if "updated_at" in profile_data and profile_data["updated_at"]:
        profile_data["updated_at"] = profile_data["updated_at"].isoformat()
    return jsonify({"profile": profile_data}), 200


# ── POST /energy/recommend ───────────────────────────────────────────────────

@energy_bp.route("/recommend", methods=["POST"])
def get_recommendation():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "")
    ok, err = _validate_session(session_id)
    if not ok:
        return jsonify({"error": err}), 400

    energy_score = _clamp(data.get("energy_score"), 0, 100, 50)
    mood         = str(data.get("mood", ""))[:50] or None
    purpose      = str(data.get("purpose", ""))[:100] or None
    hour         = _clamp(data.get("hour"), 0, 23)

    try:
        result = recommend(session_id, energy_score, mood, purpose, hour)
    except Exception as exc:
        logger.error("recommend error: %s", exc)
        return jsonify({"error": "Erro interno na recomendação."}), 500

    return jsonify(result), 200
