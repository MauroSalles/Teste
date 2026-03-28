import os
from datetime import datetime
from decimal import Decimal

import requests

from backend.database import get_db


class InstagramCommerceService:
    """Vender direto do Instagram - Stories, Feed, DMs"""

    def __init__(self):
        self.fb_api_url = "https://graph.instagram.com"
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.ig_business_account_id = os.getenv('IG_BUSINESS_ACCOUNT_ID')

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _get_flavor(self, flavor_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nome AS name, preco AS price FROM sabores WHERE id = %s",
                    (flavor_id,),
                )
                return cur.fetchone()

    def _get_ig_product_id(self, flavor_id):
        """Map internal flavor id to an Instagram product id (stub)."""
        return str(flavor_id)

    def _get_hashtag_id(self, hashtag):
        """Fetch Instagram hashtag id via Graph API."""
        response = requests.get(
            f"{self.fb_api_url}/ig_hashtag_search",
            params={
                'user_id': self.ig_business_account_id,
                'q': hashtag,
                'access_token': self.access_token,
            },
        )
        return response.json()['data'][0]['id']

    def _add_product_to_live(self, broadcast_id, flavor, start_time, duration_minutes):
        """Schedule a product to appear during a live broadcast."""
        requests.post(
            f"{self.fb_api_url}/{broadcast_id}/products",
            params={'access_token': self.access_token},
            json={
                'product_id': self._get_ig_product_id(flavor.get('id', flavor)),
                'start_time': int(start_time.timestamp()),
            },
        )

    def _credit_ugc_prize(self, post_id, prize, reason):
        """Record a UGC prize credit in the database."""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ugc_prizes (post_id, prize_amount, reason, created_at)
                    VALUES (%s, %s, %s, NOW())
                    """,
                    (post_id, prize, reason),
                )

    def _send_notification_all_users(self, title, body):
        """Broadcast an in-app notification to all users (stub)."""
        pass

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def create_shoppable_post(self, flavor_id, image_url, caption, price):
        """Cria post shoppable no Instagram"""
        try:
            self._get_flavor(flavor_id)

            media_data = {
                'image_url': image_url,
                'caption': caption,
                'user_id': self.ig_business_account_id,
            }

            media_response = requests.post(
                f"{self.fb_api_url}/{self.ig_business_account_id}/media",
                params={'access_token': self.access_token},
                json=media_data,
            )
            media_id = media_response.json()['id']

            product_tags = {
                'user_id': self.ig_business_account_id,
                'media_id': media_id,
                'products': [
                    {
                        'x': 0.5,
                        'y': 0.5,
                        'product_id': self._get_ig_product_id(flavor_id),
                    }
                ],
            }

            requests.post(
                f"{self.fb_api_url}/{media_id}/product_tags",
                params={'access_token': self.access_token},
                json=product_tags,
            )

            requests.post(
                f"{self.fb_api_url}/{media_id}/publish",
                params={'access_token': self.access_token},
            )

            return {
                'success': True,
                'post_id': media_id,
                'post_url': f'https://instagram.com/p/{media_id}',
                'shoppable': True,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_live_shopping_event(self, event_name, start_time, duration_minutes, flavors):
        """Evento ao vivo com vendas direto do live"""
        try:
            event_data = {
                'broadcast_title': event_name,
                'status': 'LIVE',
                'description': f'🎉 Vendendo {len(flavors)} sabores exclusivos!',
                'start_time': int(start_time.timestamp()),
                'planned_reaches': 5000,
            }

            broadcast = requests.post(
                f"{self.fb_api_url}/{self.ig_business_account_id}/live_videos",
                params={'access_token': self.access_token},
                json=event_data,
            )
            broadcast_id = broadcast.json()['id']

            for flavor in flavors:
                self._add_product_to_live(broadcast_id, flavor, start_time, duration_minutes)

            return {
                'success': True,
                'event_id': broadcast_id,
                'event_name': event_name,
                'start_time': start_time.isoformat(),
                'discount': '30% OFF durante live!',
                'products': flavors,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_instagram_feed_analytics(self):
        """Analytics do feed para ver o que converte"""
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            post_id,
                            flavor_id,
                            impressions,
                            clicks,
                            conversion_rate,
                            revenue_generated
                        FROM instagram_posts
                        WHERE created_at > NOW() - INTERVAL '30 days'
                        ORDER BY revenue_generated DESC
                        LIMIT 20
                        """
                    )
                    posts = cur.fetchall()

            if not posts:
                return {
                    'success': True,
                    'top_posts': [],
                    'total_impressions': 0,
                    'total_clicks': 0,
                    'avg_conversion_rate': 0,
                    'total_revenue': 0,
                }

            return {
                'success': True,
                'top_posts': list(posts),
                'total_impressions': sum(p['impressions'] for p in posts),
                'total_clicks': sum(p['clicks'] for p in posts),
                'avg_conversion_rate': sum(p['conversion_rate'] for p in posts) / len(posts),
                'total_revenue': sum(p['revenue_generated'] for p in posts),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_user_generated_content_campaign(self, hashtag, prize_pool):
        """
        Usuários compartilham fotos com hashtag.
        Top 3 fotos ganham prêmios.
        """
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO ugc_campaigns (hashtag, prize_pool, status, created_at)
                        VALUES (%s, %s, %s, NOW())
                        """,
                        (hashtag, prize_pool, 'active'),
                    )

            self._send_notification_all_users(
                f'📸 Concurso de fotos! Use {hashtag} e ganhe prêmios!',
                'Compartilhe sua melhor foto de açaí',
            )

            return {
                'success': True,
                'campaign': {
                    'hashtag': hashtag,
                    'prize_pool': prize_pool,
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'contest_rules': [
                        f'Use #{hashtag}',
                        'Marque @nossa_acaiteria',
                        'Você pode ganhar R$100 crédito!',
                        'Valido por 30 dias',
                    ],
                },
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def monitor_ugc_posts(self, hashtag):
        """Monitora posts com hashtag e seleciona melhores"""
        try:
            hashtag_id = self._get_hashtag_id(hashtag)

            posts = requests.get(
                f"{self.fb_api_url}/{hashtag_id}/recent_media",
                params={
                    'fields': 'id,caption,media_type,media_url,like_count,comments_count',
                    'access_token': self.access_token,
                },
            ).json()['data']

            posts_ranked = sorted(
                posts,
                key=lambda p: p['like_count'] + p['comments_count'],
                reverse=True,
            )

            winners = posts_ranked[:3]
            prize_amounts = [Decimal('100.00'), Decimal('75.00'), Decimal('50.00')]

            for i, post in enumerate(winners, 1):
                prize = prize_amounts[i - 1]
                self._credit_ugc_prize(
                    post['id'],
                    prize,
                    f'{i}º lugar - UGC Contest',
                )

            return {
                'success': True,
                'winners': winners,
                'prizes_distributed': sum(prize_amounts[:len(winners)]),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
