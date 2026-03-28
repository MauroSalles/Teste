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

CREATE TABLE IF NOT EXISTS referral_links (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    referral_code    VARCHAR(50) UNIQUE NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status           VARCHAR(20) DEFAULT 'active',
    total_conversions INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS referral_conversions (
    id               SERIAL PRIMARY KEY,
    referrer_id      INTEGER NOT NULL,
    referred_user_id INTEGER NOT NULL,
    referral_code    VARCHAR(50) NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at     TIMESTAMP,
    status           VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS referral_rewards (
    id               SERIAL PRIMARY KEY,
    referrer_id      INTEGER NOT NULL,
    referred_user_id INTEGER NOT NULL,
    reward_type      VARCHAR(50),
    reward_value     DECIMAL(10, 2),
    status           VARCHAR(20) DEFAULT 'pending',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at       TIMESTAMP
);

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

