"""Advanced Gamification — /api/game/*"""
from datetime import date
from flask import Blueprint, jsonify, request
from backend.database import get_db

game_bp = Blueprint("game", __name__, url_prefix="/api/game")

LEVELS = [
    (0, "Aprendiz"), (500, "Regular"), (1500, "Veterano"),
    (4000, "Expert"), (10000, "Mestre"), (25000, "Lendário"),
]
BADGES_CATALOG = [
    {"id": 1, "nome": "Iniciante", "icone": "🍦", "descricao": "Primeiro pedido realizado", "xp_requerido": 0},
    {"id": 2, "nome": "Regular", "icone": "🌟", "descricao": "500 XP acumulados", "xp_requerido": 500},
    {"id": 3, "nome": "VIP", "icone": "💎", "descricao": "2000 XP acumulados", "xp_requerido": 2000},
    {"id": 4, "nome": "Lendário", "icone": "🔥", "descricao": "10000 XP acumulados", "xp_requerido": 10000},
]
DESAFIOS_CATALOG = [
    {"id": 1, "nome": "Madrugador", "icone": "🌙", "descricao": "Peça entre 00h e 06h", "xp": 150},
    {"id": 2, "nome": "Explorador", "icone": "🗺️", "descricao": "Experimente 5 sabores diferentes", "xp": 300},
    {"id": 3, "nome": "Fidelão", "icone": "❤️", "descricao": "Faça 10 pedidos", "xp": 500},
    {"id": 4, "nome": "Social", "icone": "👥", "descricao": "Indique 3 amigos", "xp": 200},
]


def _get_level(xp: int) -> dict:
    nivel = 1
    titulo = LEVELS[0][1]
    proximo_xp = LEVELS[1][0] if len(LEVELS) > 1 else 9999
    for i, (req_xp, name) in enumerate(LEVELS):
        if xp >= req_xp:
            nivel = i + 1
            titulo = name
            proximo_xp = LEVELS[i + 1][0] if i + 1 < len(LEVELS) else req_xp
    return {"nivel": nivel, "titulo": titulo, "proximo_nivel_xp": proximo_xp}


def _get_or_create_profile(user_id: int) -> dict:
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM game_profiles WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                if not row:
                    cur.execute("""
                        INSERT INTO game_profiles (user_id, xp, nivel)
                        VALUES (%s, 0, 1) RETURNING *
                    """, (user_id,))
                    row = cur.fetchone()
                return dict(row)
    except Exception:
        return {"user_id": user_id, "xp": 0, "nivel": 1, "last_checkin": None}


@game_bp.get("/perfil/<int:user_id>")
def perfil(user_id):
    """GET /api/game/perfil/<user_id> — player profile with XP, level, badges."""
    profile = _get_or_create_profile(user_id)
    xp = profile.get("xp", 0)
    level_info = _get_level(xp)
    earned_badges = [b for b in BADGES_CATALOG if xp >= b["xp_requerido"]]
    locked_badges = [b for b in BADGES_CATALOG if xp < b["xp_requerido"]]
    return jsonify({
        "user_id": user_id,
        "xp": xp,
        **level_info,
        "badges_conquistados": earned_badges,
        "badges_bloqueados": locked_badges,
    })


@game_bp.post("/check-in")
def check_in():
    """POST /api/game/check-in — daily check-in (+50 XP)."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id é obrigatório"}), 400

    today = date.today().isoformat()
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT last_checkin FROM game_profiles WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                if row and row.get("last_checkin") and str(row["last_checkin"]) == today:
                    return jsonify({"message": "Check-in já realizado hoje!", "xp_ganho": 0}), 200
                if not row:
                    cur.execute("INSERT INTO game_profiles (user_id, xp, nivel) VALUES (%s, 50, 1)", (user_id,))
                else:
                    cur.execute("""
                        UPDATE game_profiles SET xp = xp + 50, last_checkin = %s WHERE user_id = %s
                    """, (today, user_id))
                cur.execute("UPDATE game_profiles SET last_checkin = %s WHERE user_id = %s", (today, user_id))
    except Exception:
        return jsonify({"message": "Check-in realizado! (+50 XP)", "xp_ganho": 50, "source": "mock"})

    return jsonify({"message": "Check-in realizado! +50 XP 🎉", "xp_ganho": 50})


@game_bp.get("/ranking")
def ranking():
    """GET /api/game/ranking — top 10 players by XP."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT gp.user_id, COALESCE(u.name, 'Jogador #' || gp.user_id) AS nome,
                           gp.xp, gp.nivel
                    FROM game_profiles gp
                    LEFT JOIN users u ON u.id = gp.user_id
                    ORDER BY gp.xp DESC LIMIT 10
                """)
                rows = cur.fetchall()
    except Exception:
        rows = []

    result = []
    for i, r in enumerate(rows):
        r = dict(r)
        r["posicao"] = i + 1
        r["medal"] = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
        result.append(r)
    return jsonify(result)


@game_bp.post("/desafio/<int:desafio_id>/completar")
def completar_desafio(desafio_id):
    """POST /api/game/desafio/<id>/completar — complete a challenge (+XP)."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id é obrigatório"}), 400

    desafio = next((d for d in DESAFIOS_CATALOG if d["id"] == desafio_id), None)
    if not desafio:
        return jsonify({"error": "Desafio não encontrado"}), 404

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT concluido FROM user_desafios
                    WHERE user_id = %s AND desafio_id = %s
                """, (user_id, desafio_id))
                existing = cur.fetchone()
                if existing and existing["concluido"]:
                    return jsonify({"message": "Desafio já concluído!", "xp_ganho": 0}), 200
                cur.execute("""
                    INSERT INTO user_desafios (user_id, desafio_id, concluido, completed_at)
                    VALUES (%s, %s, TRUE, NOW())
                    ON CONFLICT DO NOTHING
                """, (user_id, desafio_id))
                cur.execute("""
                    INSERT INTO game_profiles (user_id, xp, nivel) VALUES (%s, %s, 1)
                    ON CONFLICT (user_id) DO UPDATE SET xp = game_profiles.xp + %s
                """, (user_id, desafio["xp"], desafio["xp"]))
    except Exception:
        pass

    return jsonify({
        "message": f"Desafio '{desafio['nome']}' concluído! +{desafio['xp']} XP 🎉",
        "xp_ganho": desafio["xp"],
        "desafio": desafio,
    })


@game_bp.get("/desafios")
def listar_desafios():
    """GET /api/game/desafios — list active challenges."""
    return jsonify(DESAFIOS_CATALOG)


@game_bp.get("/badges")
def listar_badges():
    """GET /api/game/badges — badge catalog."""
    return jsonify(BADGES_CATALOG)
