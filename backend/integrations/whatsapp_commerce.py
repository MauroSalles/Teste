import os
from datetime import datetime

from twilio.rest import Client

from backend.database import get_db


class WhatsAppCommerceService:
    """Vender via WhatsApp Business + Two-way messaging"""

    def __init__(self):
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN'),
        )
        self.wa_number = os.getenv('WHATSAPP_BUSINESS_NUMBER')

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _get_available_flavors(self):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nome AS name, preco AS price FROM sabores ORDER BY id"
                )
                return cur.fetchall()

    def _get_flavor(self, flavor_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nome AS name, preco AS price FROM sabores WHERE id = %s",
                    (flavor_id,),
                )
                return cur.fetchone()

    def _generate_payment_link(self, order_id, total):
        """Generate a payment link for an order (stub)."""
        app_url = os.getenv('APP_URL', 'https://example.com')
        return f"{app_url}/pay/{order_id}?total={total:.2f}"

    def _get_last_order(self, customer_phone):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, status
                    FROM orders
                    WHERE customer_phone = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (customer_phone,),
                )
                return cur.fetchone()

    def _send_whatsapp_message(self, customer_phone, body):
        message = self.twilio_client.messages.create(
            from_=f"whatsapp:{self.wa_number}",
            to=f"whatsapp:{customer_phone}",
            body=body,
        )
        return {'success': True, 'message_sid': message.sid}

    def _escalate_to_support(self, customer_phone, message_body):
        """Escalate an incoming message to a human support agent (stub)."""
        return self._send_whatsapp_message(
            customer_phone,
            "🙏 Encaminhando para nosso suporte. Aguarde um momento!",
        )

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def send_flavor_catalog(self, customer_phone):
        """Envia catálogo de sabores interativo via WhatsApp"""
        try:
            flavors = self._get_available_flavors()

            message_body = "🍓 Nossos Sabores Disponíveis:\n\n"
            for i, flavor in enumerate(flavors[:5], 1):
                message_body += f"{i}. {flavor['name']} - R${flavor['price']}\n"

            message = self.twilio_client.messages.create(
                from_=f"whatsapp:{self.wa_number}",
                to=f"whatsapp:{customer_phone}",
                body=message_body,
            )

            return {'success': True, 'message_sid': message.sid}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_order_via_whatsapp(self, customer_phone, customer_name, flavor_id, quantity, address):
        """Processa pedido completo via WhatsApp"""
        try:
            flavor = self._get_flavor(flavor_id)

            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO orders
                            (customer_phone, customer_name, flavor_id, quantity, address, status, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        RETURNING id
                        """,
                        (customer_phone, customer_name, flavor_id, quantity, address, 'pending_payment'),
                    )
                    order_id = cur.fetchone()['id']

            total = flavor['price'] * quantity
            payment_link = self._generate_payment_link(order_id, total)

            confirmation_message = (
                f"✅ Pedido #{order_id} Confirmado!\n\n"
                f"{flavor['name']} x{quantity}\n"
                f"Total: R${total:.2f}\n\n"
                f"Clique para pagar:\n{payment_link}\n\n"
                "Obrigado por usar WhatsApp! 🙏"
            )

            self.twilio_client.messages.create(
                from_=f"whatsapp:{self.wa_number}",
                to=f"whatsapp:{customer_phone}",
                body=confirmation_message,
            )

            return {
                'success': True,
                'order_id': order_id,
                'payment_link': payment_link,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def send_order_status_updates(self, customer_phone, order_id, status):
        """Envia atualizações de pedido via WhatsApp"""
        status_messages = {
            'confirmed': f"✅ Pedido #{order_id} confirmado! Preparando seu açaí...",
            'preparing': f"👨‍🍳 Seu açaí está sendo feito com carinho! #{order_id}",
            'ready': f"🎉 Seu açaí está pronto para buscar! #{order_id}",
            'on_the_way': f"🚗 Saiu para entrega! Chegará em 15 min #{order_id}",
            'delivered': f"✨ Entregue! Aproveite! Deixa uma review? #{order_id}",
        }

        try:
            self.twilio_client.messages.create(
                from_=f"whatsapp:{self.wa_number}",
                to=f"whatsapp:{customer_phone}",
                body=status_messages.get(status, f"Pedido #{order_id}: {status}"),
            )
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def handle_incoming_whatsapp_message(self, incoming_message):
        """Processa mensagens chegando no WhatsApp Business"""
        try:
            customer_phone = incoming_message['From'].replace('whatsapp:', '')
            message_body = incoming_message['Body']

            if 'pedir' in message_body.lower() or 'quero' in message_body.lower():
                return self.send_flavor_catalog(customer_phone)

            elif 'status' in message_body.lower() or 'aonde' in message_body.lower():
                order = self._get_last_order(customer_phone)
                if order:
                    response = f"Seu pedido #{order['id']} está {order['status']}"
                    return self._send_whatsapp_message(customer_phone, response)

            elif 'suporte' in message_body.lower() or 'problema' in message_body.lower():
                return self._escalate_to_support(customer_phone, message_body)

            else:
                return self._send_whatsapp_message(
                    customer_phone,
                    "👋 Oi! Use /pedir para ver sabores, /status para acompanhar, /suporte para ajuda",
                )
        except Exception as e:
            return {'success': False, 'error': str(e)}
