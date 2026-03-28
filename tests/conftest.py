import os

import pytest

# Use test DB env vars set by CI; fall back to localhost defaults for local runs.
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "gelateria_test")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "testpassword")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("FLASK_ENV", "testing")

from backend.app import create_app  # noqa: E402


@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config["TESTING"] = True
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
