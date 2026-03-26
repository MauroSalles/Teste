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

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

-- ── Energy-First Product Design ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS user_energy_profile (
    id                   SERIAL PRIMARY KEY,
    session_id           VARCHAR(64) UNIQUE NOT NULL,
    baseline_energy      INTEGER     DEFAULT 50  CHECK (baseline_energy BETWEEN 0 AND 100),
    preferred_interaction TEXT        DEFAULT 'tap',
    decision_speed_ms    INTEGER     DEFAULT 0,
    exploration_rate     DECIMAL     DEFAULT 0.0,
    peak_energy_hour     INTEGER     DEFAULT 10  CHECK (peak_energy_hour BETWEEN 0 AND 23),
    energy_curve         JSONB       DEFAULT '[]',
    favorite_mood        TEXT,
    introvert_score      INTEGER     DEFAULT 50  CHECK (introvert_score BETWEEN 0 AND 100),
    sharer_score         INTEGER     DEFAULT 50  CHECK (sharer_score   BETWEEN 0 AND 100),
    updated_at           TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS energy_events (
    id                  SERIAL PRIMARY KEY,
    session_id          VARCHAR(64) NOT NULL,
    energy_score        INTEGER     CHECK (energy_score BETWEEN 0 AND 100),
    mood                TEXT,
    purpose             TEXT,
    stress_level        INTEGER     CHECK (stress_level BETWEEN 0 AND 100),
    location_context    TEXT,
    time_of_day         TEXT,
    day_of_week         TEXT,
    battery_level       INTEGER     CHECK (battery_level BETWEEN 0 AND 100),
    device_motion       TEXT,
    click_speed_ms      INTEGER,
    scroll_pattern      TEXT,
    typing_speed_cpm    INTEGER,
    flavor_recommended  TEXT,
    created_at          TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS energy_recommendations (
    id                  SERIAL PRIMARY KEY,
    session_id          VARCHAR(64) NOT NULL,
    energy_score        INTEGER,
    recommended_flavor  TEXT,
    confidence_score    DECIMAL,
    reasoning           JSONB,
    shown_at            TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    clicked             BOOLEAN     DEFAULT FALSE,
    purchased           BOOLEAN     DEFAULT FALSE
);

