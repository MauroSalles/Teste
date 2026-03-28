from datetime import datetime

from flask import Blueprint, request, jsonify

from backend.integrations.instagram_commerce import InstagramCommerceService
from backend.integrations.whatsapp_commerce import WhatsAppCommerceService

social_bp = Blueprint('social', __name__, url_prefix='/api/social')
ig_service = InstagramCommerceService()
wa_service = WhatsAppCommerceService()


@social_bp.route('/instagram/create-shoppable', methods=['POST'])
def create_shoppable_post():
    """Admin: Cria post shoppable no Instagram"""
    data = request.json or {}
    required = ('flavor_id', 'image_url', 'caption', 'price')
    if any(k not in data for k in required):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    result = ig_service.create_shoppable_post(
        data['flavor_id'],
        data['image_url'],
        data['caption'],
        data['price'],
    )
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/instagram/live-event', methods=['POST'])
def create_live_shopping():
    """Admin: Cria evento de shopping ao vivo"""
    data = request.json or {}
    required = ('event_name', 'start_time', 'duration_minutes', 'flavors')
    if any(k not in data for k in required):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    result = ig_service.create_live_shopping_event(
        data['event_name'],
        datetime.fromisoformat(data['start_time']),
        data['duration_minutes'],
        data['flavors'],
    )
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/instagram/analytics', methods=['GET'])
def instagram_analytics():
    """Analisa o que converte no Instagram"""
    result = ig_service.get_instagram_feed_analytics()
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/whatsapp/send-catalog', methods=['POST'])
def send_whatsapp_catalog():
    """Envia catálogo ao customer via WhatsApp"""
    data = request.json or {}
    if 'phone' not in data:
        return jsonify({'success': False, 'error': 'Missing required field: phone'}), 400
    result = wa_service.send_flavor_catalog(data['phone'])
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/whatsapp/order', methods=['POST'])
def whatsapp_order():
    """Processa pedido via WhatsApp"""
    data = request.json or {}
    required = ('phone', 'name', 'flavor_id', 'quantity', 'address')
    if any(k not in data for k in required):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    result = wa_service.process_order_via_whatsapp(
        data['phone'],
        data['name'],
        data['flavor_id'],
        data['quantity'],
        data['address'],
    )
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/whatsapp/status', methods=['POST'])
def whatsapp_status():
    """Envia atualização de status do pedido via WhatsApp"""
    data = request.json or {}
    required = ('phone', 'order_id', 'status')
    if any(k not in data for k in required):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    result = wa_service.send_order_status_updates(
        data['phone'],
        data['order_id'],
        data['status'],
    )
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """Webhook para receber mensagens WhatsApp"""
    incoming = request.get_json() or {}
    if 'From' not in incoming or 'Body' not in incoming:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    result = wa_service.handle_incoming_whatsapp_message(incoming)
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/ugc/campaign', methods=['POST'])
def create_ugc_campaign():
    """Cria campanha de user generated content"""
    data = request.json or {}
    if 'hashtag' not in data or 'prize_pool' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    result = ig_service.create_user_generated_content_campaign(
        data['hashtag'],
        data['prize_pool'],
    )
    return jsonify(result), 200 if result['success'] else 400


@social_bp.route('/ugc/winners', methods=['GET'])
def get_ugc_winners():
    """Seleciona e premia vencedores UGC"""
    hashtag = request.args.get('hashtag')
    if not hashtag:
        return jsonify({'success': False, 'error': 'Missing required query param: hashtag'}), 400
    result = ig_service.monitor_ugc_posts(hashtag)
    return jsonify(result), 200 if result['success'] else 400
