import numpy as np
import random
from datetime import datetime, timedelta

def get_failure_predictions():
    """Get failure predictions for equipment"""
    
    predictions = []
    
    # Simulate predictions with varying confidence levels
    prediction_scenarios = [
        {
            'equipment': 'Pump A-01',
            'timeToFailure': '12-18 hours',
            'details': 'Vibration levels increasing beyond normal threshold. Bearing degradation detected.',
            'confidence': random.randint(75, 90),
            'confidenceLevel': 'high'
        },
        {
            'equipment': 'Motor B-02',
            'timeToFailure': '36-42 hours',
            'details': 'Temperature fluctuations detected. Cooling system efficiency declining.',
            'confidence': random.randint(60, 75),
            'confidenceLevel': 'medium'
        },
        {
            'equipment': 'HVAC C-03',
            'timeToFailure': '2-5 days',
            'details': 'Pressure anomalies indicate potential compressor issues.',
            'confidence': random.randint(50, 65),
            'confidenceLevel': 'medium'
        }
    ]
    
    # Randomly include 1-2 predictions to simulate real-time predictions
    num_predictions = random.randint(1, 2)
    predictions = random.sample(prediction_scenarios, num_predictions)
    
    return {
        'predictions': predictions,
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
