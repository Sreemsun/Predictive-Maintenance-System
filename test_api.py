"""
Simple API Test Script
This script demonstrates how to send sensor data to the Predictive Maintenance API
"""

import requests
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin123"

# Create a session to maintain cookies
session = requests.Session()

def login():
    """Step 1: Login to the system"""
    print("\n" + "="*60)
    print("STEP 1: LOGGING IN")
    print("="*60)
    
    response = session.post(
        f"{API_BASE_URL}/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    
    if response.status_code == 200:
        print("✓ Login successful!")
        return True
    else:
        print("✗ Login failed!")
        print(f"Response: {response.text}")
        return False

def send_single_reading():
    """Step 2: Send a single sensor reading"""
    print("\n" + "="*60)
    print("STEP 2: SENDING SENSOR DATA")
    print("="*60)
    
    # Example sensor data (replace with your real sensor values)
    sensor_data = {
        "machine_id": "TEST-MACHINE-001",
        "type": "L",                    # L=Low, M=Medium, H=High quality
        "air_temp": 298.5,              # Kelvin (25.5°C)
        "process_temp": 308.7,          # Kelvin (35.7°C)
        "rotational_speed": 1500,       # RPM
        "torque": 40.0,                 # Newton-meters
        "tool_wear": 50,                # Minutes (0-250)
        "timestamp": datetime.now().isoformat()
    }
    
    print("\nSending data:")
    print(f"  Machine ID: {sensor_data['machine_id']}")
    print(f"  Air Temperature: {sensor_data['air_temp']}K ({sensor_data['air_temp']-273.15:.1f}°C)")
    print(f"  Process Temperature: {sensor_data['process_temp']}K ({sensor_data['process_temp']-273.15:.1f}°C)")
    print(f"  Rotational Speed: {sensor_data['rotational_speed']} RPM")
    print(f"  Torque: {sensor_data['torque']} Nm")
    print(f"  Tool Wear: {sensor_data['tool_wear']} min")
    
    response = session.post(
        f"{API_BASE_URL}/api/data/ingest",
        json=sensor_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Data sent successfully!")
        print(f"  Reading ID: {result['reading_id']}")
        print(f"  Prediction ID: {result['prediction_id']}")
        
        prediction = result['prediction']
        print("\n📊 PREDICTION RESULTS:")
        print(f"  Will Fail: {'YES ⚠️' if prediction['will_fail'] else 'NO ✓'}")
        print(f"  Failure Probability: {prediction['failure_probability']*100:.2f}%")
        print(f"  Confidence: {prediction['confidence']*100:.2f}%")
        print(f"  Risk Level: {prediction['risk_level'].upper()}")
        
        return True
    else:
        print(f"\n✗ Failed to send data: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def check_machine_history():
    """Step 3: Check machine reading history"""
    print("\n" + "="*60)
    print("STEP 3: CHECKING MACHINE HISTORY")
    print("="*60)
    
    machine_id = "TEST-MACHINE-001"
    
    response = session.get(f"{API_BASE_URL}/api/data/history/{machine_id}")
    
    if response.status_code == 200:
        data = response.json()
        readings = data.get('readings', [])
        
        print(f"\n✓ Found {len(readings)} readings for {machine_id}")
        
        if readings:
            print("\nLatest 3 readings:")
            for reading in readings[:3]:
                print(f"\n  Time: {reading['timestamp']}")
                print(f"  Air Temp: {reading['air_temperature']}K")
                print(f"  RPM: {reading['rotational_speed']}")
                print(f"  Torque: {reading['torque']} Nm")
        
        return True
    else:
        print(f"✗ Failed to get history: {response.status_code}")
        return False

def send_multiple_readings():
    """Step 4: Send multiple readings (simulating continuous monitoring)"""
    print("\n" + "="*60)
    print("STEP 4: SENDING MULTIPLE READINGS")
    print("="*60)
    print("\nSending 3 readings with 2-second intervals...")
    
    for i in range(1, 4):
        print(f"\n--- Reading {i}/3 ---")
        
        # Simulate slightly varying sensor values
        sensor_data = {
            "machine_id": "TEST-MACHINE-001",
            "type": "L",
            "air_temp": 298.5 + i * 0.5,      # Gradually increasing temperature
            "process_temp": 308.7 + i * 0.5,
            "rotational_speed": 1500 + i * 10,
            "torque": 40.0 + i * 0.5,
            "tool_wear": 50 + i,
            "timestamp": datetime.now().isoformat()
        }
        
        response = session.post(
            f"{API_BASE_URL}/api/data/ingest",
            json=sensor_data
        )
        
        if response.status_code == 200:
            result = response.json()
            prediction = result['prediction']
            status = "⚠️ FAILURE PREDICTED" if prediction['will_fail'] else "✓ OK"
            print(f"  Result: {status} | Probability: {prediction['failure_probability']*100:.1f}%")
        else:
            print(f"  ✗ Failed: {response.status_code}")
        
        if i < 3:
            time.sleep(2)  # Wait 2 seconds between readings

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("PREDICTIVE MAINTENANCE API TEST")
    print("="*60)
    print("\nThis script will:")
    print("1. Login to the system")
    print("2. Send a sensor reading")
    print("3. Check machine history")
    print("4. Send multiple readings")
    print("\nMake sure the Flask server is running on http://localhost:5000")
    print("="*60)
    
    input("\nPress Enter to start...")
    
    # Step 1: Login
    if not login():
        print("\n❌ Cannot proceed without login. Exiting...")
        return
    
    # Step 2: Send single reading
    if not send_single_reading():
        print("\n⚠️ Failed to send reading, but continuing...")
    
    # Step 3: Check history
    time.sleep(1)
    check_machine_history()
    
    # Step 4: Send multiple readings
    time.sleep(1)
    send_multiple_readings()
    
    print("\n" + "="*60)
    print("✓ API TEST COMPLETED!")
    print("="*60)
    print("\nYou can now:")
    print("- Check the dashboard at http://localhost:5000/dashboard")
    print("- View monitoring page at http://localhost:5000/monitor")
    print("- Check predictions at http://localhost:5000/predict")
    print("\nModify this script to send YOUR real sensor data!")

if __name__ == "__main__":
    main()
