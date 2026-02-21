from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
from functools import wraps
import os
import database

# Initialize Flask with correct template and static folders
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# Initialize database
database.init_database()

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

@app.route('/predict')
@login_required
def predict():
    return render_template('predict.html', username=session.get('username'))

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

@app.route('/api/ml-predict', methods=['POST'])
@login_required
def ml_predict():
    """Make prediction using trained ML model"""
    from ml_models.predictor import predict_machine_failure
    
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['type', 'air_temp', 'process_temp', 'rotational_speed', 'torque', 'tool_wear']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Make prediction
        prediction = predict_machine_failure(data)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/model-info')
@login_required
def get_model_info():
    """Get information about the loaded ML model"""
    from ml_models.predictor import get_model_info
    
    info = get_model_info()
    return jsonify(info)

@app.route('/api/batch-predict')
@login_required
def batch_predict():
    """Make predictions on batch of samples from dataset"""
    from ml_models.predictor import batch_predict_from_csv
    
    num_samples = request.args.get('samples', 10, type=int)
    results = batch_predict_from_csv('dataset.csv', num_samples)
    
    # Calculate accuracy
    correct = sum(1 for r in results if r.get('will_fail') == r.get('actual_failure'))
    accuracy = (correct / len(results) * 100) if results else 0
    
    return jsonify({
        'predictions': results,
        'total_samples': len(results),
        'accuracy': accuracy,
        'timestamp': datetime.now().isoformat()
    })

# =============================================================================
# CONTINUOUS MONITORING API ENDPOINTS
# =============================================================================

@app.route('/api/machines/register', methods=['POST'])
@login_required
def register_machine():
    """Register a new machine for monitoring"""
    try:
        data = request.json
        
        required_fields = ['machine_id', 'machine_name', 'machine_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        success = database.register_machine(
            data['machine_id'],
            data['machine_name'],
            data['machine_type'],
            data.get('location')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f"Machine {data['machine_id']} registered successfully"
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Machine already registered'
            }), 409
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/machines/list')
@login_required
def list_machines():
    """Get all registered machines"""
    try:
        machines = database.get_all_machines()
        return jsonify({
            'success': True,
            'machines': machines,
            'total': len(machines)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/ingest', methods=['POST'])
@login_required
def ingest_data():
    """
    Ingest continuous machine data and make prediction
    
    Expected JSON format:
    {
        "machine_id": "MACHINE-001",
        "type": "L",
        "air_temp": 298.5,
        "process_temp": 308.7,
        "rotational_speed": 1500,
        "torque": 40.0,
        "tool_wear": 50,
        "timestamp": "2024-01-01T12:00:00" (optional)
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['machine_id', 'type', 'air_temp', 'process_temp', 
                          'rotational_speed', 'torque', 'tool_wear']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Store machine reading
        reading_id = database.insert_machine_reading(
            machine_id=data['machine_id'],
            machine_type=data['type'],
            air_temp=data['air_temp'],
            process_temp=data['process_temp'],
            rotational_speed=data['rotational_speed'],
            torque=data['torque'],
            tool_wear=data['tool_wear'],
            timestamp=data.get('timestamp')
        )
        
        # Make prediction
        from ml_models.predictor import predict_machine_failure
        
        machine_data = {
            'type': data['type'],
            'air_temp': data['air_temp'],
            'process_temp': data['process_temp'],
            'rotational_speed': data['rotational_speed'],
            'torque': data['torque'],
            'tool_wear': data['tool_wear']
        }
        
        prediction = predict_machine_failure(machine_data)
        
        # Store prediction
        prediction_id = database.insert_prediction(
            reading_id=reading_id,
            machine_id=data['machine_id'],
            will_fail=int(prediction['will_fail']),
            failure_probability=prediction['failure_probability'],
            confidence=prediction['confidence'],
            risk_level=prediction['risk_level'],
            timestamp=data.get('timestamp')
        )
        
        return jsonify({
            'success': True,
            'reading_id': reading_id,
            'prediction_id': prediction_id,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/batch-ingest', methods=['POST'])
@login_required
def batch_ingest_data():
    """
    Ingest multiple machine readings at once
    
    Expected JSON format:
    {
        "readings": [
            {
                "machine_id": "MACHINE-001",
                "type": "L",
                "air_temp": 298.5,
                ...
            },
            ...
        ]
    }
    """
    try:
        data = request.json
        
        if 'readings' not in data or not isinstance(data['readings'], list):
            return jsonify({'success': False, 'error': 'Invalid format. Expected "readings" array'}), 400
        
        results = []
        from ml_models.predictor import predict_machine_failure
        
        for reading in data['readings']:
            try:
                # Store reading
                reading_id = database.insert_machine_reading(
                    machine_id=reading['machine_id'],
                    machine_type=reading['type'],
                    air_temp=reading['air_temp'],
                    process_temp=reading['process_temp'],
                    rotational_speed=reading['rotational_speed'],
                    torque=reading['torque'],
                    tool_wear=reading['tool_wear'],
                    timestamp=reading.get('timestamp')
                )
                
                # Make prediction
                machine_data = {
                    'type': reading['type'],
                    'air_temp': reading['air_temp'],
                    'process_temp': reading['process_temp'],
                    'rotational_speed': reading['rotational_speed'],
                    'torque': reading['torque'],
                    'tool_wear': reading['tool_wear']
                }
                
                prediction = predict_machine_failure(machine_data)
                
                # Store prediction
                prediction_id = database.insert_prediction(
                    reading_id=reading_id,
                    machine_id=reading['machine_id'],
                    will_fail=int(prediction['will_fail']),
                    failure_probability=prediction['failure_probability'],
                    confidence=prediction['confidence'],
                    risk_level=prediction['risk_level'],
                    timestamp=reading.get('timestamp')
                )
                
                results.append({
                    'machine_id': reading['machine_id'],
                    'reading_id': reading_id,
                    'prediction_id': prediction_id,
                    'success': True
                })
                
            except Exception as e:
                results.append({
                    'machine_id': reading.get('machine_id', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        successful = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'processed': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/history/<machine_id>')
@login_required
def get_machine_history(machine_id):
    """Get historical data for a specific machine"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 1000, type=int)
        
        history = database.get_machine_history(machine_id, hours, limit)
        
        return jsonify({
            'success': True,
            'machine_id': machine_id,
            'data': history,
            'count': len(history),
            'hours': hours
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/recent-predictions')
@login_required
def get_recent_predictions_api():
    """Get recent predictions across all machines"""
    try:
        limit = request.args.get('limit', 50, type=int)
        predictions = database.get_recent_predictions(limit)
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts/active')
@login_required
def get_active_alerts_api():
    """Get active alerts"""
    try:
        limit = request.args.get('limit', 50, type=int)
        alerts = database.get_active_alerts(limit)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts/acknowledge/<int:alert_id>', methods=['POST'])
@login_required
def acknowledge_alert_api(alert_id):
    """Acknowledge an alert"""
    try:
        database.acknowledge_alert(alert_id)
        
        return jsonify({
            'success': True,
            'message': f'Alert {alert_id} acknowledged'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics')
@login_required
def get_statistics_api():
    """Get statistics for machines"""
    try:
        machine_id = request.args.get('machine_id')
        hours = request.args.get('hours', 24, type=int)
        
        stats = database.get_statistics(machine_id, hours)
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'machine_id': machine_id,
            'hours': hours
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare')
@login_required
def compare_machines():
    """Compare multiple machines"""
    try:
        machine_ids = request.args.getlist('machine_ids')
        hours = request.args.get('hours', 24, type=int)
        
        if not machine_ids:
            return jsonify({'success': False, 'error': 'No machine_ids provided'}), 400
        
        comparison = database.get_comparison_data(machine_ids, hours)
        
        return jsonify({
            'success': True,
            'comparison': comparison,
            'machine_count': len(comparison),
            'hours': hours
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/monitor')
@login_required
def monitor():
    """Real-time monitoring dashboard"""
    return render_template('monitor.html', username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
