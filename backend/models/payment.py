import logging

logger = logging.getLogger(__name__)


class PaymentModel:
    """Stores and retrieves payment history in the database."""

    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS payments (
            id               SERIAL PRIMARY KEY,
            order_id         INTEGER NOT NULL,
            user_id          INTEGER NOT NULL,
            amount           DECIMAL(10, 2) NOT NULL,
            method           VARCHAR(50) NOT NULL,
            status           VARCHAR(50) NOT NULL DEFAULT 'pending',
            transaction_id   VARCHAR(255) UNIQUE,
            stripe_payment_id VARCHAR(255),
            pix_qr_code      TEXT,
            metadata         JSONB,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """

    def __init__(self, get_db):
        """
        :param get_db: callable context-manager that yields a psycopg2 connection.
        """
        self._get_db = get_db
        self._ensure_table()

    def _ensure_table(self):
        with self._get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(self.CREATE_TABLE_SQL)

    def record_payment(self, order_id, user_id, amount, method, transaction_id, metadata=None):
        """Insert a new payment record with status='pending'."""
        sql = """
            INSERT INTO payments
                (order_id, user_id, amount, method, status, transaction_id, metadata)
            VALUES (%s, %s, %s, %s, 'pending', %s, %s)
            RETURNING id
        """
        with self._get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (order_id, user_id, amount, method, transaction_id, metadata))
                row = cur.fetchone()
                return row["id"] if row else None

    def update_status(self, payment_id, status):
        """Update payment status and refresh updated_at."""
        sql = """
            UPDATE payments
               SET status = %s, updated_at = CURRENT_TIMESTAMP
             WHERE id = %s
        """
        with self._get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (status, payment_id))

    def get_payment_history(self, user_id, limit=10):
        """Return the most recent payments for a user."""
        sql = """
            SELECT * FROM payments
             WHERE user_id = %s
             ORDER BY created_at DESC
             LIMIT %s
        """
        with self._get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id, limit))
                return cur.fetchall()

    def get_by_transaction_id(self, transaction_id):
        """Look up a payment by its external transaction identifier."""
        sql = "SELECT * FROM payments WHERE transaction_id = %s LIMIT 1"
        with self._get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (transaction_id,))
                return cur.fetchone()
