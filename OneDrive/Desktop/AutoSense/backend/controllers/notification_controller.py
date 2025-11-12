from flask import request, jsonify
from backend.services.notification_service import NotificationService
from backend.models.user import User
from backend.models.session import Session
from backend.models.alert import Alert
from backend.config.database import db
from datetime import datetime
import json

class NotificationController:
    @staticmethod
    def trigger_anomaly_alert(user_id, behavior_data, trust_score):
        """Trigger alert when anomaly is detected"""
        user = User.query.get(user_id)
        session = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).first()
        
        if user and session:
            # Get location from behavior data
            location = behavior_data.get('location', 'Unknown')
            
            # Record alert
            alert = Alert(
                user_id=user_id,
                session_id=session.session_token,
                timestamp=datetime.now(),
                reason=f"Trust score dropped to {trust_score}%",
                location=json.dumps(location),
                behavior_data=json.dumps(behavior_data)
            )
            
            # Update session status to terminated
            session.status = 'terminated'
            
            db.session.add(alert)
            db.session.commit()
            
            # Send alert email
            NotificationService.send_alert_email(
                user.email,
                session.session_token,
                str(location),
                behavior_data,
                f"Trust score dropped to {trust_score}%"
            )