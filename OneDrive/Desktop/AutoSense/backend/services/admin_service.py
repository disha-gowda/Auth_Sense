from backend.models.user import User
from backend.models.alert import Alert
from backend.models.behavior import BehaviorLog

class AdminService:
    @staticmethod
    def get_all_users():
        """Get all users"""
        return User.query.all()
    
    @staticmethod
    def get_all_alerts(limit=100):
        """Get all alerts"""
        return Alert.query.order_by(Alert.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_user_behavior_stats(user_id):
        """Get user behavior statistics"""
        behavior_logs = BehaviorLog.query.filter_by(user_id=user_id).all()
        
        if not behavior_logs:
            return {
                'total_sessions': 0,
                'anomaly_count': 0,
                'average_trust_score': 100.0
            }
        
        anomaly_count = sum(1 for log in behavior_logs if log.is_anomaly)
        avg_trust_score = sum(log.trust_score for log in behavior_logs if log.trust_score) / len([log for log in behavior_logs if log.trust_score])
        
        return {
            'total_sessions': len(behavior_logs),
            'anomaly_count': anomaly_count,
            'average_trust_score': avg_trust_score
        }