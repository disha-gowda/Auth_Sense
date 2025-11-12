from datetime import datetime, timedelta
import json

class HelperUtils:
    @staticmethod
    def get_current_timestamp():
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minutes"
        else:
            hours = seconds // 3600
            return f"{hours} hours"
    
    @staticmethod
    def calculate_trust_score(baseline, current):
        """Calculate trust score based on deviation from baseline"""
        if not baseline or not current:
            return 100.0
        
        # Calculate deviation percentage for each metric
        deviations = []
        for key in baseline:
            if key in current:
                baseline_val = baseline[key] or 1  # Avoid division by zero
                current_val = current[key] or 1
                deviation = abs(baseline_val - current_val) / baseline_val * 100
                deviations.append(deviation)
        
        if not deviations:
            return 100.0
        
        avg_deviation = sum(deviations) / len(deviations)
        trust_score = max(0, 100 - avg_deviation)
        
        return trust_score
    
    @staticmethod
    def json_serialize(obj):
        """Serialize object to JSON with custom handling"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return str(obj)