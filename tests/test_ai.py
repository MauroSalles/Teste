import pytest

from backend.ai.recommendation_engine import RecommendationEngine
from backend.ai.churn_prediction import ChurnPredictionService
from backend.ai.forecasting_service import ForecastingService
from backend.ai.sentiment_service import SentimentService
from backend.ai.segmentation_service import SegmentationService


class TestRecommendationEngine:
    def test_recommendations_success(self):
        engine = RecommendationEngine()
        result = engine.get_recommendations(1, num_recommendations=5)
        assert result['success']
        assert len(result['recommendations']) <= 5

    def test_recommendations_empty_user(self):
        """User with no orders still returns success"""
        engine = RecommendationEngine()
        result = engine.get_recommendations(99999, num_recommendations=5)
        assert result['success']
        assert isinstance(result['recommendations'], list)


class TestChurnPrediction:
    def test_churn_prediction_success(self):
        service = ChurnPredictionService()
        result = service.predict_churn(1)
        assert result['success']
        assert 'churn_probability' in result
        assert 0 <= result['churn_probability'] <= 1

    def test_churn_prediction_risk_levels(self):
        service = ChurnPredictionService()
        result = service.predict_churn(1)
        assert result['risk_level'] in ('low', 'medium', 'high')


class TestForecastingService:
    def test_forecast_demand(self):
        service = ForecastingService()
        result = service.forecast_demand(1, days=30)
        assert result['success']
        assert len(result['predictions']) == 30

    def test_forecast_prediction_keys(self):
        service = ForecastingService()
        result = service.forecast_demand(1, days=7)
        assert result['success']
        for pred in result['predictions']:
            assert 'date' in pred
            assert 'predicted_quantity' in pred
            assert pred['predicted_quantity'] >= 0


class TestSentimentService:
    def test_positive_sentiment(self):
        service = SentimentService()
        result = service.analyze_review("This is absolutely wonderful and amazing!")
        assert result['success']
        assert result['sentiment'] in ('positive', 'neutral', 'negative')
        assert -1 <= result['polarity'] <= 1
        assert 0 <= result['subjectivity'] <= 1

    def test_negative_sentiment(self):
        service = SentimentService()
        result = service.analyze_review("This is terrible, awful and disgusting!")
        assert result['success']
        assert result['sentiment'] in ('positive', 'neutral', 'negative')

    def test_neutral_sentiment(self):
        service = SentimentService()
        result = service.analyze_review("The product was delivered.")
        assert result['success']

    def test_confidence_range(self):
        service = SentimentService()
        result = service.analyze_review("Nice")
        assert result['success']
        assert 0 <= result['confidence'] <= 1


class TestSegmentationService:
    def test_segment_customers(self):
        service = SegmentationService()
        result = service.segment_customers()
        assert result['success']
        assert 'segments' in result
        assert 'total_customers' in result

    def test_segment_keys(self):
        service = SegmentationService()
        result = service.segment_customers()
        assert result['success']
        for key in ('champions', 'loyal_customers', 'at_risk', 'lost'):
            assert key in result['segments']


class TestAIRoutes:
    def test_chat_missing_message(self, client):
        response = client.post('/api/ai/chat', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert not data['success']

    def test_recommendations_route(self, client):
        response = client.get('/api/ai/recommendations?user_id=1&count=3')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']
        assert len(data['recommendations']) <= 3

    def test_forecast_route(self, client):
        response = client.get('/api/ai/forecast/1?days=30')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']
        assert len(data['predictions']) == 30

    def test_churn_route(self, client):
        response = client.get('/api/ai/churn/1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']

    def test_segments_route(self, client):
        response = client.get('/api/ai/segments')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']

    def test_sentiment_route(self, client):
        response = client.post('/api/ai/sentiment', json={'text': 'Delicioso!'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']

    def test_sentiment_missing_text(self, client):
        response = client.post('/api/ai/sentiment', json={})
        assert response.status_code == 400
