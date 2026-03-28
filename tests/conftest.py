"""Pytest configuration — Flask test client fixture."""
import os

import pytest

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "")


@pytest.fixture
def app():
    from backend.app import create_app
    application = create_app()
    application.config["TESTING"] = True
    yield application


@pytest.fixture
def client(app):
    return app.test_client()
