"""Invoice / receipt PDF generation using ReportLab."""

import logging
from io import BytesIO

logger = logging.getLogger(__name__)


def generate_receipt_pdf(pedido_id, itens, total, metodo_pagamento):
    """Generate a receipt PDF and return bytes. Falls back to plain text if ReportLab unavailable."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas

        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, height - 3 * cm, "🍦 Gelateria Pro — Recibo")

        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, height - 4.5 * cm, f"Pedido #: {pedido_id}")
        c.drawString(2 * cm, height - 5.2 * cm, f"Método: {metodo_pagamento}")

        y = height - 7 * cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, "Item")
        c.drawString(12 * cm, y, "Subtotal")
        y -= 0.7 * cm

        c.setFont("Helvetica", 11)
        for item in itens:
            nome = item.get("nome", item.get("sabor", "Item"))
            qtd = item.get("quantidade", 1)
            preco = item.get("preco", 0.0)
            subtotal = float(qtd) * float(preco)
            c.drawString(2 * cm, y, f"{nome} x{qtd}")
            c.drawString(12 * cm, y, f"R$ {subtotal:.2f}")
            y -= 0.6 * cm

        y -= 0.5 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, f"Total: R$ {float(total):.2f}")

        c.showPage()
        c.save()
        buf.seek(0)
        return buf.read()

    except ImportError:
        logger.warning("ReportLab not available; generating plain text receipt")
        lines = [
            "Gelateria Pro - Recibo",
            f"Pedido #: {pedido_id}",
            f"Método: {metodo_pagamento}",
            "",
        ]
        for item in itens:
            nome = item.get("nome", item.get("sabor", "Item"))
            qtd = item.get("quantidade", 1)
            preco = item.get("preco", 0.0)
            lines.append(f"{nome} x{qtd} = R$ {float(qtd)*float(preco):.2f}")
        lines.append(f"\nTotal: R$ {float(total):.2f}")
        return "\n".join(lines).encode("utf-8")
