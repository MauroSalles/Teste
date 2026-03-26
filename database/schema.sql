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

CREATE TABLE IF NOT EXISTS payments (
    id                SERIAL PRIMARY KEY,
    order_id          INTEGER NOT NULL,
    user_id           INTEGER NOT NULL,
    amount            DECIMAL(10, 2) NOT NULL,
    method            VARCHAR(50) NOT NULL,
    status            VARCHAR(50) NOT NULL DEFAULT 'pending',
    transaction_id    VARCHAR(255) UNIQUE,
    stripe_payment_id VARCHAR(255),
    pix_qr_code       TEXT,
    metadata          JSONB,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

