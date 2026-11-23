import os
from flask import Flask, jsonify

# Vercel serverless detection
IS_VERCEL = os.getenv("VERCEL") == "1"


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-only-change-this-secret",
    )

    # Database configuration
    if IS_VERCEL:
        # Use PostgreSQL on Vercel (Vercel Postgres or external)
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            app.config["DATABASE_URL"] = database_url
            app.config["DATABASE_PATH"] = database_url
        else:
            # Fallback for local development
            db_path = os.getenv(
                "DATABASE_PATH",
                os.path.join(app.instance_path, "interviews.db")
            )
            app.config["DATABASE_PATH"] = db_path
    else:
        db_path = os.getenv(
            "DATABASE_PATH",
            os.path.join(app.instance_path, "interviews.db")
        )
        app.config["DATABASE_PATH"] = db_path

    if test_config:
        app.config.update(test_config)

    # Initialize database
    from app.db import init_db
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