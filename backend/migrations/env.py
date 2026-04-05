"""Alembic environment configuration for Gelateria Pro."""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Build DATABASE_URL from environment variables (same convention as backend/database.py)
_db_host = os.environ.get("DB_HOST", "localhost")
_db_port = os.environ.get("DB_PORT", "5432")
_db_name = os.environ.get("DB_NAME", "gelateria")
_db_user = os.environ.get("DB_USER", "gelateria")
_db_pass = os.environ.get("DB_PASSWORD", "")

# Allow a full DATABASE_URL override (e.g. from Render/Railway)
_database_url = os.environ.get(
    "DATABASE_URL",
    f"postgresql://{_db_user}:{_db_pass}@{_db_host}:{_db_port}/{_db_name}",
)

# Alembic uses SQLAlchemy — psycopg2 driver
if _database_url.startswith("postgres://"):
    _database_url = _database_url.replace("postgres://", "postgresql://", 1)

config.set_main_option("sqlalchemy.url", _database_url)

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL without a live DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (requires a live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
