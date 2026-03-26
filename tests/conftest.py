import os
import pytest

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "gelateria_test")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "testpassword")
os.environ.setdefault("DB_PORT", "5432")


@pytest.fixture
def app():
    from backend.app import create_app
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
