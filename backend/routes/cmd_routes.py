"""CMD-style command router for the Gelateria System."""
import re
from flask import Blueprint, request, jsonify
from services import (
    listar_sabores,
    adicionar_sabor,
    remover_sabor,
    listar_pedidos,
    fazer_pedido,
    listar_estoque,
    atualizar_estoque,
)

cmd_bp = Blueprint("cmd", __name__)

HELP_TEXT = """Comandos disponíveis:
  ajuda                              - Exibe esta mensagem
  listar sabores                     - Lista todos os sabores
  add sabor <nome> <preco>           - Adiciona um novo sabor
  remover sabor <id>                 - Remove um sabor pelo ID
  listar pedidos                     - Lista todos os pedidos
  fazer pedido <cliente> <sabor> <qtd> - Cria um novo pedido
  listar estoque                     - Mostra o estoque atual
  atualizar estoque <sabor> <qtd>    - Atualiza quantidade no estoque"""


def _format_sabores(rows):
    if not rows:
        return "Nenhum sabor cadastrado."
    lines = ["ID  | Nome            | Preço    | Disponível",
             "----|-----------------|----------|----------"]
    for r in rows:
        disp = "Sim" if r["disponivel"] else "Não"
        lines.append(f"{r['id']:<4}| {r['nome']:<16}| R${r['preco']:<7.2f}| {disp}")
    return "\n".join(lines)


def _format_pedidos(rows):
    if not rows:
        return "Nenhum pedido encontrado."
    lines = ["ID  | Cliente         | Sabor           | Qtd | Total   | Status",
             "----|-----------------|-----------------|-----|---------|--------"]
    for r in rows:
        lines.append(
            f"{r['id']:<4}| {str(r['cliente']):<16}| {str(r['sabor']):<16}| "
            f"{r['quantidade']:<4}| R${r['total']:<6.2f}| {r['status']}"
        )
    return "\n".join(lines)


def _format_estoque(rows):
    if not rows:
        return "Estoque vazio."
    lines = ["Nome            | Qtd  | Preço",
             "----------------|------|-------"]
    for r in rows:
        lines.append(f"{r['nome']:<16}| {r['quantidade']:<5}| R${r['preco']:.2f}")
    return "\n".join(lines)


@cmd_bp.route("/cmd", methods=["POST"])
def cmd():
    body = request.get_json(silent=True) or {}
    comando = (body.get("comando") or "").strip().lower()

    if not comando:
        return jsonify({"resposta": "Digite um comando. Use 'ajuda' para ver os disponíveis."})

    # ajuda
    if comando in ("ajuda", "help", "?"):
        return jsonify({"resposta": HELP_TEXT})

    # listar sabores
    if comando == "listar sabores":
        rows = listar_sabores()
        return jsonify({"resposta": _format_sabores(rows)})

    # add sabor <nome> <preco>
    m = re.fullmatch(r"add sabor\s+(.+)\s+([\d,.]+)", comando)
    if m:
        nome = m.group(1).strip().title()
        preco_str = m.group(2).replace(",", ".")
        try:
            preco = float(preco_str)
        except ValueError:
            return jsonify({"resposta": "Preço inválido. Ex: add sabor Manga 9.50"})
        sabor = adicionar_sabor(nome, preco)
        return jsonify({"resposta": f"Sabor '{sabor['nome']}' adicionado com sucesso! (ID: {sabor['id']})"})

    # remover sabor <id>
    m = re.fullmatch(r"remover sabor\s+(\d+)", comando)
    if m:
        resultado = remover_sabor(int(m.group(1)))
        if resultado:
            return jsonify({"resposta": f"Sabor '{resultado['nome']}' removido com sucesso!"})
        return jsonify({"resposta": "Sabor não encontrado."})

    # listar pedidos
    if comando == "listar pedidos":
        rows = listar_pedidos()
        return jsonify({"resposta": _format_pedidos(rows)})

    # fazer pedido <cliente> <sabor> <quantidade>
    # Client name is greedy (can contain spaces); flavor is last word before the integer qty.
    m = re.fullmatch(r"fazer pedido\s+(.+)\s+(\S+)\s+(\d+)", comando)
    if m:
        cliente = m.group(1).strip().title()
        sabor = m.group(2).strip().title()
        quantidade = int(m.group(3))
        pedido, erro = fazer_pedido(cliente, sabor, quantidade)
        if erro:
            return jsonify({"resposta": f"Erro: {erro}"})
        return jsonify({
            "resposta": f"Pedido #{pedido['id']} criado! Total: R${pedido['total']:.2f}"
        })

    # listar estoque
    if comando == "listar estoque":
        rows = listar_estoque()
        return jsonify({"resposta": _format_estoque(rows)})

    # atualizar estoque <sabor> <quantidade>
    m = re.fullmatch(r"atualizar estoque\s+(.+)\s+(\d+)", comando)
    if m:
        sabor = m.group(1).strip().title()
        quantidade = int(m.group(2))
        resultado, erro = atualizar_estoque(sabor, quantidade)
        if erro:
            return jsonify({"resposta": f"Erro: {erro}"})
        return jsonify({"resposta": f"Estoque de '{sabor}' atualizado para {resultado['quantidade']} unidades."})

    return jsonify({"resposta": f"Comando não reconhecido: '{comando}'. Use 'ajuda' para ver os disponíveis."})
