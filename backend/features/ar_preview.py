from flask import Blueprint, request, jsonify

from backend.database import get_db

ar_bp = Blueprint('ar', __name__, url_prefix='/api/ar')


class ARPreviewService:
    """Visualizar açaí em AR antes de comprar"""

    def _get_flavor(self, flavor_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nome AS name, preco AS price FROM sabores WHERE id = %s",
                    (flavor_id,),
                )
                return cur.fetchone()

    def _generate_ar_preview(self, flavor_id, custom_toppings):
        """Generate an AR preview URL for the given flavor and toppings (stub)."""
        app_url = __import__('os').getenv('APP_URL', 'https://example.com')
        toppings_str = ','.join(str(t) for t in custom_toppings)
        return f"{app_url}/ar/preview/{flavor_id}?toppings={toppings_str}"

    def _calculate_price_with_toppings(self, flavor_id, custom_toppings):
        """Calculate the price of a flavor with extra toppings."""
        flavor = self._get_flavor(flavor_id)
        if not flavor:
            return 0
        topping_price = len(custom_toppings) * 1.50
        return float(flavor['price']) + topping_price

    def get_ar_model(self, flavor_id):
        """Retorna modelo 3D do açaí com toppings específicos"""
        try:
            flavor = self._get_flavor(flavor_id)
            if not flavor:
                return {'success': False, 'error': 'Sabor não encontrado'}

            toppings = flavor.get('toppings', [])
            model = {
                'model_url': '/models/acai_base.gltf',
                'textures': {
                    'bowl': '/textures/bowl.png',
                    'acai': f"/textures/acai_{flavor.get('color', 'default')}.png",
                    'toppings': [f'/textures/topping_{t}.png' for t in toppings],
                },
                'animations': ['spin_360', 'zoom_in', 'toppings_fall'],
            }

            return {'success': True, 'model': model, 'flavor': dict(flavor)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def customize_ar_model(self, flavor_id, custom_toppings):
        """User customiza modelo em tempo real"""
        try:
            updated_model = {
                'base_flavor': flavor_id,
                'custom_toppings': custom_toppings,
                'preview_url': self._generate_ar_preview(flavor_id, custom_toppings),
                'estimated_price': self._calculate_price_with_toppings(flavor_id, custom_toppings),
            }

            return {'success': True, 'model': updated_model}
        except Exception as e:
            return {'success': False, 'error': str(e)}


@ar_bp.route('/model/<int:flavor_id>', methods=['GET'])
def get_ar_model(flavor_id):
    service = ARPreviewService()
    result = service.get_ar_model(flavor_id)
    return jsonify(result), 200 if result['success'] else 400


@ar_bp.route('/customize', methods=['POST'])
def customize_ar():
    data = request.json or {}
    if 'flavor_id' not in data or 'custom_toppings' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    service = ARPreviewService()
    result = service.customize_ar_model(
        data['flavor_id'],
        data['custom_toppings'],
    )
    return jsonify(result), 200 if result['success'] else 400
