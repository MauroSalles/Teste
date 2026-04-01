"""PIX payment service (mock implementation)."""

import logging
import secrets
import time

logger = logging.getLogger(__name__)

# After this many seconds the mock auto-approves the payment (simulates bank confirmation)
_MOCK_PAYMENT_AUTO_APPROVE_SECONDS = 60

# In-memory store for demo purposes
_pix_charges = {}


def _generate_txid():
    return "PIX" + secrets.token_hex(10).upper()


def create_pix_charge(valor, descricao, txid=None):
    """Create a PIX charge and return charge data with txid."""
    if txid is None:
        txid = _generate_txid()

    charge = {
        "txid": txid,
        "valor": float(valor),
        "descricao": descricao,
        "status": "pendente",
        "qrcode": f"00020126580014BR.GOV.BCB.PIX0136{txid}5204000053039865802BR5913Gelateria Pro6008Sao Paulo62070503***6304ABCD",
        "created_at": time.time(),
    }
    _pix_charges[txid] = charge
    logger.info("PIX charge created: txid=%s valor=%.2f", txid, valor)
    return charge


def check_pix_status(txid):
    """Return the payment status for a given txid."""
    charge = _pix_charges.get(txid)
    if not charge:
        return {"txid": txid, "status": "nao_encontrado"}

    elapsed = time.time() - charge["created_at"]
    if elapsed > _MOCK_PAYMENT_AUTO_APPROVE_SECONDS:
        charge["status"] = "pago"

    return {"txid": txid, "status": charge["status"], "valor": charge.get("valor")}
