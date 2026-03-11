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

# Commented out - using the more complete version below at line 765
# @app.route('/api/machines/list')
# def list_machines():
#     """Get all registered machines"""
#     try:
#         machines = database.get_all_machines()
#         return jsonify({
#             'success': True,
#             'machines': machines,
#             'total': len(machines)
#         })
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/ingest', methods=['POST'])
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

@app.route('/api/readings/recent')
@login_required
def get_recent_readings():
    """Get recent readings from database for dashboard graphs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        machine_id = request.args.get('machine_id')
        
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        if machine_id:
            query = '''
                SELECT timestamp, air_temperature, process_temperature, 
                       rotational_speed, torque, tool_wear
                FROM machine_readings
                WHERE machine_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            cursor.execute(query, (machine_id, limit))
        else:
            query = '''
                SELECT timestamp, air_temperature, process_temperature, 
                       rotational_speed, torque, tool_wear
                FROM machine_readings
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            cursor.execute(query, (limit,))
        
        readings = cursor.fetchall()
        conn.close()
        
        if not readings:
            return jsonify({
                'timestamps': [],
                'temperature': [],
                'pressure': [],
                'vibration': []
            })
        
        # Reverse to get chronological order
        readings = list(reversed(readings))
        
        # Format data for charts (convert temperature from K to C for display)
        timestamps = [r['timestamp'].split('T')[1][:8] if 'T' in r['timestamp'] else r['timestamp'][-8:] for r in readings]
        temperature = [r['air_temperature'] - 273.15 for r in readings]  # Convert to Celsius
        pressure = [r['torque'] * 2 for r in readings]  # Use torque as pressure proxy
        vibration = [r['rotational_speed'] / 100 for r in readings]  # Scale RPM to vibration
        
        return jsonify({
            'timestamps': timestamps,
            'temperature': temperature,
            'pressure': pressure,
            'vibration': vibration
        })
        
    except Exception as e:
        print(f"Error getting recent readings: {e}")
        return jsonify({
            'timestamps': [],
            'temperature': [],
            'pressure': [],
            'vibration': []
        })

@app.route('/api/health/calculated')
@login_required
def get_calculated_health():
    """Calculate health scores from recent machine data"""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Get recent predictions grouped by machine type
        cursor.execute('''
            SELECT machine_id, AVG(failure_probability) as avg_prob, COUNT(*) as count
            FROM predictions
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY machine_id
        ''')
        
        machines_data = cursor.fetchall()
        conn.close()
        
        # Default health scores
        health_scores = {
            'pump': {'score': 0, 'status': 'no_data'},
            'motor': {'score': 0, 'status': 'no_data'},
            'hvac': {'score': 0, 'status': 'no_data'}
        }
        
        # Map machines to categories and calculate health
        for machine in machines_data:
            avg_prob = machine['avg_prob']
            # Health score = 100 - (failure_probability * 100)
            score = int(100 - (avg_prob * 100))
            
            if score >= 80:
                status = 'healthy'
            elif score >= 60:
                status = 'warning'
            else:
                status = 'critical'
            
            machine_id = machine['machine_id'].lower()
            
            # Map to equipment types
            if 'pump' in machine_id:
                health_scores['pump'] = {'score': score, 'status': status}
            elif 'motor' in machine_id:
                health_scores['motor'] = {'score': score, 'status': status}
            elif 'compressor' in machine_id or 'hvac' in machine_id:
                health_scores['hvac'] = {'score': score, 'status': status}
        
        return jsonify(health_scores)
        
    except Exception as e:
        print(f"Error calculating health: {e}")
        from ml_models.health_calculator import calculate_health_scores
        return jsonify(calculate_health_scores())

@app.route('/api/predictions/recent')
@login_required
def get_recent_predictions_list():
    """Get recent failure predictions from database"""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT machine_id, failure_probability, risk_level, timestamp
            FROM predictions
            WHERE will_fail = 1 OR risk_level IN ('high', 'critical')
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        
        predictions = cursor.fetchall()
        conn.close()
        
        predictions_list = []
        for pred in predictions:
            # Calculate time to failure based on risk level
            if pred['risk_level'] == 'critical':
                time_to_failure = '6-12 hours'
            elif pred['risk_level'] == 'high':
                time_to_failure = '24-48 hours'
            else:
                time_to_failure = '2-5 days'
            
            predictions_list.append({
                'equipment': pred['machine_id'].replace('-', ' ').title(),
                'timeToFailure': time_to_failure,
                'details': f'Failure probability: {pred["failure_probability"]*100:.1f}%',
                'confidence': int(pred['failure_probability'] * 100),
                'confidenceLevel': pred['risk_level']
            })
        
        return jsonify({
            'predictions': predictions_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error getting predictions: {e}")
        return jsonify({'predictions': [], 'timestamp': datetime.now().isoformat()})

@app.route('/api/anomalies/detected')
@login_required
def get_detected_anomalies():
    """Detect anomalies from stored data"""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, rotational_speed, air_temperature, torque
            FROM machine_readings
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        readings = cursor.fetchall()
        conn.close()
        
        if not readings:
            return jsonify({
                'timestamps': [],
                'values': [],
                'anomalies': [],
                'anomaly_count': 0
            })
        
        readings = list(reversed(readings))
        
        # Simple anomaly detection: values outside 2 standard deviations
        import numpy as np
        
        vibrations = [r['rotational_speed'] / 100 for r in readings]
        mean = np.mean(vibrations)
        std = np.std(vibrations)
        
        anomalies = [abs(v - mean) > 2 * std for v in vibrations]
        timestamps = [r['timestamp'].split('T')[1][:8] if 'T' in r['timestamp'] else r['timestamp'][-8:] for r in readings]
        
        return jsonify({
            'timestamps': timestamps,
            'values': vibrations,
            'anomalies': anomalies,
            'anomaly_count': sum(anomalies)
        })
        
    except Exception as e:
        print(f"Error detecting anomalies: {e}")
        return jsonify({
            'timestamps': [],
            'values': [],
            'anomalies': [],
            'anomaly_count': 0
        })

@app.route('/api/machines/list')
def get_machines_list():
    """Get list of all machines with their latest status"""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Get unique machines with their latest readings
        query = '''
            SELECT DISTINCT mr.machine_id, mr.machine_type,
                   MAX(mr.timestamp) as last_seen,
                   (SELECT COUNT(*) FROM machine_readings WHERE machine_id = mr.machine_id) as reading_count
            FROM machine_readings mr
            GROUP BY mr.machine_id
            ORDER BY last_seen DESC
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        machines = []
        for row in rows:
            machine_id = row[0]
            
            # Get latest health prediction
            pred_query = '''
                SELECT failure_probability, will_fail, risk_level
                FROM predictions
                WHERE machine_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            '''
            cursor.execute(pred_query, (machine_id,))
            pred_row = cursor.fetchone()
            
            health_score = 100
            status = 'active'
            risk_level = 'LOW'
            
            if pred_row:
                failure_prob = pred_row[0]
                health_score = int(100 - (failure_prob * 100))
                risk_level = pred_row[2]
                
                if health_score >= 80:
                    status = 'active'
                elif health_score >= 60:
                    status = 'warning'
                else:
                    status = 'critical'
            
            # Create a readable machine name from ID
            machine_name = machine_id.replace('-', ' ').title()
            
            machines.append({
                'machine_id': machine_id,
                'machine_name': machine_name,
                'machine_type': row[1],
                'location': 'Default Location',
                'last_seen': row[2],
                'last_reading': row[2],  # Same as last_seen
                'reading_count': row[3],
                'total_readings': row[3],  # Same as reading_count
                'health_score': health_score,
                'status': status,
                'risk_level': risk_level
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'machines': machines,
            'total_count': len(machines)
        })
        
    except Exception as e:
        print(f"Error getting machines list: {e}")
        return jsonify({
            'success': False,
            'machines': [],
            'total_count': 0,
            'error': str(e)
        })

@app.route('/api/machine/<machine_id>/details')
def get_machine_details(machine_id):
    """Get detailed data for a specific machine"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Get recent readings
        query = '''
            SELECT timestamp, air_temperature, process_temperature, 
                   rotational_speed, torque, tool_wear
            FROM machine_readings
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (machine_id, limit))
        rows = cursor.fetchall()
        
        timestamps = []
        temperatures = []
        pressures = []
        speeds = []
        torques = []
        
        for row in reversed(rows):
            timestamps.append(row[0])
            temperatures.append(round(row[1] - 273.15, 2))  # K to C
            pressures.append(round(row[2] - 273.15, 2))  # Process temp
            speeds.append(row[3])
            torques.append(row[4])
        
        # Get recent predictions
        pred_query = '''
            SELECT timestamp, failure_probability, risk_level
            FROM predictions
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        '''
        cursor.execute(pred_query, (machine_id,))
        pred_rows = cursor.fetchall()
        
        predictions = []
        for pred_row in pred_rows:
            predictions.append({
                'timestamp': pred_row[0],
                'failure_probability': round(pred_row[1] * 100, 1),
                'risk_level': pred_row[2]
            })
        
        conn.close()
        
        return jsonify({
            'machine_id': machine_id,
            'readings': {
                'timestamps': timestamps,
                'temperatures': temperatures,
                'pressures': pressures,
                'speeds': speeds,
                'torques': torques
            },
            'predictions': predictions
        })
        
    except Exception as e:
        print(f"Error getting machine details: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/monitor')
@login_required
def monitor():
    """Real-time monitoring dashboard"""
    return render_template('monitor.html', username=session.get('username'))

if __name__ == '__main__':
    # Get port from environment variable (for Render deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Use debug mode only in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
