from backend.models.behavior import BehaviorLog
from backend.models.session import Session
from datetime import datetime
import json

class BehaviorService:
    @staticmethod
    def log_behavior(user_id, session_id, behavior_data, trust_score, is_anomaly=False):
        """Log user behavior"""
        behavior_log = BehaviorLog(
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now(),
            keystroke_data=json.dumps(behavior_data.get('keystroke_data', {})),
            mouse_data=json.dumps(behavior_data.get('mouse_data', {})),
            trust_score=trust_score,
            is_anomaly=is_anomaly
        )
        
        return behavior_log
    
    @staticmethod
    def get_user_behavior_history(user_id, limit=100):
        """Get user's behavior history"""
        return BehaviorLog.query.filter_by(user_id=user_id).order_by(
            BehaviorLog.timestamp.desc()
        ).limit(limit).all()
    
    @staticmethod
    def update_session_activity(session_id):
        """Update session last activity time"""
        session = Session.query.filter_by(session_token=session_id).first()
        if session:
            session.last_activity = datetime.now()
            return session
        return None