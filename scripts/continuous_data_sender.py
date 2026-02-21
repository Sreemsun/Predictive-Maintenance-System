"""
Example script for sending continuous data to the Predictive Maintenance API
This simulates an IoT device or sensor sending machine readings
"""

import requests
import time
import random
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin123"

# Session for maintaining login
session = requests.Session()

def login():
    """Login to the system"""
    response = session.post(
        f"{API_BASE_URL}/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        print("✓ Logged in successfully")
        return True
    else:
        print("✗ Login failed")
        return False

def register_machine(machine_id, machine_name, machine_type, location=None):
    """Register a new machine"""
    response = session.post(
        f"{API_BASE_URL}/api/machines/register",
        json={
            "machine_id": machine_id,
            "machine_name": machine_name,
            "machine_type": machine_type,
            "location": location
        }
    )
    
    data = response.json()
    if data.get('success'):
        print(f"✓ Machine {machine_id} registered")
    else:
        print(f"Note: {data.get('error', 'Machine may already exist')}")

def send_single_reading(machine_id, machine_type, air_temp, process_temp, 
                       rotational_speed, torque, tool_wear):
    """Send a single machine reading"""
    data = {
        "machine_id": machine_id,
        "type": machine_type,
        "air_temp": air_temp,
        "process_temp": process_temp,
        "rotational_speed": rotational_speed,
        "torque": torque,
        "tool_wear": tool_wear,
        "timestamp": datetime.now().isoformat()
    }
    
    response = session.post(
        f"{API_BASE_URL}/api/data/ingest",
        json=data
    )
    
    result = response.json()
    
    if result.get('success'):
        prediction = result['prediction']
        status = "⚠️ FAILURE PREDICTED" if prediction['will_fail'] else "✓ OK"
        prob = prediction['failure_probability'] * 100
        
        print(f"{machine_id}: {status} | Probability: {prob:.1f}% | Risk: {prediction['risk_level'].upper()}")
        return True
    else:
        print(f"✗ Error: {result.get('error')}")
        return False

def send_batch_readings(readings):
    """Send multiple readings at once"""
    response = session.post(
        f"{API_BASE_URL}/api/data/batch-ingest",
        json={"readings": readings}
    )
    
    result = response.json()
    
    if result.get('success'):
        print(f"✓ Batch ingestion: {result['successful']}/{result['processed']} successful")
        return True
    else:
        print(f"✗ Batch error: {result.get('error')}")
        return False

def generate_realistic_reading(machine_type, base_tool_wear=0):
    """Generate realistic machine parameters"""
    # Simulate normal operation with some variation
    air_temp = random.gauss(298, 2)  # Mean 298K, std 2K
    process_temp = air_temp + random.gauss(10, 1)  # About 10K higher
    
    rotational_speed = random.randint(1300, 2000)
    torque = random.gauss(40, 10)
    tool_wear = base_tool_wear + random.randint(0, 5)
    
    return {
        "type": machine_type,
        "air_temp": round(air_temp, 1),
        "process_temp": round(process_temp, 1),
        "rotational_speed": rotational_speed,
        "torque": round(max(10, torque), 1),
        "tool_wear": min(tool_wear, 250)
    }

def simulate_continuous_monitoring():
    """Simulate continuous monitoring of multiple machines"""
    
    print("\n" + "="*70)
    print("CONTINUOUS MACHINE MONITORING SIMULATION")
    print("="*70 + "\n")
    
    # Login
    if not login():
        return
    
    # Register test machines
    machines = [
        ("PUMP-001", "Hydraulic Pump A", "L", "Factory Floor A"),
        ("MOTOR-001", "Electric Motor B", "M", "Factory Floor B"),
        ("COMPRESSOR-001", "Air Compressor C", "H", "Factory Floor C")
    ]
    
    print("\nRegistering machines...")
    for machine_id, name, mtype, location in machines:
        register_machine(machine_id, name, mtype, location)
    
    print("\n" + "-"*70)
    print("Starting continuous data stream (Press Ctrl+C to stop)")
    print("-"*70 + "\n")
    
    tool_wear_tracker = {m[0]: 0 for m in machines}
    reading_count = 0
    
    try:
        while True:
            # Send reading for each machine
            for machine_id, _, machine_type, _ in machines:
                reading = generate_realistic_reading(
                    machine_type, 
                    tool_wear_tracker[machine_id]
                )
                
                send_single_reading(
                    machine_id=machine_id,
                    machine_type=reading['type'],
                    air_temp=reading['air_temp'],
                    process_temp=reading['process_temp'],
                    rotational_speed=reading['rotational_speed'],
                    torque=reading['torque'],
                    tool_wear=reading['tool_wear']
                )
                
                # Increment tool wear
                tool_wear_tracker[machine_id] = reading['tool_wear']
            
            reading_count += len(machines)
            print(f"\nTotal readings sent: {reading_count}")
            print("-"*70)
            
            # Wait before next reading cycle
            time.sleep(10)  # Send readings every 10 seconds
            
    except KeyboardInterrupt:
        print(f"\n\n✓ Simulation stopped. Total readings sent: {reading_count}")

def send_bulk_data_example():
    """Example of sending bulk data"""
    
    print("\n" + "="*70)
    print("BULK DATA INGESTION EXAMPLE")
    print("="*70 + "\n")
    
    if not login():
        return
    
    # Register a test machine
    register_machine("TEST-BULK-001", "Bulk Test Machine", "M", "Test Lab")
    
    # Generate 20 readings
    readings = []
    tool_wear = 0
    
    for i in range(20):
        reading = generate_realistic_reading("M", tool_wear)
        reading['machine_id'] = "TEST-BULK-001"
        readings.append(reading)
        tool_wear += random.randint(1, 3)
    
    print(f"Sending {len(readings)} readings in bulk...")
    send_batch_readings(readings)
    
    print("\n✓ Bulk ingestion complete!")

def main():
    """Main function"""
    print("\nSelect mode:")
    print("1. Continuous Monitoring Simulation")
    print("2. Bulk Data Ingestion Example")
    print("3. Single Reading Test")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        simulate_continuous_monitoring()
    elif choice == "2":
        send_bulk_data_example()
    elif choice == "3":
        if login():
            register_machine("TEST-001", "Test Machine", "L", "Test Lab")
            reading = generate_realistic_reading("L", 50)
            send_single_reading(
                machine_id="TEST-001",
                machine_type=reading['type'],
                air_temp=reading['air_temp'],
                process_temp=reading['process_temp'],
                rotational_speed=reading['rotational_speed'],
                torque=reading['torque'],
                tool_wear=reading['tool_wear']
            )
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
