import os
import logging

import sentry_sdk
from flask import Flask
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from backend.routes.cmd_routes import cmd_bp
from backend.routes.health_routes import health_bp

logger = logging.getLogger(__name__)


def _init_sentry():
    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=os.getenv("FLASK_ENV", "production"),
            release=os.getenv("RELEASE_VERSION", "1.0.0"),
        )
        logger.info("Sentry initialized (env=%s).", os.getenv("FLASK_ENV", "production"))


def create_app():
    _init_sentry()

    app = Flask(__name__)

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

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)

