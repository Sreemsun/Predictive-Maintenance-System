import numpy as np
import random

def calculate_health_scores():
    """Calculate health scores for each equipment"""
    
    # Simulate health scores with some variability
    scores = {
        'pump': _generate_health_data('pump'),
        'motor': _generate_health_data('motor'),
        'hvac': _generate_health_data('hvac')
    }
    
    return scores

def _generate_health_data(equipment_type):
    """Generate health data for a specific equipment"""
    
    # Base scores (can be modified to simulate degradation over time)
    base_scores = {
        'pump': 85,
        'motor': 92,
        'hvac': 78
    }
    
    # Add random variation
    base_score = base_scores.get(equipment_type, 80)
    variation = random.uniform(-8, 8)
    score = max(0, min(100, base_score + variation))
    
    # Determine status based on score
    if score >= 80:
        status = 'healthy'
    elif score >= 60:
        status = 'warning'
    else:
        status = 'critical'
    
    return {
        'score': round(score),
        'status': status
    }

def calculate_specific_health(vibration, temperature, pressure):
    """
    Calculate health score based on sensor readings
    
    Args:
        vibration: Vibration level (mm/s)
        temperature: Temperature (°C)
        pressure: Pressure (PSI)
    
    Returns:
        Health score (0-100)
    """
    
    # Define normal ranges
    vibration_normal = (5, 12)
    temperature_normal = (60, 85)
    pressure_normal = (95, 105)
    
    # Calculate deviation scores (0-100, where 100 is perfect)
    vibration_score = _calculate_deviation_score(vibration, vibration_normal, 20)
    temperature_score = _calculate_deviation_score(temperature, temperature_normal, 15)
    pressure_score = _calculate_deviation_score(pressure, pressure_normal, 10)
    
    # Weighted average (vibration is most important indicator)
    health_score = (
        vibration_score * 0.5 +
        temperature_score * 0.3 +
        pressure_score * 0.2
    )
    
    return round(health_score)

def _calculate_deviation_score(value, normal_range, tolerance):
    """
    Calculate how much a value deviates from normal range
    
    Args:
        value: Current value
        normal_range: Tuple of (min, max) normal values
        tolerance: Maximum acceptable deviation
    
    Returns:
        Score from 0-100
    """
    min_normal, max_normal = normal_range
    
    if min_normal <= value <= max_normal:
        return 100
    elif value < min_normal:
        deviation = min_normal - value
    else:
        deviation = value - max_normal
    
    # Calculate score based on deviation
    score = max(0, 100 - (deviation / tolerance * 100))
    return score
