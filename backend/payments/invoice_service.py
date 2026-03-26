import logging
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

logger = logging.getLogger(__name__)


class InvoiceService:
    """Generates payment receipts as PDF."""

    @staticmethod
    def generate_invoice(payment_data):
        """Generate a PDF receipt and return a BytesIO buffer.

        payment_data keys:
            order_id (int|str), date (str), items (list[dict]), total (float)
        Each item dict: name (str), qty (int|str), price (float)
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        table_data = [
            ["RECIBO DE PAGAMENTO", "", ""],
            [f"Pedido #{payment_data['order_id']}", f"Data: {payment_data['date']}", ""],
            ["", "", ""],
            ["Item", "Qtd", "Valor"],
        ]

        for item in payment_data.get("items", []):
            table_data.append(
                [item["name"], str(item["qty"]), f"R$ {float(item['price']):.2f}"]
            )

        table_data.append(["", "", ""])
        table_data.append(["TOTAL", "", f"R$ {float(payment_data['total']):.2f}"])

        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.beige),
                    ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer
