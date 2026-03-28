import os
import pytest

# Use SQLite-compatible test doubles or simply test without a live DB.
# The CI spins up a real Postgres DB and sets these env vars.
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "gelateria_test")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "testpassword")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")


@pytest.fixture
def app():
    from backend.app import create_app
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
