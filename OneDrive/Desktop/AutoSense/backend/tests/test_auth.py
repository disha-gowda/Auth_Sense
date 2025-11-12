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

def test_signup(client):
    """Test user signup"""
    response = client.post('/api/auth/signup', json={
        'email': 'test@example.com',
        'password': 'TestPass123!'
    })
    assert response.status_code == 200

def test_login(client):
    """Test user login"""
    # First signup the user
    client.post('/api/auth/signup', json={
        'email': 'test@example.com',
        'password': 'TestPass123!'
    })
    
    # Then try to login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'TestPass123!'
    })
    assert response.status_code == 200