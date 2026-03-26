from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from backend.models.cliente import (
    listar_clientes,
    adicionar_cliente,
    adicionar_pontos,
    segmentacao_clientes,
    top_clientes,
)
from backend.models.ingrediente import (
    listar_ingredientes,
    adicionar_ingrediente,
    ingredientes_em_alerta,
)
from backend.models.financeiro import (
    kpis_gerais,
    top_sabores,
    faturamento_por_periodo,
    caixa_atual,
    listar_despesas,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ── Dashboard ─────────────────────────────────────────────────────────────────

@api_bp.route("/dashboard/kpis", methods=["GET"])
def dashboard_kpis():
    kpis = kpis_gerais()
    tops = top_sabores(5)
    alertas = ingredientes_em_alerta()
    caixa = caixa_atual()
    return jsonify({
        "kpis": {
            "total_pedidos":      int(kpis["total_pedidos"]),
            "faturamento_total":  float(kpis["faturamento_total"]),
            "ticket_medio":       round(float(kpis["ticket_medio"]), 2),
            "faturamento_hoje":   float(kpis["faturamento_hoje"]),
            "pedidos_hoje":       int(kpis["pedidos_hoje"]),
            "faturamento_mes":    float(kpis["faturamento_mes"]),
        },
        "top_sabores": [
            {
                "id":               int(s["id"]),
                "nome":             s["nome"],
                "preco":            float(s["preco"]),
                "unidades_vendidas": int(s["unidades_vendidas"]),
                "faturamento":      float(s["faturamento"]),
            }
            for s in tops
        ],
        "alertas_ingredientes": len(alertas),
        "caixa_aberta":          caixa is not None,
    })


# ── Analytics ─────────────────────────────────────────────────────────────────

@api_bp.route("/analytics/top-sabores", methods=["GET"])
def analytics_top_sabores():
    limite = min(int(request.args.get("limite", 5)), 20)
    tops = top_sabores(limite)
    return jsonify([
        {
            "id":               int(s["id"]),
            "nome":             s["nome"],
            "preco":            float(s["preco"]),
            "unidades_vendidas": int(s["unidades_vendidas"]),
            "faturamento":      float(s["faturamento"]),
        }
        for s in tops
    ])


@api_bp.route("/relatorios/faturamento", methods=["GET"])
def relatorio_faturamento():
    try:
        inicio = date.fromisoformat(request.args.get("inicio", str(date.today() - timedelta(days=30))))
        fim    = date.fromisoformat(request.args.get("fim",    str(date.today())))
    except ValueError:
        return jsonify({"erro": "Datas inválidas. Use o formato YYYY-MM-DD."}), 400

    dados = faturamento_por_periodo(inicio, fim)
    return jsonify([
        {
            "dia":         str(d["dia"]),
            "pedidos":     int(d["pedidos"]),
            "unidades":    int(d["unidades"]),
            "faturamento": float(d["faturamento"]),
        }
        for d in dados
    ])


# ── Clientes ──────────────────────────────────────────────────────────────────

@api_bp.route("/clientes", methods=["GET"])
def get_clientes():
    clientes = listar_clientes()
    return jsonify([dict(c) for c in clientes])


@api_bp.route("/clientes", methods=["POST"])
def post_cliente():
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"erro": "Campo 'nome' é obrigatório."}), 400
    nome     = str(data["nome"])[:100]
    email    = str(data.get("email", "") or "")[:100] or None
    telefone = str(data.get("telefone", "") or "")[:20] or None
    try:
        cliente = adicionar_cliente(nome, email, telefone)
    except Exception as exc:
        if "unique" in str(exc).lower():
            return jsonify({"erro": "E-mail já cadastrado."}), 409
        raise
    return jsonify(dict(cliente)), 201


@api_bp.route("/clientes/segmentacao", methods=["GET"])
def get_segmentacao():
    return jsonify([dict(s) for s in segmentacao_clientes()])


@api_bp.route("/clientes/top", methods=["GET"])
def get_top_clientes():
    limite = min(int(request.args.get("limite", 5)), 20)
    return jsonify([dict(c) for c in top_clientes(limite)])


@api_bp.route("/fidelidade/pontos", methods=["POST"])
def post_pontos():
    data = request.get_json()
    if not data or "cliente_id" not in data or "pontos" not in data:
        return jsonify({"erro": "Campos 'cliente_id' e 'pontos' são obrigatórios."}), 400
    try:
        cliente_id = int(data["cliente_id"])
        pontos     = int(data["pontos"])
        if pontos <= 0:
            return jsonify({"erro": "Pontos devem ser positivos."}), 400
    except (TypeError, ValueError):
        return jsonify({"erro": "Valores inválidos."}), 400

    cliente = adicionar_pontos(cliente_id, pontos)
    if not cliente:
        return jsonify({"erro": f"Cliente ID {cliente_id} não encontrado."}), 404
    return jsonify(dict(cliente))


# ── Ingredientes ──────────────────────────────────────────────────────────────

@api_bp.route("/ingredientes", methods=["GET"])
def get_ingredientes():
    return jsonify([dict(i) for i in listar_ingredientes()])


@api_bp.route("/ingredientes", methods=["POST"])
def post_ingrediente():
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"erro": "Campo 'nome' é obrigatório."}), 400
    nome     = str(data["nome"])[:100]
    unidade  = str(data.get("unidade", "kg"))[:20]
    try:
        preco    = float(data.get("preco_unitario", 0))
        qtd_min  = float(data.get("quantidade_minima", 0))
        if preco < 0 or qtd_min < 0:
            return jsonify({"erro": "Valores não podem ser negativos."}), 400
    except (TypeError, ValueError):
        return jsonify({"erro": "Valores inválidos."}), 400

    ingrediente = adicionar_ingrediente(nome, unidade, preco, qtd_min)
    return jsonify(dict(ingrediente)), 201


@api_bp.route("/ingredientes/alerta", methods=["GET"])
def get_alertas_ingredientes():
    alertas = ingredientes_em_alerta()
    return jsonify([dict(a) for a in alertas])


# ── Caixa ─────────────────────────────────────────────────────────────────────

@api_bp.route("/caixa/atual", methods=["GET"])
def get_caixa_atual():
    caixa = caixa_atual()
    if caixa:
        despesas = listar_despesas(int(caixa["id"]))
        total_desp = sum(float(d["valor"]) for d in despesas)
        return jsonify({**dict(caixa), "despesas": [dict(d) for d in despesas], "total_despesas": total_desp})
    return jsonify({"status": "fechado"})
