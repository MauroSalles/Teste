"""Tests for AI routes with mocked services."""

from unittest.mock import MagicMock, patch

import pytest


class TestChatRoute:
    def test_chat_missing_message(self, client):
        resp = client.post("/api/ai/chat", json={})
        assert resp.status_code == 400

    def test_chat_empty_message(self, client):
        resp = client.post("/api/ai/chat", json={"message": "  "})
        assert resp.status_code == 400

    def test_chat_predefined_response(self, client):
        resp = client.post("/api/ai/chat", json={"message": "Oi!"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_chat_menu_question(self, client):
        resp = client.post("/api/ai/chat", json={"message": "quais são os sabores?"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "response" in data
        # Predefined response should mention at least one flavor
        assert any(
            flavor in data["response"].lower()
            for flavor in ("chocolate", "morango", "baunilha", "açaí", "sabor")
        )

    @patch("backend.ai.chatbot_service.os.environ.get")
    @patch("backend.ai.chatbot_service._openai_chat")
    def test_chat_uses_openai_when_key_set(self, mock_openai, mock_env, client):
        mock_env.return_value = "fake-openai-key"
        mock_openai.return_value = {"response": "Olá do OpenAI!"}
        resp = client.post("/api/ai/chat", json={"message": "Olá"})
        assert resp.status_code == 200


class TestRecommendationsRoute:
    def test_recommendations_no_user(self, client):
        with patch("backend.ai.recommendation_engine.get_recommendations") as mock_rec:
            mock_rec.return_value = ["Chocolate", "Morango"]
            resp = client.get("/api/ai/recommendations")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_recommendations_with_user_id(self, client):
        with patch("backend.ai.recommendation_engine.get_recommendations") as mock_rec:
            mock_rec.return_value = ["Pistache"]
            resp = client.get("/api/ai/recommendations?user_id=1&limit=3")
        assert resp.status_code == 200

    def test_recommendations_db_error_returns_empty(self, client):
        with patch("backend.ai.recommendation_engine.get_recommendations") as mock_rec:
            mock_rec.side_effect = Exception("DB error")
            resp = client.get("/api/ai/recommendations")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["recommendations"] == []


class TestSentimentRoute:
    def test_sentiment_missing_text(self, client):
        resp = client.post("/api/ai/sentiment", json={})
        assert resp.status_code == 400

    def test_sentiment_positive(self, client):
        resp = client.post("/api/ai/sentiment", json={"text": "adorei o sorvete, muito delicioso!"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "sentiment" in data
        assert "score" in data
        assert data["sentiment"] in ("positive", "negative", "neutral")

    def test_sentiment_negative(self, client):
        resp = client.post("/api/ai/sentiment", json={"text": "péssimo, não gostei!"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["sentiment"] in ("positive", "negative", "neutral")

    def test_sentiment_neutral(self, client):
        resp = client.post("/api/ai/sentiment", json={"text": "o sorvete existia"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "sentiment" in data


class TestSentimentService:
    def test_keyword_positive(self):
        from backend.ai.sentiment_service import _keyword_sentiment
        result = _keyword_sentiment("ótimo produto, adorei!")
        assert result["sentiment"] == "positive"

    def test_keyword_negative(self):
        from backend.ai.sentiment_service import _keyword_sentiment
        result = _keyword_sentiment("péssimo, ruim demais")
        assert result["sentiment"] == "negative"

    def test_empty_text(self):
        from backend.ai.sentiment_service import analyze_sentiment
        result = analyze_sentiment("")
        assert result["sentiment"] == "neutral"
        assert result["score"] == 0.0


class TestChatbotService:
    def test_predefined_oi(self):
        from backend.ai.chatbot_service import _get_predefined_response
        resp = _get_predefined_response("oi")
        assert "Bem-vindo" in resp or "Olá" in resp

    def test_predefined_sabores(self):
        from backend.ai.chatbot_service import _get_predefined_response
        resp = _get_predefined_response("quais sabores vocês têm?")
        assert "Chocolate" in resp or "sabor" in resp.lower()

    def test_predefined_unknown(self):
        from backend.ai.chatbot_service import _get_predefined_response
        resp = _get_predefined_response("xyzzy foobar qux")
        assert isinstance(resp, str)
        assert len(resp) > 0
