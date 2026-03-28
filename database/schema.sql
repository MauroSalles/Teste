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

-- Social Commerce tables

CREATE TABLE IF NOT EXISTS orders (
    id              SERIAL PRIMARY KEY,
    customer_phone  VARCHAR(30) NOT NULL,
    customer_name   VARCHAR(150) NOT NULL,
    flavor_id       INTEGER NOT NULL REFERENCES sabores(id) ON DELETE CASCADE,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    address         TEXT NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'pending_payment',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS instagram_posts (
    id                SERIAL PRIMARY KEY,
    post_id           VARCHAR(100) NOT NULL,
    flavor_id         INTEGER REFERENCES sabores(id) ON DELETE SET NULL,
    impressions       INTEGER NOT NULL DEFAULT 0,
    clicks            INTEGER NOT NULL DEFAULT 0,
    conversion_rate   DECIMAL(5, 4) NOT NULL DEFAULT 0,
    revenue_generated DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ugc_campaigns (
    id          SERIAL PRIMARY KEY,
    hashtag     VARCHAR(150) NOT NULL,
    prize_pool  DECIMAL(10, 2) NOT NULL,
    status      VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ugc_prizes (
    id           SERIAL PRIMARY KEY,
    post_id      VARCHAR(100) NOT NULL,
    prize_amount DECIMAL(10, 2) NOT NULL,
    reason       VARCHAR(255),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

