# AuthSense+ - Intelligent Behavioral Authentication System

## Overview
AuthSense+ is an AI-powered behavioral authentication system that continuously monitors user behavior to detect anomalies and protect against account hijacking.

## Features
- Real-time behavioral monitoring (typing patterns, mouse movements)
- AI-powered anomaly detection
- Automatic session termination on suspicious activity
- Location tracking and alerts
- Comprehensive admin dashboard

## Technology Stack
- Backend: Python Flask, SQLAlchemy
- Frontend: React.js, TailwindCSS
- Database: PostgreSQL
- AI/ML: Scikit-learn, TensorFlow
- Authentication: JWT, OTP

## Installation
1. Clone the repository
2. Install backend dependencies: `pip install -r requirements.txt`
3. Install frontend dependencies: `cd frontend && npm install`
4. Set up environment variables in `.env`
5. Run backend: `python backend/app.py`
6. Run frontend: `cd frontend && npm start`