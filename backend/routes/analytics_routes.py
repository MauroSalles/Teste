"""Advanced analytics blueprint — /api/analytics/*

Provides richer business intelligence endpoints beyond the basic /api/status
summary, including revenue overview, sales trends, flavour ranking, stock
alert matrix, and cache diagnostics.
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

import backend.models.pedido as pedido_model
import backend.models.sabor as sabor_model
import backend.models.estoque as estoque_model
from backend import cache as _cache

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")
logger = logging.getLogger(__name__)

_CACHE_TTL = 120  # seconds


# ── Helpers ────────────────────────────────────────────────────────────────

def _safe_list(model_fn, *args, **kwargs):
    try:
        return list(model_fn(*args, **kwargs))
    except Exception as exc:
        logger.warning("analytics: model error — %s", exc)
        return []


# ── Routes ─────────────────────────────────────────────────────────────────

@analytics_bp.get("/overview")
def overview():
    """Comprehensive business overview — cached 2 min."""
    cache_key = "analytics:overview"
    cached = _cache.get(cache_key, _CACHE_TTL)
    if cached is not None:
        return jsonify(cached)

    sabores = _safe_list(sabor_model.listar_sabores)
    pedidos = _safe_list(pedido_model.listar_pedidos)
    estoque = _safe_list(estoque_model.ver_estoque)

    preco_map = {s["nome"]: float(s.get("preco", 0)) for s in sabores}
    receita = sum(
        float(p.get("quantidade", 0)) * preco_map.get(p.get("sabor", ""), 0.0)
        for p in pedidos
    )

    estoque_critico = [e for e in estoque if int(e.get("quantidade", 0)) == 0]
    estoque_baixo = [e for e in estoque if 0 < int(e.get("quantidade", 0)) < 5]
    estoque_saudavel = [
        e for e in estoque if int(e.get("quantidade", 0)) >= 5
    ]

    ticket_medio = (receita / len(pedidos)) if pedidos else 0.0

    result = {
        "resumo": {
            "total_sabores": len(sabores),
            "total_pedidos": len(pedidos),
            "receita_total": round(receita, 2),
            "ticket_medio": round(ticket_medio, 2),
        },
        "estoque": {
            "critico": len(estoque_critico),
            "baixo": len(estoque_baixo),
            "saudavel": len(estoque_saudavel),
            "itens_criticos": [dict(e) for e in estoque_critico],
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    _cache.set(cache_key, result, _CACHE_TTL)
    return jsonify(result)


@analytics_bp.get("/vendas/tendencia")
def tendencia_vendas():
    """Daily sales trend for the last N days (default 30).

    Query param: ``dias`` (int, 1–90).
    """
    try:
        dias = max(1, min(int(request.args.get("dias", 30)), 90))
    except (TypeError, ValueError):
        dias = 30

    cache_key = f"analytics:tendencia:{dias}"
    cached = _cache.get(cache_key, _CACHE_TTL)
    if cached is not None:
        return jsonify(cached)

    rows_diario = _safe_list(pedido_model.relatorio_vendas, "diario")
    rows_semanal = _safe_list(pedido_model.relatorio_vendas, "semanal")

    result = {
        "dias": dias,
        "diario": [dict(r) for r in rows_diario],
        "semanal": [dict(r) for r in rows_semanal],
    }

    _cache.set(cache_key, result, _CACHE_TTL)
    return jsonify(result)


@analytics_bp.get("/sabores/ranking")
def ranking_sabores():
    """Rank flavours by popularity and (optionally) average rating."""
    try:
        limit = max(1, min(int(request.args.get("limit", 10)), 50))
    except (TypeError, ValueError):
        limit = 10

    cache_key = f"analytics:sabores_ranking:{limit}"
    cached = _cache.get(cache_key, _CACHE_TTL)
    if cached is not None:
        return jsonify(cached)

    por_pedidos = _safe_list(pedido_model.sabores_populares, limit)

    result = {
        "limit": limit,
        "por_pedidos": [dict(r) for r in por_pedidos],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    _cache.set(cache_key, result, _CACHE_TTL)
    return jsonify(result)


@analytics_bp.get("/estoque/alertas")
def estoque_alertas():
    """Return stock alert matrix with criticality levels."""
    cache_key = "analytics:estoque_alertas"
    cached = _cache.get(cache_key, 60)
    if cached is not None:
        return jsonify(cached)

    estoque = _safe_list(estoque_model.ver_estoque)

    def _nivel(qty: int) -> str:
        if qty == 0:
            return "critico"
        if qty < 5:
            return "baixo"
        if qty < 15:
            return "normal"
        return "alto"

    items = [
        {**dict(e), "nivel": _nivel(int(e.get("quantidade", 0)))}
        for e in estoque
    ]
    items.sort(key=lambda x: x.get("quantidade", 0))

    result = {
        "total_itens": len(items),
        "criticos": sum(1 for i in items if i["nivel"] == "critico"),
        "baixos": sum(1 for i in items if i["nivel"] == "baixo"),
        "itens": items,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    _cache.set(cache_key, result, 60)
    return jsonify(result)


@analytics_bp.get("/cache/info")
def cache_info():
    """Return cache backend status (debug aid)."""
    return jsonify(_cache.info())
