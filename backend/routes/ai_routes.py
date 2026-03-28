from flask import Blueprint, request, jsonify

from backend.ai.chatbot_service import ChatBotService
from backend.ai.recommendation_engine import RecommendationEngine
from backend.ai.forecasting_service import ForecastingService
from backend.ai.churn_prediction import ChurnPredictionService
from backend.ai.segmentation_service import SegmentationService
from backend.ai.sentiment_service import SentimentService

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

chatbot_service = ChatBotService()
recommendation_engine = RecommendationEngine()
forecasting_service = ForecastingService()
churn_service = ChurnPredictionService()
segmentation_service = SegmentationService()
sentiment_service = SentimentService()


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Chat com IA"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Campo "message" obrigatório'}), 400

    user_id = data.get('user_id', 0)
    result = chatbot_service.get_chat_response(
        user_id,
        data['message'],
        data.get('history', []),
    )
    return jsonify(result), 200 if result['success'] else 400


@ai_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Recomendações personalizadas"""
    user_id = request.args.get('user_id', 1, type=int)
    num = request.args.get('count', 5, type=int)
    result = recommendation_engine.get_recommendations(user_id, num)
    return jsonify(result), 200


@ai_bp.route('/forecast/<int:flavor_id>', methods=['GET'])
def forecast_flavor(flavor_id):
    """Prevê demanda de sabor"""
    days = request.args.get('days', 30, type=int)
    result = forecasting_service.forecast_demand(flavor_id, days)
    return jsonify(result), 200 if result['success'] else 400


@ai_bp.route('/churn/<int:user_id>', methods=['GET'])
def predict_churn(user_id):
    """Prediz risco de churn"""
    result = churn_service.predict_churn(user_id)
    return jsonify(result), 200 if result['success'] else 400


@ai_bp.route('/segments', methods=['GET'])
def get_segments():
    """Segmentação de clientes"""
    result = segmentation_service.segment_customers()
    return jsonify(result), 200 if result['success'] else 400


@ai_bp.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analisa sentimento de texto"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'success': False, 'error': 'Campo "text" obrigatório'}), 400

    result = sentiment_service.analyze_review(data['text'])
    return jsonify(result), 200 if result['success'] else 400
