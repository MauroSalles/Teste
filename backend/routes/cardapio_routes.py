"""Cardápio Digital Inteligente — /api/cardapio/*
Graceful degradation: returns mock data if tables don't exist yet.
"""
from flask import Blueprint, jsonify, request
from backend.database import get_db

cardapio_bp = Blueprint("cardapio", __name__, url_prefix="/api/cardapio")

_NUTRI_MOCK = {
    "default": {"calorias": 150, "gorduras": 4.5, "carboidratos": 28.0, "proteinas": 3.0, "acucar": 22.0, "porcao_gramas": 100},
    "chocolate": {"calorias": 210, "gorduras": 8.0, "carboidratos": 30.0, "proteinas": 4.0, "acucar": 26.0, "porcao_gramas": 100},
    "morango": {"calorias": 120, "gorduras": 3.0, "carboidratos": 22.0, "proteinas": 2.5, "acucar": 18.0, "porcao_gramas": 100},
    "pistache": {"calorias": 230, "gorduras": 12.0, "carboidratos": 24.0, "proteinas": 5.5, "acucar": 16.0, "porcao_gramas": 100},
}


def _analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis (no external libs)."""
    text_lower = text.lower()
    positive = ["ótimo", "excelente", "delicioso", "incrível", "perfeito", "maravilhoso", "amei", "adorei", "bom", "gostei"]
    negative = ["ruim", "péssimo", "horrível", "terrível", "decepcionante", "não gostei", "feio", "estragado"]
    pos_score = sum(1 for w in positive if w in text_lower)
    neg_score = sum(1 for w in negative if w in text_lower)
    if pos_score > neg_score:
        return "positivo"
    if neg_score > pos_score:
        return "negativo"
    return "neutro"


@cardapio_bp.get("")
def listar_cardapio():
    """GET /api/cardapio — full menu with placeholder image, price, description, popularity tag."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.nome, s.preco,
                           COALESCE(e.quantidade, 0) AS estoque,
                           COALESCE(AVG(a.nota), 0) AS nota_media,
                           COUNT(a.id) AS total_avaliacoes
                    FROM sabores s
                    LEFT JOIN estoque e ON e.sabor_id = s.id
                    LEFT JOIN avaliacoes a ON a.sabor_id = s.id
                    GROUP BY s.id, s.nome, s.preco, e.quantidade
                    ORDER BY nota_media DESC, s.nome
                """)
                rows = cur.fetchall()
    except Exception:
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, nome, preco FROM sabores ORDER BY nome")
                    rows = [dict(r, estoque=0, nota_media=0, total_avaliacoes=0) for r in cur.fetchall()]
        except Exception:
            rows = []

    result = []
    for r in rows:
        r = dict(r)
        tag = "popular" if float(r.get("nota_media", 0)) >= 4 else ("novidade" if r.get("total_avaliacoes", 0) == 0 else "")
        result.append({
            "id": r["id"],
            "nome": r["nome"],
            "preco": float(r["preco"]),
            "estoque": r.get("estoque", 0),
            "nota_media": round(float(r.get("nota_media", 0)), 1),
            "total_avaliacoes": r.get("total_avaliacoes", 0),
            "tag": tag,
            "imagem_placeholder": f"https://ui-avatars.com/api/?name={r['nome']}&background=random&color=fff&size=200",
            "descricao": f"Delicioso sorvete de {r['nome'].lower()}, feito com ingredientes selecionados.",
        })
    return jsonify(result)


@cardapio_bp.get("/destaque")
def destaque():
    """GET /api/cardapio/destaque — top 3 best-selling flavors this week."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.id, s.nome, s.preco,
                           SUM(p.quantidade) AS total_vendido
                    FROM sabores s
                    JOIN pedidos p ON p.sabor_id = s.id
                    WHERE p.data >= NOW() - INTERVAL '7 days'
                    GROUP BY s.id, s.nome, s.preco
                    ORDER BY total_vendido DESC
                    LIMIT 3
                """)
                rows = cur.fetchall()
    except Exception:
        rows = []

    if not rows:
        return jsonify([
            {"id": 1, "nome": "Chocolate", "preco": 10.0, "total_vendido": 42, "destaque": True},
            {"id": 2, "nome": "Morango", "preco": 9.5, "total_vendido": 35, "destaque": True},
            {"id": 3, "nome": "Pistache", "preco": 12.0, "total_vendido": 28, "destaque": True},
        ])

    return jsonify([dict(r, destaque=True) for r in rows])


@cardapio_bp.get("/<int:sabor_id>/nutricional")
def nutricional(sabor_id):
    """GET /api/cardapio/<id>/nutricional — nutritional info for a flavor."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM info_nutricional WHERE sabor_id = %s", (sabor_id,))
                row = cur.fetchone()
                if not row:
                    cur.execute("SELECT nome FROM sabores WHERE id = %s", (sabor_id,))
                    sabor = cur.fetchone()
                    if not sabor:
                        return jsonify({"error": "Sabor não encontrado"}), 404
                    key = sabor["nome"].lower()
                    nutri = _NUTRI_MOCK.get(key, _NUTRI_MOCK["default"])
                    cur.execute("""
                        INSERT INTO info_nutricional (sabor_id, calorias, gorduras, carboidratos, proteinas, acucar, porcao_gramas)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (sabor_id) DO NOTHING
                        RETURNING *
                    """, (sabor_id, nutri["calorias"], nutri["gorduras"], nutri["carboidratos"],
                          nutri["proteinas"], nutri["acucar"], nutri["porcao_gramas"]))
                    row = cur.fetchone() or {**nutri, "sabor_id": sabor_id}
    except Exception:
        nutri = _NUTRI_MOCK.get("default")
        return jsonify({**nutri, "sabor_id": sabor_id, "source": "mock"})

    return jsonify(dict(row))


@cardapio_bp.post("/<int:sabor_id>/avaliacao")
def criar_avaliacao(sabor_id):
    """POST /api/cardapio/<id>/avaliacao — rate a flavor (1-5 + comment)."""
    data = request.get_json(silent=True) or {}
    nota = data.get("nota")
    comentario = (data.get("comentario") or "").strip()
    user_id = data.get("user_id")

    try:
        nota = int(nota)
        if not (1 <= nota <= 5):
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "nota deve ser um inteiro entre 1 e 5"}), 400

    sentimento = _analyze_sentiment(comentario) if comentario else "neutro"

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM sabores WHERE id = %s", (sabor_id,))
                if not cur.fetchone():
                    return jsonify({"error": "Sabor não encontrado"}), 404
                cur.execute("""
                    INSERT INTO avaliacoes (sabor_id, user_id, nota, comentario, sentimento)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, sabor_id, nota, comentario, sentimento, created_at
                """, (sabor_id, user_id, nota, comentario, sentimento))
                row = cur.fetchone()
    except Exception as e:
        return jsonify({"error": "Não foi possível salvar a avaliação", "detail": str(e)}), 500

    return jsonify(dict(row)), 201


@cardapio_bp.get("/<int:sabor_id>/avaliacoes")
def listar_avaliacoes(sabor_id):
    """GET /api/cardapio/<id>/avaliacoes — list ratings for a flavor with average."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT nota, comentario, sentimento, created_at
                    FROM avaliacoes WHERE sabor_id = %s
                    ORDER BY created_at DESC
                """, (sabor_id,))
                rows = cur.fetchall()
                media = sum(float(r["nota"]) for r in rows) / len(rows) if rows else 0
    except Exception:
        return jsonify({"sabor_id": sabor_id, "media": 0, "total": 0, "avaliacoes": []})

    return jsonify({
        "sabor_id": sabor_id,
        "media": round(media, 1),
        "total": len(rows),
        "avaliacoes": [dict(r) for r in rows],
    })
