import logging

from textblob import TextBlob

from backend.database import get_db

logger = logging.getLogger(__name__)


class SentimentService:
    """Analisa sentimento de reviews"""

    def analyze_review(self, review_text):
        """Analisa sentimento de um review"""
        try:
            blob = TextBlob(review_text)
            polarity = blob.sentiment.polarity        # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1

            if polarity > 0.5:
                sentiment = 'positive'
            elif polarity < -0.5:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            return {
                'success': True,
                'sentiment': sentiment,
                'polarity': float(polarity),
                'subjectivity': float(subjectivity),
                'confidence': float(subjectivity),
            }
        except Exception as e:
            logger.error("Sentiment analysis error: %s", e)
            return {'success': False, 'error': str(e)}

    def batch_analyze(self, review_ids):
        """Analisa múltiplos reviews"""
        results = {}
        for review_id in review_ids:
            review = self._get_review(review_id)
            if review:
                sentiment = self.analyze_review(review['text'])
                self._update_review_sentiment(review_id, sentiment.get('sentiment'))
                results[review_id] = sentiment
        return results

    def _get_review(self, review_id):
        """Busca review pelo ID"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, text FROM reviews WHERE id = %s", (review_id,))
                    row = cursor.fetchone()
                    return dict(row) if row else None
        except Exception:
            return None

    def _update_review_sentiment(self, review_id, sentiment):
        """Atualiza sentimento no banco"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE reviews SET sentiment = %s WHERE id = %s",
                        (sentiment, review_id),
                    )
        except Exception as e:
            logger.warning("Failed to update review sentiment: %s", e)
