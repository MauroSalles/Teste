"""REST API blueprint — /api/*"""

from flask import Blueprint, jsonify, request

import backend.models.sabor as sabor_model
import backend.models.pedido as pedido_model
import backend.models.estoque as estoque_model
import backend.models.estoque_sabores as estoque_sabores_model
from backend.models.fidelidade import (
    obter_pontos,
    adicionar_pontos,
    resgatar,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ── Sabores ──────────────────────────────────────────────────────────────────

@api_bp.get("/sabores")
def listar_sabores():
    page = request.args.get("page", None, type=int)
    per_page = request.args.get("per_page", None, type=int)
    sabores = sabor_model.listar_sabores(page=page, per_page=per_page)
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
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    page = max(1, page)
    per_page = max(1, min(per_page, 100))
    pedidos = pedido_model.listar_pedidos(page=page, per_page=per_page)
    return jsonify([dict(p) for p in pedidos])


@api_bp.get("/pedidos/<int:pedido_id>")
def obter_pedido(pedido_id):
    pedido = pedido_model.obter_pedido(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404
    return jsonify(dict(pedido))


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

    metodo = (data.get("metodo_pagamento") or "dinheiro").strip().lower()
    if metodo not in pedido_model.METODOS_PAGAMENTO:
        return jsonify({"error": f"metodo_pagamento deve ser um de: {', '.join(pedido_model.METODOS_PAGAMENTO)}"}), 400

    observacao = (data.get("observacao") or "").strip() or None

    pedido = pedido_model.criar_pedido(sabor_id, quantidade, metodo, observacao)
    if not pedido:
        return jsonify({"error": "Sabor não encontrado"}), 404
    return jsonify(dict(pedido)), 201


@api_bp.put("/pedidos/<int:pedido_id>")
def atualizar_pedido(pedido_id):
    """Edit an order — change quantity, payment method, status, or add notes."""
    data = request.get_json(silent=True) or {}
    quantidade = data.get("quantidade")
    metodo = data.get("metodo_pagamento")
    status = data.get("status")
    observacao = data.get("observacao")

    if quantidade is not None:
        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            return jsonify({"error": "quantidade deve ser um inteiro positivo"}), 400

    if metodo is not None:
        metodo = metodo.strip().lower()
        if metodo not in pedido_model.METODOS_PAGAMENTO:
            return jsonify({"error": f"metodo_pagamento deve ser um de: {', '.join(pedido_model.METODOS_PAGAMENTO)}"}), 400

    if status is not None:
        status = status.strip().lower()
        if status not in pedido_model.STATUS_PEDIDO:
            return jsonify({"error": f"status deve ser um de: {', '.join(pedido_model.STATUS_PEDIDO)}"}), 400

    pedido = pedido_model.atualizar_pedido(
        pedido_id, quantidade=quantidade, metodo_pagamento=metodo,
        status=status, observacao=observacao
    )
    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404
    return jsonify(dict(pedido))


@api_bp.delete("/pedidos/<int:pedido_id>")
def cancelar_pedido(pedido_id):
    """Cancel an order (marks as 'cancelado')."""
    pedido = pedido_model.cancelar_pedido(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido não encontrado"}), 404
    return jsonify({"message": "Pedido cancelado com sucesso", "pedido": dict(pedido)})


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


# ── Estoque Self-Service (estoque_sabores) ────────────────────────────────────

@api_bp.get("/estoque/sabores")
def listar_estoque_sabores():
    """List all self-service flavors with stock levels, categories, and alerts."""
    rows = estoque_sabores_model.listar_estoque_sabores()
    return jsonify([dict(r) for r in rows])


@api_bp.get("/estoque/sabores/resumo")
def resumo_estoque_sabores():
    """Summary of self-service inventory — totals, alerts, category breakdown."""
    rows = estoque_sabores_model.listar_estoque_sabores()
    flavors = [dict(r) for r in rows]
    acai = [f for f in flavors if f["categoria"] == "açaí"]
    sorvete = [f for f in flavors if f["categoria"] == "sorvete"]
    faltando = [f for f in flavors if f["estoque_minimo_sugestao"] > 0 and f["quantidade_atual"] < f["estoque_minimo_sugestao"]]
    rapida = [f for f in flavors if f["resposicao_rapida"]]
    return jsonify({
        "total": len(flavors),
        "acai": len(acai),
        "sorvete": len(sorvete),
        "faltando": len(faltando),
        "reposicao_rapida": len(rapida),
        "itens_faltando": faltando,
        "itens_reposicao_rapida": rapida,
    })


@api_bp.get("/estoque/faltando")
def estoque_faltando():
    rows = estoque_sabores_model.listar_faltando()
    return jsonify([dict(r) for r in rows])


@api_bp.post("/estoque/pedido-semanal")
def pedido_semanal():
    data = request.get_json(silent=True) or {}
    itens = data.get("itens")
    observacao = data.get("observacao")
    if not isinstance(itens, list) or not itens:
        return jsonify({"error": "itens deve ser uma lista não-vazia"}), 400
    for item in itens:
        if not isinstance(item, dict):
            return jsonify({"error": "cada item deve ser um objeto"}), 400
        try:
            int(item["estoque_sabor_id"])
            q = int(item["quantidade"])
            if q <= 0:
                raise ValueError("quantidade deve ser um inteiro positivo")
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "cada item requer estoque_sabor_id e quantidade (inteiro positivo)"}), 400
    row = estoque_sabores_model.registrar_pedido_semanal(itens, observacao)
    return jsonify(dict(row)), 201


@api_bp.post("/estoque/atualizar")
def atualizar_estoque():
    data = request.get_json(silent=True) or {}
    itens = data.get("itens")
    if not isinstance(itens, list) or not itens:
        return jsonify({"error": "itens deve ser uma lista não-vazia"}), 400
    for item in itens:
        if not isinstance(item, dict):
            return jsonify({"error": "cada item deve ser um objeto"}), 400
        try:
            int(item["estoque_sabor_id"])
            q = int(item["quantidade"])
            if q <= 0:
                raise ValueError("quantidade deve ser um inteiro positivo")
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "cada item requer estoque_sabor_id e quantidade (inteiro positivo)"}), 400
    updated = estoque_sabores_model.registrar_remessa(itens)
    return jsonify([dict(r) for r in updated])


# ── Status / Dashboard summary ────────────────────────────────────────────────

@api_bp.get("/status")
def status():
    sabores = sabor_model.listar_sabores()
    pedidos = pedido_model.listar_pedidos()
    estoque = estoque_model.ver_estoque()
    # Build O(1) lookup by name to avoid O(N²) scan per order
    preco_por_nome = {s["nome"]: float(s["preco"]) for s in sabores}
    receita = sum(
        float(p.get("quantidade", 0)) * preco_por_nome.get(p.get("sabor", ""), 0.0)
        for p in pedidos
        if p.get("status", "confirmado") != "cancelado"
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
