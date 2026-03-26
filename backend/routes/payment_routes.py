import logging

from flask import Blueprint, jsonify, request, send_file

from backend.auth.jwt_handler import token_required
from backend.payments.pix_service import PIXPaymentService
from backend.payments.stripe_service import StripePaymentService

logger = logging.getLogger(__name__)

payment_bp = Blueprint("payments", __name__, url_prefix="/api/payments")

stripe_service = StripePaymentService()
pix_service = PIXPaymentService()


@payment_bp.route("/stripe/intent", methods=["POST"])
@token_required
def create_stripe_intent(current_user):
    """Create a Stripe payment intent."""
    data = request.get_json(silent=True) or {}
    if "amount" not in data or "order_id" not in data:
        return jsonify({"error": "amount and order_id are required"}), 400

    result = stripe_service.create_payment_intent(
        data["amount"],
        current_user.get("customer_id"),
        {"order_id": str(data["order_id"])},
    )
    return jsonify(result), 200 if result["success"] else 400


@payment_bp.route("/stripe/setup", methods=["POST"])
@token_required
def create_setup_intent(current_user):
    """Create a Stripe SetupIntent to save a card for future payments."""
    result = stripe_service.create_setup_intent(current_user.get("customer_id"))
    return jsonify(result), 200 if result["success"] else 400


@payment_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """Stripe webhook endpoint for payment confirmation."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")
    result = stripe_service.process_webhook(payload, sig_header)
    return jsonify(result), 200


@payment_bp.route("/stripe/refund", methods=["POST"])
@token_required
def refund_payment(current_user):
    """Refund a Stripe payment (full or partial)."""
    data = request.get_json(silent=True) or {}
    if "payment_id" not in data:
        return jsonify({"error": "payment_id is required"}), 400

    result = stripe_service.refund_payment(
        data["payment_id"], amount=data.get("amount")
    )
    return jsonify(result), 200 if result["success"] else 400


@payment_bp.route("/pix/qrcode", methods=["POST"])
@token_required
def generate_pix_qr(current_user):
    """Generate a dynamic PIX QR code."""
    data = request.get_json(silent=True) or {}
    if "order_id" not in data or "amount" not in data:
        return jsonify({"error": "order_id and amount are required"}), 400

    result = pix_service.generate_pix_qr_code(
        data["order_id"],
        data["amount"],
        current_user.get("email", ""),
    )
    return jsonify(result), 200 if result["success"] else 400


@payment_bp.route("/pix/status/<transaction_id>", methods=["GET"])
@token_required
def check_pix_status(current_user, transaction_id):
    """Check PIX payment status in real time."""
    result = pix_service.check_pix_status(transaction_id)
    return jsonify(result), 200


@payment_bp.route("/methods", methods=["GET"])
@token_required
def list_payment_methods(current_user):
    """List saved payment methods for the current user."""
    return jsonify({"methods": current_user.get("payment_methods", [])}), 200
