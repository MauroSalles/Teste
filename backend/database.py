import os
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

_pool: pool.ThreadedConnectionPool | None = None

_MIN_CONN = int(os.environ.get("DB_POOL_MIN", 1))
_MAX_CONN = int(os.environ.get("DB_POOL_MAX", 10))


def _build_dsn() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url
    return (
        f"host={os.environ.get('DB_HOST', 'localhost')} "
        f"dbname={os.environ.get('DB_NAME', 'gelateria')} "
        f"user={os.environ.get('DB_USER', 'postgres')} "
        f"password={os.environ.get('DB_PASSWORD', '')} "
        f"port={os.environ.get('DB_PORT', '5432')}"
    )


def get_pool() -> pool.ThreadedConnectionPool:
    global _pool
    if _pool is None or _pool.closed:
        _pool = pool.ThreadedConnectionPool(
            _MIN_CONN,
            _MAX_CONN,
            dsn=_build_dsn(),
            cursor_factory=RealDictCursor,
        )
        logger.info("Database connection pool created (%d–%d connections).", _MIN_CONN, _MAX_CONN)
    return _pool


@contextmanager
def get_db():
    """Yield a connection from the pool, auto-committing on success or rolling back on error."""
    conn = get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        get_pool().putconn(conn)


def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "../database/schema.sql")
    with get_db() as conn:
        with conn.cursor() as cursor:
            with open(schema_path, "r") as f:
                cursor.execute(f.read())

