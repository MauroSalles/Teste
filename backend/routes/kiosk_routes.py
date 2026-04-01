"""Kiosk / Self-service mode — /api/kiosk/*
Allows order without user account via temporary token (30min TTL).
"""
import secrets
import time
from flask import Blueprint, jsonify, request
from backend.database import get_db

kiosk_bp = Blueprint("kiosk", __name__, url_prefix="/api/kiosk")

# In-memory token store {token: {created_at, cart, ...}}
_sessions: dict = {}
SESSION_TTL = 1800  # 30 minutes


def _cleanup_sessions():
    """Remove expired sessions."""
    now = time.time()
    expired = [t for t, s in _sessions.items() if now - s["created_at"] > SESSION_TTL]
    for t in expired:
        del _sessions[t]


@kiosk_bp.post("/sessao/iniciar")
def iniciar_sessao():
    """POST /api/kiosk/sessao/iniciar — start a kiosk session (30min token)."""
    _cleanup_sessions()
    token = secrets.token_urlsafe(16)
    _sessions[token] = {"created_at": time.time(), "cart": [], "paid": False}
    return jsonify({"token": token, "ttl_segundos": SESSION_TTL, "mensagem": "Sessão iniciada! Bem-vindo 🍦"})


@kiosk_bp.get("/sessao/<token>")
def verificar_sessao(token):
    """GET /api/kiosk/sessao/<token> — check if session is active."""
    _cleanup_sessions()
    session = _sessions.get(token)
    if not session:
        return jsonify({"ativo": False, "error": "Sessão expirada ou inválida"}), 404
    remaining = int(SESSION_TTL - (time.time() - session["created_at"]))
    return jsonify({"ativo": True, "segundos_restantes": remaining, "itens_no_carrinho": len(session["cart"])})


@kiosk_bp.post("/pedido")
def pedido_kiosk():
    """POST /api/kiosk/pedido — place order via kiosk (no login required)."""
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    itens = data.get("itens", [])

    _cleanup_sessions()
    if not _sessions.get(token):
        return jsonify({"error": "Sessão inválida ou expirada"}), 401
    if not itens:
        return jsonify({"error": "Nenhum item selecionado"}), 400

    valor_total = 0.0
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                for item in itens:
                    cur.execute("SELECT preco, nome FROM sabores WHERE id = %s", (item.get("sabor_id"),))
                    row = cur.fetchone()
                    if row:
                        item["nome"] = row["nome"]
                        item["preco_unit"] = float(row["preco"])
                        valor_total += float(row["preco"]) * int(item.get("quantidade", 1))
    except Exception:
        valor_total = sum(float(i.get("preco", 0)) * int(i.get("quantidade", 1)) for i in itens)

    _sessions[token]["cart"] = itens
    _sessions[token]["valor_total"] = valor_total
    return jsonify({
        "mensagem": "Pedido registrado! Prossiga para o pagamento.",
        "itens": itens,
        "valor_total": valor_total,
        "token": token,
    })


@kiosk_bp.post("/pagamento")
def pagamento_kiosk():
    """POST /api/kiosk/pagamento — process kiosk payment."""
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    metodo = data.get("metodo", "pix")

    _cleanup_sessions()
    session = _sessions.get(token)
    if not session:
        return jsonify({"error": "Sessão inválida ou expirada"}), 401
    if session.get("paid"):
        return jsonify({"error": "Pagamento já realizado nesta sessão"}), 400
    if not session.get("cart"):
        return jsonify({"error": "Carrinho vazio"}), 400

    session["paid"] = True
    valor = session.get("valor_total", 0)
    return jsonify({
        "status": "aprovado",
        "metodo": metodo,
        "valor": valor,
        "mensagem": f"Pagamento de R${valor:.2f} aprovado via {metodo}! 🎉",
        "numero_pedido": secrets.token_hex(3).upper(),
    })


@kiosk_bp.get("/cardapio-simplificado")
def cardapio_simplificado():
    """GET /api/kiosk/cardapio-simplificado — touch-optimized menu."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.nome, s.preco, COALESCE(e.quantidade, 0) AS estoque
                    FROM sabores s
                    LEFT JOIN estoque e ON e.sabor_id = s.id
                    WHERE COALESCE(e.quantidade, 1) > 0
                    ORDER BY s.nome
                """)
                rows = cur.fetchall()
                return jsonify([dict(r) for r in rows])
    except Exception:
        return jsonify([
            {"id": 1, "nome": "Chocolate", "preco": 10.0, "estoque": 20},
            {"id": 2, "nome": "Morango", "preco": 9.5, "estoque": 15},
            {"id": 3, "nome": "Baunilha", "preco": 8.0, "estoque": 18},
            {"id": 4, "nome": "Pistache", "preco": 12.0, "estoque": 10},
            {"id": 5, "nome": "Limão", "preco": 9.0, "estoque": 12},
        ])
