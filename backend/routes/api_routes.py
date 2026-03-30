from flask import Blueprint, request, jsonify

from backend.models.sabor import (
    listar_sabores,
    adicionar_sabor,
    atualizar_sabor,
    remover_sabor,
)
from backend.models.pedido import listar_pedidos, criar_pedido
from backend.models.estoque import ver_estoque, definir_estoque, obter_estoque, ajustar_estoque
from backend.models.sabor import buscar_sabor_por_nome

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ─────────────────────────────────────────────────────────
# Sabores
# ─────────────────────────────────────────────────────────

@api_bp.route("/sabores", methods=["GET"])
def get_sabores():
    """Return all ice-cream flavors."""
    return jsonify({"sabores": [dict(s) for s in listar_sabores()]}), 200


@api_bp.route("/sabores", methods=["POST"])
def post_sabores():
    """Add a new flavor. Body: {nome, preco}"""
    data = request.get_json(force=True) or {}
    nome = (data.get("nome") or "").strip()
    preco = data.get("preco")

    if not nome:
        return jsonify({"error": "O campo 'nome' é obrigatório."}), 400
    try:
        preco = float(preco)
        if preco < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "O campo 'preco' deve ser um número não-negativo."}), 400

    sabor = adicionar_sabor(nome, preco)
    return jsonify({"sabor": dict(sabor)}), 201


@api_bp.route("/sabores/<int:sabor_id>", methods=["PUT"])
def put_sabor(sabor_id):
    """Update the price of a flavor. Body: {preco}"""
    data = request.get_json(force=True) or {}
    preco = data.get("preco")
    try:
        preco = float(preco)
        if preco < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "O campo 'preco' deve ser um número não-negativo."}), 400

    sabor = atualizar_sabor(sabor_id, preco)
    if not sabor:
        return jsonify({"error": f"Sabor ID {sabor_id} não encontrado."}), 404
    return jsonify({"sabor": dict(sabor)}), 200


@api_bp.route("/sabores/<int:sabor_id>", methods=["DELETE"])
def delete_sabor(sabor_id):
    """Remove a flavor."""
    sabor = remover_sabor(sabor_id)
    if not sabor:
        return jsonify({"error": f"Sabor ID {sabor_id} não encontrado."}), 404
    return jsonify({"message": f"Sabor ID {sabor_id} removido com sucesso."}), 200


# ─────────────────────────────────────────────────────────
# Pedidos
# ─────────────────────────────────────────────────────────

@api_bp.route("/pedidos", methods=["GET"])
def get_pedidos():
    """Return all orders."""
    pedidos = listar_pedidos()
    result = []
    for p in pedidos:
        row = dict(p)
        if hasattr(row.get("data"), "isoformat"):
            row["data"] = row["data"].isoformat()
        result.append(row)
    return jsonify({"pedidos": result}), 200


@api_bp.route("/pedidos", methods=["POST"])
def post_pedidos():
    """Create a new order. Body: {sabor_id, quantidade} or {sabor, quantidade}"""
    data = request.get_json(force=True) or {}
    quantidade = data.get("quantidade")

    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "O campo 'quantidade' deve ser um inteiro positivo."}), 400

    # Accept either sabor_id (int) or sabor (name string)
    sabor_id = data.get("sabor_id")
    if sabor_id is not None:
        try:
            sabor_id = int(sabor_id)
        except (TypeError, ValueError):
            return jsonify({"error": "O campo 'sabor_id' deve ser um inteiro."}), 400
        # Verify the flavor exists
        sabores = listar_sabores()
        sabor = next((s for s in sabores if s["id"] == sabor_id), None)
        if not sabor:
            return jsonify({"error": f"Sabor ID {sabor_id} não encontrado."}), 404
    else:
        nome_sabor = (data.get("sabor") or "").strip()
        if not nome_sabor:
            return jsonify({"error": "Informe 'sabor_id' ou 'sabor' (nome)."}), 400
        sabor = buscar_sabor_por_nome(nome_sabor)
        if not sabor:
            return jsonify({"error": f"Sabor '{nome_sabor}' não encontrado."}), 404
        sabor_id = sabor["id"]

    estoque_atual = obter_estoque(sabor_id)
    if estoque_atual > 0 and quantidade > estoque_atual:
        return jsonify({
            "error": f"Estoque insuficiente. Disponível: {estoque_atual}, solicitado: {quantidade}."
        }), 409

    pedido = criar_pedido(sabor_id, quantidade)
    if estoque_atual > 0:
        ajustar_estoque(sabor_id, -quantidade)

    row = dict(pedido)
    if hasattr(row.get("data"), "isoformat"):
        row["data"] = row["data"].isoformat()
    return jsonify({"pedido": row}), 201


# ─────────────────────────────────────────────────────────
# Estoque
# ─────────────────────────────────────────────────────────

@api_bp.route("/estoque", methods=["GET"])
def get_estoque():
    """Return current stock for all flavors."""
    itens = ver_estoque()
    return jsonify({"estoque": [dict(i) for i in itens]}), 200


@api_bp.route("/estoque/<int:sabor_id>", methods=["PUT"])
def put_estoque(sabor_id):
    """Set (or adjust) the stock for a flavor. Body: {quantidade} to set, or {delta} to adjust."""
    data = request.get_json(force=True) or {}

    if "quantidade" in data:
        try:
            qtd = int(data["quantidade"])
            if qtd < 0:
                raise ValueError
        except (TypeError, ValueError):
            return jsonify({"error": "O campo 'quantidade' deve ser um inteiro não-negativo."}), 400
        item = definir_estoque(sabor_id, qtd)
    elif "delta" in data:
        try:
            delta = int(data["delta"])
        except (TypeError, ValueError):
            return jsonify({"error": "O campo 'delta' deve ser um inteiro."}), 400
        item = ajustar_estoque(sabor_id, delta)
    else:
        return jsonify({"error": "Informe 'quantidade' (para definir) ou 'delta' (para ajustar)."}), 400

    if not item:
        return jsonify({"error": f"Sabor ID {sabor_id} não encontrado."}), 404
    return jsonify({"estoque": dict(item)}), 200


# ─────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────

@api_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    """Return a summary of the system: flavors, orders, and low-stock alerts."""
    sabores = listar_sabores()
    pedidos = listar_pedidos()
    estoque = ver_estoque()

    sem_estoque = [dict(i) for i in estoque if int(i["quantidade"]) == 0]
    estoque_baixo = [dict(i) for i in estoque if 0 < int(i["quantidade"]) <= 5]

    return jsonify({
        "total_sabores": len(sabores),
        "total_pedidos": len(pedidos),
        "sem_estoque": sem_estoque,
        "estoque_baixo": estoque_baixo,
    }), 200
