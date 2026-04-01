"""Public Analytics — /api/analytics/*
All endpoints are public (no auth required).
Graceful degradation with mock data if DB not available.
"""
from flask import Blueprint, jsonify
from backend.database import get_db

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.get("/sabores-populares")
def sabores_populares():
    """GET /api/analytics/sabores-populares — top flavors last 30 days."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.nome, SUM(p.quantidade) AS total_pedidos
                    FROM pedidos p
                    JOIN sabores s ON s.id = p.sabor_id
                    WHERE p.data >= NOW() - INTERVAL '30 days'
                    GROUP BY s.nome
                    ORDER BY total_pedidos DESC
                    LIMIT 10
                """)
                rows = cur.fetchall()
                if not rows:
                    raise ValueError("no data")
                return jsonify([dict(r) for r in rows])
    except Exception:
        return jsonify([
            {"nome": "Chocolate", "total_pedidos": 142},
            {"nome": "Morango", "total_pedidos": 118},
            {"nome": "Pistache", "total_pedidos": 95},
            {"nome": "Baunilha", "total_pedidos": 87},
            {"nome": "Limão", "total_pedidos": 64},
        ])


@analytics_bp.get("/horarios-pico")
def horarios_pico():
    """GET /api/analytics/horarios-pico — peak hours data for bar chart."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXTRACT(HOUR FROM data)::INTEGER AS hora,
                           COUNT(*) AS pedidos
                    FROM pedidos
                    GROUP BY hora ORDER BY hora
                """)
                rows = cur.fetchall()
                if not rows:
                    raise ValueError("no data")
                return jsonify([dict(r) for r in rows])
    except Exception:
        import random
        random.seed(42)
        return jsonify([
            {"hora": h, "pedidos": max(0, int(20 * abs(h - 14) / 14 * random.uniform(0.5, 1.5)))}
            for h in range(24)
        ])


@analytics_bp.get("/satisfacao")
def satisfacao():
    """GET /api/analytics/satisfacao — NPS score from ratings."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) FILTER (WHERE nota >= 4) AS promotores,
                        COUNT(*) FILTER (WHERE nota = 3) AS neutros,
                        COUNT(*) FILTER (WHERE nota <= 2) AS detratores,
                        COUNT(*) AS total,
                        ROUND(AVG(nota), 2) AS media
                    FROM avaliacoes
                """)
                row = dict(cur.fetchone())
                total = row.get("total", 0) or 0
                if total > 0:
                    nps = round(((row["promotores"] - row["detratores"]) / total) * 100, 1)
                else:
                    nps = 75.0
                row["nps"] = nps
                return jsonify(row)
    except Exception:
        return jsonify({"nps": 75.0, "media": 4.2, "total": 0, "source": "mock"})


@analytics_bp.get("/mapa-calor")
def mapa_calor():
    """GET /api/analytics/mapa-calor — heatmap data (hour x day of week)."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXTRACT(DOW FROM data)::INTEGER AS dia_semana,
                           EXTRACT(HOUR FROM data)::INTEGER AS hora,
                           COUNT(*) AS pedidos
                    FROM pedidos
                    GROUP BY dia_semana, hora
                    ORDER BY dia_semana, hora
                """)
                rows = cur.fetchall()
                if rows:
                    return jsonify([dict(r) for r in rows])
    except Exception:
        pass
    import random
    random.seed(7)
    data = []
    for dia in range(7):
        for hora in range(24):
            pedidos = max(0, int(random.gauss(5 if 12 <= hora <= 20 else 1, 2)))
            data.append({"dia_semana": dia, "hora": hora, "pedidos": pedidos})
    return jsonify(data)


@analytics_bp.get("/receita-mensal")
def receita_mensal():
    """GET /api/analytics/receita-mensal — revenue for the last 12 months."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT TO_CHAR(DATE_TRUNC('month', p.data), 'YYYY-MM') AS mes,
                           ROUND(SUM(p.quantidade * s.preco)::NUMERIC, 2) AS receita
                    FROM pedidos p
                    JOIN sabores s ON s.id = p.sabor_id
                    WHERE p.data >= NOW() - INTERVAL '12 months'
                    GROUP BY mes ORDER BY mes
                """)
                rows = cur.fetchall()
                if rows:
                    return jsonify([dict(r) for r in rows])
    except Exception:
        pass
    import random
    from datetime import date, timedelta
    random.seed(99)
    base = date.today().replace(day=1)
    data = []
    for i in range(11, -1, -1):
        d = base - timedelta(days=30 * i)
        data.append({"mes": d.strftime("%Y-%m"), "receita": round(random.uniform(1200, 4500), 2)})
    return jsonify(data)
