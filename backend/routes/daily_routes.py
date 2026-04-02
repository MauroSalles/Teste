"""Daily ritual blueprint — /api/daily/*

Implements the "Sabor do Dia" feature:
  - deterministic daily flavor (MD5 of today's date)
  - daily check-in with streak tracking (+10 points)
  - mood (humor) logging
  - admin dashboard: today's average mood
"""

import hashlib
import logging
from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

try:
    from backend.database import get_db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

logger = logging.getLogger(__name__)

daily_bp = Blueprint("daily", __name__, url_prefix="/api/daily")

# Fallback flavor list when DB is unavailable
_SABORES_FALLBACK = [
    {"id": 1, "nome": "Chocolate", "preco": 10.00},
    {"id": 2, "nome": "Morango", "preco": 9.50},
    {"id": 3, "nome": "Baunilha", "preco": 8.00},
    {"id": 4, "nome": "Pistache", "preco": 12.00},
    {"id": 5, "nome": "Limão", "preco": 9.00},
]


def _sabor_do_dia_index(flavors_count: int) -> int:
    """Deterministic daily index using MD5 of today's date."""
    digest = hashlib.md5(str(date.today()).encode()).hexdigest()
    return int(digest, 16) % flavors_count


def _get_sabor_do_dia():
    """Return the featured flavor of the day."""
    try:
        if _DB_AVAILABLE:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, nome, preco FROM sabores ORDER BY id")
                    rows = cur.fetchall()
            sabores = [dict(r) for r in rows]
    except Exception as e:
        logger.warning("DB unavailable for sabor do dia, using fallback: %s", e)
        sabores = _SABORES_FALLBACK

    if not sabores:
        sabores = _SABORES_FALLBACK

    idx = _sabor_do_dia_index(len(sabores))
    sabor = sabores[idx]
    return {
        "id": sabor["id"],
        "nome": sabor["nome"],
        "preco": float(sabor["preco"]),
        "preco_com_desconto": round(float(sabor["preco"]) * 0.9, 2),
        "desconto_percent": 10,
        "data": str(date.today()),
    }


# ── Sabor do Dia ──────────────────────────────────────────────────────────────

@daily_bp.get("/sabor")
def sabor_do_dia():
    """Return today's featured flavor (rotates at midnight)."""
    return jsonify(_get_sabor_do_dia())


# ── Check-in ──────────────────────────────────────────────────────────────────

@daily_bp.post("/checkin")
@token_required
def daily_checkin(current_user):
    """Register a daily check-in (+10 points, streak counter)."""
    user_id = current_user["id"]
    today = date.today()

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Verify if already checked in today
                cur.execute(
                    "SELECT id, streak_atual FROM daily_checkins WHERE user_id=%s AND data=%s",
                    (user_id, today),
                )
                existing = cur.fetchone()
                if existing:
                    return jsonify({
                        "message": "Check-in já realizado hoje",
                        "streak": existing["streak_atual"],
                        "pontos_ganhos": 0,
                    }), 200

                # Calculate streak
                yesterday = today - timedelta(days=1)
                cur.execute(
                    "SELECT streak_atual FROM daily_checkins WHERE user_id=%s AND data=%s",
                    (user_id, yesterday),
                )
                prev = cur.fetchone()
                streak = (prev["streak_atual"] + 1) if prev else 1

                cur.execute(
                    """INSERT INTO daily_checkins (user_id, data, streak_atual)
                       VALUES (%s, %s, %s)""",
                    (user_id, today, streak),
                )

                # Add 10 loyalty points
                cur.execute(
                    """INSERT INTO fidelidade (user_id, pontos)
                       VALUES (%s, 10)
                       ON CONFLICT (user_id)
                       DO UPDATE SET pontos = fidelidade.pontos + 10,
                                     updated_at = CURRENT_TIMESTAMP""",
                    (user_id,),
                )

        return jsonify({
            "message": "Check-in realizado!",
            "streak": streak,
            "pontos_ganhos": 10,
            "sabor_do_dia": _get_sabor_do_dia(),
        }), 201

    except Exception as e:
        logger.error("Checkin error: %s", e)
        return jsonify({"error": "Erro no check-in", "streak": 1, "pontos_ganhos": 0}), 500


# ── Streak ────────────────────────────────────────────────────────────────────

@daily_bp.get("/streak/<int:user_id>")
def get_streak(user_id):
    """Return the current consecutive check-in streak for a user."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT streak_atual FROM daily_checkins
                       WHERE user_id=%s ORDER BY data DESC LIMIT 1""",
                    (user_id,),
                )
                row = cur.fetchone()
        streak = row["streak_atual"] if row else 0
    except Exception as e:
        logger.warning("Streak DB error: %s", e)
        streak = 0

    return jsonify({"user_id": user_id, "streak": streak})


# ── Calendário (últimos 30 dias) ──────────────────────────────────────────────

@daily_bp.get("/calendario")
@token_required
def calendario(current_user):
    """Return last 30 days of check-ins for GitHub-style contribution graph."""
    user_id = current_user["id"]
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT data, streak_atual, humor
                       FROM daily_checkins
                       WHERE user_id=%s AND data >= CURRENT_DATE - INTERVAL '30 days'
                       ORDER BY data""",
                    (user_id,),
                )
                rows = cur.fetchall()
        dias = [{"data": str(r["data"]), "streak": r["streak_atual"], "humor": r["humor"]} for r in rows]
    except Exception as e:
        logger.warning("Calendario DB error: %s", e)
        dias = []

    return jsonify({"user_id": user_id, "dias": dias, "total": len(dias)})


# ── Humor ─────────────────────────────────────────────────────────────────────

@daily_bp.post("/humor")
@token_required
def registrar_humor(current_user):
    """Register the user's mood for today (feliz/neutro/triste)."""
    user_id = current_user["id"]
    data = request.get_json(silent=True) or {}
    humor = (data.get("humor") or "").strip().lower()

    if humor not in ("feliz", "neutro", "triste"):
        return jsonify({"error": "humor deve ser feliz, neutro ou triste"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO daily_checkins (user_id, data, humor)
                       VALUES (%s, CURRENT_DATE, %s)
                       ON CONFLICT (user_id, data)
                       DO UPDATE SET humor = EXCLUDED.humor""",
                    (user_id, humor),
                )
    except Exception as e:
        logger.error("Humor error: %s", e)
        return jsonify({"error": "Erro ao registrar humor"}), 500

    return jsonify({"message": "Humor registrado", "humor": humor})


@daily_bp.get("/humor/media")
def humor_media():
    """Admin: return today's average mood counts."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT humor, COUNT(*) AS total
                       FROM daily_checkins
                       WHERE data = CURRENT_DATE AND humor IS NOT NULL
                       GROUP BY humor""",
                )
                rows = cur.fetchall()
        counts = {r["humor"]: r["total"] for r in rows}
    except Exception as e:
        logger.warning("Humor media DB error: %s", e)
        counts = {}

    return jsonify({
        "data": str(date.today()),
        "feliz": counts.get("feliz", 0),
        "neutro": counts.get("neutro", 0),
        "triste": counts.get("triste", 0),
    })
