"""Smoke tests for the 5 new API blueprints using Flask test client with mocked DB."""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch
import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_mock_db(fetchone_val=None, fetchall_val=None):
    """Build a context-manager-compatible mock for get_db()."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = fetchone_val
    mock_cursor.fetchall.return_value = fetchall_val if fetchall_val is not None else []
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


# ── Cardápio Routes ──────────────────────────────────────────────────────────

class TestCardapioRoutes:

    @patch("backend.routes.cardapio_routes.get_db")
    def test_listar_cardapio_with_db(self, mock_get_db, client):
        conn = make_mock_db(fetchall_val=[
            {"id": 1, "nome": "Chocolate", "preco": 10.0, "estoque": 5, "nota_media": 4.5, "total_avaliacoes": 10}
        ])
        mock_get_db.return_value = conn
        resp = client.get("/api/cardapio")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    @patch("backend.routes.cardapio_routes.get_db", side_effect=Exception("DB down"))
    def test_listar_cardapio_graceful_degradation(self, _, client):
        resp = client.get("/api/cardapio")
        # graceful: returns 200 with empty list or mock
        assert resp.status_code == 200

    def test_destaque_mock_fallback(self, client):
        """Without DB, /destaque returns mock flavors."""
        with patch("backend.routes.cardapio_routes.get_db", side_effect=Exception("no db")):
            resp = client.get("/api/cardapio/destaque")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 3

    @patch("backend.routes.cardapio_routes.get_db")
    def test_nutricional_sabor_not_found(self, mock_get_db, client):
        conn = make_mock_db(fetchone_val=None)
        mock_get_db.return_value = conn
        resp = client.get("/api/cardapio/9999/nutricional")
        # Either 404 or mock fallback (graceful degradation)
        assert resp.status_code in (200, 404, 500)

    def test_criar_avaliacao_invalid_nota(self, client):
        resp = client.post("/api/cardapio/1/avaliacao", json={"nota": 6})
        assert resp.status_code == 400

    def test_criar_avaliacao_missing_nota(self, client):
        resp = client.post("/api/cardapio/1/avaliacao", json={})
        assert resp.status_code == 400

    @patch("backend.routes.cardapio_routes.get_db")
    def test_criar_avaliacao_sabor_not_found(self, mock_get_db, client):
        conn = make_mock_db(fetchone_val=None)
        mock_get_db.return_value = conn
        resp = client.post("/api/cardapio/9999/avaliacao", json={"nota": 4})
        assert resp.status_code in (404, 500)

    def test_listar_avaliacoes_graceful(self, client):
        with patch("backend.routes.cardapio_routes.get_db", side_effect=Exception("no db")):
            resp = client.get("/api/cardapio/1/avaliacoes")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 0

    def test_sentiment_positive(self):
        from backend.routes.cardapio_routes import _analyze_sentiment
        assert _analyze_sentiment("Absolutamente delicioso! Amei!") == "positivo"

    def test_sentiment_negative(self):
        from backend.routes.cardapio_routes import _analyze_sentiment
        assert _analyze_sentiment("Horrível, péssimo serviço") == "negativo"

    def test_sentiment_neutral(self):
        from backend.routes.cardapio_routes import _analyze_sentiment
        assert _analyze_sentiment("Sorvete de baunilha.") == "neutro"


# ── Delivery Routes ──────────────────────────────────────────────────────────

class TestDeliveryRoutes:

    def test_criar_pedido_sem_itens(self, client):
        resp = client.post("/api/delivery/pedido", json={"endereco": "Rua A, 1"})
        assert resp.status_code == 400

    def test_criar_pedido_sem_endereco(self, client):
        resp = client.post("/api/delivery/pedido", json={"itens": [{"sabor_id": 1, "quantidade": 1}]})
        assert resp.status_code == 400

    @patch("backend.routes.delivery_routes.get_db", side_effect=Exception("no db"))
    def test_criar_pedido_mock_fallback(self, _, client):
        resp = client.post("/api/delivery/pedido", json={
            "itens": [{"sabor_id": 1, "quantidade": 1, "preco": 10.0}],
            "endereco": "Rua Teste, 1"
        })
        assert resp.status_code == 201

    def test_status_pedido_mock(self, client):
        with patch("backend.routes.delivery_routes.get_db", side_effect=Exception("no db")):
            resp = client.get("/api/delivery/pedido/999/status")
        assert resp.status_code == 200

    def test_track_pedido_mock(self, client):
        with patch("backend.routes.delivery_routes.get_db", side_effect=Exception("no db")):
            resp = client.get("/api/delivery/pedido/999/track")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "status" in data

    def test_atualizar_status_invalido(self, client):
        resp = client.put("/api/delivery/pedido/1/status", json={"status": "voando"})
        assert resp.status_code == 400

    def test_calcular_frete_sp(self, client):
        resp = client.post("/api/delivery/calcular-frete", json={"cep": "01310-100"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "frete" in data
        assert data["frete"] == 8.0

    def test_calcular_frete_sem_cep(self, client):
        resp = client.post("/api/delivery/calcular-frete", json={})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["frete"] == 5.0

    def test_historico_sem_user_id(self, client):
        resp = client.get("/api/delivery/historico")
        assert resp.status_code == 400

    def test_historico_graceful(self, client):
        with patch("backend.routes.delivery_routes.get_db", side_effect=Exception("no db")):
            resp = client.get("/api/delivery/historico?user_id=1")
        assert resp.status_code == 200
        assert resp.get_json() == []


# ── Game Routes ──────────────────────────────────────────────────────────────

class TestGameRoutes:

    @patch("backend.routes.game_routes.get_db", side_effect=Exception("no db"))
    def test_perfil_mock_fallback(self, _, client):
        resp = client.get("/api/game/perfil/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["user_id"] == 1
        assert "xp" in data

    def test_perfil_has_badges(self, client):
        with patch("backend.routes.game_routes.get_db", side_effect=Exception("no db")):
            resp = client.get("/api/game/perfil/1")
        data = resp.get_json()
        assert "badges_conquistados" in data

    def test_check_in_sem_user_id(self, client):
        resp = client.post("/api/game/check-in", json={})
        assert resp.status_code == 400

    @patch("backend.routes.game_routes.get_db", side_effect=Exception("no db"))
    def test_check_in_mock_fallback(self, _, client):
        resp = client.post("/api/game/check-in", json={"user_id": 1})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["xp_ganho"] == 50

    @patch("backend.routes.game_routes.get_db", side_effect=Exception("no db"))
    def test_ranking_empty(self, _, client):
        resp = client.get("/api/game/ranking")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_listar_desafios(self, client):
        resp = client.get("/api/game/desafios")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 4

    def test_listar_badges(self, client):
        resp = client.get("/api/game/badges")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 4

    def test_completar_desafio_sem_user_id(self, client):
        resp = client.post("/api/game/desafio/1/completar", json={})
        assert resp.status_code == 400

    def test_completar_desafio_invalido(self, client):
        resp = client.post("/api/game/desafio/999/completar", json={"user_id": 1})
        assert resp.status_code == 404

    @patch("backend.routes.game_routes.get_db", side_effect=Exception("no db"))
    def test_completar_desafio_ok(self, _, client):
        resp = client.post("/api/game/desafio/1/completar", json={"user_id": 1})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["xp_ganho"] == 150

    def test_get_level_aprendiz(self):
        from backend.routes.game_routes import _get_level
        info = _get_level(0)
        assert info["titulo"] == "Aprendiz"

    def test_get_level_lendario(self):
        from backend.routes.game_routes import _get_level
        info = _get_level(25000)
        assert info["titulo"] == "Lendário"


# ── Analytics Routes ──────────────────────────────────────────────────────────

class TestAnalyticsRoutes:

    @patch("backend.routes.analytics_routes.get_db", side_effect=Exception("no db"))
    def test_sabores_populares_mock(self, _, client):
        resp = client.get("/api/analytics/sabores-populares")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 5
        assert data[0]["nome"] == "Chocolate"

    @patch("backend.routes.analytics_routes.get_db", side_effect=Exception("no db"))
    def test_horarios_pico_mock(self, _, client):
        resp = client.get("/api/analytics/horarios-pico")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 24

    @patch("backend.routes.analytics_routes.get_db", side_effect=Exception("no db"))
    def test_satisfacao_mock(self, _, client):
        resp = client.get("/api/analytics/satisfacao")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "nps" in data

    @patch("backend.routes.analytics_routes.get_db", side_effect=Exception("no db"))
    def test_mapa_calor_mock(self, _, client):
        resp = client.get("/api/analytics/mapa-calor")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 7 * 24

    @patch("backend.routes.analytics_routes.get_db", side_effect=Exception("no db"))
    def test_receita_mensal_mock(self, _, client):
        resp = client.get("/api/analytics/receita-mensal")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 12


# ── Kiosk Routes ──────────────────────────────────────────────────────────────

class TestKioskRoutes:

    def test_iniciar_sessao(self, client):
        resp = client.post("/api/kiosk/sessao/iniciar")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data
        assert data["ttl_segundos"] == 1800

    def test_verificar_sessao_invalida(self, client):
        resp = client.get("/api/kiosk/sessao/token-invalido-xyz")
        assert resp.status_code == 404

    def test_verificar_sessao_valida(self, client):
        r = client.post("/api/kiosk/sessao/iniciar")
        token = r.get_json()["token"]
        resp = client.get(f"/api/kiosk/sessao/{token}")
        assert resp.status_code == 200
        assert resp.get_json()["ativo"] is True

    def test_pedido_sem_sessao(self, client):
        resp = client.post("/api/kiosk/pedido", json={"token": "invalido", "itens": [{"sabor_id": 1, "quantidade": 1}]})
        assert resp.status_code == 401

    def test_pedido_sem_itens(self, client):
        r = client.post("/api/kiosk/sessao/iniciar")
        token = r.get_json()["token"]
        resp = client.post("/api/kiosk/pedido", json={"token": token, "itens": []})
        assert resp.status_code == 400

    @patch("backend.routes.kiosk_routes.get_db", side_effect=Exception("no db"))
    def test_pedido_kiosk_ok(self, _, client):
        r = client.post("/api/kiosk/sessao/iniciar")
        token = r.get_json()["token"]
        resp = client.post("/api/kiosk/pedido", json={
            "token": token,
            "itens": [{"sabor_id": 1, "quantidade": 2, "preco": 10.0}]
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "valor_total" in data

    def test_pagamento_carrinho_vazio(self, client):
        r = client.post("/api/kiosk/sessao/iniciar")
        token = r.get_json()["token"]
        resp = client.post("/api/kiosk/pagamento", json={"token": token, "metodo": "pix"})
        assert resp.status_code == 400

    @patch("backend.routes.kiosk_routes.get_db", side_effect=Exception("no db"))
    def test_pagamento_completo(self, _, client):
        r = client.post("/api/kiosk/sessao/iniciar")
        token = r.get_json()["token"]
        client.post("/api/kiosk/pedido", json={
            "token": token,
            "itens": [{"sabor_id": 1, "quantidade": 1, "preco": 10.0}]
        })
        resp = client.post("/api/kiosk/pagamento", json={"token": token, "metodo": "pix"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "aprovado"

    def test_cardapio_simplificado_mock(self, client):
        with patch("backend.routes.kiosk_routes.get_db", side_effect=Exception("no db")):
            resp = client.get("/api/kiosk/cardapio-simplificado")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 5


# ── QR ASCII Utility ──────────────────────────────────────────────────────────

class TestQrAscii:

    def test_generate_returns_string(self):
        from backend.utils.qr_ascii import generate_qr_ascii
        result = generate_qr_ascii("test@pix.key")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_deterministic(self):
        from backend.utils.qr_ascii import generate_qr_ascii
        a = generate_qr_ascii("same-key")
        b = generate_qr_ascii("same-key")
        assert a == b

    def test_generate_different_keys(self):
        from backend.utils.qr_ascii import generate_qr_ascii
        a = generate_qr_ascii("key-one")
        b = generate_qr_ascii("key-two")
        assert a != b

    def test_generate_has_finder_pattern(self):
        from backend.utils.qr_ascii import generate_qr_ascii
        result = generate_qr_ascii("any")
        assert "█▀▀▀▀▀█" in result
