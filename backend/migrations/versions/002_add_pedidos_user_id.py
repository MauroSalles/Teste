"""002_add_pedidos_user_id

Adds user_id column to pedidos table with FK to users(id).

Revision ID: 002
Revises: 001
Create Date: 2024-01-02
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'pedidos' AND column_name = 'user_id'
          ) THEN
            ALTER TABLE pedidos ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
            CREATE INDEX IF NOT EXISTS idx_pedidos_user_id ON pedidos (user_id);
          END IF;
        END$$;
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_pedidos_user_id")
    op.execute("""
        ALTER TABLE pedidos DROP COLUMN IF EXISTS user_id
    """)
