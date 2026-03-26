import os
import logging
import logging.config
from flask import Flask, jsonify
from flask_cors import CORS

from backend.routes.cmd_routes import cmd_bp
from backend.routes.health_routes import health_bp
from backend.routes.api_routes import api_bp
from backend.routes.auth_routes import auth_bp

logger = logging.getLogger(__name__)


def _configure_logging(flask_env: str) -> None:
    fmt = (
        '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
        if flask_env == "production"
        else "%(levelname)-8s %(name)s — %(message)s"
    )
    logging.basicConfig(level=logging.INFO, format=fmt)


def create_app():
    flask_env = os.environ.get("FLASK_ENV", "production")
    _configure_logging(flask_env)

    app = Flask(__name__)

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")
    if not allowed_origins:
        if flask_env == "production":
            logger.warning(
                "ALLOWED_ORIGINS not set — CORS will deny all cross-origin requests. "
                "Set ALLOWED_ORIGINS to your frontend URL."
            )
            cors_origins = []
        else:
            cors_origins = [
                "http://localhost:3000",
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "http://localhost:8080",
            ]
    else:
        cors_origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

    CORS(app, origins=cors_origins, supports_credentials=True)

    # ── Blueprints ─────────────────────────────────────────────────────────────
    app.register_blueprint(cmd_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    # ── Generic error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso não encontrado."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Método não permitido."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Internal server error: %s", e)
        return jsonify({"error": "Erro interno do servidor."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
