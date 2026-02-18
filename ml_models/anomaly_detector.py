import numpy as np
from datetime import datetime, timedelta
from ml_models.data_simulator import generate_sensor_data

def detect_anomalies():
    """Detect anomalies in sensor data"""
    
    # Get recent sensor data
    data = generate_sensor_data(100)
    
    # Detect anomalies in each sensor type
    vibration_anomalies = _detect_anomalies_zscore(data['vibration'], threshold=2.5)
    temperature_anomalies = _detect_anomalies_zscore(data['temperature'], threshold=2.5)
    pressure_anomalies = _detect_anomalies_zscore(data['pressure'], threshold=3.0)
    
    # Combine anomalies (if any sensor shows anomaly, mark as anomaly)
    combined_anomalies = [
        vib or temp or press
        for vib, temp, press in zip(vibration_anomalies, temperature_anomalies, pressure_anomalies)
    ]
    
    # For visualization, use vibration data as primary indicator
    return {
        'timestamps': data['timestamps'],
        'values': data['vibration'],
        'anomalies': combined_anomalies,
        'anomaly_count': sum(combined_anomalies)
    }

def _detect_anomalies_zscore(data, threshold=3.0):
    """
    Detect anomalies using Z-score method
    
    Args:
        data: List or array of values
        threshold: Z-score threshold (default 3.0)
    
    Returns:
        List of boolean values indicating anomalies
    """
    data_array = np.array(data)
    
    # Calculate mean and standard deviation
    mean = np.mean(data_array)
    std = np.std(data_array)
    
    if std == 0:
        return [False] * len(data)
    
    # Calculate Z-scores
    z_scores = np.abs((data_array - mean) / std)
    
    # Identify anomalies
    anomalies = (z_scores > threshold).tolist()
    
    return anomalies

def _detect_anomalies_iqr(data):
    """
    Detect anomalies using Interquartile Range (IQR) method
    
    Args:
        data: List or array of values
    
    Returns:
        List of boolean values indicating anomalies
    """
    data_array = np.array(data)
    
    # Calculate quartiles
    q1 = np.percentile(data_array, 25)
    q3 = np.percentile(data_array, 75)
    iqr = q3 - q1
    
    # Define bounds
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Identify anomalies
    anomalies = ((data_array < lower_bound) | (data_array > upper_bound)).tolist()
    
    return anomalies

def _detect_anomalies_moving_average(data, window=10, threshold=2.0):
    """
    Detect anomalies using moving average method
    
    Args:
        data: List or array of values
        window: Window size for moving average
        threshold: Multiplier for standard deviation
    
    Returns:
        List of boolean values indicating anomalies
    """
    data_array = np.array(data)
    anomalies = [False] * len(data)
    
    if len(data) < window:
        return anomalies
    
    # Calculate moving average and standard deviation
    for i in range(window, len(data)):
        window_data = data_array[i-window:i]
        mean = np.mean(window_data)
        std = np.std(window_data)
        
        if std > 0:
            z_score = abs((data_array[i] - mean) / std)
            anomalies[i] = z_score > threshold
    
    return anomalies

def detect_anomalies_isolation_forest(data):
    """
    Detect anomalies using Isolation Forest algorithm
    Note: This is a simplified version. In production, use sklearn.ensemble.IsolationForest
    
    Args:
        data: Dictionary containing sensor readings
    
    Returns:
        List of anomaly scores
    """
    # This would require scikit-learn in production
    # For now, using a simplified approach
    
    vibration = np.array(data.get('vibration', []))
    temperature = np.array(data.get('temperature', []))
    pressure = np.array(data.get('pressure', []))
    
    # Simplified anomaly scoring
    scores = []
    for v, t, p in zip(vibration, temperature, pressure):
        score = 0
        # Check if values are outside expected ranges
        if v > 15 or v < 5:
            score += 0.4
        if t > 85 or t < 60:
            score += 0.3
        if p > 105 or p < 95:
            score += 0.3
        scores.append(score)
    
    return scores

def analyze_anomaly_patterns(anomalies, timestamps):
    """
    Analyze patterns in detected anomalies
    
    Args:
        anomalies: List of boolean anomaly indicators
        timestamps: List of corresponding timestamps
    
    Returns:
        Dictionary with anomaly analysis
    """
    total_anomalies = sum(anomalies)
    
    if total_anomalies == 0:
        return {
            'total_count': 0,
            'severity': 'low',
            'pattern': 'none'
        }
    
    # Calculate anomaly frequency
    frequency = total_anomalies / len(anomalies)
    
    # Determine severity
    if frequency > 0.2:
        severity = 'high'
    elif frequency > 0.1:
        severity = 'medium'
    else:
        severity = 'low'
    
    # Detect clustering (anomalies occurring in groups)
    clusters = _detect_clusters(anomalies)
    
    pattern = 'clustered' if len(clusters) > 1 else 'isolated' if total_anomalies < 3 else 'scattered'
    
    return {
        'total_count': total_anomalies,
        'frequency': round(frequency, 3),
        'severity': severity,
        'pattern': pattern,
        'cluster_count': len(clusters)
    }

def _detect_clusters(anomalies, min_gap=5):
    """Detect clusters of anomalies"""
    clusters = []
    current_cluster = []
    
    for i, is_anomaly in enumerate(anomalies):
        if is_anomaly:
            current_cluster.append(i)
        elif current_cluster:
            clusters.append(current_cluster)
            current_cluster = []
    
    if current_cluster:
        clusters.append(current_cluster)
    
    return clusters
