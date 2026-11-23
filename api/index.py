import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask app
app = create_app()

# Vercel needs the app variable to be named 'app'
# This file serves as the entry point for Vercel serverless functions

if __name__ == "__main__":
    app.run()