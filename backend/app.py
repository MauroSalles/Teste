import os
import time
import logging
import json
from flask import Flask, request, g
from flask_cors import CORS

from backend.routes.cmd_routes import cmd_bp
from backend.routes.health_routes import health_bp

logger = logging.getLogger(__name__)


def _configure_logging():
    """Use JSON structured logging in production, plain text in dev/testing."""
    flask_env = os.environ.get("FLASK_ENV", "production")
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "time": self.formatTime(record, self.datefmt),
            }
            if record.exc_info:
                log_record["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(log_record, ensure_ascii=False)

    handler = logging.StreamHandler()
    if flask_env == "production":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level, logging.INFO))
    root.handlers = [handler]


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

    # ── Request/response logging ──────────────────────────────────────────────
    @app.before_request
    def _before():
        g.t0 = time.monotonic()

    @app.after_request
    def _after(response):
        elapsed_ms = round((time.monotonic() - g.t0) * 1000, 2)
        logger.info(
            "%s %s → %s (%.1f ms)",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    # ── Generic error handlers ────────────────────────────────────────────────
    @app.errorhandler(404)
    def _not_found(exc):
        return {"error": "endpoint not found"}, 404

    @app.errorhandler(405)
    def _method_not_allowed(exc):
        return {"error": "method not allowed"}, 405

    @app.errorhandler(500)
    def _internal_error(exc):
        logger.exception("Unhandled exception")
        return {"error": "internal server error"}, 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
