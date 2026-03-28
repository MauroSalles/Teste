import logging

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from backend.database import get_db

logger = logging.getLogger(__name__)

_N_FEATURES = 10


class ChurnPredictionService:
    """Identifica clientes em risco"""

    def __init__(self):
        self.model = self._build_model()

    def predict_churn(self, user_id):
        """Prediz chance de cliente sair"""
        try:
            features = self._extract_features(user_id)
            probability = float(self.model.predict_proba([features])[0][1])

            action = None
            if probability > 0.6:
                action = self._recommend_action(user_id, probability)

            return {
                'success': True,
                'user_id': user_id,
                'churn_probability': probability,
                'risk_level': (
                    'high' if probability > 0.6
                    else 'medium' if probability > 0.3
                    else 'low'
                ),
                'recommended_action': action,
            }
        except Exception as e:
            logger.error("Churn prediction error: %s", e)
            return {'success': False, 'error': str(e)}

    def _build_model(self):
        """Cria modelo RandomForest com dados sintéticos de bootstrap"""
        rng = np.random.default_rng(42)

        # Generate synthetic training data so the model is always ready
        n_samples = 100
        X = rng.random((n_samples, _N_FEATURES))
        # Simple rule: high days_since_last_order → churn
        y = (X[:, 3] > 0.6).astype(int)

        clf = RandomForestClassifier(n_estimators=10, random_state=42)
        clf.fit(X, y)
        return clf

    def _extract_features(self, user_id):
        """Extrai features para modelo"""
        user = self._get_user_stats(user_id)
        return [
            float(user.get('days_since_signup', 0)),
            float(user.get('total_orders', 0)),
            float(user.get('total_spent', 0.0)),
            float(user.get('days_since_last_order', 0)),
            float(user.get('order_frequency', 0.0)),
            float(user.get('average_order_value', 0.0)),
            float(user.get('lifetime_value', 0.0)),
            float(user.get('support_tickets', 0)),
            float(user.get('reviews_count', 0)),
            float(user.get('app_opens_last_30days', 0)),
        ]

    def _get_user_stats(self, user_id):
        """Calcula estatísticas agregadas de pedidos a partir do banco"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            COUNT(*)                    AS total_orders,
                            COALESCE(SUM(p.quantidade * s.preco), 0) AS total_spent,
                            COALESCE(
                                EXTRACT(DAY FROM NOW() - MAX(p.data)), 9999
                            )                           AS days_since_last_order,
                            COALESCE(AVG(p.quantidade * s.preco), 0) AS average_order_value
                        FROM pedidos p
                        JOIN sabores s ON p.sabor_id = s.id
                        """
                    )
                    row = cursor.fetchone()
                    if row:
                        return dict(row)
        except Exception:
            pass
        return {}

    def _recommend_action(self, user_id, probability):
        """Recomenda ação para reter cliente"""
        actions = {
            'send_discount': 'Envie cupom de 20% desconto',
            'send_personalized_offer': 'Ofereça seu sabor favorito com desconto',
            'send_loyalty_milestone': 'Mostre que está perto de próximo tier',
            'call_customer': 'Ligue para cliente (pessoal)',
            'gift_sample': 'Envie amostra gratis de novo sabor',
        }

        if probability > 0.8:
            return actions['call_customer']
        elif probability > 0.7:
            return actions['send_personalized_offer']
        else:
            return actions['send_discount']
