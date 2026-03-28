import logging
from datetime import datetime

import numpy as np
from sklearn.cluster import KMeans

from backend.database import get_db

logger = logging.getLogger(__name__)

_N_SEGMENTS = 4
_SEGMENT_NAMES = ['champions', 'loyal_customers', 'at_risk', 'lost']


class SegmentationService:
    """Segmenta clientes por RFM"""

    def segment_customers(self):
        """RFM: Recency, Frequency, Monetary"""
        try:
            customers = self._calculate_rfm_all()

            if len(customers) < _N_SEGMENTS:
                # Not enough customers to cluster — assign all to 'champions'
                segments = {name: [] for name in _SEGMENT_NAMES}
                for customer in customers:
                    segments['champions'].append(customer)
                return {
                    'success': True,
                    'segments': segments,
                    'total_customers': len(customers),
                }

            X = np.array([
                [c['recency'], c['frequency'], c['monetary']]
                for c in customers
            ], dtype=float)

            kmeans = KMeans(n_clusters=_N_SEGMENTS, random_state=42, n_init='auto')
            clusters = kmeans.fit_predict(X)

            segments = {name: [] for name in _SEGMENT_NAMES}
            for customer, cluster in zip(customers, clusters):
                segments[_SEGMENT_NAMES[int(cluster)]].append(customer)

            return {
                'success': True,
                'segments': segments,
                'total_customers': len(customers),
            }
        except Exception as e:
            logger.error("Segmentation error: %s", e)
            return {'success': False, 'error': str(e)}

    def _calculate_rfm_all(self):
        """Calcula RFM de todos os sabores (grouped by sabor)"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            p.sabor_id                            AS sabor_id,
                            s.nome                               AS name,
                            EXTRACT(DAY FROM NOW() - MAX(p.data)) AS recency,
                            COUNT(*)                              AS frequency,
                            SUM(p.quantidade * s.preco)           AS monetary
                        FROM pedidos p
                        JOIN sabores s ON p.sabor_id = s.id
                        GROUP BY p.sabor_id, s.nome
                        """
                    )
                    rows = cursor.fetchall()

            rfm_data = []
            for row in rows:
                rfm_data.append({
                    'sabor_id': row['sabor_id'],
                    'name': row['name'],
                    'recency': float(row['recency'] or 0),
                    'frequency': int(row['frequency']),
                    'monetary': float(row['monetary'] or 0),
                })

            return rfm_data
        except Exception:
            return []
