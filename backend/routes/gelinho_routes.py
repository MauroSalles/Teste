"""Gelinho mascot blueprint — /api/gelinho/*

Gelinho is the emotional ice cream mascot.
Uses OpenAI GPT if OPENAI_API_KEY is set; otherwise falls back to
a bank of 50+ pre-defined responses organised by category.
"""

import logging
import os
import random

from flask import Blueprint, jsonify, request

from backend.auth.jwt_handler import token_required

try:
    from backend.database import get_db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

logger = logging.getLogger(__name__)

gelinho_bp = Blueprint("gelinho", __name__, url_prefix="/api/gelinho")

# ── Fallback responses (no OpenAI) ────────────────────────────────────────────

RESPOSTAS_GELINHO = {
    "saudacao": [
        "Olá! Que bom te ver por aqui! Já escolheu o sabor de hoje? 😄",
        "Ei! Seu sorvete favorito está com saudades de você! 🍦",
        "Oi oi! Pronto para uma pausa gelada? Estou aqui! 🎉",
        "Bem-vindo de volta! Hoje temos novidades incríveis! ✨",
        "Olá! Você apareceu na hora certa — o sabor do dia está sensacional! 🍓",
    ],
    "recomendacao": [
        "Com base nos seus pedidos, acho que você vai amar nosso Pistache Premium!",
        "O Sabor do Dia está incrível — e com 10% OFF para você!",
        "Já experimentou nosso sorvete de Maracujá com Cream Cheese? Um espetáculo!",
        "Para o calor de hoje, nada melhor que nosso sorvete de Limão Siciliano! 🍋",
        "Dica quente: o combo Baunilha + Calda de Caramelo está arrasando hoje! 🍯",
        "Nosso sorvete de Morango com pedaços de chocolate é irresistível! 🍓🍫",
    ],
    "encorajamento": [
        "Você está arrasando! Continue fazendo check-in para ganhar mais pontos! 🔥",
        "Incrível! Você já está no nível VIP! Orgulho mesmo! 🏆",
        "Cada dia de check-in te aproxima de recompensas exclusivas! 💎",
        "Você é um dos nossos clientes mais fiéis. Muito obrigado! 💙",
        "Sua sequência de dias consecutivos é impressionante! Continue assim! ⚡",
    ],
    "piada": [
        "Por que o sorvete foi ao médico? Porque estava se derretendo de amor! 😂",
        "O que o sorvete disse para a casquinha? 'Você me completa!' 🍦❤️",
        "Qual é o sorvete mais musical? O de Violeta! 😄",
        "Por que o sorvete nunca mente? Porque é todo feito de creme de verdade! 🥛",
        "Como o sorvete cumprimenta os amigos? 'Olá, gelado amigo!' 🤣",
        "O que o sorvete faz quando fica nervoso? Congela! 😅",
    ],
    "despedida": [
        "Até logo! Volte sempre para mais sabores incríveis! 👋🍦",
        "Tchau tchau! Guarda espaço para o próximo sorvete! 😉",
        "Até a próxima! Estou sempre aqui quando bater aquela vontade! 💙",
        "Foi um prazer! Compartilha nossa Gelateria com seus amigos! 🤩",
    ],
    "agradecimento": [
        "Obrigado pela sua fidelidade! Você é especial para nós! 💙",
        "Muito obrigado! Clientes como você fazem tudo valer a pena! 🙏",
        "Fico feliz que esteja aqui! Seu carinho é nosso combustível! ⚡",
    ],
    "humor_feliz": [
        "Que ótimo que você está feliz! Um dia assim merece sorvete duplo! 🍦🍦",
        "Felicidade combina perfeitamente com sorvete! Boa escolha! 😄",
    ],
    "humor_neutro": [
        "Dias neutros existem — mas um sorvete sempre melhora tudo! 🍦",
        "Precisa de uma dose de alegria gelada? Estou aqui! 💙",
    ],
    "humor_triste": [
        "Ei, fique bem! Sorvete não resolve tudo, mas ajuda muito! 🤗🍦",
        "Estou aqui por você! Um sorvete de Chocolate Belga vai te animar! 🍫",
        "Dias difíceis passam — e sorvete suaviza tudo! Um abraço virtual! 🫂",
    ],
}

_OPENAI_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))

_GELINHO_SYSTEM_PROMPT = """Você é o Gelinho 🍦, mascote emocional e simpático da Gelateria Pro.
Sua personalidade:
- Alegre, caloroso e encorajador
- Especialista em sorvetes e sobremesas geladas
- Fala em português brasileiro, informal mas respeitoso
- Usa emojis de forma natural (🍦🎉💙🔥✨)
- Responde de forma curta (1-3 frases)
- Adapta o tom ao humor do usuário
Você NÃO é um chatbot de suporte técnico — foque em conexão emocional e recomendações."""


def _resposta_fallback(categoria: str = "saudacao") -> str:
    """Return a random fallback response for the given category."""
    respostas = RESPOSTAS_GELINHO.get(categoria, RESPOSTAS_GELINHO["saudacao"])
    return random.choice(respostas)


def _resposta_openai(mensagem: str, contexto: dict) -> str:
    """Call OpenAI GPT to generate a contextual Gelinho response."""
    try:
        import openai  # type: ignore
        client = openai.OpenAI()
        system = _GELINHO_SYSTEM_PROMPT
        if contexto.get("nome"):
            system += f"\nO nome do usuário é {contexto['nome']}."
        if contexto.get("streak"):
            system += f"\nEle está com uma sequência de {contexto['streak']} dias consecutivos de check-in."
        if contexto.get("ultimo_sabor"):
            system += f"\nO último sabor pedido foi {contexto['ultimo_sabor']}."
        if contexto.get("humor"):
            system += f"\nHumor registrado hoje: {contexto['humor']}."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": mensagem},
            ],
            max_tokens=150,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("OpenAI error, using fallback: %s", e)
        return _resposta_fallback("saudacao")


def _get_user_context(user_id: int) -> dict:
    """Fetch minimal context for personalising Gelinho responses."""
    ctx: dict = {}
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM users WHERE id=%s", (user_id,))
                u = cur.fetchone()
                if u:
                    ctx["nome"] = u["name"]

                cur.execute(
                    "SELECT streak_atual, humor FROM daily_checkins WHERE user_id=%s ORDER BY data DESC LIMIT 1",
                    (user_id,),
                )
                ci = cur.fetchone()
                if ci:
                    ctx["streak"] = ci["streak_atual"]
                    ctx["humor"] = ci["humor"]
    except Exception as e:
        logger.warning("Context fetch error: %s", e)
    return ctx


# ── Conversa ──────────────────────────────────────────────────────────────────

@gelinho_bp.post("/conversa")
@token_required
def conversar(current_user):
    """Chat with Gelinho. Uses GPT if available, otherwise uses fallback bank."""
    user_id = current_user["id"]
    data = request.get_json(silent=True) or {}
    mensagem = (data.get("mensagem") or "").strip()

    if not mensagem:
        return jsonify({"error": "mensagem é obrigatória"}), 400

    contexto = _get_user_context(user_id)

    if _OPENAI_AVAILABLE:
        resposta = _resposta_openai(mensagem, contexto)
    else:
        # Choose category based on simple keyword matching
        msg_lower = mensagem.lower()
        if any(w in msg_lower for w in ("oi", "olá", "ola", "hey", "bom dia", "boa tarde", "boa noite")):
            cat = "saudacao"
        elif any(w in msg_lower for w in ("piada", "engraçado", "rir", "humor")):
            cat = "piada"
        elif any(w in msg_lower for w in ("triste", "ruim", "mal", "péssimo")):
            cat = "humor_triste"
        elif any(w in msg_lower for w in ("obrigado", "obrigada", "valeu", "thanks")):
            cat = "agradecimento"
        elif any(w in msg_lower for w in ("tchau", "bye", "até", "sair")):
            cat = "despedida"
        elif any(w in msg_lower for w in ("sabor", "sorvete", "gelado", "pedido", "pedir")):
            cat = "recomendacao"
        elif any(w in msg_lower for w in ("pontos", "streak", "sequência", "level")):
            cat = "encorajamento"
        else:
            humor = contexto.get("humor", "")
            if humor == "feliz":
                cat = "humor_feliz"
            elif humor == "triste":
                cat = "humor_triste"
            else:
                cat = "saudacao"
        resposta = _resposta_fallback(cat)

    return jsonify({
        "gelinho": resposta,
        "contexto": {
            "nome": contexto.get("nome"),
            "streak": contexto.get("streak", 0),
        },
    })


# ── Frase do dia ──────────────────────────────────────────────────────────────

@gelinho_bp.get("/frase-do-dia")
@token_required
def frase_do_dia(current_user):
    """Return a personalised motivational phrase based on streak and mood."""
    user_id = current_user["id"]
    ctx = _get_user_context(user_id)
    streak = ctx.get("streak", 0)
    humor = ctx.get("humor", "neutro")
    nome = ctx.get("nome", "amigo")

    if streak >= 30:
        frase = f"Uau, {nome}! 30 dias seguidos! Você é uma lenda da Gelateria! 🏆🍦"
    elif streak >= 7:
        frase = f"Impressionante, {nome}! {streak} dias consecutivos! Continue assim! 🔥"
    elif streak >= 3:
        frase = f"Olá, {nome}! {streak} dias de sequência — você está voando! ⚡"
    elif humor == "triste":
        frase = f"Ei, {nome}. Dias difíceis passam. Um sorvete vai te animar! 🤗🍦"
    elif humor == "feliz":
        frase = f"Que dia lindo para um sorvete, {nome}! Felicidade total! 😄🍦"
    else:
        frase = f"Bom dia, {nome}! Começou o check-in hoje? Não perca seus pontos! 💎"

    return jsonify({"frase": frase, "streak": streak, "humor": humor})


# ── Dica personalizada ────────────────────────────────────────────────────────

@gelinho_bp.get("/dica")
@token_required
def dica_personalizada(current_user):
    """Return a flavor tip based on the user's order history."""
    user_id = current_user["id"]
    sabor_recomendado = "Pistache Premium"

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT s.nome, COUNT(*) AS total
                       FROM pedidos p
                       JOIN sabores s ON s.id = p.sabor_id
                       WHERE p.user_id = %s
                       GROUP BY s.nome ORDER BY total DESC LIMIT 1""",
                    (user_id,),
                )
                row = cur.fetchone()
        if row:
            sabor_recomendado = row["nome"]
    except Exception as e:
        logger.warning("Dica DB error: %s", e)

    respostas = [
        f"Com base no seu histórico, aposto que você vai amar mais do {sabor_recomendado}! 🍦",
        f"Seu sabor do coração parece ser {sabor_recomendado} — ótimo gosto! ✨",
        f"Dica Gelinho: {sabor_recomendado} combina perfeitamente com calda de caramelo! 🍯",
    ]

    return jsonify({
        "dica": random.choice(respostas),
        "sabor_recomendado": sabor_recomendado,
    })
