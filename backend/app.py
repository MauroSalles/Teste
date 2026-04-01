import os
import logging
from flask import Flask
from flask_cors import CORS

from backend.routes.cmd_routes import cmd_bp
from backend.routes.health_routes import health_bp
from backend.routes.gamification_routes import gamification_bp
from backend.routes.api_routes import api_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.payment_routes import payment_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.loyalty_routes import loyalty_bp
from backend.routes.notification_routes import notification_bp
from backend.realtime.socket_events import socketio

logger = logging.getLogger(__name__)


def create_app():
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
    app.register_blueprint(gamification_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(loyalty_bp)
    app.register_blueprint(notification_bp)

    socketio.init_app(app, cors_allowed_origins=cors_origins or "*")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
