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

-- Loyalty System Tables

CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    email      VARCHAR(200) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    device_id  VARCHAR(255),
    last_ip    VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS referral_codes (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES users(id),
    code       VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    status     VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS referrals (
    id               SERIAL PRIMARY KEY,
    referrer_id      INT NOT NULL REFERENCES users(id),
    referred_user_id INT NOT NULL REFERENCES users(id),
    created_at       TIMESTAMP DEFAULT NOW(),
    status           VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS orders (
    id              SERIAL PRIMARY KEY,
    user_id         INT REFERENCES users(id),
    total           DECIMAL(10, 2) NOT NULL DEFAULT 0,
    applied_coupon  VARCHAR(50),
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    final_total     DECIMAL(10, 2),
    status          VARCHAR(50) DEFAULT 'pending',
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS coupons (
    id                  SERIAL PRIMARY KEY,
    code                VARCHAR(50) UNIQUE NOT NULL,
    user_id             INT NOT NULL REFERENCES users(id),
    discount_percentage DECIMAL(5, 2),
    discount_type       VARCHAR(50),
    discount_value      DECIMAL(10, 2),
    max_uses            INT DEFAULT 1,
    current_uses        INT DEFAULT 0,
    valid_from          TIMESTAMP NOT NULL,
    valid_until         TIMESTAMP NOT NULL,
    min_order_value     DECIMAL(10, 2) DEFAULT 0,
    max_usage_per_order INT DEFAULT 1,
    tier_level          VARCHAR(20),
    created_at          TIMESTAMP DEFAULT NOW(),
    last_used_at        TIMESTAMP,
    status              VARCHAR(20) DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS idx_coupons_code      ON coupons (code);
CREATE INDEX IF NOT EXISTS idx_coupons_user_id   ON coupons (user_id);
CREATE INDEX IF NOT EXISTS idx_coupons_valid_until ON coupons (valid_until);

CREATE TABLE IF NOT EXISTS coupon_usage_log (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id),
    coupon_code     VARCHAR(50) NOT NULL,
    order_id        INT NOT NULL REFERENCES orders(id),
    discount_amount DECIMAL(10, 2) NOT NULL,
    used_at         TIMESTAMP DEFAULT NOW(),
    device_ip       VARCHAR(50),
    user_agent      TEXT
);

CREATE INDEX IF NOT EXISTS idx_coupon_usage_user_date ON coupon_usage_log (user_id, used_at);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_code      ON coupon_usage_log (coupon_code);

CREATE TABLE IF NOT EXISTS fraud_detection_log (
    id           SERIAL PRIMARY KEY,
    user_id      INT NOT NULL REFERENCES users(id),
    coupon_code  VARCHAR(50),
    reason       VARCHAR(255),
    action       VARCHAR(50),
    flagged_at   TIMESTAMP DEFAULT NOW(),
    resolved     BOOLEAN DEFAULT FALSE
);

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

