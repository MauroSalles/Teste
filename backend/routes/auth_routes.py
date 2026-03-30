from flask import Blueprint, request, jsonify

from backend.models.user import criar_usuario, autenticar_usuario
from backend.auth.jwt_handler import generate_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user. Body: {name, email, password}"""
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Os campos 'name', 'email' e 'password' são obrigatórios."}), 400
    if len(password) < 6:
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres."}), 400

    try:
        user = criar_usuario(name, email, password)
    except Exception as e:
        msg = str(e)
        if "unique" in msg.lower() or "duplicate" in msg.lower():
            return jsonify({"error": "E-mail já cadastrado."}), 409
        return jsonify({"error": "Erro ao criar usuário."}), 500

    token = generate_token(user["id"], user["email"])
    return jsonify({"token": token, "user": dict(user)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user. Body: {email, password}"""
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Os campos 'email' e 'password' são obrigatórios."}), 400

    try:
        user, err = autenticar_usuario(email, password)
    except Exception:
        return jsonify({"error": "Erro interno."}), 500

    if err:
        return jsonify({"error": err}), 401

    token = generate_token(user["id"], user["email"])
    return jsonify({"token": token, "user": user}), 200
