import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Get configuration from environment
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8000"))

    app.run(debug=debug, host=host, port=port)