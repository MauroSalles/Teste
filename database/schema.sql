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


-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id          SERIAL PRIMARY KEY,
    pedido_id   INTEGER REFERENCES pedidos(id) ON DELETE SET NULL,
    metodo      VARCHAR(50) NOT NULL CHECK (metodo IN ('stripe', 'pix', 'dinheiro')),
    status      VARCHAR(50) NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'aprovado', 'recusado', 'cancelado')),
    valor       DECIMAL(10, 2) NOT NULL,
    external_id VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Referral codes
CREATE TABLE IF NOT EXISTS referral_codes (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    code        VARCHAR(20) NOT NULL UNIQUE,
    referral_count INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Referral conversions
CREATE TABLE IF NOT EXISTS referral_conversions (
    id          SERIAL PRIMARY KEY,
    referrer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status      VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (referrer_id, referred_id)
);

-- Coupons
CREATE TABLE IF NOT EXISTS coupons (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50) NOT NULL UNIQUE,
    discount_pct    DECIMAL(5, 2) NOT NULL CHECK (discount_pct > 0 AND discount_pct <= 100),
    max_discount_brl DECIMAL(10, 2) NOT NULL DEFAULT 20.00,
    min_order_brl   DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    max_uses_per_day INTEGER NOT NULL DEFAULT 5,
    max_uses_per_month INTEGER NOT NULL DEFAULT 2,
    expiry_date     DATE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Coupon usage log
CREATE TABLE IF NOT EXISTS coupon_usage_log (
    id          SERIAL PRIMARY KEY,
    coupon_id   INTEGER NOT NULL REFERENCES coupons(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_value DECIMAL(10, 2) NOT NULL,
    discount_applied DECIMAL(10, 2) NOT NULL,
    used_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat logs (AI chatbot)
CREATE TABLE IF NOT EXISTS chat_logs (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    message     TEXT NOT NULL,
    response    TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product reviews
CREATE TABLE IF NOT EXISTS reviews (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    sabor_id    INTEGER REFERENCES sabores(id) ON DELETE CASCADE,
    rating      INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment     TEXT,
    sentiment   VARCHAR(20),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notification log
CREATE TABLE IF NOT EXISTS notification_log (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    type        VARCHAR(50) NOT NULL,
    channel     VARCHAR(50) NOT NULL DEFAULT 'email',
    subject     VARCHAR(255),
    status      VARCHAR(20) NOT NULL DEFAULT 'sent',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
