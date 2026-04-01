"""REST API blueprint — /api/*"""

import hashlib
from datetime import date
from flask import Blueprint, jsonify, request

import backend.models.sabor as sabor_model
import backend.models.pedido as pedido_model
import backend.models.estoque as estoque_model
import backend.models.feedback as feedback_model
from backend.models.fidelidade import (
    obter_pontos,
    adicionar_pontos,
    resgatar,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ── Sabores ──────────────────────────────────────────────────────────────────

@api_bp.get("/sabores")
def listar_sabores():
    sabores = sabor_model.listar_sabores()
    return jsonify([dict(s) for s in sabores])


@api_bp.post("/sabores")
def criar_sabor():
    data = request.get_json(silent=True) or {}
    nome = (data.get("nome") or "").strip()
    preco = data.get("preco")
    if not nome or preco is None:
        return jsonify({"error": "nome e preco são obrigatórios"}), 400
    try:
        preco = float(preco)
        if preco < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "preco deve ser um número positivo"}), 400
    sabor = sabor_model.adicionar_sabor(nome, preco)
    return jsonify(dict(sabor)), 201


@api_bp.put("/sabores/<int:sabor_id>")
def atualizar_sabor(sabor_id):
    data = request.get_json(silent=True) or {}
    preco = data.get("preco")
    if preco is None:
        return jsonify({"error": "preco é obrigatório"}), 400
    try:
        preco = float(preco)
        if preco < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "preco deve ser um número positivo"}), 400

    sabor = sabor_model.atualizar_sabor(sabor_id, preco)
    if not sabor:
        return jsonify({"error": "Sabor não encontrado"}), 404
    return jsonify(dict(sabor))


@api_bp.delete("/sabores/<int:sabor_id>")
def remover_sabor(sabor_id):
    sabor = sabor_model.remover_sabor(sabor_id)
    if not sabor:
        return jsonify({"error": "Sabor não encontrado"}), 404
    return jsonify({"message": "Sabor removido com sucesso", "sabor": dict(sabor)})


# ── Pedidos ──────────────────────────────────────────────────────────────────

@api_bp.get("/pedidos")
def listar_pedidos():
    pedidos = pedido_model.listar_pedidos()
    return jsonify([dict(p) for p in pedidos])


@api_bp.post("/pedidos")
def criar_pedido():
    data = request.get_json(silent=True) or {}
    sabor_id = data.get("sabor_id")
    quantidade = data.get("quantidade")
    if sabor_id is None or quantidade is None:
        return jsonify({"error": "sabor_id e quantidade são obrigatórios"}), 400
    try:
        sabor_id = int(sabor_id)
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "sabor_id e quantidade devem ser inteiros positivos"}), 400

    pedido = pedido_model.criar_pedido(sabor_id, quantidade)
    if not pedido:
        return jsonify({"error": "Sabor não encontrado"}), 404
    return jsonify(dict(pedido)), 201


# ── Estoque ──────────────────────────────────────────────────────────────────

@api_bp.get("/estoque")
def listar_estoque():
    estoque = estoque_model.ver_estoque()
    return jsonify([dict(e) for e in estoque])


@api_bp.put("/estoque/<int:sabor_id>")
def set_estoque(sabor_id):
    data = request.get_json(silent=True) or {}
    quantidade = data.get("quantidade")
    if quantidade is None:
        return jsonify({"error": "quantidade é obrigatória"}), 400
    try:
        quantidade = int(quantidade)
        if quantidade < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "quantidade deve ser um inteiro não-negativo"}), 400
    row = estoque_model.definir_estoque(sabor_id, quantidade)
    if not row:
        return jsonify({"error": "Sabor não encontrado"}), 404
    return jsonify(dict(row))


# ── Status / Dashboard summary ────────────────────────────────────────────────

@api_bp.get("/status")
def status():
    sabores = sabor_model.listar_sabores()
    pedidos = pedido_model.listar_pedidos()
    estoque = estoque_model.ver_estoque()
    receita = sum(
        float(p.get("quantidade", 0)) * float(
            next((s["preco"] for s in sabores if s["nome"] == p.get("sabor")), 0)
        )
        for p in pedidos
    )
    estoque_baixo = [e for e in estoque if int(e.get("quantidade", 0)) < 5]
    return jsonify({
        "total_sabores": len(sabores),
        "total_pedidos": len(pedidos),
        "receita_total": round(receita, 2),
        "alertas_estoque_baixo": len(estoque_baixo),
        "estoque_baixo": [dict(e) for e in estoque_baixo],
        "pedidos_recentes": [dict(p) for p in pedidos[:10]],
    })


# ── Relatórios ────────────────────────────────────────────────────────────────

@api_bp.get("/relatorios/vendas")
def relatorio_vendas():
    periodo = request.args.get("periodo", "diario")
    if periodo not in ("diario", "semanal", "mensal"):
        return jsonify({"error": "periodo deve ser: diario, semanal ou mensal"}), 400
    rows = pedido_model.relatorio_vendas(periodo)
    return jsonify([dict(r) for r in rows])


@api_bp.get("/relatorios/sabores-populares")
def sabores_populares():
    try:
        limit = int(request.args.get("limit", 5))
        limit = max(1, min(limit, 50))
    except (TypeError, ValueError):
        limit = 5
    rows = pedido_model.sabores_populares(limit)
    return jsonify([dict(r) for r in rows])


# ── Fidelidade ────────────────────────────────────────────────────────────────

@api_bp.get("/fidelidade/<int:user_id>/pontos")
def get_pontos(user_id):
    row = obter_pontos(user_id)
    if not row:
        return jsonify({"user_id": user_id, "pontos": 0, "resgates": 0})
    return jsonify(dict(row))


@api_bp.post("/fidelidade/<int:user_id>/resgatar")
def resgatar_pontos(user_id):
    try:
        row = resgatar(user_id)
        return jsonify({"message": "Recompensa resgatada com sucesso!", **row})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ── Feedback ──────────────────────────────────────────────────────────────────

@api_bp.post("/feedback")
def criar_feedback():
    """Submit customer feedback (name, optional email, message, rating 1–5)."""
    data = request.get_json(silent=True) or {}
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip() or None
    mensagem = (data.get("mensagem") or "").strip()
    nota = data.get("nota")

    if not nome or not mensagem:
        return jsonify({"error": "nome e mensagem são obrigatórios"}), 400
    try:
        nota = int(nota)
        if nota < 1 or nota > 5:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "nota deve ser um inteiro entre 1 e 5"}), 400

    row = feedback_model.registrar_feedback(nome, email, mensagem, nota)
    return jsonify(dict(row)), 201


@api_bp.get("/feedback")
def listar_feedback():
    """Return recent feedback records (last 50, email omitted for privacy)."""
    rows = feedback_model.listar_feedbacks()
    return jsonify([dict(r) for r in rows])


@api_bp.get("/feedback/media")
def media_feedback():
    """Return the average customer rating."""
    media = feedback_model.media_nota()
    return jsonify({"media_nota": media})


# ── Sabor do Dia ──────────────────────────────────────────────────────────────

@api_bp.get("/sabor-do-dia")
def sabor_do_dia():
    """Return a deterministic daily flavor chosen from the active menu."""
    sabores = sabor_model.listar_sabores()
    if not sabores:
        return jsonify({"error": "Nenhum sabor cadastrado"}), 404

    # Deterministic: pick the sabor based on the day of the year
    day_seed = int(hashlib.md5(str(date.today()).encode()).hexdigest(), 16)
    escolhido = sabores[day_seed % len(sabores)]
    return jsonify({
        "data": str(date.today()),
        "sabor": dict(escolhido),
        "descricao": f"Hoje é dia de {escolhido['nome']}! 🍦 Aproveite esse sabor especial do dia.",
    })


# ── Cardápio com info nutricional ─────────────────────────────────────────────

# Static nutritional data keyed by lower-case flavor name (kcal per scoop ~100g)
_NUTRICIONAL = {
    "chocolate": {"calorias": 216, "proteinas": 4.0, "carboidratos": 28, "gorduras": 10, "fibras": 1.2},
    "morango":   {"calorias": 127, "proteinas": 2.5, "carboidratos": 22, "gorduras": 4,  "fibras": 0.6},
    "baunilha":  {"calorias": 207, "proteinas": 3.5, "carboidratos": 24, "gorduras": 11, "fibras": 0.0},
    "pistache":  {"calorias": 230, "proteinas": 5.0, "carboidratos": 22, "gorduras": 14, "fibras": 1.5},
    "limão":     {"calorias": 110, "proteinas": 2.0, "carboidratos": 20, "gorduras": 3,  "fibras": 0.3},
}

_ALERGENOS = {
    "chocolate": ["leite", "glúten", "amendoim"],
    "morango":   ["leite"],
    "baunilha":  ["leite", "ovos"],
    "pistache":  ["leite", "nozes"],
    "limão":     ["leite"],
}


@api_bp.get("/cardapio")
def cardapio():
    """Return the full menu enriched with nutritional info and allergens."""
    sabores = sabor_model.listar_sabores()
    resultado = []
    for s in sabores:
        chave = s["nome"].lower()
        resultado.append({
            **dict(s),
            "nutricional": _NUTRICIONAL.get(chave, {}),
            "alergenos": _ALERGENOS.get(chave, []),
        })
    return jsonify(resultado)


@api_bp.get("/cardapio/<int:sabor_id>")
def cardapio_sabor(sabor_id):
    """Return a single flavor enriched with nutritional info."""
    sabores = sabor_model.listar_sabores()
    sabor = next((s for s in sabores if s["id"] == sabor_id), None)
    if not sabor:
        return jsonify({"error": "Sabor não encontrado"}), 404
    chave = sabor["nome"].lower()
    return jsonify({
        **dict(sabor),
        "nutricional": _NUTRICIONAL.get(chave, {}),
        "alergenos": _ALERGENOS.get(chave, []),
    })

