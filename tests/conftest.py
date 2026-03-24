"""
Pytest fixtures for Gelateria test suite.
Connects to the PostgreSQL database configured via environment variables.
"""
import os
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor

from backend.app import create_app


# ---------------------------------------------------------------------------
# Flask test client
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    os.environ.setdefault("FLASK_ENV", "testing")
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture(scope="session")
def client(app):
    """A test client for the app."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _dsn():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url
    return (
        f"host={os.environ.get('DB_HOST', 'localhost')} "
        f"dbname={os.environ.get('DB_NAME', 'gelateria_test')} "
        f"user={os.environ.get('DB_USER', 'postgres')} "
        f"password={os.environ.get('DB_PASSWORD', '')} "
        f"port={os.environ.get('DB_PORT', '5432')}"
    )


def _db_available() -> bool:
    try:
        conn = psycopg2.connect(_dsn(), connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


requires_db = pytest.mark.skipif(
    not _db_available(),
    reason="PostgreSQL not available — set DB_HOST / DB_USER / DB_PASSWORD env vars",
)


@pytest.fixture(scope="session")
def db_conn():
    """Raw psycopg2 connection for setup/teardown queries."""
    if not _db_available():
        pytest.skip("PostgreSQL not available")
    conn = psycopg2.connect(_dsn(), cursor_factory=RealDictCursor)
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_tables(db_conn):
    """Truncate tables before each test so tests are independent."""
    with db_conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE pedidos, estoque, sabores RESTART IDENTITY CASCADE")
    yield
