"""001_initial_schema

Initial migration — represents the baseline schema from database/schema.sql
(sabores, pedidos, estoque, users, referral_conversions, user_badges,
daily_challenges, wheel_spins, fidelidade, estoque_sabores, pedidos_reposicao).

Revision ID: 001
Revises: (none)
Create Date: 2024-01-01
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS sabores (
            id     SERIAL PRIMARY KEY,
            nome   VARCHAR(100) NOT NULL,
            preco  DECIMAL(10, 2) NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id         SERIAL PRIMARY KEY,
            sabor_id   INTEGER NOT NULL REFERENCES sabores(id) ON DELETE CASCADE,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            data       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metodo_pagamento VARCHAR(30) DEFAULT 'dinheiro',
            status     VARCHAR(20) DEFAULT 'confirmado',
            observacao TEXT
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id        SERIAL PRIMARY KEY,
            sabor_id  INTEGER NOT NULL UNIQUE REFERENCES sabores(id) ON DELETE CASCADE,
            quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id             SERIAL PRIMARY KEY,
            name           VARCHAR(200) NOT NULL,
            email          VARCHAR(255) NOT NULL UNIQUE,
            password_hash  VARCHAR(255) NOT NULL,
            avatar_url     VARCHAR(500),
            level          INTEGER NOT NULL DEFAULT 1,
            total_points   INTEGER NOT NULL DEFAULT 0,
            level_updated_at TIMESTAMP,
            deleted_at     TIMESTAMP,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS referral_conversions (
            id           SERIAL PRIMARY KEY,
            referrer_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            referred_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            status       VARCHAR(50) NOT NULL DEFAULT 'pending',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS user_badges (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            badge_type  VARCHAR(100) NOT NULL,
            badge_data  JSONB,
            awarded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS daily_challenges (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            challenges JSONB NOT NULL,
            date       DATE NOT NULL DEFAULT CURRENT_DATE,
            UNIQUE (user_id, date)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS wheel_spins (
            id       SERIAL PRIMARY KEY,
            user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reward   VARCHAR(200) NOT NULL,
            spun_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS fidelidade (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            pontos     INTEGER NOT NULL DEFAULT 0,
            resgates   INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS estoque_sabores (
            id                    SERIAL PRIMARY KEY,
            nome                  VARCHAR(100) NOT NULL,
            volume_litros         DECIMAL(4,1) NOT NULL,
            categoria             VARCHAR(20)  NOT NULL CHECK (categoria IN ('açaí', 'sorvete')),
            em_exposicao          BOOLEAN      NOT NULL DEFAULT TRUE,
            quantidade_atual      INTEGER      NOT NULL DEFAULT 0 CHECK (quantidade_atual >= 0),
            estoque_minimo_sugestao INTEGER    NOT NULL DEFAULT 0 CHECK (estoque_minimo_sugestao >= 0),
            resposicao_rapida     BOOLEAN      NOT NULL DEFAULT FALSE,
            data_atualizacao      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (nome, volume_litros)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS pedidos_reposicao (
            id          SERIAL PRIMARY KEY,
            data_pedido TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            itens       JSONB     NOT NULL,
            observacao  TEXT,
            status      VARCHAR(20) NOT NULL DEFAULT 'pendente'
        )
    """)

    # Performance indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_data ON pedidos (data DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_sabor_id ON pedidos (sabor_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos (status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_fidelidade_user_id ON fidelidade (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_referral_referrer ON referral_conversions (referrer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_wheel_spins_user ON wheel_spins (user_id, spun_at DESC)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS pedidos_reposicao CASCADE")
    op.execute("DROP TABLE IF EXISTS estoque_sabores CASCADE")
    op.execute("DROP TABLE IF EXISTS fidelidade CASCADE")
    op.execute("DROP TABLE IF EXISTS wheel_spins CASCADE")
    op.execute("DROP TABLE IF EXISTS daily_challenges CASCADE")
    op.execute("DROP TABLE IF EXISTS user_badges CASCADE")
    op.execute("DROP TABLE IF EXISTS referral_conversions CASCADE")
    op.execute("DROP TABLE IF EXISTS estoque CASCADE")
    op.execute("DROP TABLE IF EXISTS pedidos CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS sabores CASCADE")
