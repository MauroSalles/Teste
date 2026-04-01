"""Payment routes blueprint — /api/payments/*"""

import logging

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

logger = logging.getLogger(__name__)

payment_bp = Blueprint("payment", __name__, url_prefix="/api/payments")


# ── Stripe ────────────────────────────────────────────────────────────────────

@payment_bp.post("/stripe/intent")
@token_required
def stripe_intent(current_user):
    from backend.payments.stripe_service import create_payment_intent
    data = request.get_json(silent=True) or {}
    amount = data.get("amount_cents")
    if not amount or not isinstance(amount, int) or amount <= 0:
        return jsonify({"error": "amount_cents deve ser um inteiro positivo"}), 400

    currency = data.get("currency", "brl")
    metadata = data.get("metadata", {})
    metadata["user_id"] = str(current_user["id"])

    intent = create_payment_intent(amount, currency=currency, metadata=metadata)
    if intent is None:
        return jsonify({"error": "Stripe não configurado"}), 503

    return jsonify({"client_secret": intent.get("client_secret"), "id": intent.get("id")}), 201


@payment_bp.post("/stripe/webhook")
def stripe_webhook():
    from backend.payments.stripe_service import handle_webhook
    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature", "")
    try:
        result = handle_webhook(payload, sig_header)
        return jsonify(result), 200
    except Exception as exc:
        logger.warning("Webhook error: %s", exc)
        return jsonify({"error": str(exc)}), 400


# ── PIX ───────────────────────────────────────────────────────────────────────

@payment_bp.post("/pix/qrcode")
@token_required
def pix_qrcode(current_user):
    from backend.payments.pix_service import create_pix_charge
    data = request.get_json(silent=True) or {}
    valor = data.get("valor")
    if valor is None:
        return jsonify({"error": "valor é obrigatório"}), 400
    try:
        valor = float(valor)
        if valor <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "valor deve ser um número positivo"}), 400

    descricao = data.get("descricao", "Pedido Gelateria Pro")
    charge = create_pix_charge(valor, descricao)
    return jsonify(charge), 201


@payment_bp.get("/pix/status/<transaction_id>")
@token_required
def pix_status(current_user, transaction_id):
    from backend.payments.pix_service import check_pix_status
    result = check_pix_status(transaction_id)
    return jsonify(result), 200


# ── Methods ───────────────────────────────────────────────────────────────────

@payment_bp.get("/methods")
def payment_methods():
    return jsonify([
        {"id": "stripe", "nome": "Cartão de Crédito/Débito", "disponivel": True},
        {"id": "pix", "nome": "PIX", "disponivel": True},
        {"id": "dinheiro", "nome": "Dinheiro", "disponivel": True},
    ]), 200
