from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import jwt
from datetime import datetime, timedelta

class SecurityUtils:
    @staticmethod
    def hash_password(password):
        """Hash a password"""
        return generate_password_hash(password)
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify a password against its hash"""
        return check_password_hash(hashed_password, password)
    
    @staticmethod
    def generate_token(data, secret_key, expires_in=3600):
        """Generate JWT token"""
        payload = {
            'data': data,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_token(token, secret_key):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload['data']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_secure_string(length=32):
        """Generate a secure random string"""
        return secrets.token_urlsafe(length)