import decimal
import os
import logging
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from backend.routes.cmd_routes import cmd_bp
from backend.routes.health_routes import health_bp
from backend.routes.referral_routes import referral_bp


class _JSONProvider(DefaultJSONProvider):
    """Extend Flask's default JSON provider to handle Decimal values."""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.json_provider_class = _JSONProvider
    app.json = _JSONProvider(app)

    flask_env = os.environ.get("FLASK_ENV", "production")
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")

    if not allowed_origins:
        if flask_env == "production":
            logger.warning(
                "ALLOWED_ORIGINS is not set. CORS will deny all cross-origin requests. "
                "Set ALLOWED_ORIGINS to your frontend URL."
            )
            cors_origins = []
        else:
            cors_origins = ["http://localhost:3000", "http://localhost:5500", "http://127.0.0.1:5500"]
    else:
        cors_origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

    CORS(app, origins=cors_origins)

    app.register_blueprint(cmd_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(referral_bp)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
