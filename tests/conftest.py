"""Shared pytest fixtures for the Gelateria test suite."""
import os
import pytest

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "gelateria_test")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "testpassword")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("FLASK_ENV", "testing")


@pytest.fixture(scope="session")
def app():
    from backend.app import create_app

    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture()
def clean_db():
    """Wipe and re-seed the test DB before a test that needs it (integration tests)."""
    from backend.database import get_db

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM estoque")
            cur.execute("DELETE FROM pedidos")
            cur.execute("DELETE FROM sabores")
            cur.execute(
                "INSERT INTO sabores (nome, preco) VALUES (%s, %s) RETURNING id",
                ("TestChocolate", 10.00),
            )
    yield
