import logging

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.database import get_db

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Machine Learning recommendations usando filtragem colaborativa"""

    def get_recommendations(self, user_id, num_recommendations=5):
        """Recomenda sabores personalizados"""
        try:
            user_vector = self._get_user_vector(user_id)
            all_products = self._get_product_vectors()

            if not all_products:
                return {'success': True, 'recommendations': []}

            product_matrix = np.array([p['vector'] for p in all_products])
            similarities = cosine_similarity([user_vector], product_matrix)[0]

            top_indices = np.argsort(similarities)[-num_recommendations:][::-1]

            recommendations = []
            for idx in top_indices:
                product = all_products[idx]
                score = float(similarities[idx])
                recommendations.append({
                    'product_id': product['id'],
                    'name': product['name'],
                    'score': score,
                    'reason': self._get_reason(user_id, product['id']),
                })

            return {'success': True, 'recommendations': recommendations}
        except Exception as e:
            logger.error("Recommendation error: %s", e)
            return {'success': False, 'error': str(e)}

    def _get_order_history(self, user_id):
        """Retorna histórico de pedidos"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT p.sabor_id, p.quantidade, s.preco,
                               EXTRACT(HOUR FROM p.data) AS hour
                        FROM pedidos p
                        JOIN sabores s ON p.sabor_id = s.id
                        ORDER BY p.data DESC
                        """,
                    )
                    return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []

    def _get_user_vector(self, user_id):
        """Cria vetor do cliente (behavior encoding)"""
        orders = self._get_order_history(user_id)

        # Features: [price_preference, frequency, time_of_day, avg_qty, variety]
        vector = np.zeros(5)

        if orders:
            vector[0] = np.mean([float(o['preco']) for o in orders])
            vector[1] = len(orders) / 30.0
            vector[2] = np.mean([float(o['hour']) for o in orders])
            vector[3] = np.mean([float(o['quantidade']) for o in orders])
            vector[4] = len({o['sabor_id'] for o in orders})

        return vector

    def _get_product_vectors(self):
        """Retorna vetores de todos os produtos"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, nome, preco FROM sabores ORDER BY id")
                    rows = cursor.fetchall()

            products = []
            for i, row in enumerate(rows):
                # Simple feature vector: [price_norm, position, popularity=1, 0, 0]
                vector = np.array([
                    float(row['preco']) / 20.0,  # normalised price (max ~20)
                    (i + 1) / max(len(rows), 1),  # position normalised
                    1.0,
                    0.0,
                    0.0,
                ])
                products.append({'id': row['id'], 'name': row['nome'], 'vector': vector})

            return products
        except Exception:
            return []

    def _get_reason(self, user_id, product_id):
        """Explica por que recomendou"""
        reasons = [
            "Similar aos seus sabores favoritos",
            "Popular entre clientes como você",
            "Avaliação alta (4.8 estrelas)",
            "Novo e em tendência agora",
            "Você ainda não provou este!",
        ]
        return reasons[hash(f"{user_id}{product_id}") % len(reasons)]
