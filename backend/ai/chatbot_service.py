import os
import json
import logging

import openai

from backend.database import get_db

logger = logging.getLogger(__name__)


class ChatBotService:
    """ChatBot GPT-4 com contexto de cliente"""

    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4"

    def get_chat_response(self, user_id, message, chat_history):
        """Responde com contexto do cliente"""
        try:
            context = self._build_context(user_id, chat_history)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente de uma gelateria.\n\n"
                        f"Cliente info: {context}\n\n"
                        "Regras:\n"
                        "- Responda sempre em português fluente\n"
                        "- Seja amigável e entusiasmado\n"
                        "- Recomende sabores baseado no histórico\n"
                        "- Ofereça promoções personalizadas\n"
                        "- Dirija para compra quando apropriado\n"
                        "- Resolve problemas rapidamente\n"
                    ),
                },
                {"role": "user", "content": message},
            ]

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            answer = response.choices[0].message.content
            self._log_conversation(user_id, message, answer)

            return {
                'success': True,
                'response': answer,
                'finish_reason': response.choices[0]['finish_reason'],
            }
        except Exception as e:
            logger.error("ChatBot error: %s", e)
            return {'success': False, 'error': str(e)}

    def _build_context(self, user_id, chat_history):
        """Cria contexto do cliente para IA"""
        user_data = {
            'orders': self._get_order_history(user_id, limit=5),
            'last_purchase': self._get_last_purchase(user_id),
        }
        return json.dumps(user_data, ensure_ascii=False)

    def _get_order_history(self, user_id, limit=5):
        """Retorna últimos pedidos para contexto"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT p.id, s.nome, p.quantidade, p.data
                        FROM pedidos p
                        JOIN sabores s ON p.sabor_id = s.id
                        ORDER BY p.data DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cursor.fetchall()
                    return [dict(r) for r in rows]
        except Exception:
            return []

    def _get_last_purchase(self, user_id):
        """Retorna última compra do usuário"""
        history = self._get_order_history(user_id, limit=1)
        return history[0] if history else None

    def _log_conversation(self, user_id, user_msg, bot_response):
        """Armazena conversa no banco"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO chat_logs (user_id, user_message, bot_response, created_at)
                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                        """,
                        (user_id, user_msg, bot_response),
                    )
        except Exception as e:
            logger.warning("Failed to log conversation: %s", e)
