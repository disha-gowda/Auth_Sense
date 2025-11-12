from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.services.behavior_service import BehaviorService
from backend.config.database import db
from datetime import datetime
import json

class BehaviorController:
    @staticmethod
    def record_behavior():
        """Record user behavior and check for anomalies"""
        user_id = get_jwt_identity()
        behavior_data = request.json
        
        # Update session activity
        session_id = request.headers.get('Session-ID', 'unknown')
        BehaviorService.update_session_activity(session_id)
        
        # Calculate trust score using AI model
        trust_score = 100.0  # Placeholder - would integrate with AI service
        
        # Check if behavior is anomalous
        is_anomaly = trust_score < 70  # Threshold
        
        # Store behavior log
        behavior_log = BehaviorService.log_behavior(
            user_id, session_id, behavior_data, trust_score, is_anomaly
        )
        
        db.session.add(behavior_log)
        
        if is_anomaly:
            # Trigger alert
            from backend.controllers.notification_controller import NotificationController
            NotificationController.trigger_anomaly_alert(user_id, behavior_data, trust_score)
            return jsonify({'action': 'logout', 'trust_score': trust_score}), 200
        
        db.session.commit()
        return jsonify({'trust_score': trust_score}), 200
    
    @staticmethod
    def get_user_behavior_history():
        """Get user's behavior history"""
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 100, type=int)
        
        behavior_logs = BehaviorService.get_user_behavior_history(user_id, limit)
        
        return jsonify({
            'behavior_logs': [log.to_dict() for log in behavior_logs]
        }), 200