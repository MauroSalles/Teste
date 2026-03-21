import os
from flask import Flask
from flask_cors import CORS
from routes import cmd_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(cmd_bp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
