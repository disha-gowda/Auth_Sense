import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd

class AIService:
    def __init__(self):
        self.models = {}
        self.scalers = {}
    
    def train_model(self, user_id, behavior_data):
        """Train an anomaly detection model for the user"""
        try:
            df = pd.DataFrame(behavior_data)
            
            # Extract features for training
            features = ['keystroke_speed', 'mouse_speed', 'idle_time', 'cursor_path_length']
            feature_data = df[features].fillna(0).values
            
            # Normalize features
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(feature_data)
            
            # Train Isolation Forest
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(scaled_data)
            
            # Store model and scaler
            self.models[user_id] = model
            self.scalers[user_id] = scaler
            
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict_anomaly(self, user_id, current_behavior):
        """Predict if current behavior is anomalous"""
        if user_id not in self.models:
            return 100.0  # Return high score if no model exists yet
        
        try:
            features = ['keystroke_speed', 'mouse_speed', 'idle_time', 'cursor_path_length']
            
            # Prepare current behavior data
            feature_vector = np.array([[
                current_behavior.get('keystroke_speed', 0),
                current_behavior.get('mouse_speed', 0),
                current_behavior.get('idle_time', 0),
                current_behavior.get('cursor_path_length', 0)
            ]])
            
            # Scale the data
            scaled_vector = self.scalers[user_id].transform(feature_vector)
            
            # Predict anomaly (1 = normal, -1 = anomaly)
            prediction = self.models[user_id].predict(scaled_vector)
            anomaly_score = self.models[user_id].score_samples(scaled_vector)[0]
            
            # Convert to trust score (0-100)
            trust_score = max(0, min(100, (anomaly_score + 2) * 25))  # Normalize to 0-100
            
            return trust_score
        except Exception as e:
            print(f"Error predicting anomaly: {e}")
            return 100.0