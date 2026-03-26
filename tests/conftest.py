import os
import pytest

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("JWT_SECRET", "test-secret-key-that-is-long-enough-for-hmac")

from backend.app import create_app  # noqa: E402


@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_token():
    """Generate a valid JWT for testing."""
    import jwt

    payload = {
        "sub": "1",
        "email": "test@test.com",
        "customer_id": "cus_test123",
        "payment_methods": [],
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
