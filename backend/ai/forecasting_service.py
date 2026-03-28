import logging

import numpy as np
import pandas as pd
from prophet import Prophet

from backend.database import get_db

logger = logging.getLogger(__name__)

_MIN_PROPHET_ROWS = 2


class ForecastingService:
    """Previsão de demanda com Prophet"""

    def forecast_demand(self, flavor_id, days=30):
        """Prevê demanda dos próximos X dias"""
        try:
            historical_data = self._get_sales_history(flavor_id, days=90)

            if len(historical_data) < _MIN_PROPHET_ROWS:
                # Not enough history — return zero-filled forecast
                predictions = [
                    {
                        'date': (pd.Timestamp.today() + pd.Timedelta(days=i + 1)).strftime('%Y-%m-%d'),
                        'predicted_quantity': 0,
                        'lower_bound': 0,
                        'upper_bound': 0,
                    }
                    for i in range(days)
                ]
                return {'success': True, 'flavor_id': flavor_id, 'predictions': predictions}

            df = pd.DataFrame({
                'ds': [h['date'] for h in historical_data],
                'y': [float(h['quantity']) for h in historical_data],
            })

            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                interval_width=0.95,
            )
            model.fit(df)

            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)

            predictions = []
            for _, row in forecast.tail(days).iterrows():
                predictions.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_quantity': int(max(0, row['yhat'])),
                    'lower_bound': int(max(0, row['yhat_lower'])),
                    'upper_bound': int(max(0, row['yhat_upper'])),
                })

            return {'success': True, 'flavor_id': flavor_id, 'predictions': predictions}
        except Exception as e:
            logger.error("Forecasting error: %s", e)
            return {'success': False, 'error': str(e)}

    def forecast_all_flavors(self):
        """Prevê demanda de TODOS os sabores"""
        flavors = self._get_all_flavors()
        forecasts = {}
        for flavor in flavors:
            forecast = self.forecast_demand(flavor['id'])
            if forecast['success']:
                forecasts[flavor['id']] = forecast['predictions']
        return forecasts

    def _get_sales_history(self, flavor_id, days=90):
        """Retorna histórico de vendas por sabor"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT DATE(data) AS date, SUM(quantidade) AS quantity
                        FROM pedidos
                        WHERE sabor_id = %s
                          AND data >= CURRENT_DATE - INTERVAL '%s days'
                        GROUP BY DATE(data)
                        ORDER BY date
                        """,
                        (flavor_id, days),
                    )
                    return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []

    def _get_all_flavors(self):
        """Retorna todos os sabores"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, nome FROM sabores ORDER BY id")
                    return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []
