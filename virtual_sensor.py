"""
Virtual Sensor Generator
Automatically generates realistic sensor data and sends to the API
Simulates different machine conditions: Normal, Degrading, and Failing
"""

import requests
import time
import random
import math
from datetime import datetime
import threading

# Configuration
API_BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin123"

# Global session
session = requests.Session()

class VirtualMachine:
    """Simulates a virtual machine with sensors"""
    
    def __init__(self, machine_id, machine_name, machine_type, health_state="normal"):
        self.machine_id = machine_id
        self.machine_name = machine_name
        self.machine_type = machine_type  # L, M, or H
        self.health_state = health_state  # normal, degrading, failing
        self.tool_wear = random.randint(0, 50)
        self.time_step = 0
        
        # Base values for normal operation
        self.base_values = {
            'L': {
                'air_temp': 298.0,
                'process_temp': 308.5,
                'speed': 1500,
                'torque': 40.0
            },
            'M': {
                'air_temp': 299.0,
                'process_temp': 309.5,
                'speed': 1650,
                'torque': 45.0
            },
            'H': {
                'air_temp': 300.0,
                'process_temp': 310.5,
                'speed': 1800,
                'torque': 50.0
            }
        }
    
    def generate_sensor_reading(self):
        """Generate realistic sensor data based on machine health state"""
        
        base = self.base_values[self.machine_type]
        self.time_step += 1
        
        # Add natural variation (sine wave + random noise)
        time_variation = math.sin(self.time_step * 0.1) * 2
        
        if self.health_state == "normal":
            # Normal operation - small variations
            air_temp = base['air_temp'] + time_variation + random.gauss(0, 1)
            process_temp = base['process_temp'] + time_variation + random.gauss(0, 1.5)
            speed = base['speed'] + random.randint(-50, 50)
            torque = base['torque'] + random.gauss(0, 3)
            self.tool_wear += random.randint(0, 2)
            
        elif self.health_state == "degrading":
            # Degrading - increased variation and trending up
            air_temp = base['air_temp'] + time_variation + random.gauss(2, 2)
            process_temp = base['process_temp'] + time_variation + random.gauss(3, 2)
            speed = base['speed'] + random.randint(-100, 150)
            torque = base['torque'] + random.gauss(5, 5)
            self.tool_wear += random.randint(1, 4)
            
        else:  # failing
            # Failing - high variation, dangerous levels
            air_temp = base['air_temp'] + time_variation + random.gauss(8, 3)
            process_temp = base['process_temp'] + time_variation + random.gauss(12, 4)
            speed = base['speed'] + random.randint(-200, 300)
            torque = base['torque'] + random.gauss(15, 8)
            self.tool_wear += random.randint(2, 6)
        
        # Keep tool wear in valid range
        self.tool_wear = min(self.tool_wear, 250)
        
        # Ensure positive values
        air_temp = max(air_temp, 290)
        process_temp = max(process_temp, 300)
        speed = max(speed, 1000)
        torque = max(torque, 10)
        
        return {
            "machine_id": self.machine_id,
            "type": self.machine_type,
            "air_temp": round(air_temp, 1),
            "process_temp": round(process_temp, 1),
            "rotational_speed": int(speed),
            "torque": round(torque, 1),
            "tool_wear": self.tool_wear,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status_emoji(self):
        """Get emoji for current health state"""
        if self.health_state == "normal":
            return "✅"
        elif self.health_state == "degrading":
            return "⚠️"
        else:
            return "🚨"


class VirtualSensorSystem:
    """Manages multiple virtual machines"""
    
    def __init__(self):
        self.machines = []
        self.running = False
        self.update_interval = 10  # seconds between updates
    
    def login(self):
        """Login to the system"""
        try:
            response = session.post(
                f"{API_BASE_URL}/login",
                json={"username": USERNAME, "password": PASSWORD}
            )
            if response.status_code == 200:
                print("✅ Logged in successfully")
                return True
            else:
                print("❌ Login failed")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the Flask server is running on http://localhost:5000")
            return False
    
    def add_machine(self, machine_id, name, machine_type, health_state="normal"):
        """Add a virtual machine"""
        machine = VirtualMachine(machine_id, name, machine_type, health_state)
        self.machines.append(machine)
        print(f"✅ Added: {name} ({machine_id}) - Health: {health_state.upper()}")
        return machine
    
    def send_reading(self, machine):
        """Send sensor reading for a machine"""
        try:
            data = machine.generate_sensor_reading()
            
            response = session.post(
                f"{API_BASE_URL}/api/data/ingest",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result['prediction']
                
                status = machine.get_status_emoji()
                risk_color = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🟠',
                    'critical': '🔴'
                }
                
                print(f"{status} {machine.machine_name}: "
                      f"Temp={data['air_temp']:.1f}K, "
                      f"Speed={data['rotational_speed']}RPM, "
                      f"Torque={data['torque']:.1f}Nm | "
                      f"{risk_color.get(prediction['risk_level'], '⚪')} "
                      f"Risk: {prediction['risk_level'].upper()} "
                      f"({prediction['failure_probability']*100:.1f}%)")
                
                return True
            else:
                print(f"❌ Error sending data for {machine.machine_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_cycle(self):
        """Run one data collection cycle for all machines"""
        print(f"\n{'='*80}")
        print(f"📊 Data Collection Cycle - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        for machine in self.machines:
            self.send_reading(machine)
            time.sleep(0.5)  # Small delay between machines
    
    def start(self):
        """Start the virtual sensor system"""
        self.running = True
        
        print("\n" + "="*80)
        print("🚀 VIRTUAL SENSOR SYSTEM STARTED")
        print("="*80)
        print(f"Active Machines: {len(self.machines)}")
        print(f"Update Interval: {self.update_interval} seconds")
        print("\nStatus Legend:")
        print("  ✅ Normal Operation  ⚠️ Degrading  🚨 Failing")
        print("  🟢 Low Risk  🟡 Medium Risk  🟠 High Risk  🔴 Critical Risk")
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(self.update_interval)
        
        except KeyboardInterrupt:
            print("\n\n" + "="*80)
            print("🛑 Virtual Sensor System Stopped")
            print("="*80)
            self.running = False
    
    def stop(self):
        """Stop the virtual sensor system"""
        self.running = False


def main():
    """Main function to run virtual sensor system"""
    
    print("\n" + "="*80)
    print("🤖 VIRTUAL SENSOR GENERATOR")
    print("="*80)
    print("Generates realistic sensor data for testing")
    print("="*80 + "\n")
    
    # Create system
    system = VirtualSensorSystem()
    
    # Login
    if not system.login():
        return
    
    print("\n" + "-"*80)
    print("⚙️  CONFIGURING VIRTUAL MACHINES")
    print("-"*80 + "\n")
    
    # Add virtual machines with different health states
    system.add_machine(
        machine_id="VM-PUMP-001",
        name="Virtual Pump A",
        machine_type="L",
        health_state="normal"
    )
    
    system.add_machine(
        machine_id="VM-MOTOR-002",
        name="Virtual Motor B",
        machine_type="M",
        health_state="normal"
    )
    
    system.add_machine(
        machine_id="VM-COMPRESSOR-003",
        name="Virtual Compressor C",
        machine_type="H",
        health_state="degrading"
    )
    
    # Optionally add a failing machine to test alerts
    # system.add_machine(
    #     machine_id="VM-PUMP-004",
    #     name="Virtual Pump D (Failing)",
    #     machine_type="L",
    #     health_state="failing"
    # )
    
    print("\n" + "-"*80)
    
    # Ask for update interval
    try:
        interval = input("\nEnter update interval in seconds (default 10): ").strip()
        if interval:
            system.update_interval = int(interval)
    except:
        pass
    
    # Start the system
    input("\nPress Enter to start the virtual sensors...")
    system.start()


if __name__ == "__main__":
    main()
