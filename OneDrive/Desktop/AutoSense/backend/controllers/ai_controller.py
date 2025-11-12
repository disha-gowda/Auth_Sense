from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.services.ai_service import AIService
from backend.config.database import db
import pandas as pd

class AIController:
    def __init__(self):
        self.ai_service = AIService()
    
    def train_model(self):
        """Train AI model with user behavior data"""
        user_id = get_jwt_identity()
        behavior_data = request.json
        
        success = self.ai_service.train_model(user_id, behavior_data)
        
        if success:
            return jsonify({'message': 'Model trained successfully'}), 200
        else:
            return jsonify({'error': 'Failed to train model'}), 500
    
    def predict(self):
        """Predict if current behavior is anomalous"""
        user_id = get_jwt_identity()
        behavior_data = request.json
        
        trust_score = self.ai_service.predict_anomaly(user_id, behavior_data)
        
        return jsonify({'trust_score': trust_score}), 200