from backend.config.database import db
from datetime import datetime

class BehaviorLog(db.Model):
    __tablename__ = 'behavior_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    keystroke_data = db.Column(db.Text)
    mouse_data = db.Column(db.Text)
    trust_score = db.Column(db.Float)
    is_anomaly = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'trust_score': self.trust_score,
            'is_anomaly': self.is_anomaly
        }