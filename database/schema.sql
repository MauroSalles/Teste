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

-- ── Self-service flavor inventory (estoque_sabores) ──────────────────────────
CREATE TABLE IF NOT EXISTS estoque_sabores (
    id                    SERIAL PRIMARY KEY,
    nome                  VARCHAR(100) NOT NULL,
    volume_litros         DECIMAL(4,1) NOT NULL,
    categoria             VARCHAR(20)  NOT NULL CHECK (categoria IN ('açaí', 'sorvete')),
    em_exposicao          BOOLEAN      NOT NULL DEFAULT TRUE,
    quantidade_atual      INTEGER      NOT NULL DEFAULT 0 CHECK (quantidade_atual >= 0),
    estoque_minimo_sugestao INTEGER    NOT NULL DEFAULT 0 CHECK (estoque_minimo_sugestao >= 0),
    resposicao_rapida     BOOLEAN      NOT NULL DEFAULT FALSE,
    data_atualizacao      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nome, volume_litros)
);

-- Weekly replenishment orders log
CREATE TABLE IF NOT EXISTS pedidos_reposicao (
    id          SERIAL PRIMARY KEY,
    data_pedido TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    itens       JSONB     NOT NULL,
    observacao  TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'pendente'
);

-- Pre-populate all self-service flavors
INSERT INTO estoque_sabores (nome, volume_litros, categoria, em_exposicao, estoque_minimo_sugestao, resposicao_rapida) VALUES
    -- Açaí
    ('Açaí tradicional',    10.0, 'açaí',    TRUE, 10, TRUE),
    ('Açaí grego',          10.0, 'açaí',    TRUE,  6, TRUE),
    ('Açaí com morango',    10.0, 'açaí',    TRUE,  0, FALSE),
    ('Açaí Black',          10.0, 'açaí',    TRUE,  0, FALSE),
    ('Açaí zero',           10.0, 'açaí',    TRUE,  0, FALSE),
    ('Açaí trufado',        10.0, 'açaí',    TRUE,  0, FALSE),
    ('Açaí ninho',          10.0, 'açaí',    TRUE,  0, FALSE),
    ('Açaí paçoca',         10.0, 'açaí',    TRUE,  0, FALSE),
    ('Açaí cupuaçu',         5.0, 'açaí',    TRUE,  0, FALSE),
    ('Açaí banana',          5.0, 'açaí',    TRUE,  0, FALSE),
    -- Sorvetes
    ('Menta com chocolate', 10.0, 'sorvete', TRUE,  0, FALSE),
    ('Chocolate belga',     10.0, 'sorvete', TRUE,  1, TRUE),
    ('Pistache',            10.0, 'sorvete', TRUE,  0, FALSE),
    ('Côco',                10.0, 'sorvete', TRUE,  1, TRUE),
    ('Cappuccino',          10.0, 'sorvete', TRUE,  0, FALSE),
    ('Doce de leite',       10.0, 'sorvete', TRUE,  0, FALSE),
    ('Grego maracujá',      10.0, 'sorvete', TRUE,  0, FALSE),
    ('Grego Cereja',        10.0, 'sorvete', TRUE,  0, FALSE),
    ('Unicórnio',           10.0, 'sorvete', TRUE,  0, FALSE),
    ('Pitaya',              10.0, 'sorvete', TRUE,  1, TRUE),
    ('Limão',               10.0, 'sorvete', TRUE,  0, FALSE),
    ('Morango',             10.0, 'sorvete', TRUE,  0, FALSE),
    ('Flocos',              10.0, 'sorvete', TRUE,  0, FALSE),
    ('Manga',                5.0, 'sorvete', TRUE,  0, FALSE),
    ('Abacaxi',              5.0, 'sorvete', TRUE,  0, FALSE),
    ('Banana caramelizada',  5.0, 'sorvete', TRUE,  0, FALSE),
    ('Paçoca',               5.0, 'sorvete', TRUE,  0, FALSE),
    ('Chocolate branco',     5.0, 'sorvete', TRUE,  0, FALSE),
    ('Baunilha',             5.0, 'sorvete', TRUE,  0, FALSE),
    ('Laranja',              5.0, 'sorvete', TRUE,  0, FALSE),
    ('Café',                 5.0, 'sorvete', TRUE,  0, FALSE),
    ('Goiaba',               5.0, 'sorvete', TRUE,  0, FALSE),
    ('Mamão',                5.0, 'sorvete', TRUE,  0, FALSE),
    ('Algodão doce',         5.0, 'sorvete', TRUE,  0, FALSE),
    ('Creme de cupuaçu',     5.0, 'sorvete', TRUE,  0, FALSE),
    ('Milho verde',          5.0, 'sorvete', TRUE,  0, FALSE)
ON CONFLICT (nome, volume_litros) DO NOTHING;

-- ── Pedidos: add payment & status columns ────────────────────────────────────
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'pedidos' AND column_name = 'metodo_pagamento'
  ) THEN
    ALTER TABLE pedidos ADD COLUMN metodo_pagamento VARCHAR(30) DEFAULT 'dinheiro';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'pedidos' AND column_name = 'status'
  ) THEN
    ALTER TABLE pedidos ADD COLUMN status VARCHAR(20) DEFAULT 'confirmado';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'pedidos' AND column_name = 'observacao'
  ) THEN
    ALTER TABLE pedidos ADD COLUMN observacao TEXT;
  END IF;
END$$;

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;


-- Flavor ratings / reviews
CREATE TABLE IF NOT EXISTS avaliacoes (
    id SERIAL PRIMARY KEY,
    sabor_id INTEGER REFERENCES sabores(id) ON DELETE CASCADE,
    user_id INTEGER,
    nota INTEGER CHECK (nota BETWEEN 1 AND 5),
    comentario TEXT,
    sentimento VARCHAR(20) DEFAULT 'neutro',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Nutritional info per flavor
CREATE TABLE IF NOT EXISTS info_nutricional (
    id SERIAL PRIMARY KEY,
    sabor_id INTEGER UNIQUE REFERENCES sabores(id) ON DELETE CASCADE,
    calorias INTEGER DEFAULT 150,
    gorduras DECIMAL DEFAULT 4.5,
    carboidratos DECIMAL DEFAULT 28.0,
    proteinas DECIMAL DEFAULT 3.0,
    acucar DECIMAL DEFAULT 22.0,
    porcao_gramas INTEGER DEFAULT 100
);

-- Gamification profiles
CREATE TABLE IF NOT EXISTS game_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
    xp INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    last_checkin DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Badge catalog
CREATE TABLE IF NOT EXISTS badges (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    descricao TEXT,
    icone VARCHAR(10),
    xp_requerido INTEGER DEFAULT 0
);

-- User earned badges
CREATE TABLE IF NOT EXISTS user_game_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    badge_id INTEGER REFERENCES badges(id),
    earned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

-- Challenges catalog
CREATE TABLE IF NOT EXISTS desafios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200),
    descricao TEXT,
    xp_recompensa INTEGER DEFAULT 100,
    ativo BOOLEAN DEFAULT TRUE
);

-- User challenge progress
CREATE TABLE IF NOT EXISTS user_desafios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    desafio_id INTEGER REFERENCES desafios(id),
    concluido BOOLEAN DEFAULT FALSE,
    progresso INTEGER DEFAULT 0,
    completed_at TIMESTAMP
);

-- Delivery orders
CREATE TABLE IF NOT EXISTS delivery_pedidos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    itens JSONB NOT NULL DEFAULT '[]',
    endereco TEXT,
    cep VARCHAR(9),
    status VARCHAR(50) DEFAULT 'recebido',
    valor_total DECIMAL(10,2) DEFAULT 0,
    metodo_pagamento VARCHAR(50) DEFAULT 'pix',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Seed badge catalog
INSERT INTO badges (nome, descricao, icone, xp_requerido) VALUES
    ('Iniciante', 'Bem-vindo à gelateria!', '🍦', 0),
    ('Regular', 'Frequentador fiel', '🌟', 500),
    ('VIP', 'Cliente especial', '💎', 2000),
    ('Lendário', 'Status máximo', '🔥', 10000)
ON CONFLICT DO NOTHING;

-- Seed challenges
INSERT INTO desafios (nome, descricao, xp_recompensa) VALUES
    ('Madrugador', 'Faça um pedido entre 00h e 06h', 150),
    ('Explorador', 'Experimente 5 sabores diferentes', 300),
    ('Fidelão', 'Faça 10 pedidos', 500),
    ('Social', 'Indique 3 amigos', 200)
ON CONFLICT DO NOTHING;
