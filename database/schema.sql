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

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;
