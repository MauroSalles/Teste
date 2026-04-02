"""Social feed, daily check-in, and Sabor do Dia routes — /api/social/* and /api/checkin, /api/sabor-do-dia"""

import hashlib
import logging
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request

from backend.database import get_db

logger = logging.getLogger(__name__)

social_bp = Blueprint("social", __name__, url_prefix="/api")

# ── Sabor do Dia (deterministic, changes at midnight) ──────────────────────

_SABORES_DO_DIA = [
    {"nome": "Chocolate Belga", "emoji": "🍫", "descricao": "Cacau 70% selecionado, cremoso e intenso."},
    {"nome": "Morango Silvestre", "emoji": "🍓", "descricao": "Morangos frescos colhidos ao amanhecer."},
    {"nome": "Pistache da Sicília", "emoji": "🟢", "descricao": "Pistache italiano premium, inconfundível."},
    {"nome": "Baunilha Bourbon", "emoji": "🤍", "descricao": "Fava de baunilha de Madagascar."},
    {"nome": "Limão Siciliano", "emoji": "🍋", "descricao": "Refrescante e levemente ácido."},
    {"nome": "Caramelo Salgado", "emoji": "🧡", "descricao": "O equilíbrio perfeito entre doce e salgado."},
    {"nome": "Matcha Japonês", "emoji": "🍵", "descricao": "Chá verde premium de Uji, Japão."},
    {"nome": "Maracujá Tropical", "emoji": "🌺", "descricao": "Tropical e vibrante como um pôr do sol."},
    {"nome": "Açaí da Amazônia", "emoji": "🫐", "descricao": "Energia pura da floresta amazônica."},
    {"nome": "Cookie & Cream", "emoji": "🍪", "descricao": "Pedaços crocantes de biscoito no creme gelado."},
    {"nome": "Mango Alphonso", "emoji": "🥭", "descricao": "A manga mais doce do mundo, da Índia."},
    {"nome": "Framboesa Negra", "emoji": "🫒", "descricao": "Silvestres e aromáticas, colhidas na estação."},
    {"nome": "Tiramisu", "emoji": "☕", "descricao": "Espresso intenso, mascarpone e cacau."},
    {"nome": "Lavanda Provence", "emoji": "💜", "descricao": "Floral e elegante, do sul da França."},
]

_FRASES_GELINHO = [
    "Oi! Que sabor você escolheria hoje? 😊",
    "Sabia que o sorvete foi inventado na China há mais de 2000 anos? 🤯",
    "Cada colherada é uma viagem! Para onde você quer ir hoje? ✈️",
    "O Sabor do Dia foi escolhido especialmente para você! 🍦",
    "Já fez o seu check-in de hoje? Mantenha o streak! 🔥",
    "Partilhe um momento doce com alguém especial hoje! 💛",
    "O sorvete perfeito começa com os melhores ingredientes. ✨",
    "Curiosidade: o sabor favorito do mundo é chocolate! 🍫",
    "Qual é o seu sabor da infância? Me conta! 👀",
    "Hoje é um ótimo dia para experimentar algo novo! 🌟",
    "O segredo está nos detalhes — como os nossos ingredientes! 🌿",
    "Obrigado por estar aqui! Você faz parte da família Gelateria! 🏠",
    "Deixe uma mensagem no feed para animar o dia de alguém! 💬",
    "Você sabia? Cada emoji que usamos tem um significado especial! 🎨",
    "Tecnologia + sorvete = perfeição! 🤖🍦",
]


@social_bp.get("/sabor-do-dia")
def sabor_do_dia():
    """Return a deterministic daily flavour that rotates at midnight."""
    today = date.today()
    idx = (today.year * 366 + today.timetuple().tm_yday) % len(_SABORES_DO_DIA)
    sabor = _SABORES_DO_DIA[idx]
    frase_idx = (today.year * 366 + today.timetuple().tm_yday) % len(_FRASES_GELINHO)
    return jsonify({
        "sabor": sabor,
        "frase_gelinho": _FRASES_GELINHO[frase_idx],
        "data": today.isoformat(),
    })


# ── Daily check-in + streak ────────────────────────────────────────────────

def _get_session_id(request) -> str:
    """Extract the anonymous session identifier sent by the client.

    The client (frontend) is responsible for generating and persisting a
    UUID stored in ``localStorage``.  It must be sent via the
    ``X-Session-Id`` header or the ``session_id`` JSON body field.
    If neither is present, a random per-request token is generated so the
    call can still complete, albeit without cross-request session continuity.
    We intentionally avoid using the IP address because that would conflate
    users behind NAT / shared proxies.
    """
    sid = request.headers.get("X-Session-Id", "").strip()
    if not sid:
        body = request.get_json(silent=True, force=True)
        sid = ((body or {}).get("session_id") or "").strip() if isinstance(body, dict) else ""
    if not sid:
        import os
        sid = hashlib.sha256(os.urandom(16)).hexdigest()[:32]
    return sid[:64]


@social_bp.post("/checkin")
def checkin():
    """Record daily check-in and return current streak."""
    data = request.get_json(silent=True) or {}
    mood = data.get("mood", "neutral")
    if mood not in ("happy", "neutral", "sad"):
        mood = "neutral"

    session_id = _get_session_id(request)
    today = date.today()
    yesterday = today - timedelta(days=1)

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Check if already checked in today
                cur.execute(
                    "SELECT id, streak FROM daily_checkins WHERE session_id = %s AND date = %s",
                    (session_id, today),
                )
                existing = cur.fetchone()
                if existing:
                    return jsonify({
                        "already_done": True,
                        "streak": existing["streak"],
                        "date": today.isoformat(),
                    })

                # Compute streak: +1 if checked in yesterday, else reset to 1
                cur.execute(
                    "SELECT streak FROM daily_checkins WHERE session_id = %s AND date = %s",
                    (session_id, yesterday),
                )
                prev = cur.fetchone()
                streak = (prev["streak"] + 1) if prev else 1

                cur.execute(
                    """INSERT INTO daily_checkins (session_id, date, mood, streak)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (session_id, date) DO NOTHING
                       RETURNING streak""",
                    (session_id, today, mood, streak),
                )

                return jsonify({
                    "already_done": False,
                    "streak": streak,
                    "date": today.isoformat(),
                    "mood": mood,
                })
    except Exception as e:
        logger.error("checkin error: %s", e)
        return jsonify({"error": "Erro ao registrar check-in"}), 500


@social_bp.get("/checkin/status")
def checkin_status():
    """Return today's check-in status and streak for this session."""
    session_id = _get_session_id(request)
    today = date.today()
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT streak, mood FROM daily_checkins WHERE session_id = %s AND date = %s",
                    (session_id, today),
                )
                row = cur.fetchone()
                if row:
                    return jsonify({
                        "checked_in": True,
                        "streak": row["streak"],
                        "mood": row["mood"],
                        "date": today.isoformat(),
                    })
                # Check yesterday for streak context
                yesterday = today - timedelta(days=1)
                cur.execute(
                    "SELECT streak FROM daily_checkins WHERE session_id = %s AND date = %s",
                    (session_id, yesterday),
                )
                prev = cur.fetchone()
                return jsonify({
                    "checked_in": False,
                    "streak": (prev["streak"] if prev else 0),
                    "date": today.isoformat(),
                })
    except Exception as e:
        logger.error("checkin_status error: %s", e)
        return jsonify({"checked_in": False, "streak": 0, "date": today.isoformat()})


# ── Social Feed ────────────────────────────────────────────────────────────

@social_bp.get("/social/feed")
def feed():
    """Return the latest social posts."""
    try:
        limit = int(request.args.get("limit", 20))
        limit = max(1, min(limit, 50))
    except (TypeError, ValueError):
        limit = 20

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, author, content, emoji, likes,
                              to_char(created_at, 'DD/MM/YYYY HH24:MI') AS created_at
                       FROM social_posts
                       ORDER BY created_at DESC
                       LIMIT %s""",
                    (limit,),
                )
                posts = [dict(r) for r in cur.fetchall()]
        return jsonify(posts)
    except Exception as e:
        logger.error("feed error: %s", e)
        return jsonify([])


@social_bp.post("/social/post")
def create_post():
    """Create a new social feed post."""
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    author = (data.get("author") or "Visitante").strip()[:100]
    emoji = (data.get("emoji") or "🍦").strip()[:10]

    if not content:
        return jsonify({"error": "content é obrigatório"}), 400
    if len(content) > 280:
        return jsonify({"error": "content deve ter no máximo 280 caracteres"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO social_posts (author, content, emoji)
                       VALUES (%s, %s, %s)
                       RETURNING id, author, content, emoji, likes,
                                 to_char(created_at, 'DD/MM/YYYY HH24:MI') AS created_at""",
                    (author, content, emoji),
                )
                post = dict(cur.fetchone())
        return jsonify(post), 201
    except Exception as e:
        logger.error("create_post error: %s", e)
        return jsonify({"error": "Erro ao criar post"}), 500


@social_bp.post("/social/post/<int:post_id>/like")
def like_post(post_id: int):
    """Toggle a like on a post (deduped per session)."""
    session_id = _get_session_id(request)
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Check if already liked
                cur.execute(
                    "SELECT id FROM social_likes WHERE post_id = %s AND session_id = %s",
                    (post_id, session_id),
                )
                existing = cur.fetchone()
                if existing:
                    # Unlike
                    cur.execute(
                        "DELETE FROM social_likes WHERE post_id = %s AND session_id = %s",
                        (post_id, session_id),
                    )
                    cur.execute(
                        "UPDATE social_posts SET likes = GREATEST(likes - 1, 0) WHERE id = %s RETURNING likes",
                        (post_id,),
                    )
                    row = cur.fetchone()
                    return jsonify({"liked": False, "likes": row["likes"] if row else 0})
                else:
                    # Like
                    cur.execute(
                        "INSERT INTO social_likes (post_id, session_id) VALUES (%s, %s)",
                        (post_id, session_id),
                    )
                    cur.execute(
                        "UPDATE social_posts SET likes = likes + 1 WHERE id = %s RETURNING likes",
                        (post_id,),
                    )
                    row = cur.fetchone()
                    if not row:
                        return jsonify({"error": "Post não encontrado"}), 404
                    return jsonify({"liked": True, "likes": row["likes"]})
    except Exception as e:
        logger.error("like_post error: %s", e)
        return jsonify({"error": "Erro ao curtir post"}), 500
