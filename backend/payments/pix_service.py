import hashlib
import logging
import time
import uuid

logger = logging.getLogger(__name__)

_PIX_STORE: dict = {}


def create_pix_charge(value: float, description: str, pedido_id: int):
    """Generate a mock PIX charge with QR code data."""
    txid = uuid.uuid4().hex[:26].upper()
    qr_payload = (
        f"00020126580014BR.GOV.BCB.PIX0136{hashlib.md5(txid.encode()).hexdigest()}"
        f"5204000053039865406{value:.2f}5802BR5913Gelateria Pro6008Brasilia"
        f"62070503***6304ABCD"
    )
    charge = {
        "txid": txid,
        "pedido_id": pedido_id,
        "value": value,
        "description": description,
        "status": "ativa",
        "qr_code": qr_payload,
        "qr_code_base64": f"data:image/png;base64,mock_qr_{txid}",
        "expiration": int(time.time()) + 3600,
    }
    _PIX_STORE[txid] = charge
    logger.info("PIX charge created: txid=%s value=%.2f", txid, value)
    return charge


def check_pix_status(txid: str):
    """Return the current status of a PIX charge."""
    charge = _PIX_STORE.get(txid)
    if not charge:
        return None
    return {"txid": txid, "status": charge.get("status", "ativa"), "value": charge.get("value")}
