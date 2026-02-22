import numpy as np
from datetime import datetime, timedelta

def generate_sensor_data(points=50):
    """Generate empty sensor data - no simulated values"""
    # Return empty data
    return {
        'timestamps': [],
        'temperature': [],
        'pressure': [],
        'vibration': []
    }

def generate_historical_data(hours=24):
    """Generate historical sensor data for specified hours"""
    points = hours * 12  # One point every 5 minutes
    now = datetime.now()
    timestamps = [(now - timedelta(minutes=i*5)).strftime('%Y-%m-%d %H:%M') for i in range(points)][::-1]
    
    # Generate more realistic long-term trends
    t = np.linspace(0, hours, points)
    
    # Temperature with daily cycle
    temperature = 70 + 10 * np.sin(2 * np.pi * t / 24) + np.random.normal(0, 1.5, points)
    
    # Pressure with gradual drift
    pressure = 100 + 5 * np.sin(2 * np.pi * t / 48) + np.random.normal(0, 1, points)
    
    # Vibration with increasing trend (wearing equipment)
    vibration = 8 + 0.1 * t + 3 * np.abs(np.sin(2 * np.pi * t / 12)) + np.random.normal(0, 0.8, points)
    
    # Add some anomalies
    anomaly_count = max(1, points // 20)
    spike_indices = np.random.choice(points, size=anomaly_count, replace=False)
    vibration[spike_indices] += np.random.uniform(5, 12, anomaly_count)
    
    return {
        'timestamps': timestamps,
        'temperature': temperature.tolist(),
        'pressure': pressure.tolist(),
        'vibration': vibration.tolist()
    }
