import pytest
from backend.app import app
from backend.config.database import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_record_behavior(client):
    """Test behavior recording"""
    # This would require authentication
    pass