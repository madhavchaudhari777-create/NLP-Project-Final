import os
from flask import Flask, jsonify
from app.db import init_db


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-only-change-this-secret",
    )

    db_path = os.getenv(
        "DATABASE_PATH",
        os.path.join(app.instance_path, "interviews.db")
    )
    app.config["DATABASE_PATH"] = db_path

    if test_config:
        app.config.update(test_config)

    # Ensure database tables exist
    init_db(app.config["DATABASE_PATH"])

    from app.routes import main
    app.register_blueprint(main)

    # Return JSON instead of HTML for 500 errors so the frontend can parse it.
    @app.errorhandler(500)
    def handle_500(e):
        return jsonify(success=False, error="Internal server error: " + str(e)), 500

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify(success=False, error="Endpoint not found."), 404

    return app