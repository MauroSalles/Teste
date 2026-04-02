-- Gelateria System — PostgreSQL Schema

CREATE TABLE IF NOT EXISTS sabores (
    id     SERIAL PRIMARY KEY,
    nome   VARCHAR(100) NOT NULL,
    preco  DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS pedidos (
    id         SERIAL PRIMARY KEY,
    sabor_id   INTEGER NOT NULL REFERENCES sabores(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS estoque (
    id        SERIAL PRIMARY KEY,
    sabor_id  INTEGER NOT NULL UNIQUE REFERENCES sabores(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0)
);

-- Users table (for gamification / loyalty system)
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
);

-- Referral conversions (used by leaderboard & loyalty)
CREATE TABLE IF NOT EXISTS referral_conversions (
    id           SERIAL PRIMARY KEY,
    referrer_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status       VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User badges (gamification)
CREATE TABLE IF NOT EXISTS user_badges (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_type  VARCHAR(100) NOT NULL,
    badge_data  JSONB,
    awarded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily challenges (gamification)
CREATE TABLE IF NOT EXISTS daily_challenges (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenges JSONB NOT NULL,
    date       DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (user_id, date)
);

-- Wheel spins (gamification)
CREATE TABLE IF NOT EXISTS wheel_spins (
    id       SERIAL PRIMARY KEY,
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reward   VARCHAR(200) NOT NULL,
    spun_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loyalty points (fidelidade)
CREATE TABLE IF NOT EXISTS fidelidade (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    pontos     INTEGER NOT NULL DEFAULT 0,
    resgates   INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- Partners & Marketplace (FEATURE_MARKETPLACE)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS partners (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(200) NOT NULL,
    email        VARCHAR(255) NOT NULL UNIQUE,
    api_key      VARCHAR(128) NOT NULL UNIQUE,
    plan         VARCHAR(50) NOT NULL DEFAULT 'free',  -- free | starter | pro
    active       BOOLEAN NOT NULL DEFAULT TRUE,
    metadata     JSONB,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Franchise Portal (FEATURE_FRANCHISE_PORTAL)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS franchises (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(200) NOT NULL,
    owner_name     VARCHAR(200) NOT NULL,
    email          VARCHAR(255) NOT NULL UNIQUE,
    city           VARCHAR(100),
    country        VARCHAR(100) NOT NULL DEFAULT 'Brazil',
    status         VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending | active | suspended
    partner_id     INTEGER REFERENCES partners(id) ON DELETE SET NULL,
    opened_at      DATE,
    metadata       JSONB,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Feature flag overrides per tenant (stored preferences override env vars)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS feature_flag_overrides (
    id         SERIAL PRIMARY KEY,
    tenant_id  VARCHAR(100) NOT NULL,
    flag_name  VARCHAR(100) NOT NULL,
    enabled    BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tenant_id, flag_name)
);
