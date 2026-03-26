"""Pytest configuration and fixtures for the Gelateria test suite."""

import os
import pytest

# ── Point tests at a local in-memory SQLite-like setup or a test Postgres DB ──
# The CI workflow supplies these env vars; locally you can override via .env.test.

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("DB_HOST", os.environ.get("DB_HOST", "localhost"))
os.environ.setdefault("DB_NAME", os.environ.get("DB_NAME", "gelateria_test"))
os.environ.setdefault("DB_USER", os.environ.get("DB_USER", "postgres"))
os.environ.setdefault("DB_PASSWORD", os.environ.get("DB_PASSWORD", ""))
os.environ.setdefault("DB_PORT", os.environ.get("DB_PORT", "5432"))
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-ci")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")


def _clean_tables():
    """Remove test-created rows, keeping seed data intact."""
    try:
        from backend.database import get_db
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM pedidos")
                cur.execute("DELETE FROM estoque")
                cur.execute("DELETE FROM usuarios")
                cur.execute(
                    "DELETE FROM sabores WHERE nome NOT IN "
                    "('Chocolate','Morango','Baunilha','Pistache','Limão')"
                )
    except Exception:
        pass  # DB may not be available in all environments


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    from backend.app import create_app
    application = create_app()
    application.config["TESTING"] = True
    yield application


@pytest.fixture(scope="session")
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """Test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def clean_db():
    """Wipe test data before and after each test (keeps schema intact)."""
    _clean_tables()
    yield
    _clean_tables()
