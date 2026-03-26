"""REST API routes — sabores, pedidos, estoque, dashboard."""

import logging
from flask import Blueprint, jsonify, request

from backend.models.sabor import (
    listar_sabores,
    adicionar_sabor,
    atualizar_sabor,
    remover_sabor,
    buscar_sabor_por_nome,
)
from backend.models.pedido import listar_pedidos, criar_pedido
from backend.models.estoque import ver_estoque, definir_estoque, ajustar_estoque, obter_estoque
from backend.auth.jwt_handler import require_auth, require_admin

api_bp = Blueprint("api", __name__, url_prefix="/api")
logger = logging.getLogger(__name__)


# ── Sabores ────────────────────────────────────────────────────────────────────

@api_bp.route("/sabores", methods=["GET"])
def get_sabores():
    sabores = listar_sabores()
    return jsonify([dict(s) for s in sabores])


@api_bp.route("/sabores", methods=["POST"])
@require_admin
def post_sabor():
    data = request.get_json(silent=True) or {}
    nome = (data.get("nome") or "").strip()
    preco = data.get("preco")

    if not nome:
        return jsonify({"error": "nome é obrigatório."}), 400
    try:
        preco = float(preco)
        if preco < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "preco deve ser um número não-negativo."}), 400

    sabor = adicionar_sabor(nome, preco)
    return jsonify(dict(sabor)), 201


@api_bp.route("/sabores/<int:sabor_id>", methods=["PUT"])
@require_admin
def put_sabor(sabor_id: int):
    data = request.get_json(silent=True) or {}
    preco = data.get("preco")
    try:
        preco = float(preco)
        if preco < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "preco deve ser um número não-negativo."}), 400

    sabor = atualizar_sabor(sabor_id, preco)
    if not sabor:
        return jsonify({"error": "Sabor não encontrado."}), 404
    return jsonify(dict(sabor))


@api_bp.route("/sabores/<int:sabor_id>", methods=["DELETE"])
@require_admin
def delete_sabor(sabor_id: int):
    sabor = remover_sabor(sabor_id)
    if not sabor:
        return jsonify({"error": "Sabor não encontrado."}), 404
    return jsonify({"message": f"Sabor '{sabor['nome']}' removido com sucesso."})


# ── Pedidos ────────────────────────────────────────────────────────────────────

@api_bp.route("/pedidos", methods=["GET"])
@require_auth
def get_pedidos():
    pedidos = listar_pedidos()
    return jsonify([
        {
            "id": p["id"],
            "sabor": p["sabor"],
            "quantidade": p["quantidade"],
            "data": p["data"].isoformat(),
        }
        for p in pedidos
    ])


@api_bp.route("/pedidos", methods=["POST"])
def post_pedido():
    data = request.get_json(silent=True) or {}
    sabor_nome = (data.get("sabor") or "").strip()
    quantidade = data.get("quantidade")

    if not sabor_nome:
        return jsonify({"error": "sabor é obrigatório."}), 400
    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "quantidade deve ser um inteiro positivo."}), 400

    sabor = buscar_sabor_por_nome(sabor_nome)
    if not sabor:
        return jsonify({"error": f"Sabor '{sabor_nome}' não encontrado."}), 404

    estoque_atual = obter_estoque(sabor["id"])
    if estoque_atual > 0 and quantidade > estoque_atual:
        return jsonify({
            "error": f"Estoque insuficiente. Disponível: {estoque_atual}, Solicitado: {quantidade}"
        }), 409

    pedido = criar_pedido(sabor["id"], quantidade)
    if estoque_atual > 0:
        ajustar_estoque(sabor["id"], -quantidade)

    total = float(sabor["preco"]) * quantidade
    return jsonify({
        "id": pedido["id"],
        "sabor": sabor["nome"],
        "quantidade": quantidade,
        "preco_unitario": float(sabor["preco"]),
        "total": total,
        "data": pedido["data"].isoformat(),
    }), 201


# ── Estoque ────────────────────────────────────────────────────────────────────

@api_bp.route("/estoque", methods=["GET"])
def get_estoque():
    itens = ver_estoque()
    return jsonify([dict(i) for i in itens])


@api_bp.route("/estoque/<int:sabor_id>", methods=["PUT"])
@require_admin
def put_estoque(sabor_id: int):
    data = request.get_json(silent=True) or {}
    quantidade = data.get("quantidade")
    try:
        quantidade = int(quantidade)
        if quantidade < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "quantidade deve ser um inteiro não-negativo."}), 400

    item = definir_estoque(sabor_id, quantidade)
    return jsonify(dict(item))


# ── Dashboard ──────────────────────────────────────────────────────────────────

@api_bp.route("/dashboard", methods=["GET"])
@require_admin
def get_dashboard():
    from backend.database import get_db
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM sabores")
            total_sabores = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) AS total FROM pedidos")
            total_pedidos = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT COALESCE(SUM(p.quantidade * s.preco), 0) AS receita
                FROM pedidos p JOIN sabores s ON s.id = p.sabor_id
                """
            )
            receita_total = float(cur.fetchone()["receita"])

            cur.execute(
                """
                SELECT COALESCE(SUM(p.quantidade * s.preco), 0) AS receita
                FROM pedidos p JOIN sabores s ON s.id = p.sabor_id
                WHERE p.data >= CURRENT_DATE
                """
            )
            receita_hoje = float(cur.fetchone()["receita"])

            cur.execute(
                """
                SELECT s.nome, SUM(p.quantidade) AS total_vendido
                FROM pedidos p JOIN sabores s ON s.id = p.sabor_id
                GROUP BY s.nome
                ORDER BY total_vendido DESC
                LIMIT 5
                """
            )
            top_sabores = [dict(r) for r in cur.fetchall()]

            cur.execute(
                """
                SELECT DATE(p.data) AS dia, SUM(p.quantidade * s.preco) AS receita
                FROM pedidos p JOIN sabores s ON s.id = p.sabor_id
                WHERE p.data >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(p.data)
                ORDER BY dia
                """
            )
            vendas_semana = [
                {"dia": str(r["dia"]), "receita": float(r["receita"])}
                for r in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT COUNT(*) AS sem_estoque
                FROM sabores s
                LEFT JOIN estoque e ON e.sabor_id = s.id
                WHERE COALESCE(e.quantidade, 0) = 0
                """
            )
            sem_estoque = cur.fetchone()["sem_estoque"]

    return jsonify({
        "total_sabores": total_sabores,
        "total_pedidos": total_pedidos,
        "receita_total": receita_total,
        "receita_hoje": receita_hoje,
        "top_sabores": top_sabores,
        "vendas_semana": vendas_semana,
        "sabores_sem_estoque": sem_estoque,
    })
