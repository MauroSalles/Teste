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

-- ── New tables for Gelateria Pro upgrade ─────────────────────────────────────

CREATE TABLE IF NOT EXISTS payments (
    id         SERIAL PRIMARY KEY,
    pedido_id  INTEGER REFERENCES pedidos(id),
    metodo     VARCHAR(50),
    status     VARCHAR(50) DEFAULT 'pendente',
    valor      DECIMAL(10, 2),
    stripe_id  VARCHAR(255),
    pix_txid   VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_logs (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    message    TEXT,
    response   TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    sabor_id   INTEGER REFERENCES sabores(id),
    rating     INTEGER CHECK (rating >= 1 AND rating <= 5),
    comentario TEXT,
    sentiment  VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS referral_codes (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) UNIQUE,
    code       VARCHAR(20) UNIQUE NOT NULL,
    tier       INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS referrals (
    id               SERIAL PRIMARY KEY,
    referral_code_id INTEGER REFERENCES referral_codes(id),
    referred_user_id INTEGER REFERENCES users(id) UNIQUE,
    status           VARCHAR(50) DEFAULT 'pending',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coupons (
    id                 SERIAL PRIMARY KEY,
    code               VARCHAR(50) UNIQUE NOT NULL,
    discount_pct       DECIMAL(5, 2),
    min_order          DECIMAL(10, 2) DEFAULT 0,
    max_uses_per_user  INTEGER DEFAULT 2,
    max_uses_daily     INTEGER DEFAULT 5,
    expires_at         TIMESTAMP,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coupon_usage_log (
    id         SERIAL PRIMARY KEY,
    coupon_id  INTEGER REFERENCES coupons(id),
    user_id    INTEGER REFERENCES users(id),
    pedido_id  INTEGER REFERENCES pedidos(id),
    used_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notification_log (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    type       VARCHAR(50),
    channel    VARCHAR(50),
    status     VARCHAR(50),
    payload    JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Indexes for performance ───────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_payments_pedido_id   ON payments(pedido_id);
CREATE INDEX IF NOT EXISTS idx_payments_status       ON payments(status);
CREATE INDEX IF NOT EXISTS idx_chat_logs_user_id     ON chat_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id       ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_sabor_id      ON reviews(sabor_id);
CREATE INDEX IF NOT EXISTS idx_referral_codes_code   ON referral_codes(code);
CREATE INDEX IF NOT EXISTS idx_referrals_code_id     ON referrals(referral_code_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_coupon   ON coupon_usage_log(coupon_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_user     ON coupon_usage_log(user_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_used_at  ON coupon_usage_log(used_at);
CREATE INDEX IF NOT EXISTS idx_notification_user_id  ON notification_log(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_created  ON notification_log(created_at);

