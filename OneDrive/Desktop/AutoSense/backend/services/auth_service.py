from backend.models.user import User
from backend.models.session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

class AuthService:
    @staticmethod
    def register_user(email, password):
        """Register a new user"""
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "User already exists"
        
        otp = AuthService.generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=5)
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            otp=otp,
            otp_expiry=otp_expiry
        )
        
        return user, None
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        import random
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def verify_otp(email, otp):
        """Verify OTP for user"""
        user = User.query.filter_by(email=email, otp=otp).first()
        
        if not user or user.otp_expiry < datetime.now():
            return False, None
        
        # Clear OTP after verification
        user.otp = None
        user.otp_expiry = None
        
        return True, user
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return None, "Invalid credentials"
        
        return user, None