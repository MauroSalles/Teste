-- Gelateria System - PostgreSQL Schema
-- Run this script to create the database structure

CREATE DATABASE gelateria;

\c gelateria;

-- Flavors table
CREATE TABLE sabores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    preco DECIMAL(10, 2) NOT NULL CHECK (preco > 0),
    disponivel BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(150),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for client lookup by name (used in every order)
CREATE INDEX idx_clientes_nome ON clientes (nome);

-- Orders table
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    sabor_id INTEGER REFERENCES sabores(id),
    quantidade INTEGER NOT NULL DEFAULT 1 CHECK (quantidade > 0),
    total DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock table
CREATE TABLE estoque (
    id SERIAL PRIMARY KEY,
    sabor_id INTEGER REFERENCES sabores(id) UNIQUE,
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed some initial flavors
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 8.50),
    ('Morango', 7.50),
    ('Baunilha', 7.00),
    ('Menta', 8.00),
    ('Pistache', 10.00);

-- Seed initial stock
INSERT INTO estoque (sabor_id, quantidade)
SELECT id, 100 FROM sabores;
