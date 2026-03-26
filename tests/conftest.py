"""
Pytest fixtures that set up a real PostgreSQL test database.

Requires the following environment variables (same as CI):
  DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, FLASK_ENV
"""

import os
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor

from backend.app import create_app


@pytest.fixture(scope="session")
def app():
    """Create a Flask test application."""
    test_app = create_app()
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_tables():
    """Truncate mutable tables before each test to ensure isolation."""
    # Import here so the pool is already initialised by the time we clean up.
    from backend.database import get_pool

    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "TRUNCATE TABLE pedidos, estoque, sabores RESTART IDENTITY CASCADE"
            )
            # Re-seed sabores so every test starts from a known state
            cur.execute(
                """
                INSERT INTO sabores (nome, preco) VALUES
                    ('Chocolate', 10.00),
                    ('Morango', 9.50),
                    ('Baunilha', 8.00)
                """
            )
        conn.commit()
    finally:
        pool.putconn(conn)
