"""Chatbot service — uses OpenAI if configured, otherwise predefined responses."""

import logging
import os
import re

logger = logging.getLogger(__name__)

_MENU = {
    "chocolate": "R$ 10,00",
    "morango": "R$ 9,50",
    "baunilha": "R$ 8,00",
    "pistache": "R$ 12,00",
    "limão": "R$ 9,00",
}

_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

_PREDEFINED = [
    (r"(oi|olá|ola|bom dia|boa tarde|boa noite|hey|hi)", "Olá! Bem-vindo à Gelateria Pro! 🍦 Como posso te ajudar?"),
    (r"(sabor|sabores|cardápio|cardapio|menu|opções|opcoes)", f"Nossos sabores: {', '.join(f'{k.title()} ({v})' for k, v in _MENU.items())} 😋"),
    (r"(preço|preco|valor|custa|quanto)", f"Nossos preços: {', '.join(f'{k.title()}: {v}' for k, v in _MENU.items())}"),
    (r"(pedido|pedir|comprar|quero)", "Para fazer um pedido, use o terminal ou o painel administrativo. Digite o sabor e quantidade!"),
    (r"(horário|horario|funciona|aberto|fecha)", "Funcionamos de segunda a domingo, das 10h às 22h 🕙"),
    (r"(endereço|endereco|onde|localização|localizacao)", "Estamos na Rua das Sorvetes, 123 — Centro, São Paulo/SP 📍"),
    (r"(entrega|delivery|motoboy)", "Fazemos entrega em até 45 minutos para o bairro. Taxa de R$ 5,00 🛵"),
    (r"(pagamento|pagar|forma|pix|cartão|cartao|dinheiro)", "Aceitamos PIX, cartão de crédito/débito e dinheiro 💳"),
    (r"(pontos|fidelidade|fidelidad|loyalty)", "Acumule pontos a cada pedido e troque por desconto! Use /api/loyalty para ver seus pontos 🌟"),
    (r"(obrigad|valeu|thanks|obg)", "De nada! Fico feliz em ajudar 😊 Volte sempre!"),
]


def chat(message, context=None):
    """Process a chat message and return a response."""
    if not message or not isinstance(message, str):
        return {"response": "Por favor, envie uma mensagem válida."}

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            return _openai_chat(message, context, api_key)
        except Exception as exc:
            logger.warning("OpenAI chat failed, using fallback: %s", exc)

    return {"response": _get_predefined_response(message)}


def _openai_chat(message, context, api_key):
    import openai
    client = openai.OpenAI(api_key=api_key)
    messages = [
        {
            "role": "system",
            "content": (
                "Você é o assistente virtual da Gelateria Pro. "
                "Responda de forma simpática e em português. "
                f"O menu atual é: {', '.join(f'{k.title()} ({v})' for k, v in _MENU.items())}."
            ),
        }
    ]
    if context:
        messages.extend(context)
    messages.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model=_OPENAI_MODEL,
        messages=messages,
        max_tokens=300,
    )
    return {"response": completion.choices[0].message.content}


def _get_predefined_response(message):
    """Return a predefined response based on keyword matching."""
    lower = message.lower()
    for pattern, response in _PREDEFINED:
        if re.search(pattern, lower):
            return response
    return (
        "Desculpe, não entendi. Posso te ajudar com: cardápio, preços, "
        "horários, endereço, formas de pagamento ou fazer um pedido! 🍦"
    )
