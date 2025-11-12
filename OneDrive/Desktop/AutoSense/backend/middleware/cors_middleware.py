from flask_cors import CORS

def setup_cors(app):
    """Setup CORS for the application"""
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:3001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Session-ID"]
        }
    })