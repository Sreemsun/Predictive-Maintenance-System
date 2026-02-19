from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# Mock user database (replace with actual database in production)
USERS = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest(),
    'operator': hashlib.sha256('operator123'.encode()).hexdigest()
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if username in USERS and USERS[username] == hashed_password:
            session['username'] = username
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Check if username already exists
        if username in USERS:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Hash password and store user
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        USERS[username] = hashed_password
        
        return jsonify({'success': True, 'message': 'Registration successful! Redirecting to login...'})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/api/sensor-data')
@login_required
def get_sensor_data():
    """Generate simulated sensor data"""
    from ml_models.data_simulator import generate_sensor_data
    data = generate_sensor_data()
    return jsonify(data)

@app.route('/api/health-score')
@login_required
def get_health_score():
    """Get equipment health scores"""
    from ml_models.health_calculator import calculate_health_scores
    scores = calculate_health_scores()
    return jsonify(scores)

@app.route('/api/predictions')
@login_required
def get_predictions():
    """Get failure predictions"""
    from ml_models.predictor import get_failure_predictions
    predictions = get_failure_predictions()
    return jsonify(predictions)

@app.route('/api/anomalies')
@login_required
def get_anomalies():
    """Detect anomalies in sensor data"""
    from ml_models.anomaly_detector import detect_anomalies
    anomalies = detect_anomalies()
    return jsonify(anomalies)

@app.route('/api/alerts')
@login_required
def get_alerts():
    """Get active alerts"""
    from ml_models.alert_system import get_active_alerts
    alerts = get_active_alerts()
    return jsonify(alerts)

@app.route('/api/historical-data')
@login_required
def get_historical_data():
    """Get historical sensor trends"""
    hours = request.args.get('hours', 24, type=int)
    from ml_models.data_simulator import generate_historical_data
    data = generate_historical_data(hours)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
