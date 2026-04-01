import logging
import os
from flask import Blueprint, request, jsonify

from backend.auth.jwt_handler import token_required
from backend.payments.stripe_service import create_payment_intent, handle_webhook
from backend.payments.pix_service import create_pix_charge, check_pix_status
from backend.models.payment import registrar_pagamento, obter_pagamento

logger = logging.getLogger(__name__)

payment_bp = Blueprint("payment_bp", __name__, url_prefix="/api/payments")


@payment_bp.route("/methods", methods=["GET"])
def list_methods():
    methods = []
    if os.environ.get("STRIPE_SECRET_KEY"):
        methods.append({"id": "stripe", "name": "Cartão de Crédito/Débito (Stripe)", "enabled": True})
    else:
        methods.append({"id": "stripe", "name": "Cartão de Crédito/Débito (Stripe)", "enabled": False})
    methods.append({"id": "pix", "name": "PIX", "enabled": True})
    methods.append({"id": "dinheiro", "name": "Dinheiro", "enabled": True})
    return jsonify({"methods": methods})


@payment_bp.route("/stripe/intent", methods=["POST"])
@token_required
def stripe_intent(current_user):
    data = request.get_json(silent=True) or {}
    amount_cents = data.get("amount_cents")
    if not amount_cents or not isinstance(amount_cents, int) or amount_cents <= 0:
        return jsonify({"error": "amount_cents must be a positive integer"}), 400
    currency = data.get("currency", "brl")
    pedido_id = data.get("pedido_id")
    metadata = {"user_id": current_user["id"], "pedido_id": pedido_id or ""}
    try:
        intent = create_payment_intent(amount_cents, currency, metadata)
        if pedido_id:
            registrar_pagamento(
                pedido_id=pedido_id,
                metodo="stripe",
                valor=amount_cents / 100,
                status="pendente",
                external_id=intent.get("id"),
            )
        return jsonify(intent), 201
    except Exception as exc:
        logger.error("stripe_intent error: %s", exc)
        return jsonify({"error": "Payment processing error"}), 500


@payment_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")
    try:
        event = handle_webhook(payload, sig_header)
        event_type = event.get("type", "")
        if event_type == "payment_intent.succeeded":
            ext_id = event.get("data", {}).get("object", {}).get("id")
            logger.info("PaymentIntent succeeded: %s", ext_id)
        return jsonify({"received": True})
    except Exception as exc:
        logger.error("stripe_webhook error: %s", exc)
        return jsonify({"error": "Webhook processing error"}), 400


@payment_bp.route("/pix/qrcode", methods=["POST"])
@token_required
def pix_qrcode(current_user):
    data = request.get_json(silent=True) or {}
    value = data.get("value")
    pedido_id = data.get("pedido_id")
    description = data.get("description", "Pedido Gelateria Pro")
    if not value or float(value) <= 0:
        return jsonify({"error": "value must be a positive number"}), 400
    charge = create_pix_charge(float(value), description, pedido_id)
    if pedido_id:
        registrar_pagamento(
            pedido_id=pedido_id,
            metodo="pix",
            valor=float(value),
            status="pendente",
            external_id=charge["txid"],
        )
    return jsonify(charge), 201


@payment_bp.route("/pix/status/<txid>", methods=["GET"])
def pix_status(txid):
    result = check_pix_status(txid)
    if not result:
        return jsonify({"error": "txid not found"}), 404
    return jsonify(result)
