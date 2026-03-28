"""Tests for social commerce routes and services."""
import json
from unittest.mock import patch, MagicMock


# ------------------------------------------------------------------ #
# Instagram routes                                                     #
# ------------------------------------------------------------------ #

class TestInstagramRoutes:
    def test_create_shoppable_post_missing_fields(self, client):
        """Route should return 400 when required fields are missing."""
        response = client.post(
            '/api/social/instagram/create-shoppable',
            json={},
            content_type='application/json',
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_instagram_analytics_route_exists(self, client):
        """Analytics endpoint should be reachable (mocked DB)."""
        with patch(
            'backend.integrations.instagram_commerce.get_db'
        ) as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_get_db.return_value = mock_conn

            response = client.get('/api/social/instagram/analytics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_create_shoppable_post_service_error(self, client):
        """If Instagram API fails the route should still return JSON."""
        with patch.object(
            __import__(
                'backend.integrations.instagram_commerce',
                fromlist=['InstagramCommerceService'],
            ).InstagramCommerceService,
            'create_shoppable_post',
            return_value={'success': False, 'error': 'api error'},
        ):
            response = client.post(
                '/api/social/instagram/create-shoppable',
                json={
                    'flavor_id': 1,
                    'image_url': 'https://example.com/img.jpg',
                    'caption': 'Test',
                    'price': '25.00',
                },
                content_type='application/json',
            )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


# ------------------------------------------------------------------ #
# WhatsApp routes                                                      #
# ------------------------------------------------------------------ #

class TestWhatsAppRoutes:
    def test_send_catalog_missing_phone(self, client):
        """Endpoint should return 400 when 'phone' field is missing."""
        response = client.post(
            '/api/social/whatsapp/send-catalog',
            json={},
            content_type='application/json',
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_webhook_default_reply(self, client):
        """Webhook for an unrecognised message should return success or error JSON."""
        with patch.object(
            __import__(
                'backend.integrations.whatsapp_commerce',
                fromlist=['WhatsAppCommerceService'],
            ).WhatsAppCommerceService,
            'handle_incoming_whatsapp_message',
            return_value={'success': True, 'message_sid': 'SMtest'},
        ):
            response = client.post(
                '/api/social/whatsapp/webhook',
                json={'From': 'whatsapp:+5511999999999', 'Body': 'hello'},
                content_type='application/json',
            )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


# ------------------------------------------------------------------ #
# AR preview routes                                                    #
# ------------------------------------------------------------------ #

class TestARPreviewRoutes:
    def test_get_ar_model_not_found(self, client):
        """Non-existent flavor should return 400."""
        with patch(
            'backend.features.ar_preview.get_db'
        ) as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_get_db.return_value = mock_conn

            response = client.get('/api/ar/model/9999')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_get_ar_model_found(self, client):
        """Existing flavor should return 200 with model data."""
        fake_flavor = {
            'id': 1, 'name': 'Chocolate', 'price': 10.0, 'color': 'dark', 'toppings': [],
        }
        with patch(
            'backend.features.ar_preview.get_db'
        ) as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = fake_flavor
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_get_db.return_value = mock_conn

            response = client.get('/api/ar/model/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'model' in data

    def test_customize_ar_model(self, client):
        """Customize endpoint should return updated model."""
        fake_flavor = {'id': 1, 'name': 'Chocolate', 'price': 10.0}
        with patch(
            'backend.features.ar_preview.get_db'
        ) as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = fake_flavor
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_get_db.return_value = mock_conn

            response = client.post(
                '/api/ar/customize',
                json={'flavor_id': 1, 'custom_toppings': ['granola', 'banana']},
                content_type='application/json',
            )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['model']['base_flavor'] == 1


# ------------------------------------------------------------------ #
# UGC routes                                                           #
# ------------------------------------------------------------------ #

class TestUGCRoutes:
    def test_create_ugc_campaign_success(self, client):
        """UGC campaign creation should succeed when DB write is mocked."""
        with patch(
            'backend.integrations.instagram_commerce.get_db'
        ) as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_get_db.return_value = mock_conn

            response = client.post(
                '/api/social/ugc/campaign',
                json={'hashtag': 'acailover', 'prize_pool': '225.00'},
                content_type='application/json',
            )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['campaign']['hashtag'] == 'acailover'
