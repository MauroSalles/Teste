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

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ── Sabores ──────────────────────────────────────────────────────────────────

@api_bp.route("/sabores", methods=["GET"])
def get_sabores():
    return jsonify([dict(s) for s in listar_sabores()])


@api_bp.route("/sabores", methods=["POST"])
def post_sabor():
    data = request.get_json()
    if not data or "nome" not in data or "preco" not in data:
        return jsonify({"error": "nome e preco são obrigatórios"}), 400
    nome = str(data["nome"]).strip()
    if not nome:
        return jsonify({"error": "nome não pode ser vazio"}), 400
    try:
        preco = float(data["preco"])
        if preco < 0:
            return jsonify({"error": "Preço não pode ser negativo"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Preço inválido"}), 400
    sabor = adicionar_sabor(nome, preco)
    return jsonify(dict(sabor)), 201


@api_bp.route("/sabores/<int:sabor_id>", methods=["PUT"])
def put_sabor(sabor_id):
    data = request.get_json()
    if not data or "preco" not in data:
        return jsonify({"error": "preco é obrigatório"}), 400
    try:
        preco = float(data["preco"])
        if preco < 0:
            return jsonify({"error": "Preço não pode ser negativo"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Preço inválido"}), 400
    sabor = atualizar_sabor(sabor_id, preco)
    if not sabor:
        return jsonify({"error": "Sabor não encontrado"}), 404
    return jsonify(dict(sabor))


@api_bp.route("/sabores/<int:sabor_id>", methods=["DELETE"])
def delete_sabor(sabor_id):
    sabor = remover_sabor(sabor_id)
    if not sabor:
        return jsonify({"error": "Sabor não encontrado"}), 404
    return jsonify({"message": f"Sabor '{sabor['nome']}' removido com sucesso"})


# ── Pedidos ───────────────────────────────────────────────────────────────────

@api_bp.route("/pedidos", methods=["GET"])
def get_pedidos():
    pedidos = listar_pedidos()
    result = [
        {
            "id": p["id"],
            "sabor": p["sabor"],
            "quantidade": p["quantidade"],
            "data": p["data"].isoformat() if p["data"] else None,
        }
        for p in pedidos
    ]
    return jsonify(result)


@api_bp.route("/pedidos", methods=["POST"])
def post_pedido():
    data = request.get_json()
    if not data or "sabor_nome" not in data or "quantidade" not in data:
        return jsonify({"error": "sabor_nome e quantidade são obrigatórios"}), 400
    try:
        quantidade = int(data["quantidade"])
        if quantidade <= 0:
            return jsonify({"error": "Quantidade deve ser maior que zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Quantidade inválida"}), 400
    sabor = buscar_sabor_por_nome(str(data["sabor_nome"]).strip())
    if not sabor:
        return jsonify({"error": f"Sabor '{data['sabor_nome']}' não encontrado"}), 404
    estoque_atual = obter_estoque(sabor["id"])
    if estoque_atual > 0 and quantidade > estoque_atual:
        return jsonify({"error": f"Estoque insuficiente. Disponível: {estoque_atual}"}), 422
    pedido = criar_pedido(sabor["id"], quantidade)
    if estoque_atual > 0:
        ajustar_estoque(sabor["id"], -quantidade)
    return jsonify(
        {
            "id": pedido["id"],
            "sabor": sabor["nome"],
            "quantidade": quantidade,
            "total": float(sabor["preco"]) * quantidade,
        }
    ), 201


# ── Estoque ───────────────────────────────────────────────────────────────────

@api_bp.route("/estoque", methods=["GET"])
def get_estoque():
    return jsonify([dict(i) for i in ver_estoque()])


@api_bp.route("/estoque/<int:sabor_id>", methods=["PUT"])
def put_estoque(sabor_id):
    data = request.get_json()
    if not data or "quantidade" not in data:
        return jsonify({"error": "quantidade é obrigatória"}), 400
    try:
        qtd = int(data["quantidade"])
        if qtd < 0:
            return jsonify({"error": "Quantidade não pode ser negativa"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Quantidade inválida"}), 400
    result = definir_estoque(sabor_id, qtd)
    return jsonify(dict(result))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@api_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    sabores = listar_sabores()
    pedidos = listar_pedidos()
    itens = ver_estoque()

    total_sabores = len(sabores)
    total_pedidos = len(pedidos)

    sabor_preco = {s["nome"]: float(s["preco"]) for s in sabores}
    total_receita = sum(
        sabor_preco.get(p["sabor"], 0) * p["quantidade"] for p in pedidos
    )

    contagem: dict[str, int] = {}
    for p in pedidos:
        contagem[p["sabor"]] = contagem.get(p["sabor"], 0) + p["quantidade"]
    top_sabores = sorted(contagem.items(), key=lambda x: x[1], reverse=True)[:5]

    sem_estoque = [i for i in itens if int(i["quantidade"]) == 0]
    estoque_baixo = [i for i in itens if 0 < int(i["quantidade"]) <= 5]

    return jsonify(
        {
            "total_sabores": total_sabores,
            "total_pedidos": total_pedidos,
            "total_receita": round(total_receita, 2),
            "ticket_medio": round(total_receita / total_pedidos, 2) if total_pedidos > 0 else 0,
            "top_sabores": [{"nome": nome, "quantidade": qtd} for nome, qtd in top_sabores],
            "sem_estoque": len(sem_estoque),
            "estoque_baixo": len(estoque_baixo),
            "alertas_estoque": [
                {"nome": i["nome"], "quantidade": int(i["quantidade"])}
                for i in sem_estoque + estoque_baixo
            ],
        }
    )
