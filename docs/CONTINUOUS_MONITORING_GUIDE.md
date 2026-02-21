# 🚀 Continuous Monitoring Quick Start Guide

## ✅ What's New

Your predictive maintenance system now includes:

✅ **Database Storage** - All readings and predictions stored in SQLite  
✅ **Continuous Data Ingestion** - API for streaming data from IoT devices  
✅ **Real-Time Monitoring Dashboard** - Live visualization and tracking  
✅ **Historical Analytics** - Time-series plotting and comparison  
✅ **Automated Alerts** - Critical predictions trigger alerts automatically  
✅ **Batch Processing** - Efficient bulk data ingestion  

## 🎯 Quick Start (5 Minutes)

### 1. Start the Application

The Flask server is already running on:
```
http://localhost:5000
```

### 2. Login

Open your browser and go to http://localhost:5000

**Login credentials:**
- Username: `admin`
- Password: `admin123`

### 3. Access Real-Time Monitoring

Click the **"📊 Real-Time Monitor"** button in the sidebar or navigate to:
```
http://localhost:5000/monitor
```

### 4. Register Your First Machine

On the monitoring page:
1. Click **"➕ Register New Machine"**
2. Fill in the details:
   - Machine ID: `PUMP-001`
   - Machine Name: `Hydraulic Pump A`
   - Machine Type: `L` (Low Quality)
   - Location: `Factory Floor A` (optional)
3. Click **"Register Machine"**

### 5. Send Test Data

Two options:

#### Option A: Web Interface (Easy)
1. Click **"Single Reading"** button
2. Select your machine from dropdown
3. Enter parameters:
   - Air Temperature: `298.5`
   - Process Temperature: `308.7`
   - Rotational Speed: `1500`
   - Torque: `40.0`
   - Tool Wear: `50`
4. Click **"Send Data & Predict"**

#### Option B: Python Script (Automated)
```bash
python continuous_data_sender.py
```
Select option 1 for continuous simulation.

### 6. View Results

Watch the **Live Predictions** section update in real-time!
- Green ✅ = Machine OK
- Red ⚠️ = Failure Predicted

---

## 📊 View Visualizations

1. Select a machine from the dropdown
2. Choose time range (Last 24 Hours)
3. Click **"📊 Load Charts"**

You'll see 4 interactive charts:
- Failure Probability Trend
- Temperature Monitoring
- Operational Parameters
- Risk Level Distribution

---

## 🔄 Simulate Continuous Data Stream

Want to see it in action?

1. Click **"🎮 Simulate Data Stream"** button
2. Confirm the prompt
3. Watch 10 random readings get processed instantly
4. See predictions appear in the live feed

Or use the Python script for continuous simulation:
```bash
python continuous_data_sender.py
# Select option 1
```

This will:
- Register 3 test machines
- Send readings every 10 seconds
- Show real-time predictions
- Track tool wear over time
- Run until you press Ctrl+C

---

## 🔌 API Integration

### Send Data from Your IoT Device

```python
import requests

# Login
session = requests.Session()
session.post('http://localhost:5000/login', 
             json={'username': 'admin', 'password': 'admin123'})

# Send reading
response = session.post('http://localhost:5000/api/data/ingest',
    json={
        'machine_id': 'PUMP-001',
        'type': 'L',
        'air_temp': 298.5,
        'process_temp': 308.7,
        'rotational_speed': 1500,
        'torque': 40.0,
        'tool_wear': 50
    })

result = response.json()
print(f"Prediction: {result['prediction']}")
```

### Batch Upload

For high-frequency data:
```python
session.post('http://localhost:5000/api/data/batch-ingest',
    json={
        'readings': [
            {
                'machine_id': 'PUMP-001',
                'type': 'L',
                'air_temp': 298.5,
                'process_temp': 308.7,
                'rotational_speed': 1500,
                'torque': 40.0,
                'tool_wear': 50
            },
            # ... more readings
        ]
    })
```

---

## 📈 Key Features Walkthrough

### 1. Machine Management
- ➕ Register machines
- 👀 View status and statistics
- 🔍 Select machines for comparison
- 📊 Track total readings per machine

### 2. Data Ingestion
- 📝 Single reading form
- 📦 Bulk upload API
- 🎮 Data simulation
- ⏰ Automatic timestamping

### 3. Live Predictions Feed
- ⚡ Auto-refresh every 5 seconds
- ✅ Color-coded status
- 📊 Probability and confidence scores
- 🚨 Risk level indicators

### 4. Visualizations
- 📈 Time-series charts
- 📊 Interactive plots (Plotly)
- 🔄 Customizable time ranges
- 🎨 Professional graphs

### 5. Machine Comparison
- ✔️ Select multiple machines
- 📊 Side-by-side metrics
- 📈 Performance analysis
- 📉 Identify outliers

### 6. Alerts System
- 🚨 Automatic alert generation
- ⚠️ Critical risk notifications
- ✅ Acknowledge alerts
- 📊 Alert counter

---

## 🗄️ Database

All data is stored in:
```
predictive_maintenance.db
```

**Tables:**
- `machines` - Registered machines
- `machine_readings` - All sensor data
- `predictions` - ML predictions
- `alerts` - Generated alerts

**View your data:**
```bash
sqlite3 predictive_maintenance.db
.tables
SELECT * FROM machines;
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;
```

---

## 📚 Complete API Documentation

See `API_DOCUMENTATION.md` for:
- Complete endpoint reference
- Request/response examples
- Error handling
- Authentication details
- Best practices

---

## 🎓 Example Use Cases

### Use Case 1: Factory Floor Monitoring
```python
# Register all machines
machines = [
    ('PUMP-001', 'Hydraulic Pump A', 'L', 'Floor A'),
    ('MOTOR-001', 'Electric Motor B', 'M', 'Floor B'),
    ('COMP-001', 'Air Compressor C', 'H', 'Floor C')
]

for machine_id, name, mtype, location in machines:
    register_machine(machine_id, name, mtype, location)

# Continuous monitoring loop
while True:
    for machine in machines:
        reading = get_sensor_data(machine)  # Your sensor code
        send_to_api(reading)
    time.sleep(60)  # Every minute
```

### Use Case 2: Predictive Maintenance Schedule
```python
# Get statistics for all machines
stats = requests.get('http://localhost:5000/api/statistics').json()

if stats['failure_predictions'] > 0:
    print(f"⚠️ {stats['failure_predictions']} machines need attention")
    
    # Get active alerts
    alerts = requests.get('http://localhost:5000/api/alerts/active').json()
    
    for alert in alerts['alerts']:
        schedule_maintenance(alert['machine_id'])
```

### Use Case 3: Historical Analysis
```python
# Get 7 days of data
history = requests.get(
    'http://localhost:5000/api/data/history/PUMP-001?hours=168'
).json()

# Analyze trends
import pandas as pd
df = pd.DataFrame(history['data'])
print(df['failure_probability'].describe())
```

---

## 🔧 Troubleshooting

### Database Issues
```bash
# Reinitialize database
python database.py
```

### Can't Access Web Interface
- Check server is running: `http://localhost:5000`
- Verify you're logged in
- Check Flask console for errors

### API Returns 401 Unauthorized
- Login first: `POST /login`
- Use session cookies or re-authenticate

### No Predictions Appearing
- Ensure machine is registered
- Check machine_id matches exactly
- Verify all required fields are provided

---

## 📊 Architecture Overview

```
IoT Devices/Sensors
       ↓
  [Flask API]
       ↓
 [ML Predictor] ← Trained Model (98.6% accuracy)
       ↓
  [SQLite DB]
       ↓
[Web Dashboard] → Real-time visualization
```

**Data Flow:**
1. Sensor sends reading → API endpoint
2. Reading stored → database
3. ML model predicts → failure probability
4. Prediction stored → database
5. Alert generated → if high risk
6. Dashboard updates → real-time display
7. Charts plotted → historical analysis

---

## 🎯 Next Steps

1. **Register your actual machines**
2. **Integrate with your IoT devices** (see API docs)
3. **Set up continuous monitoring** loop
4. **Monitor the dashboard** regularly
5. **Analyze trends** over time
6. **Schedule maintenance** based on predictions

---

## 📞 Support Files

- `API_DOCUMENTATION.md` - Complete API reference
- `PREDICTION_GUIDE.md` - Manual prediction guide
- `continuous_data_sender.py` - Example Python client
- `database.py` - Database management
- `train_model.py` - Retrain model with new data

---

## 🎉 You're All Set!

Your predictive maintenance system is now fully operational with:
- ✅ Continuous data ingestion
- ✅ Real-time predictions
- ✅ Historical storage
- ✅ Interactive visualizations
- ✅ Automated alerts
- ✅ Machine comparison

**Start monitoring your machines now!**

Navigate to: http://localhost:5000/monitor
