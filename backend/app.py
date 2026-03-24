import os
import logging
import json
import time
from flask import Flask, request, g
from flask_cors import CORS

from backend.routes.cmd_routes import cmd_bp
from backend.routes.health_routes import health_bp

logger = logging.getLogger(__name__)


def _configure_logging():
    """Set up structured JSON logging for production, plain text for development."""
    flask_env = os.environ.get("FLASK_ENV", "production")
    log_level = logging.DEBUG if flask_env == "development" else logging.INFO

    if flask_env == "production":
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    "time": self.formatTime(record),
                    "level": record.levelname,
                    "name": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_record["exc_info"] = self.formatException(record.exc_info)
                return json.dumps(log_record)

        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logging.basicConfig(level=log_level, handlers=[handler])
    else:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        )


def create_app():
    _configure_logging()

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

    # ── Request / response logging ─────────────────────────────────────────
    @app.before_request
    def _start_timer():
        g.start_time = time.monotonic()

    @app.after_request
    def _log_request(response):
        elapsed_ms = round((time.monotonic() - g.start_time) * 1000, 1)
        logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
