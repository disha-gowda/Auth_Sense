from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import uuid
import json
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///authsense.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
mail = Mail(app)

# Import models after db initialization
from models.user import User
from models.session import Session
from models.behavior import BehaviorLog
from models.alert import Alert

# AI Model Storage
user_models = {}

def generate_otp():
    import random
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    try:
        msg = Message(
            subject="AuthSense+ - OTP Verification",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"Your OTP for AuthSense+ is: {otp}\nValid for 5 minutes."
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False

def send_alert_email(user_email, session_id, location, behavior_data, reason):
    try:
        msg = Message(
            subject="⚠️ AuthSense+ Security Alert — Suspicious Session Activity",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        
        body = f"""
        Hello,
        
        We detected abnormal behavior during your recent AuthSense session.
        
        📍 Location: {location}
        🧠 Trust Score: {behavior_data.get('trust_score', 'N/A')}%
        ⚡ Detected Issue: {reason}
        
        Session ID: {session_id}
        Timestamp: {datetime.now().isoformat()}
        
        Your account was automatically logged out for safety.
        
        — AuthSense+ Security AI
        """
        
        msg.body = body
        
        # Attach behavior data as JSON
        behavior_json = json.dumps(behavior_data, indent=2)
        part = msg.attach(filename='session_log.json', content=behavior_json)
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending alert email: {e}")
        return False

def train_behavior_model(user_id, behavior_data):
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
        user_models[user_id] = {
            'model': model,
            'scaler': scaler,
            'features': features
        }
        
        return True
    except Exception as e:
        print(f"Error training model: {e}")
        return False

def predict_anomaly(user_id, current_behavior):
    """Predict if current behavior is anomalous"""
    if user_id not in user_models:
        return 100.0  # Return high score if no model exists yet
    
    try:
        model_data = user_models[user_id]
        features = model_data['features']
        
        # Prepare current behavior data
        feature_vector = np.array([[
            current_behavior.get('keystroke_speed', 0),
            current_behavior.get('mouse_speed', 0),
            current_behavior.get('idle_time', 0),
            current_behavior.get('cursor_path_length', 0)
        ]])
        
        # Scale the data
        scaled_vector = model_data['scaler'].transform(feature_vector)
        
        # Predict anomaly (1 = normal, -1 = anomaly)
        prediction = model_data['model'].predict(scaled_vector)
        anomaly_score = model_data['model'].score_samples(scaled_vector)[0]
        
        # Convert to trust score (0-100)
        trust_score = max(0, min(100, (anomaly_score + 2) * 25))  # Normalize to 0-100
        
        return trust_score
    except Exception as e:
        print(f"Error predicting anomaly: {e}")
        return 100.0

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400
    
    otp = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=5)
    
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        otp=otp,
        otp_expiry=otp_expiry
    )
    
    db.session.add(user)
    db.session.commit()
    
    if send_otp_email(email, otp):
        return jsonify({'message': 'OTP sent to email'}), 200
    else:
        return jsonify({'error': 'Failed to send OTP'}), 500

@app.route('/api/auth/verify_signup_otp', methods=['POST'])
def verify_signup_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    
    user = User.query.filter_by(email=email, otp=otp).first()
    
    if not user or user.otp_expiry < datetime.now():
        return jsonify({'error': 'Invalid or expired OTP'}), 400
    
    # Clear OTP after verification
    user.otp = None
    user.otp_expiry = None
    db.session.commit()
    
    return jsonify({'message': 'Account verified successfully'}), 200

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    otp = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=5)
    
    user.otp = otp
    user.otp_expiry = otp_expiry
    db.session.commit()
    
    if send_otp_email(email, otp):
        return jsonify({'message': 'OTP sent to email'}), 200
    else:
        return jsonify({'error': 'Failed to send OTP'}), 500

@app.route('/api/auth/verify_login_otp', methods=['POST'])
def verify_login_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    
    user = User.query.filter_by(email=email, otp=otp).first()
    
    if not user or user.otp_expiry < datetime.now():
        return jsonify({'error': 'Invalid or expired OTP'}), 400
    
    # Clear OTP and generate session token
    access_token = create_access_token(identity=user.id)
    
    session_id = str(uuid.uuid4())
    session = Session(
        user_id=user.id,
        session_token=access_token,
        created_at=datetime.now(),
        last_activity=datetime.now()
    )
    
    user.otp = None
    user.otp_expiry = None
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'access_token': access_token,
        'user_id': user.id,
        'email': user.email
    }), 200

@app.route('/api/behavior/events', methods=['POST'])
@jwt_required()
def record_behavior():
    user_id = get_jwt_identity()
    behavior_data = request.json
    
    # Update last activity in session
    session = Session.query.filter_by(user_id=user_id, status='active').first()
    if session:
        session.last_activity = datetime.now()
    
    # Calculate trust score
    trust_score = predict_anomaly(user_id, behavior_data)
    
    # Check if behavior is anomalous
    is_anomaly = trust_score < 70  # Threshold
    
    # Store behavior log
    behavior_log = BehaviorLog(
        user_id=user_id,
        session_id=session.session_token if session else 'unknown',
        timestamp=datetime.now(),
        keystroke_data=json.dumps(behavior_data.get('keystroke_data', {})),
        mouse_data=json.dumps(behavior_data.get('mouse_data', {})),
        trust_score=trust_score,
        is_anomaly=is_anomaly
    )
    
    db.session.add(behavior_log)
    
    if is_anomaly:
        # Trigger alert
        trigger_anomaly_alert(user_id, behavior_data, trust_score)
        return jsonify({'action': 'logout', 'trust_score': trust_score}), 200
    
    db.session.commit()
    return jsonify({'trust_score': trust_score}), 200

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
        send_alert_email(
            user.email,
            session.session_token,
            str(location),
            behavior_data,
            f"Trust score dropped to {trust_score}%"
        )

@app.route('/api/ai/train', methods=['POST'])
@jwt_required()
def train_model():
    user_id = get_jwt_identity()
    behavior_data = request.json
    
    success = train_behavior_model(user_id, behavior_data)
    
    if success:
        return jsonify({'message': 'Model trained successfully'}), 200
    else:
        return jsonify({'error': 'Failed to train model'}), 500

@app.route('/api/ai/predict', methods=['POST'])
@jwt_required()
def predict():
    user_id = get_jwt_identity()
    behavior_data = request.json
    
    trust_score = predict_anomaly(user_id, behavior_data)
    
    return jsonify({'trust_score': trust_score}), 200

@app.route('/api/user/dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    user_id = get_jwt_identity()
    
    # Get current trust score
    user = User.query.get(user_id)
    
    # Get recent sessions
    sessions = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).limit(5).all()
    
    # Get recent alerts
    alerts = Alert.query.filter_by(user_id=user_id).order_by(Alert.timestamp.desc()).limit(5).all()
    
    return jsonify({
        'trust_score': user.trust_score if user else 100,
        'recent_sessions': [session.to_dict() for session in sessions],
        'recent_alerts': [alert.to_dict() for alert in alerts]
    }), 200

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_users():
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200

@app.route('/api/admin/logs', methods=['GET'])
@jwt_required()
def admin_logs():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(50).all()
    return jsonify({'logs': [alert.to_dict() for alert in alerts]}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)