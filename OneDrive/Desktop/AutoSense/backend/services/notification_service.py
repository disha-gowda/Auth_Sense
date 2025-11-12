from flask_mail import Message
from backend import mail
import json

class NotificationService:
    @staticmethod
    def send_otp_email(email, otp):
        """Send OTP to user's email"""
        try:
            msg = Message(
                subject="AuthSense+ - OTP Verification",
                sender=mail.app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Your OTP for AuthSense+ is: {otp}\nValid for 5 minutes."
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending OTP: {e}")
            return False
    
    @staticmethod
    def send_alert_email(user_email, session_id, location, behavior_data, reason):
        """Send security alert email"""
        try:
            msg = Message(
                subject="⚠️ AuthSense+ Security Alert — Suspicious Session Activity",
                sender=mail.app.config['MAIL_USERNAME'],
                recipients=[user_email]
            )
            
            body = f"""
            Hello,
            
            We detected abnormal behavior during your recent AuthSense session.
            
            📍 Location: {location}
            🧠 Trust Score: {behavior_data.get('trust_score', 'N/A')}%
            ⚡ Detected Issue: {reason}
            
            Session ID: {session_id}
            Timestamp: {behavior_data.get('timestamp', 'Unknown')}
            
            Your account was automatically logged out for safety.
            
            — AuthSense+ Security AI
            """
            
            msg.body = body
            
            # Attach behavior data as JSON
            behavior_json = json.dumps(behavior_data, indent=2)
            msg.attach(filename='session_log.json', content=behavior_json)
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending alert email: {e}")
            return False