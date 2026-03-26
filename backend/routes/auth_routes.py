"""Auth routes — register, login, refresh, logout, profile."""

import re
import logging
from flask import Blueprint, jsonify, request, g

from backend.models.usuario import (
    criar_usuario,
    buscar_usuario_por_email,
    buscar_usuario_por_id,
    verificar_senha,
)
from backend.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    blacklist_token,
    is_blacklisted,
    require_auth,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""

    if not nome or not email or not senha:
        return jsonify({"error": "nome, email e senha são obrigatórios."}), 400
    if not _EMAIL_RE.match(email):
        return jsonify({"error": "E-mail inválido."}), 400
    if len(senha) < 8:
        return jsonify({"error": "A senha deve ter pelo menos 8 caracteres."}), 400

    existing = buscar_usuario_por_email(email)
    if existing:
        return jsonify({"error": "E-mail já cadastrado."}), 409

    try:
        user = criar_usuario(nome, email, senha)
    except Exception as exc:
        logger.exception("Erro ao criar usuário: %s", exc)
        return jsonify({"error": "Erro interno ao criar usuário."}), 500

    access = create_access_token(user["id"], user["role"])
    refresh = create_refresh_token(user["id"])
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "user": {"id": user["id"], "nome": user["nome"], "email": user["email"], "role": user["role"]},
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""

    if not email or not senha:
        return jsonify({"error": "email e senha são obrigatórios."}), 400

    user = buscar_usuario_por_email(email)
    if not user or not verificar_senha(senha, user["senha_hash"]):
        return jsonify({"error": "Credenciais inválidas."}), 401

    access = create_access_token(user["id"], user["role"])
    refresh = create_refresh_token(user["id"])
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "user": {"id": user["id"], "nome": user["nome"], "email": user["email"], "role": user["role"]},
    })


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json(silent=True) or {}
    token = data.get("refresh_token") or ""
    if not token:
        return jsonify({"error": "refresh_token é obrigatório."}), 400
    if is_blacklisted(token):
        return jsonify({"error": "Token inválido."}), 401
    try:
        import jwt as pyjwt
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return jsonify({"error": "Tipo de token inválido."}), 401
    except Exception:
        return jsonify({"error": "Token inválido ou expirado."}), 401

    user_id = payload["sub"]
    user = buscar_usuario_por_id(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado."}), 404

    blacklist_token(token)
    new_access = create_access_token(user["id"], user["role"])
    new_refresh = create_refresh_token(user["id"])
    return jsonify({"access_token": new_access, "refresh_token": new_refresh})


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        blacklist_token(auth[7:])
    data = request.get_json(silent=True) or {}
    rt = data.get("refresh_token")
    if rt:
        blacklist_token(rt)
    return jsonify({"message": "Logout efetuado com sucesso."})


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    user = buscar_usuario_por_id(g.user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado."}), 404
    return jsonify({
        "id": user["id"],
        "nome": user["nome"],
        "email": user["email"],
        "role": user["role"],
        "criado_em": user["criado_em"].isoformat() if user.get("criado_em") else None,
    })
