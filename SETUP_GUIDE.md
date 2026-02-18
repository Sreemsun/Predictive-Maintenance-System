# Predictive Maintenance System - Setup Guide

## Quick Setup Instructions

### Step 1: Open Terminal
Open PowerShell or Command Prompt in the project directory:
```bash
cd "c:\Sreemsun\Tool analysis"
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Access the Application
Open your browser and go to: **http://localhost:5000**

### Step 6: Login
Use these credentials:
- Username: `admin`
- Password: `admin123`

## Project Structure

```
Tool analysis/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Comprehensive documentation
├── SETUP_GUIDE.md                 # This file
├── templates/                      # HTML templates
│   ├── login.html                 # Login page
│   └── dashboard.html             # Main dashboard
├── static/                         # Static files
│   ├── css/                       # Stylesheets
│   │   ├── login.css
│   │   └── dashboard.css
│   └── js/                        # JavaScript files
│       ├── login.js
│       └── dashboard.js
└── ml_models/                      # Machine learning modules
    ├── __init__.py
    ├── data_simulator.py          # Generate sensor data
    ├── health_calculator.py       # Calculate health scores
    ├── predictor.py               # Predict failures
    ├── anomaly_detector.py        # Detect anomalies
    └── alert_system.py            # Manage alerts
```

## Features

✅ User Authentication System
✅ Real-time Sensor Data Visualization
✅ Equipment Health Monitoring
✅ Failure Prediction (2-48 hours ahead)
✅ Anomaly Detection
✅ Multi-level Alert System
✅ Interactive Charts (Plotly)
✅ Responsive Design
✅ Auto-refresh Dashboard

## Troubleshooting

### Issue: Port 5000 already in use
**Solution:** Change the port in app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Module not found
**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Prophet installation fails
**Solution:** Install PyStan first:
```bash
pip install pystan==2.19.1.1
pip install prophet
```

## Testing the Application

1. **Login Page**: Test authentication with provided credentials
2. **Dashboard**: Verify all components load correctly
3. **Refresh Button**: Click to reload all data
4. **Time Range**: Change time range selector to load historical data
5. **Navigation**: Click sidebar items to test navigation
6. **Logout**: Test logout functionality

## Customization

### Change Update Interval
Edit `static/js/dashboard.js` (line ~17):
```javascript
updateInterval = setInterval(() => {
    loadAllData();
}, 5000);  // Change 5000 to desired milliseconds
```

### Add New Users
Edit `app.py` (line ~13):
```python
USERS = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest(),
    'operator': hashlib.sha256('operator123'.encode()).hexdigest(),
    'newuser': hashlib.sha256('password123'.encode()).hexdigest()  # Add here
}
```

### Modify Alert Thresholds
Edit `ml_models/alert_system.py` (line ~57):
```python
thresholds = {
    'vibration': {'warning': 15, 'critical': 20},
    'temperature': {'warning': 85, 'critical': 95},
    'pressure': {'warning': 110, 'critical': 120}
}
```

## Next Steps

1. **Integrate Real Data**: Replace simulated data with actual sensor readings
2. **Add Database**: Implement PostgreSQL/MySQL for data persistence
3. **Enhance ML Models**: Train models on real industrial equipment data
4. **Add Notifications**: Implement email/SMS alerts for critical events
5. **Deploy**: Deploy to cloud platform (AWS, Azure, Heroku)

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualization**: Plotly.js
- **ML Libraries**: NumPy, Pandas, Scikit-learn
- **Future**: Prophet, MQTT, PostgreSQL

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the code comments in app.py and ml_models/
3. Ensure all dependencies are correctly installed

---

**Happy Monitoring! 🚀**
