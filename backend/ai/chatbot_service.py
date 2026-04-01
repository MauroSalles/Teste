import logging
import os

logger = logging.getLogger(__name__)

_MENU_KEYWORDS = {
    "cardapio": "Nosso cardápio inclui: 🍫 Chocolate (R$10,00), 🍓 Morango (R$9,50), 🍦 Baunilha (R$8,00), 🌿 Pistache (R$12,00) e 🍋 Limão (R$9,00). Qual sabor deseja experimentar?",
    "sabores": "Temos os seguintes sabores disponíveis: Chocolate, Morango, Baunilha, Pistache e Limão. Todos feitos com ingredientes frescos!",
    "pedido": "Para fazer um pedido, basta digitar 'pedir <sabor> <quantidade>' no terminal ou usar nossa API. Posso ajudar com mais alguma coisa?",
    "preco": "Nossos preços variam de R$8,00 (Baunilha) a R$12,00 (Pistache). Ótimo custo-benefício para um gelato premium!",
    "preço": "Nossos preços variam de R$8,00 (Baunilha) a R$12,00 (Pistache). Ótimo custo-benefício para um gelato premium!",
    "pontos": "Você acumula pontos a cada pedido! 10 pontos por R$1 gasto. Troque seus pontos por descontos e brindes.",
    "fidelidade": "Nosso programa de fidelidade oferece: pontos em compras, missões diárias, giro da sorte e muito mais! Acesse o dashboard para ver seu progresso.",
    "ajuda": "Posso ajudar com: cardápio, preços, pedidos, pontos de fidelidade, promoções e horários. O que você precisa?",
    "promocao": "Confira nossas promoções no dashboard! Temos descontos especiais para membros do programa de fidelidade.",
    "promoção": "Confira nossas promoções no dashboard! Temos descontos especiais para membros do programa de fidelidade.",
    "horario": "Funcionamos de segunda a domingo, das 10h às 22h. Sábados e domingos até às 23h!",
    "horário": "Funcionamos de segunda a domingo, das 10h às 22h. Sábados e domingos até às 23h!",
    "obrigado": "Disponha! Estamos sempre aqui para ajudar. 🍦 Volte sempre!",
    "oi": "Olá! Bem-vindo à Gelateria Pro! 🍦 Como posso ajudar você hoje?",
    "ola": "Olá! Bem-vindo à Gelateria Pro! 🍦 Como posso ajudar você hoje?",
    "olá": "Olá! Bem-vindo à Gelateria Pro! 🍦 Como posso ajudar você hoje?",
}

_DEFAULT_RESPONSE = (
    "Não entendi bem sua pergunta. Posso ajudar com informações sobre nosso cardápio, "
    "preços, pedidos, pontos de fidelidade e promoções. Tente perguntar sobre algum desses tópicos!"
)


def _predefined_response(message: str) -> str:
    lower = message.lower().strip()
    for keyword, response in _MENU_KEYWORDS.items():
        if keyword in lower:
            return response
    return _DEFAULT_RESPONSE


def get_bot_response(message: str, user_id: int = None) -> dict:
    """Return chatbot response. Uses OpenAI if configured, else smart predefined responses."""
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key:
        try:
            import openai  # type: ignore

            openai.api_key = openai_key
            client = openai.OpenAI(api_key=openai_key)
            system_prompt = (
                "Você é um atendente virtual da Gelateria Pro, uma sorveteria premium. "
                "Seja simpático, use emojis moderadamente e responda em português. "
                "Cardápio: Chocolate R$10, Morango R$9.50, Baunilha R$8, Pistache R$12, Limão R$9."
            )
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                max_tokens=200,
            )
            response_text = completion.choices[0].message.content.strip()
            return {"response": response_text, "source": "openai"}
        except Exception as exc:
            logger.warning("OpenAI error, falling back to predefined: %s", exc)

    response_text = _predefined_response(message)
    return {"response": response_text, "source": "predefined"}
