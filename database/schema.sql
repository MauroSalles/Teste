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

-- ── ERP EXPANSION TABLES ─────────────────────────────────────────────────

-- Customer loyalty & CRM
CREATE TABLE IF NOT EXISTS clientes (
    id                SERIAL PRIMARY KEY,
    nome              VARCHAR(100) NOT NULL,
    email             VARCHAR(100) UNIQUE,
    telefone          VARCHAR(20),
    pontos_fidelidade INTEGER     NOT NULL DEFAULT 0,
    tier              VARCHAR(20) NOT NULL DEFAULT 'Bronze',
    data_cadastro     TIMESTAMP            DEFAULT CURRENT_TIMESTAMP
);

-- Ingredients catalog
CREATE TABLE IF NOT EXISTS ingredientes (
    id                 SERIAL PRIMARY KEY,
    nome               VARCHAR(100)    NOT NULL,
    unidade            VARCHAR(20)     NOT NULL DEFAULT 'kg',
    preco_unitario     DECIMAL(10, 4)  NOT NULL DEFAULT 0,
    quantidade_atual   DECIMAL(10, 3)  NOT NULL DEFAULT 0,
    quantidade_minima  DECIMAL(10, 3)  NOT NULL DEFAULT 0,
    data_validade      DATE,
    data_cadastro      TIMESTAMP                DEFAULT CURRENT_TIMESTAMP
);

-- Price history (audit trail for price changes)
CREATE TABLE IF NOT EXISTS precos_historico (
    id             SERIAL PRIMARY KEY,
    sabor_id       INTEGER        NOT NULL REFERENCES sabores(id) ON DELETE CASCADE,
    preco_anterior DECIMAL(10, 2),
    preco_novo     DECIMAL(10, 2) NOT NULL,
    motivo         VARCHAR(200),
    data_mudanca   TIMESTAMP               DEFAULT CURRENT_TIMESTAMP
);

-- Cash register sessions
CREATE TABLE IF NOT EXISTS caixa (
    id                SERIAL PRIMARY KEY,
    data_abertura     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_fechamento   TIMESTAMP,
    valor_abertura    DECIMAL(10, 2) NOT NULL DEFAULT 0,
    valor_fechamento  DECIMAL(10, 2),
    status            VARCHAR(20)    NOT NULL DEFAULT 'aberto'
);

-- Expenses linked to a cash register session
CREATE TABLE IF NOT EXISTS despesas (
    id          SERIAL PRIMARY KEY,
    caixa_id    INTEGER        REFERENCES caixa(id) ON DELETE SET NULL,
    descricao   VARCHAR(200)   NOT NULL,
    valor       DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
    data        TIMESTAMP               DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

