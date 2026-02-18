import random
from datetime import datetime, timedelta

def get_active_alerts():
    """Get list of active alerts"""
    
    alert_templates = [
        {
            'equipment': 'Pump A-01',
            'message': 'Vibration levels exceeded threshold (18.5 mm/s)',
            'severity': 'critical',
            'timestamp': _get_recent_timestamp(minutes=5)
        },
        {
            'equipment': 'Motor B-02',
            'message': 'Temperature spike detected (92°C)',
            'severity': 'warning',
            'timestamp': _get_recent_timestamp(minutes=12)
        },
        {
            'equipment': 'HVAC C-03',
            'message': 'Pressure fluctuation detected',
            'severity': 'warning',
            'timestamp': _get_recent_timestamp(minutes=25)
        },
        {
            'equipment': 'Pump A-01',
            'message': 'Bearing temperature above normal range',
            'severity': 'info',
            'timestamp': _get_recent_timestamp(minutes=45)
        }
    ]
    
    # Randomly return 0-3 alerts to simulate real-time system
    num_alerts = random.randint(0, 3)
    active_alerts = random.sample(alert_templates, num_alerts) if num_alerts > 0 else []
    
    # Sort by severity (critical first)
    severity_order = {'critical': 0, 'warning': 1, 'info': 2}
    active_alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
    
    return {
        'alerts': active_alerts,
        'total_count': len(active_alerts)
    }

def generate_alert(equipment, sensor_type, value, threshold, severity='warning'):
    """
    Generate an alert based on sensor reading
    
    Args:
        equipment: Equipment name
        sensor_type: Type of sensor (vibration, temperature, pressure)
        value: Current sensor value
        threshold: Threshold value
        severity: Alert severity (critical, warning, info)
    
    Returns:
        Alert dictionary
    """
    
    messages = {
        'vibration': f'Vibration level {value:.1f} mm/s exceeds threshold {threshold} mm/s',
        'temperature': f'Temperature {value:.1f}°C exceeds threshold {threshold}°C',
        'pressure': f'Pressure {value:.1f} PSI outside normal range ({threshold} PSI)'
    }
    
    alert = {
        'equipment': equipment,
        'message': messages.get(sensor_type, f'{sensor_type} anomaly detected'),
        'severity': severity,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sensor_type': sensor_type,
        'value': value,
        'threshold': threshold
    }
    
    return alert

def evaluate_alert_conditions(sensor_data, equipment_name):
    """
    Evaluate sensor data and generate alerts if conditions are met
    
    Args:
        sensor_data: Dictionary containing current sensor readings
        equipment_name: Name of the equipment
    
    Returns:
        List of generated alerts
    """
    
    alerts = []
    
    # Define thresholds
    thresholds = {
        'vibration': {'warning': 15, 'critical': 20},
        'temperature': {'warning': 85, 'critical': 95},
        'pressure': {'warning': 110, 'critical': 120}
    }
    
    # Check vibration
    vibration = sensor_data.get('vibration', 0)
    if vibration > thresholds['vibration']['critical']:
        alerts.append(generate_alert(
            equipment_name, 'vibration', vibration, 
            thresholds['vibration']['critical'], 'critical'
        ))
    elif vibration > thresholds['vibration']['warning']:
        alerts.append(generate_alert(
            equipment_name, 'vibration', vibration,
            thresholds['vibration']['warning'], 'warning'
        ))
    
    # Check temperature
    temperature = sensor_data.get('temperature', 0)
    if temperature > thresholds['temperature']['critical']:
        alerts.append(generate_alert(
            equipment_name, 'temperature', temperature,
            thresholds['temperature']['critical'], 'critical'
        ))
    elif temperature > thresholds['temperature']['warning']:
        alerts.append(generate_alert(
            equipment_name, 'temperature', temperature,
            thresholds['temperature']['warning'], 'warning'
        ))
    
    # Check pressure
    pressure = sensor_data.get('pressure', 0)
    if pressure > thresholds['pressure']['critical'] or pressure < 85:
        alerts.append(generate_alert(
            equipment_name, 'pressure', pressure,
            thresholds['pressure']['critical'], 'critical'
        ))
    elif pressure > thresholds['pressure']['warning'] or pressure < 90:
        alerts.append(generate_alert(
            equipment_name, 'pressure', pressure,
            thresholds['pressure']['warning'], 'warning'
        ))
    
    return alerts

def prioritize_alerts(alerts):
    """
    Prioritize alerts based on severity and recency
    
    Args:
        alerts: List of alert dictionaries
    
    Returns:
        Sorted list of alerts
    """
    
    severity_scores = {
        'critical': 3,
        'warning': 2,
        'info': 1
    }
    
    # Sort by severity (descending) and timestamp (most recent first)
    sorted_alerts = sorted(
        alerts,
        key=lambda x: (
            -severity_scores.get(x['severity'], 0),
            x['timestamp']
        ),
        reverse=True
    )
    
    return sorted_alerts

def send_alert_notification(alert):
    """
    Send alert notification (placeholder for actual implementation)
    
    In production, this would:
    - Send email notifications
    - Push to mobile app
    - Send SMS for critical alerts
    - Log to SIEM system
    - Trigger automated responses
    
    Args:
        alert: Alert dictionary
    """
    
    print(f"[ALERT] {alert['severity'].upper()}: {alert['equipment']} - {alert['message']}")
    
    # Placeholder for actual notification logic
    # if alert['severity'] == 'critical':
    #     send_sms(alert)
    #     send_email(alert)
    #     trigger_emergency_protocol(alert)
    # elif alert['severity'] == 'warning':
    #     send_email(alert)
    #     log_to_system(alert)

def _get_recent_timestamp(minutes=0):
    """Get a recent timestamp"""
    time = datetime.now() - timedelta(minutes=minutes)
    return time.strftime('%Y-%m-%d %H:%M:%S')

def calculate_alert_statistics(alerts, time_period='24h'):
    """
    Calculate statistics about alerts over a time period
    
    Args:
        alerts: List of alerts
        time_period: Time period for analysis
    
    Returns:
        Dictionary with alert statistics
    """
    
    total_alerts = len(alerts)
    
    if total_alerts == 0:
        return {
            'total': 0,
            'critical': 0,
            'warning': 0,
            'info': 0,
            'average_per_hour': 0
        }
    
    # Count by severity
    severity_counts = {
        'critical': sum(1 for a in alerts if a['severity'] == 'critical'),
        'warning': sum(1 for a in alerts if a['severity'] == 'warning'),
        'info': sum(1 for a in alerts if a['severity'] == 'info')
    }
    
    # Calculate rate
    hours = int(time_period.rstrip('h'))
    average_per_hour = total_alerts / hours
    
    return {
        'total': total_alerts,
        'critical': severity_counts['critical'],
        'warning': severity_counts['warning'],
        'info': severity_counts['info'],
        'average_per_hour': round(average_per_hour, 2)
    }
