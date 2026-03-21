from flask import Blueprint, jsonify, request
from backend.services.cmd_service import processar_comando

cmd_bp = Blueprint("cmd", __name__)

MAX_COMMAND_LENGTH = 500


@cmd_bp.route("/cmd", methods=["POST"])
def cmd():
    data = request.get_json()
    if not data or "comando" not in data:
        return jsonify({"resposta": "Requisição inválida. Envie JSON com campo 'comando'."}), 400
    comando = data["comando"]
    if not isinstance(comando, str):
        return jsonify({"resposta": "O campo 'comando' deve ser uma string."}), 400
    if len(comando) > MAX_COMMAND_LENGTH:
        return jsonify({"resposta": f"Comando muito longo (máximo {MAX_COMMAND_LENGTH} caracteres)."}), 400
    resposta = processar_comando(comando)
    return jsonify({"resposta": resposta})
