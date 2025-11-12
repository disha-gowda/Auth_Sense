from flask import request, jsonify
from flask_jwt_extended import create_access_token
from backend.services.auth_service import AuthService
from backend.models.user import User
from backend.models.session import Session
from backend.config.database import db
from datetime import datetime, timedelta
import uuid

class AuthController:
    @staticmethod
    def signup():
        """Handle user signup"""
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user, error = AuthService.register_user(email, password)
        if error:
            return jsonify({'error': error}), 400
        
        db.session.add(user)
        db.session.commit()
        
        if AuthService.send_otp_email(email, user.otp):
            return jsonify({'message': 'OTP sent to email'}), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
    
    @staticmethod
    def verify_signup_otp():
        """Verify signup OTP"""
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        success, user = AuthService.verify_otp(email, otp)
        if not success:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        
        db.session.commit()
        return jsonify({'message': 'Account verified successfully'}), 200
    
    @staticmethod
    def login():
        """Handle user login"""
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user, error = AuthService.authenticate_user(email, password)
        if error:
            return jsonify({'error': error}), 401
        
        otp = AuthService.generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=5)
        
        user.otp = otp
        user.otp_expiry = otp_expiry
        db.session.commit()
        
        if AuthService.send_otp_email(email, otp):
            return jsonify({'message': 'OTP sent to email'}), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
    
    @staticmethod
    def verify_login_otp():
        """Verify login OTP"""
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        success, user = AuthService.verify_otp(email, otp)
        if not success:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        
        # Generate session token
        access_token = create_access_token(identity=user.id)
        
        session_id = str(uuid.uuid4())
        session = Session(
            user_id=user.id,
            session_token=access_token,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'user_id': user.id,
            'email': user.email
        }), 200