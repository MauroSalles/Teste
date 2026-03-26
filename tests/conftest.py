"""
Pytest configuration and shared fixtures.
The test DB is initialised by CI via:
  psql ... -f database/schema.sql
Environment variables (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT)
are set by the CI workflow.
"""
import os
import pytest

# Ensure Flask uses testing mode before app import
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
