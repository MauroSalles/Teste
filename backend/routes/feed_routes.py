"""Social Feed blueprint — /api/feed/*

Mini social network for the ice cream shop:
  - Timeline of posts (orders, achievements, check-ins)
  - Like and comment on posts
  - Trending posts of the week
  - Auto-generated posts for milestones
"""

import logging

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

try:
    from backend.database import get_db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

logger = logging.getLogger(__name__)

feed_bp = Blueprint("feed", __name__, url_prefix="/api/feed")

# Fallback posts for when the DB is unavailable
_MOCK_POSTS = [
    {
        "id": 1,
        "user_id": 1,
        "autor": "Maria S.",
        "tipo": "primeiro_pedido",
        "conteudo": "🍦 Maria S. acabou de fazer seu primeiro pedido!",
        "curtidas": 12,
        "created_at": "2026-04-01T10:00:00",
        "comentarios": 2,
    },
    {
        "id": 2,
        "user_id": 2,
        "autor": "João P.",
        "tipo": "streak",
        "conteudo": "🔥 João P. mantém 7 dias consecutivos de check-in!",
        "curtidas": 25,
        "created_at": "2026-04-01T09:30:00",
        "comentarios": 5,
    },
]


# ── Feed ──────────────────────────────────────────────────────────────────────

@feed_bp.get("")
def listar_feed():
    """Return recent posts (paginated, 20 per page)."""
    page = max(1, request.args.get("page", 1, type=int))
    offset = (page - 1) * 20

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT fp.id, fp.user_id, u.name AS autor, fp.tipo,
                              fp.conteudo, fp.curtidas, fp.created_at,
                              (SELECT COUNT(*) FROM feed_comentarios fc WHERE fc.post_id = fp.id) AS comentarios
                       FROM feed_posts fp
                       LEFT JOIN users u ON u.id = fp.user_id
                       ORDER BY fp.created_at DESC
                       LIMIT 20 OFFSET %s""",
                    (offset,),
                )
                rows = cur.fetchall()
        posts = []
        for r in rows:
            p = dict(r)
            p["created_at"] = str(p["created_at"])
            posts.append(p)
    except Exception as e:
        logger.warning("Feed DB error: %s", e)
        posts = _MOCK_POSTS

    return jsonify({"posts": posts, "page": page})


# ── Criar post ────────────────────────────────────────────────────────────────

@feed_bp.post("/post")
@token_required
def criar_post(current_user):
    """Create a new post (text + optional base64 image)."""
    user_id = current_user["id"]
    data = request.get_json(silent=True) or {}
    conteudo = (data.get("conteudo") or "").strip()
    imagem = data.get("imagem_base64")

    if not conteudo:
        return jsonify({"error": "conteudo é obrigatório"}), 400
    if len(conteudo) > 500:
        return jsonify({"error": "conteudo deve ter no máximo 500 caracteres"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO feed_posts (user_id, tipo, conteudo, imagem_base64)
                       VALUES (%s, 'manual', %s, %s) RETURNING id, created_at""",
                    (user_id, conteudo, imagem),
                )
                row = cur.fetchone()
    except Exception as e:
        logger.error("Criar post error: %s", e)
        return jsonify({"error": "Erro ao criar post"}), 500

    return jsonify({
        "id": row["id"],
        "conteudo": conteudo,
        "created_at": str(row["created_at"]),
    }), 201


# ── Curtir ────────────────────────────────────────────────────────────────────

@feed_bp.post("/<int:post_id>/curtir")
@token_required
def curtir_post(current_user, post_id):
    """Like a post."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE feed_posts SET curtidas = curtidas + 1 WHERE id=%s RETURNING curtidas",
                    (post_id,),
                )
                row = cur.fetchone()
        if not row:
            return jsonify({"error": "Post não encontrado"}), 404
        curtidas = row["curtidas"]
    except Exception as e:
        logger.error("Curtir error: %s", e)
        return jsonify({"error": "Erro ao curtir post"}), 500

    return jsonify({"post_id": post_id, "curtidas": curtidas})


# ── Comentar ──────────────────────────────────────────────────────────────────

@feed_bp.post("/<int:post_id>/comentar")
@token_required
def comentar_post(current_user, post_id):
    """Comment on a post."""
    user_id = current_user["id"]
    data = request.get_json(silent=True) or {}
    texto = (data.get("texto") or "").strip()

    if not texto:
        return jsonify({"error": "texto é obrigatório"}), 400
    if len(texto) > 280:
        return jsonify({"error": "Comentário deve ter no máximo 280 caracteres"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Verify post exists
                cur.execute("SELECT id FROM feed_posts WHERE id=%s", (post_id,))
                if not cur.fetchone():
                    return jsonify({"error": "Post não encontrado"}), 404

                cur.execute(
                    """INSERT INTO feed_comentarios (post_id, user_id, texto)
                       VALUES (%s, %s, %s) RETURNING id, created_at""",
                    (post_id, user_id, texto),
                )
                row = cur.fetchone()
    except Exception as e:
        logger.error("Comentar error: %s", e)
        return jsonify({"error": "Erro ao comentar"}), 500

    return jsonify({
        "id": row["id"],
        "post_id": post_id,
        "texto": texto,
        "created_at": str(row["created_at"]),
    }), 201


# ── Trending ──────────────────────────────────────────────────────────────────

@feed_bp.get("/trending")
def trending():
    """Return the most liked posts of the week."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT fp.id, fp.user_id, u.name AS autor, fp.tipo,
                              fp.conteudo, fp.curtidas, fp.created_at
                       FROM feed_posts fp
                       LEFT JOIN users u ON u.id = fp.user_id
                       WHERE fp.created_at >= NOW() - INTERVAL '7 days'
                       ORDER BY fp.curtidas DESC
                       LIMIT 10""",
                )
                rows = cur.fetchall()
        posts = [dict(r) for r in rows]
        for p in posts:
            p["created_at"] = str(p["created_at"])
    except Exception as e:
        logger.warning("Trending DB error: %s", e)
        posts = sorted(_MOCK_POSTS, key=lambda x: x["curtidas"], reverse=True)

    return jsonify({"trending": posts})


# ── Feed de usuário ───────────────────────────────────────────────────────────

@feed_bp.get("/usuario/<int:user_id>")
def feed_usuario(user_id):
    """Return posts from a specific user."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT fp.id, fp.user_id, u.name AS autor, fp.tipo,
                              fp.conteudo, fp.curtidas, fp.created_at
                       FROM feed_posts fp
                       LEFT JOIN users u ON u.id = fp.user_id
                       WHERE fp.user_id=%s
                       ORDER BY fp.created_at DESC
                       LIMIT 50""",
                    (user_id,),
                )
                rows = cur.fetchall()
        posts = [dict(r) for r in rows]
        for p in posts:
            p["created_at"] = str(p["created_at"])
    except Exception as e:
        logger.warning("Feed usuario DB error: %s", e)
        posts = [p for p in _MOCK_POSTS if p["user_id"] == user_id]

    return jsonify({"user_id": user_id, "posts": posts})


# ── Auto-post helper (called by other modules) ────────────────────────────────

def criar_post_automatico(user_id: int, tipo: str, conteudo: str) -> None:
    """Insert an auto-generated post (streak, badge, first order)."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO feed_posts (user_id, tipo, conteudo) VALUES (%s, %s, %s)",
                    (user_id, tipo, conteudo),
                )
    except Exception as e:
        logger.warning("Auto-post error: %s", e)
