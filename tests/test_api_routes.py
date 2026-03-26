"""
Unit tests for the REST API routes using Flask test client.
All DB calls are patched so no real PostgreSQL is needed.
"""
from datetime import date
from unittest.mock import patch, MagicMock
import pytest
import json


@pytest.fixture
def app():
    import os
    os.environ.setdefault("FLASK_ENV", "testing")
    os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
    from backend.app import create_app
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_ok(client):
    with patch("backend.database.get_pool") as mock_pool:
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_pool.return_value.getconn.return_value = mock_conn
        mock_pool.return_value.putconn = MagicMock()
        resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "gelateria-backend"


# ── /cmd ──────────────────────────────────────────────────────────────────────

def test_cmd_missing_body(client):
    resp = client.post("/cmd", content_type="application/json", data="{}")
    assert resp.status_code == 400


def test_cmd_too_long(client):
    resp = client.post(
        "/cmd",
        json={"comando": "a" * 501},
    )
    assert resp.status_code == 400


@patch("backend.services.cmd_service.listar_sabores", return_value=[])
def test_cmd_listar_sabores(mock_ls, client):
    resp = client.post("/cmd", json={"comando": "listar sabores"})
    assert resp.status_code == 200
    assert "resposta" in resp.get_json()


# ── /api/dashboard/kpis ──────────────────────────────────────────────────────

_KPI_MOCK = {
    "total_pedidos": 5, "pedidos_hoje": 1,
    "faturamento_total": 50.0, "faturamento_hoje": 10.0,
    "faturamento_mes": 40.0, "ticket_medio": 10.0,
}
_TOP_MOCK = [{"id": 1, "nome": "Choc", "preco": 10.0, "unidades_vendidas": 3, "faturamento": 30.0}]


@patch("backend.routes.api_routes.kpis_gerais", return_value=_KPI_MOCK)
@patch("backend.routes.api_routes.top_sabores", return_value=_TOP_MOCK)
@patch("backend.routes.api_routes.ingredientes_em_alerta", return_value=[])
@patch("backend.routes.api_routes.caixa_atual", return_value=None)
def test_dashboard_kpis(m1, m2, m3, m4, client):
    resp = client.get("/api/dashboard/kpis")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "kpis" in data
    assert data["kpis"]["total_pedidos"] == 5
    assert data["caixa_aberta"] is False
    assert len(data["top_sabores"]) == 1


# ── /api/analytics/top-sabores ───────────────────────────────────────────────

@patch("backend.routes.api_routes.top_sabores", return_value=_TOP_MOCK)
def test_top_sabores_api(mock_tops, client):
    resp = client.get("/api/analytics/top-sabores?limite=3")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data[0]["nome"] == "Choc"


# ── /api/relatorios/faturamento ──────────────────────────────────────────────

@patch("backend.routes.api_routes.faturamento_por_periodo", return_value=[
    {"dia": date(2025, 1, 1), "pedidos": 2, "unidades": 4, "faturamento": 40.0}
])
def test_relatorio_faturamento(mock_fat, client):
    resp = client.get("/api/relatorios/faturamento?inicio=2025-01-01&fim=2025-01-31")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data[0]["faturamento"] == 40.0


def test_relatorio_faturamento_data_invalida(client):
    resp = client.get("/api/relatorios/faturamento?inicio=notadate")
    assert resp.status_code == 400


# ── /api/clientes ─────────────────────────────────────────────────────────────

@patch("backend.routes.api_routes.listar_clientes", return_value=[])
def test_get_clientes_empty(mock_lc, client):
    resp = client.get("/api/clientes")
    assert resp.status_code == 200
    assert resp.get_json() == []


@patch("backend.routes.api_routes.adicionar_cliente", return_value={
    "id": 1, "nome": "Ana", "email": None, "telefone": None,
    "pontos_fidelidade": 0, "tier": "Bronze"
})
def test_post_cliente(mock_add, client):
    resp = client.post("/api/clientes", json={"nome": "Ana"})
    assert resp.status_code == 201
    assert resp.get_json()["nome"] == "Ana"


def test_post_cliente_sem_nome(client):
    resp = client.post("/api/clientes", json={"email": "x@x.com"})
    assert resp.status_code == 400


# ── /api/fidelidade/pontos ────────────────────────────────────────────────────

@patch("backend.routes.api_routes.adicionar_pontos", return_value={
    "id": 1, "nome": "Ana", "pontos_fidelidade": 50, "tier": "Bronze"
})
def test_post_pontos(mock_add, client):
    resp = client.post("/api/fidelidade/pontos", json={"cliente_id": 1, "pontos": 50})
    assert resp.status_code == 200
    assert resp.get_json()["pontos_fidelidade"] == 50


def test_post_pontos_sem_campos(client):
    resp = client.post("/api/fidelidade/pontos", json={"cliente_id": 1})
    assert resp.status_code == 400


def test_post_pontos_negativo(client):
    resp = client.post("/api/fidelidade/pontos", json={"cliente_id": 1, "pontos": -5})
    assert resp.status_code == 400


@patch("backend.routes.api_routes.adicionar_pontos", return_value=None)
def test_post_pontos_cliente_nao_encontrado(mock_add, client):
    resp = client.post("/api/fidelidade/pontos", json={"cliente_id": 999, "pontos": 10})
    assert resp.status_code == 404


# ── /api/ingredientes ─────────────────────────────────────────────────────────

@patch("backend.routes.api_routes.listar_ingredientes", return_value=[])
def test_get_ingredientes_empty(mock_li, client):
    resp = client.get("/api/ingredientes")
    assert resp.status_code == 200


@patch("backend.routes.api_routes.adicionar_ingrediente", return_value={
    "id": 1, "nome": "Leite", "unidade": "litro", "preco_unitario": 3.5,
    "quantidade_atual": 0, "quantidade_minima": 0, "data_validade": None
})
def test_post_ingrediente(mock_add, client):
    resp = client.post("/api/ingredientes", json={"nome": "Leite", "unidade": "litro", "preco_unitario": 3.5})
    assert resp.status_code == 201


def test_post_ingrediente_sem_nome(client):
    resp = client.post("/api/ingredientes", json={"unidade": "kg"})
    assert resp.status_code == 400


@patch("backend.routes.api_routes.ingredientes_em_alerta", return_value=[])
def test_get_alertas_ingredientes(mock_alerta, client):
    resp = client.get("/api/ingredientes/alerta")
    assert resp.status_code == 200
    assert resp.get_json() == []


# ── /api/caixa/atual ──────────────────────────────────────────────────────────

@patch("backend.routes.api_routes.caixa_atual", return_value=None)
def test_get_caixa_fechado(mock_caixa, client):
    resp = client.get("/api/caixa/atual")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "fechado"
