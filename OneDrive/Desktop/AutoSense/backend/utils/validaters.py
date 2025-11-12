import re
from email_validator import validate_email, EmailNotValidError

class ValidationUtils:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        try:
            validated_email = validate_email(email)
            return True, validated_email.email
        except EmailNotValidError:
            return False, None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_otp(otp):
        """Validate OTP format"""
        if len(otp) != 6 or not otp.isdigit():
            return False
        return True