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

-- Notification preferences per user
CREATE TABLE IF NOT EXISTS user_notification_preferences (
    user_id              INTEGER PRIMARY KEY,
    email_promotional    BOOLEAN NOT NULL DEFAULT TRUE,
    email_transactional  BOOLEAN NOT NULL DEFAULT TRUE,
    sms_promotional      BOOLEAN NOT NULL DEFAULT TRUE,
    sms_transactional    BOOLEAN NOT NULL DEFAULT TRUE,
    push_promotional     BOOLEAN NOT NULL DEFAULT TRUE,
    push_transactional   BOOLEAN NOT NULL DEFAULT TRUE,
    quiet_hours          JSONB   NOT NULL DEFAULT '{}'
);

-- Outbound notification queue (scheduled / pending sends)
CREATE TABLE IF NOT EXISTS notification_queue (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL,
    channel      VARCHAR(20)  NOT NULL DEFAULT 'email',
    template     VARCHAR(100) NOT NULL,
    payload      TEXT,
    scheduled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       VARCHAR(20)  NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Audit log of sent notifications
CREATE TABLE IF NOT EXISTS notification_log (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    channel     VARCHAR(20)  NOT NULL DEFAULT 'email',
    template    VARCHAR(100) NOT NULL,
    status_code INTEGER,
    sent_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- FCM / APNs device tokens
CREATE TABLE IF NOT EXISTS device_tokens (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    token      TEXT    NOT NULL,
    platform   VARCHAR(20) NOT NULL DEFAULT 'web',
    active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, token)
);

-- User behaviour cache used by the smart timing engine
CREATE TABLE IF NOT EXISTS user_behavior_cache (
    user_id              INTEGER PRIMARY KEY,
    timezone             VARCHAR(60)  NOT NULL DEFAULT 'UTC',
    most_active_hours    JSONB        NOT NULL DEFAULT '[11, 12]',
    weekend_active       BOOLEAN      NOT NULL DEFAULT FALSE,
    behavior_confidence  DECIMAL(4,2) NOT NULL DEFAULT 0.50,
    orders_analyzed      INTEGER      NOT NULL DEFAULT 0,
    updated_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT INTO sabores (nome, preco) VALUES
    ('Chocolate', 10.00),
    ('Morango', 9.50),
    ('Baunilha', 8.00),
    ('Pistache', 12.00),
    ('Limão', 9.00)
ON CONFLICT DO NOTHING;

