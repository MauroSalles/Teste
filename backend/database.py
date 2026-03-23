import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2 import pool as pg_pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_pool: pg_pool.ThreadedConnectionPool | None = None


def _get_pool() -> pg_pool.ThreadedConnectionPool:
    """Return the shared connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        password = os.getenv("DB_PASSWORD")
        if not password:
            raise RuntimeError(
                "DB_PASSWORD environment variable is not set. "
                "Create a .env file based on backend/.env.example."
            )
        _pool = pg_pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "gelateria"),
            user=os.getenv("DB_USER", "postgres"),
            password=password,
            port=os.getenv("DB_PORT", "5432"),
            cursor_factory=RealDictCursor,
        )
    return _pool


@contextmanager
def get_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Context manager that yields a pooled connection.

    Automatically rolls back on exception and returns the connection to the
    pool when the ``with`` block exits.
    """
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)
