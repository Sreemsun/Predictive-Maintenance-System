import numpy as np
import random
from datetime import datetime, timedelta
import joblib
import os
import pandas as pd

def get_failure_predictions():
    """Get failure predictions for equipment"""
    
    # Return empty predictions - no simulated data
    return {
        'predictions': [],
        'timestamp': datetime.now().isoformat()
    }

def predict_failure_time(sensor_history):
    """
    Predict time to failure based on sensor history
    
    Args:
        sensor_history: Dictionary containing sensor readings over time
    
    Returns:
        Predicted hours until failure, confidence score
    """
    
    # This is a simplified prediction model
    # In production, you would use trained ML models (LSTM, Prophet, etc.)
    
    vibration = np.array(sensor_history.get('vibration', []))
    temperature = np.array(sensor_history.get('temperature', []))
    
    # Calculate trends
    vibration_trend = _calculate_trend(vibration)
    temperature_trend = _calculate_trend(temperature)
    
    # Check for anomalies
    vibration_anomalies = _count_anomalies(vibration, threshold=15)
    temperature_anomalies = _count_anomalies(temperature, threshold=80)
    
    # Simple prediction logic
    risk_score = 0
    
    if vibration_trend > 0.2:
        risk_score += 30
    if temperature_trend > 0.15:
        risk_score += 25
    if vibration_anomalies > 3:
        risk_score += 25
    if temperature_anomalies > 2:
        risk_score += 20
    
    # Estimate time to failure based on risk score
    if risk_score > 70:
        hours_to_failure = random.uniform(2, 12)
        confidence = random.uniform(75, 90)
    elif risk_score > 40:
        hours_to_failure = random.uniform(12, 48)
        confidence = random.uniform(60, 75)
    else:
        hours_to_failure = random.uniform(48, 168)
        confidence = random.uniform(40, 60)
    
    return hours_to_failure, confidence

def _calculate_trend(data):
    """Calculate the trend (slope) of data"""
    if len(data) < 2:
        return 0
    
    x = np.arange(len(data))
    coefficients = np.polyfit(x, data, 1)
    return coefficients[0]  # Return slope

def _count_anomalies(data, threshold):
    """Count values exceeding threshold"""
    return np.sum(data > threshold)

def calculate_rul(sensor_data):
    """
    Calculate Remaining Useful Life (RUL)
    
    Args:
        sensor_data: Current sensor readings
    
    Returns:
        RUL in hours
    """
    
    # Simplified RUL calculation
    # In production, use proper degradation models
    
    vibration = sensor_data.get('vibration', 8)
    temperature = sensor_data.get('temperature', 70)
    
    # Calculate health degradation rate
    vibration_factor = max(0, (vibration - 8) / 12)  # 0 to 1 scale
    temperature_factor = max(0, (temperature - 70) / 20)  # 0 to 1 scale
    
    degradation_rate = (vibration_factor * 0.6 + temperature_factor * 0.4)
    
    # Estimate RUL (in hours)
    # Assuming normal operation gives 1000 hours RUL
    base_rul = 1000
    rul = base_rul * (1 - degradation_rate)
    
    return max(0, rul)

# =============================================================================
# TRAINED MODEL FUNCTIONS
# =============================================================================

# Global variables to cache loaded models
_loaded_model = None
_loaded_scaler = None
_loaded_encoder = None

def load_trained_model(model_type='gradient_boosting'):
    """
    Load the trained ML model and preprocessing objects
    
    Args:
        model_type: 'random_forest' or 'gradient_boosting'
    
    Returns:
        model, scaler, label_encoder
    """
    global _loaded_model, _loaded_scaler, _loaded_encoder
    
    # Return cached models if already loaded
    if _loaded_model is not None:
        return _loaded_model, _loaded_scaler, _loaded_encoder
    
    try:
        # Get the correct path to trained_models directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(current_dir, 'trained_models')
        
        # Load model
        if model_type == 'random_forest':
            model_path = os.path.join(models_dir, 'random_forest_model.pkl')
        else:
            model_path = os.path.join(models_dir, 'gradient_boosting_model.pkl')
        
        _loaded_model = joblib.load(model_path)
        
        # Load scaler and encoder
        _loaded_scaler = joblib.load(os.path.join(models_dir, 'scaler.pkl'))
        _loaded_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.pkl'))
        
        print(f"Model loaded successfully: {model_type}")
        return _loaded_model, _loaded_scaler, _loaded_encoder
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None, None

def predict_machine_failure(machine_data):
    """
    Predict if a machine will fail using the trained ML model
    
    Args:
        machine_data: Dictionary with keys:
            - type: 'L', 'M', or 'H' (Low, Medium, High quality variant)
            - air_temp: Air temperature in Kelvin
            - process_temp: Process temperature in Kelvin
            - rotational_speed: Rotational speed in rpm
            - torque: Torque in Nm
            - tool_wear: Tool wear in minutes
    
    Returns:
        Dictionary with prediction results:
            - will_fail: Boolean
            - failure_probability: Float (0-1)
            - confidence: Float (0-100)
            - risk_level: String ('low', 'medium', 'high', 'critical')
    """
    
    # Load model
    model, scaler, label_encoder = load_trained_model('gradient_boosting')
    
    if model is None:
        # Fallback to simulated prediction if model not available
        return {
            'will_fail': random.choice([True, False]),
            'failure_probability': random.uniform(0.1, 0.9),
            'confidence': random.uniform(50, 80),
            'risk_level': 'medium',
            'error': 'Model not loaded'
        }
    
    try:
        # Encode machine type
        type_encoded = label_encoder.transform([machine_data['type']])[0]
        
        # Prepare features in the correct order
        features = np.array([[
            type_encoded,
            machine_data['air_temp'],
            machine_data['process_temp'],
            machine_data['rotational_speed'],
            machine_data['torque'],
            machine_data['tool_wear']
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        
        # Get probability (if available)
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_scaled)[0]
            failure_probability = probabilities[1]  # Probability of failure
        else:
            failure_probability = 0.8 if prediction == 1 else 0.2
        
        # Calculate confidence
        confidence = abs(failure_probability - 0.5) * 200  # Scale to 0-100
        
        # Determine risk level
        if failure_probability >= 0.8:
            risk_level = 'critical'
        elif failure_probability >= 0.6:
            risk_level = 'high'
        elif failure_probability >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'will_fail': bool(prediction),
            'failure_probability': float(failure_probability),
            'confidence': float(confidence),
            'risk_level': risk_level
        }
        
    except Exception as e:
        print(f"Error making prediction: {e}")
        return {
            'will_fail': False,
            'failure_probability': 0.0,
            'confidence': 0.0,
            'risk_level': 'unknown',
            'error': str(e)
        }

def batch_predict_from_csv(csv_path='dataset.csv', num_samples=10):
    """
    Make predictions on a batch of samples from CSV
    
    Args:
        csv_path: Path to CSV file
        num_samples: Number of samples to predict
    
    Returns:
        List of prediction results
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Take random samples
        samples = df.sample(min(num_samples, len(df)))
        
        results = []
        for _, row in samples.iterrows():
            machine_data = {
                'type': row['Type'],
                'air_temp': row['Air temperature [K]'],
                'process_temp': row['Process temperature [K]'],
                'rotational_speed': row['Rotational speed [rpm]'],
                'torque': row['Torque [Nm]'],
                'tool_wear': row['Tool wear [min]']
            }
            
            prediction = predict_machine_failure(machine_data)
            prediction['actual_failure'] = row['Machine failure']
            prediction['product_id'] = row['Product ID']
            
            results.append(prediction)
        
        return results
        
    except Exception as e:
        print(f"Error in batch prediction: {e}")
        return []

def get_model_info():
    """Get information about the loaded model"""
    model, scaler, encoder = load_trained_model()
    
    if model is None:
        return {'status': 'Model not loaded'}
    
    return {
        'status': 'loaded',
        'model_type': type(model).__name__,
        'feature_count': scaler.n_features_in_ if hasattr(scaler, 'n_features_in_') else 'unknown',
        'classes': encoder.classes_.tolist() if hasattr(encoder, 'classes_') else []
    }
