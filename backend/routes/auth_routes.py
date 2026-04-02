"""Auth blueprint — /api/auth/*"""

from flask import Blueprint, jsonify, request

from backend.models.user import autenticar_usuario, buscar_usuario_por_id, criar_usuario
from backend.auth.jwt_handler import generate_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _is_valid_email(email: str) -> bool:
    """Basic email validation without backtracking-prone regex."""
    if not email or len(email) > 254:
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    local, domain = parts
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email e password são obrigatórios"}), 400
    if not _is_valid_email(email):
        return jsonify({"error": "E-mail inválido"}), 400
    if len(password) < 8:
        return jsonify({"error": "password deve ter no mínimo 8 caracteres"}), 400

    try:
        user = criar_usuario(name, email, password)
    except Exception as e:
        err = str(e)
        if "unique" in err.lower() or "duplicate" in err.lower():
            return jsonify({"error": "E-mail já cadastrado"}), 409
        return jsonify({"error": "Erro ao criar usuário"}), 500

    token = generate_token(user["id"], user["email"])
    return jsonify({"token": token, "user": dict(user)}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email e password são obrigatórios"}), 400

    user = autenticar_usuario(email, password)
    if not user:
        return jsonify({"error": "Credenciais inválidas"}), 401

    token = generate_token(user["id"], user["email"])
    return jsonify({
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "level": user["level"],
            "total_points": user["total_points"],
        },
    })


@auth_bp.get("/me")
@token_required
def me(current_user):
    user = buscar_usuario_por_id(current_user["id"])
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(dict(user))
