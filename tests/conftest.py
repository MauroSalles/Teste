import os
import pytest

# Set test env vars before importing the app so Flask/DB config is correct
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('DB_HOST', os.environ.get('DB_HOST', 'localhost'))
os.environ.setdefault('DB_NAME', os.environ.get('DB_NAME', 'gelateria_test'))
os.environ.setdefault('DB_USER', os.environ.get('DB_USER', 'postgres'))
os.environ.setdefault('DB_PASSWORD', os.environ.get('DB_PASSWORD', 'testpassword'))
os.environ.setdefault('DB_PORT', os.environ.get('DB_PORT', '5432'))

# Stub external credentials so imports don't fail
os.environ.setdefault('TWILIO_ACCOUNT_SID', 'ACtest')
os.environ.setdefault('TWILIO_AUTH_TOKEN', 'testtoken')
os.environ.setdefault('WHATSAPP_BUSINESS_NUMBER', '+15005550006')
os.environ.setdefault('INSTAGRAM_ACCESS_TOKEN', 'ig_test_token')
os.environ.setdefault('IG_BUSINESS_ACCOUNT_ID', '12345')

from backend.app import create_app  # noqa: E402


@pytest.fixture
def app():
    application = create_app()
    application.config['TESTING'] = True
    yield application


@pytest.fixture
def client(app):
    return app.test_client()
