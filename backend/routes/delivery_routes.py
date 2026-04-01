"""Delivery & order tracking — /api/delivery/*
Graceful degradation if delivery_pedidos table doesn't exist.
"""
import json
from flask import Blueprint, jsonify, request
from backend.database import get_db

delivery_bp = Blueprint("delivery", __name__, url_prefix="/api/delivery")

# In-memory fallback if DB not available
_mock_orders: dict = {}
_order_counter = 100


def _frete_por_cep(cep: str) -> dict:
    """Mock freight calculation by CEP prefix."""
    cep = (cep or "").replace("-", "").strip()
    if not cep or len(cep) < 5:
        return {"frete": 5.0, "prazo_dias": 3, "regiao": "Desconhecida"}
    prefix = int(cep[:2])
    if prefix <= 19:
        return {"frete": 8.0, "prazo_dias": 1, "regiao": "São Paulo Capital"}
    if prefix <= 29:
        return {"frete": 7.5, "prazo_dias": 1, "regiao": "São Paulo Interior"}
    if prefix <= 39:
        return {"frete": 10.0, "prazo_dias": 2, "regiao": "Minas Gerais"}
    if prefix <= 49:
        return {"frete": 12.0, "prazo_dias": 2, "regiao": "Bahia/Sergipe"}
    return {"frete": 15.0, "prazo_dias": 3, "regiao": "Outras regiões"}


@delivery_bp.post("/pedido")
def criar_pedido_delivery():
    """POST /api/delivery/pedido — create a delivery order."""
    global _order_counter
    data = request.get_json(silent=True) or {}
    itens = data.get("itens", [])
    endereco = (data.get("endereco") or "").strip()
    cep = (data.get("cep") or "").strip()
    metodo = data.get("metodo_pagamento", "pix")
    user_id = data.get("user_id")

    if not itens:
        return jsonify({"error": "itens não pode ser vazio"}), 400
    if not endereco:
        return jsonify({"error": "endereco é obrigatório"}), 400

    valor_total = 0.0
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                for item in itens:
                    cur.execute("SELECT preco FROM sabores WHERE id = %s", (item.get("sabor_id"),))
                    row = cur.fetchone()
                    if row:
                        valor_total += float(row["preco"]) * int(item.get("quantidade", 1))
    except Exception:
        valor_total = sum(float(i.get("preco", 0)) * int(i.get("quantidade", 1)) for i in itens)

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO delivery_pedidos (user_id, itens, endereco, cep, metodo_pagamento, valor_total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, status, created_at
                """, (user_id, json.dumps(itens), endereco, cep, metodo, valor_total))
                row = cur.fetchone()
                pedido_id = row["id"]
                status = row["status"]
                created_at = row["created_at"]
    except Exception:
        _order_counter += 1
        pedido_id = _order_counter
        status = "recebido"
        created_at = "now"
        _mock_orders[pedido_id] = {"id": pedido_id, "status": "recebido", "itens": itens,
                                    "endereco": endereco, "valor_total": valor_total}

    return jsonify({
        "id": pedido_id,
        "status": status,
        "valor_total": valor_total,
        "mensagem": f"Pedido #{pedido_id} recebido! Aguardando confirmação.",
        "created_at": str(created_at),
    }), 201


@delivery_bp.get("/pedido/<int:pedido_id>/status")
def status_pedido(pedido_id):
    """GET /api/delivery/pedido/<id>/status — get order status."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, status, valor_total, endereco, created_at, updated_at
                    FROM delivery_pedidos WHERE id = %s
                """, (pedido_id,))
                row = cur.fetchone()
                if not row:
                    return jsonify({"error": "Pedido não encontrado"}), 404
                return jsonify(dict(row))
    except Exception:
        if pedido_id in _mock_orders:
            return jsonify(_mock_orders[pedido_id])
        return jsonify({"id": pedido_id, "status": "recebido", "source": "mock"})


@delivery_bp.put("/pedido/<int:pedido_id>/status")
def atualizar_status(pedido_id):
    """PUT /api/delivery/pedido/<id>/status — update order status (admin)."""
    VALID_STATUSES = ["recebido", "preparando", "a caminho", "entregue", "cancelado"]
    data = request.get_json(silent=True) or {}
    novo_status = (data.get("status") or "").strip().lower()
    if novo_status not in VALID_STATUSES:
        return jsonify({"error": f"Status inválido. Válidos: {VALID_STATUSES}"}), 400

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE delivery_pedidos
                    SET status = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, status, updated_at
                """, (novo_status, pedido_id))
                row = cur.fetchone()
                if not row:
                    return jsonify({"error": "Pedido não encontrado"}), 404
                return jsonify(dict(row))
    except Exception:
        if pedido_id in _mock_orders:
            _mock_orders[pedido_id]["status"] = novo_status
            return jsonify(_mock_orders[pedido_id])
        return jsonify({"id": pedido_id, "status": novo_status, "source": "mock"})


@delivery_bp.get("/pedido/<int:pedido_id>/track")
def track_pedido(pedido_id):
    """GET /api/delivery/pedido/<id>/track — real-time tracking info."""
    STATUS_STEPS = {
        "recebido": {"step": 1, "eta_min": 40, "mensagem": "Pedido recebido! Estamos confirmando."},
        "preparando": {"step": 2, "eta_min": 25, "mensagem": "Seu sorvete está sendo preparado 🍦"},
        "a caminho": {"step": 3, "eta_min": 10, "mensagem": "Entregador a caminho! 🛵"},
        "entregue": {"step": 4, "eta_min": 0, "mensagem": "Entregue! Bom apetite! ✅"},
        "cancelado": {"step": 0, "eta_min": 0, "mensagem": "Pedido cancelado."},
    }
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, status, valor_total, endereco FROM delivery_pedidos WHERE id = %s", (pedido_id,))
                row = cur.fetchone()
                if not row:
                    return jsonify({"error": "Pedido não encontrado"}), 404
                status = row["status"]
    except Exception:
        row = _mock_orders.get(pedido_id, {"id": pedido_id, "status": "recebido"})
        status = row.get("status", "recebido")

    step_info = STATUS_STEPS.get(status, STATUS_STEPS["recebido"])
    return jsonify({
        "id": pedido_id,
        "status": status,
        **step_info,
        "total_steps": 4,
        "posicao_entregador": {"lat": -23.5505, "lng": -46.6333},
    })


@delivery_bp.post("/calcular-frete")
def calcular_frete():
    """POST /api/delivery/calcular-frete — calculate shipping by CEP."""
    data = request.get_json(silent=True) or {}
    cep = data.get("cep", "")
    result = _frete_por_cep(cep)
    return jsonify(result)


@delivery_bp.get("/historico")
def historico():
    """GET /api/delivery/historico — order history for a user."""
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id é obrigatório"}), 400
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, status, valor_total, endereco, metodo_pagamento, created_at
                    FROM delivery_pedidos
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 20
                """, (user_id,))
                rows = cur.fetchall()
    except Exception:
        rows = []
    return jsonify([dict(r) for r in rows])
