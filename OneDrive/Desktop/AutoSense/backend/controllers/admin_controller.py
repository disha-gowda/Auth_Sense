from flask import request, jsonify
from backend.services.admin_service import AdminService
from backend.models.user import User
from backend.models.alert import Alert

class AdminController:
    @staticmethod
    def get_all_users():
        """Get all users"""
        users = AdminService.get_all_users()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    
    @staticmethod
    def get_all_alerts():
        """Get all alerts"""
        alerts = AdminService.get_all_alerts()
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
    
    @staticmethod
    def get_user_stats():
        """Get user behavior statistics"""
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        stats = AdminService.get_user_behavior_stats(user_id)
        return jsonify(stats), 200