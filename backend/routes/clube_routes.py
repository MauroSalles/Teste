"""Clube de Assinatura blueprint — /api/clube/*

Monthly subscription tiers:
  - Bronze  R$19.90/month: 1 free flavor + 5% OFF
  - Prata   R$39.90/month: 2 free flavors + 10% OFF + free shipping
  - Ouro    R$69.90/month: weekly free flavor + 15% OFF + free shipping + early access
"""

import logging
from datetime import date
from dateutil.relativedelta import relativedelta  # type: ignore

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

try:
    from backend.database import get_db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

logger = logging.getLogger(__name__)

clube_bp = Blueprint("clube", __name__, url_prefix="/api/clube")

PLANOS = {
    "bronze": {
        "nome": "Bronze 🥉",
        "preco": 19.90,
        "descricao": "Perfeito para começar",
        "beneficios": [
            "1 sabor grátis por mês",
            "5% OFF em todos os pedidos",
            "Acesso ao painel de sócio",
        ],
        "desconto_percent": 5,
        "sabores_gratis_mes": 1,
        "frete_gratis": False,
        "acesso_antecipado": False,
    },
    "prata": {
        "nome": "Prata 🥈",
        "preco": 39.90,
        "descricao": "O favorito dos fãs de sorvete",
        "beneficios": [
            "2 sabores grátis por mês",
            "10% OFF em todos os pedidos",
            "Frete grátis",
            "Acesso ao painel de sócio",
        ],
        "desconto_percent": 10,
        "sabores_gratis_mes": 2,
        "frete_gratis": True,
        "acesso_antecipado": False,
    },
    "ouro": {
        "nome": "Ouro 🥇",
        "preco": 69.90,
        "descricao": "A experiência completa",
        "beneficios": [
            "Sabor grátis toda semana",
            "15% OFF em todos os pedidos",
            "Frete grátis",
            "Acesso antecipado a novos sabores",
            "Acesso ao painel de sócio",
        ],
        "desconto_percent": 15,
        "sabores_gratis_mes": 4,
        "frete_gratis": True,
        "acesso_antecipado": True,
    },
}


# ── Listar planos ─────────────────────────────────────────────────────────────

@clube_bp.get("/planos")
def listar_planos():
    """Return all available subscription plans."""
    return jsonify(list(PLANOS.values()))


# ── Assinar ───────────────────────────────────────────────────────────────────

@clube_bp.post("/assinar")
@token_required
def assinar(current_user):
    """Subscribe to a monthly plan."""
    user_id = current_user["id"]
    data = request.get_json(silent=True) or {}
    plano = (data.get("plano") or "").strip().lower()

    if plano not in PLANOS:
        return jsonify({"error": f"Plano inválido. Escolha: {', '.join(PLANOS)}"}), 400

    hoje = date.today()
    renovacao = hoje + relativedelta(months=1)

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO clube_assinaturas
                           (user_id, plano, status, data_inicio, data_renovacao)
                       VALUES (%s, %s, 'ativo', %s, %s)
                       ON CONFLICT (user_id)
                       DO UPDATE SET plano=%s, status='ativo',
                                     data_inicio=%s, data_renovacao=%s,
                                     beneficios_usados=0""",
                    (user_id, plano, hoje, renovacao, plano, hoje, renovacao),
                )
    except Exception as e:
        logger.error("Assinar error: %s", e)
        return jsonify({"error": "Erro ao assinar plano"}), 500

    return jsonify({
        "message": f"Bem-vindo ao plano {PLANOS[plano]['nome']}!",
        "plano": plano,
        "data_renovacao": str(renovacao),
    }), 201


# ── Meu plano ─────────────────────────────────────────────────────────────────

@clube_bp.get("/meu-plano")
@token_required
def meu_plano(current_user):
    """Return the current user's subscription details."""
    user_id = current_user["id"]
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM clube_assinaturas WHERE user_id=%s",
                    (user_id,),
                )
                row = cur.fetchone()
    except Exception as e:
        logger.error("Meu plano error: %s", e)
        return jsonify({"error": "Erro ao buscar plano"}), 500

    if not row:
        return jsonify({"plano": None, "message": "Você não possui assinatura ativa"}), 200

    row = dict(row)
    row["detalhes"] = PLANOS.get(row["plano"], {})
    row["data_inicio"] = str(row["data_inicio"])
    row["data_renovacao"] = str(row["data_renovacao"])
    return jsonify(row)


# ── Cancelar ──────────────────────────────────────────────────────────────────

@clube_bp.post("/cancelar")
@token_required
def cancelar(current_user):
    """Cancel subscription."""
    user_id = current_user["id"]
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE clube_assinaturas SET status='cancelado' WHERE user_id=%s",
                    (user_id,),
                )
    except Exception as e:
        logger.error("Cancelar error: %s", e)
        return jsonify({"error": "Erro ao cancelar assinatura"}), 500

    return jsonify({"message": "Assinatura cancelada. Esperamos te ver de volta em breve! 💙"})


# ── Benefícios ────────────────────────────────────────────────────────────────

@clube_bp.get("/beneficios")
@token_required
def listar_beneficios(current_user):
    """List redeemable benefits for this month."""
    user_id = current_user["id"]
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT plano, beneficios_usados FROM clube_assinaturas WHERE user_id=%s AND status='ativo'",
                    (user_id,),
                )
                row = cur.fetchone()
    except Exception as e:
        logger.warning("Beneficios error: %s", e)
        return jsonify({"error": "Erro ao buscar benefícios"}), 500

    if not row:
        return jsonify({"error": "Sem assinatura ativa"}), 403

    plano_key = row["plano"]
    plano_info = PLANOS.get(plano_key, {})
    total = plano_info.get("sabores_gratis_mes", 0)
    usados = row["beneficios_usados"]
    disponiveis = max(0, total - usados)

    return jsonify({
        "plano": plano_key,
        "sabores_gratis_mes": total,
        "beneficios_usados": usados,
        "disponiveis": disponiveis,
        "desconto_percent": plano_info.get("desconto_percent", 0),
        "frete_gratis": plano_info.get("frete_gratis", False),
    })


# ── Resgatar benefício ────────────────────────────────────────────────────────

@clube_bp.post("/resgatar/<int:beneficio_id>")
@token_required
def resgatar_beneficio(current_user, beneficio_id):
    """Redeem a monthly benefit (increments beneficios_usados)."""
    user_id = current_user["id"]
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT plano, beneficios_usados FROM clube_assinaturas WHERE user_id=%s AND status='ativo'",
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    return jsonify({"error": "Sem assinatura ativa"}), 403

                plano_info = PLANOS.get(row["plano"], {})
                total = plano_info.get("sabores_gratis_mes", 0)
                if row["beneficios_usados"] >= total:
                    return jsonify({"error": "Benefícios do mês esgotados"}), 400

                cur.execute(
                    "UPDATE clube_assinaturas SET beneficios_usados = beneficios_usados + 1 WHERE user_id=%s",
                    (user_id,),
                )
    except Exception as e:
        logger.error("Resgatar error: %s", e)
        return jsonify({"error": "Erro ao resgatar benefício"}), 500

    return jsonify({"message": "Benefício resgatado com sucesso! 🍦", "beneficio_id": beneficio_id})
