"""
Database Module for Predictive Maintenance System
Handles storage of machine readings and predictions
"""

import sqlite3
from datetime import datetime
import json
import os

DATABASE_PATH = '../predictive_maintenance.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Machine Readings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machine_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            machine_type TEXT NOT NULL,
            air_temperature REAL NOT NULL,
            process_temperature REAL NOT NULL,
            rotational_speed INTEGER NOT NULL,
            torque REAL NOT NULL,
            tool_wear INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Predictions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reading_id INTEGER,
            machine_id TEXT NOT NULL,
            will_fail INTEGER NOT NULL,
            failure_probability REAL NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reading_id) REFERENCES machine_readings(id)
        )
    ''')
    
    # Machine Registry Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT UNIQUE NOT NULL,
            machine_name TEXT NOT NULL,
            machine_type TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'active',
            last_reading_time DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            prediction_id INTEGER,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            acknowledged INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prediction_id) REFERENCES predictions(id)
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_machine_readings_machine_id 
        ON machine_readings(machine_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_machine_readings_timestamp 
        ON machine_readings(timestamp)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_predictions_machine_id 
        ON predictions(machine_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
        ON predictions(timestamp)
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

def insert_machine_reading(machine_id, machine_type, air_temp, process_temp, 
                          rotational_speed, torque, tool_wear, timestamp=None):
    """Insert a machine reading into the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO machine_readings 
        (machine_id, machine_type, air_temperature, process_temperature, 
         rotational_speed, torque, tool_wear, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (machine_id, machine_type, air_temp, process_temp, 
          rotational_speed, torque, tool_wear, timestamp))
    
    reading_id = cursor.lastrowid
    
    # Update machine last reading time
    cursor.execute('''
        UPDATE machines 
        SET last_reading_time = ? 
        WHERE machine_id = ?
    ''', (timestamp, machine_id))
    
    conn.commit()
    conn.close()
    
    return reading_id

def insert_prediction(reading_id, machine_id, will_fail, failure_probability, 
                     confidence, risk_level, timestamp=None):
    """Insert a prediction into the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO predictions 
        (reading_id, machine_id, will_fail, failure_probability, 
         confidence, risk_level, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (reading_id, machine_id, will_fail, failure_probability, 
          confidence, risk_level, timestamp))
    
    prediction_id = cursor.lastrowid
    
    # Create alert if high risk
    if risk_level in ['high', 'critical'] or will_fail:
        severity = 'critical' if risk_level == 'critical' else 'warning'
        message = f"Machine {machine_id} predicted to fail with {failure_probability*100:.1f}% probability"
        
        cursor.execute('''
            INSERT INTO alerts 
            (machine_id, prediction_id, alert_type, severity, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (machine_id, prediction_id, 'failure_prediction', severity, message))
    
    conn.commit()
    conn.close()
    
    return prediction_id

def register_machine(machine_id, machine_name, machine_type, location=None):
    """Register a new machine in the system"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO machines (machine_id, machine_name, machine_type, location)
            VALUES (?, ?, ?, ?)
        ''', (machine_id, machine_name, machine_type, location))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Machine already exists
        return False
    finally:
        conn.close()

def get_machine_history(machine_id, hours=24, limit=1000):
    """Get historical readings for a machine"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, p.will_fail, p.failure_probability, p.confidence, p.risk_level
        FROM machine_readings r
        LEFT JOIN predictions p ON r.id = p.reading_id
        WHERE r.machine_id = ?
        AND datetime(r.timestamp) >= datetime('now', '-' || ? || ' hours')
        ORDER BY r.timestamp DESC
        LIMIT ?
    ''', (machine_id, hours, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_all_machines():
    """Get all registered machines"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*,
               COUNT(r.id) as total_readings,
               MAX(r.timestamp) as last_reading
        FROM machines m
        LEFT JOIN machine_readings r ON m.machine_id = r.machine_id
        GROUP BY m.machine_id
        ORDER BY m.created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_recent_predictions(limit=50):
    """Get recent predictions across all machines"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, r.machine_type, r.air_temperature, r.process_temperature,
               r.rotational_speed, r.torque, r.tool_wear
        FROM predictions p
        JOIN machine_readings r ON p.reading_id = r.id
        ORDER BY p.timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_active_alerts(limit=50):
    """Get unacknowledged alerts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.*, m.machine_name
        FROM alerts a
        JOIN machines m ON a.machine_id = m.machine_id
        WHERE a.acknowledged = 0
        ORDER BY a.timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def acknowledge_alert(alert_id):
    """Mark an alert as acknowledged"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE alerts SET acknowledged = 1 WHERE id = ?', (alert_id,))
    
    conn.commit()
    conn.close()

def get_statistics(machine_id=None, hours=24):
    """Get statistics for machines"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if machine_id:
        cursor.execute('''
            SELECT 
                COUNT(*) as total_readings,
                AVG(failure_probability) as avg_failure_prob,
                MAX(failure_probability) as max_failure_prob,
                SUM(CASE WHEN will_fail = 1 THEN 1 ELSE 0 END) as failure_predictions,
                SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) as high_count
            FROM predictions
            WHERE machine_id = ?
            AND datetime(timestamp) >= datetime('now', '-' || ? || ' hours')
        ''', (machine_id, hours))
    else:
        cursor.execute('''
            SELECT 
                COUNT(*) as total_readings,
                AVG(failure_probability) as avg_failure_prob,
                MAX(failure_probability) as max_failure_prob,
                SUM(CASE WHEN will_fail = 1 THEN 1 ELSE 0 END) as failure_predictions,
                SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) as high_count
            FROM predictions
            WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' hours')
        ''', (hours,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else {}

def get_comparison_data(machine_ids, hours=24):
    """Get comparison data for multiple machines"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholders = ','.join(['?' for _ in machine_ids])
    
    query = f'''
        SELECT 
            p.machine_id,
            m.machine_name,
            AVG(p.failure_probability) as avg_failure_prob,
            MAX(p.failure_probability) as max_failure_prob,
            AVG(r.air_temperature) as avg_air_temp,
            AVG(r.process_temperature) as avg_process_temp,
            AVG(r.rotational_speed) as avg_speed,
            AVG(r.torque) as avg_torque,
            AVG(r.tool_wear) as avg_tool_wear,
            COUNT(*) as reading_count
        FROM predictions p
        JOIN machine_readings r ON p.reading_id = r.id
        JOIN machines m ON p.machine_id = m.machine_id
        WHERE p.machine_id IN ({placeholders})
        AND datetime(p.timestamp) >= datetime('now', '-' || ? || ' hours')
        GROUP BY p.machine_id
    '''
    
    params = list(machine_ids) + [hours]
    cursor.execute(query, params)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
    print("Database setup complete!")
